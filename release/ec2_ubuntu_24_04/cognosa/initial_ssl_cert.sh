#!/usr/bin/env bash
# FIRST-TIME certificate issuance only. For routine renewal use update_ssl_cert.sh.
#
# nginx cannot start with nginx_default.conf until the cert exists (the :443
# block references it), so temporarily run nginx with the :80-only dummy conf,
# obtain the cert, then switch to the full conf.
#
# Before running: replace DOMAIN and EMAIL below (and in nginx_default*.conf).
set -euo pipefail
cd "$(dirname "$0")"
DOMAIN=dev.cognosa.net
EMAIL=harry@cognosa.net

docker compose down
cp nginx_default_dummy.conf ./nginx/conf.d/default.conf
docker compose up -d nginx

docker compose run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  -d "$DOMAIN" \
  --email "$EMAIL" \
  --agree-tos --no-eff-email

docker compose down
cp nginx_default.conf ./nginx/conf.d/default.conf
docker compose up -d --build
