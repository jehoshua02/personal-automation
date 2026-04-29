# Ollama Chat UI

## Abstract

Build a frontend chat interface for interacting with local Ollama models. Two new services: a frontend service (serves UI, takes user input, sends to backend) and a backend chat service (receives HTTP requests from frontend, routes them to Ollama). Purpose: explore what Ollama is capable of.

## Priority: 1

- Value: 6/10 — Exploratory, informs future LLM decisions.
- Momentum: 1/10 — Greenfield.
- Effort: 4/10 — Two services, each simple.
- Risk: 1/10 — Isolated, no impact on existing pipeline.
- Override: User wants to do this tonight.

## Timeline

- Captured: 2026-04-28
- Refined: 2026-04-28

## Details

- Frontend service: serves HTML chat UI, sends user prompts to backend service via HTTP.
- Backend chat service: receives chat requests from frontend, forwards to Ollama (`ollama:11434/api/chat`), returns response. Single responsibility is routing chat from frontend to LLM.
- Hits Ollama directly, not through llm-processor.
