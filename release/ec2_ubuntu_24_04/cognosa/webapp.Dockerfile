# Build context: repo root (git clone at /home/ubuntu/cognosa-src).
# Invoked from /home/ubuntu/cognosa/docker-compose.yml.
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY req_webapp.txt ./
RUN pip install --no-cache-dir -r req_webapp.txt

COPY backend/ ./
# Runtime configuration comes from docker-compose env/env_file, never from the
# developer .env tracked in git (also excluded by .dockerignore).
RUN rm -f .env

EXPOSE 8000

CMD ["uvicorn", "webapp:app", "--host", "0.0.0.0", "--port", "8000"]
