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
- Started: 2026-04-27
- Verified: 2026-04-27
- Done: 2026-04-27

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

### Implementation Plan

**Rules:**
- Strict TDD: tests first, then implementation, for every service.
- 5 attempts max on any blocker before stopping and surfacing it.
- UAT is scripted — no manual verification except OAuth consent.
- Build and verify one service at a time, in dependency order.

**Phase 0: Browser-dependent (do before user steps away)**
1. Build auth service with OAuth2 flow
2. User completes consent in browser → tokens stored
3. Verify token works with a test Gmail API call

**Phase 1: Infrastructure**
4. docker-compose with ollama, GPU passthrough, model pull
5. Verify ollama responds to health check and inference

**Phase 2: Input**
6. gmail-reader service — TDD, fetch messages, manage "processed" label
7. Verify against test inbox (send test emails to jehoshua02dev@gmail.com first)

**Phase 3: Processing**
8. llm-processor service — TDD, extract tasks/events/notes from message content
9. Verify extraction output against known test inputs

**Phase 4: Output**
10. task-writer — TDD, write to Google Tasks "Auto-Extracted" list
11. calendar-writer — TDD, write to Google Calendar
12. note-writer — TDD, write local markdown files
13. Verify each writer with scripted checks (API reads, file existence)

**Phase 5: Integration**
14. orchestrator — TDD, wires pipeline end-to-end
15. Scripted UAT: send test email → run pipeline → verify task/event/note created

**Verification strategy:**
- Unit tests per service (mocked dependencies)
- Integration tests per service (real dependencies where possible)
- End-to-end UAT script: sends email, triggers pipeline, asserts outputs exist in Google Tasks, Calendar, and local notes folder

## Verification

### Unit Tests (54 total, all passing)
- auth: 12/12
- gmail-reader: 8/8
- llm-processor: 7/7
- task-writer: 5/5
- calendar-writer: 5/5
- note-writer: 9/9
- orchestrator: 8/8

### Integration Tests
- OAuth token verified against Gmail API (profile returned for jehoshua02dev@gmail.com)
- Ollama inference verified (llama3.1:8b responds correctly)
- All 7 service health checks pass

### End-to-End UAT
- Test email 1: "Dinner with Sarah Thursday 7pm" → extracted task (pick up dry cleaning), event (dinner), note (restaurant confirmation RES-4521). Task written to Google Tasks, note written to markdown.
- Test email 2: "Quarterly review next Monday" → extracted task (prepare self-assessment), event (quarterly review at HR office, 10-11am), note (employee ID EMP-7842). All three written successfully to Google Tasks, Google Calendar, and markdown.
- Processed label applied to emails after processing.
- Second pipeline run correctly skips already-processed emails.

### Bugs Fixed During Testing
1. LLM response parser didn't handle plain ``` code blocks (only ```json). Fixed regex to extract JSON from any wrapper.
2. Calendar writer failed on missing end time. Added default end = start + 1 hour.
3. Note filenames used raw RFC 2822 date header. Orchestrator now parses to YYYY-MM-DD.
