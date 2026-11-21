# Conversation mode — implementation plan

Written 2026-11-20 against `main` at `72d64f1`. Implements
`docs/conversation_mode_design_261120.md` (fifteen decisions, no open points). Nothing in
this plan has been built.

Working rules: all work on branch `feature/conversation-mode`; one slice at a time; stop
after each slice for review; `main` is touched only by the final merge.

---

## 1. Findings from the code that adjust the design

These came out of reading the code for this plan. Items 1 and 2 changed statements in the
design document; both were agreed on 2026-11-20 and the design is corrected. Items 3–5 are
implementation facts.

1. **The filter conversion is not fully generic.** `tasks_lib/vdb_lib/qdrant_filters.py`
   contains handling keyed on `sub_type` values beginning `ledra_`. The design document
   calls this module generic. New chat code will name no collection field, but it will
   reuse this module as it is, so chat inherits the same Ledra-specific branch that
   `Queries` already has. Agreed: accepted. The design now states that filtering is not a
   fully generic capability (its section 8).
2. **Qdrant only in the first version.** The multi-backend dispatcher (`vdb_ops.py`)
   cannot be imported outside `run_tasks`, because `tasks_lib/cmd_line_opts.py` parses the
   command line at import. `qdrant_ops.py` has no such dependency and can be used directly,
   which also guarantees chat retrieves exactly as `Queries` does. Every enabled collection
   in groups 1–4 is Qdrant; the pgvector and Chroma rows are disabled. Agreed: chat lists
   Qdrant collections only, and there is no plan to support pgvector or Chroma going
   forward.
3. **The heartbeat must not reuse `WatchdogThread`.** It writes `ap_type='run_tasks'`
   regardless of its argument, and the web app's stale-task sweep treats any such live row
   as proof that a runner is up. The chat service writes its own `chat_service` row.
4. **The browser needs a route to the service outside nginx.** Locally the app is served
   from port 8000 and the chat service will listen on 8001. The web app reports the chat
   port in `GET /users/me` (from a new `CHAT_SERVICE_PORT` in its `.env`, blank on EC2
   where nginx routes the path). The chat service enables CORS with the existing
   `CORS_ORIGINS`.
5. **The filter form can be reused more directly than the design assumed.** It reads two
   module-level stores (`useDefaultGVDBsRetrFiltersStore`, `useModalGVDBsRetrFiltersStore`).
   The chat and `Queries` pages are never mounted together, so chat can drive the same
   stores if it initialises them on entry and resets them on exit. Only the wrapper is new.

---

## 2. Naming and layout

| Item | Choice |
|---|---|
| Branch | `feature/conversation-mode` |
| Nav label and route | `Chat`, `/app/chat`, in the `Query Documents` menu |
| Service entry point | `backend/chat_service.py` (`uvicorn chat_service:app --port 8001`) |
| Service package | `backend/chat_lib/` |
| API prefix | `/api/v1/chat/` |
| Tables | `chat_conversations`, `chat_messages` |
| New columns | `api_groups.chat_enabled`, `api_groups.chat_rewrite_gllms_id`, `group_vdbs.gvdbs_chat_cfg` |
| New setting | `chat_history_turns` (default 6) |
| Frontend page | `frontend/src/pages/Chat/` |

**`chat_lib/` modules:** `app.py` (FastAPI app, CORS, startup), `auth.py` (login check and
group switch), `routers.py`, `schemas.py`, `tables.py` (database access), `retrieval.py`
(embedding cache, Qdrant search), `rewrite.py`, `prompt.py` (message assembly),
`llm_providers.py` (async streaming per LLM type), `turn.py` (one turn, SSE), `heartbeat.py`.

**Imported from existing code, unchanged:** `common/` (config, models, sessions, filter
schema), `cwa_lib/users.py` (token check), `tasks_lib/vdb_lib/qdrant_ops.py` and
`qdrant_filters.py`, `tasks_lib/llm_lib/tiktoken_count.py`.

---

## 3. Contracts fixed before coding

