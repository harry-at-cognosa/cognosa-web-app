#!/usr/bin/env python3
"""
FUROCAD — Phase 1 / Pass 1: extract the body text of Papetti, *The Forensic
Unreliability of Shaken Baby Syndrome* (2024) into section-aware chunks and load
them into the Qdrant collection used by Cognosa.

Design: docs/furocad/pass1_book_ingest_design.md

Usage (from backend/, with the project venv):

    ../venv/bin/python -m tools.ingest_dev.furocad_book_loader extract
    ../venv/bin/python -m tools.ingest_dev.furocad_book_loader load   [--recreate] [--kind body|footnote]
    ../venv/bin/python -m tools.ingest_dev.furocad_book_loader check  "query text"

`extract` writes <OUT_DIR>/furocad_book_pass1.jsonl (one record per chunk, body and
footnote) and <OUT_DIR>/furocad_book_pass1_report.md (quality gates, coverage, token
histogram, spot checks). Nothing touches Qdrant until `load`.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import random
import re
import statistics
import sys
import uuid
from dataclasses import dataclass, field, asdict

import pymupdf  # PyMuPDF

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------
PDF_PATH = os.environ.get(
    "FUROCAD_PDF",
    "/Users/harry/+_claude_projects_from_260807/p67_furocad_notes/SBS_Paperback_July_2024.pdf",
)
TOC_PATH = os.environ.get(
    "FUROCAD_TOC",
    "/Users/harry/+_claude_projects_from_260807/p67_furocad_notes/sbs_book_toc.txt",
)
OUT_DIR = os.environ.get(
    "FUROCAD_OUT",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "furocad_out"),
)

SOURCE_ID = "papetti_2024_sbs"
SOURCE_TITLE = "The Forensic Unreliability of Shaken Baby Syndrome"
SOURCE_AUTHOR = "Papetti"
SOURCE_YEAR = 2024
INGEST_RUN = "pass1_2026-08-19"

PAGE_OFFSET = 18            # printed page p -> PDF index p + 18 - 1 (0-based)
FIRST_PAGE, LAST_PAGE = 1, 316   # pass-1 scope (printed pages)
KNOWN_BLANK_PAGES = {8, 78, 198, 252}

QDRANT_URL = os.environ.get("FUROCAD_QDRANT", "qdrant_local")   # ParsedUrl alias or host:port
COLLECTION = os.environ.get("FUROCAD_COLLECTION", "furocad")                        # body chunks
FOOTNOTE_COLLECTION = os.environ.get("FUROCAD_FN_COLLECTION", "furocad_footnotes")   # linked footnote points
# Footnotes live in a sibling collection: the platform has no fixed default filter, and
# short citation-dense notes otherwise crowd body chunks out of top-k.
EMB_MODEL = os.environ.get("FUROCAD_EMB_MODEL", "BAAI/bge-base-en-v1.5")

TARGET_TOKENS = 350
MAX_TOKENS = 450          # body tokens target ceiling
TOTAL_MAX_TOKENS = 500    # prefix + overlap + body must stay under the 512 bge window
MIN_TAIL_TOKENS = 120       # below this, a unit tail is merged back into the previous chunk
OVERLAP_MAX_TOKENS = 40     # overlap sentence is dropped if longer than this

# typography (from the scan)
HEAD_SIZES = {22.0: 1, 16.0: 2, 14.0: 3, 12.0: 4}   # font size -> heading level
BODY_MIN, BODY_MAX = 11.5, 12.5
FOOTNOTE_SIZE = 9.0
MARKER_MAX_SIZE = 7.5
RUNNING_HEAD_Y = 60
LINE_PITCH = 18.0

SOFT_HYPHEN = "\xad"

# ----------------------------------------------------------------------------
# Data model
# ----------------------------------------------------------------------------
@dataclass
class Line:
    page: int
    y: float
    x0: float
    x1: float
    size: float
    fonts: set
    text: str
    role: str            # head1..head4 | body | footnote | marker-only | other


@dataclass
class Heading:
    level: int
    number: str          # "3.2.1" | "3" for chapter
    title: str
    page: int


@dataclass
class Paragraph:
    text: str
    page_start: int
    page_end: int
    refs: list = field(default_factory=list)   # footnote numbers referenced


@dataclass
class Unit:
    chapter_no: int
    chapter_title: str
    section_id: str      # "3.2.1" | "3.0" for chapter intro / chapters without sections
    section_title: str
    breadcrumb: str
    page_start: int
    page_end: int
    paragraphs: list = field(default_factory=list)


@dataclass
class Footnote:
    number: int
    page_start: int
    page_end: int
    text: str


# ----------------------------------------------------------------------------
# 1. Line extraction and role classification
# ----------------------------------------------------------------------------
def page_lines(doc: pymupdf.Document, printed_page: int) -> list[Line]:
    pg = doc[printed_page + PAGE_OFFSET - 1]
    out: list[Line] = []
    for blk in pg.get_text("dict")["blocks"]:
        if blk["type"] != 0:
            continue
        for ln in blk["lines"]:
            spans = [s for s in ln["spans"] if s["text"]]
            if not spans:
                continue
            # Rebuild text, converting 7pt digit spans (footnote markers) to [^N]
            parts = []
            for s in spans:
                t = s["text"]
                if s["size"] <= MARKER_MAX_SIZE and t.strip().isdigit():
                    parts.append(f"[^{t.strip()}]")
                else:
                    parts.append(t)
            text = "".join(parts)
            if not text.strip():
                continue
            big = [s for s in spans if s["size"] > MARKER_MAX_SIZE]
            size = round(max(s["size"] for s in big), 1) if big else round(max(s["size"] for s in spans), 1)
            fonts = {s["font"] for s in big} if big else {s["font"] for s in spans}
            y = ln["bbox"][1]
            role = classify(size, fonts, y, text)
            out.append(Line(printed_page, y, ln["bbox"][0], ln["bbox"][2], size, fonts, text, role))
    out.sort(key=lambda l: (l.y, l.x0))
    return out


def classify(size: float, fonts: set, y: float, text: str) -> str:
    bold_arial = any("Arial-Bold" in f for f in fonts)
    if y < RUNNING_HEAD_Y:
        return "other"                       # running head
    if size == 84.0:
        return "other"                       # chapter number glyph
    if bold_arial and size in HEAD_SIZES:
        return f"head{HEAD_SIZES[size]}"     # numbered first line or continuation line
    if BODY_MIN <= size <= BODY_MAX and any("Times" in f for f in fonts):
        return "body"
    if 6.0 <= size <= FOOTNOTE_SIZE + 0.6:
        return "footnote"
    return "other"


# ----------------------------------------------------------------------------
# 2. Structure: headings -> units; body lines -> paragraphs; footnotes
# ----------------------------------------------------------------------------
HEAD_NUM_RE = re.compile(r"^(\d+(?:\.\d+){1,3})\s*\t?\s*(.*)$")


def clean_join(prev: str, nxt: str) -> str:
    """Join two consecutive lines of one paragraph, resolving soft hyphens."""
    prev = prev.rstrip()
    if prev.endswith(SOFT_HYPHEN):
        return prev[:-1] + nxt.lstrip()
    if prev.endswith("-"):
        return prev + nxt.lstrip()          # hyphen at line end: broken word or compound
    return prev + " " + nxt.lstrip()


def normalise(text: str) -> str:
    text = text.replace(SOFT_HYPHEN, "")
    text = re.sub(r"[ \t]+", " ", text)
    text = text.replace(" ,", ",").replace(" .", ".")
    return text.strip()


def extract_structure(doc: pymupdf.Document):
    """Return (units, footnotes, per_page_stats)."""
    units: list[Unit] = []
    footnotes: dict[int, Footnote] = {}
    stats = {}

    chapter_no = 0
    chapter_title = ""
    sec_titles: dict[str, str] = {}       # "3.2" -> title (for breadcrumbs)
    cur_unit: Unit | None = None
    cur_par: Paragraph | None = None
    par_open_across_page = False          # previous page ended mid-paragraph
    pending_head: Heading | None = None   # heading being assembled over several lines
    open_fn: Footnote | None = None       # footnote continuing across lines/pages
    col_right = None

    def close_par():
        nonlocal cur_par
        if cur_par and cur_unit is not None and cur_par.text.strip():
            cur_par.text = normalise(cur_par.text)
            cur_par.refs = [int(n) for n in re.findall(r"\[\^(\d+)\]", cur_par.text)]
            cur_unit.paragraphs.append(cur_par)
        cur_par = None

    def close_unit(last_page: int):
        nonlocal cur_unit
        close_par()
        if cur_unit is not None:
            cur_unit.page_end = last_page
            units.append(cur_unit)
        cur_unit = None

    def start_unit(section_id: str, section_title: str, page: int):
        nonlocal cur_unit
        close_unit(page)
        parts = [f"Ch. {chapter_no} {chapter_title}"]
        if section_id.endswith(".0"):
            pass
        else:
            nums = section_id.split(".")
            for depth in range(2, len(nums) + 1):
                sid = ".".join(nums[:depth])
                parts.append(f"{sid} {sec_titles.get(sid, '')}".strip())
        cur_unit = Unit(chapter_no, chapter_title, section_id, section_title,
                        " › ".join(parts), page, page)

    def flush_head(h: Heading):
        nonlocal chapter_no, chapter_title
        title = normalise(h.title)
        if h.level == 1:
            chapter_no += 1
            chapter_title = title
            start_unit(f"{chapter_no}.0", title, h.page)
        else:
            sec_titles[h.number] = title
            start_unit(h.number, title, h.page)

    for pp in range(FIRST_PAGE, LAST_PAGE + 1):
        lines = page_lines(doc, pp)
        body_lines = [l for l in lines if l.role == "body"]
        fn_lines = [l for l in lines if l.role == "footnote"]
        stats[pp] = {"body_chars": sum(len(l.text) for l in body_lines),
                     "fn_chars": sum(len(l.text) for l in fn_lines),
                     "heads": sum(1 for l in lines if l.role.startswith("head"))}
        if body_lines:
            col_right = max(l.x1 for l in body_lines)

        # ---- body & headings, in reading order -------------------------------
        prev_body: Line | None = None
        first_body_on_page = True
        for l in lines:
            if l.role == "other" or l.role == "footnote":
                continue
            if l.role.startswith("head"):
                close_par()
                level = int(l.role[4:])
                m = HEAD_NUM_RE.match(l.text.strip())
                starts_new = (level == 1 and not (pending_head and pending_head.level == 1 and pending_head.page == pp)) \
                    or (level > 1 and m is not None)
                if starts_new:
                    if pending_head:
                        flush_head(pending_head)
                    pending_head = Heading(level, "" if level == 1 else m.group(1),
                                           l.text if level == 1 else m.group(2), pp)
                elif pending_head and pending_head.level == level:
                    pending_head.title = clean_join(pending_head.title, l.text)   # wrapped heading line
                # else: stray bold line (e.g. appendix figure label) — ignore
                continue

            # body line
            if pending_head:
                flush_head(pending_head)
                pending_head = None
            if cur_unit is None:
                continue  # text before the first heading (should not happen in scope)
            new_par = False
            if cur_par is None:
                new_par = True
            elif first_body_on_page:
                # continuation across the page break unless previous paragraph clearly ended
                new_par = not par_open_across_page
            elif prev_body is not None and (l.y - prev_body.y) > LINE_PITCH * 1.5:
                new_par = True
            if new_par:
                close_par()
                cur_par = Paragraph(l.text, pp, pp)
            else:
                cur_par.text = clean_join(cur_par.text, l.text)
                cur_par.page_end = pp
            prev_body = l
            first_body_on_page = False

        # decide whether the paragraph continues onto the next page
        if prev_body is not None and cur_par is not None:
            short_last_line = col_right is not None and prev_body.x1 < col_right - 12
            ends_sentence = bool(re.search(r'[.!?”"\)\]](\[\^\d+\])?\s*$', prev_body.text.strip()))
            par_open_across_page = not (short_last_line and ends_sentence)
        else:
            par_open_across_page = False
        if pending_head and pending_head.level == 1 and not body_lines:
            pass  # chapter opener page: heading flushed when body starts next page

        # ---- footnotes --------------------------------------------------------
        if fn_lines:
            fn_left = min(l.x0 for l in fn_lines)
        for l in fn_lines:
            t = l.text
            m = re.match(r"^(\d{1,4})[\t ]+(.*)$", t)
            at_margin = l.x0 <= fn_left + 2.0
            if m and at_margin and (open_fn is None or open_fn.number < int(m.group(1)) <= open_fn.number + 3):
                if open_fn:
                    open_fn.text = normalise(open_fn.text)
                    footnotes[open_fn.number] = open_fn
                open_fn = Footnote(int(m.group(1)), pp, pp, m.group(2))
            else:
                if open_fn is None:
                    continue
                t = t.lstrip("\t ")
                if not t:
                    continue
                open_fn.text = clean_join(open_fn.text, t)
                open_fn.page_end = pp

    if pending_head:
        flush_head(pending_head)
    close_unit(LAST_PAGE)
    if open_fn:
        open_fn.text = normalise(open_fn.text)
        footnotes[open_fn.number] = open_fn
    return units, footnotes, stats


# ----------------------------------------------------------------------------
# 3. Chunking
# ----------------------------------------------------------------------------
_tok = None


def n_tokens(text: str) -> int:
    global _tok
    if _tok is None:
        from transformers import AutoTokenizer
        _tok = AutoTokenizer.from_pretrained(EMB_MODEL)
    return len(_tok.encode(text, add_special_tokens=True))


SENT_SPLIT = re.compile(r"(?<=[.!?”\"])\s+(?=[A-Z“\"\(\[])")


def split_sentences(text: str) -> list[str]:
    return [s for s in SENT_SPLIT.split(text) if s.strip()]


def hard_split(text: str, budget: int) -> list[str]:
    """Split a single over-long sentence on word boundaries to fit the budget."""
    words, out, buf = text.split(), [], []
    for w in words:
        if buf and n_tokens(" ".join(buf + [w])) > budget:
            out.append(" ".join(buf)); buf = []
        buf.append(w)
    if buf:
        out.append(" ".join(buf))
    return out


def split_long_paragraph(p: Paragraph, budget: int) -> list[Paragraph]:
    if n_tokens(p.text) <= budget:
        return [p]
    pieces = []
    for sent in split_sentences(p.text):
        pieces.extend(hard_split(sent, budget) if n_tokens(sent) > budget else [sent])
    out, buf = [], []
    for s_ in pieces:
        if buf and n_tokens(" ".join(buf + [s_])) > budget:
            out.append(Paragraph(" ".join(buf), p.page_start, p.page_end))
            buf = []
        buf.append(s_)
    if buf:
        out.append(Paragraph(" ".join(buf), p.page_start, p.page_end))
    for q in out:
        q.refs = [int(n) for n in re.findall(r"\[\^(\d+)\]", q.text)]
    return out


def chunk_unit(u: Unit) -> list[dict]:
    pages_all = f"pp. {u.page_start}–{u.page_end}"
    prefix_tokens = n_tokens(f"[{u.breadcrumb}] ({pages_all})") + 2
    body_budget = min(MAX_TOKENS, TOTAL_MAX_TOKENS - prefix_tokens - OVERLAP_MAX_TOKENS)
    target = min(TARGET_TOKENS, body_budget - 40)
    pars = [q for p in u.paragraphs for q in split_long_paragraph(p, body_budget)]
    groups: list[list[Paragraph]] = []
    buf: list[Paragraph] = []
    buf_tokens = 0
    for p in pars:
        pt = n_tokens(p.text)
        if buf and (buf_tokens + pt > body_budget or buf_tokens >= target):
            groups.append(buf)
            buf, buf_tokens = [], 0
        buf.append(p)
        buf_tokens += pt
    if buf:
        # merge a tiny tail back into the previous group if it fits
        if groups and buf_tokens < MIN_TAIL_TOKENS and \
                sum(n_tokens(p.text) for p in groups[-1]) + buf_tokens <= body_budget:
            groups[-1].extend(buf)
        else:
            groups.append(buf)

    chunks = []
    prev_last_sentence = None
    for gi, g in enumerate(groups):
        body = "\n\n".join(p.text for p in g)
        overlap = ""
        if prev_last_sentence and n_tokens(prev_last_sentence) <= OVERLAP_MAX_TOKENS:
            overlap = "… " + prev_last_sentence + "\n\n"
        page_start = min(p.page_start for p in g)
        page_end = max(p.page_end for p in g)
        refs = sorted({r for p in g for r in p.refs})
        pages = f"p. {page_start}" if page_start == page_end else f"pp. {page_start}–{page_end}"
        prefix = f"[{u.breadcrumb}] ({pages})"
        text = f"{prefix}\n{overlap}{body}"
        chunks.append({
            "kind": "body",
            "text": text,
            "body_text": body,
            "prefix": prefix,
            "chapter_no": u.chapter_no,
            "chapter_title": u.chapter_title,
            "section_id": u.section_id,
            "section_title": u.section_title,
            "breadcrumb": u.breadcrumb,
            "page_start": page_start,
            "page_end": page_end,
            "unit_chunk_idx": gi,
            "unit_chunks": len(groups),
            "n_tokens": n_tokens(text),
            "footnote_refs": refs,
        })
        sents = split_sentences(g[-1].text)
        prev_last_sentence = sents[-1] if sents else None
    return chunks


def build_records(units: list[Unit], footnotes: dict[int, Footnote]) -> list[dict]:
    records = []
    idx = 0
    for u in units:
        for c in chunk_unit(u):
            c["chunk_idx"] = idx
            idx += 1
            records.append(c)
    # footnotes -> linked records
    ref_owner = {}
    for c in records:
        for r in c["footnote_refs"]:
            ref_owner.setdefault(r, c)
    for num in sorted(footnotes):
        fn = footnotes[num]
        owner = ref_owner.get(num)
        if owner is None:
            crumb, ch, sid, st = "", None, None, None
        else:
            crumb, ch, sid, st = owner["breadcrumb"], owner["chapter_no"], owner["section_id"], owner["section_title"]
        base_prefix = f"[{crumb} › footnote {num}" if crumb else f"[footnote {num}"
        fn_budget = TOTAL_MAX_TOKENS - n_tokens(base_prefix + " part 99/99]") - 4
        parts = [q.text for q in split_long_paragraph(Paragraph(fn.text, fn.page_start, fn.page_end), fn_budget)]
        for k, part_text in enumerate(parts):
            prefix = base_prefix + (f" part {k + 1}/{len(parts)}]" if len(parts) > 1 else "]")
            text = f"{prefix}\n{part_text}"
            records.append({
                "kind": "footnote",
                "text": text,
                "body_text": part_text,
                "prefix": prefix,
                "note_no": num,
                "note_part": k + 1,
                "note_parts": len(parts),
                "chapter_no": ch,
                "chapter_title": owner["chapter_title"] if owner else None,
                "section_id": sid,
                "section_title": st,
                "breadcrumb": crumb,
                "page_start": fn.page_start,
                "page_end": fn.page_end,
                "anchors_chunk_idx": owner["chunk_idx"] if owner else None,
                "n_tokens": n_tokens(text),
                "chunk_idx": idx,
            })
            idx += 1
    return records


# ----------------------------------------------------------------------------
# 4. Report / quality gates
# ----------------------------------------------------------------------------
def load_toc(path: str) -> list[tuple[str, str, int]]:
    """-> [(number or 'Chapter N', title, page)]"""
    out = []
    for raw in open(path, encoding="utf8"):
        line = raw.strip()
        if not line or line.startswith(("Appendix", "Index")) or re.match(r"^\d+\. ", line):
            continue
        m = re.match(r"^(Chapter \d+|\d+(?:\.\d+){1,3})[:\s]+(.*?)[\s.]*\.{2,}[\s.]*(\d+)\s*$", line)
        if m:
            out.append((m.group(1), m.group(2).strip(), int(m.group(3))))
    return out


def write_report(units, footnotes, stats, records, toc, path):
    body = [r for r in records if r["kind"] == "body"]
    fns = [r for r in records if r["kind"] == "footnote"]
    L = []
    L.append(f"# FUROCAD pass-1 extraction report ({INGEST_RUN})\n")
    L.append(f"Source: `{os.path.basename(PDF_PATH)}` printed pp. {FIRST_PAGE}–{LAST_PAGE}; tokenizer/embedding `{EMB_MODEL}`\n")
    L.append(f"- section units: **{len(units)}**\n- body chunks: **{len(body)}**\n- footnotes: **{len(footnotes)}** "
             f"(numbers {min(footnotes) if footnotes else '-'}–{max(footnotes) if footnotes else '-'}) in {len(fns)} records "
             f"({sum(1 for r in fns if r.get('note_parts', 1) > 1)} parts of split long notes)\n")
    # --- gate 1: TOC headings
    found = {(u.section_id if not u.section_id.endswith('.0') else f"Chapter {u.chapter_no}"): u for u in units}
    missing, wrong_page = [], []
    for num, title, page in toc:
        u = found.get(num)
        if u is None:
            missing.append((num, title, page))
        elif u.page_start != page:
            wrong_page.append((num, title, page, u.page_start))
    L.append(f"## Gate 1 — TOC headings: {len(toc) - len(missing)}/{len(toc)} found, {len(wrong_page)} on a different page "
             f"{'✅' if not missing and not wrong_page else '❌'}\n")
    for m in missing: L.append(f"- MISSING {m}")
    for w in wrong_page: L.append(f"- PAGE MISMATCH {w}")
    # --- gate 2: page coverage
    covered = set()
    for r in body:
        covered.update(range(r["page_start"], r["page_end"] + 1))
    uncovered = [p for p in range(FIRST_PAGE, LAST_PAGE + 1) if p not in covered and p not in KNOWN_BLANK_PAGES]
    opener_only = [p for p in uncovered if stats[p]["body_chars"] == 0]
    real_gaps = [p for p in uncovered if stats[p]["body_chars"] > 0]
    L.append(f"\n## Gate 2 — page coverage: {len(covered)} pages in body chunks; uncovered with body text: {real_gaps} "
             f"{'✅' if not real_gaps else '❌'}; pages with no body text (openers/blank): {opener_only}\n")
    # --- gate 3: char conservation
    extracted = sum(s["body_chars"] for s in stats.values())
    in_chunks = sum(len(r["body_text"]) for r in body)
    L.append(f"## Gate 3 — body text conservation: extracted {extracted:,} chars (raw lines) vs {in_chunks:,} in chunks "
             f"({in_chunks / extracted:.1%}) {'✅' if 0.90 <= in_chunks / extracted <= 1.03 else '⚠️'}\n")
    # --- gate 4: footnote consistency
    refs = sorted({r for c in body for r in c["footnote_refs"]})
    unmatched_refs = [r for r in refs if r not in footnotes]
    orphan_fns = [n for n in footnotes if n not in set(refs)]
    gaps = [n for n in range(min(footnotes), max(footnotes)) if n not in footnotes] if footnotes else []
    L.append(f"## Gate 4 — footnotes: {len(refs)} distinct markers in body; markers without footnote text: {unmatched_refs[:20]}"
             f"{'…' if len(unmatched_refs) > 20 else ''}; footnotes never referenced: {orphan_fns[:20]}{'…' if len(orphan_fns) > 20 else ''}; "
             f"numbering gaps: {gaps[:20]}{'…' if len(gaps) > 20 else ''} "
             f"{'✅' if not unmatched_refs and not gaps else '⚠️'}\n")
    # --- gate 5: token histogram
    toks = [r["n_tokens"] for r in body]
    over = sum(1 for t in toks if t > TOTAL_MAX_TOKENS + 12)
    under = sum(1 for t in toks if t < MIN_TAIL_TOKENS)
    L.append(f"## Gate 5 — body chunk tokens (incl. prefix): min {min(toks)}, median {int(statistics.median(toks))}, "
             f"p90 {sorted(toks)[int(len(toks) * .9)]}, max {max(toks)}; > {TOTAL_MAX_TOKENS + 12}: {over}; < {MIN_TAIL_TOKENS}: {under} ({under / len(toks):.1%}) "
             f"{'✅' if over == 0 and under / len(toks) < 0.08 else '⚠️'} (short chunks are complete short sections; they are not merged across section boundaries)\n")
    hist = collections.Counter((t // 50) * 50 for t in toks)
    L.append("```\n" + "\n".join(f"{b:4d}-{b + 49:<4d} {'#' * hist[b]} {hist[b]}" for b in sorted(hist)) + "\n```\n")
    ftoks = [r["n_tokens"] for r in fns]
    if ftoks:
        L.append(f"Footnote chunk tokens: median {int(statistics.median(ftoks))}, max {max(ftoks)}, > 512: {sum(1 for t in ftoks if t > 512)}\n")
    # --- units table
    L.append("## Section units\n\n| section | title | pages | paragraphs | chunks |\n|---|---|---|---|---|")
    for u in units:
        n = sum(1 for r in body if r["section_id"] == u.section_id and r["chapter_no"] == u.chapter_no)
        L.append(f"| {u.section_id} | {u.section_title[:60]} | {u.page_start}–{u.page_end} | {len(u.paragraphs)} | {n} |")
    # --- spot checks
    random.seed(7)
    L.append("\n## Spot checks (10 random body chunks)\n")
    for r in random.sample(body, min(10, len(body))):
        L.append(f"### chunk {r['chunk_idx']} — {r['n_tokens']} tokens, refs {r['footnote_refs']}\n\n```\n{r['text'][:1200]}\n```\n")
    L.append("\n## Spot checks (5 random footnotes)\n")
    for r in random.sample(fns, min(5, len(fns))):
        L.append(f"```\n{r['text'][:600]}\n```\n")
    with open(path, "w", encoding="utf8") as f:
        f.write("\n".join(L))


# ----------------------------------------------------------------------------
# 5. Commands
# ----------------------------------------------------------------------------
def cmd_extract(args):
    os.makedirs(OUT_DIR, exist_ok=True)
    doc = pymupdf.open(PDF_PATH)
    units, footnotes, stats = extract_structure(doc)
    records = build_records(units, footnotes)
    jsonl = os.path.join(OUT_DIR, "furocad_book_pass1.jsonl")
    with open(jsonl, "w", encoding="utf8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    report = os.path.join(OUT_DIR, "furocad_book_pass1_report.md")
    write_report(units, footnotes, stats, records, load_toc(TOC_PATH), report)
    print(f"units={len(units)} body_chunks={sum(1 for r in records if r['kind']=='body')} footnotes={len(footnotes)}")
    print(f"wrote {jsonl}\nwrote {report}")


def point_id(kind: str, key: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"cognosa/{SOURCE_ID}/{kind}/{key}"))


def record_to_document(r: dict):
    from langchain_core.documents import Document
    md = {
        "source": SOURCE_ID,
        "source_type": "book",
        "source_title": SOURCE_TITLE,
        "source_author": SOURCE_AUTHOR,
        "source_year": SOURCE_YEAR,
        "kind": r["kind"],
        "chapter_no": r["chapter_no"],
        "chapter_title": r["chapter_title"],
        "section_id": r["section_id"],
        "section_title": r["section_title"],
        "breadcrumb": r["breadcrumb"],
        "page_start": r["page_start"],
        "page_end": r["page_end"],
        "chunk_idx": r["chunk_idx"],
        "ingest_run": INGEST_RUN,
    }
    if r["kind"] == "body":
        md["footnote_refs"] = r["footnote_refs"]
    else:
        md["note_no"] = r["note_no"]
        md["note_part"] = r.get("note_part", 1)
        md["note_parts"] = r.get("note_parts", 1)
        md["anchors_chunk_idx"] = r["anchors_chunk_idx"]
    return Document(page_content=r["text"], metadata=md)


def _load_into(ops, emb, collection: str, records: list[dict], recreate: bool):
    from langchain_qdrant import QdrantVectorStore
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    exists = ops.collection_exists(collection)
    if exists is None:
        sys.exit("Qdrant not reachable")
    if exists and recreate:
        ops.client.delete_collection(collection)
        exists = False
    if not exists:
        ops.create_collection(emb, collection)
    else:
        # idempotent re-load: drop this source's points first
        ops.client.delete(
            collection_name=collection,
            points_selector=Filter(must=[FieldCondition(key="metadata.source", match=MatchValue(value=SOURCE_ID))]),
        )
    store = QdrantVectorStore(client=ops.client, collection_name=collection, embedding=emb)
    docs = [record_to_document(r) for r in records]
    ids = [point_id(r["kind"], f"{r['note_no']}.{r.get('note_part', 1)}" if r["kind"] == "footnote" else str(r["chunk_idx"])) for r in records]
    B = 64
    for i in range(0, len(docs), B):
        store.add_documents(docs[i:i + B], ids=ids[i:i + B])
        print(f"  {collection}: {min(i + B, len(docs))}/{len(docs)}", end="\r", flush=True)
    info = ops.client.get_collection(collection)
    print(f"\n  collection '{collection}': {info.points_count} points, dim {info.config.params.vectors.size}")


def cmd_load(args):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from common.parsed_url import ParsedUrl
    from tasks_lib.vdb_lib.qdrant_ops import QdrantOps
    from langchain_huggingface import HuggingFaceEmbeddings

    jsonl = os.path.join(OUT_DIR, "furocad_book_pass1.jsonl")
    records = [json.loads(l) for l in open(jsonl, encoding="utf8")]
    body = [r for r in records if r["kind"] == "body"]
    fns = [r for r in records if r["kind"] == "footnote"]
    print(f"{len(body)} body -> '{COLLECTION}', {len(fns)} footnote -> '{FOOTNOTE_COLLECTION}' with {EMB_MODEL}")
    emb = HuggingFaceEmbeddings(model_name=EMB_MODEL, encode_kwargs={"normalize_embeddings": True})
    ops = QdrantOps(ParsedUrl.from_url(QDRANT_URL))
    if args.kind in ("all", "body"):
        _load_into(ops, emb, COLLECTION, body, args.recreate)
    if args.kind in ("all", "footnote"):
        _load_into(ops, emb, FOOTNOTE_COLLECTION, fns, args.recreate)


def cmd_check(args):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    from common.parsed_url import ParsedUrl
    from tasks_lib.vdb_lib.qdrant_ops import QdrantOps
    from langchain_huggingface import HuggingFaceEmbeddings
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    emb = HuggingFaceEmbeddings(model_name=EMB_MODEL, encode_kwargs={"normalize_embeddings": True})
    ops = QdrantOps(ParsedUrl.from_url(QDRANT_URL))
    coll = FOOTNOTE_COLLECTION if args.kind == "footnote" else COLLECTION
    res = ops.client.query_points(coll, query=emb.embed_query(args.query), limit=args.k, with_payload=True)
    for p in res.points:
        md = p.payload["metadata"]
        print(f"\n--- score {p.score:.3f} | {md['kind']} | {md['breadcrumb']} | pp {md['page_start']}-{md['page_end']}")
        print(p.payload["page_content"][:500])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("extract")
    p = sub.add_parser("load"); p.add_argument("--recreate", action="store_true"); p.add_argument("--kind", default="all", choices=["all", "body", "footnote"])
    p = sub.add_parser("check"); p.add_argument("query"); p.add_argument("-k", type=int, default=5); p.add_argument("--kind", default="body", choices=["body", "footnote"])
    args = ap.parse_args()
    {"extract": cmd_extract, "load": cmd_load, "check": cmd_check}[args.cmd](args)


if __name__ == "__main__":
    main()
