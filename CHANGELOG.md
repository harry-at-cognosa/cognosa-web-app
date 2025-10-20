## [0.9e] (2025-10-19)

1. fixed:
   retained previous history queries on another user login.

2. added `doc_tasks` columns:
   `gvdbs_json` - JSON dictionary with vector db credentials
   `gllms_json` - JSON dictionary with LLM credentials
   Note: these VDB/LLM credentials will be used,
   even if current `group_vdb`/`group_llm` row was changed during request.
   `vdb_query_seconds` - vector db query time in seconds
   `llm_query_seconds` - llm query time in seconds
   `llm_tokens_sent` - calculated tokens number sent to LLM.
   `llm_tokens_received` - calculated tokens number received from LLM.
   Note: tokens calculation can be not exact.
   Uses `gpt4o` model token calculation as default.

3. `RAG Documents` page:
   Show info: `VectorDB/LLM time: .../... Tokens Sent/Recv: .../...`
   Show less white space in the LLM answer window.

4. `Server Status` page:
   Show info `api_settings` -> `app_version` and `db_version`

5. Changed `GET /users/me` route to give out `api_groups`.`group_name` of logged user group.
   Top navigation bar: added `group_name` of currently logged user.

6. Added web manifest and icons.

7. `Manage Contexts` and `Manage Users` pages:
   added `sort by column` ability.

8. Added `Groups` page:
   CRUD operations for `api_groups` PostgreSQL table.
   Only for superusers.

9. Added `LLMs` page:
   CRUD operations for `group_llms` PostgreSQL table.
   Only for superusers.

10. Added `VDBs` page:
    CRUD operations for `group_vdbs` PostgreSQL table.
    Only for superusers.

11. Added "Reload" button to all CRUD tables.

## [0.8] (2025-10-12)

1. Added `doc_tasks`.`sent_to_llm`.
   Here will be full request to LLM. For debugging purposes.

2. Added `deleted` column to PostgreSQL tables:
   `api_groups`, `api_users`, `doc_tasks`, `group_contexts`, `group_llm`, `group_vdbs`.
   Will be used for "logical" deletion.
   Default: 0.
   `deleted` = 1 means row was deleted.

3. Added generic table CRUD operations:
   Create new row,
   update existing row,
   delete existing row (or set deleted = 1)

4. `Manage Contexts` page:
   Allow add new row.
   Allow update row.
   Allow delete (set `group_contexts`.`deleted` = 1).
   Won't show deleted rows, and on RAG documents page too.

5. Added `log_crud` PostgreSQL table.
   It will save info for each CRUD operation:
   `dt` - operation datetime
   `group_id`, `user_id`, `user_name` - user info
   `source_addr` - ip address of the user
   `method` - HTTP methods: GET / POST / PUT / DELETE
   `dest_addr` - server url, e.g. http://127.0.0.1:8000/manage_contexts/1
   `data` - request data
   `result` - result of operation

6. RAG Documents options (Contexts, VDBs, LLMs) are now fetched by /doc_tasks/options

## [0.7.1] (2025-10-05)

#### changes:

1. `Login` page:
   Now allows login by `api_users.email` or `api_users.user_name`.

2. `Manage Contexts` page:
   updated `Manage Contexts` table (currently only view).

3. New page `Users` (for superusers only).
   There is `Manage Users` table (currently only view).

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
