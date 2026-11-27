# ADR-002: Asynchronous orchestration and job queue

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-11-27 |
| Deciders | Engineering (Madhavan), Product (Avinash Pandit) |
| Related | [System architecture](../SYSTEM_ARCHITECTURE.md), [job lifecycle](../JOB_LIFECYCLE.md), [component design](../COMPONENT_DESIGN.md) |

## 1. Context

The pipeline contains work that takes seconds to minutes: GPU inference, model loading, rendering, QC. Jobs can fail, be preempted, time out, wait for human approval or need shot-level retry. The orchestration layer must survive process restarts, avoid duplicate charges, support cancellation and provide observable progress.

We need to choose how work is queued and orchestrated.

## 2. Decision

Use **PostgreSQL as both the source of truth and the initial queue**, with workers claiming jobs using `SELECT ... FOR UPDATE SKIP LOCKED`.

Key properties:

- Enqueue happens in the same transaction as the domain state change.
- Jobs carry leases, heartbeats, attempts and idempotency keys.
- Approval gates are represented as job/stage states, not external signals.
- A broker may be added later for dispatch latency, but PostgreSQL remains authoritative for job state.

## 3. Alternatives considered

### 3.1 Temporal

Rejected for the MVP. Temporal provides durable workflows, timers and retries, but it adds a separate cluster, worker model, operational burden and a second source of truth. The team is small and the first deployment is a single host. The approval and cost requirements are expressible in a relational model. Temporal remains a candidate if workflow complexity or scale later justifies it.

### 3.2 Celery with Redis or RabbitMQ

Rejected as the primary. Celery is familiar, but it introduces a separate broker and result backend, weakens transactional enqueue (dual-write risk) and makes job state harder to query and audit. It may be reconsidered as a dispatch layer if polling latency becomes a bottleneck.

### 3.3 Cloud-managed queue (SQS, Pub/Sub)

Rejected for the initial architecture. It would couple the product to a cloud provider and complicate local development and private deployment. The abstraction can be revisited for enterprise or multi-region deployments.

### 3.4 In-process background tasks

Rejected. They do not survive process restarts, cannot be observed centrally and cannot be recovered after a crash. They are suitable only for trivial, non-critical work.

## 4. Consequences

Positive:

- Transactional enqueue eliminates the dual-write problem between domain state and queue.
- Job state, cost, audit and approval data share one database and one transaction model.
- Easier local development: one PostgreSQL instance.
- `SKIP LOCKED` supports concurrent workers without broker infrastructure.
- Job history and metrics are directly queryable.

Negative:

- Polling introduces dispatch latency, mitigated by short poll intervals and partitioned queues.
- High throughput may require partitioning or a broker.
- Lease and heartbeat logic must be implemented correctly.
- Long-running jobs require careful timeout and cancellation handling.

Mitigations:

- Partition queues by job class and capability.
- Use leases with heartbeats and compare-and-set completion.
- Keep the queue interface abstract so a broker can be added without changing domain code.
- Measure queue latency and throughput before adding infrastructure.

## 5. Reversal criteria

Reconsider when measured queue latency or throughput prevents meeting stage or cost targets, or when workflow complexity makes the relational model unmaintainable. Any change must preserve the job state schema and audit semantics, or include a migration plan.

## 6. Related documents

- [Job lifecycle](../JOB_LIFECYCLE.md)
- [Component design](../COMPONENT_DESIGN.md)
- [Error handling](../../engineering/ERROR_HANDLING.md)
- [Observability](../../engineering/OBSERVABILITY.md)
