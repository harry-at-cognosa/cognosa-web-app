# Follow-up question behavior — worked example, query #175

> **Users should be reminded that "follow up questions overwrite the first query (except for the response text) so clone and run a new query if you want to compare two results."**

Source: local `cwa_db`, `doc_tasks.doc_task_id = 175`, run 2026-10-11 16:26–16:27. Code: `backend/cwa_lib/sql_tables/doc_tasks.py:231-245`, `backend/tasks_lib/vdb_lib/found_documents.py`.

---

## Question 1 (Harry)

> I have a general question about our "follow up question" capability. This was added sort of as an afterthought, so no new `doc_task` row is created for the follow up and, inevitably, some of the data from the first query is lost. I think. Can you look at the local database for the locally running instance of Cognosa and tell me, for query #175, if there is a way to tell why the initial query found nothing and the follow up query gave an answer from the vector database content? Is it possible that the retrieval parameters changed? Mostly I want to know if there is any trace (other than the actual response, which is preserved) of the results of the original query.

## Answer 1

**Short answer.** Yes, the retrieval parameters changed, and two traces of the first query survive. Everything else about the first run was overwritten.

**What a follow-up does.** The follow-up path reuses the same `doc_tasks` row and overwrites `input_text`, `gvdbs_cfg_json`, `gvdbs_json`, `gllms_json`, `gc_id`, `sent_to_llm`, the timing and token columns, and `status`. The first answer survives only because the second answer is written to `output_text_2`.

**Task 175.**
- The question text is the same in both runs: `rt-p1.debug.log` shows the identical `input_text` at 16:26:22 and 16:27:38. The follow-up was not a rewording.
- The row's current `gvdbs_cfg_json` is MMR, k=40, fetch_k=70, lambda_mult=0.5 (the follow-up's setting). The VDB row `cpa-c42t_collection (qdrant-Sim20)` defaults to similarity, k=20.
- **Trace 1, `context_json`:** cumulative, each item tagged with `question_seqn`. Question 1 contributed 20 items (1–20); question 2 added 22 new items (21–42).
- **Trace 2, run-task logs:** `rt.debug.log` shows the first LLM call took about 3 s and the second about 9 s. The log does not record parameters.
- The first answer was "I don't know". Wachter appears in none of the 42 retrieved chunks (text search only). The stored data does not explain why the second answer was fuller.

**Lost for good.** The first run's retrieval parameters, `sent_to_llm` prompt, token counts and timings, and any filter / LLM / context selections that differed between the two runs.

**Not checked.** The current `sent_to_llm` contains only 20 "Document" blocks, not 42. It is unknown which 20, or whether the follow-up's new documents reached the LLM.

**Possible fixes.** Cheap: snapshot the first query's `input_text`, `gvdbs_cfg_json`, `sent_to_llm`, timings and tokens into new `_q1` columns before the overwrite. Larger: a separate `doc_task` row per question.

**For the future `doc_tasks` column change.** The overwrite happens in `backend/cwa_lib/sql_tables/doc_tasks.py:231-245`. That is where the follow-up sets the fields listed above on the existing row and increments `question_number`. Any snapshot columns (for example `_q1` copies) would be filled there, before those assignments. `question_number > 1` already raises "Task already has follow-up question", so there is only ever one follow-up per row. This is deferred: it is not an issue for now.

---

## Question 2 (Harry)

> How do we know this: *"Trace 1, context_json: context_json is cumulative and each item is tagged with question_seqn. Question 1 retrieved exactly 20 documents (items 1–20). That matches similarity at k=20. Question 2 added 22 new items (21–42). MMR returned 40, so about 18 of them duplicated documents from the first pass. The first query's retrieved set is therefore preserved, and so is the set the follow-up added. Trace 2, run-task logs: rt.debug.log shows the first LLM call took about 3 seconds and the second about 9 seconds. The log does not record the parameters."*

## Answer 2

Part of that is verified and part is inference, and the inference was stated too confidently.

**Verified from the data and code**
- A query over `context_json` for task 175, grouped by `question_seqn`, returned 20 items for question 1 (items 1–20) and 22 for question 2 (items 21–42).
- `found_documents.py`: `append()` sets `question_seqn` to the task's current `question_number`, and skips chunks whose text exactly matches one already in `context_json`, so only new chunks get the follow-up's tag.
- `rt.debug.log` timestamps: 16:26:22→16:26:25 (first LLM call), 16:27:38→16:27:47 (second).
- Current `gvdbs_cfg_json` is MMR k=40; by the code, that is the follow-up's config because the follow-up overwrites it.

**Inferred, not proven**
- **"Similarity at k=20":** question 1 returned 20 items and the VDB row's default is similarity k=20, but MMR with k=20 would also give 20, and nothing stored records what question 1 used. The "k" is a deduction; the "similarity" is only a guess.
- **"MMR returned 40, so about 18 duplicated":** how many chunks question 2 returned was never observed. 40 was assumed from the config. Only the 22 new ones are known; the 18 is arithmetic on that assumption. Duplicates are exact-text matches, so near-identical chunks would count as new.
- **"Preserved":** true for the chunks `context_json` kept; not true of the first run's ranking, scores or order, which `context_json` does not record per query.

**What can be supported.** Question 2 added 22 new chunks, more than the 20 that question 1 returned, so question 2 returned at least 22 chunks and a k=20 setting could not have produced that. This assumes question 1 did not drop blank chunks to land on 20. The exact first-run parameters are unrecoverable; treat them as unknown.

---

*Typo corrections in Harry's questions (silent per standing instruction): "quesiton" → "question", "sort of" spacing, "locally running instances" → "instance".*
