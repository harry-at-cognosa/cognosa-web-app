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

*Items 2–5 were observed by Claude during the p666 CPA collection rebuild and are recorded
here for triage; delete any that are not worth tracking.*
