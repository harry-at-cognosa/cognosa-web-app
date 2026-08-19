# FUROCAD — Phase 1 / Pass 1: ingesting the book's body text

**Collection theme:** *furocad* — Forensic UnReliability of CA (child-abuse) Diagnoses.
**Source:** Papetti, *The Forensic Unreliability of Shaken Baby Syndrome* (paperback, July 2024),
`/Users/harry/+_claude_projects_from_260807/p67_furocad_notes/SBS_Paperback_July_2024.pdf`
(TOC: `sbs_book_toc.txt`, same folder).
**Status:** implemented and loaded 2026-08-19 (`backend/tools/ingest_dev/furocad_book_loader.py`; report in `furocad_out/`). See §5 for what changed in implementation.

---

## 1. What the scan of the PDF established

| Fact | Value |
|---|---|
| PDF pages | 358; InDesign 19.4 export, full text layer, no bookmarks |
| Printed page *p* ↔ PDF index | PDF page = *p* + 18 (printed 1 = PDF 19) |
| Front matter | PDF 1–18 (title, copyright, about, contents, foreword, preface) — **skip** |
| Body (chapters 1–6) | printed 1–316 — **pass 1 scope** |
| Appendix | printed 317–334, 7 parts, 17 image pages, ArialNarrow 10 pt captions — pass 2 |
| Index | printed 335–340, Times 8 pt — skip |
| Body text volume | ≈237 K chars (≈60 K tokens) |
| Footnote volume | ≈410 K chars (≈100 K tokens) — **1.7× the body** |
| Chapter-opener images | 1 decorative image on each chapter first page (1, 9, 79, 199, 253, 313) — ignore |

### Typography is deterministic (every role has a unique size/font)

| Role | Font | Size | Position |
|---|---|---|---|
| Chapter number | MinionPro-Regular | 84 | chapter opener |
| Chapter title | Arial-BoldMT | 22 | chapter opener |
| `x.y` section heading | Arial-BoldMT | 16 | body |
| `x.y.z` subsection heading | Arial-BoldMT | 14 | body |
| `x.y.z.w` sub-subsection heading | Arial-BoldMT | 12 | body (ch. 5 only) |
| Body text | Times-Roman / Times-Italic | 11.9–12.1 | y > 60, above footnote rule |
| Footnote reference marks in body | Times-Roman | 7 (and SC700 6.3) | superscript |
| Footnote text | TimesNewRomanPSMT (+Italic) | 9 | bottom of page |
| Running head | Arial-BoldMT + ArialMT | 12 / 11.6 | y ≈ 33 (and a 2nd line y ≈ 47 on long titles) |
| Appendix figure labels | Arial-BoldMT | 14 | single letters A–M, p. 322+ |
| Index entries | Times-Roman | 8 | p. 335–340 |

**Validation already run:** a font-size rule over the whole book recovers **every** heading in
`sbs_book_toc.txt` (99 TOC entries, incl. all eleven `5.3.3.x`) on the TOC's stated page.
Multi-line headings (e.g. "2.1 The Role of Physicians in Evaluating / and Reporting Abuse")
appear as consecutive lines of the same size and must be joined.

Line-end soft hyphens are present as U+00AD (`controversy surround\xad / ing`); body line
pitch is 18 pt, footnote pitch 11 pt.

---

## 2. Design decisions for pass 1

### 2.1 Unit of structure: the *section unit*

Build a tree from the headings: **chapter → section → subsection → sub-subsection**.
A *section unit* is the body text between one heading and the next heading of any level,
with its printed page range. Chapter 1 and 6 are single units (no subsections); chapter
intros (text between the chapter title and `x.1`) are their own unit with `section = "x.0"`.

Section units vary enormously: `3.2.3 Retinal Hemorrhage` is 22 pages; `2.7.1 Mechanism/Name`
is 2. So the unit is the *context* boundary, not the chunk.

### 2.2 Chunking: structure-first, size-bounded, paragraph-aligned

1. Reconstruct paragraphs inside each unit (new paragraph = first-line indent or vertical gap
   > 1 line pitch; join soft-hyphenated line breaks; keep italics as plain text).
