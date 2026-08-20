### Layout on the EC2 host (git-pull deploy, since 2026-08-20)

```
/home/ubuntu/cognosa/        ops dir (never overwritten by deploys)
    .env                     COGNOSA_DOMAIN=dev.cognosa.net  (compose interpolation)
    env_app.env  env_run_tasks.env  env_db.env
    docker-compose.yml       copied from the clone by deploy.sh
    deploy.sh -> ../cognosa-src/release/ec2_ubuntu_24_04/cognosa/deploy.sh
    nginx/conf.d/default.conf, nginx/log/
    pg_db_data/  qdrantdb/  app_logs/  rt_logs/
/home/ubuntu/cognosa-src/    git clone of the app repo = docker build context
```

Images are built from the clone (`build.context: ../cognosa-src`); the
developer `backend/.env` in git is excluded (`.dockerignore` + `rm -f .env`),
so all runtime config comes from the env files above. Hugging Face models are
cached in the `hf_cache` volume and survive rebuilds.

### Update to a new release

```
cd /home/ubuntu/cognosa
sudo ./deploy.sh              # origin/main
sudo ./deploy.sh v0.46        # or any tag / sha / branch
```

deploy.sh: fetch + detached checkout, refresh docker-compose.yml, build app+rt,
stop app+rt, `alembic upgrade head`, `up -d`, prune old images, append to
`deploy.log`. Brief downtime of app/rt only; db/qdrant/nginx keep running.

### First-time setup of a host

Needs EC2 Ubuntu 24.04, >= 4 CPU, 8 GB RAM, 32 GB disk, DNS A record for the domain.

1. Run the Docker install part of `install.sh` (up to and including `cd /home/ubuntu/cognosa`).
2. `git clone https://github.com/harry-at-cognosa/cognosa-web-app.git /home/ubuntu/cognosa-src`
   (private repo: register a per-host read-only deploy key and clone over SSH).
3. `cd /home/ubuntu/cognosa` and create from the `*-default` templates in the
   clone's `release/ec2_ubuntu_24_04/cognosa/`: `.env`, `env_app.env`,
   `env_run_tasks.env`, `env_db.env`. Copy `nginx_default.conf`,
   `nginx_default_dummy.conf`, `initial_ssl_cert.sh`, `cognosa.service`; edit the
   domain in the nginx confs and `initial_ssl_cert.sh`.
4. `ln -s ../cognosa-src/release/ec2_ubuntu_24_04/cognosa/deploy.sh deploy.sh`
   and `cp ../cognosa-src/release/ec2_ubuntu_24_04/cognosa/docker-compose.yml .`
5. `mkdir -p nginx/conf.d nginx/log` then `sudo ./initial_ssl_cert.sh` (obtains the cert and brings the stack up).
6. Either `sudo docker compose run --rm app python init_sql_db.py` (fresh DB) or
   restore a dump (next section). Load Qdrant collections (next section).
7. systemd + renewal cron: last block of `install.sh`, and the cron line under
   "Let's Encrypt SSL certificate".

### Refresh data from another environment

PostgreSQL (wholesale replace; `cwa_user` is the container superuser):

```
# source:  pg_dump -Fc -O -x -d cwa_db -f cwa_db_<date>.dump ; scp it to ~/cognosa/
cd /home/ubuntu/cognosa
sudo docker compose stop app rt
sudo docker compose exec -T db sh -c 'pg_dump -Fc -U "$POSTGRES_USER" "$POSTGRES_DB"' > pg_backup_$(date +%y%m%d).dump
sudo docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d postgres -c "DROP DATABASE cwa_db" -c "CREATE DATABASE cwa_db"'
sudo docker compose exec -T db sh -c 'pg_restore -U "$POSTGRES_USER" -d cwa_db -O -x' < cwa_db_<date>.dump
sudo docker compose up -d
```

Qdrant collections (per collection, version-tolerant):

```
# source:  curl -X POST localhost:6333/collections/<c>/snapshots  -> download from
#          localhost:6333/collections/<c>/snapshots/<file> ; scp to ~/cognosa/
curl -X PUT "localhost:6333/collections/<c>/snapshots/upload?priority=snapshot" \
     -F "snapshot=@<file>.snapshot"
```

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

install.sh - commands for full installation (Docker + first bring-up)
deploy.sh - update a running host to a git ref (see above)
.env-default - COGNOSA_DOMAIN template for compose
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
