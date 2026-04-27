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

#### Phase 1: email-filter service (TDD)

1. Scaffold `services/email-filter/` (app.py, filter.py, requirements.txt, Dockerfile)
2. Tests first: whitelist logic, LLM classification, endpoint integration
3. Whitelist: load from `/config/whitelist.json`, match on sender email/domain
4. LLM classification: prompt Ollama with email context, parse JSON response `{important: bool, reason: string}`
5. `POST /filter` endpoint wires it together

#### Phase 2: orchestrator integration (TDD)

1. Tests first: orchestrator skips extract for filtered emails
2. Add filter call in orchestrator loop before extract
3. Pass filter verdict to mark-processed (different label for filtered vs processed)

#### Phase 3: gmail-reader label support

1. Add "AutoFiltered" label handling to gmail-reader mark-processed endpoint
2. Filtered emails get labeled but not extracted — user can review the label in Gmail

#### Phase 4: e2e test

1. Update e2e tests to verify filter → extract → write flow
2. Verify filtered emails get correct label

### Whitelist bootstrap

Start with an empty whitelist. User adds senders as they review "AutoFiltered" emails and identify false negatives. Config file is bind-mounted so it's editable without rebuild.
