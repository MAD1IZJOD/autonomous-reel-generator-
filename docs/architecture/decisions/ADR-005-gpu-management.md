# ADR-005: GPU infrastructure management

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-11-27 |
| Deciders | Engineering (Madhavan), Product (Avinash Pandit) |
| Related | [GPU orchestration](../../infrastructure/GPU_ORCHESTRATION.md), [cost optimization](../../infrastructure/COST_OPTIMIZATION.md), [system architecture](../SYSTEM_ARCHITECTURE.md) |

## 1. Context

The existing workflow provisions a fresh RunPod pod per session, downloads roughly 75 GB of models, runs inference, then terminates the pod. A tested 60-second short cost about $9.06 including setup and tests; a repeat in the same style cost about $1. The founder's observation is that most GPU waste comes from model loading, not inference.

Measured constraints include:

- L40 48 GB for image and video workloads.
- A100 SXM 80 GB for the tested production InfiniteTalk configuration.
- InfiniteTalk 720p OOM on L40; 480p production configuration roughly 368–425 seconds per 4-second burst plus roughly 465 seconds of model loading.
- Pod setup roughly 12 minutes.

These are observations from one environment and must be reproduced before infrastructure commitments.

## 2. Decision

Manage GPU capacity as **pools of resident model servers** with a provider abstraction:

- Pools are defined by capability and hardware requirement, not by individual model.
- Model servers stay warm and batch compatible jobs.
- Inputs are prefvalidated on CPU before provisioning.
- Idle sessions shut down after a configurable window (baseline 5–10 minutes).
- Model weights are cached on a persistent volume or baked into the image; repeated 75 GB downloads are treated as an incident.
- Every session has a cost meter, lease, heartbeat and termination verification.
- RunPod is the first provider adapter; the interface allows others.

## 3. Alternatives considered

### 3.1 Fresh pod per job (current workflow)

Rejected as the default. It recreates the dominant waste: provisioning and model loading. It may still be used for isolated experiments or capabilities with very low demand.

### 3.2 Serverless GPU

Rejected for the baseline. It can reduce idle cost but does not solve model loading, and its pricing and cold-start behaviour must be measured. It remains a candidate for burst capacity.

### 3.3 Self-hosted Kubernetes GPU cluster

Rejected for the MVP. It adds cluster operations before demand and utilization are known. It is a plausible enterprise option later.

### 3.4 One always-on GPU box

Rejected. It would remove provisioning waste but would idle expensively and would not match the variable, capability-specific hardware requirements (L40 for image/video, A100 for InfiniteTalk).

## 4. Consequences

Positive:

- Model loading cost is amortized across many jobs.
- Batching and warm pools directly target the observed waste.
- Preflight prevents expensive failures.
- Cost and timing are attributable per session and job.
- Provider choice is not hardcoded.

Negative:

- Resident pools incur idle cost if shutdown fails.
- Session lifecycle, reconciliation and orphan detection add complexity.
- Model server health and versioning must be managed.
- Hardware claims are provisional until reproduced.

Mitigations:

- Idle shutdown with a watchdog independent of job state.
- Budget reservations and pause thresholds.
- Termination verification and paging on failure.
- Measured reproduction before scaling commitments.
- Clear distinction between tested, rejected, proposed and untested models.

## 5. Reversal criteria

Reconsider if a provider offers better economics for the actual workload, if utilization is too low to justify warm pools, or if model loading becomes negligible through other means. Any change must be supported by measured cost per accepted output, not by pricing pages alone.

## 6. Related documents

- [GPU orchestration](../../infrastructure/GPU_ORCHESTRATION.md)
- [Cost optimization](../../infrastructure/COST_OPTIMIZATION.md)
- [Model registry](../../ai/MODEL_REGISTRY.md)
- [Model evaluation](../../ai/MODEL_EVALUATION.md)
- [Job lifecycle](../JOB_LIFECYCLE.md)
