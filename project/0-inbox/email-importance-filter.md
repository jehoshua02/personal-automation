# Email Importance Filter

## Abstract

Insert a filtering step before LLM extraction that decides if an email is worth surfacing tasks/events from. Without this, the pipeline just converts noisy email into noisy tasks.

## Timeline

- Captured: 2026-04-27

## Details

### Problem

Pipeline extracts tasks/events/notes from every email indiscriminately. Result: noisy tasks instead of noisy email. No value added.

### Strategies to discuss

- **Sender whitelist:** Known-important senders always pass through. Simple, deterministic, but requires maintenance.
- **LLM categorization:** Ask LLM to classify email importance before extraction. More flexible, but adds latency and depends on prompt quality.
- **Hybrid:** Whitelist for known senders, LLM for the rest.

### Open questions

- Where in the pipeline does the filter go? Before or after gmail-reader fetch?
- New service or added to existing service?
- What categories? (important / noise / unsure?)
- How to bootstrap the whitelist?
- How to handle false negatives (important email filtered out)?
