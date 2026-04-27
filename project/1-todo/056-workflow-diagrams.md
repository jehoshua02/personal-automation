# Workflow Diagrams

## Abstract

Create visual diagrams of the automation pipeline workflows showing service interactions and data flow.

## Priority: 56

- Value: 4/10 — Aids understanding and onboarding, but not blocking anything.
- Momentum: 1/10 — No work started.
- Effort: 3/10 — Pipeline is well-structured. Mermaid diagrams can be generated from known topology.
- Risk: 1/10 — Zero risk. Documentation only.

## Timeline

- Captured: 2026-04-27

## Details

### Research findings

**Pipeline flow** (triggered by `POST /run` to orchestrator):
1. Orchestrator → `gmail-reader/fetch` → list of email messages
2. Per message: Orchestrator → `llm-processor/extract` → `{tasks[], events[], notes[]}`
3. Fan-out per extraction type:
   - Each task → `task-writer/write` (Google Tasks API via auth)
   - Each event → `calendar-writer/write` (Google Calendar API via auth)
   - Each note → `note-writer/write` (local filesystem)
4. Orchestrator → `gmail-reader/mark-processed` → marks email done

**Service dependency graph:**
- auth ← gmail-reader, task-writer, calendar-writer (OAuth tokens)
- ollama ← llm-processor (LLM inference)
- note-writer is standalone (filesystem only)
- orchestrator calls gmail-reader, llm-processor, task-writer, calendar-writer, note-writer

### Implementation plan

Create `docs/` directory with Mermaid diagrams in Markdown:

1. **docs/pipeline-flow.md** — Sequence diagram showing the full `POST /run` pipeline: orchestrator → gmail-reader → llm-processor → fan-out to writers → mark-processed
2. **docs/service-topology.md** — Flowchart showing service dependencies, ports, and auth relationships
3. **docs/data-flow.md** — Diagram showing data shapes at each stage: raw email → extracted items → written outputs

Use Mermaid syntax (renders natively on GitHub). No external tools needed.

## Verification

- All three diagrams render correctly on GitHub
- Diagrams accurately reflect current codebase (cross-check with source)
