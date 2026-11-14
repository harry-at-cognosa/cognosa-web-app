# Cognosa — TODO / feature and defect list

Working list of things worth fixing or building in the Cognosa web app. Newest context at
the top of each entry. Items are not in priority order.

Started 2026-09-02 during the CPA collection rebuild (p666_cpa_load).

---

## 1. Retrieval parameter selection resets to default after every query

**Raised by:** Harry, 2026-09-02.

After a query completes, the UI reverts the retrieval configuration to the default. Running
a second query with the same non-default settings means re-selecting them every time.

This is worse than re-entering a single number. Different **retrieval types** take different
*parameter fields*, not merely different values — so restoring a configuration means
re-choosing the type and then re-populating a different set of inputs.

**Current workaround:** multiple `group_vdbs` rows pointing at the same collection, each
carrying its own default retrieval parameters. Selecting the entry swaps the whole
configuration in one step. Group 2 does this for `casambi_collection`, and Ledra likewise.
It works, but it is a workaround for the reset — not the reason the feature should exist.

**Wanted:** retrieval settings persist across queries within a session, or an explicit
"keep settings" control. The A/B comparison the workaround enables should not require
duplicate database rows to be usable.

---

## 2. `document_loader_qdrant.py` is not idempotent

**Observed:** 2026-09-01, verified against live data.

`QdrantOps.save_to_qdrant` (`backend/tasks_lib/vdb_lib/qdrant_ops.py:107`) calls:

```python
vector_store.add_documents(documents)
```

with no `ids=`, so `langchain_qdrant` assigns a **random UUID4 to every chunk**. Running the
loader twice over the same folder stores every chunk twice under different IDs.
`create_collection()` returns early when the collection exists, so a second run appends
silently rather than warning.

**Fixed for the CPA collection only** by `backend/cpa/cpa_document_loader_qdrant.py`, which
derives point IDs as `uuid5` over an NFKC-normalised SHA-256 of the chunk text. Verified: a
full re-run leaves the collection at 29,748 points.

**Also fixed 2026-10-11** for incremental batches: the CPA loader checks for existing IDs
and skips them, so re-loading never re-embeds or overwrites (`PLAN-batch-refresh_261011.md`
in `p666_cpa_load`).

**Still open** for every other collection — `ledra_brands_products_xlsx`,
`wab_group_products`, `casambi_collection`, `furocad`, `furocad_footnotes` — all of which
still load through the original path. The fix is small: thread an `ids` argument through
`save_to_qdrant`.

---

## 3. Parse failures are logged and swallowed

**Observed:** 2026-09-01.

`document_loader_qdrant.py` catches per-file exceptions, writes a log line, and continues.
With no manifest, a file that fails to parse is indistinguishable from one that was never
offered.

This is how `essay scoring-1988-Wayne_Patience_Joan_Auchter-GED_testing-services.pdf`
ended up absent from `collection_1` without anyone noticing. (That file turned out to be an
illegible photocopy and is now excluded deliberately — but nothing surfaced the loss at the
time.)

**Wanted:** the loader emits a per-file report — loaded / skipped / failed, with counts and
reasons. `cpa_document_loader_qdrant.py` does this and can be copied.

---

## 4. No payload field indexes on any collection

**Observed:** 2026-09-01, all six collections plus the new one.

Every collection reports an empty `payload_schema`, so all metadata filtering runs as a full
payload scan. Invisible at current sizes; it becomes the bottleneck as a collection grows,
or on any move to a single collection with a tenant-id filter.

Relevant now that `cpa-c42t_collection` carries `flag_a`…`flag_f`, `flags_set` and
`row_number` metadata specifically intended for future filtered retrieval.

**Update 2026-10-11:** `cpa-c42t_collection` now has two keyword indexes,
`metadata.cpa_batch` and `metadata.cpa_source_file`, created by
`backend/cpa/cpa_payload_indexes.py` on M1, dev and demo. Everything else above still
holds.

---

## 5. `group_vdbs.json` seed has drifted from production

**Observed:** 2026-09-01.

`backend/.init_sql_data/group_vdbs.json` holds **4 rows**. The live `group_vdbs` table on
both demo and the M1 holds **9**, including `furocad`, `furocad_footnotes` and
`casambi_collection` entries absent from the seed.

A new instance built from the seed will not reproduce the current configuration. Either the
seed is a deliberate minimal fixture — in which case say so in the file — or it should be
regenerated from a known-good environment.

