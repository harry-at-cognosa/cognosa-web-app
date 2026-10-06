# Component stack diagram

Flat layered view of the Cognosa web app: four columns (React SPA, `app` FastAPI
process, `rt` task processor, offline tools), the repo packages inside each in call
order, the third-party libraries at the foot of each column, the shared `common/`
package, and the data stores and LLM endpoints with the connections each process opens.
This is the diagram that shows where LangChain lives.

Published copy: https://claude.ai/artifact/NDqev3dkGHGW6SKsitCKfz

| File | Purpose |
|---|---|
| `gen_component_stack.py` | Generator. Panel contents are plain string lists; panels auto-size and wrap. |
| `page_head.html` / `page_tail.html` | Title, CSS tokens, lede / caption, key, LangChain table, process table. |
| `component_stack.svg` | Output: bare SVG. |
| `cognosa_component_stack.html` | Output: the full page. |
| `preview.py` | Optional Playwright screenshot to `preview.png`. |

Regenerate: `python3 docs/architecture/component_stack/gen_component_stack.py`
