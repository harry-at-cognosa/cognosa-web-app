# Conversation mode for Cognosa — design

Drafted 2026-11-20 against `main` at `64969a8`; revised the same day through several
rounds of review.
Target tenant: group 2 (product collection and Casambi collection). Nothing here has been
built; effort figures are estimates, not measurements.

---

## 1. Decisions taken

| # | Decision |
|---|---|
| 1 | Audience is logged-in Cognosa users only. No customer-site widget. |
| 2 | Chat is a separate page from `Queries`. |
| 3 | A conversation is bound to one collection, and to one set of filter values where the collection defines filters. Both are chosen at the start and then locked; a different collection or different filters means a new conversation. Collections are independent: there is no retrieval across collections. The LLM may be changed between turns. |
| 4 | Conversations are **not** stored as `doc_tasks` rows. `doc_tasks` stays the record for debugging and tuning retrieval. |
| 5 | Chat has its own runner: a separate streaming service, not `run_tasks`. |
| 6 | Storage is lean: what a typical chat product keeps, and no more. |
| 7 | Transcripts persist until the user deletes them. |
| 8 | Nothing about retrieval results is stored: no source list, no chunk IDs, no chunk text. The question and answer text are the record, and the download is that transcript. |
| 9 | No group-admin view of other users' conversations. |
| 10 | The design is collection-agnostic. Nothing in code or schema names a field of any particular collection; group 2 is only the first tenant to use it. |
| 11 | The rewrite call uses the conversation's own LLM, unless the group has a rewrite LLM set, in which case that one is used. |
| 12 | Access to conversations is a group-level attribute, default off. Only a superuser can see or edit it; group admins cannot see it. A group without it does not see the page. |
| 13 | Reconstructing which chunks produced an answer is not a requirement. Where an answer should name its sources, the LLM does so in the answer text. |
| 14 | The number of earlier turns resent to the LLM is a platform setting, `chat_history_turns`, default 6. It is a window only; there is no cap on conversation length. |
| 15 | Each answer offers "Open in Queries", for following up on an answer with a full query. |

The working philosophy: chat is for finding out; `Queries` is for documenting and
verifying. A user who needs detail after a conversation runs a query based on what they
learned.

---

## 2. Summary

- A new **chat service** (its own process) embeds the question, retrieves from Qdrant,
  and streams the LLM answer to the browser over SSE. It writes each message to the
  database once, when complete.
- Two new lean tables, `chat_conversations` and `chat_messages`, holding the text of each
  question and answer. No retrieved chunks, sources or prompts are stored.
- A new `Chat` page. `doc_tasks` and `run_tasks.py` are not modified; the `Queries` page
  gains only an entry point that pre-fills a new query from a chat turn.
- Size: roughly 1,600–2,150 new lines, almost nothing modified, one migration, one new
  process (one new Docker service on EC2 and one nginx route).

---

## 3. Why the existing pipeline is not reused

- **Volume.** A `doc_tasks` row stores the retrieved chunks twice, in `context_json` and
  again inside `sent_to_llm`. At k=30 that is an estimated 60–80 KB per turn against
  2–4 KB of question and answer text.
- **Purpose.** Chat turns would fill the Manage Doc Tasks pages, which exist for retrieval
  tuning.
- **Streaming.** `run_tasks` streams by rewriting the answer column on every chunk while
  the browser polls once per second. That is the opposite of the lean approach.
- **Concurrency.** `qd_vdb_fetched.py:24` calls `LLMWorker(...).run()`, not `.start()`, so
  one LLM answer streams at a time per runner and nothing else is dispatched meanwhile.
  Tolerable for a workbench; not for several people chatting.
- **The follow-up feature is not a model to extend.** The LLM never sees the first
  question or answer, and only one follow-up is allowed
  (`docs/follow_up_question_behavior_ex175.md`).
- **The web app cannot host it.** `req_webapp.txt` carries no torch, sentence-transformers
  or LangChain; adding them would turn a light image into a multi-gigabyte one.

---

## 4. The chat service

A second FastAPI application (working name `chat_service.py`, own port) that shares the
`common/` package, the database and the JWT secret with the web app.

**One turn, end to end:**

1. Browser sends `POST /api/v1/chat/conversations/{id}/messages` with the message text
   and the LLM. The collection and any filter values come from the conversation. The
   service authenticates the same bearer token the web app issues.
2. The user message is written to `chat_messages`.
3. If the conversation has earlier turns, a short non-streaming LLM call rewrites the
   message into a standalone question, using the turns in the history window.
