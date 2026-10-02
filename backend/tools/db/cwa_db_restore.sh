#!/usr/bin/env bash
# Replace a target's cwa_db with a dump from ~/0_hold_cwa_db.  DESTRUCTIVE.
#
#   cwa_db_restore.sh <target> <dump> [-noprompt] [-nomigrate]
#
#   target      m1 | dev | demo        (m2, m3, m4: not implemented yet)
#   dump        a file in ~/0_hold_cwa_db, or a full path
#   -noprompt   do not ask for confirmation
#   -nomigrate  do not run `alembic upgrade head` after the restore
#
# Sequence: preflight, confirm, safety dump of the current database to
# ~/0_hold_cwa_db/cwa_db_<target>_<stamp>_prerestore.dump, drop, create,
# pg_restore -O -x, alembic upgrade head, report.
#
# Required state before running:
#   m1         Postgres up; web app, run_tasks and SQL clients disconnected
#              from cwa_db (the script aborts and lists sessions otherwise).
#              Restart the app by hand afterwards.
#   dev, demo  Instance up, compose stack up. The script stops app + rt,
#              restores, and restarts the cognosa service (1-2 min downtime).
# Plan: docs/DB_BACKUP_RESTORE_PLAN.md
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
. "$SCRIPT_DIR/cwa_db_common.sh"
REPO_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
BACKEND_DIR="$REPO_DIR/backend"
ALEMBIC="$REPO_DIR/venv/bin/alembic"

# Objects a pgvector-free Postgres cannot restore (see release !README.MD).
TOC_FILTER='EXTENSION.*vector|langchain_pg_|ix_cmetadata_gin'

usage() { sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; }

TARGET=""
DUMP_ARG=""
PROMPT=1
MIGRATE=1
while [ $# -gt 0 ]; do
    case "$1" in
        -noprompt)  PROMPT=0; shift ;;
        -nomigrate) MIGRATE=0; shift ;;
        -qdrant)    die "-qdrant is not implemented yet in restore (plan section 5)" ;;
        -h|-help|--help) usage; exit 0 ;;
        -*)         die "unknown option '$1' (try -h)" ;;
        *)          if [ -z "$TARGET" ]; then TARGET="$1"
                    elif [ -z "$DUMP_ARG" ]; then DUMP_ARG="$1"
                    else die "unexpected argument '$1'"; fi
                    shift ;;
    esac
done
[ -n "$TARGET" ] && [ -n "$DUMP_ARG" ] || { usage; exit 1; }

target_resolve "$TARGET"

# ------------------------------------------------------------------ preflight
# Everything here runs before anything is changed.
preflight_hold_dir
preflight_local_tools

if [ -f "$DUMP_ARG" ]; then DUMP="$DUMP_ARG"
elif [ -f "$HOLD_DIR/$DUMP_ARG" ]; then DUMP="$HOLD_DIR/$DUMP_ARG"
else die "dump file '$DUMP_ARG' not found (looked in . and $HOLD_DIR)"; fi
pg_restore -l "$DUMP" >/dev/null 2>&1 || die "$DUMP is not a readable pg_dump archive"

preflight_server

HAVE_DB=0
if db_exists; then HAVE_DB=1; fi

DMAJ="$(dump_pg_major "$DUMP")"
TMAJ="$(target_pg_major)"
if [ -n "$DMAJ" ] && [ -n "$TMAJ" ] && [ "$DMAJ" -gt "$TMAJ" ]; then
    die "dump was written by pg_dump $DMAJ; $T_TAG has pg_restore $TMAJ and cannot read it"
fi

if [ "$T_MODE" = "local" ]; then
    if [ "$HAVE_DB" = 1 ]; then
        SESSIONS="$(db_other_sessions)"
        if [ -n "$SESSIONS" ]; then
            warn "$T_TAG: $DB_NAME has open sessions; close them and run again. Nothing was changed."
            say "pid|user|application|client|state"
            say "$SESSIONS"
            exit 1
        fi
    fi
    if [ "$MIGRATE" = 1 ]; then
        [ -x "$ALEMBIC" ] || die "$ALEMBIC not found (needed for the migration step; or pass -nomigrate)"
    fi
