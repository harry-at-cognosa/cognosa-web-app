## [0.7.1] (2025-10-05)

#### changes:

1. `Login` page:
   Now allows login by `api_users.email` or `api_users.user_name`.

## [0.7] (2025-10-04)

#### changes:

1. Added git repository.

2. Added `group_llms` PostgreSQL table.
   Now each group can have several LLM.
   LLM types: dummy, ollama-local, ollama-remote

3. Added `backend/init_sql_data/group_llms.json` to use in `backend/init_sql_db.py` script.

4. changed `RAG documents` page:
   Now user must select LLM (if there are more than 1) to query documents.
   Also, added vertical scrolls for both (history and query) sides.

5. changed `Server Status` page:
   Added info about all LLM specified in `group_llms` PostgreSQL table.
   Each LLM is checked by `run_tasks.py` script.

6. Added `api_users`.`user_name`.
   It must be unique, have length from 3 to 32 characters. Allowed characters:
   a-z0-9\_-
   Constraints added to PostgreSQL and Pydantic/Sqlalchemy schema.

7. Added `backend/init_sql_data/api_users.json` to use in `backend/init_sql_db.py` script.
   No need to use `backend/create_user.py` during project installation.

## [0.6] (2025-09-28)

#### changes:

1. Added support for many vector db storages / collections for each group.
2. changed `RAG documents` page:
   If there are several vector db specified (in `group_vdbs` table),
   it will show select box at the top of query area.
   If storage/collection is not Ready, it will be listed last there.

3. changed `Server Status` page to show all `group_vdbs` rows
   and show checking status for each vectordb / collection.

4. Now we support 3 types of vector database storage types:
   chroma / qdrant / pgvector

5. Qdrant/pgvector separate scripts (in `/backend` folder):
   `check_pgvector.py`
   `check_qdrant_server.py`  
   `document_loader_pgvector.py`
   `document_loader_qdrant.py`
   Note: document loaders use multiprocessing.

## [0.5] (2025-09-21)

#### changes:

1. API routes changed to /api/v1
   See http://127.0.0.1:8000/docs

2. PostgreSQL table for tasks: `doc_tasks`

3. Added `doc_tasks`.`optional_text`.
   This is from "
   It will be send to LLM, but not used in vector db search.

4. Query Documents -> RAG Documents page:
   Added queries history list at the left.
   Grouped by Today / This week / Before.
   Each one can be deleted (button X at the right).

5. ChromaDB server has memory leakage. Will be changed to other vector db (PostgreSQL pg_vector ?).

## [0.4] (2025-09-14)

#### changes:

1. run_tasks script now has command line options (all are optional):
   -d - (optional) Dummy operations (ChromaDB and LLM are not needed).
   -s <number> - (optional) Secondary instance.
   There must 1 primary instance, and any number of secondary, each with unique number.

2. new PostgreSQL table: api_processes.
   There will be info about running processes and threads of run_tasks instances.
   Also, info about ChromaDB collections available (run_task_primary -> chromadb_pool).

3. Server Status (only for superusers for now) will show info from:
   `api_processes` and `vdb_status` PostgreSQL tables.
   There will be info for each run_tasks instance (primary, and secondary ones if running).
   Each running `python3 run_tasks.py [-s <number>]` means separate instance.
   Withing each run_tasks instance there will be shown several processes with their statuses.

   Next info table (VDB Status) will be about available ChromaDB collections (only used in `group_vdbs` PostgreSQL table)

4. Query Document -> RAG page now has Markdown LLM response window.

5. Query Document -> Manage Contexts page (unfinished)

6. .init_sql_data... files went to `/backend/.init_sql_data` folder.

## [0.3] (2025-09-07)

#### changes:

1. added PostgreSQL tables:
   `api_groups`
   `group_contexts`
   `group_vdbs`

2. redone run_tasks.py
   There are new parameters in .env file for it. Commented there.
   Now it will use multiprocessing to send queries to ChromaDB server.
   And threading to send queries to LLM.
   LLM answer is streamed to db / frontend, so it shows tokens as they appear.

3. frontend barely works, but can send full query:
   write input text, choose context, click on button Ask.

## [0.2] (2025-08-31)

#### added React + Bootstrap frontend

1. `api_users` PostgreSQL table
2. `create_user.py` script to make new user
3. `Login` page
4. `Document queries` page (simulation only for now)
5. `Password change` page
6. `Logout` function

---

## [0.1] (2025-08-24)

#### first tryouts