4. The service embeds the standalone question with its own copy of the embedding model and
   queries Qdrant, using the collection's chat retrieval settings and the conversation's
   filter values.
5. It assembles a message list: system prompt containing this turn's chunks with their
   metadata, the text of the last `chat_history_turns` turns, and the new message. The
   chunks are used for this call and then discarded.
6. It streams the answer to the browser as SSE events: status, tokens, then a final event
   carrying the token counts.
7. On completion it writes the assistant message once. If the user presses Stop, the
   browser closes the stream, the LLM call is cancelled, and the partial answer is saved
   and marked as stopped.

**Properties:**

- **Concurrent by design.** LLM streaming is network-bound, so an async service handles
  many conversations at once. Embedding a short question takes milliseconds and runs in a
  thread.
- **Independent of `run_tasks`.** Every seeded collection uses `all-MiniLM-L6-v2`, which is
  small; the service loads its own copy from the shared `hf_cache` volume. It can be
  restarted without touching queries.
- **Shares configuration, not execution.** It reads `group_vdbs` and `group_llms` (URLs,
  models, keys, enabled flags, health status) as the web app does.
- **Provider code.** The three provider classes in `tasks_lib/llm_lib/` build a
  single-string prompt and are synchronous. The chat service needs its own small provider
  layer that takes a message list and streams asynchronously. It should not import the
  runner's classes; keeping them separate honours decision 5.
- **Filters.** Validation of filter values (`common/features/gvdbs_retr_filters.py`) and
  their conversion to a Qdrant filter (`tasks_lib/vdb_lib/qdrant_filters.py`) are generic,
  self-contained modules. The service uses them as they are.
- **Embedding models.** Loaded on first use and kept cached, with an optional preload list
  in the environment mirroring `RT_VDB_EMB_MODELS_PRELOAD`.
- **Health.** It reports a heartbeat to `api_processes`, so it appears on Server Status.

**Deployment:**

- Local: one more terminal (`uvicorn chat_service:app --port 8001`).
- EC2: one new service in `docker-compose.yml`, built from the `run_tasks` image (it has
  the needed libraries), and one nginx `location /api/v1/chat/` routed to it. The existing
  nginx block already sets `proxy_buffering off`; SSE additionally needs a longer
  `proxy_read_timeout`.
- Browser transport: `fetch` with a streamed response body, because `EventSource` cannot
  send the `Authorization` header that the app's token scheme uses.

---

## 5. Data model

One Alembic migration. Existing tables change by three columns only: one on `group_vdbs`
and two on `api_groups`.

**`chat_conversations`**

| Column | Note |
|---|---|
| `conv_id`, `group_id`, `user_id` | owner; every read filters on both |
| `title` | first words of the first message; user-renamable |
| `gvdbs_id` | the conversation's collection; fixed |
| `filters_json` | filter values chosen at the start, if the collection defines filters; fixed |
| `gllms_id` | last used LLM, the default for the next turn |
| `created_at`, `updated_at` | sidebar ordering |

**`chat_messages`**

| Column | Note |
|---|---|
| `msg_id`, `conv_id`, `seqn` | ordering within the conversation |
| `role` | `user` or `assistant` |
| `content` | the message text |
| `gllms_id` | the LLM this turn used |
| `retrieval_query` | the standalone question actually searched |
| `tokens_in`, `tokens_out`, `seconds` | cost and latency accounting |
| `status` | complete, stopped, or error |
| `created_at` | |

**Not stored:** retrieved chunks in any form (text, IDs, metadata, scores), the assembled
prompt, and intermediate streaming states.

**Sources in answers.** Because each chunk's metadata is in the prompt, the chat system
prompt can instruct the LLM to name the sources it relied on. Any citation is then part of
the answer text and is stored, shown and downloaded with it. Such citations are the LLM's
own account and can be incomplete or wrong; the `Queries` page remains the place to see
exactly what a search retrieves.

**Filters.** Where a collection defines retrieval filters (`group_vdbs.gvdbs_retr_filters`)
the values chosen at the start are saved once on the conversation, in the same generic
shape `doc_tasks.gvdbs_cfg_json` already uses. A collection without filters leaves it
null. The code never names a particular filter field.

**Deletion** is a hard delete of the conversation and its messages, consistent with
"persist until deleted". There is no trace table and no retention job.

**Chat settings.** `group_vdbs` gains `gvdbs_chat_cfg` (JSON): the chat k and search type
for that collection, and the chat system prompt. Chat rarely needs the 30 chunks the
workbench defaults to; 8–10 keeps prompts small and answers fast. Keeping the system
prompt per collection avoids overloading `group_contexts`, whose templates require
`{context}` and `{question}` and belong to the query model.