else
    rsh_n 'sudo -n systemctl cat cognosa >/dev/null' 2>/dev/null \
        || die "$T_TAG: cannot run 'sudo systemctl' for the cognosa service without a password"
fi

NEED_FILTER=1
if db_has_pgvector; then NEED_FILTER=0; fi

STAMP="$(date +%y%m%d_%H%M%S)"
REV_TARGET="none"
if [ "$HAVE_DB" = 1 ]; then REV_TARGET="$(db_alembic_rev)"; fi

# -------------------------------------------------------------------- confirm
say "== restore $DB_NAME on $T_TAG ($T_HOST, $T_MODE)"
say "   dump      $DUMP"
say "   size      $(file_size_h "$DUMP"), $(dump_toc_count "$DUMP") TOC entries"
say "   source    PostgreSQL $(dump_from_version "$DUMP")"
if [ "$HAVE_DB" = 1 ]; then
    say "   target    $DB_NAME exists, alembic $REV_TARGET; it will be DROPPED and replaced"
else
    say "   target    $DB_NAME does not exist; it will be created"
fi
if [ "$NEED_FILTER" = 1 ]; then
    say "   pgvector  not available on $T_TAG: the vector extension and langchain_pg_* tables will be skipped"
fi
if [ "$T_MODE" = "ssh" ]; then
    say "   services  app + rt will be stopped, then the cognosa service restarted"
fi

if [ "$PROMPT" = 1 ]; then
    [ -t 0 ] || die "not running on a terminal; pass -noprompt to run unattended"
    printf 'Type the target name (%s) to proceed: ' "$T_TAG"
    read -r ANSWER || ANSWER=""
    [ "$ANSWER" = "$T_TAG" ] || die "confirmation did not match; nothing was changed"
fi

# ---------------------------------------------------------------- safety dump
SAFETY=""
if [ "$HAVE_DB" = 1 ]; then
    SAFETY="$HOLD_DIR/cwa_db_${T_TAG}_${STAMP}_prerestore.dump"
    say "== safety dump of the current database"
    dump_target "$SAFETY"
    say "   $SAFETY ($(file_size_h "$SAFETY"))"
    log_line "backup  target=$T_TAG file=$(basename "$SAFETY") size=$(file_size_h "$SAFETY") alembic=$REV_TARGET (pre-restore)"
fi

TMP_TOC=""
TMP_LOG="$(mktemp -t cwa_db_restore)"
trap 'rm -f "$TMP_LOG" "$TMP_TOC"' EXIT

RDIR="$REMOTE_OPS/db_restore"
RFILE="$RDIR/restore_$STAMP.dump"
STOPPED=0

# Failure before the drop: the target's database is intact.
abort_intact() {
    if [ "$STOPPED" = 1 ]; then
        rsh_n "cd $REMOTE_OPS && docker compose start app rt" >/dev/null 2>&1 \
            || warn "$T_TAG: could not restart app + rt; run 'docker compose start app rt' in $REMOTE_OPS"
    fi
    log_line "restore ABORTED target=$T_TAG dump=$(basename "$DUMP") reason=$1"
    die "$1. $DB_NAME on $T_TAG was not changed."
}

# Failure after the drop: the target's database is missing or incomplete.
fail_dropped() {
    warn "$1"
    say "$DB_NAME on $T_TAG is now missing or incomplete."
    if [ -n "$SAFETY" ]; then
        say "To put the previous database back:"
        say "   $0 $T_TAG $SAFETY -noprompt"
    fi
    if [ "$T_MODE" = "ssh" ]; then
        say "app + rt are still stopped on $T_TAG; the uploaded dump was kept at $RFILE"
    fi
    [ -s "$TMP_LOG" ] && { say "--- last output:"; tail -20 "$TMP_LOG"; }
    log_line "restore FAILED target=$T_TAG dump=$(basename "$DUMP") safety=$(basename "${SAFETY:-none}")"
    exit 1
}

