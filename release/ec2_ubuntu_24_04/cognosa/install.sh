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
# nginx + let's encrypt preinstall
###
# dummy configuration - just to get certificate
cp nginx_default_dummy.conf ./nginx/conf.d/
sudo docker compose up -d nginx

sudo docker compose run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  -d dev.cognosa.net \
  --email yury.matveev.1983@gmail.com \
  --agree-tos --no-eff-email --force-renewal

sudo docker compose down
# prod configuration
cp nginx_default.conf ./nginx/conf.d/
###

sudo docker compose up -d --build
sudo docker compose run --rm app python init_sql_db.py

sudo cp cognosa.service /etc/systemd/system/
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable cognosa.service
sudo systemctl start cognosa.service

sudo systemctl status cognosa
sudo docker compose ps


sudo reboot
