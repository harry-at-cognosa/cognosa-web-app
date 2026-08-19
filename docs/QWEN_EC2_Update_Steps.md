# Updating EC2 Cognosa Instance to Support Qwen LLM

## Overview

The EC2 deployment is **copy-based** (not a git repo). Updates are applied by copying changed files to the server, rebuilding Docker images, and running the database migration.

## Prerequisites

- SSH key pair for the EC2 instance
- The EC2 instance IP address (or domain like `dev.cognosa.net`)
- The changed files from this commit (already on your local machine)

## Step-by-Step Procedure

### Step 1: SSH into the EC2 instance

```bash
ssh -i /path/to/your-key.pem ubuntu@<EC2_IP_OR_DOMAIN>
```

### Step 2: Stop the application

```bash
cd /home/ubuntu/cognosa
sudo systemctl stop cognosa.service
docker compose down
```

### Step 3: Copy the changed backend files from your local machine

Open a **new local terminal** (not the SSH session) and run these `scp` commands to copy only the 4 changed backend files:

```bash
KEY="/path/to/your-key.pem"
HOST="ubuntu@<EC2_IP_OR_DOMAIN>"
REMOTE="/home/ubuntu/cognosa/backend"

# 1. Updated enum (adds 'qwen' type)
scp -i $KEY backend/common/enums/gllms_types.py $HOST:$REMOTE/common/enums/gllms_types.py

# 2. Updated dispatcher (routes qwen to OpenAI handler)
scp -i $KEY backend/tasks_lib/llm_lib/llm_ops.py $HOST:$REMOTE/tasks_lib/llm_lib/llm_ops.py

# 3. Updated OpenAI handler (qwen health check)
scp -i $KEY backend/tasks_lib/llm_lib/llm_type_openai.py $HOST:$REMOTE/tasks_lib/llm_lib/llm_type_openai.py

# 4. New Alembic migration
scp -i $KEY backend/alembic/versions/22cb85c671f5_add_qwen_to_gllms_type_enum.py $HOST:$REMOTE/alembic/versions/
```

(The init data JSON and schema SQL files are not needed on the server — they're only used for fresh installs.)

### Step 4: Rebuild Docker images and start services

Back in the **SSH session**:

```bash
cd /home/ubuntu/cognosa
docker compose up -d --build
```

This rebuilds the `app` and `rt` (run_tasks) images, which `COPY backend/` into the container — so they pick up the new files.

### Step 5: Run the Alembic migration

This adds `'qwen'` to the PostgreSQL `gllms_type_enum`:

```bash
docker compose exec app alembic upgrade head
```

If `exec` doesn't work (container not fully up yet), use:

```bash
docker compose run --rm app alembic upgrade head
```

### Step 6: Verify everything is running

```bash
docker compose ps
```

All services (`db`, `qdrant`, `app`, `rt`, `nginx`) should show as "Up".

### Step 7: Re-enable the systemd service

```bash
sudo systemctl start cognosa.service
```

### Step 8: Configure a Qwen LLM via the UI

1. Log in as a superuser
2. Go to **SuperUser > LLMs** (SU Manage LLMs page)
3. Create a new LLM entry:
   - **Type**: `qwen`
   - **Name**: `Qwen Plus` (or whatever you prefer)
   - **API Base**: `https://dashscope-us.aliyuncs.com/compatible-mode/v1`
   - **Model**: `qwen-plus` (or `qwen-turbo`, `qwen-max`)
   - **API Key**: your DashScope API key
4. Wait ~5 seconds for the status worker to verify — it should turn green (Ready)
5. Go to **Query Documents**, select the Qwen LLM, and test a query

## Quick Reference: Files Changed

| File on local machine | Destination on EC2 |
|---|---|
| `backend/common/enums/gllms_types.py` | `/home/ubuntu/cognosa/backend/common/enums/gllms_types.py` |
| `backend/tasks_lib/llm_lib/llm_ops.py` | `/home/ubuntu/cognosa/backend/tasks_lib/llm_lib/llm_ops.py` |
| `backend/tasks_lib/llm_lib/llm_type_openai.py` | `/home/ubuntu/cognosa/backend/tasks_lib/llm_lib/llm_type_openai.py` |
| `backend/alembic/versions/22cb85c671f5_...py` | `/home/ubuntu/cognosa/backend/alembic/versions/` |

## Rollback (if needed)

If something goes wrong, the old files can be recovered from the Docker image cache. Or simply re-copy the original files from your local git repo:

```bash
git show HEAD~1:backend/common/enums/gllms_types.py > /tmp/gllms_types.py
# then scp /tmp/gllms_types.py back to the server
```