**History window.** A new `api_settings` row, `chat_history_turns`, default 6, added to
`ApiSettingsNamesEnum` and edited on Manage Api Settings. A turn is one question with its
answer. Turns older than the window stay visible on the page but are no longer sent to the
LLM. Six is a judgement, not a measurement: what a follow-up refers to is nearly always
within the last two or three turns, and six turns add an estimated 3,000–6,000 tokens per
call.

**Chat switch.** `api_groups` gains `chat_enabled` (boolean, default false).

- *Who can see and edit it:* superusers only, on the Manage Groups page. It needs no
  special mechanism. Group admins have no page over group attributes; their one route into
  `api_groups` (`routers/ga_settings.py`) reads and writes the single field
  `gvdbs_retr_params` by name, and the group row is never returned whole. A new column
  exposed only in the superuser Manage Groups schemas is therefore invisible to group
  admins by construction. The same holds for the rewrite LLM below.
- *What users see:* only the effect. `GET /users/me` gains a boolean saying whether the
  caller's group has chat, and the nav entry is shown or hidden accordingly. In a group
  without chat nothing indicates that the feature exists.
- *Enforcement:* the chat service checks the flag on every request and refuses a group
  without it, so hiding the nav entry is not the only barrier.
- *One knock-on:* the collection's chat settings (`gvdbs_chat_cfg`) are edited on the
  superuser Manage VDBs page only. They are not added to the group-admin Manage VDBs page,
  so a group admin sees no trace of chat there either.

**Rewrite LLM.** `api_groups` also gains `chat_rewrite_gllms_id`, nullable, pointing at one of
that group's own `group_llms` rows. Resolution per turn: the group's rewrite LLM if it is
set, enabled and not reporting an error; otherwise the conversation's LLM. The setting is
per group, not platform-wide, because LLM rows and their API keys belong to groups: a
platform-level setting would have no key to call with. It is edited on the superuser
Manage Groups page.

**Expected volume.** A turn is roughly 2–4 KB (two message rows), against an estimated
60–80 KB for a `doc_tasks` row covering the same exchange.

---

## 6. API (all under `/api/v1/chat/`, served by the chat service)

| Method | Path | Purpose |
|---|---|---|
| GET | `/options` | collections and LLMs enabled for the user's group |
| GET | `/conversations` | sidebar list |
| POST | `/conversations` | create, with the collection and any filter values |
| GET | `/conversations/{id}` | the conversation's messages |
| PATCH | `/conversations/{id}` | rename (collection and filters cannot be changed) |
| DELETE | `/conversations/{id}` | delete |
| POST | `/conversations/{id}/messages` | send a message; SSE response |

Every route filters on the caller's `user_id` and `group_id`. There are no group-admin or
superuser routes.

---

## 7. The `Chat` page

A new nav entry beside `Queries`, at `/app/chat`.

- **Sidebar:** conversations grouped by date, rename and delete, `New chat`. Same
  resizable splitter as the `Queries` page.
- **Thread:** user and assistant messages, answers rendered with the existing
  `MarkdownRenderer`, tokens appearing as they stream.
- **Composer:** pinned to the bottom; Enter sends, Shift+Enter breaks a line; the send
  button becomes Stop while an answer streams.
- **Header:** for a new chat, the collection selector and, where the collection defines
  filters, its filter control. Both lock when the first message is sent and are then shown
  read-only. The LLM selector stays live. No retrieval parameters, context template or
  short name.
- **Open in Queries:** on each answer. Opens the `Queries` page with a new query
  pre-filled from that turn: the standalone question that was searched, the conversation's
  collection and its filter values. The user adjusts and asks as usual; from there the
  full retrieval record exists in `doc_tasks`.
- **Download this conversation:** builds a Markdown file in the browser from the loaded
  messages (the collection and filter values, then each question and answer with its LLM
  and timestamp), in the manner of `Save Result`. Nothing is written on the server.

Reused as is: `MarkdownRenderer`, the theme classes, the splitter, the token in
`localStorage`. Adapted: the schema-driven filter component, which is currently wired to
the `Queries` stores and needs a store of its own for chat. Not reused: the `Queries`
task stores, which are built around a single task.

Regeneration, message editing and copy buttons are common in chat products and are left
out of the first version.

---

## 8. Generality, and group 2 as first tenant

