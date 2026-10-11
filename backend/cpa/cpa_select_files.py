"""
Layer 1 of a cpa-c42t_collection load: file selection.

Runs before any parsing or embedding. Produces a LOAD-MANIFEST.csv listing every
candidate file and what will happen to it, so the selection can be reviewed
before anything is embedded.

Batch mode (2026-10-11): scan only the folder(s) given with --root, label every
row with a batch id, and mark files whose stem is already present in the
collection as skipped-already-loaded. The September 2026 rebuild scanned three
fixed roots; that manifest is kept in p666_cpa_load/LOAD-MANIFEST.csv.

See PLAN.md sections 3 and 4.3, and PLAN-batch-refresh_261011.md section 4.2.
"""
import argparse, csv, hashlib, re, sys
from collections import Counter
from pathlib import Path

# Types the document loader can parse. .doc is absent deliberately: convert to
# .docx with `textutil -convert docx` into the batch folder first.
SUPPORTED = {'pdf', 'docx', 'pptx', 'html', 'htm', 'txt', 'md', 'csv', 'xlsx'}

# Excluded by decision, not by failure. See ANALYSIS.md section 4.
EXCLUDED_BY_DECISION = {
    'essay scoring-1988-Wayne_Patience_Joan_Auchter-GED_testing-services.pdf':
        'illegible photocopy, no usable text layer (owner confirmed)',
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

# Present in collection_1 once, superseded by a better treatment of the same content.
SUPERSEDED = {
    'Ann_List_of_Sources-200704_shared.xlsx':
        'earlier variant of Ann_List_of_Sources-200704f.xlsx, which is loaded row-by-row',
}

# EndNote citation exports masquerading as spreadsheets.
CITATION_XLSX = re.compile(r'^Annotated_List_of_.*EndNote.*\.xlsx$', re.I)

# Preference when one document exists in several formats.
FORMAT_RANK = {'pdf': 0, 'docx': 1, 'txt': 2, 'md': 3, 'pptx': 4,
               'html': 5, 'htm': 6, 'csv': 7, 'xlsx': 8}

# Files that are Harry's own analysis notes rather than sources.
NOTE_EXT = {'md'}

BATCH_SUFFIX = re.compile(r'_(\d{6}[a-z]?)$')


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


def collect(roots, batch):
    rows = []
    for root in roots:
        if not root.exists():
            sys.exit(f"ERROR: {root} does not exist")
        for p in sorted(root.rglob('*'), key=lambda x: str(x).lower()):
            if not p.is_file() or p.name.startswith('.') or p.name.upper().startswith('LOAD-'):
                continue
            rows.append({'path': p, 'corpus': batch})
    return rows


def loaded_stems(host, port, collection):
    """Stems of every cpa_source_file already in the collection."""
    from qdrant_client import QdrantClient
    from qdrant_client.models import PayloadSelectorInclude
    client = QdrantClient(host=host, port=port)
    if not client.collection_exists(collection):
        print(f"WARNING: collection '{collection}' does not exist; no already-loaded check",
              file=sys.stderr)
        return set()
    stems, offset = set(), None
    while True:
        pts, offset = client.scroll(
            collection, limit=2000, offset=offset, with_vectors=False,
            with_payload=PayloadSelectorInclude(include=['metadata.cpa_source_file']))
        for pt in pts:
            pl = pt.payload or {}
            name = (pl.get('metadata') or {}).get('cpa_source_file') or pl.get('metadata.cpa_source_file')
            if name:
                stems.add(stem_of(Path(name)))
        if offset is None:
            break
    return stems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', action='append', required=True, type=Path,
                    help='folder to scan; repeatable')
    ap.add_argument('--batch', help='batch label; default: trailing _YYMMDD of the first root')
    ap.add_argument('--manifest', type=Path, help='output CSV; default <first root>/LOAD-MANIFEST.csv')
    ap.add_argument('--collection', default='cpa-c42t_collection')
    ap.add_argument('--host', default='localhost')
    ap.add_argument('--port', type=int, default=6333)
    ap.add_argument('--no-collection-check', action='store_true',
                    help='skip the already-loaded check against Qdrant')
    args = ap.parse_args()

    batch = args.batch
    if not batch:
        m = BATCH_SUFFIX.search(args.root[0].name)
        if not m:
            sys.exit("ERROR: --batch not given and first --root does not end in _YYMMDD")
        batch = m.group(1)
    dest = args.manifest or (args.root[0] / 'LOAD-MANIFEST.csv')

    rows = collect(args.root, batch)
    stem_keep, hash_keep = {}, {}
    out = []

    # Pass 1 - rule-based exclusion.
    for r in rows:
        p, e = r['path'], ext_of(r['path'])
        r['kind'] = 'note' if e in NOTE_EXT else 'paper'
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
            r['status'], r['reason'] = 'skipped-unsupported', 'legacy .doc; convert to .docx with textutil first'
        elif e not in SUPPORTED:
            r['status'], r['reason'] = 'skipped-unsupported', f'.{e or "no extension"} not parseable'
        else:
            r['status'], r['reason'] = 'candidate', ''
        out.append(r)

    # Pass 2 - byte-identical duplicates within the batch.
    for r in out:
        if r['status'] != 'candidate':
            continue
        h = sha256(r['path'])
        if h in hash_keep:
            r['status'] = 'skipped-duplicate-bytes'
            r['reason'] = f'byte-identical to {hash_keep[h].name}'
        else:
            hash_keep[h] = r['path']

    # Pass 3 - same document, different format, within the batch.
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

    # Pass 4 - already in the collection (by filename stem). Chunk-level overlap
    # is caught in the loader by content ID.
    already = set() if args.no_collection_check else loaded_stems(args.host, args.port, args.collection)
    for r in out:
        if r['status'] == 'candidate' and stem_of(r['path']) in already:
            r['status'] = 'skipped-already-loaded'
            r['reason'] = f'a file with this stem is already in {args.collection}'

    for r in out:
        if r['status'] == 'candidate':
            r['status'] = 'load'

    with dest.open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['seqn', 'status', 'corpus', 'kind', 'filename', 'ext', 'bytes', 'reason', 'abspath'])
        for i, r in enumerate(sorted(out, key=lambda x: (x['status'], str(x['path']).lower())), 1):
            p = r['path']
            w.writerow([i, r['status'], r['corpus'], r['kind'], p.name, ext_of(p),
                        p.stat().st_size, r['reason'], str(p)])

    counts = Counter(r['status'] for r in out)
    print(f"batch {batch}   {'status':<26} {'files':>6}")
    for k in sorted(counts):
        print(f"  {k:<24} {counts[k]:>6}")
    print(f"\n  {'TOTAL':<24} {len(out):>6}")
    print(f"\nmanifest -> {dest}")


if __name__ == '__main__':
    main()
