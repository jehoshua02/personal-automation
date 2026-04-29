# Network Segmentation

## Abstract

Move backend/internal services to a private Docker network. Frontend services communicate only through dedicated backend services, never directly to internal services. Enforce frontend → backend → private service routing.
