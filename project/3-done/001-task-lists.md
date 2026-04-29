# Task Lists

## Abstract

Add lists to tasks. A task belongs to exactly one list (mutually exclusive). Default list "Inbox" for tasks without a specified list.

## Priority: 1

- Value: 7/10 — Core organizational feature.
- Momentum: 9/10 — Just shipped labels, same codebase.
- Effort: 3/10 — Simple FK, one new table, filter by list.
- Risk: 2/10 — Additive schema change, default list handles migration.
- Override: User wants this now.

## Timeline

- Captured: 2026-04-29
- Refined: 2026-04-29
- Started: 2026-04-29
- Verified: 2026-04-29
- Done: 2026-04-29

## Details

- `lists` table: id, name (unique).
- `tasks.list_id` FK, required.
- Default "Inbox" list created on startup.
- Tasks created without a list go to Inbox.
- CRUD for lists, filter tasks by list.

## Plan

Feature branch: `task-lists`

### 1. Backend: update task-service
- TDD: tests for list CRUD, task-list assignment, filtering
- Add List model, list_id FK on Task
- Ensure "Inbox" list exists on startup
- `POST /lists`, `GET /lists`
- `GET /tasks?list=X` filter
- Tasks include `list` in response

### 2. Frontend: update task-frontend
- List selector/tabs
- Default to Inbox

### 3. Integration test & verify

## Verification

Unit tests: 33 passing.

Integration (Postgres):
```
GET /lists → [Inbox] (default created)
POST /tasks with list=Shopping → created in Shopping
GET /tasks?list=Shopping → filtered
GET /lists → [Inbox, Shopping]
```

Frontend: list tabs, move dropdown, label filters — all confirmed by user.
