# Cognosa web app — roadmap and backlog

Status (2026-09-15): **paused** at release 0.48.0. Active use is limited to demos
on dev.cognosa.net / demo.cognosa.net (EC2, stopped between uses). Development
resumes when NAAG (group 4) supplies additional source documents and sample
queries for their existing Qdrant collections, or when another customer drives
a requirement.

Conventions: shipped work goes in `CHANGELOG.md`; this file holds only what is
not yet done. Remove an item here when its changelog entry lands.

## Open items carried from prior sessions

1. **Take the GitHub repo private.** Deferred 2026-08-20; still public.
   Prerequisite: a read-only deploy key per EC2 host and re-pointing
   `~/cognosa-src`'s remote to SSH. Procedure and constraints in
   `docs/github_going_private.md`.

2. **Feature 201, phase 2 — scope undefined.** Phase 1 (0.48.0) exports a single
   query result as Markdown via the `Save Result` button. No phase 2 scope was
   ever written down. Candidates to decide on before starting: batch export of
   several history rows; additional formats (PDF, DOCX); including retrieved
   context chunks / citations in the export; a server-side export endpoint so
   Safari and Firefox get a proper Save As.

3. **Authenticated NAAG smoke test on EC2.** Log in at dev and demo and run a
   NAAG query against FUROCAD end-to-end. Never exercised in an automated
   session after the 2026-08-20 deploy revamp (no credentials available then).
   Harry has run demos since, so treat as informally covered; keep here until a
   scripted check exists.

## Backlog ideas (not committed to)

- Superuser **"clone LLM entry"** action on `Manage LLMs`, to create a new
  group LLM row from an existing one instead of retyping provider settings.
- **CPU-only torch** in the `run_tasks` Docker image to cut its size
  (6–10 GB today). Only matters if EC2 hosts stay CPU-only.
- **Frontend chunking.** Vite warns that `vendor` (842 kB) and `xlsx` (331 kB)
  chunks exceed 500 kB. Dynamic import of the xlsx path and a manual vendor
  split would help first-load time. Cosmetic until users notice.

## Housekeeping

- Two code TODOs: drop the `tasks` table special case in `backend/init_sql_db.py`;
  implement the "check queue filled" stub in `backend/tasks_lib/qd_lib/qd_init.py`.
- `docs/QWEN_LLM_Integration_Plan.md` and `docs/QWEN_EC2_Update_Steps.md` are
  superseded (Qwen shipped; deploy procedure now lives in
  `release/ec2_ubuntu_24_04/cognosa/!README.MD`). Archive or delete.
- `api_settings.app_version` / `db_version` in the live databases hold free-form
  dump-tracking notes rather than the release number. The seed
  (`backend/.init_sql_data/api_settings.json`) now says `0.48.0`; decide whether
  the live rows should be normalised to match, since the value is shown on the
  index page and the superuser Server Status page.
- Release procedure used for 0.48.0, for repetition: rebuild the frontend
  (`cd frontend && npm run build`) and confirm `backend/static` has no git
  drift; cut the `[Unreleased]` section in `CHANGELOG.md` into a dated version
  header; update the version line in `README.md` and the seed `app_version`;
  commit; create an annotated tag `v<version>`; push `main` and the tag to
  both `origin` (GitHub) and `gitlab`.
