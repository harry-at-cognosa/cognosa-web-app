sudo docker compose down

cp nginx_default_dummy.conf ./nginx/conf.d/default.conf

sudo docker compose up -d nginx

sudo docker compose run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  -d dev.cognosa.net \
  --email yury.matveev.1983@gmail.com \
  --agree-tos --no-eff-email --force-renewal

sudo docker compose down

cp nginx_default.conf ./nginx/conf.d/default.conf

sudo docker compose up -d --build