**`gvdbs_chat_cfg`** (JSON on the collection; all keys optional):

```json
{ "search_type": "similarity", "search_kwargs": { "k": 8 }, "system_prompt": "..." }
```

Empty means: the collection's own default search type with k capped at 8, and a built-in
generic system prompt. Chat therefore works on any collection with no configuration.

**`chat_conversations.filters_json`:** the same shape as the `filters` member of
`doc_tasks.gvdbs_cfg_json`, validated by the existing
`GVDBsRetrFiltersFunctions.check_user_request`.

**Send a message:** `POST /api/v1/chat/conversations/{id}/messages`
with `{ "content": "...", "gllms_id": 12 }`. Response is `text/event-stream`:

| Event | Data |
|---|---|
| `status` | `{ "text": "Searching…" }` |
| `token` | `{ "t": "…" }` |
| `done` | `{ "msg_id": 0, "tokens_in": 0, "tokens_out": 0, "seconds": 0.0 }` |
| `error` | `{ "text": "…" }` |

**Rules:**
- A turn is one user message plus its answer. History sent to the LLM is the last
  `chat_history_turns` turns whose answer is complete or stopped; failed turns are skipped.
- One answer in flight per conversation; a second send meanwhile is refused (HTTP 409).
- Stop is the browser closing the stream. The service cancels the LLM call and saves the
  partial answer with status `stopped`.
- Message status values: `complete`, `stopped`, `error`.
- Title: first 35 characters of the first message, as `Queries` does for short names.
- The service runs as a single process (one uvicorn worker), which the in-flight rule and
  the embedding cache rely on.

---

## 4. Slices

Each slice ends with a check that can be run and shown. Slices 1–3 need no UI.

### Slice 1 — Database and settings

- Models: `common/sql_models/chat_conversations.py`, `chat_messages.py`; new columns on
  `ApiGroups` and `GroupVDBs`; register in `common/sql_models/__init__.py`.
- One Alembic revision on top of head `7c3d9e2a1b54`: two tables, three columns, index on
  `chat_conversations (user_id, updated_at)` and `chat_messages (conv_id, seqn)`.
- `chat_history_turns` added to `ApiSettingsNamesEnum`, its validator, the startup
  defaults and `backend/.init_sql_data/api_settings.json`.
- `common/features/chat_cfg.py`: the `gvdbs_chat_cfg` schema and its defaults.
- **Check:** upgrade and downgrade both run cleanly on the local database; existing
  `Queries` still work with `run_tasks` and the web app restarted.

### Slice 2 — Service skeleton

- `chat_service.py`, `chat_lib/app.py`, `auth.py`, `heartbeat.py`, `schemas.py`,
  `tables.py`, and the non-streaming routes: `GET /options`, conversation list, create,
  read, rename, delete.
- Every route requires a valid token and `chat_enabled` for the caller's group, and
  filters on the caller's `user_id` and `group_id`.
- `GET /options` returns the group's enabled Qdrant collections (with filter schema) and
  enabled LLMs.
- `backend/tools/chat_smoke.py`: a command-line script that logs in and exercises the API.
- **Check:** the smoke script creates, lists, renames and deletes a conversation; a user
  in a group without the switch gets 403; a second user cannot read the first user's
  conversation; the service appears on Server Status.

### Slice 3 — One turn, end to end

- `retrieval.py`: embedding models loaded on first use and cached, optional preload list
  `CHAT_EMB_MODELS_PRELOAD`; search through `QdrantOps.get_docs` in a worker thread, with
  the conversation's filters.
- `rewrite.py`: standalone-question call, using the group's rewrite LLM when set and
  healthy, otherwise the turn's LLM. Skipped on the first turn.
- `llm_providers.py`: async streaming for the OpenAI-compatible types (OpenAI, Ollama,
  Qwen, Mistral), Claude and Gemini, with the same per-provider parameters `run_tasks`
  uses (for example no `temperature` for Claude), plus the `dummy` type for free testing.
