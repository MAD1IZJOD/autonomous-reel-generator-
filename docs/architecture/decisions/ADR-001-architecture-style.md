# ADR-001: Architecture style

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-11-27 |
| Deciders | Engineering (Madhavan), Product (Avinash Pandit) |
| Related | [System architecture](../SYSTEM_ARCHITECTURE.md), [ADR-002](ADR-002-async-orchestration.md), [ADR-005](ADR-005-gpu-management.md) |

## 1. Context

We are replacing a working but informal AI video workflow with a standalone product. The workflow has long-running, expensive, failure-prone GPU stages, human approval gates, versioned media assets and multiple external providers. The initial team is small, but the system is intended to become commercially deployable and eventually multi-tenant.

The question is whether to start with a microservice architecture or a simpler deployment.

## 2. Decision

Start with a **modular monolith control plane** plus **independently scalable worker tiers**:

- One control-plane application containing domain modules with enforced boundaries.
- Separate CPU worker processes for render, probing, QC orchestration and composition.
- Separate GPU agents and model servers for inference.
- A single relational database as the source of truth.
- S3-compatible object storage for media.

Modules are designed so they can be extracted into separate services later, but extraction is not the default.

## 3. Alternatives considered

### 3.1 Microservices from day one

Rejected for the MVP. It would add distributed transactions, service discovery, per-service deployment, network failure modes and observability overhead before throughput, team boundaries and security requirements are measured. The actual scaling pressure is GPU inference and rendering, which are already separate tiers.

### 3.2 Single script or notebook workflow

Rejected. This is the current state we are leaving. It has no durable job state, no approval gates, no cost attribution and no recovery.

### 3.3 Serverless functions for all stages

Rejected. Long-running GPU inference, model loading and FFmpeg rendering do not fit typical serverless limits. Cold starts would recreate the model-loading waste we are trying to remove. Serverless may be used later for lightweight, stateless helpers if measured.

### 3.4 One monolith including GPU inference

Rejected. GPU model servers have different hardware, lifecycle and scaling needs. Embedding them in the control plane would couple deploys and force GPU hardware on every host.

## 4. Consequences

Positive:

- Fast iteration with one transactional database.
- Simpler deployment and debugging for a small team.
- Module boundaries preserve future extraction.
- GPU and render capacity scale independently.
- Clear ownership of state in PostgreSQL.

Negative:

- Discipline is required to keep module boundaries; a monolith can become a big ball of mud.
- One deploy unit for all API modules; a change to one module requires deploying the control plane.
- Horizontal scaling of the API is process-level, not service-level.

Mitigations:

- Module imports are constrained by package structure and review.
- Cross-module state changes use explicit service calls or recorded events.
- Provider SDK types are isolated in adapters.
- Extraction criteria are documented in [SYSTEM_ARCHITECTURE.md](../SYSTEM_ARCHITECTURE.md).

## 5. Reversal criteria

Reconsider this decision when one or more of the following are measured:

- A module needs an independent release cadence that cannot be met by the monolith.
- A module has materially different scaling or security requirements.
- A tenant requires isolation that cannot be provided within the monolith.
- Operational complexity of the monolith exceeds that of the proposed split.

Any extraction must be justified by evidence and recorded in a new ADR. It must not be done speculatively.

## 6. Notes

This decision does not imply that the application is a single process. The control plane, CPU workers, GPU agents and model servers are separate processes from the start. The monolith refers to the control plane's code and deployment unit.
