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

## 2. Add the cloud models as Group LLMs

Superuser → Manage LLMs → New. The two rows created 2026-10-11 (same key for both):

| Field    | Row A                          | Row B                          |
|----------|--------------------------------|--------------------------------|
| Type     | `mistral`                      | `mistral`                      |
| Name     | `Mistral Large`                | `Mistral Small`                |
| API Base | `https://api.mistral.ai/v1`    | `https://api.mistral.ai/v1`    |
| Model    | `mistral-large-latest`         | `mistral-small-latest`         |
| API Key  | key from step 1                | key from step 1                |

Status turns green within a minute. Green only proves the key is valid, not
that a plan is active (see step 1). Other model ids: `mistral-medium-latest`,
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

Confirm the exact tag on https://ollama.com/library before pulling. `magistral`
(24B reasoning variant, same footprint) is also pulled on the M2; a row for it is
the same as above with Model `magistral`.

Ollama on the M2 must listen on the LAN, not just localhost, or the status check
says "server not found". Set `OLLAMA_HOST=0.0.0.0` in whatever launches it
(the M2 runs it as a service, not the menu-bar app) and restart. Watch for
leading/trailing spaces when pasting API Base and Model; they are saved verbatim.

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

## Timings, 2026-10-11

Same question against the same collection, local Cognosa on the M1 Max.

| LLM | Context | Sent / received tokens | Time | Answer |
|---|---|---|---|---|
| Mistral Small, API | short and concise | 16,588 / 272 | 3.1 s | adequate |
| Mistral Large, API | fully documented | 16,537 / 497 | 8.2 s | most comprehensive |
| Mistral Small 3.2, Ollama on M2 over LAN | fully documented | 16,889 / 202 | 133.4 s | brief, correct |

The 133 s is almost entirely prefill: ~17K tokens of context must be processed
before the first output token, and an M2 Studio prefills a 24B Q4 model at
roughly 150 tokens/s. Generating 200 tokens takes a few seconds. The first call
also paid the model load. A repeat query on a warm model is faster but still
well over a minute at this context size, so the local path is for privacy or
cost, not latency. The concise context cuts it substantially.
