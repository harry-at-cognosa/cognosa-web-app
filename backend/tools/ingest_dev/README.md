# ingest_dev — ad-hoc ingestion & retrieval-test scripts

Development scripts written during the Casambi collection work (Nov–Dec 2025).
Previously untracked in `~/cognosa_web_app/backend/`; versioned here 2026-08-19.
They are **not** part of the runtime (`webapp.py` / `run_tasks.py`) and are not
shipped to EC2.

| Script | Purpose |
|---|---|
| `casambi_document_loader_qdrant.py` | Multi-strategy chunker/loader for the Casambi corpus → Qdrant `casambi_collection` (classification by filename). |
| `casambi_document_loader_qdrant_v2.py` | Same, classification by folder structure **and** filename. Current version. |
| `inspect_qdrant_251204.py` | Dump collection info / sample points. |
| `filtered_search_test_251204.py` | Metadata-filtered similarity search smoke test (`*_results_251204.txt` = captured output). |
| `test_casambi_retrieval.py` | Retrieval test through Cognosa's own `QdrantOps` (`*_results_251227_run_1.log.txt` = captured output). |
| `test_casambi_interactive.py`, `_v2.py` | Interactive query REPL against the collection; v2 adds word/char counts. |

## Running

The scripts import `common` and `tasks_lib`, so run them as modules from `backend/`
with the project venv:

```bash
cd backend
../venv/bin/python -m tools.ingest_dev.test_casambi_interactive_v2
../venv/bin/python -m tools.ingest_dev.casambi_document_loader_qdrant_v2
```

Requires a running Qdrant (`URL_QDRANT_LOCAL` in `backend/.env`) and, for the
loaders, `python-docx` (now in `requirements.txt`).

## Caveats

- `DOCUMENTS_PATH = "../../documents_casambi"` in the loaders is **cwd-relative**.
  It resolved to `~/documents_casambi` only because the original checkout lived at
  `~/cognosa_web_app`. From any other checkout, edit the constant or symlink
  `<repo>/../documents_casambi` before running.
- `_251204` / `_251227` suffixes are capture dates (yymmdd), not versions.
- The loaders write directly to Qdrant; they bypass the `doc_tasks` queue and
  `run_tasks.py`.
