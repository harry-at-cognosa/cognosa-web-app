## [Unreleased]

1. LLM models moved to current vendor generation (data migration
   `backend/tools/sql/update_llm_models_260819.sql`, apply per environment):
   `claude-sonnet-4-5` -> `claude-sonnet-5`, `claude-opus-4-5` -> `claude-opus-5`,
   `gemini-2.5-flash` -> `gemini-3.7-flash`,
   `gpt-5-mini` -> `gpt-5.6-terra` (rows named "GPT 5") / `gpt-5.6-luna` (rows named "GPT 5 mini"),
   `qwen-plus` -> `qwen3.8-max`. Same defaults in `backend/.init_sql_data/group_llms.json`.

2. `backend/tasks_lib/llm_lib/llm_type_claude.py`: no longer sends `temperature`.
   Claude Opus 5 / Sonnet 5 / Opus 4.7+ reject sampling parameters with HTTP 400.
   Gemini 3.x, GPT 5.6 and Qwen 3.x work through the existing provider code unchanged.

3. `backend/tools/sql/`: new home for idempotent data-only migrations, with
   `apply_sql.py` (runs a script via the app's `DATABASE_URL`, `--dry-run` supported).

4. `backend/tools/ingest_dev/`: previously untracked Casambi loader / retrieval-test
   scripts are now versioned; `python-docx` added to `requirements.txt`.

## [0.21b] (2026-02-07)

1. `Query Documents` -> `Queries` page ->
   `Retrieval Filters`: now are sent to backend + loaded from history.
   For the same query, if user changes `Document Collection`, values are preserved for each `Document Collection`.

2. Apply `Retrieval Filters` to Qdrant db.
   Python Module: `/backend/tasks_lib/vdb_lib/qdrant_filters.py`.
   Common filters (text search as substring, case-sensitive):
   `Product Name`
   `SKU`
   `Type`
   `Product Series`
   `Select Category`
   `Select SubCat`
   `Brand`
   `Alias`
   Ledra specific filters:
   `Base/Alt`:
   if `base` it will use documents with key not exists/filled: metadata.alt_product_id
   if `alt` it will use documents with key filled: metadata.alt_product_id
   `Product ID`:
   if `Base/Alt` is `base`, then use path "metadata.base_product_id"
   if `Base/Alt` is `alt`, then use path "metadata.alt_product_id"
   in other cases, use both "metadata.base_product_id" "metadata.alt_product_id" as OR clause.

3. `GroupAdmin` -> `Queries` page:
   Show `Retrieval Filters` if specified in `Info` column for each query row.

4. Added auto-filling functionality for `Retrieval Filters` select fields:
   `Category`, `Subcategory`.
   `SuperUser` - > `VDBs` page -> table row edit -> `Refresh Metadata Indexes`:
   this switch will send refreshing task to `group_vdbs_tasks` table.
   This task will be fetched by `run_tasks.py`,
   then all `auto-fill` select paths values will be obtained from Qdrant collection
   and be written to `group_vdbs_select_values` table.

## [0.20a] (2026-02-01)

1. Added `group_vdbs`.`gvdbs_retr_filters`.
   Can be edited on `SuperUser` - > `VDBs` page.
   This JSON string will store `Retrieval Filters` for certain `group_vdbs` row.

2. `Query Documents` -> `Queries` page:
   added `Retrieval Filters`: table of current values + reset button + modal to edit values.
   This is shown only if `group_vdbs`.`gvdbs_retr_filters` is filled.

## [0.19a] (2026-01-25)

1. Added new columns:
   1.1. `api_groups`.`gvdbs_retr_params`
   Filled with copy of `api_settings` -> `gvdbs_def_retr_params` value.
   1.2. `group_vdbs`.`gvdbs_retr_params`
   Filled with copy of `api_groups`.`gvdbs_retr_params`, accordingly to `group_id`.

2. `SuperUser` -> `Groups` page:
   added editable: Retrieval Parameters for each `api_group` row.
   Default for new groups: `api_settings` -> `gvdbs_def_retr_params` value.

3. `SuperUser` -> `VDBs` page:
   added editable: Retrieval Parameters for each `group_vdbs` row.
   Default for new vdbs: `api_group`.`gvdbs_retr_params` value.

4. added `GroupAdmin` -> `Retrieval Parameters` page:
   edit `api_groups`.`gvdbs_retr_params` value for current group.
   Only for groupadmin users.

5. added `GroupAdmin` -> `VDBs` page:
   Table shows `group_vdbs` rows for current groupadmin user `group_id`.
   Allows to change: `enabled`, `gvdbs_name`, `gvdbs_seqn`, `gvdbs_retr_params` for existing rows.
   Only for groupadmin users.

6. `Query Documents` -> `Queries` page:
   `Search Options` renamed to `Retrieval Parameters`.
   Now it uses RP from `group_vdbs` row selected.
   If user is regular (neither superuser / groupadmin / contentmanager),
   `Retrieval Parameters` are not shown and used from:
   `group_vdbs`.`gvdbs_retr_params` - for Document Search (collection selected)
   or `api_groups`.`gvdbs_retr_params` - for No Document Search

## [0.18b] (2026-01-18)

Bug fix:

1. `GroupAdmin` -> `Queries` page:
   Now it shows only queries for current user's group_id.

## [0.18a] (2026-01-18)

Document Collection Retrieval Parameters changes:

1.  It was in `api_settings` -> `gvdbs_cfg_json`,
    now in `api_settings` -> `gvdbs_def_retr_params`.
    (defaults are copied from previous value)

2.  `SuperUsers` page - > `Api Settings` -> `gvdbs_def_retr_params`:
    SIM / MMR / SST default parameters are saved separately.

3.  `Query Documents` -> `Queries` page:
    If user clicks on history query,
    it will set one of SIM / MMR / SST parameters from history query, leaving others from default.
    If user clicks on `New Query`, parameters will change to default.

## [0.17b] (2025-12-14)

1. Added additional spinner while first loading of React libraries.

2. Using log rotation for docker compose containers:
   PostgreSQL, nginx, qdrant.

3. Added `release/.../update_ssl_cert.sh`
   Run this script on EC2 instance to update Let's Encrypt SSL certificate manually.
   SSL certificates are valid for 3 months.

4. Fixed and refactored auth by username. Now it works in `/docs` too.

## [0.16d] (2025-12-07)

Need to upgrade db:
`cd backend`
`alembic upgrade head`

1. `Query Documents` -> `Queries` page -> left panel:
   added `doc_tasks`.`doc_task_id` value for each history query.

2. Added `api_users`.`last_seen` + show it on pages:
   `GroupAdmin` -> `Users`
   `SuperUser` -> `Users`

3. Added `group_llms`.`enabled` and `group_vdbs`.`enabled`.
   These columns are editable on `SuperUsers` -> `LLM` and `VDBs` pages.
   Disabled VDBs/LLMs won't be checked and be shown on:
   `SuperUsers` -> `Server Status`
   `Query` page
   main index page

4. Added `api_settings` -> `gvdbs_cfg_json` option.
   This will be default value for `Queries` page -> `Document Collection` options.
   If not specified, will be filled to defaults on server start.

5. Added `GroupAdmin` -> `Queries` page.
   Similar to `SuperUser` -> `Doc Tasks` page, but with some restrictions.

6. `Query Documents` -> `Queries` page:
   Added `Search Option` -> `Reset` button. It will reset to defaults.
   Changed `Search Option` behaviour:
   On first load, it will set to defaults.
   If user clicks `New Query`, it will stay the same as previous query.
   If user clicks on history query, it will load values from history query.

## [0.15f] (2025-11-30)

1. Added new variants for `group_llms`.`gllms_type`: `chatgpt`, `gemini`.
   For these ones - use empty `API Base` url in `SuperUsers` -> `LLMs`.
   Added functionality for `Gemini`. Need to install python library:
   `pip install langchain-google-genai==3.1.0`

   Need to upgrade db:
   `cd backend`
   `alembic upgrade head`

2. Additional checks for LLM urls.
   Now no need to fill API Base URL for Claude LLMs.
   It will use `https://api.anthropic.com/v1` by default.

3. Less checks for public LLM API (ChatGPT, Gemini, Claude):
   only once in 5 minutes.

4. `Query Documents` -> `Queries` page:
   Added `Reload` buttons for `Document Collection` and `LLM` lists.
   Now non-ready VDBs and LLMs are marked:
   yellow (warning, mostly for ChromaDB) or red.
   Sort VDBs and LLMs by: (is ready?, seqn number).
   Not ready rows goes after ready ones.
   `No document search` will be the last anyway.

5. Added `SuperUser` -> `Change Group` option.
   There superuser can change his own:
   `group_id`
   `is_contentmanager`
   `is_groupadmin`
   Page will be reloaded after change.

6. `Query Documents` -> `Queries` page:
   If query parameters are the same as previously sent, user will be asked:
   `Query is the same as previous. Please, change something.`
   Added `Clone this query` button.
   Restrict usage of VDBs and LLMs marked red (on both frontend and backend).

7. Fixes:
   `Query Documents` -> `Queries` page:
   clone current query if it is being deleted on left panel.
   `SuperUser` -> `LLMs` and `VDBs` pages:
   Set new VDBs and LLMs statuses as `danger`: `Not checked yet`.

8. Added spinner on `after login` redirection page.

## [0.14g] (2025-11-22)

1. Updates for pushing to GitLab:
   Secrets removed from git repo.
   React public libraries are now compiled separately to `static` folder.
   Added `static` and `release` folders to git repo.
   Python libraries version numbers now are frozen.
   Langchain libraries are updated to the latest.

2. Moved webapp to `/app` route.
   Added index page from `api_settings` -> `index_page` value.
   Current routes:
   `/` - Index page
   `/login` - Login page
   `/app/*` - Web app page

3. `SuperUser` -> `Api Settings` page:
   added `Add` row function. Currently only for options:
   `app_version`
   `db_version`
   `webapp_main_color`
   `index_page`

4. Now only authorized users can get `/app` page.
   Non-authorized will be redirected to `/login` page,
   frontend libraries will not be downloaded by them.

5. Added `/app` index page for authorized users.
   There will be:
   Description card and link to `Query Documents` -> `Queries` page.
   App / DB versions.
   Available VDB and LLM tables (for current user group_ip):
   `name` and `status` (Ready or error)

6. Generic tables:
   Pagination limit control now can be edited, or selected from list.
   Order column is marked by color.
   Added Export to Excel/JSON for each row (in `View` modal dialog).
   Now table cells are dimmed while page reloading.

## [0.13h] (2025-11-16)

1. `Document Queries` page:
   Set search type from history queries.
   Set default search type for a new query.
   Various bugfixes.

2. Generic tables -> Create / Update values dialog:
   Show description for each field.
   Added input validation.
   Show errors for each field after Save.
   Applied to pages/tables:
   `Query Documents`->`Manage Contexts`
   `GroupAdmin`->`Users`
   `SuperUser`->`Users`

3. Generic tables: miscellaneous visual updates.

4. `SuperUser`->`Doc Tasks` table:
   Added export (current rows) to Excel file.
   File is made on frontend (client's side).

5. `Document Queries` page:
   Added "No Document search, use only LLM" option as another `Document Collection` select choice.
   If it is chosen, question (and optional instruction) will be sent to LLM without vector db search.

6. `Document Queries` page:
   Added `Found Documents (...)` button that will show modal with all found documents.
   Only for superusers.

7. `SuperUser`->`Doc Tasks` table:
   Added export (current rows) to JSON file.
   File is made on frontend (client's side).

8. `Query Documents` page:
   Added second follow-up question ability.
   User can change all options and question.
   Second request will rewrite everything in `doc_tasks`,
   leaving only first answer from LLM in `doc_tasks`.`output_text`.
   Second answer will be in `doc_tasks`.`output_text_2`.
   Also will be updated `doc_tasks`.`question_number`.
   Sequence number of question will be saved in `doc_tasks`.`context_json` -> `question_seqn` number.

   Need to upgrade db:
   `cd backend`
   `alembic upgrade head`

## [0.12c] (2025-11-09)

1. Generic tables: added default order by/dir.
   Specified `desc` for `SuperUser` -> `Doc Tasks` and `Log CRUD`

2. Added pagination controls for all tables:
   Button `fast-backward` - goes to offset 0;
   Button `backward` - previous page;
   Button `forward` - next page;
   Button `fast-forward` - last page;
   Label `a-b/c`, where
   `a` - displayed rows first number (from 1),
   `b` - displayed rows last number,
   `c` - total rows that can be displayed;
   Select box with `5/10/20` rows per page.

3. Using Alembic to upgrade PostgreSQL db.
   Install python library:
   `pip install alembic`
   Upgrade db:
   `cd backend`
   `alembic upgrade head`

4. Added `doc_tasks`.`gvdbs_cfg_json`.
   This is configurable on `Document Queries` page (top right corner).
   This can be used to choose different vector db search parameters:
   `search_type` - Defines the type of search that the Retriever should perform.
   Can be `similarity` (default), `mmr`, or `similarity_score_threshold`.
   `search_kwargs` - Keyword arguments to pass to the search function. Can include things like:
   `k`: Amount of documents to return (Default: 10)
   `score_threshold`: Minimum relevance threshold for `similarity_score_threshold`. (Default: 0.5)
   `fetch_k`: Amount of documents to pass to `MMR` algorithm (Default: 20)
   `lambda_mult`: Diversity of results returned by `MMR`; 1 for minimum diversity and 0 for maximum. (Default: 0.5)
   Also visible on `SuperUsers` -> `Doc Tasks` page.

5. `SuperUser` -> `Doc Tasks` and `Log CRUD` pages:
   added `View` button to tables. Click on it will show vertical modal with row values.

## [0.11b] (2025-11-02)

Changes for initial deploy:

1. harder default user passwords

2. Added VDB/LLM URLs like:
   ollama_local
   qdrant_local
   pg_local
   chroma_local
   They are taken from .env, e.g. URL_OLLAMA_LOCAL.

3. Separate requirements.txt for:
   run_tasks.py: req_run_tasks.txt
   webapp.py: req_webapp.txt

4. Rewrote sql connections for run_tasks due different type of process spawning on Linux.

5. Added `release` folder. Check out `release/.../!README.MD`.

6. Updated `SuperUsers -> Users` page:
   Only for superusers.
   CRUD operations on `api_users` PostgreSQL table.
   Disable edit for himself: `user_name`, `email`, `is_active`, `is_superuser`.
   Create/edit: error if user_name or email existing.
   Delete: cannot delete himself.
   Note: errors are not showing for now. Will just do nothing.

7. `SuperUsers`/`GroupAdmin` -> `Users` pages:
   deleting user will change `api_users` columns:
   `deleted` = 1
   `email` = `deleted_{user_id}__<email>`
   `user_name` = `deleted_{user_id}__<user_name>`
   So superuser or groupadmin can delete and made user with same email/user_name.

8. Added `SuperUsers -> Doc Tasks` page:
   view/delete `doc_tasks` PostgreSQL table values.

9. Added `SuperUsers -> Log CRUD` page:
   view/delete `log_crud` PostgreSQL table values.

## [0.10c] (2025-10-26)

1. added:
   Ability to use Anthropic API - Claude LLM models.
   `requirements.txt` changed.

2. added `api_settings` -> `webapp_main_color` option.
   This relates to background colors of top navigation bar
   and some elements on RAG Documents page.
   Default: gray.
   Can be one of:
   slate, gray, zinc, neutral, stone, red, orange,
   amber, yellow, lime, green, emerald, teal, cyan,
   sky, blue, indigo, violet, purple, fuchsia, pink, rose.

3. Renamed RAG Documents to Query Documents.

4. All Superuser routes now have prefix `/su/`
   and now are "protected" - redirect to login if user is not superuser.
   All Superuser pages are under `SuperUser` dropdown.

5. added `SuperUsers -> Api Settings` page:
   view/edit existing `api_settings` PostgreSQL table values.
   Theme color changes on-the-fly after editing.

6. added `GroupAdmin -> Users` page:
   Only for groupadmins.
   CRUD operations on `api_users` PostgreSQL table.
   View/edit: only it's own group users, without superadmins (if it is not himself).
   Edit for other users: `user_name`, `full_name`, `email`, `password`, `is_active`, `is_contentmanager`, `is_groupadmin`.
   Edit for himself: only `full_name`, `password`, `is_contentmanager`.
   Create/edit: error if user_name or email existing.
   Delete: only it's own group users, without superusers or himself.
   Note: errors are not showing for now. Will just do nothing.

7. fixed `/logout`. Should work fine now.

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