2. Split each unit into chunks of **target ≈ 350 tokens, hard max ≈ 450**, never breaking a
   paragraph unless a single paragraph exceeds the max (then split at sentence boundaries).
   Overlap: **one trailing sentence** of the previous chunk (cheap, avoids boundary loss,
   doesn't double-count whole paragraphs).
3. Do **not** use embedding-similarity ("semantic") breakpoint chunking for pass 1. The
   author's own section structure is a stronger semantic segmentation than cosine drift on a
   MiniLM/bge embedding, and it is deterministic and auditable. Revisit only if retrieval
   evaluation shows mid-section topic drift.

### 2.3 The "chapter head" prefix (your requirement)

Every chunk's **embedded text** is:

```
[Ch. 3 The Challenges › 3.2 The Collapse of the Pathophysiologic Premises › 3.2.3 Retinal Hemorrhage] (pp. 120–142)
<chunk body>
```

- The prefix is the full breadcrumb, not just the chapter name — it is what disambiguates
  "SBS findings as of 2001" (2.7.3) from "the same findings disputed" (3.2.x) from
  "the same findings in a Daubert frame" (5.3.3.x). It costs ~25–40 tokens per chunk.
- The same breadcrumb is also stored as separate metadata fields (below) so it can be
  used by Qdrant payload filters, not only by the embedding.
- The page range lets the LLM cite pages in answers, which matters for a legal audience.

### 2.4 Footnotes: separate chunks, linked, not inlined

The footnotes are the evidentiary apparatus of the book (case citations, study citations,
quoted parentheticals). They are 1.7× the body text. Inlining them would swamp the body
embeddings; dropping them loses the citations a legal/medical user will ask for.

Proposal:
- Body chunk text keeps footnote **markers** as `[^212]` tokens (so a retrieved body chunk
  still shows which notes support it).
- Each footnote becomes its own point, `kind = footnote`, embedded with a shorter prefix
  (`[Ch. 3 › 3.1.1 › footnote 212]`) and payload `anchors_body_chunk_id`, `page`, `note_no`.
  Footnotes that run over a page break are stitched by note number.
- Retrieval default for the group: **body chunks only** (payload filter `kind = body`) to keep
  the top-k semantically clean; a second "with citations" retrieval mode (or a post-retrieval
  expansion that pulls the footnotes referenced by the retrieved body chunks) is a
  pass-2/phase-2 feature. The data model supports it from day one.

### 2.5 Payload (Qdrant point metadata) per chunk

```
source_id:        "papetti_2024_sbs"          # stable id for the book
source_type:      "book"                       # later: "article"
source_title:     "The Forensic Unreliability of Shaken Baby Syndrome"
source_author:    "Papetti"
source_year:      2024
kind:             "body" | "footnote"
chapter_no:       3
chapter_title:    "The Challenges"
section_id:       "3.2.3"                      # "1.0" for a chapter intro / chapter 1
section_title:    "Retinal Hemorrhage"
breadcrumb:       "Ch. 3 The Challenges › 3.2 … › 3.2.3 Retinal Hemorrhage"
page_start:       120
page_end:         121
chunk_idx:        47                           # running index within the book
unit_chunk_idx:   3                            # index within the section unit
n_tokens:         362
footnote_refs:    [309, 310, 311]              # body chunks
note_no / anchors_body_chunk_id                # footnote chunks
ingest_run:       "pass1_2026-08-19"
```

Keep Cognosa's existing `metadata.*` conventions where they exist (check `qdrant_filters.py`
for the retrieval-filter keys the UI already knows) — e.g. `Category`/`Subcategory` could map to
`chapter_title`/`section_title` so the existing Retrieval Filters UI works unchanged.

### 2.6 Embedding model

All existing collections use `sentence-transformers/all-MiniLM-L6-v2` (384-d, **256-token
max sequence** — text beyond that is silently truncated). With a 350-token target chunk plus
a 30-token prefix, MiniLM would truncate roughly the last third of every chunk.

Recommendation: **`BAAI/bge-base-en-v1.5`** (768-d, 512-token window, strong on
English retrieval benchmarks, runs fine on Apple Silicon). The platform already supports
any HF model name per `group_vdbs` row (`gvdbs_emb_model`) and loads it on demand, so
this needs no code change — only the `group_vdbs` row and, for speed, adding it to
`RT_VDB_EMB_MODELS_PRELOAD` in `backend/.env`.
If you prefer to stay on MiniLM for consistency, drop the chunk target to ≈200 tokens and
shorten the prefix to chapter + section id only.

### 2.7 Collection and tenant

- One Qdrant collection **`furocad`** for the whole theme (book now, journal articles in
  phase 2), discriminated by `source_type` / `source_id` in the payload. One collection keeps
  cross-source retrieval trivial ("what does the book say vs. what do the articles say" is a
  filter, not a join).
- `group_vdbs` row under the tenant you designate (NAAG, group 4, is the natural home, or a
  new group). Created via the SU UI or a small SQL insert.

### 2.8 Delivery path

