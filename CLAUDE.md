# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is personal-automation?

Automated personal productivity pipelines — email processing, calendar management, task scheduling, and time budgeting. Uses Google APIs, local open-source LLMs via Ollama, and self-hosted scripting. Runs inside Docker containers.

## Commands

```bash
# Start all services
docker compose up -d

# Run unit tests for a single service
docker compose run --rm --no-deps <service> pytest tests/ -v

# Services that need auth running (omit --no-deps):
docker compose run --rm auth pytest tests/ -v
docker compose run --rm gmail-reader pytest tests/ -v
docker compose run --rm note-writer pytest tests/ -v

# Run e2e tests (requires all services running + valid OAuth tokens)
docker compose up -d
docker compose run --rm e2e-tests

# Build a single service
docker compose build <service>

# Run the pipeline
curl -X POST http://localhost:8086/run -H "Content-Type: application/json" -d '{"max_results": 10}'

# Pull/swap LLM model
docker compose exec ollama ollama pull <model-name>
```

## Architecture

Nine Docker containers, each a single-responsibility HTTP service on a shared Compose network. All Python (Flask). No service calls another directly except through HTTP JSON APIs.

**Pipeline flow** (`POST /run` to orchestrator:8086):
1. orchestrator → `gmail-reader/fetch` → list of email messages
2. Per message: orchestrator → `email-filter/filter` → `{important, reason, method}`
3. If not important: orchestrator → `gmail-reader/mark-processed` with label "AutoFiltered" → skip to next
4. If important: orchestrator → `llm-processor/extract` → `{tasks[], events[], notes[]}`
5. Fan-out per extraction type:
   - tasks → `task-writer/write` → Google Tasks API
   - events → `calendar-writer/write` → Google Calendar API
   - notes → `note-writer/write` → local markdown files
6. orchestrator → `gmail-reader/mark-processed` → labels email in Gmail

**Auth pattern**: auth service (8080) manages OAuth2 tokens. gmail-reader, task-writer, and calendar-writer call `GET auth:8080/token` to get an access token before hitting Google APIs. note-writer has no auth (writes to bind-mounted filesystem).

**LLM**: llm-processor calls Ollama (11434) running llama3.1:8b locally on GPU. No email content leaves the machine.

**Config**: Services read config from environment variables set in `docker-compose.yml`. `CALENDAR_ID` comes from `.env` (gitignored).

## Workflow

- Task management follows the quarry plugin. Folder structure is in `project/README.md`.
- Do not use Claude global memory. All project knowledge lives in this repo.
- When the next step is obvious from the workflow rules, just do it. Don't ask.
- **One question at a time.** During refinement Q&A, ask only one question per message.
- **One-shot at pickup.** When moving a task from todo → doing, front-load all codebase research (read code, check APIs, trace dependencies) so the task file has a complete plan that can be executed without further questions. Inbox → todo refinement only needs enough context to score accurately.
- **Clear after done.** Run `/clear` after moving a task to `project/3-done/` to reset context for the next task.
- Push to remote after every commit.

## Implementation Rules

- **Install nothing on host.** Everything runs in Docker containers.
- **Docker Compose cluster.** Single responsibility per container. Services communicate via HTTP.
- **Languages:** Python or TypeScript per service. Any other language requires documented justification.
- **Strict TDD.** Tests first, then implementation, for every service.
- **5 attempts max** on any blocker before stopping and surfacing it.
- **Script UAT.** No manual verification except where unavoidable (e.g., OAuth consent).
- **Browser steps first.** Do all interactive/browser-dependent work before background processing so the user can step away.
- **Pre-approve permissions.** Before a long unattended run, set up `.claude/settings.local.json` with the bash commands needed.
- **Clean architecture.** Single responsibility from containers down to functions. Provider abstraction for swappable backends.
- **Contracts between services.** Language-agnostic, stable HTTP APIs. Each service can be rewritten independently.
- **Build and verify incrementally.** One service at a time in dependency order. Each step has a clear pass/fail signal before moving on.
- **Document the plan in the task file.** If context is lost, the task file has everything needed to resume.
