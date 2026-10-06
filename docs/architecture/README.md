# Architecture diagrams

Three generated diagrams, each in its own folder with a Python generator that emits
plain inline SVG (no Mermaid, no JavaScript) plus the HTML page around it.

| Folder | Diagram | Question it answers |
|---|---|---|
| [`deployment_topology/`](deployment_topology/) ([published](https://claude.ai/artifact/Re8RXKLNKDPeAYqf2Rhj4Z)) | Isometric deployment view | What runs where: EC2 hosts, compose containers, Ollama GPU host, cloud LLM APIs, supporting services |
| [`component_stack/`](component_stack/) ([published](https://claude.ai/artifact/NDqev3dkGHGW6SKsitCKfz)) | Layered component / software stack | What the code is made of: processes, packages, libraries (including LangChain), shared package, stores |
| [`query_sequence/`](query_sequence/) ([published](https://claude.ai/artifact/TYktZ7Nrzp9HpvFXJ1CMN9)) | Numbered swimlane sequence | What happens to one question, step by step, with the `doc_tasks.status` state machine |

Each folder's README has the file list and the regenerate command. Edit the generator
or the page parts, rerun, and republish the HTML to the same artifact URL (listed in each README).
