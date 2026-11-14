# Cognosa — TODO archive

Entries moved out of `TODO.md` once done or withdrawn. They keep their original numbers.

---

## 1. Retrieval parameter selection resets to default after every query

**Raised by:** Harry, 2026-09-02. **Archived 2026-11-13:** no longer describes the app's
behaviour. Superseded by item 10; the persistence of query parameters is now as wanted.

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

## 5. `group_vdbs.json` seed has drifted from production

**Observed:** 2026-09-01.

`backend/.init_sql_data/group_vdbs.json` holds **4 rows**. The live `group_vdbs` table on
both demo and the M1 holds **9**, including `furocad`, `furocad_footnotes` and
`casambi_collection` entries absent from the seed.

A new instance built from the seed will not reproduce the current configuration. Either the
seed is a deliberate minimal fixture — in which case say so in the file — or it should be
regenerated from a known-good environment.

**Done 2026-11-13.** The seed now holds the six live rows for groups 1 and 2 (the only
groups `api_groups.json` seeds; `group_vdbs` has a foreign key to it), taken from the local
`cwa_db`: CPA, pgvector and chroma `collection_1` (both disabled), Ledra, and the two
Casambi entries. Each row also carries `enabled`, `gvdbs_retr_params` and
`gvdbs_retr_filters`, which `backend/init_sql_db.py` now reads when present. The WAB
(group 3) and Papetti SBS (group 4) rows are left out; adding them means adding those
groups to `api_groups.json` first.

---

## 10. New Query: keep collection, retrieval parameters, context and LLM

**Raised by:** Harry, 2026-11-13, following the retrieval-filter carry-over fix.
**Done 2026-11-13** (commits `cc688ee` source, `fbd6bc0` rebuilt bundle).

Before: "New Query" (`setNewQuery` in
`frontend/src/pages/QueryDocuments/stores/useDocTasksCurrent.ts`, called from
`QueriesListBar.tsx`) reset everything to defaults: Document Collection, Retrieval
Parameters, Context and LLM, along with the query text. It did not clear the retrieval
filters, which carried over silently into the next query.

**Wanted:** New Query clears the **retrieval filters** (and the query text, short name and
response) but keeps the **Document Collection, Retrieval Parameters, Context and LLM** as
the user last had them. Assume the user will reuse those settings; they change only when
the user resets or changes them by hand.

**As built:** as wanted. Changing the Document Collection by hand still loads that
collection's default retrieval parameters, and opening a query from the history list still
shows that query's own settings; New Query then keeps whatever is showing. Active retrieval
filters are now flagged on the Retrieval Filters button (amber, with a count).