A standalone loader, `backend/tools/ingest_dev/furocad_book_loader.py`, writing directly
to Qdrant through the platform's own `QdrantOps`/`EmbModels` (same pattern as the Casambi v2
loader, so the collection is born compatible with the retrieval code). Not through
`doc_tasks`/`run_tasks` for pass 1 — that pipeline is for tenant uploads, and this ingestion
is curated and iterative. Two-stage, re-runnable:

1. **`extract`** → `furocad_book_pass1.jsonl` (one record per chunk, text + payload) and a
   human-readable `furocad_book_pass1_report.md` (units, pages, chunk counts, token
   histograms, any page not covered, any TOC heading not found). *This is the artifact to
   review before anything touches Qdrant.*
2. **`load`** → embeds the JSONL and upserts to Qdrant (idempotent: deterministic point ids
   from `source_id + kind + chunk_idx`, so re-loading replaces rather than duplicates).

### 2.9 Quality gates (pass/fail, automated in the report)

- All 99 TOC headings found, on the TOC page ± 0 (already true in the scan).
- Every printed page 1–316 contributes to ≥ 1 body chunk, except pages that are blank or
  chapter openers only (8, 78, 198, 252 — known blanks).
- Sum of chunk body characters ≈ body chars extracted (±2 %: overlap sentences).
- Footnote numbers in body markers ⊆ footnote chunks found; max/min note_no contiguous per
  chapter.
- Token histogram: no body chunk > 450 tokens; < 5 % under 120 tokens (tail of units).
- Spot-check set: 10 random chunks printed with breadcrumb for eyeball review.

### 2.10 Not in pass 1 (explicitly deferred)

- Appendix text and images (pass 2: figure captions + image descriptions via a vision model).
- Index (skip permanently; it adds no retrievable semantics).
- Front matter (foreword/preface) — could be added as `kind = front_matter` later; low value.
- Embedding-similarity chunking, hybrid/BM25 sparse vectors, re-ranking — phase-2 tuning.
- The "footnote expansion" retrieval mode — phase 2.

---

## 3. Open decisions (need your call)

1. **Embedding model:** `BAAI/bge-base-en-v1.5` (recommended) vs. stay on MiniLM.
2. **Tenant / group** for the `furocad` collection (NAAG = group 4?).
3. **Collection naming:** single `furocad` collection with `source_type` payload (recommended)
   vs. `furocad_book` now and `furocad_articles` later.
4. **Footnotes in pass 1:** ingest as linked `kind = footnote` points now (recommended — the
   extraction work is the same and it is cheap to carry) vs. body only.
5. **Chunk target:** ≈350 tokens / max 450 (recommended with bge) — or different.

## 4. Effort estimate

Extraction + report: half a day including the quality gates. Loader + Qdrant + `group_vdbs`
row + first retrieval smoke tests through the Cognosa UI: another half day. Pass 1 is a
one-day item once the five decisions above are made.

---

## 5. Implementation notes (2026-08-19)

All five open decisions were taken as recommended (bge-base-en-v1.5; group 4 NAAG; single
theme collection; footnotes ingested; 350/450 tokens). Result of the first extraction:

| metric | value |
|---|---|
| section units | 82 (= every chapter/section heading in the TOC; all on the TOC's page) |
| body chunks | 216, median 337 tokens incl. prefix, max 482, 13 short complete sections < 120 |
| footnotes | 884 (= 884 body markers, no gaps), 937 records after splitting 53 long notes ≤ 494 tokens |
| text conservation | 99.6 % of extracted body characters land in chunks |
| page coverage | all 312 text pages; 8, 78, 198, 252, 316 have no body text |

**One deviation from §2.4/§2.7:** footnotes are loaded into a sibling collection
`furocad_footnotes` rather than the same collection with a `kind` payload. Reason: the
platform's retrieval filters are user-selected per query and there is no way to configure a
fixed default filter on a `group_vdbs` row, and in a mixed collection the short,
citation-dense footnotes took 4 of the top-5 slots on every test query. Two `group_vdbs` rows
for NAAG (ids 8 and 9) expose them as "FUROCAD — … (text)" and "… (footnotes / citations)"
in the collection dropdown. The footnote points keep `anchors_chunk_idx` / `note_no`, so a
future "expand with citations" retrieval mode, or a platform-level `default_filter` on
`group_vdbs` (the better long-term fix — add to phase 2), needs no re-ingestion.

Hyphenation: line-end hyphens (soft U+00AD and hard) are joined without a space; the only
known casualty is the rare suspended hyphen ("second- or third-…"), accepted.

Retrieval smoke tests through `QdrantOps.get_docs` (k=4) hit the right section on every
probe and show the breadcrumb working across chapters (e.g. "lucid interval" → 2.7.8 *as
believed in 2001* and 3.3 *proof of lucid intervals*).
