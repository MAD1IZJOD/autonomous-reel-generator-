# Milestones

| Field | Value |
|---|---|
| Status | Foundation |
| Last updated | 2026-11-27 |
| Related | [Execution plan](EXECUTION_PLAN.md), [acceptance criteria](../product/ACCEPTANCE_CRITERIA.md), [risks](RISKS.md) |

Milestones are gated. A milestone is complete only when its exit criteria are evidenced. Calendar dates are intentionally omitted until the code audit establishes the workload.

## Milestone 0 — Discovery and code audit

**Objective:** understand the existing system, its scripts, models, costs and licences well enough to reproduce it and plan the product.

**Deliverables:**

- Audit report covering scripts, workflows, models, providers, hardware and timings.
- Dependency and execution-sequence map.
- Licence review for all models, tools and assets.
- Gap list of undocumented or manual steps.
- Cost and timing observations with sources.
- Updated open questions.

**Exit criteria:**

- The team can state what the reference reproduction requires and costs.
- Every component has a licence status.
- The integration strategy (wrap vs port vs replace) is decided per component.
- No application code has been written.

**Dependencies:** founder artifacts and access to existing accounts.

**Risks:** missing scripts, undocumented steps, licence surprises. See [RISKS.md](RISKS.md).

## Milestone 1 — Reference reproduction

**Objective:** reproduce one existing 60-second short end to end through a controlled process.

**Deliverables:**

- Reference input package and approved script.
- Reproduced video and run manifest.
- Timing, cost, retry and failure records.
- QC evidence for voice and lip-sync.
- Founder acceptance note from a blind comparison.
- Repeat-run measurement.

**Exit criteria:**

- AC-REP-001 through AC-REP-010 are satisfied.
- The reproduction is repeatable by another engineer from documented steps.
- Variance against the founder's reported figures is explained.

**Dependencies:** Milestone 0.

## Milestone 2 — Standalone execution foundation

**Objective:** create the application foundation and integrate existing scripts one stage at a time.

**Deliverables:**

- Repository scaffold and CI.
- Domain models, state machines and invariants.
- Database schema and migrations.
- Object storage adapter.
- Job engine with leases and retries.
- Provider adapters for the baseline capabilities.
- GPU lifecycle adapter.
- At least one stage running through the application with real inference.
- Minimal web UI for run status and artifacts.
- Observability and cost instrumentation.

**Exit criteria:**

- A run can be created from an approved plan.
- Job state, cost and provenance are recorded.
- Failures are visible and recoverable.
- No fake outputs or mock success.

**Dependencies:** Milestone 1.

## Milestone 3 — GPU efficiency

**Objective:** reduce waste from provisioning and model loading.

**Deliverables:**

- Resident model servers and warm pools.
- Compatible-job batching.
- Preflight validation.
- Idle shutdown and watchdog.
- Cost metering and budget controls.
- Before/after measurement on the reference run.

**Exit criteria:**

- Model loading waste is measured and reduced.
- No orphaned GPU sessions during a normal run.
- Cost per accepted output is compared with the Milestone 1 baseline.
- Quality is unchanged.

**Dependencies:** Milestone 2.

## Milestone 4 — Model abstraction and routing

**Objective:** make providers and models replaceable and evaluate alternatives without sacrificing quality.

**Deliverables:**

- Model registry and routing policy.
- All model references removed from domain code.
- Licence and egress gates.
- At least one completed evaluation record for an open alternative.
- Routing decisions stored and reviewable.

**Exit criteria:**

- A model can be added or replaced without code changes.
- Quality floors are enforced.
- Premium baselines are retained where they win.

**Dependencies:** Milestone 1, Milestone 0 licence review, Milestone 2.

## Milestone 5 — Product MVP

**Objective:** package the capability into a usable single-workspace product.

**Deliverables:**

- Project, script and plate-sheet management.
- Approval workflows and review UI.
- Shot-level regeneration.
- Progress tracking and cost visibility.
- Final QC and export.
- Run recovery and cancellation.
- Security and retention controls.
- Runbooks and documentation.

**Exit criteria:**

- All P0 capabilities in [MVP_SCOPE.md](../product/MVP_SCOPE.md) are implemented and tested.
- MVP acceptance criteria are met.
- A real 60-second short is produced through the product and accepted by the founder.

**Dependencies:** Milestones 2, 3 and 4.

## Milestone 6 — Enterprise readiness

**Objective:** investigate and, if justified, implement multi-user, private and enterprise capabilities.

**Deliverables:**

- Multi-tenancy and isolation review.
- Private deployment and customer-managed inference design.
- Access control, SSO and SCIM investigation.
- Data retention and audit export design.
- Compliance investigation.
- Prioritised roadmap.

**Exit criteria:**

- Enterprise requirements are documented and prioritised.
- A decision is made on whether to pursue enterprise features and in what order.

**Dependencies:** Milestone 5 and customer or market input.

## Cross-milestone evidence

Every milestone produces:

- A progress entry in [PROGRESS.md](PROGRESS.md).
- Updated open questions.
- Updated risks where new risks appear.
- Commit history with the required identity.
- A milestone report linked from the progress entry.

No milestone is complete without evidence. Work performed without evidence is not counted.
