#!/usr/bin/env bash
# Dump a target's cwa_db into ~/0_hold_cwa_db on this machine.
#
#   cwa_db_backup.sh <target> [-label <text>] [-qdrant]
#
#   target   m1 | dev | demo          (m2, m3, m4: not implemented yet)
#   -label   free text appended to the dump filename, e.g. v0.47_orange
#   -qdrant  also snapshot every Qdrant collection on the target (default: off)
#
# Output, all in ~/0_hold_cwa_db:
#   cwa_db_<target>_<YYMMDD_HHMMSS>[_<label>].dump       pg_dump custom format
#   with -qdrant, sharing the dump's timestamp:
#   qdrant_<target>_<YYMMDD_HHMMSS>_<collection>.snapshot.gz   one per collection
#   qdrant_<target>_<YYMMDD_HHMMSS>.manifest             collection|points|sha256|file
#
# The database server (and Qdrant, with -qdrant) must be up; the app may be
# running and in use. Nothing on the target is changed.
# Plan: docs/DB_BACKUP_RESTORE_PLAN.md
set -euo pipefail

. "$(cd "$(dirname "$0")" && pwd)/cwa_db_common.sh"

usage() { sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'; }

TARGET=""
LABEL=""
QDRANT=0
while [ $# -gt 0 ]; do
    case "$1" in
        -label)    [ $# -ge 2 ] || die "-label needs a value"; LABEL="$2"; shift 2 ;;
        -qdrant)   QDRANT=1; shift ;;
        -h|-help|--help) usage; exit 0 ;;
        -*)        die "unknown option '$1' (try -h)" ;;
        *)         [ -z "$TARGET" ] || die "only one target allowed (got '$TARGET' and '$1')"; TARGET="$1"; shift ;;
    esac
done
[ -n "$TARGET" ] || { usage; exit 1; }

target_resolve "$TARGET"

# Preflight: fail before anything is written.
preflight_hold_dir
preflight_local_tools
preflight_server
preflight_db
if [ "$QDRANT" = 1 ]; then preflight_qdrant; fi

STAMP="$(date +%y%m%d_%H%M%S)"
NAME="cwa_db_${T_TAG}_${STAMP}"
if [ -n "$LABEL" ]; then
    NAME="${NAME}_$(printf '%s' "$LABEL" | tr -c 'A-Za-z0-9._-' '_')"
fi
OUT="$HOLD_DIR/$NAME.dump"

say "== backing up $DB_NAME on $T_TAG ($T_HOST, $T_MODE)"
REV="$(db_alembic_rev)"
dump_target "$OUT"

SIZE="$(file_size_h "$OUT")"
say "   file     $OUT"
say "   size     $SIZE"
say "   entries  $(dump_toc_count "$OUT") (TOC)"
say "   server   PostgreSQL $(dump_from_version "$OUT")"
say "   alembic  $REV"
log_line "backup  target=$T_TAG file=$NAME.dump size=$SIZE alembic=$REV"

if [ "$QDRANT" = 1 ]; then
    PREFIX="qdrant_${T_TAG}_${STAMP}"
    MANIFEST="$HOLD_DIR/$PREFIX.manifest"
    # The manifest is written last; a set without one is incomplete and the
    # restore script will not accept it.
    trap 'if [ -e "$MANIFEST.partial" ]; then rm -f "$MANIFEST.partial"; warn "Qdrant set $PREFIX is incomplete: no manifest written (the Postgres dump above is complete)"; fi' EXIT
    say "== backing up Qdrant collections on $T_TAG"
    COLLS="$(qdrant_collections)"
    : > "$MANIFEST.partial"
    N=0
    for c in $COLLS; do
        PTS="$(qdrant_points "$c")"
        F="${PREFIX}_$c.snapshot.gz"
        qdrant_backup_collection "$c" "$HOLD_DIR/$F"
        printf '%s|%s|%s|%s\n' "$c" "${PTS:-?}" "$QB_SHA" "$F" >> "$MANIFEST.partial"
        say "   $c  points=${PTS:-?}  $(file_size_h "$HOLD_DIR/$F")"
        N=$((N + 1))
    done
    mv "$MANIFEST.partial" "$MANIFEST"
    say "   manifest $MANIFEST ($N collections)"
    log_line "backup  target=$T_TAG qdrant=$PREFIX collections=$N"
fi
say "== done"
