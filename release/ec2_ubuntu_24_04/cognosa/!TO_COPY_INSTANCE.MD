### Clean copying of AWS EC2 Cognosa-Dev Instance

Steps to launch copy of dev.cognosa.net on demo.cognosa.net.
1) On AWS EC2 panel:
Elastic IPs: create/release new elastic ip (for new EC2 instance).
E.g. it will be: 52.13.212.94

2) Route66 (or whatever):
Assign domain demo.cognosa.net as 52.13.212.94


On AWS EC2 panel:
3) Instances:
Select `cognosa-dev` instance -> Actions -> Image and templates -> Launch more like this:
Change instance name to e.g. `cognosa-demo` and create/start new instance.
Check it's `Private IPv4 addresses`. Will be like: 172.31.53.142

4) Elastic IPs:
associate elastic ip (52.13.212.94) to `cognosa-demo` instance.

5) Security groups:
Find `cognosa-llm-sec-group` (this is LLM server sec group).
Add it's inbound rules:
5.1) Allow all traffic IPv4 from 52.13.212.94/32  (cognosa-demo public ip address)
5.1) Allow all traffic IPv4 from 172.31.53.142/32  (cognosa-demo private ip address)

--- end of AWS EC2 panel tasks ---

6) Connect SSH (Putty or whatever) to previous instance (dev.cognosa.net)
to backup Qdrant and PostgreSQL databases:
```
cd /home/ubuntu/cognosa
sudo docker compose down
tar -zcvf qdrantdb_2026-01-09.tgz qdrantdb
tar -zcvf pg_db_data_2026-01-09.tgz pg_db_data
```

7) Copy `qdrantdb_2026-01-09.tgz` and `pg_db_data_2026-01-09.tgz` to your local machine.

--- end of tasks on previous instance ---

8) Prepare release folder to copy it to the new `demo.cognosa.net` EC2 instance.
There will be:
```
backend/*
nginx/*

!README.MD
cognosa.service
docker-compose.yml
env_app.env
env_db.env
env_run_tasks.env
install.sh
nginx_default.conf
nginx_default_dummy.conf
pg_db_data_2026-01-09.tgz  -  latest backup of PostgreSQL db data
qdrantdb_2026-01-09.tgz - latest backup of Qdrant db data
req_run_tasks.txt
req_webapp.txt
run_tasks.Dockerfile
update_ssl_cert.sh
initial_ssl_cert.sh
webapp.Dockerfile
```

9) Find and change all occurrences of `dev.cognosa.net` to `demo.cognosa.net` (without quotes) in files:
```
docker-compose.yml
install.sh
nginx_default.conf - note that it has several occurrences to change
nginx_default_dummy.conf
initial_ssl_cert.sh
```

10) Copy release folder to the new EC2 instance, so there will be:
/home/ubuntu/cognosa/backend/* and so on.

--- end of local machine tasks ---

11) Connect SSH to the new AWS EC2 instance (demo.cognosa.net).
Run all commands from /release/install.sh file.
It's better to run them one-by-one.
Then install the certbot renewal cron (see !README.MD, "Let's Encrypt SSL certificate").

12) After last command and instance reboot, unpack database backups:
```
cd cognosa
sudo docker compose down
sudo rm -rf qdrant
tar -xzf qdrantdb_2026-01-09.tgz -C .
sudo rm -rf pg_db_data
tar -xzf pg_db_data_2026-01-09.tgz -C .
sudo chown -R 999:999 pg_db_data
sudo chmod -R 700 pg_db_data
```
