# /home/ubuntu/cognosa/run_tasks.Dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY req_run_tasks.txt ./
RUN pip install --no-cache-dir -r req_run_tasks.txt

COPY backend/ ./

CMD ["python", "run_tasks.py"]

