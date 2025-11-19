# /home/ubuntu/cognosa/webapp.Dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY req_webapp.txt ./
RUN pip install --no-cache-dir -r req_webapp.txt

COPY backend/ ./

EXPOSE 8000

CMD ["uvicorn", "webapp:app", "--host", "0.0.0.0", "--port", "8000"]
