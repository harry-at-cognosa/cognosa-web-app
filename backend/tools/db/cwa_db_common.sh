# Shared by cwa_db_backup.sh and cwa_db_restore.sh (sourced, not run).
# Plan: docs/DB_BACKUP_RESTORE_PLAN.md.  Written for macOS /bin/bash 3.2.

HOLD_DIR="${CWA_HOLD_DIR:-$HOME/0_hold_cwa_db}"
LOG_FILE="$HOLD_DIR/backup_restore.log"
DB_NAME="cwa_db"

# Local (Mac) Postgres
LOCAL_PGUSER="postgres"
LOCAL_PGHOST="localhost"
PGAPP_BIN="/Applications/Postgres.app/Contents/Versions/latest/bin"

# EC2 hosts: Postgres runs in the compose service `db`; the superuser is the
# container's own $POSTGRES_USER (env_db.env), never passed from here.
SSH_KEY="${CWA_SSH_KEY:-$HOME/ctc01instance.pem}"
REMOTE_OPS="/home/ubuntu/cognosa"

# Qdrant HTTP API. On EC2 it is only reachable from the host itself, so calls
# run there over SSH. Snapshots are written on the Qdrant host before download.
QDRANT_LOCAL_URL="${CWA_QDRANT_URL:-http://127.0.0.1:6333}"
QDRANT_REMOTE_URL="http://localhost:6333"
QDRANT_MIN_FREE_KB=2097152      # refuse to snapshot on an EC2 host with < 2 GB free

# tag|kind|address|ssh_user
TARGETS="m1|mac|10.0.100.211|harry
m2|mac|10.0.100.212|harryAtMac
m3|mac|10.0.100.210|harryAtMac
m4|mac|10.0.100.215|harry
dev|ec2|dev.cognosa.net|ubuntu
demo|ec2|demo.cognosa.net|ubuntu"

say()  { printf '%s\n' "$*"; }
warn() { printf 'WARNING: %s\n' "$*" >&2; }
die()  { printf 'ABORTED: %s\n' "$*" >&2; exit 1; }

log_line() {
    printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$LOG_FILE"
}

target_tags() { printf '%s\n' "$TARGETS" | cut -d'|' -f1 | tr '\n' ' '; }

# Sets T_TAG, T_KIND (mac|ec2), T_HOST, T_USER, T_MODE (local|ssh)
target_resolve() {
    local line
    line="$(printf '%s\n' "$TARGETS" | grep "^$1|" || true)"
    [ -n "$line" ] || die "unknown target '$1' (known: $(target_tags))"
    T_TAG="$1"
    T_KIND="$(printf '%s' "$line" | cut -d'|' -f2)"
    T_HOST="$(printf '%s' "$line" | cut -d'|' -f3)"
    T_USER="$(printf '%s' "$line" | cut -d'|' -f4)"
    if [ "$T_KIND" = "mac" ]; then
        # A Mac target is handled locally when this machine owns its address.
        if ifconfig 2>/dev/null | grep -q "inet $T_HOST "; then
            T_MODE="local"
        else
            die "target '$T_TAG' ($T_HOST) is not this machine; remote Macs are not implemented yet (plan section 8)"
        fi
    else
        T_MODE="ssh"
    fi
}

# rsh passes stdin through to the remote command; rsh_n gives it none.
rsh() {
    ssh -i "$SSH_KEY" -o BatchMode=yes -o IdentitiesOnly=yes -o ConnectTimeout=10 \
        -o ServerAliveInterval=30 "$T_USER@$T_HOST" "$@"
}
rsh_n() { rsh "$@" </dev/null; }

# Run a command inside the remote `db` container. $1 is a sh -c script; keep
# it free of single quotes. $POSTGRES_USER is expanded inside the container.
rdb() { rsh "cd $REMOTE_OPS && docker compose exec -T db sh -c '$1'"; }

# db_sql <database> : run the SQL on stdin against the target, unaligned tuples only.
db_sql() {
    if [ "$T_MODE" = "local" ]; then
        psql -X -w -At -v ON_ERROR_STOP=1 -U "$LOCAL_PGUSER" -h "$LOCAL_PGHOST" -d "$1"
    else
        rdb "psql -X -w -At -v ON_ERROR_STOP=1 -U \"\$POSTGRES_USER\" -d $1"
    fi
}

