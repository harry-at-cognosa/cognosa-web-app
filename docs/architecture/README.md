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

## Public copies on files.cognosa.net

`publish_s3.sh` regenerates the three pages, wraps each in a full HTML skeleton (the
committed pages have none because the claude.ai Artifact viewer supplies it), uploads
them to the bucket root with an explicit HTML content type, invalidates CloudFront, and
verifies the public URLs. Run it after any change you want visible to others:

```sh
docs/architecture/publish_s3.sh              # all three
docs/architecture/publish_s3.sh --dry-run    # everything except upload + invalidation
docs/architecture/publish_s3.sh --no-gen component_stack   # one diagram, committed HTML as is
```

| Diagram | Public URL |
|---|---|
| Deployment topology | https://files.cognosa.net/Cognosa_deployment_topology.html |
| Component stack | https://files.cognosa.net/Cognosa_component_stack.html |
| Query sequence | https://files.cognosa.net/Cognosa_query_sequence.html |

The header of the script lists the bucket, distribution id, cache policy, and the
AWS identity it expects.
