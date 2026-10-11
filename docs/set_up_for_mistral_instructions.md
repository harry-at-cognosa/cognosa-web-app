# Set up Mistral on Cognosa

Added 2026-10-11, commit `fbd20bc`. The `mistral` Group LLM type routes through the
OpenAI-compatible client, same as Qwen. Deployed to local, dev and demo. Verified 2026-10-11 with Small and Large on
pay-as-you-go, concise and full contexts.

## 1. Get an API key and activate a plan

1. Go to https://console.mistral.ai and create an account. Choose **Company**
   (invoicing only; features and limits are the same as Individual).
2. Left nav → **API Keys** → **Create new key**. Copy it; it is shown once.
3. Left nav → **Billing** → activate **Pay as you go** (card on file, no subscription).

A key with no active plan passes the `/v1/models` health check (status turns green)
but every chat call fails: `mistral-large-latest` returns 403 `tier_not_allowed`,
and `mistral-small-latest` returns 429 with `x-ratelimit-limit-req-minute: 0`.
In Cognosa both surface as "Undefined LLM error". The free Experiment tier was not
offered at sign-up on 2026-10-11; pay-as-you-go is the working path.

Check a key directly:

```
curl -s -o /dev/null -w '%{http_code}\n' https://api.mistral.ai/v1/chat/completions \
  -H 'Authorization: Bearer KEY' -H 'content-type: application/json' \
  -d '{"model":"mistral-small-latest","messages":[{"role":"user","content":"OK?"}],"max_tokens":5}'
```

200 means ready. 403 or 429 means the plan is not active.

## 2. Add the cloud model as a Group LLM

Superuser → Manage LLMs → New.

| Field    | Value                          |
|----------|--------------------------------|
| Type     | `mistral`                      |
| Name     | `Mistral Large`                |
| API Base | `https://api.mistral.ai/v1`    |
| Model    | `mistral-large-latest`         |
| API Key  | key from step 1                |

Status turns green within a minute. Green only proves the key is valid, not
that a plan is active (see step 1). Other model ids: `mistral-medium-latest`, `mistral-small-latest`,
`magistral-medium-latest`, `codestral-latest`.

## 3. Add a local Mistral via Ollama on the M2 (10.0.100.212)

On the M2:

```
ollama pull mistral-small3.2
```

Then a second Group LLM row:

| Field    | Value                            |
|----------|----------------------------------|
| Type     | `ollama_remote`                  |
| Name     | `Ollama Mistral Small (M2)`      |
| API Base | `http://10.0.100.212:11434/v1`   |
| Model    | `mistral-small3.2`               |
| API Key  | `ollama`                         |

Confirm the exact tag on https://ollama.com/library before pulling.

## 4. Test

Query Documents → pick the Mistral LLM from the dropdown → submit a query →
check the streamed answer.

## Pricing reference (La Plateforme, Oct 2026, $/M tokens in/out)

| Model          | In   | Out  |
|----------------|------|------|
| Small 4        | 0.15 | 0.60 |
| Large 3        | 0.50 | 1.50 |
| Medium 3.5     | 1.50 | 7.50 |
| Ministral 3/8/14B | 0.10–0.20 | same |
