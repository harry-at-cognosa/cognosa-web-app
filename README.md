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

6. create superuser (email, password, fullname, is_superuser, group_id = 1):

```
source ./venv/bin/activate
cd backend
python3 create_user.py -e john_smith@example.com -p 12345678 -f "John Smith" -s -g 1
```

#### run web app services

7. Terminal 1: install and run ollama (e.g. model: gemma3) in background:

```
ollama run gemma3
```

8. Terminal 2: run in background (wait until VDB Worker 1 and 2 will print ready in console):

```
source ./venv/bin/activate
cd backend
python3 run_tasks.py
```

9. Terminal 3: run in background:

```
source ./venv/bin/activate
cd backend
uvicorn webapp:app
```

10. Terminal 4: Run Vector DB server in background:

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

11. browse to webpage and test it: http://127.0.0.1:8000

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
