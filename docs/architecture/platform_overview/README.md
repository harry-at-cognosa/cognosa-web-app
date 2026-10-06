# Platform overview (executive level)

Two simple figures on one page, replacing the two original hand-drawn overviews:

1. **How a question is answered**: ten numbered steps across User, Web app, API server,
   RAG engine, Knowledge base, Language model. Corrected from the ChromaDB-era drawing.
2. **What the platform is made of**: seven layers from People down to Hosting. Corrected
   from the generic "Enterprise RAG" layer diagram (no Redis, S3, Weaviate, Vue, WebSocket).

Plain-language labels, no file names, one vector database, one generic model box. Same
colour families as the three detailed diagrams so the two levels read as one set.

| File | Purpose |
|---|---|
| `gen_platform_overview.py` | Generator for both figures and the page. |
| `page_head.html` / `page_mid.html` / `page_tail.html` | Title, CSS tokens, lede, the two captions, pointer to the detailed diagrams. |
| `request_flow.svg` / `platform_layers.svg` | Output: the two bare figures. |
| `cognosa_platform_overview.html` | Output: the full page. |
| `preview.py` | Optional Playwright screenshot to `preview.png`. |

Published copy: https://claude.ai/artifact/7XLHGZiAB3zKDEzWjnqiyU
Public copy: https://files.cognosa.net/Cognosa_platform_overview.html

Regenerate: `python3 docs/architecture/platform_overview/gen_platform_overview.py`
