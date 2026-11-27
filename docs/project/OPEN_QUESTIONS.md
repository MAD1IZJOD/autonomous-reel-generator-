# Open Questions

| Field | Value |
|---|---|
| Status | Living document; updated as questions are resolved |
| Last updated | 2026-11-27 |
| Related | [Execution plan](EXECUTION_PLAN.md), [risks](RISKS.md), [milestones](MILESTONES.md) |

## 1. How to use this document

Each question has an ID, the area it affects, why it matters, whether it blocks a milestone and a provisional owner. Resolving a question means recording the answer, the evidence and the date in this document or in an ADR, then updating the documents that depended on it.

A question is `Blocking` if work cannot proceed safely without an answer. A question is `Non-blocking` if a provisional decision can be made and revisited.

## 2. Product and scope

| ID | Question | Why it matters | Blocking? | Owner |
|---|---|---|---|---|
| Q-001 | What is the final product name? | Branding, packaging, documentation | Non-blocking | Product |
| Q-002 | Is the product commercialised as SaaS, licensed software or a service? | Architecture, tenancy, billing | Non-blocking for MVP | Product |
| Q-003 | What licence applies to the repository and contributions? | Legal reuse, open-source strategy | Non-blocking for MVP | Product/Legal |
| Q-004 | What are the target output formats and durations beyond 60-second shorts? | Rendering, storage, QC | Non-blocking | Product |
| Q-005 | Is external client review required in the MVP? | User model, auth, UI | Non-blocking | Product |
| Q-006 | Are there customer-specific branding or template requirements? | Graphics kit, export | Non-blocking | Product |

## 3. Existing system and reproduction

| ID | Question | Why it matters | Blocking? | Owner |
|---|---|---|---|---|
| Q-010 | Can the founder provide all existing scripts, skill files and media? | Milestone 0 cannot start without them | Blocking (M0) | Product |
| Q-011 | Which steps in the existing workflow are undocumented or manual? | Automation scope and effort | Blocking (M0) | Engineering |
| Q-012 | What are the exact model versions and settings in production use? | Reproducibility | Blocking (M1) | Engineering |
| Q-013 | Can the reference reproduction run within existing paid accounts? | Cost and access | Blocking (M1) | Product/Engineering |
| Q-014 | What is the undocumented variance between the founder's reported costs and a clean run? | Baseline accuracy | Non-blocking | Engineering |

## 4. Architecture and infrastructure

| ID | Question | Why it matters | Blocking? | Owner |
|---|---|---|---|---|
| Q-020 | What throughput and concurrency are required? | Queue sizing, pool sizing | Non-blocking until M3 | Engineering |
| Q-021 | Do GPU agents pull jobs or are they driven by a control channel? | GPU orchestration design | Non-blocking | Engineering |
| Q-022 | Are model weights baked into images or mounted from a volume? | Licence, cache, deploy | Non-blocking | Engineering |
| Q-023 | Is managed PostgreSQL or self-hosted used in first production? | Deployment, cost, ops | Non-blocking | Engineering |
| Q-024 | Is a message broker needed before the MVP? | Complexity vs latency | Non-blocking | Engineering |
| Q-025 | What are the recovery time and point objectives? | Backup and DR design | Non-blocking | Product/Engineering |

## 5. Models and licensing

| ID | Question | Why it matters | Blocking? | Owner |
|---|---|---|---|---|
| Q-030 | What are the exact licence terms for Qwen-Image, Qwen-Image-Edit-2511 and Wan 2.2? | Commercial usability | Blocking for production enablement | Engineering/Legal |
| Q-031 | Is Qwen-Image 2.0 or newer commercially usable? | Future model choice | Non-blocking | Engineering |
| Q-032 | Can LongCat 1.6 improve lip-sync enough to justify evaluation? | Open alternative to HeyGen | Non-blocking | Engineering |
| Q-033 | Does fine-tuning IndicF5 on Avi's recording resolve accent and script issues? | Open voice alternative | Non-blocking | Engineering |
| Q-034 | Can InfiniteTalk be fine-tuned to match HeyGen? | Open presenter alternative | Non-blocking | Engineering |
| Q-035 | Is a house-style LoRA worth the training cost? | Quality/cost trade-off | Non-blocking | Product/Engineering |
| Q-036 | What are the consent requirements for the digital twin in a commercial product? | Legal blocker | Blocking for export | Product/Legal |
| Q-037 | Can model weights be redistributed or cached under their licences? | Deployment design | Non-blocking | Engineering/Legal |

