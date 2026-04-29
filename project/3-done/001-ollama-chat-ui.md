# Ollama Chat UI

## Abstract

Build a frontend chat interface for interacting with local Ollama models. Two new services: a frontend service (serves UI, takes user input, sends to backend) and a backend chat service (receives HTTP requests from frontend, routes them to Ollama). Purpose: explore what Ollama is capable of.

## Priority: 1

- Value: 6/10 — Exploratory, informs future LLM decisions.
- Momentum: 1/10 — Greenfield.
- Effort: 4/10 — Two services, each simple.
- Risk: 1/10 — Isolated, no impact on existing pipeline.
- Override: User wants to do this tonight.

## Timeline

- Captured: 2026-04-28
- Refined: 2026-04-28
- Started: 2026-04-28
- Verified: 2026-04-28
- Done: 2026-04-28

## Details

- Frontend service: serves HTML chat UI, sends user prompts to backend service via HTTP.
- Backend chat service: receives chat requests from frontend, forwards to Ollama (`ollama:11434/api/chat`), returns response. Single responsibility is routing chat from frontend to LLM.
- Hits Ollama directly, not through llm-processor.

## Plan

Feature branch: `001-ollama-chat-ui`

### 1. Backend service: `chat-backend` (port 8088)
- TDD: tests first for `/chat` endpoint
- `POST /chat` — accepts `{"message": "..."}`, forwards to Ollama `/api/generate`, returns `{"response": "..."}`
- `GET /health`
- Env vars: `OLLAMA_URL`, `LLM_MODEL`
- Files: Dockerfile, requirements.txt, app.py, chat.py, tests/
- Add to docker-compose.yml, depends_on ollama

### 2. Frontend service: `chat-frontend` (port 8089)
- TDD: tests for serving index page
- Serves a single HTML page with text input and response area
- JS sends POST to chat-backend via exposed port 8088
- Files: Dockerfile, requirements.txt, app.py, templates/index.html, tests/
- Add to docker-compose.yml

### 3. Integration test
- docker compose up both services + ollama
- curl: send prompt, get response

### 4. Verify & complete

## Verification

```
$ curl -s http://localhost:8088/health
{"status":"ok"}

$ curl -s http://localhost:8089/health
{"status":"ok"}

$ curl -s -X POST http://localhost:8088/chat -H "Content-Type: application/json" -d '{"message": "Say hello in exactly 5 words."}'
{"response":"Hello, how are you doing today?"}
```

Unit tests: 7 backend, 2 frontend — all pass.
Frontend UI available at http://localhost:8089.
