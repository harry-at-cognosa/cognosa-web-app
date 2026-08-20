# Update system
sudo apt update && sudo apt upgrade -y

# Install prerequisites
sudo apt install -y ca-certificates curl gnupg lsb-release

# Add Docker’s official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repo
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine and Compose plugin
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify
docker --version
docker compose version

sudo mkdir -p /home/ubuntu/cognosa
sudo chown $USER:$USER /home/ubuntu/cognosa
cd /home/ubuntu/cognosa

###
# application source = git clone (docker build context); see !README.MD "First-time setup"
###
git clone https://github.com/harry-at-cognosa/cognosa-web-app.git /home/ubuntu/cognosa-src
REL=/home/ubuntu/cognosa-src/release/ec2_ubuntu_24_04/cognosa
cp $REL/docker-compose.yml .
ln -sf ../cognosa-src/release/ec2_ubuntu_24_04/cognosa/deploy.sh deploy.sh
cp $REL/nginx_default.conf $REL/nginx_default_dummy.conf $REL/initial_ssl_cert.sh $REL/update_ssl_cert.sh $REL/cognosa.service .
mkdir -p nginx/conf.d nginx/log
# create .env, env_app.env, env_run_tasks.env, env_db.env from $REL/*-default, then continue

###
# nginx + let's encrypt preinstall
###
# dummy configuration - just to get certificate
cp nginx_default_dummy.conf ./nginx/conf.d/default.conf
sudo docker compose up -d nginx

sudo docker compose run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  -d dev.cognosa.net \
  --email yury.matveev.1983@gmail.com \
  --agree-tos --no-eff-email --force-renewal

sudo docker compose down
# prod configuration
cp nginx_default.conf ./nginx/conf.d/default.conf
###

chmod +x update_ssl_cert.sh initial_ssl_cert.sh

sudo docker compose up -d --build
# fresh DB only; to restore a dump instead see !README.MD "Refresh data"
sudo docker compose run --rm app python init_sql_db.py

sudo cp cognosa.service /etc/systemd/system/
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable cognosa.service
sudo systemctl start cognosa.service

sudo systemctl status cognosa
sudo docker compose ps


sudo reboot
