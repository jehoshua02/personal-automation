## What is personal-automation?

Automated personal productivity pipelines — email processing, calendar management, task scheduling, and time budgeting. Uses Google APIs, local open-source LLMs via Ollama, and self-hosted scripting.

Runs inside claude-container.

## Workflow

- Task management follows the quarry plugin. Folder structure is in `project/README.md`.
- Do not use Claude global memory. All project knowledge lives in this repo.
- When the next step is obvious from the workflow rules, just do it. Don't ask.
- **One-shot at pickup.** When moving a task from todo → doing, front-load all codebase research (read code, check APIs, trace dependencies) so the task file has a complete plan that can be executed without further questions. Inbox → todo refinement only needs enough context to score accurately.
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
