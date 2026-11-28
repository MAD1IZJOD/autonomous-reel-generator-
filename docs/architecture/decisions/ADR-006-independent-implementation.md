# ADR-006: Begin Independent Implementation Without the Founder's Scripts

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-11-28 |
| Supersedes | The gating rule in `AGENTS.md` section 2 and `docs/project/EXECUTION_PLAN.md` section 2 |
| Related | [PRD](../product/PRD.md), [system architecture](SYSTEM_ARCHITECTURE.md), [baseline reproduction plan](../discovery/BASELINE_REPRODUCTION_PLAN.md) |

## Context

The original plan required Milestone 0 (code audit) and Milestone 1 (reference reproduction) to finish before application development. Those milestones assumed the founder's controller, ComfyUI workflows, model servers, HyperFrames builder and QC scripts would be supplied.

The founder has instead supplied a technical specification and `CLAUDE.md` describing the production pipeline, settings and constraints. The original implementation artifacts are not available and will not be supplied. Waiting for them would block the product indefinitely.

The specification is sufficient to build an independent implementation, but it is not sufficient to claim reproduction of the founder's exact quality. The distinction must remain explicit.

## Decision

1. Begin Phase 4 implementation from the written specification, not from the founder's code.
2. Build an independent control plane, job engine, asset registry, routing layer and media pipeline.
3. Use deterministic mock providers and synthetic fixtures for the first vertical slice. No paid calls, GPU provisioning or model downloads.
4. Treat founder-reported settings as reference configurations, not verified production values.
5. Preserve the unknown register. A value is not verified because it appears in this ADR or in code.
6. Keep the reference reproduction plan as a later validation activity, not as a precondition for building the product.
7. Do not claim that mocked output demonstrates model quality. Mocked output validates architecture, state transitions, media plumbing and QC mechanics only.

## Consequences

- The product can progress without founder artifacts.
- The first demonstration is an explainer workflow with real FFmpeg output but synthetic voice, stills, motion and presenter assets.
- Real provider integration remains a separate, cost-gated step.
- Milestone numbering in older documents is retained for history, but implementation now proceeds on the Phase 4 track described in `docs/implementation/PHASE4_IMPLEMENTATION_PLAN.md`.
- `AGENTS.md` and `EXECUTION_PLAN.md` must no longer forbid application code.

## What this ADR does not decide

- That the founder's exact quality has been reproduced.
- That any open-weight model is commercially licensed.
- That mock media is acceptable for publication.
- That GPU or paid-provider access is available.
