-- Cognosa: update group_llms to current-generation vendor models (2026-08-19)
--
-- Idempotent: each UPDATE matches on (gllms_type, old gllms_model [, gllms_name]),
-- so re-running is a no-op. Portable to the EC2 databases (same schema/rows).
-- Review with the SELECT at the bottom before/after.
--
-- Requires backend code >= commit 71d8dea (Claude provider no longer sends
-- `temperature`, which Claude 5 / Opus 4.7+ reject with HTTP 400).
--
-- Apply:  psql "<postgresql url>" -f backend/tools/sql/update_llm_models_260819.sql
-- or see README.md in this folder for the venv/SQLAlchemy variant.

BEGIN;

-- Anthropic ---------------------------------------------------------------
UPDATE group_llms
   SET gllms_model = 'claude-sonnet-5',
       gllms_name  = 'Claude Sonnet 5'
 WHERE gllms_type = 'claude' AND gllms_model = 'claude-sonnet-4-5';

UPDATE group_llms
   SET gllms_model = 'claude-opus-5',
       gllms_name  = 'Claude Opus 5'
 WHERE gllms_type = 'claude' AND gllms_model = 'claude-opus-4-5';

-- Google ------------------------------------------------------------------
UPDATE group_llms
   SET gllms_model = 'gemini-3.7-flash',
       gllms_name  = 'Gemini 3.7 Flash'
 WHERE gllms_type = 'gemini' AND gllms_model = 'gemini-2.5-flash';

-- OpenAI ------------------------------------------------------------------
-- Rows previously named "GPT 5" (mid tier) -> gpt-5.6-terra
UPDATE group_llms
   SET gllms_model = 'gpt-5.6-terra',
       gllms_name  = 'GPT 5.6 Terra'
 WHERE gllms_type = 'chatgpt' AND gllms_model = 'gpt-5-mini' AND gllms_name = 'GPT 5';

-- Rows previously named "GPT 5 mini" (small tier) -> gpt-5.6-luna
UPDATE group_llms
   SET gllms_model = 'gpt-5.6-luna',
       gllms_name  = 'GPT 5.6 Luna'
 WHERE gllms_type = 'chatgpt' AND gllms_model = 'gpt-5-mini' AND gllms_name = 'GPT 5 mini';

-- Alibaba / DashScope -----------------------------------------------------
UPDATE group_llms
   SET gllms_model = 'qwen3.8-max',
       gllms_name  = 'Qwen 3.8 Max'
 WHERE gllms_type = 'qwen' AND gllms_model = 'qwen-plus';

COMMIT;

-- Verify ------------------------------------------------------------------
SELECT gllms_id, group_id, gllms_type, gllms_name, gllms_model, enabled, gllms_status
  FROM group_llms
 WHERE deleted = 0
 ORDER BY group_id, gllms_seqn;