preflight_hold_dir() {
    [ -d "$HOLD_DIR" ] || die "hold folder $HOLD_DIR does not exist on this machine"
    [ -w "$HOLD_DIR" ] || die "hold folder $HOLD_DIR is not writable"
}

# Local client tools (also needed for remote targets: pg_restore -l verifies dumps).
preflight_local_tools() {
    if ! command -v pg_restore >/dev/null 2>&1 && [ -d "$PGAPP_BIN" ]; then
        PATH="$PGAPP_BIN:$PATH"
    fi
    local t
    for t in pg_dump pg_restore psql; do
        command -v "$t" >/dev/null 2>&1 || die "$t not found on PATH (expected Postgres.app at $PGAPP_BIN)"
    done
}

# The server (SSH + db container for ec2) and its Postgres must answer.
preflight_server() {
    if [ "$T_MODE" = "ssh" ]; then
        [ -r "$SSH_KEY" ] || die "SSH key $SSH_KEY not found or not readable"
        rsh_n true 2>/dev/null \
            || die "cannot SSH to $T_USER@$T_HOST (instance stopped, port 22 closed to this address, or host key changed)"
        [ -n "$(rsh_n "cd $REMOTE_OPS && docker compose ps --status running -q db" 2>/dev/null)" ] \
            || die "$T_TAG: compose service 'db' is not running in $REMOTE_OPS"
    fi
    [ "$(printf 'select 1' | db_sql postgres 2>/dev/null)" = "1" ] \
        || die "$T_TAG: cannot connect to the Postgres server"
}

db_exists() {
    [ "$(printf "select 1 from pg_database where datname='%s'" "$DB_NAME" | db_sql postgres 2>/dev/null)" = "1" ]
}

preflight_db() {
    db_exists || die "$T_TAG: database $DB_NAME does not exist"
    [ "$(printf 'select 1' | db_sql "$DB_NAME" 2>/dev/null)" = "1" ] \
        || die "$T_TAG: cannot connect to database $DB_NAME"
}

# Prints the alembic revision of the target's cwa_db, or "none".
db_alembic_rev() {
    local rev
    rev="$(printf 'select version_num from alembic_version' | db_sql "$DB_NAME" 2>/dev/null | head -1)"
    printf '%s' "${rev:-none}"
}

# dump_target <outfile> : custom-format dump of the target's cwa_db into a
# local file. Written as <outfile>.partial and renamed only once the archive
# has been read back successfully.
dump_target() {
    local out="$1" partial="$1.partial" rc=0
    [ -e "$out" ] && die "$out already exists"
    if [ "$T_MODE" = "local" ]; then
        pg_dump -w -U "$LOCAL_PGUSER" -h "$LOCAL_PGHOST" -Fc -f "$partial" "$DB_NAME" || rc=$?
    else
        rdb "pg_dump -Fc -U \"\$POSTGRES_USER\" $DB_NAME" </dev/null > "$partial" || rc=$?
    fi
    if [ "$rc" -ne 0 ]; then
        rm -f "$partial"
        die "$T_TAG: pg_dump failed (exit $rc); no dump file kept"
    fi
    if [ ! -s "$partial" ] || ! pg_restore -l "$partial" >/dev/null 2>&1; then
        rm -f "$partial"
        die "$T_TAG: dump is empty or not a readable archive; no dump file kept"
    fi
    mv "$partial" "$out"
}

# One-line facts about a dump file.
dump_toc_count()    { pg_restore -l "$1" | grep -cv '^;' || true; }
dump_from_version() { pg_restore -l "$1" | sed -n 's/^; *Dumped from database version: *//p' | head -1; }
file_size_h() {
    wc -c < "$1" | awk '{ if ($1 >= 1048576) printf "%.1fM", $1/1048576;
                          else if ($1 >= 1024) printf "%.0fK", $1/1024;
                          else printf "%dB", $1 }'
}

# ---------------------------------------------------------------- Qdrant