## 6. Quality and evaluation

| ID | Question | Why it matters | Blocking? | Owner |
|---|---|---|---|---|
| Q-040 | What is the exact SyncNet threshold for this workflow? | QC gate calibration | Non-blocking | Engineering |
| Q-041 | How should jaw over-stretch be detected reliably? | Lip-sync QC | Non-blocking | Engineering |
| Q-042 | Should identity-consistency scoring be added for characters? | Quality improvement | Non-blocking | Product/Engineering |
| Q-043 | How should thresholds be calibrated for non-Avi presenters? | Multi-subject support | Non-blocking | Product/Engineering |
| Q-044 | Should quality profiles be user-selectable per run? | UX and cost | Non-blocking | Product |
| Q-045 | What dataset size is sufficient for model evaluation? | Evaluation validity | Non-blocking | Engineering |

## 7. Data and media

| ID | Question | Why it matters | Blocking? | Owner |
|---|---|---|---|---|
| Q-050 | Should voice be stored as one track, per-plate clips, or both? | Storage and editing | Non-blocking | Engineering |
| Q-051 | Should derived artifacts be separate versions or QC evidence only? | Asset model | Non-blocking | Engineering |
| Q-052 | Should content-addressed deduplication be workspace-wide or run-wide? | Storage cost | Non-blocking | Engineering |
| Q-053 | Should archived assets move to cold storage automatically? | Cost | Non-blocking | Engineering |
| Q-054 | How are multi-track audio and captions represented? | Data model | Non-blocking | Engineering |
| Q-055 | What are the final retention periods? | Compliance and cost | Blocking for production launch | Product/Legal |
| Q-056 | How is deletion verified in provider-side storage? | Compliance | Non-blocking | Engineering |

## 8. Security and enterprise

| ID | Question | Why it matters | Blocking? | Owner |
|---|---|---|---|---|
| Q-060 | Is application-level encryption required for restricted data in the first deployment? | Security design | Non-blocking | Engineering |
| Q-061 | Can GPU pods be fully isolated from the internet in all provider configurations? | Security | Non-blocking | Engineering |
| Q-062 | Are customer-managed keys a launch requirement or an enterprise feature? | Scope | Non-blocking | Product |
| Q-063 | Which compliance frameworks are required by target customers? | Enterprise scope | Non-blocking | Product |
| Q-064 | Is multi-tenancy required for the first commercial release? | Architecture and scope | Non-blocking for MVP | Product |

## 9. Development and operations

| ID | Question | Why it matters | Blocking? | Owner |
|---|---|---|---|---|
| Q-070 | What are the exact local development commands and tool versions? | Developer onboarding | Non-blocking | Engineering |
| Q-071 | Does GPU development use a remote pod or recorded fixtures only? | Cost and workflow | Non-blocking | Engineering |
| Q-072 | Is database seeding automated? | Developer experience | Non-blocking | Engineering |
| Q-073 | Do frontend and backend share a dev proxy? | Developer experience | Non-blocking | Engineering |
| Q-074 | Is blue/green deployment required for the MVP? | Release process | Non-blocking | Engineering |
| Q-075 | Are GPU images built in this repository or a separate one? | Repository structure | Non-blocking | Engineering |

## 10. Product and commercial

| ID | Question | Why it matters | Blocking? | Owner |
|---|---|---|---|---|
| Q-080 | What budget thresholds are appropriate for the first deployment? | Cost control | Non-blocking | Product/Engineering |
| Q-081 | Is internal cost tracked per run or charged to users? | Product model | Non-blocking | Product |
| Q-082 | How is shared GPU session cost attributed across jobs? | Cost accuracy | Non-blocking | Engineering |
| Q-083 | Should spot or preemptible instances be used for non-critical work? | Cost | Non-blocking | Engineering |
| Q-084 | How are provider pricing changes handled? | Cost stability | Non-blocking | Engineering |
| Q-085 | What risks should be escalated to the founder immediately? | Governance | Non-blocking | Product |

## 11. Resolving questions

A question is resolved by:

1. Recording the answer in this document or an ADR.
2. Updating dependent documents.
3. Marking the question as resolved with date and evidence.
4. Removing it from the blocking list if applicable.

Questions are never deleted; resolved questions remain as a decision history.
