# Plan: Add Qwen (DashScope) as a New LLM Provider

## Context

The cognosa_web_app platform already supports 5 LLM provider types: `dummy`, `ollama_local`, `ollama_remote`, `chatgpt`, `gemini`, and `claude`. Qwen models (via Alibaba's DashScope service) expose an **OpenAI-compatible API** — meaning they use the same `openai` Python client library, just with a different `base_url` and API key. The goal is to add `qwen` as a first-class provider type so that a superuser can configure a Qwen model for a group as easily as they configure an OpenAI/ChatGPT model today.

## Design Insight

Because DashScope's `/compatible-mode/v1` endpoint is OpenAI-compatible, the existing `LLMTypeOpenAI` class (which uses `langchain_openai.ChatOpenAI`) can be **reused directly** — just like it's already reused for Ollama. The key difference from `chatgpt` is that Qwen needs a custom `base_url` and its own `check_working()` logic (using Bearer auth like OpenAI, not unauthenticated like Ollama).

## Changes Required (7 files, all surgical)

### 1. `backend/common/enums/gllms_types.py` — Add enum value
- Add `QWEN = 'qwen'` to `GLLMsTypes`
- Add `GLLMsTypes.QWEN` to `public_api_gllms_types` list

### 2. `backend/tasks_lib/llm_lib/llm_ops.py` — Route Qwen to OpenAI handler
- Add `GLLMsTypes.QWEN` to the existing tuple on line 34:
  ```python
  elif llm_type in (GLLMsTypes.OLLAMA_LOCAL, GLLMsTypes.OLLAMA_REMOTE, GLLMsTypes.CHATGPT, GLLMsTypes.QWEN):
  ```

### 3. `backend/tasks_lib/llm_lib/llm_type_openai.py` — Handle Qwen in `check_working()`
- In `check_working()`: Qwen needs Bearer-token auth (like ChatGPT), not unauthenticated (like Ollama). Add `GLLMsTypes.QWEN` to a new branch that validates with an auth header, but hitting its own `base_url` + `/models` instead of `api.openai.com`:
  ```python
  if self.llm_type == GLLMsTypes.CHATGPT:
      # existing OpenAI check
  elif self.llm_type == GLLMsTypes.QWEN:
      full_url = f"{self.llm_api_base}/models"
      headers = {"Authorization": f"Bearer {self.llm_api_key.get_secret_value()}"}
      return requests.get(full_url, timeout=5, headers=headers).status_code == 200
  else:
      # existing Ollama check (no auth)
  ```
- **`stream_to_llm()` needs NO change** — The `ChatOpenAI` constructor already uses `base_url` for non-ChatGPT types. Qwen is not `GLLMsTypes.CHATGPT`, so it will naturally get `base_url=self.llm_api_base` (`https://dashscope-us.aliyuncs.com/compatible-mode/v1`).

### 4. `backend/alembic/versions/` — New Alembic migration
- Create a new migration to add `'qwen'` to the PostgreSQL `gllms_type_enum` enum type. Following the existing pattern from `1f84f4203c8f`:
  ```sql
  CREATE TYPE gllms_type_enum_new AS ENUM ('dummy','ollama_local','ollama_remote','chatgpt','gemini','claude','qwen');
  ALTER TABLE group_llms ALTER COLUMN gllms_type TYPE gllms_type_enum_new USING gllms_type::text::gllms_type_enum_new;
  DROP TYPE IF EXISTS gllms_type_enum;
  ALTER TYPE gllms_type_enum_new RENAME TO gllms_type_enum;
  ```

### 5. `backend/.init_sql_data/group_llms.json` — Add sample Qwen config
- Add a sample entry for new installations:
  ```json
  {
    "group_id": 1,
    "gllms_seqn": 4,
    "gllms_type": "qwen",
    "gllms_name": "Qwen Plus",
    "gllms_api_base": "https://dashscope-us.aliyuncs.com/compatible-mode/v1",
    "gllms_model": "qwen-plus",
    "gllms_api_key": "sk-your-dashscope-key"
  }
  ```

### 6. `cwa_db_schema.sql` — Update reference schema
- Add `'qwen'` to the `gllms_type_enum` definition (documentation/reference file)

### 7. `cwa_db_12tables_schema.sql` — Update reference schema
- Add `'qwen'` to the `gllms_type_enum` definition (documentation/reference file)

## What Does NOT Need to Change

| File / Area | Why No Change Needed |
|---|---|
| `llm_type_openai.py` `stream_to_llm()` | Already handles non-ChatGPT types with custom `base_url`. Qwen gets this for free. |
| **Frontend** (all components) | Entirely data-driven. LLM dropdown, status display, and SU management table all render from backend data. No hardcoded provider lists. |
| `workers.py` | Uses `LLMOps` which routes correctly via the dispatcher. |
| `vdb_llm_status_worker.py` | Calls `LLMOps.check_working()`, which will work via the dispatcher. |
| `su_manage_llms.py` (router/page) | Accepts `gllms_type` as a free string; no validation against an allowlist. |
| Pydantic schemas | `gllms_type` is typed as `str`, not constrained to specific values. |
| Token counting (`tiktoken_count.py`) | Already falls back to `o200k_base` encoding for unknown models. |
| `common/watchdogs/__init__.py` | `is_need_to_check_llm()` uses `public_api_gllms_types` list, which we update in step 1. |
| pip dependencies | Qwen uses the existing `openai`/`langchain_openai` packages. |

## Verification

1. Run the Alembic migration: `alembic upgrade head`
2. Via the SU Manage LLMs page, create a new LLM entry with:
   - Type: `qwen`
   - Name: `Qwen Plus`
   - API Base: `https://dashscope-us.aliyuncs.com/compatible-mode/v1`
   - Model: `qwen-plus`
   - API Key: your DashScope API key
3. Wait for the status worker cycle (~5 seconds) — the LLM should show status `success`/`Ready`
4. Go to Query Documents, select the Qwen LLM from the dropdown, submit a query, and verify streaming response