---

## 6. Manage Contexts: make the Name and Text column widths adjustable

**Raised by:** Harry, 2026-11-11, while capturing screens for the SBS demo video (p67_sbs_demo).

On Manage Contexts (`/app/manage_contexts`, `frontend/src/pages/ManageContexts/`) the Name
column takes most of the table width and the Text column is narrow, so each context's text
shows only its first five or six wrapped lines. Reading a whole context means dragging the
text box's resize handle taller, row by row, or opening Edit.

**Wanted:** adjustable widths for the Name and Text columns (drag to resize), so the Text
column can be given the room. A wider default for Text would help on its own: the names are
short and the text is the content.

---

## 7. Manage Doc Tasks: filter rows on column values

**Raised by:** Harry, 2026-11-12. Future feature.

On Manage Doc Tasks (`/app/manage_doc_tasks`; `backend/cwa_lib/pages/su_manage_doc_tasks.py`
and `ga_manage_doc_tasks.py`, `frontend/src/pages/SuManageDocTasks/`, `GaManageDocTasks/`)
the only row filter today is the **Group ID: Name** dropdown.

**Wanted:**

- **ID (`doc_task_id`)** — a single value, or a minimum and/or maximum (a range).
- **User ID / Name** — a dropdown like the group one, cascading from it: list only the users
  that survive the group selection to its left, and further limit the rows.
- **`status`**, **`gvdbs_id`**, **`gllms_id`** — filter on value.
- **`fetched_at`** — user-set minimum and maximum datetime (a range; the control is open).

Filters combine (AND) with each other and with the group selection.

---

## 8. Manage Doc Tasks: column selection and column resizing

**Raised by:** Harry, 2026-11-12. Future feature. Two requirements, on Manage Doc Tasks
(`/app/manage_doc_tasks`; same files as item 7).

1. **Column selection.** The first four columns — doc task id, Group ID: Name,
   User ID / Name, status — are always shown. Every column after those is selectable: the
   user chooses whether it is included in the visible set of columns on the page. Harry has
   a UX in mind for the selector; ask him for it before designing one.
2. **Column resizing.** Adjustable column widths (drag to resize), as item 6 asks for
   Manage Contexts.

---

## 9. Manage Doc Tasks: raise the rows-per-page maximum, and make it a setting

**Raised by:** Harry, 2026-11-12.

Both Manage Doc Tasks pages inherit `max_limit = 20` and `select_limit = [5, 10, 20]`, the
class defaults at `backend/cwa_lib/pydantic_schemas/generic_table.py:36`. The server clamps
the requested limit to `max_limit` (`backend/cwa_lib/pages/__init__.py:86`). Since the Excel
and JSON exports write only the current page, no single export can exceed 20 rows.

**Wanted:**

- The maximum comes from a setting, `doc_task_max_rows_ret`, default **50**, in place of
  the hardcoded value. It lives in the existing `api_settings` table (Manage API Settings
  page) and is system-wide, not per group.
- `select_limit = [5, 10, 20, 50]` on both pages.

The Limit box is a number input with the `select_limit` values as suggestions, so a value
off the list can already be typed: with the setting at 75, a user could enter 40.

---

## 10. New Query: keep collection, retrieval parameters, context and LLM

**Raised by:** Harry, 2026-11-13, following the retrieval-filter carry-over fix (branch
`worktree-clear-filters-on-new-query`).

Today "New Query" (`setNewQuery` in
`frontend/src/pages/QueryDocuments/stores/useDocTasksCurrent.ts`, called from
`QueriesListBar.tsx`) resets everything to defaults: Document Collection, Retrieval
Parameters, Context and LLM, along with the query text.

**Wanted:** New Query clears the **retrieval filters** (and the query text, short name and
response) but keeps the **Document Collection, Retrieval Parameters, Context and LLM** as
the user last had them. Assume the user will reuse those settings; they change only when
the user resets or changes them by hand.

Related to item 1, which asks for retrieval settings to persist across queries.

**Done 2026-11-13** on the same branch. Changing the Document Collection by hand still
loads that collection's default retrieval parameters, and opening a query from the history
list still shows that query's own settings; New Query then keeps whatever is showing.

---

*Items 2–5 were observed by Claude during the p666 CPA collection rebuild and are recorded
here for triage; delete any that are not worth tracking.*
