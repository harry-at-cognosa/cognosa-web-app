#!/usr/bin/env bash
# Deploy a git ref of the Cognosa repo to this EC2 host.
#
#   cd /home/ubuntu/cognosa && ./deploy.sh [git-ref]     (default: origin/main)
#
# Run as the clone's owner (ubuntu, member of the docker group). Under sudo,
# git commands are delegated back to $SUDO_USER so the clone stays user-owned.
#
# Steps: fetch + checkout the ref in /home/ubuntu/cognosa-src, refresh
# docker-compose.yml from the clone, build app + rt images, stop them, run
# alembic migrations, start everything, prune dangling images.
# Data (pg_db_data, qdrantdb, env files, nginx conf, certs) is never touched.
#
# /home/ubuntu/cognosa/deploy.sh is a symlink into the clone, so this script
# updates itself on checkout (bash keeps the old inode for the running copy).
set -euo pipefail

OPS="$(cd "$(dirname "$0")" && pwd)"            # /home/ubuntu/cognosa
SRC="${COGNOSA_SRC:-$OPS/../cognosa-src}"
REF="${1:-origin/main}"
REL="release/ec2_ubuntu_24_04/cognosa"

g() { if [ "$(id -u)" = 0 ] && [ -n "${SUDO_USER:-}" ]; then sudo -u "$SUDO_USER" git "$@"; else git "$@"; fi; }

[ -d "$SRC/.git" ] || { echo "no git clone at $SRC (see !README.MD, first-time setup)"; exit 1; }
[ -f "$OPS/.env" ] && grep -q '^COGNOSA_DOMAIN=' "$OPS/.env" || { echo "missing COGNOSA_DOMAIN in $OPS/.env"; exit 1; }

echo "== fetching $REF"
g -C "$SRC" fetch --quiet --tags origin
g -C "$SRC" checkout --quiet --detach "$REF"
echo "== at: $(g -C "$SRC" log -1 --format='%h %ad %s' --date=short)"

cp "$SRC/$REL/docker-compose.yml" "$OPS/docker-compose.yml"
cd "$OPS"

echo "== building images"
docker compose build app rt

echo "== stopping app + rt, migrating"
docker compose stop app rt
docker compose up -d db qdrant
docker compose run --rm --no-deps app alembic upgrade head

echo "== starting"
docker compose up -d
# nginx resolves `app` once at config load; recreated app container = new IP
docker compose exec -T nginx nginx -s reload
docker image prune -f >/dev/null

docker compose ps
echo "== deployed $(g -C "$SRC" rev-parse --short HEAD) at $(date -u +%FT%TZ)" | tee -a "$OPS/deploy.log"