# -------------------------------------------------------------------- replace
if [ "$T_MODE" = "ssh" ]; then
    say "== stopping app + rt on $T_TAG"
    rsh_n "cd $REMOTE_OPS && docker compose stop app rt" >"$TMP_LOG" 2>&1 \
        || abort_intact "could not stop app + rt"
    STOPPED=1
    SESSIONS="$(db_other_sessions || true)"
    if [ -n "$SESSIONS" ]; then
        say "pid|user|application|client|state"
        say "$SESSIONS"
        abort_intact "$DB_NAME still has the open sessions listed above"
    fi

    say "== uploading the dump"
    rsh_n "mkdir -p $RDIR" || abort_intact "could not create $RDIR"
    rcp "$DUMP" "$RFILE" || abort_intact "upload failed"
    SUM_LOCAL="$(shasum -a 256 "$DUMP" | cut -d' ' -f1)"
    SUM_REMOTE="$(rsh_n "sha256sum $RFILE" | cut -d' ' -f1)"
    [ "$SUM_LOCAL" = "$SUM_REMOTE" ] || abort_intact "uploaded dump does not match the local file (SHA-256)"
    rsh_n "cd $REMOTE_OPS && docker compose exec -T db sh -c 'cat > /tmp/d.dump' < $RFILE" \
        || abort_intact "could not copy the dump into the db container"
    LOPT=""
    if [ "$NEED_FILTER" = 1 ]; then
        rdb "pg_restore -l /tmp/d.dump | grep -vE \"$TOC_FILTER\" > /tmp/toc.txt" </dev/null \
            || abort_intact "could not build the restore list"
        LOPT="-L /tmp/toc.txt"
    fi

    say "== drop, create, restore"
    rdb "psql -X -w -q -v ON_ERROR_STOP=1 -U \"\$POSTGRES_USER\" -d postgres -c \"DROP DATABASE IF EXISTS $DB_NAME\" -c \"CREATE DATABASE $DB_NAME\"" \
        </dev/null >"$TMP_LOG" 2>&1 || fail_dropped "drop/create failed"
    rdb "pg_restore -U \"\$POSTGRES_USER\" -d $DB_NAME -O -x --exit-on-error $LOPT /tmp/d.dump" \
        </dev/null >"$TMP_LOG" 2>&1 || fail_dropped "pg_restore failed"
else
    LOPT=""
    if [ "$NEED_FILTER" = 1 ]; then
        TMP_TOC="$(mktemp -t cwa_db_toc)"
        pg_restore -l "$DUMP" | grep -vE "$TOC_FILTER" > "$TMP_TOC" || abort_intact "could not build the restore list"
        LOPT="-L $TMP_TOC"
    fi

    say "== drop, create, restore"
    if [ "$HAVE_DB" = 1 ]; then
        dropdb -w -U "$LOCAL_PGUSER" -h "$LOCAL_PGHOST" "$DB_NAME" >"$TMP_LOG" 2>&1 || fail_dropped "dropdb failed"
    fi
    createdb -w -U "$LOCAL_PGUSER" -h "$LOCAL_PGHOST" "$DB_NAME" >"$TMP_LOG" 2>&1 || fail_dropped "createdb failed"
    # $LOPT is deliberately unquoted: empty, or "-L <file>".
    pg_restore -w -U "$LOCAL_PGUSER" -h "$LOCAL_PGHOST" -d "$DB_NAME" -O -x --exit-on-error $LOPT "$DUMP" \
        >"$TMP_LOG" 2>&1 || fail_dropped "pg_restore failed"
fi
say "   restored"