The service, tables and page behave identically for every collection. What varies is
configuration held on the collection's `group_vdbs` row: its chat retrieval settings, its
system prompt, and whatever filter schema it already has.

**Filters in chat.** The existing filter mechanism is already schema-driven, so chat
offers a collection's filters, when it has any, without knowing what they are. The user
sets them before the first message; they then hold for the whole conversation. Proposing
filter values automatically from the message text is a possible later refinement.

**Group 2.** Two collections, both on `all-MiniLM-L6-v2`:

| Collection | Qdrant name | Workbench default | Filters defined |
|---|---|---|---|
| Architectural Lighting Solutions | `ledra_brands_products_xlsx` | similarity, k=30 | yes, 10 fields |
| Casambi | `casambi_collection` | MMR 25/45/0.5 | none |

- Each conversation uses one of them. Finding in Casambi which parts are light sensors,
  then looking for such products in the product collection, is two conversations (or a
  conversation and a query).
- The only work specific to group 2 is configuration: a chat system prompt and chat
  retrieval settings for each collection. Its one existing template was written for single
  questions.

---

## 9. Size estimate

| Area | New | Modified |
|---|---|---|
| Database | 2 tables, 3 columns, 1 migration | — |
| Chat service | ~650–850 lines: app, auth wiring, routes, rewrite, retrieval, provider layer, SSE, heartbeat | — |
| Frontend | ~950–1,300 lines: page, sidebar, thread, composer, stream client, stores, filter control, download | `Router.tsx`, `TopNavBar.tsx`, prefill entry point on the `Queries` page |
| Deployment | 1 compose service, 1 nginx location | `docker-compose.yml`, `nginx_default.conf`, README |
| Admin UI | chat settings field on the superuser Manage VDBs page; chat switch and rewrite LLM on Manage Groups; `chat_history_turns` in settings | 2 pages, settings enum |

Order of magnitude: five to eight focused working days including testing on M1, dev and
demo. This is more than reusing `doc_tasks` would have cost, because the provider layer
and the streaming transport are new, but it leaves the query pipeline untouched. The filter control is the least certain item.

---

## 10. Suggested phasing

| Phase | Content |
|---|---|
| 1 | Chat service, tables, `Chat` page, history window, rewrite step, filter control, download, "Open in Queries", per-group switch, group 2 system prompts |
| 2 | Regenerate and copy; summarization of long histories |
| Potential optimization | Skipping retrieval on turns that do not need it (see below) |
| Later, if wanted | Filter values proposed from the message text |

Retrieval across more than one collection is out of scope and not planned.

**Potential optimization: skipping retrieval.** Some messages ask for nothing new from
the collection: "put that in a table", "shorter please", "translate that to German",
"thanks". In phase 1 every turn runs a search regardless, so such a message retrieves
chunks that match nothing useful, which costs a little time and adds irrelevant text to
the prompt. The optimization: the rewrite step also judges whether the message needs
retrieval, and when it does not, the service skips the search and sends the LLM the
conversation history alone.

The limitation follows from storing nothing about retrieval. On a skipped turn the LLM has
its earlier answer but not the chunks behind it. That suffices for reformatting or
shortening. A message such as "tell me more about the second one" must still be treated as
needing retrieval, because the detail is not in the earlier answer. Misjudging that
boundary gives a thin or invented answer, which is why this is not in phase 1 and should be
adopted only if the wasted searches prove noticeable.

---

## 11. Known constraints

- **Embedding models are held twice.** A question must be embedded with the model the
  collection was built with, and the chat service loads its own copy alongside the ones in
  the `run_tasks` VDB workers. Model size (parameters) drives that memory; vector length
  drives storage in Qdrant and is a separate matter.

  | Groups | Embedding model | Parameters | Vector length | Model file |
  |---|---|---|---|---|
  | 1, 2, 3 | `all-MiniLM-L6-v2` | ~23 M | 384 | ~90 MB |
  | 4 | `BAAI/bge-base-en-v1.5` | ~109 M | 768 | ~440 MB |

  (Groups from the local database holding the demo data, 2026-11-20; model figures as
  published.) Both together are modest. A group adopting a model of the "large" class,
  1–2 GB or more, would raise the service's footprint and per-question delay on CPU. The
  remedy then would be one shared embedding process for both runners.
- **Citations are the LLM's own.** With nothing about retrieval stored, a source named in
  an answer cannot be checked against what was retrieved, except by "Open in Queries".
- **Locked scope.** A user who wants to narrow or widen the filters mid-conversation must
  start a new chat and loses the earlier turns as context.

## 12. Open points

None at present.