# q_sh <bash snippet> : run the snippet where the target's Qdrant is
# reachable; inside it, $Q is the base URL. No stdin.
q_sh() {
    if [ "$T_MODE" = "local" ]; then
        Q="$QDRANT_LOCAL_URL" bash -c "set -o pipefail; $1" </dev/null
    else
        rsh_n "Q=$QDRANT_REMOTE_URL; set -o pipefail; $1"
    fi
}

q_url() { if [ "$T_MODE" = "local" ]; then printf '%s' "$QDRANT_LOCAL_URL"; else printf '%s on %s' "$QDRANT_REMOTE_URL" "$T_HOST"; fi; }

# json_str <field> : value of the first "field":"value" pair in the JSON on stdin.
json_str() { sed -n "s/.*\"$1\":\"\([^\"]*\)\".*/\1/p" | head -1; }

preflight_qdrant() {
    q_sh 'curl -fsS -m 10 "$Q/collections" >/dev/null' 2>/dev/null \
        || die "$T_TAG: cannot reach Qdrant at $(q_url) (is it running?)"
    command -v shasum >/dev/null 2>&1 || die "shasum not found on PATH"
    if [ "$T_MODE" = "ssh" ]; then
        local free
        free="$(rsh_n "df -Pk / | awk 'NR==2 {print \$4}'" 2>/dev/null)"
        [ "${free:-0}" -ge "$QDRANT_MIN_FREE_KB" ] \
            || die "$T_TAG: only ${free:-?} KB free on /; snapshots need working space on the server"
    fi
}

# Collection names on the target, one per line, sorted.
qdrant_collections() {
    local resp
    resp="$(q_sh 'curl -fsS -m 30 "$Q/collections"')" || die "$T_TAG: cannot list Qdrant collections"
    printf '%s' "$resp" | grep -o '"name":"[^"]*"' | cut -d'"' -f4 | sort || true
}

qdrant_points() {
    q_sh "curl -fsS -m 30 \"\$Q/collections/$1\"" 2>/dev/null \
        | sed -n 's/.*"points_count":\([0-9]*\).*/\1/p' | head -1 || true
}

# qdrant_backup_collection <collection> <outfile.gz>
# Snapshot on the server, stream it back gzipped, delete the server-side
# snapshot, then verify the SHA-256 Qdrant reported. Sets QB_SHA.
qdrant_backup_collection() {
    local c="$1" out="$2" partial="$2.partial" resp snap got rc=0
    case "$c" in *[!A-Za-z0-9._-]*) die "collection name '$c' has characters this script does not handle" ;; esac
    [ -e "$out" ] && die "$out already exists"
    resp="$(q_sh "curl -fsS -m 900 -X POST \"\$Q/collections/$c/snapshots\"")" \
        || die "$T_TAG: creating a snapshot of collection $c failed"
    snap="$(printf '%s' "$resp" | json_str name)"
    QB_SHA="$(printf '%s' "$resp" | json_str checksum)"
    case "$snap" in ""|*[!A-Za-z0-9._-]*) die "$T_TAG: unexpected snapshot name for $c: '$snap'" ;; esac
    q_sh "curl -fsS \"\$Q/collections/$c/snapshots/$snap\" | gzip -1" > "$partial" || rc=$?
    q_sh "curl -fsS -m 120 -X DELETE \"\$Q/collections/$c/snapshots/$snap\" >/dev/null" \
        || warn "$T_TAG: could not delete server-side snapshot $snap of $c"
    if [ "$rc" -ne 0 ] || ! gzip -t "$partial" 2>/dev/null; then
        rm -f "$partial"
        die "$T_TAG: download of the $c snapshot failed; no file kept"
    fi
    if [ -n "$QB_SHA" ]; then
        got="$(gunzip -c "$partial" | shasum -a 256 | cut -d' ' -f1)"
        if [ "$got" != "$QB_SHA" ]; then
            rm -f "$partial"
            die "$T_TAG: checksum mismatch on the $c snapshot; no file kept"
        fi
    else
        warn "$T_TAG: Qdrant gave no checksum for $c; snapshot not verified"
    fi
    mv "$partial" "$out"
}
