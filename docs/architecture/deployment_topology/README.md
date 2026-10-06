# Deployment topology diagram

Isometric ("2.5D") view of where each runtime piece of the Cognosa web app lives:
the per-environment EC2 app host (dev solid; demo and prod ghosted), its six Docker
Compose containers and their volumes, the GPU Ollama host, the four cloud LLM APIs,
and the AWS and external services around them.

Published copy: https://claude.ai/artifact/Re8RXKLNKDPeAYqf2Rhj4Z

| File | Purpose |
|---|---|
| `gen_deployment_topology.py` | Generator. Edit this to move, add, or relabel anything. |
| `page_head.html` | Title, CSS tokens (light + dark), lede. |
| `page_tail.html` | Caption, colour key, host and container tables. |
| `deployment_topology.svg` | Output: bare SVG, no scripts or external refs. |
| `cognosa_deployment_topology.html` | Output: the full page. |
| `preview.py` | Optional: screenshot the page with Playwright to `preview.png`. |

Regenerate after editing:

```bash
python3 docs/architecture/deployment_topology/gen_deployment_topology.py
python3 docs/architecture/deployment_topology/preview.py   # optional look
```

Conventions: arrows point from the client that opens the connection to the service
that listens. Only Qdrant is drawn; ChromaDB and pgvector are drop-in alternatives
behind the same `group_vdbs` config. Dashed outlines are replicated or alternate
instances.

Companion diagrams planned for this folder: component / software stack, and the
query sequence (see docs/PROJECT_STRUCTURE.md for the prose version).
