# Todo Database

## Abstract

Build a task-service (HTTP CRUD API) and task-store (Postgres with bind-mounted volume) for persisting tasks. Fields: title, description, completed timestamp, created/modified timestamps.

## Priority: 1

- Value: 6/10 — Foundation for replacing Google Tasks dependency.
- Momentum: 1/10 — Greenfield.
- Effort: 4/10 — Two services, straightforward schema.
- Risk: 2/10 — First stateful service (Postgres), but isolated.
- Override: User wants to do this tonight.

## Timeline

- Captured: 2026-04-28
- Refined: 2026-04-28
- Started: 2026-04-29
- Verified: 2026-04-29
- Done: 2026-04-29

## Details

- task-service: Python/Flask HTTP API for CRUD operations on tasks.
- task-store: Postgres container with bind-mounted volume for persistence through container churn.
- Fields: title, description, completed_at, created_at, updated_at.

## Plan

Feature branch: `001-todo-database`

### 1. task-store: Postgres container
- Add Postgres service to docker-compose.yml with bind-mounted volume
- Env vars: POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
- Port 5432 (internal only, no host mapping needed)

### 2. task-service (port 8090)
- TDD: tests first for all CRUD endpoints
- `POST /tasks` — create task (title required, description optional)
- `GET /tasks` — list all tasks
- `GET /tasks/<id>` — get single task
- `PUT /tasks/<id>` — update task (title, description, completed_at)
- `DELETE /tasks/<id>` — delete task
- Schema auto-creates on startup
- Files: Dockerfile, requirements.txt, app.py, db.py, tests/
- Add to docker-compose.yml, depends_on task-store

### 3. Integration test
- docker compose up task-store task-service
- curl: create, list, get, update, delete

### 4. Verify & complete

## Verification

Unit tests: 14 passing (SQLite in-memory).

Integration (Postgres):
```
POST /tasks → 201, task created with timestamps
GET /tasks → 200, list with 1 task
GET /tasks/1 → 200, single task
PUT /tasks/1 (completed_at) → 200, completed_at set
DELETE /tasks/1 → 204
GET /tasks/1 → 404 (confirmed deleted)
```

DB retry logic handles Postgres startup delay.
