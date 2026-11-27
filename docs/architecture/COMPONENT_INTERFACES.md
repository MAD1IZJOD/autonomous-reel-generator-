# Component Interfaces

| Field | Value |
|---|---|
| Status | Foundation; interfaces are provisional until implementation |
| Last updated | 2026-11-27 |
| Related | [Component design](COMPONENT_DESIGN.md), [architecture review](ARCHITECTURE_REVIEW.md), [provider abstraction](../ai/PROVIDER_ABSTRACTION.md) |

## 1. Purpose

This document defines the contracts between components. It is the reference for implementation and for testing. Interfaces are expressed as ports and data contracts, not as framework code.

## 2. Common contracts

### 2.1 Identifiers

All identifiers are opaque strings. Recommended formats:

- Workspace, user, project: UUIDv7 or prefixed ULID.
- Run, job, asset version: prefixed ULID.
- Stage: dotted lowercase identifier (`voice.synthesize`).
- Shot: `P###` within a plate sheet version.

### 2.2 Timestamps and time

- All timestamps are UTC ISO-8601.
- Durations are in seconds as decimals.
- Frame counts use 25 FPS unless a render spec says otherwise.
- Leases use database time, not worker time.

### 2.3 Error envelope

```json
{
  "code": "PROV_RATE_LIMIT",
  "message": "The voice provider is temporarily rate limited.",
  "retryable": true,
  "correlation_id": "req_01J...",
  "details": {}
}
```

### 2.4 Idempotency

Every mutation accepts an `Idempotency-Key` header. The key is stored with the resulting entity. Replaying the same key returns the original result without re-executing side effects.

## 3. Core domain ports

### 3.1 `JobQueue`

```text
claim(worker, classes, lease) -> ClaimedJob | None
heartbeat(job_id, lease_token, extend) -> void
complete(job_id, lease_token, outcome) -> void
cancel(job_id, reason) -> void
```

### 3.2 `ProviderPort`

```text
execute(request, ctx) -> ProviderResult
reconcile(provider_job_id, ctx) -> ProviderResult | None
health() -> ProviderHealth
```

### 3.3 `RoutingPort`

```text
resolve(capability, requirements, ctx) -> RoutingDecision
```

### 3.4 `StoragePort`

```text
put_staging(key, bytes, metadata) -> StagingRef
promote(staging_ref, content_hash) -> AssetStorageRef
get_signed_url(storage_ref, ttl) -> URL
delete(storage_ref) -> void
```

### 3.5 `GpuPoolPort`

```text
acquire_session(pool, requirements) -> GpuSession
release_session(session_id, outcome) -> void
terminate_session(session_id) -> void
reconcile(session_id) -> SessionStatus
```

### 3.6 `Clock` and `IdGenerator`

Injected ports for deterministic testing. No component calls the system clock or UUID generator directly in domain code.

## 4. Data contracts

### 4.1 `Plate`

```json
{
  "id": "P001",
  "start_s": 0.0,
  "duration_s": 3.2,
  "layout": "presenter-left-proof-right",
  "a_roll": "string",
  "b_roll": "string",
  "motion_graphic": "string",
  "voiceover": "string",
  "sfx": [{"id": "marker-swipe", "at_s": 2.4}],
  "caption": "string",
  "visual_refs": ["asset:proof-dashboard-v3"],
  "approval_state": "draft"
}
```

### 4.2 `RoutingDecision`

```json
{
  "capability": "image.keyframe",
  "selected_model_id": "qwen-image-lightning",
  "selected_deployment_id": "dep_01J...",
  "fallback_chain": [],
  "rejected_candidates": [{"model_id": "...", "reason": "licence_unclear"}],
  "estimated_cost_usd": 0.12,
  "estimated_latency_s": 18,
  "quality_floor": "baseline",
  "policy_version": 3,
  "created_at": "2026-11-27T00:00:00Z"
}
```

### 4.3 `ProviderResult`

