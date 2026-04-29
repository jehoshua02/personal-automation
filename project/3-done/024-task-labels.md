# Task Labels

## Abstract

Add labels to tasks in task-service and filter the task list by label. Enables categorization and filtered views in the task-frontend.

## Priority: 1

- Value: 7/10 — Core feature for organizing tasks.
- Momentum: 8/10 — task-service and task-frontend just built tonight.
- Effort: 4/10 — New tables, update CRUD, update frontend.
- Risk: 2/10 — Additive schema change, no breaking changes.
- Override: User wants this now.

## Timeline

- Captured: 2026-04-29
- Refined: 2026-04-29
- Started: 2026-04-29
- Verified: 2026-04-29
- Done: 2026-04-29

## Details

- Many-to-many: `labels` table + `task_labels` join table.
- Tasks returned with their labels array.
- `GET /tasks?label=X` filters by label.
- Frontend: label input on create, filter dropdown/buttons.

## Plan

Feature branch: `024-task-labels`

### 1. Backend: update task-service schema
- TDD: tests for label CRUD and filtering
- Add Label model and task_labels association table
- `POST /labels` — create label
- `GET /labels` — list all labels
- `POST /tasks` — accept optional `labels` array
- `PUT /tasks/<id>` — update labels
- `GET /tasks?label=X` — filter by label
- Tasks include `labels` in response

### 2. Frontend: update task-frontend
- Label input when creating tasks
- Filter buttons/dropdown by label
- Display labels on each task

### 3. Integration test & verify

## Verification

Unit tests: 23 passing.

Integration (Postgres):
```
POST /tasks with labels → 201, labels attached
GET /tasks?label=grocery → filtered results
GET /labels → all labels listed
```

Frontend tested in browser by user — confirmed working.
