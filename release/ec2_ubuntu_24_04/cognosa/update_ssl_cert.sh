#!/usr/bin/env bash
# Renew the Let's Encrypt certificate with ZERO downtime.
#
# The running nginx already serves /.well-known/acme-challenge/ on :80 from the
# shared `nginx_vhost` volume, so certbot can complete the http-01 challenge
# without stopping the stack. `renew` reuses the webroot config saved at first
# issuance (/etc/letsencrypt/renewal/<domain>.conf) and only acts when fewer
# than 30 days remain; add --force-renewal to override.
#
# Run manually:   cd /home/ubuntu/cognosa && sudo ./update_ssl_cert.sh
# Automated:      root crontab on each host runs the same two commands
#                 Mon/Thu 03:17 UTC (see !README.MD).
#
# INITIAL issuance (no cert yet, nginx cannot start its :443 block) is a
# different procedure: see initial_ssl_cert.sh.
set -euo pipefail
cd "$(dirname "$0")"

docker compose run --rm certbot renew --no-random-sleep-on-renew "$@"
docker compose exec -T nginx nginx -s reload

echo "Certificate now served:"
docker compose run --rm certbot certificates 2>/dev/null | grep -E 'Domains|Expiry'