```json
{
  "status": "succeeded",
  "provider_job_id": "prov_123",
  "output_staging_refs": ["staging:..."],
  "usage": {"images": 1, "seconds": 0},
  "cost_usd": 0.04,
  "timing": {"queue_s": 2, "processing_s": 14, "upload_s": 1},
  "error": null
}
```

### 4.4 `QcReport`

```json
{
  "asset_version_id": "av_01J...",
  "metric": "mouth_opening_mean",
  "value": 0.27,
  "threshold": 0.28,
  "outcome": "warn",
  "configuration_id": "qc_cfg_01J...",
  "evidence_refs": ["qc:contact-sheet-01J..."]
}
```

### 4.5 `CostEntry`

```json
{
  "run_id": "run_01J...",
  "stage_id": "motion.generate",
  "shot_id": "P001",
  "provider": "runpod",
  "gpu_session_id": "gpu_01J...",
  "cost_type": "gpu_inference",
  "estimated_usd": 0.80,
  "actual_usd": 0.74,
  "currency": "USD"
}
```

## 5. Domain events

Events are recorded in the same transaction as the state change, or via an outbox.

| Event | Emitted when | Consumers |
|---|---|---|
| `RunCreated` | Run snapshot created | Observability, cost |
| `StageStarted` | Stage job claimed | Observability |
| `StageCompleted` | Stage validated | Orchestrator, cost |
| `StageFailed` | Stage failed | Orchestrator, alerts |
| `ApprovalRecorded` | Gate closed | Orchestrator, audit |
| `AssetVersionCreated` | New asset version committed | QC, render, audit |
| `ShotRegenerated` | Shot regeneration requested | Orchestrator, audit |
| `BudgetThresholdCrossed` | Budget limit reached | Dispatch pause, alerts |
| `GpuSessionOrphaned` | Session past idle window | Termination, alerts |
| `ExportCreated` | Export completed | Audit, billing |

## 6. API surface (provisional)

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/v1/projects` | Create project |
| `POST` | `/v1/projects/{id}/scripts` | Add script version |
| `POST` | `/v1/projects/{id}/plans` | Generate or create plate sheet |
| `PATCH` | `/v1/plans/{id}` | Edit draft plan |
| `POST` | `/v1/plans/{id}/approve` | Approve plan version |
| `POST` | `/v1/runs` | Create run from approved inputs |
| `GET` | `/v1/runs/{id}` | Run status, stages, gates, cost |
| `POST` | `/v1/runs/{id}/cancel` | Cancel run |
| `POST` | `/v1/runs/{id}/stages/{stage}/retry` | Retry stage |
| `POST` | `/v1/shots/{shot}/regenerate` | Regenerate shot |
| `GET` | `/v1/shots/{shot}/candidates` | Scored candidates and evidence |
| `POST` | `/v1/approvals` | Record approval or rejection |
| `GET` | `/v1/assets/{id}/versions/{v}/download-url` | Short-lived signed URL |
| `POST` | `/v1/runs/{id}/export` | Request export |
| `GET` | `/v1/runs/{id}/manifest` | Provenance and cost manifest |
| `GET` | `/v1/admin/models` | Registry administration |
| `GET` | `/v1/admin/costs` | Cost reporting |

Rules:

- All mutations require an idempotency key.
- List endpoints are cursor-paginated and workspace-scoped.
- Long operations return `202` with a resource reference.

## 7. Interface rules

1. Domain code depends only on ports, never on SDKs or frameworks.
2. Adapters are the only components that import provider or storage SDKs.
3. Every external call carries a deadline and a trace ID.
4. Every mutation is idempotent or carries an idempotency key.
5. Every state transition is validated by the domain layer.
6. Every artifact is validated before the job is marked successful.
7. Every interface change is recorded in this document and, if architectural, in an ADR.

## 8. Open questions

- Whether events are delivered synchronously or through an outbox.
- Whether the API is REST-only or also exposes a job-status stream.
- Whether provider adapters share a common HTTP client.
- Whether asset storage uses copy or direct upload to the final key.
- Whether QC adapters run in-process or as isolated workers.

Tracked in `docs/project/OPEN_QUESTIONS.md`.
