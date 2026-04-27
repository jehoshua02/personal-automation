# Gmail Processing Pipeline

## Abstract

Automated pipeline that reads Gmail inbox via Google APIs, uses a local open-source LLM to extract tasks, reference info, and calendar events. Outputs to Google Tasks, Google Calendar, and local markdown notes. Runs in claude-container.

## Priority: 38

- Value: 8/10 — High personal productivity impact, automates manual inbox review
- Momentum: 2/10 — Fresh start, no prior work
- Effort: 7/10 — Multiple integrations (Google APIs, Ollama, Docker), provider abstractions
- Risk: 4/10 — Google API auth complexity, but self-contained and reversible

## Timeline

- Captured: 2026-04-26
- Refined: 2026-04-26

## Details

### Decisions

- **Languages**: Python or TypeScript per-service. Any other language requires documented justification.
- **Host rule**: Install nothing on host. Everything containerized.
- **Docker**: docker-compose cluster. Single responsibility per container.
- **Notes**: Local markdown files. Simple format: date + topic slug filename, email link required. Provider must be swappable.
- **Tasks**: Google Tasks API, list name "Auto-Extracted". Provider must be swappable.
- **LLM**: Ollama containerized, local GPU (RTX 3070 Ti, 8GB VRAM). Candidates: Llama 3.1 8B, Mistral 7B, Phi-3 Mini. Model must be swappable. Support running multiple models in parallel for benchmarking/comparison.
- **Trigger**: Manual first → cron poll → Gmail Pub/Sub push (progressive).
- **Scope**: All mail, most recent first, working backward. Label "processed" tracks processed messages.
- **LLM extraction**: Tasks (explicit and implicit), calendar events, reference notes. Must handle non-obvious/inferred items.
- **Google OAuth2**: Starting fresh. GCP project setup included. Auth token management in its own container.
- **Testing**: Dedicated test Google account. GCP project in unverified/test mode with test account added as test user.
- **Architecture**: Provider abstraction layer for tasks, notes, and LLM. Swappable backends. Clean architecture.

### Containers

- **auth** — OAuth2 token management, shared by services needing Google API access
- **gmail-reader** — fetches messages, manages "processed" label
- **llm-processor** — receives message content, calls Ollama, returns structured extractions
- **task-writer** — writes to Google Tasks ("Auto-Extracted" list)
- **calendar-writer** — writes to Google Calendar
- **note-writer** — writes local markdown files
- **orchestrator** — coordinates the pipeline, routes extractions to writers
- **ollama** — official Ollama image, GPU passthrough, model volume

### Prerequisites

- [x] Create test Google account — jehoshua02dev@gmail.com
- [x] Create GCP project, enable Gmail/Calendar/Tasks APIs
- [x] Create OAuth2 client credentials — downloaded to secrets/
- [x] Add test account as test user in OAuth consent screen
- [x] .gitignore secrets/

### Open Questions (resolved)
All initial questions resolved. Architecture design is next step.
