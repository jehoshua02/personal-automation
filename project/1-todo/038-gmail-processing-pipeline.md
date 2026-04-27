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

- **Notes**: Local markdown files. Provider must be swappable.
- **Tasks**: Google Tasks API. Provider must be swappable.
- **LLM**: Ollama on local GPU (RTX 3070 Ti, 8GB VRAM). Candidates: Llama 3.1 8B, Mistral 7B, Phi-3 Mini. Model must be swappable. Support running multiple models in parallel for benchmarking/comparison.
- **Trigger**: Manual first → cron poll → Gmail Pub/Sub push (progressive).
- **Scope**: All mail, most recent first, working backward. Custom label tracks processed messages.
- **Hosting**: Inside claude-container Docker environment.
- **Architecture**: Provider abstraction layer for tasks, notes, and LLM. Swappable backends.

### Architecture (to design)

- Google API auth (OAuth2 for Gmail, Calendar, Tasks)
- Gmail reader: fetch messages, manage processed label
- LLM processor: extract tasks, events, notes from message content
- Provider interfaces: TaskProvider, NoteProvider, LLMProvider
- Output writers: Google Tasks, Google Calendar, local markdown
- Benchmark harness: run same message through multiple models, compare outputs
- Orchestrator: ties it all together, handles errors/retries

### Open Questions (resolved)
All initial questions resolved. Architecture design is next step.
