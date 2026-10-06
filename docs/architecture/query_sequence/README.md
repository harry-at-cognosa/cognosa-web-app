# Query sequence diagram

Swimlane sequence of one question: React SPA → app → Postgres `doc_tasks` → rt main
loop → VDB worker → Qdrant → LLM worker → LLM, and back to the SPA by polling. Each
step is numbered; pills on the Postgres lane show the `doc_tasks.status` value written
at that step (`common/enums/doc_task_status.py`). Replaces the older ChromaDB-era
sequence drawing.

Published copy: https://claude.ai/artifact/TYktZ7Nrzp9HpvFXJ1CMN9

| File | Purpose |
|---|---|
| `gen_query_sequence.py` | Generator. Steps are a list of `msg(from, to, lines, status)` / `act(lane, lines, status)` calls. |
| `page_head.html` / `page_tail.html` | Title, CSS tokens, lede / caption, status table, notes. |
| `query_sequence.svg` | Output: bare SVG. |
| `cognosa_query_sequence.html` | Output: the full page. |
| `preview.py` | Optional Playwright screenshot to `preview.png`. |

Regenerate: `python3 docs/architecture/query_sequence/gen_query_sequence.py`
