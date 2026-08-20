### Deployment procedures:

Needs EC2 Ubuntu 24.04 instance with at least 4 CPU, 8GB RAM, 32GB storage.

1. Fill `backend` and `qdrant` folders.
2. Copy this folder to EC2 instance `/home/ubuntu` folder,
   so there will be `/home/ubuntu/cognosa/backend` and others.

3. Run commands (better one-by-one) from install.sh

### Notes:

To access to PostgreSQL:
Allow connections in EC2 console: instance TCP port 5432 <-> your address.
You can see PostgreSQL user/password in docker-compose.yml.

### Folders:

#### Fill before installation:

backend - must be copy of Cognosa/backend folder.
qdrantdb - Qdrant DB folder. There will be `aliases` and `collections` folders.

#### Will be created during installation:

pg_db_data - PostgreSQL DB folder (used by FastAPI webapp)
app_logs - FastAPI webapp logs (not filled for now)
rt_logs - run_tasks.py logs

Other folders are for installation procedures.

### Files:

docker-compose_full.yml - full Docker Compose template with Nginx + Let's Encrypt.
docker-compose_no_nginx.yml - for local installation, without Nginx + Let's Encrypt. URL: https://127.0.0.1:8000

docker-compose.yml - Use either docker-compose_full.yml or docker-compose_full.yml

install.sh - commands for full installation
install_no_nginx.sh - commands for local installation, without Nginx + Let's Encrypt.

Other files are for installation procedures.

### Let's Encrypt SSL certificate

Certs last 90 days. Let's Encrypt no longer sends expiry emails (since June 2025),
so renewal is automated: each host has a root crontab entry (Mon/Thu 03:17 UTC)
that runs `certbot renew` and reloads nginx, logging to `certbot_cron.log`.
`renew` is a no-op until fewer than 30 days remain.

```
sudo crontab -l
# 17 3 * * 1,4  cd /home/ubuntu/cognosa && docker compose run --rm certbot renew --quiet && docker compose exec -T nginx nginx -s reload >> /home/ubuntu/cognosa/certbot_cron.log 2>&1
```

Manual renewal (zero downtime, nothing is stopped):

```
cd /home/ubuntu/cognosa
sudo ./update_ssl_cert.sh            # add --force-renewal to renew early
```

First-time issuance on a new host (nginx cannot start without a cert):
edit DOMAIN/EMAIL in `initial_ssl_cert.sh`, then `sudo ./initial_ssl_cert.sh`.

Check expiry from anywhere:

```
echo | openssl s_client -servername dev.cognosa.net -connect dev.cognosa.net:443 2>/dev/null | openssl x509 -noout -dates
```

### To reclaim more space on EC2 instance:

```
sudo docker system prune -a --volumes --force
```
