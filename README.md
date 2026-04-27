# personal-automation

Automated Gmail processing pipeline that reads your inbox, extracts actionable items using a local LLM, and writes them to Google Tasks, Google Calendar, and local markdown notes. Everything runs in Docker — nothing installed on your machine.

## Why

Email is where tasks, meetings, and reference info go to hide. This pipeline pulls them out automatically:

- **Tasks** — explicit requests and implied obligations land in a Google Tasks list ("Auto-Extracted")
- **Events** — meetings, deadlines, and time-specific items land on your Google Calendar
- **Notes** — credentials, confirmation numbers, reference info saved as markdown with a link back to the original email

Processing uses a local LLM (Llama 3.1 8B via Ollama) running on your GPU. No email content leaves your machine.

## Architecture

Eight containers, one job each:

| Service | Port | Role |
|---|---|---|
| **auth** | 8080 | OAuth2 token management for Google APIs |
| **ollama** | 11434 | Local LLM server (GPU) |
| **gmail-reader** | 8081 | Fetches messages, manages "processed" label |
| **llm-processor** | 8082 | Extracts tasks/events/notes from email content |
| **task-writer** | 8083 | Writes to Google Tasks |
| **calendar-writer** | 8084 | Writes to Google Calendar |
| **note-writer** | 8085 | Writes markdown files |
| **orchestrator** | 8086 | Coordinates the pipeline end-to-end |

Services communicate over HTTP with stable JSON contracts. Each can be rewritten in any language independently.

## Prerequisites

- Docker with Compose v2+
- NVIDIA GPU with drivers installed (for Ollama)
- A Google Cloud project with these APIs enabled:
  - Gmail API
  - Google Calendar API
  - Google Tasks API
- OAuth2 client credentials (Web application type)

## Setup

### 1. Google Cloud

1. Create a project at [console.cloud.google.com](https://console.cloud.google.com)
2. Enable Gmail, Calendar, and Tasks APIs
3. Configure OAuth consent screen (External, test mode)
4. Add your email as a test user
5. Create OAuth2 credentials (Web application)
6. Set authorized redirect URI to `http://localhost:8080/callback`
7. Download the client secret JSON

### 2. Credentials

Place the downloaded JSON in `secrets/`:

```
secrets/client_secret_<your-client-id>.apps.googleusercontent.com.json
```

Update `docker-compose.yml` to point to your file:

```yaml
services:
  auth:
    volumes:
      - ./secrets/<your-file>.json:/secrets/client_secret.json:ro
```

### 3. Start the cluster

```bash
docker compose up -d
```

### 4. Pull the LLM model

```bash
docker compose exec ollama ollama pull llama3.1:8b
```

### 5. Authenticate

Open [http://localhost:8080/login](http://localhost:8080/login) in your browser. Sign in with your Google account and grant permissions. You'll see a JSON response confirming authentication.

### 6. Run the pipeline

```bash
curl -X POST http://localhost:8086/run -H "Content-Type: application/json" -d '{"max_results": 10}'
```

Processed emails are labeled "processed" in Gmail and won't be re-fetched on subsequent runs.

## Running tests

### Unit tests (per service)

```bash
docker compose run --rm auth pytest tests/ -v
docker compose run --rm gmail-reader pytest tests/ -v
docker compose run --rm --no-deps llm-processor pytest tests/ -v
docker compose run --rm --no-deps task-writer pytest tests/ -v
docker compose run --rm --no-deps calendar-writer pytest tests/ -v
docker compose run --rm note-writer pytest tests/ -v
docker compose run --rm --no-deps orchestrator pytest tests/ -v
```

### Integration / E2E tests

Requires all services running and OAuth tokens valid:

```bash
docker compose up -d
docker compose run --rm e2e-tests
```

The e2e suite (22 tests) covers service health, OAuth against all three Google APIs, message fetching, LLM extraction, all three writers, full pipeline flow, and idempotency.

## Swapping the LLM model

Change the `LLM_MODEL` environment variable in `docker-compose.yml` and pull the new model:

```bash
docker compose exec ollama ollama pull <model-name>
```

Restart the processor:

```bash
docker compose up -d llm-processor
```

## Notes storage

Notes are stored in the `notes-data` Docker volume at `/data/notes` inside the note-writer container. To inspect:

```bash
docker compose exec note-writer bash -c "ls /data/notes/"
docker compose exec note-writer bash -c "cat /data/notes/<filename>"
```

To use a local directory instead, change the volume to a bind mount in `docker-compose.yml`:

```yaml
note-writer:
  volumes:
    - ./notes:/data/notes
```
