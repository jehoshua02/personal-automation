# Network Segmentation

## Abstract

Move backend/internal services to a private Docker network. Frontend services communicate only through dedicated backend services, never directly to internal services. Enforce frontend → backend → private service routing.

## Priority: 48

- Value: 6/10 — Security architecture, aligns with stated design direction.
- Momentum: 2/10 — Architecture decision documented, chat services established the frontend/backend pattern.
- Effort: 4/10 — Docker network config, update compose, test connectivity.
- Risk: 5/10 — Could break inter-service communication if misconfigured.

## Timeline

- Captured: 2026-04-28
- Refined: 2026-04-29
