"""
Layer 1 of the cpa-c42t_collection load: file selection.

Runs before any parsing or embedding. Produces LOAD-MANIFEST.csv listing every
candidate file and what will happen to it, so the selection can be reviewed
before ~40,000 embeddings are computed.

See PLAN.md sections 3 and 4.3.
"""
import csv, hashlib, os, re, sys
from pathlib import Path

NEW      = Path("/Users/harry/Downloads/3-lit-review-sources-docs")
OLD      = Path("/Users/harry/Downloads/Cognosa_v0.1/documents_for_chromadb")
STAGING  = Path("/Users/harry/+_claude_projects_from_260807/p666_cpa_load/staging_converted")

# Types the document loader can parse. .doc is absent deliberately: the two that
# carry unique content were converted to .docx into STAGING, the other five are
# redundant with an existing .pdf/.docx twin.
SUPPORTED = {'pdf', 'docx', 'pptx', 'html', 'htm', 'txt', 'md', 'csv', 'xlsx'}

# Excluded by decision, not by failure. See ANALYSIS.md section 4.
EXCLUDED_BY_DECISION = {
    'essay scoring-1988-Wayne_Patience_Joan_Auchter-GED_testing-services.pdf':
        'illegible photocopy, no usable text layer (owner confirmed)',
    # No extractable text. Verified with pypdf 2026-09-01: zero characters across
    # all pages. Listed here so they are reported as decisions, not as failures,
    # which keeps a genuine parser breakage visible in the report.
    '052-original-1963-revised-report-on-algol-60-naurAlgol60.pdf':
        'page scans, no text layer; content loads from 052-revised-report-on-algol60-1963-retyped.pdf',
    '150_Detecting hoaxes, frauds, and deception in writing style online_2012_IEEE Xplore Full-Text PDF.pdf':
        'empty 3.8KB stub, 1 page, no text and no images',
    '311-powers-et-al-2001_STUMPING E‐RATER- CHALLENGING THE VALIDITY OF AUTOMATED ESSAY SCORING - Powers - 2001 - ETS Research.pdf':
        'empty 3.8KB stub, 1 page, no text and no images',
    'fragement-1.pdf':
        'single image, no text layer; content loads from fragement-1.png.pdf',
}

# Handled by the row-oriented loader, not the document loader. PLAN.md section 8.
ROW_ORIENTED = {'Ann_List_of_Sources-200704f.xlsx'}

# Present in collection_1 today, but superseded by a better treatment of the same
# content. Excluded deliberately, not by rule.
SUPERSEDED = {
    'Ann_List_of_Sources-200704_shared.xlsx':
        'earlier variant of Ann_List_of_Sources-200704f.xlsx, which is loaded row-by-row',
}

# EndNote citation exports masquerading as spreadsheets.
CITATION_XLSX = re.compile(r'^Annotated_List_of_.*EndNote.*\.xlsx$', re.I)

# Preference when one document exists in several formats.
FORMAT_RANK = {'pdf': 0, 'docx': 1, 'txt': 2, 'md': 3, 'pptx': 4,
               'html': 5, 'htm': 6, 'csv': 7, 'xlsx': 8}


def ext_of(p: Path) -> str:
    return p.suffix.lower().lstrip('.')


def stem_of(p: Path) -> str:
    s = p.stem
    if s.lower().endswith('.doc'):      # "x.doc.docx" -> "x"
        s = s[:-4]
    return s.lower()


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def collect():
    rows = []
    for root, corpus in ((NEW, 'new'), (OLD, 'existing'), (STAGING, 'converted')):
        if not root.exists():
            print(f"WARNING: {root} does not exist", file=sys.stderr)
            continue
        for p in sorted(root.rglob('*'), key=lambda x: str(x).lower()):
            if not p.is_file() or p.name == '.DS_Store':
                continue
            rows.append({'path': p, 'corpus': corpus})
    return rows


def main():
    rows = collect()
    ext_seen, stem_keep, hash_keep = {}, {}, {}
    out = []

    # Pass 1 - rule-based exclusion.
    for r in rows:
        p, e = r['path'], ext_of(r['path'])
        if p.name in EXCLUDED_BY_DECISION:
            r['status'], r['reason'] = 'excluded-by-decision', EXCLUDED_BY_DECISION[p.name]
        elif p.name in SUPERSEDED:
            r['status'], r['reason'] = 'skipped-superseded', SUPERSEDED[p.name]
        elif p.name in ROW_ORIENTED:
            r['status'], r['reason'] = 'row-oriented-loader', 'data table; see PLAN.md section 8'
        elif CITATION_XLSX.match(p.name):
            r['status'], r['reason'] = 'skipped-citation-list', 'EndNote annotated source list'
        elif e == 'rtf':
            r['status'], r['reason'] = 'skipped-citation-list', 'EndNote reference export'
        elif e == 'enw':
            r['status'], r['reason'] = 'skipped-citation-list', 'EndNote citation record'
        elif e == 'doc':
            r['status'], r['reason'] = 'skipped-superseded', 'legacy .doc; converted copy or twin used instead'
        elif e not in SUPPORTED:
            r['status'], r['reason'] = 'skipped-unsupported', f'.{e or "no extension"} not parseable'
        else:
            r['status'], r['reason'] = 'candidate', ''
        out.append(r)

    # Pass 2 - byte-identical duplicates.
    for r in out:
        if r['status'] != 'candidate':
            continue
        h = sha256(r['path'])
        r['sha256'] = h
        if h in hash_keep:
            r['status'] = 'skipped-duplicate-bytes'
            r['reason'] = f'byte-identical to {hash_keep[h].name}'
        else:
            hash_keep[h] = r['path']

    # Pass 3 - same document, different format.
    for r in out:
        if r['status'] != 'candidate':
            continue
        s, e = stem_of(r['path']), ext_of(r['path'])
        if s in stem_keep:
            prev = stem_keep[s]
            if FORMAT_RANK.get(e, 99) < FORMAT_RANK.get(ext_of(prev['path']), 99):
                prev['status'] = 'skipped-duplicate-format'
                prev['reason'] = f'same document as {r["path"].name}, lower-ranked format'
                stem_keep[s] = r
            else:
                r['status'] = 'skipped-duplicate-format'
                r['reason'] = f'same document as {prev["path"].name}, lower-ranked format'
        else:
            stem_keep[s] = r

    for r in out:
        if r['status'] == 'candidate':
            r['status'] = 'load'

    dest = Path('/Users/harry/+_claude_projects_from_260807/p666_cpa_load/LOAD-MANIFEST.csv')
    with dest.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['seqn', 'status', 'corpus', 'filename', 'ext', 'bytes', 'reason', 'abspath'])
        for i, r in enumerate(sorted(out, key=lambda x: (x['status'], str(x['path']).lower())), 1):
            p = r['path']
            w.writerow([i, r['status'], r['corpus'], p.name, ext_of(p),
                        p.stat().st_size, r['reason'], str(p)])

    from collections import Counter
    counts = Counter(r['status'] for r in out)
    print(f"{'status':<26} {'files':>6}")
    for k in sorted(counts):
        print(f"  {k:<24} {counts[k]:>6}")
    print(f"\n  {'TOTAL':<24} {len(out):>6}")
    print(f"\nmanifest -> {dest}")


if __name__ == '__main__':
    main()
