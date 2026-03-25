# Containerize and Document

The bot has been running on your VM as a background process (`nohup`). That works for development, but it's fragile — it won't restart after a reboot, logs aren't managed, and it runs outside Docker while the backend runs inside. In this task, you containerize the bot so it runs alongside the backend as a proper Docker service.

## Requirements targeted

- **P3.1** Bot containerized with Dockerfile
- **P3.2** Added as service in `docker-compose.yml`
- **P3.3** Running as container on VM
- **P3.4** README documents deployment

## Deliverables

### 1. Bot Dockerfile (`bot/Dockerfile`)

Installs dependencies using `uv sync` from `bot/pyproject.toml` and runs the bot entry point.

> [!IMPORTANT]
> Do **not** use `requirements.txt` or `pip install`. The project uses `uv` and `pyproject.toml` exclusively. Having both `pyproject.toml` and `requirements.txt` leads to dependency drift and random breakage. If your coding agent generates a `requirements.txt`, delete it.

### 2. Bot service in `docker-compose.yml`

Add a `bot` service to the existing compose file:

- Connects to backend via Docker network (service name, not `localhost`)
- Reads `BOT_TOKEN` and LLM credentials from environment
- Restarts unless stopped

> [!IMPORTANT]
> **Docker networking change.** Until now, the bot ran on the host and used `localhost:42002` to reach the backend. Inside Docker, `localhost` means the container itself. The bot must use the Docker service name instead: `http://backend:8000`.

### 3. README deploy section

Add a "Deploy" section to the project README explaining: required env vars, docker compose commands, how to verify.

## Verify

### Build and start

On your VM, stop the background bot process and switch to Docker:

```terminal
cd ~/se-toolkit-lab-7

# Stop the nohup bot
pkill -f "bot.py" 2>/dev/null

# Start everything with Docker
docker compose --env-file .env.docker.secret up --build -d
docker compose --env-file .env.docker.secret ps
```

You should see the `bot` service running alongside `backend`, `postgres`, `caddy`.

### Check the bot container is healthy

```terminal
# Is it running?
docker compose --env-file .env.docker.secret ps bot

# Check logs for startup errors
docker compose --env-file .env.docker.secret logs bot --tail 20
```

**What to look for in the logs:**

- "Application started" — bot connected to Telegram successfully
- "HTTP Request: POST .../getUpdates" — bot is polling for messages
- No Python tracebacks

### Verify in Telegram

Send these in Telegram — everything that worked before should still work:

1. `/start` — welcome message
2. `/health` — backend status
3. "what labs are available?" — natural language, LLM-powered
4. "which lab has the lowest pass rate?" — multi-step reasoning

### Common Docker problems

| Symptom                            | Likely cause                                                                                                                  |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Bot container keeps restarting     | Check logs: `docker compose logs bot`. Usually a missing env var or import error.                                             |
| `/health` fails but worked before  | `LMS_API_BASE_URL` must be `http://backend:8000` (not `localhost:42002`). Inside Docker, `localhost` is the container itself. |
| LLM queries fail but worked before | `LLM_API_BASE_URL` must use `host.docker.internal` (not `localhost`). The qwen proxy is on a different Docker network.        |
| "BOT_TOKEN is required" error      | Bot env vars need to be in `.env.docker.secret`, not just `.env.bot.secret`.                                                  |
| Build fails at `uv sync --frozen`  | `uv.lock` must be copied in the Dockerfile. Check your `COPY` commands.                                                       |

## Acceptance criteria

### On `GitHub`

- [ ] [`Git workflow`](../../../wiki/git-workflow.md) followed (issue, branch, PR, review, merge).

### On `GitHub` on the `main` branch

- [ ] `bot/Dockerfile` exists.
- [ ] `docker-compose.yml` includes a `bot` service.

### On the VM (REMOTE)

- [ ] Bot container running (`docker ps` shows it).
- [ ] Backend still healthy (`curl -sf http://localhost:42002/docs` returns 200).
- [ ] `git remote get-url origin` matches student's GitHub repo.
- [ ] README has a section with "deploy" in heading.
- [ ] Bot responds in Telegram from the container (TA-verified).
- [ ] Git workflow followed.
- [ ] .
