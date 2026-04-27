# Email Importance Filter

## Abstract

Insert a filtering step before LLM extraction that decides if an email is worth surfacing tasks/events from. Without this, the pipeline just converts noisy email into noisy tasks.

## Priority: 18

- Value: 9/10 — Pipeline is essentially broken without this. 80%+ noise means it creates more work than it saves.
- Momentum: 3/10 — LLM and gmail-reader infrastructure exist, but no filtering work started.
- Effort: 5/10 — New service, whitelist config, LLM prompt for categorization, integration into orchestrator.
- Risk: 3/10 — False negatives are the main risk, but mitigated by a review mechanism. Non-destructive — emails stay in Gmail.

## Timeline

- Captured: 2026-04-27
- Refined: 2026-04-27
- Started: 2026-04-27
- Verified: 2026-04-27
- Done: 2026-04-27

## Details

### Problem

Pipeline extracts tasks/events/notes from every email indiscriminately. Result: noisy tasks instead of noisy email. 80%+ of emails are noise.

### Strategy

Hybrid approach:
- **Sender whitelist:** Known-important senders always pass through.
- **LLM categorization:** For non-whitelisted senders, LLM classifies importance.
- **Safety net:** Filtered emails need a review mechanism (not silently dropped). Importance of false negatives varies by email.

### Architecture

New service: `email-filter` on port 8087. Follows single-responsibility pattern.

**Endpoint:** `POST /filter`
- Input: `{subject, body, from, date}`
- Output: `{important: bool, reason: string, method: "whitelist"|"llm"}`

**Logic:**
1. Check sender against whitelist (JSON config file at `/config/whitelist.json`, bind-mounted)
2. If whitelisted → `{important: true, method: "whitelist"}`
3. Else → call Ollama to classify, return verdict with reason

**Orchestrator change** (orchestrator.py:64, before `process_message()`):
- Call `POST email-filter:8087/filter` for each message
- Skip `extract` for non-important emails
- Mark filtered emails with a different Gmail label (e.g., "AutoFiltered") via `gmail-reader/mark-processed` so they can be reviewed

### Codebase references

- Orchestrator loop: `orchestrator.py:64` — insert filter call before `process_message()`
- Email fields available: `id, subject, body, from, date, link`
- LLM call pattern: `llm-processor/processor.py:8-76` — reuse for classification prompt
- Model: `llama3.1:8b` via Ollama at `http://ollama:11434`, JSON mode
- New service port: 8087 (next available after orchestrator:8086)
- Docker pattern: `build: ./services/email-filter`, `depends_on: [ollama]`

### Implementation plan

#### Phase 1: email-filter service (TDD) — DONE

- 15/15 tests passing. Whitelist + LLM classification + fail-open defaults.
- Workaround: ran tests via `docker run` mounting code into existing llm-processor image (docker build blocked over SSH by DPAPI).

#### Phase 2: orchestrator integration (TDD) — DONE

- 11/11 tests passing. Filter called before extract, filtered emails skipped.

#### Phase 3: gmail-reader label support — DONE

- 9/9 tests passing. mark-processed accepts optional label param. Filtered emails get "AutoFiltered" label.

#### Phase 4: e2e tests — DONE

- 26/26 e2e tests pass. Filter rejects spam, passes important emails, applies AutoFiltered label.
- Fixed: fetch query now excludes both `processed` and `AutoFiltered` labels.
- Added volume mounts for all services in docker-compose (no rebuild needed for code changes).

## Verification

```
26 passed in 34.60s
```

All unit tests: 15/15 email-filter, 11/11 orchestrator, 9/9 gmail-reader.
All e2e tests: 26/26 including filter spam, pass important, pipeline filter+label, no refetch.

### Whitelist bootstrap

Start with an empty whitelist. User adds senders as they review "AutoFiltered" emails and identify false negatives. Config file is bind-mounted so it's editable without rebuild.
