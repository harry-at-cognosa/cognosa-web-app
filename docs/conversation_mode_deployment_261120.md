# Conversation mode — deployment to dev and demo

Written 2026-11-20. Covers deploying the Chat capability to the two EC2 hosts, the
version labels, and how to roll back. Section 6 is the log of the dev deployment, filled
in as each step was run.

---

## 1. Version labels

The repository uses three-part version numbers with `v` tags (`v0.48.0` was the only tag).

| Label | What it is | Use |
|---|---|---|
| `v0.49.0` | `main` as it stood before any chat code (commit `12c4b60`). Everything built since 0.48.0: resizable tables, Manage Doc Tasks filters, cancel button, backup scripts. | **Rollback point.** |
| `v1.0.0` | The first version with Chat. Tagged 2026-11-20 after dev passed. | What dev and demo run. |

Fixes found while testing become `v1.0.1`, `v1.0.2`, and so on.

Dev first ran the branch `feature/conversation-mode` by name (section 6), then `v1.0.0`.

---

## 2. Hosts (checked live 2026-11-20)

| | dev | demo |
|---|---|---|
| Address | dev.cognosa.net, 44.230.124.164 | demo.cognosa.net, 52.13.212.94 |
| Instance | `i-01cf57d1433d161fc`, `c6a.xlarge` (4 vCPU, 8 GiB) | `i-0cb656285d48d9bfc`, `c6a.xlarge` |
| Disk | 48 GiB gp3; 14 GiB free before deploy | 48 GiB gp3 |
| Running before deploy | commit `6ae5de4` (2026-10-27), migration `7c3d9e2a1b54` | not checked (stopped) |

**No resizing is needed.** On dev, memory in use before the deploy was 2.4 GiB of 7.7 GiB
(`rt` 2.0 GiB, Qdrant 1.0 GiB). The chat container is one more Python process holding one
small embedding model. Disk: the chat image is the `rt` image with a different start
command, so it adds almost nothing; 14 GiB of Docker build cache can be reclaimed if
space ever runs short (`docker builder prune`).

Access: `ssh -i ~/ctc01instance.pem ubuntu@<address>` from the M1. Both hosts stop at
01:00 Pacific every night; start with `~/bin/startup_dev.sh` or `startup_demo.sh`.

---

## 3. What the deployment changes on a host

- **Database:** one additive migration (`3f8a1c5d9e27`): two new tables, three new columns,
  one settings row. Nothing existing is altered or removed.
- **Containers:** `app` and `rt` are rebuilt; a new `chat` container is added.
- **nginx:** one new `location /api/v1/chat/` block, added by hand (the host's nginx config
  is never overwritten by a deploy).
- **Chat stays off** for every group until a superuser turns it on.

---

## 4. Procedure for one host

Run from `~/cognosa` on the host unless stated.

**Step 1 — Back up the database.**

```
docker compose exec -T db sh -c 'pg_dump -Fc -U "$POSTGRES_USER" "$POSTGRES_DB"' > pg_backup_pre_chat_$(date +%y%m%d).dump
```

**Step 2 — Back up the nginx config.**

```
cp nginx/conf.d/default.conf nginx/conf.d/default.conf.bak-pre-chat
```

**Step 3 — Deploy.** Builds the images, applies the migration, starts the chat container.

```
./deploy.sh v1.0.0          # dev, before the tag exists: ./deploy.sh origin/feature/conversation-mode
```

The first run on a host uses the previous copy of `deploy.sh`, which does not know about
chat; it still works, because `docker compose up -d` builds and starts any container that
is missing. A line `!! nginx -> chat returned 404` on later runs before step 4 is expected.

**Step 4 — Add the nginx route.** In `nginx/conf.d/default.conf`, inside the
`listen 443 ssl` server, above the line `# Proxy everything to the FastAPI app (uvicorn)`:

```
    location /api/v1/chat/ {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://chat:8001;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_read_timeout 600s;
    }
```

**Step 5 — Test and reload nginx.**

```
docker compose exec -T nginx nginx -t          # must say: syntax is ok / test is successful
docker compose exec -T nginx nginx -s reload
```

**Step 6 — Confirm the route.** An unauthenticated request must reach the chat service and
be refused:

```
curl -s -o /dev/null -w '%{http_code}\n' https://<host name>/api/v1/chat/options     # expect 401
```

**Step 7 — Confirm queries still work.** Log in and run one ordinary query.

**Step 8 — Turn chat on for a group.** SuperUser / Groups, edit the group, switch `Chat?`
on. Users of that group see `Query Documents` / `Chat` after their next page load.

**Step 9 — Test chat.** From the M1, with a user of that group:

```
cd ~/cognosa_web_app/backend
../venv/bin/python -m tools.chat_smoke --base https://<host name> --web https://<host name> \
    --user NAME --password PASSWORD --turns
```

