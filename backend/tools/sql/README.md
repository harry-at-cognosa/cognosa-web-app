# backend/tools/sql — one-off data migrations

Data-only changes to `cwa_db` that are not schema changes (schema changes go
through Alembic). Each script is idempotent and safe to re-run; apply it to
every environment (local demo DB, each EC2 instance) that should pick up the
change.

| Script | Purpose |
|---|---|
| `update_llm_models_260819.sql` | Move `group_llms` rows from 4.5-gen vendor models to current ones (Claude 5, Gemini 3.7, GPT 5.6, Qwen 3.8). Needs backend ≥ 71d8dea. |

## Applying

With `psql`, using the URL from `backend/.env` (note the app's `database://`
scheme must be rewritten to `postgresql://`):

```bash
psql "postgresql://user:pass@localhost:5432/cwa_db" -f backend/tools/sql/update_llm_models_260819.sql
```

Or from the project venv, with no psql dependency:

```bash
cd backend
../venv/bin/python tools/sql/apply_sql.py tools/sql/update_llm_models_260819.sql
```

Restart `run_tasks.py` afterwards so the LLM workers re-check model status.
