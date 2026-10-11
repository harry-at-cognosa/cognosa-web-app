"""
Document loader for cpa-c42t_collection.

Forked from backend/document_loader_qdrant.py. The original is left in place because
other collections still use it.

Two things differ from the original, both deliberate:

  1. Point IDs are DETERMINISTIC - uuid5 over a normalised hash of the chunk text,
     instead of the random uuid4 that langchain_qdrant assigns by default. This makes
     the loader idempotent: re-running it overwrites rather than appends, and a chunk
     that already exists is not duplicated.

  2. Every file's outcome is RECORDED in a report CSV. The original swallowed parse
     failures with only a log line, which is how a PDF went missing from collection_1
     without anyone noticing.

Input is LOAD-MANIFEST.csv produced by cpa_select_files.py; only rows with
status == 'load' are processed.

Batch mode (2026-10-11, PLAN-batch-refresh_261011.md section 4.3): --batch labels
every point with metadata.cpa_batch, and IDs already present in the collection are
skipped before embedding, so an existing point is never re-embedded or overwritten
and a batch owns exactly the points it created.
"""
import argparse, csv, hashlib, re, sys, unicodedata, uuid
from collections import Counter
from multiprocessing import Pool
from pathlib import Path
from time import time

from langchain_community.document_loaders import (
    PyPDFLoader, Docx2txtLoader, UnstructuredPowerPointLoader,
    UnstructuredHTMLLoader, TextLoader, CSVLoader, UnstructuredExcelLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, OptimizersConfigDiff

MODEL             = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE        = 1000
CHUNK_OVERLAP     = 200
INDEXING_THRESHOLD = 50_000          # KB. Keeps search exact past ~166k points.

# Stable namespace so IDs are reproducible across runs and machines.
CPA_NAMESPACE = uuid.UUID("6f2a1c94-3b7d-5e18-9a4f-c42b00000000")

LOADERS = {
    'pdf':  PyPDFLoader,
    'docx': Docx2txtLoader,
    'pptx': UnstructuredPowerPointLoader,
    'html': UnstructuredHTMLLoader,
    'htm':  UnstructuredHTMLLoader,
    'txt':  lambda p: TextLoader(p, encoding='utf8', autodetect_encoding=True),
    'md':   lambda p: TextLoader(p, encoding='utf8', autodetect_encoding=True),
    'csv':  lambda p: CSVLoader(p, autodetect_encoding=True),
    'xlsx': UnstructuredExcelLoader,
}


def canonical(text: str) -> str:
    """Normalised form used for the content hash.

    NFKC matters: PDF extraction emits ligatures (collection_1 contains U+FB01 for
    'fi'), so raw bytes differ where the text does not.
    """
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', text)).strip()


def content_id(text: str) -> str:
    digest = hashlib.sha256(canonical(text).encode('utf-8')).hexdigest()
    return str(uuid.uuid5(CPA_NAMESPACE, digest))


def parse_one(row):
    """Parse and split one file. Runs in a worker process."""
    path, ext = Path(row['abspath']), row['ext']
    try:
        factory = LOADERS.get(ext)
        if factory is None:
            return row, [], f'no loader for .{ext}'
        docs = factory(str(path)).load()
        if not docs:
            return row, [], 'loader returned no documents'
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, length_function=len)
        chunks = splitter.split_documents(docs)
        if not chunks:
            return row, [], 'no chunks after splitting'
        out = []
        for c in chunks:
            if canonical(c.page_content):
                out.append({'text': c.page_content, 'metadata': dict(c.metadata)})
        if not out:
            return row, [], 'all chunks empty after normalisation'
        return row, out, ''
    except Exception as exc:
        return row, [], f'{type(exc).__name__}: {exc}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--manifest', required=True)
    ap.add_argument('--collection', default='cpa-c42t_collection')
    ap.add_argument('--host', default='localhost')
    ap.add_argument('--port', type=int, default=6333)
    ap.add_argument('--report', required=True)
    ap.add_argument('--processes', type=int, default=8)
    ap.add_argument('--batch-size', type=int, default=256)
    ap.add_argument('--append', action='store_true',
                    help='permit loading into a collection that already exists')
    ap.add_argument('--dry-run', action='store_true',
                    help='parse and deduplicate, write the report, embed nothing')
    ap.add_argument('--limit', type=int, default=0, help='process only the first N files')
    ap.add_argument('--batch', help='batch label written to metadata.cpa_batch; required with --append')
    args = ap.parse_args()
    if args.append and not args.batch:
        sys.exit("ERROR: --append requires --batch <label>")

    rows = [r for r in csv.DictReader(open(args.manifest, encoding='utf-8'))
            if r['status'] == 'load']
    rows.sort(key=lambda r: r['abspath'].lower())        # deterministic order
    if args.limit:
        rows = rows[:args.limit]
    print(f"{len(rows)} files to process")

    client = QdrantClient(host=args.host, port=args.port)
    exists = client.collection_exists(args.collection)
    if exists and not args.append and not args.dry_run:
        sys.exit(f"ERROR: collection '{args.collection}' already exists. "
                 f"Pass --append to add to it, or drop it first.")

    # ---- parse in parallel, results returned in submission order ----
    t0 = time()
    parsed, done = [], 0
    with Pool(processes=args.processes) as pool:
        for row, chunks, err in pool.imap(parse_one, rows):
            done += 1
            parsed.append((row, chunks, err))
            if done % 25 == 0 or done == len(rows):
                print(f"  parsed {done}/{len(rows)}  ({time()-t0:.0f}s)")

    # ---- deduplicate serially, first writer wins ----
    seen, per_row = {}, []
    for row, chunks, err in parsed:
        if err:
            per_row.append((row, None, 0, err))
            continue
        items, dropped = [], 0
        for c in chunks:
            pid = content_id(c['text'])
            if pid in seen:
                dropped += 1
                continue
            seen[pid] = row['filename']
            meta = dict(c['metadata'])
            meta['cpa_source_file'] = row['filename']
            meta['cpa_corpus'] = 'batch' if args.batch else row['corpus']
            if args.batch:
                meta['cpa_batch'] = args.batch
            meta['cpa_doc_kind'] = row.get('kind') or 'paper'
            items.append((pid, {'text': c['text'], 'metadata': meta}))
        per_row.append((row, items, dropped, ''))

    # ---- skip IDs already in the collection (never re-embed, never overwrite) ----
    existing = set()
    if exists:
        all_ids = [pid for _, items, _, err in per_row if not err for pid, _ in items]
        for i in range(0, len(all_ids), 1000):
            got = client.retrieve(args.collection, ids=all_ids[i:i + 1000],
                                  with_payload=False, with_vectors=False)
            existing.update(str(p.id) for p in got)

    docs, ids, report = [], [], []
    for row, items, dropped, err in per_row:
        if err:
            report.append((row, 'failed', 0, 0, 0, err))
            continue
        kept = present = 0
        for pid, d in items:
            if pid in existing:
                present += 1
                continue
            docs.append(d); ids.append(pid); kept += 1
        outcome = 'loaded' if kept else ('already-present' if present else 'all-chunks-duplicate')
        report.append((row, outcome, kept, dropped, present, ''))

    total_chunks = sum(len(c) for _, c, e in parsed if not e)
    print(f"\nparsed {total_chunks:,} chunks -> {len(docs):,} to upsert "
          f"({total_chunks - len(docs) - len(existing):,} collapsed as duplicate content, "
          f"{len(existing):,} already in collection)")
    print(f"expected_delta = {len(docs):,}")

    with open(args.report, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['filename', 'corpus', 'kind', 'ext', 'outcome', 'chunks_kept',
                    'chunks_dropped_dup', 'chunks_already_present', 'error', 'abspath'])
        for row, outcome, kept, dropped, present, err in report:
            w.writerow([row['filename'], row['corpus'], row.get('kind') or 'paper', row['ext'],
                        outcome, kept, dropped, present, err, row['abspath']])
    print(f"report -> {args.report}")
    for k, v in sorted(Counter(o for _, o, _, _, _, _ in report).items()):
        print(f"  {k:<24} {v:>5}")

    if args.dry_run:
        print("\ndry run: nothing embedded, nothing written to Qdrant")
        return

    # ---- create collection ----
    if not exists:
        emb_probe = HuggingFaceEmbeddings(model_name=MODEL)
        size = len(emb_probe.embed_query("test"))
        client.create_collection(
            collection_name=args.collection,
            vectors_config=VectorParams(size=size, distance=Distance.COSINE),
            optimizers_config=OptimizersConfigDiff(indexing_threshold=INDEXING_THRESHOLD),
        )
        print(f"created '{args.collection}' dim={size} "
              f"indexing_threshold={INDEXING_THRESHOLD}KB")

    if not docs:
        print("\nnothing to upsert")
        return

    # ---- embed and upsert ----
    from langchain_core.documents import Document
    store = QdrantVectorStore(client=client, collection_name=args.collection,
                              embedding=HuggingFaceEmbeddings(model_name=MODEL))
    t1 = time()
    for i in range(0, len(docs), args.batch_size):
        batch = docs[i:i + args.batch_size]
        store.add_documents(
            [Document(page_content=d['text'], metadata=d['metadata']) for d in batch],
            ids=ids[i:i + args.batch_size])
        print(f"  upserted {min(i+args.batch_size, len(docs)):,}/{len(docs):,} "
              f"({time()-t1:.0f}s)")

    info = client.get_collection(args.collection)
    print(f"\ndone in {time()-t0:.0f}s. points={info.points_count} "
          f"indexed={info.indexed_vectors_count}")


if __name__ == '__main__':
    main()