# -------------------------------------------------------------------- migrate
REV_BEFORE="$(db_alembic_rev)"
REV_AFTER="$REV_BEFORE"
MIG="skipped (-nomigrate)"
if [ "$MIGRATE" = 1 ]; then
    say "== alembic upgrade head"
    RC=0
    if [ "$T_MODE" = "local" ]; then
        (cd "$BACKEND_DIR" && "$ALEMBIC" upgrade head) >"$TMP_LOG" 2>&1 || RC=$?
    else
        rsh_n "cd $REMOTE_OPS && docker compose run --rm --no-deps app alembic upgrade head" >"$TMP_LOG" 2>&1 || RC=$?
    fi
    REV_AFTER="$(db_alembic_rev)"
    if [ "$RC" -ne 0 ]; then
        MIG="FAILED at $REV_AFTER"
        warn "alembic upgrade failed; schema left at $REV_AFTER. A dump newer than the deployed code gives \"Can't locate revision\"."
        tail -5 "$TMP_LOG"
    elif [ "$REV_BEFORE" != "$REV_AFTER" ]; then
        MIG="MIGRATED $REV_BEFORE -> $REV_AFTER"
        say "   MIGRATED $REV_BEFORE -> $REV_AFTER"
    else
        MIG="none needed"
        say "   schema already at head ($REV_AFTER), no migration"
    fi
fi

# -------------------------------------------------------------------- restart
if [ "$T_MODE" = "ssh" ]; then
    say "== restarting the cognosa service"
    rsh_n "rm -f $RFILE; cd $REMOTE_OPS && docker compose exec -T db rm -f /tmp/d.dump /tmp/toc.txt" >/dev/null 2>&1 || true
    rsh_n "sudo -n systemctl restart cognosa" >"$TMP_LOG" 2>&1 \
        || warn "$T_TAG: 'systemctl restart cognosa' failed; the database is restored but the stack needs attention"
    if rsh_n 'for i in $(seq 1 60); do curl -fsSk -o /dev/null https://localhost/ && exit 0; sleep 3; done; exit 1'; then
        say "   https://$T_HOST/ answers"
    else
        warn "$T_TAG: the app did not answer on https://localhost/ within 3 minutes; check 'docker compose ps' in $REMOTE_OPS"
    fi
fi

# --------------------------------------------------------------------- report
say "== done"
COUNTS="$(printf "select 'api_users', count(*) from api_users union all select 'api_groups', count(*) from api_groups union all select 'group_vdbs', count(*) from group_vdbs" \
    | db_sql "$DB_NAME" 2>/dev/null | tr '|' '=' | tr '\n' ' ' || true)"
say "   rows      ${COUNTS:-unavailable}"
say "   alembic   $REV_AFTER (migration: $MIG)"
[ -n "$SAFETY" ] && say "   previous  $SAFETY"

# Report only: Qdrant collections the restored database refers to but the target lacks.
if q_sh 'curl -fsS -m 10 "$Q/collections" >/dev/null' 2>/dev/null; then
    WANT="$(printf "select distinct gvdbs_collection from group_vdbs where gvdbs_type = 'qdrant' and deleted = 0 order by 1" | db_sql "$DB_NAME" 2>/dev/null | sort || true)"
    HAVE="$(qdrant_collections)"
    MISSING="$(comm -23 <(printf '%s\n' "$WANT") <(printf '%s\n' "$HAVE") | tr '\n' ' ')"
    if [ -n "${MISSING// /}" ]; then
        warn "Qdrant on $T_TAG lacks collections this database refers to: $MISSING"
    else
        say "   qdrant    every collection the database refers to exists on $T_TAG"
    fi
else
    warn "Qdrant on $T_TAG is not reachable; collection check skipped"
fi
if [ "$T_MODE" = "local" ]; then
    say "   next      restart the web app and run_tasks"
fi
log_line "restore target=$T_TAG dump=$(basename "$DUMP") safety=$(basename "${SAFETY:-none}") alembic=$REV_AFTER migration=\"$MIG\""
