# cwa_db backup / restore scripts — plan

Date: 2026-10-02. Status: `cwa_db_common.sh` and `cwa_db_backup.sh` built and run
against `m1`, `dev` and `demo` (build step 1 of section 7). `-qdrant` on backup is built
and run against `dev` and `demo`; on `m1` it was only exercised as far as the preflight
abort, because Qdrant was not running there. Restore (including its `-qdrant` half) and
the `README.md` are not written yet.

## 1. Scope

Two bash scripts, run from M1 (or any Mac that has `~/0_hold_cwa_db`), plus one shared
include:

```
backend/tools/db/
    cwa_db_common.sh      target table, preflight checks, logging (sourced, not run)
    cwa_db_backup.sh      dump a target's cwa_db into ~/0_hold_cwa_db
    cwa_db_restore.sh     replace a target's cwa_db from a dump in ~/0_hold_cwa_db
    README.md             usage + required platform state (section 6 of this plan)
```

Phase 1 targets: `m1`, `dev`, `demo`. Targets `m2`, `m3`, `m4` are deferred (section 8).
Qdrant collections are optional and off by default (section 5).

The remote procedure is the manual one already documented in
`release/ec2_ubuntu_24_04/cognosa/!README.MD` ("Refresh data from another environment"),
scripted.

## 2. Targets

| Tag | Host | Access | Postgres | DB superuser | Working dir |
|---|---|---|---|---|---|
| `m1` | localhost (10.0.100.211) | local | Postgres.app 17.6, pgvector 0.8.0 | `postgres` (passwordless locally) | — |
| `dev` | dev.cognosa.net | `ssh -i ~/ctc01instance.pem ubuntu@…` | `postgres:17` container `db`, no pgvector | `$POSTGRES_USER` from `env_db.env` (`cwa_user`) | `/home/ubuntu/cognosa` |
| `demo` | demo.cognosa.net | same key | same (assumed; verified at preflight) | same | `/home/ubuntu/cognosa` |

Differences that drive the design:

- On EC2 the superuser is `cwa_user`, not `postgres`, and every `pg_*` command runs as
  `docker compose exec -T db …` over SSH. Credentials are never passed from M1; the
  container's own `$POSTGRES_USER` / `$POSTGRES_DB` are used.
- EC2 has no pgvector. A dump taken on a Mac contains the `vector` extension and the
  `langchain_pg_*` tables, which must be filtered out of the restore TOC or
  `--exit-on-error` aborts part-way.
- Owners differ between environments, so every restore uses `-O -x`
  (`--no-owner --no-privileges`). This is a deliberate departure from the bare
  `pg_restore -U postgres -d cwa_db <file>` in the original request: without `-O`, an
  EC2-origin dump fails on M1 because role `cwa_user` does not exist there.
- VDB and LLM endpoints in the data are symbolic (`qdrant_local`, `pg_local`,
  `chroma_local`, resolved per host from env), so rows are portable across environments.
  The exception is function, not addressing: the M1 `pgvector` VDB row has no backing
  tables on EC2 after the TOC filter, and the `chroma` row needs a Chroma server.

A target tag whose address belongs to the machine running the script is handled in local
mode; otherwise in SSH mode. All paths use `$HOME`, so the `harry` / `harryAtMac`
difference does not matter on the machine running the script.

## 3. Backup — `cwa_db_backup.sh <target> [-label <text>] [-qdrant]`

Output: `~/0_hold_cwa_db/cwa_db_<target>_<YYMMDD_HHMMSS>[_<label>].dump`
(timestamp from the local clock; label is free text, sanitised to `[A-Za-z0-9._-]`, for
the version/colour tags currently added by hand).

1. **Preflight — abort with a warning before anything else if any check fails.**
   - `~/0_hold_cwa_db` exists and is writable.
   - Local: `pg_dump` on PATH; `psql … -d cwa_db -c 'select 1'` succeeds.
   - Remote: SSH connects (`BatchMode=yes`, `ConnectTimeout=10`, `IdentitiesOnly=yes`);
     the `db` container is running; `select 1` on `cwa_db` succeeds inside it.
