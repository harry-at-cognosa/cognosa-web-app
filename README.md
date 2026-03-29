## Overview
Cognosa is a well-tested, multi-tenant Retrieval-Augmented Generation (RAG) platform. It enables organizations (tenants) to vectorize their proprietary documents, store them in tenant-isolated vector database collections, and give their users access to multiple open-source and proprietary LLMs for question answering against that data.

It is more fully described at [files.cognosa.net/cognosa-info](http://files.cognosa.net/cognosa-info/).

The platform has three runtime components:

1.	FastAPI web server (webapp.py) — serves the React SPA and all REST API endpoints
2.	Background task processor (run_tasks.py) — multiprocessing VDB workers + threaded LLM workers that execute the RAG pipeline
3.	React + TypeScript frontend — Bootstrap-based UI with real-time query polling and streaming LLM response display

__Version:__ 0.19a (2026-01-25) — see CHANGELOG.md for full history (development began August 2025).
__Database:__ PostgreSQL (cwa_db), with any of optional Qdrant, ChromaDB, or pgvector for vector storage.
__LLMs:__ Models from Anthropic, Google, Alibaba, Meta and others via API key, as well as local and remote Ollama hosted open source models.



### Steps to run

#### install procedures:

0. Create vector databases accordingly specified in `group_vdbs` PostgreSQL table
   (filled from `/backend/.init_sql_data/group_vdbs.json`)

1. Create PostgreSQL database: cwa_db
   (Cognosa Web App db)

2. Go the project root folder.
   Create Virtual enviroment and install Python libraries:

```
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

3. check `/backend/.env` PostgreSQL credentials: login, password, host, port, db

4. check `/backend/.api_settings_init_data.json` file: llm settings (should work like defaults)

5. init PostgreSQL `cwa_db` database (it will use `.init_sql_data_*.json` files):

```
source ./venv/bin/activate
cd backend
python3 init_sql_db.py
```

#### run web app services

6. Terminal 1: install and run ollama (e.g. model: gemma3) in background:

```
ollama run gemma3
```

7. Terminal 2: run in background (wait until VDB Worker 1 and 2 will print ready in console):

```
source ./venv/bin/activate
cd backend
python3 run_tasks.py
```

8. Terminal 3: run in background:

```
source ./venv/bin/activate
cd backend
uvicorn webapp:app
```

9. Terminal 4: Run Vector DB server in background:

For pgvector: it should use existing PostgreSQL instance.

For Qdrant: see os-specific instructions. Should be just:

```
qdrant
```

For ChromaDB (specify path to your chroma_db):

```
source ./venv/bin/activate
chroma run --port 8010 --path .\chroma_db\
```

10. browse to webpage and test it: http://127.0.0.1:8000

---

### (unimportant, already done) Frontend compilation to /backend/static folder:

1. install NodeJS and npm anyhow
2. run in terminal (from project root folder):

```
cd frontend
npm install
npm build
```

Notes:
npm modules to install are specified in `package.json`.
Build options are specified in `vite.config.ts`.
If npm install shows error "npm error ERESOLVE unable to resolve dependency tree", use instead:
`npm install --legacy-peer-deps`
