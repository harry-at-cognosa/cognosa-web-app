# Cognosa — TODO summary

One line per entry in `TODO.md`, which holds the detail. As of 2026-11-13. Items 1, 5, 6 and 10
are in `todo_archive.md`; numbers are kept stable.

| # | Short name | Description |
|---|---|---|
| 2 | Loader not idempotent | `document_loader_qdrant.py` assigns random point IDs, so re-running it duplicates every chunk. Fixed for the CPA collection only; open for the other five. |
| 3 | Parse failures swallowed | The loader logs per-file exceptions and continues, so a failed file is indistinguishable from one never offered. Wanted: a per-file loaded / skipped / failed report. |
| 4 | No payload indexes | Collections have no payload field indexes, so metadata filters run as full scans. Only `cpa-c42t_collection` has any (two keyword indexes). |
| 7 | Manage Doc Tasks filters | Add a single-value or min/max filter on the ID column, a User ID / Name dropdown cascading from the group dropdown, value filters on `status`, `gvdbs_id` and `gllms_id`, and a min/max range on `fetched_at`. |
| 8 | Manage Doc Tasks column selection and resizing | Columns after the first four become optionally visible, and column widths become drag-resizable. |
| 9 | Manage Doc Tasks rows-per-page maximum | Replace the hardcoded `max_limit` of 20 with a system-wide `api_settings` entry, `doc_task_max_rows_ret` (default 50), and offer `[5, 10, 20, 50]` in the Limit list. |