2. **Dump.**
   - Local: `pg_dump -U postgres -h localhost -Fc -f <file>.partial cwa_db`
   - Remote: streamed straight to M1, no file left on the server:
     `ssh … 'cd ~/cognosa && docker compose exec -T db sh -c "pg_dump -Fc -U \"\$POSTGRES_USER\" \"\$POSTGRES_DB\""' > <file>.partial`
3. **Verify.** Non-zero size and `pg_restore -l <file>.partial` reads the TOC. Only then
   rename `.partial` to the final name; on failure the partial is deleted and the script
   exits non-zero.
4. **Report and log.** File, size, TOC entry count, source `alembic_version`. One line
   appended to `~/0_hold_cwa_db/backup_restore.log`.
5. `-qdrant`: see section 5.

Dumps are full fidelity (no `-O -x` at dump time); ownership and pgvector differences are
handled at restore time, so any dump can be restored to any target.

## 4. Restore — `cwa_db_restore.sh <target> <dump> [-noprompt] [-nomigrate] [-qdrant]`

`<dump>` is a filename in `~/0_hold_cwa_db` or a full path.

1. **Preflight — abort with a warning before anything else if any check fails.**
   - Dump file exists and `pg_restore -l` reads it.
   - Server reachable (SSH for remote) and the database server answers on the
     maintenance DB `postgres`. Whether `cwa_db` currently exists is noted; if it does
     not (e.g. after a failed restore), steps 3 and the drop are skipped.
   - Target's `pg_restore` major version ≥ the dump's `pg_dump` major version (all three
     phase-1 targets are 17 today).
   - **Local only:** if any session other than the script's own is connected to `cwa_db`,
     abort and list them (`pid`, `usename`, `application_name`, `client_addr`, `state`
     from `pg_stat_activity`). Nothing is terminated.
   - With `-qdrant`: the matching snapshot set exists (section 5).
2. **Confirm.** Print target, dump file, size, dump origin/time, and the target's current
   `alembic_version`; require the target tag to be typed. `-noprompt` skips this.
3. **Safety dump.** The target's current `cwa_db` is dumped via the backup routine to
   `~/0_hold_cwa_db/cwa_db_<target>_<stamp>_prerestore.dump` (for remote targets this
   lands on M1 directly). Restore does not proceed unless this succeeds.
4. **Remote only — stop writers:** `docker compose stop app rt`.
5. **Remote only — upload:** `scp` the dump to `/home/ubuntu/cognosa/db_restore/`,
   verify SHA-256 against the local file, then pipe it into the `db` container
   (`/tmp/d.dump`).
6. **TOC filter.** If the target has no `vector` in `pg_available_extensions`, build the
   TOC with
   `pg_restore -l | grep -vE "EXTENSION.*vector|langchain_pg_|ix_cmetadata_gin"` and
   restore with `-L`. Decided by probing the target, not by target name.
7. **Replace.**
   - Local:
     ```
     dropdb   -U postgres cwa_db
     createdb -U postgres cwa_db
     pg_restore -U postgres -d cwa_db -O -x --exit-on-error [-L toc] <dump>
     ```
   - Remote (inside the `db` container):
     ```
     psql -U "$POSTGRES_USER" -d postgres -c "DROP DATABASE cwa_db" -c "CREATE DATABASE cwa_db"
     pg_restore -U "$POSTGRES_USER" -d cwa_db -O -x --exit-on-error -L /tmp/toc.txt /tmp/d.dump
     ```
   - On failure: stop, leave `app`/`rt` stopped (remote), keep the uploaded dump, and
     print the exact command that restores the safety dump. No automatic rollback.
8. **Migrate (default on; `-nomigrate` skips).** Read `alembic_version` before, run
   `alembic upgrade head`, read it after.
   - Remote: `docker compose run --rm --no-deps app alembic upgrade head` (as `deploy.sh`).
   - Local: `backend/` with `venv/bin/alembic upgrade head`.
   - Output is explicit either way: `MIGRATED <old> -> <new>` or
     `schema already at head (<rev>), no migration`. A dump newer than the deployed code
     (revision unknown to alembic) is reported as a warning, not a failure.
9. **Remote only — restart:** `sudo systemctl restart cognosa` (full down/up, refreshes
   the nginx upstream), then wait for the app and check `https://localhost/` as
   `deploy.sh` does. Remove the uploaded dump and container temp files on success.
