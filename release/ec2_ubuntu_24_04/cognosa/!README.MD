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

### To update Let's Encrypt SSL certificate:

Either run whole `update_ssl_cert.sh` script, or line-by-line.

```
cd /home/ubuntu/cognosa
./update_ssl_cert.sh
```

### To reclaim more space on EC2 instance:

```
sudo docker system prune -a --volumes --force
```
