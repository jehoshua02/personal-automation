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

## Details

### Problem

Pipeline extracts tasks/events/notes from every email indiscriminately. Result: noisy tasks instead of noisy email. 80%+ of emails are noise.

### Strategy

Hybrid approach:
- **Sender whitelist:** Known-important senders always pass through.
- **LLM categorization:** For non-whitelisted senders, LLM classifies importance.
- **Safety net:** Filtered emails need a review mechanism (not silently dropped). Importance of false negatives varies by email.
