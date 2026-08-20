# What was done today — 2026-08-20

Both EC2 hosts (dev.cognosa.net, demo.cognosa.net) are refreshed and running the
same software and data as the M1 Studio.

## What was done

**TLS** — both certs had been expired since 13 July; renewed zero-downtime, valid
to 18 Nov 2026; root cron (Mon/Thu 03:17 UTC) on both hosts renews and reloads
nginx automatically.

**Deploy revamp** (commits `c9a3751`…`b2473bf`, pushed to GitHub + GitLab):

- `~/cognosa-src` git clone is the docker build context; `~/cognosa` holds only
  per-host config and data.
- `cd ~/cognosa && ./deploy.sh [ref]` — fetch, checkout, build app+rt,
  `alembic upgrade head`, restart app/rt only, wait for app, reload nginx,
  verify. Three real-world bugs surfaced and were fixed along the way (stale
  nginx upstream, early reload, sudo/git ownership).
- systemd unit is now oneshot/`up -d`; `ubuntu` is in the docker group; the
  developer `.env` is no longer baked into images; HF model cache persisted in a
  volume; certbot behind a compose profile.
- Full procedure in `release/ec2_ubuntu_24_04/cognosa/!README.MD`; the old QWEN
  doc is marked superseded.

**Data** — both hosts: Postgres replaced wholesale with today's local `cwa_db`
dump (4 groups incl. NAAG, 11 users, Claude 5-era model names; pgvector remnants
filtered out); `furocad` (216 pts) and `furocad_footnotes` (937 pts) recovered
into Qdrant. App-side status pollers show all NAAG VDBs and all five NAAG LLMs
**Ready** on both hosts — i.e. the Claude 5 temperature fix is confirmed
end-to-end.

**Final state:** dev and demo at `32fa564`, HTTPS 200, pre-replacement DB
backups at `~/cognosa/pg_backup_{dev,demo}_pre_v045_260820.dump`, old code
parked in `~/cognosa/backend_copydeploy_pre_260820/`.

## Left to do

- Log in at dev.cognosa.net / demo.cognosa.net and run a NAAG query against
  FUROCAD — an authenticated query was not exercised (no credentials in the
  session).
- Backlog (recorded in Claude memory): superuser "clone LLM entry" UI idea;
  CPU-only torch to shrink the rt image (currently 6–10 GB).
- When the repo goes private: add a read-only deploy key per host and re-point
  `~/cognosa-src`'s remote to SSH (see `docs/github_going_private.md`).
