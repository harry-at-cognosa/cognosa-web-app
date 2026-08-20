# Build context: repo root (git clone at /home/ubuntu/cognosa-src).
# Invoked from /home/ubuntu/cognosa/docker-compose.yml.
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY req_run_tasks.txt ./
RUN pip install --no-cache-dir -r req_run_tasks.txt

COPY backend/ ./
RUN rm -f .env

CMD ["python", "run_tasks.py"]