- `prompt.py`, `turn.py`: message assembly, SSE stream, single write on completion,
  stop handling, error handling, token counts.
- **Check:** from the smoke script against group 2: a first question streams an answer; a
  follow-up with a pronoun retrieves on the rewritten question (shown in
  `retrieval_query`); interrupting the stream leaves a `stopped` message; two
  conversations stream at the same time; a bad API key yields an `error` event and row.
  Run once per LLM type that group 2 has enabled.

### Slice 4 — Chat page

- `pages/Chat/`: page, sidebar and item, thread, message, composer, header with
  collection and LLM selectors; stores for options, the conversation list and the current
  conversation; `api/chatClient.ts` (base URL from `/users/me`, `fetch` stream reader).
- Web app: `chat_enabled` and the chat port added to `GET /users/me` and to
  `useLoggedUserStore`; nav entry and route shown only when enabled.
- **Check:** in the browser on M1, as a group 2 user: start a conversation, watch it
  stream, stop one mid-answer, reopen it from the sidebar after a reload, rename and
  delete. As a user of a group without the switch: no nav entry, and the route redirects.

### Slice 5 — Filters, Open in Queries, download

- Filter wrapper for the header, driving the existing filter form; values sent with
  conversation creation; header locks after the first message and shows the values
  read-only.
- "Open in Queries" on each answer: navigates to `Queries` with the turn's standalone
  question, collection and filter values; `QueryArea` gains a small prefill on arrival,
  modelled on the existing clone action.
- "Download this conversation": Markdown built in the browser.
- **Check:** a filtered conversation on the product collection returns only matching
  material, confirmed by opening a turn in `Queries` and inspecting the retrieved context
  there; the Casambi collection shows no filter control; the download opens as readable
  Markdown.

### Slice 6 — Superuser settings

- Manage Groups: `chat_enabled` (yes/no) and `chat_rewrite_gllms_id` (validated to be an
  LLM of that group; blank for none).
- Superuser Manage VDBs: `gvdbs_chat_cfg`, edited as JSON text with server-side validation.
- Manage Api Settings: `chat_history_turns`, validated as a positive integer.
- Not added to any group-admin page.
- **Check:** turning the switch off removes the nav entry at next login and the service
  refuses requests; changing chat k and the system prompt changes the next answer;
  setting a rewrite LLM is visible in the service log for the next follow-up.

### Slice 7 — Deployment and group 2 configuration

- `docker-compose.yml`: a `chat` service built from the `run_tasks` Dockerfile with the
  command overridden to uvicorn, the shared `hf_cache` volume, and the same `SECRET` as
  the web app. `nginx_default.conf`: `location /api/v1/chat/` to it, with a long read
  timeout. Deploy README updated.
- Local start instructions in `README.md`; `CHANGELOG.md` entry; frontend bundle rebuilt.
- Chat system prompts and chat k for the two group 2 collections, drafted for your review.
- Migration and switch applied on dev and demo following the existing deploy procedure.
- **Check:** a conversation on dev.cognosa.net and on demo.cognosa.net, streaming through
  nginx; `Queries` unaffected on both.

---

## 5. Order and dependencies

Slices run in the order given. Slice 6 could move ahead of slice 4 if you would rather
set the switch from the UI than by SQL during testing; until it exists, the switch and
chat settings for group 2 are set by a one-line SQL statement on the local database.

Slices 1–3 change no existing behaviour. Slice 4 is the first to alter the web app
(`/users/me`, nav). Slice 5 is the only one that touches the `Queries` page.

---

## 6. Not included

Skipping retrieval on turns that do not need it; regenerate, edit and copy; summarising
long histories; retrieval across collections; pgvector and Chroma collections in chat;
any group-admin or superuser view of conversations; automated tests beyond the smoke
script (the repository has no test suite today).

---

## 7. Decisions settled before starting (2026-11-20)

1. The Ledra-specific branch in the reused filter module is accepted (finding 1).
2. Chat is Qdrant-only (finding 2).
3. The label users see is `Chat`.