Then in a browser: ask a question, ask a follow-up, stop an answer, reload the page.

**Step 10 — (optional) Set the chat settings** for the group's collections: SuperUser / VDBs,
`Chat Settings`. Drafts for group 2 are in `conversation_mode_group2_chat_settings_draft.md`.

---

## 5. Rolling back

The migration is additive, so the older code runs against the migrated database
unchanged. Rolling back is therefore one command and needs no database step:

```
cd ~/cognosa && ./deploy.sh v0.49.0
```

- The chat container is left running by that command but nothing routes users to it once
  the older web app no longer shows the `Chat` menu entry. To stop it:
  `docker compose stop chat` is not available under the older compose file; use
  `docker stop cognosa-chat-1`.
- The nginx block can stay. If the chat container is removed entirely, remove the block
  too (restore `default.conf.bak-pre-chat` and reload), because nginx will not load a
  config that names a container which does not exist.
- To return dev to exactly what it ran before this deployment: `./deploy.sh 6ae5de4`.
- Only if the chat tables themselves must go:
  `docker compose run --rm --no-deps app alembic downgrade 7c3d9e2a1b54`, run **while the
  chat-capable code is still deployed**. This deletes all stored conversations.
- Last resort: restore the dump from step 1 (see the deploy README, "Refresh data").

---

## 6. Log — dev, 2026-11-20

All times UTC (2026-11-21 04:50–05:00; evening of 2026-11-20 Pacific). Run from the M1
over SSH. Deployed ref: branch `feature/conversation-mode` at commit `7fdf59f`.

| # | Step | Result |
|---|---|---|
| 0 | Local preparation | Slice 7 committed. `v0.49.0` tagged on pre-chat `main` (`12c4b60`). `main`, the tag and the branch pushed to GitHub. |
| 1 | Database backup | `~/cognosa/pg_backup_pre_chat_261120.dump`, 969 KB, readable (13 tables of data). |
| 2 | nginx config backup | `~/cognosa/nginx/conf.d/default.conf.bak-pre-chat`. |
| 3 | `./deploy.sh origin/feature/conversation-mode` | Exit code 0, about 4.5 minutes. Migration `7c3d9e2a1b54 -> 3f8a1c5d9e27` applied. `app`, `rt` and the new `chat` container started. Output kept in `~/cognosa/deploy_chat_261120.log`. |
| 3a | Chat container check | Started cleanly, loaded the embedding model in 13 s, answers 401 inside the Docker network. Through nginx: 404, as expected before step 4. |
| 4 | nginx route added | Block inserted above `location /` in the 443 server; the only difference from the backup is those 15 lines. |
| 5 | nginx test and reload | "syntax is ok", "test is successful"; reloaded. |
| 6 | Route check | `https://dev.cognosa.net/api/v1/chat/options` returns 401; login page returns 200. |
| 7 | Ordinary query | As `lb_admin`, a Casambi query with Claude Sonnet 5 completed (status 6, 1,644 characters, search 0.4 s, LLM 4.5 s). Test query deleted. |
| 8 | Chat switched on | Group 2 only, by SQL (`update api_groups set chat_enabled = true where group_id = 2`), because `lb_admin` is not a superuser on dev. |
| 9 | Chat smoke test with real turns | 25 of 25 passed against `https://dev.cognosa.net` as `lb_admin`: streamed answer (89 pieces, first after 4.3 s), follow-up rewritten before searching, stop, refusal of a second send, two conversations at once. Test conversations deleted. |
| 10 | Chat settings | Not applied. Both group 2 collections run on the defaults. |

**State after deployment**

- Containers: `app`, `chat`, `db`, `nginx`, `qdrant`, `rt` all running.
- Memory: `chat` 0.9 GiB, `rt` 1.7 GiB; 4.5 GiB available on the host.
- Disk: 14 GiB free, unchanged.
- Chat log: no errors. Logs are in `~/cognosa/chat_logs/`.
- No conversations or messages left in the database.

**Issues and observations**

1. **`lb_admin` is not a superuser on dev** (it is on the local M1 database), so the
   switch could not be set through SuperUser / Groups with that account. The superuser
   in group 2 on dev is `hal_ledra`. Step 8 was done by SQL instead.
2. **The first deploy ran the previous `deploy.sh`**, as predicted in section 4, so it
   did not print the new "nginx -> chat" line. Later deploys will.
3. **nginx was not restarted by the deploy**, only reloaded. Adding `chat` to its
   `depends_on` did not recreate the container.
4. **Not yet checked on dev:** the Chat page in a browser (the smoke test exercises the
   service through nginx, not the page), the filter control, "Open in Queries", the
   download, and the other three LLM types.
5. **Demo is untouched** and stopped. It still needs the whole of section 4.