10. **Report and log.** Row counts for `api_users`, `api_groups`, `group_vdbs`; final
    `alembic_version`; the collection check from section 5; one line in
    `backup_restore.log`.

## 5. Qdrant collections (optional, default off)

Postgres-only is the default for both scripts. Collections are mostly static; a dedicated
per-collection / per-group / all-collections tool is a separate future project.

- **Always, on restore (report only):** compare
  `select distinct gvdbs_collection from group_vdbs where gvdbs_type='qdrant' and deleted=0`
  with the target's `GET /collections`, and warn for each collection the restored
  database references that the target's Qdrant does not have.
- **`-qdrant` on backup (built):** Qdrant reachability and, on EC2, at least 2 GB free
  on `/` are checked in preflight, before the Postgres dump. Then, for every collection
  on the target: create a snapshot, stream it back gzipped, delete the server-side
  snapshot, and verify the SHA-256 that Qdrant reported. Files:
  `~/0_hold_cwa_db/qdrant_<target>_<YYMMDD_HHMMSS>_<collection>.snapshot.gz` (same stamp
  as the dump taken in that run) plus `qdrant_<target>_<YYMMDD_HHMMSS>.manifest`
  (`collection|points|sha256|file`). The manifest is written last, so a set without one
  is incomplete. On EC2 the calls run on the host over SSH. Measured 2026-10-02: seven
  collections, about 245 MB compressed, about 75 seconds per host.
- **`-qdrant` on restore:** restore the snapshot set whose target and stamp match the
  dump filename and whose manifest exists, using the README's `snapshots/recover` procedure (it creates missing
  collections; `snapshots/upload` 404s on a new collection in 1.15.5). Collections on the
  target that are not in the set are left untouched.

## 6. Required platform state

| Operation | State before running | What the script changes | Downtime |
|---|---|---|---|
| Backup, any target | DB server up. App may be running and in use. | Nothing. | None |
| Restore `m1` | Postgres.app up. Web app, `run_tasks` and any SQL client (DataGrip) disconnected from `cwa_db`. | Aborts and lists sessions if any are connected. Does not start or stop the app. | Until the app is restarted by hand |
| Restore `dev` / `demo` | Instance running, full compose stack up (`db` must be up). | Stops `app` + `rt`, replaces the DB, migrates, restarts the `cognosa` service. | Roughly 1–2 minutes |

## 7. Build and test order

1. `cwa_db_common.sh` + `cwa_db_backup.sh`; back up `m1`, `dev`, `demo`; check each with
   `pg_restore -l`.
2. `cwa_db_restore.sh` local mode; restore an `m1` dump to `m1`, then a `dev` dump to `m1`.
3. Remote mode against `dev`: restore a `dev` dump to `dev` (round trip), then an `m1`
   dump to `dev` (exercises the pgvector filter and migration reporting).
4. `demo` last, round trip only, once `dev` is clean.
5. `-qdrant` on both scripts.
6. `m2`–`m4`.

## 8. Deferred: m2, m3, m4

| Tag | Address | Home |
|---|---|---|
| `m1` | 10.0.100.211 | `/Users/harry` |
| `m2` | 10.0.100.212 | `/Users/harryAtMac` |
| `m3` | 10.0.100.210 | `/Users/harryAtMac` |
| `m4` | 10.0.100.215 | `/Users/harry` |

Intended approach: SSH to the Mac, run its native `pg_dump` / `pg_restore`, stream the
dump over the SSH connection (no shared mount needed). To settle when this is built:
Remote Login and key auth on each Mac; the SSH user per host; full path to the Postgres
binaries, since Postgres.app is not on PATH in a non-interactive SSH shell; the
Postgres major version and pgvector presence on each.

## 9. Assumptions not yet verified

- Verified 2026-10-02 by the backup runs: SSH to `dev` and `demo` with
  `~/ctc01instance.pem`; both run PostgreSQL 17.9 in the `db` container with the same
  compose layout; M1's `pg_restore` 17.6 reads their dumps; all three databases are at
  alembic revision `22cb85c671f5`.
- Not yet verified: `ubuntu` has passwordless `sudo` for `systemctl restart cognosa`.
- The EC2 instances are sometimes stopped; preflight reports an unreachable host and
  exits, and does not start instances.
