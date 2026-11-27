# Failure Recovery

| Field | Value |
|---|---|
| Status | Foundation |
| Last updated | 2026-11-27 |
| Related | [Error handling](../engineering/ERROR_HANDLING.md), [job lifecycle](JOB_LIFECYCLE.md), [GPU orchestration](../infrastructure/GPU_ORCHESTRATION.md), [observability](../engineering/OBSERVABILITY.md) |

## 1. Purpose

Failure recovery is a product capability, not an afterthought. The pipeline is long, expensive and distributed across providers and GPUs. Every failure mode must have a defined detection, containment, recovery and verification path.

## 2. Recovery principles

- Fail visibly and cheaply.
- Preserve partial work as evidence; do not hide it.
- Reuse completed, validated work on retry.
- Never mark a failed or partial run as successful.
- Terminate billable resources before investigating.
- Record cost impact for every failure.
- Prefer automatic recovery for transient failures and human escalation for permanent ones.

## 3. Failure categories and recovery

### 3.1 Worker process crash

| Step | Action |
|---|---|
| Detection | Heartbeat expiry |
| Automatic | Lease expires; job becomes `Lost`, then reclaimable |
| Recovery | New worker claims the job and resumes from the last checkpoint |
| Verification | Attempt count increments; no duplicate completion due to lease token |
| Cost | No new cost unless work is repeated |

### 3.2 GPU pod preemption or termination

| Step | Action |
|---|---|
| Detection | Health check failure or provider status change |
| Automatic | Attempt fails with classified error; completed shots remain valid |
| Recovery | Reconcile provider state; provision a new session; retry failed jobs |
| Verification | Cost entries record the failed attempt and the replacement session |
| Cost | Failed attempt cost is recorded as waste |

### 3.3 Model server hang

| Step | Action |
|---|---|
| Detection | Step timeout or failed health check |
| Automatic | Terminate the session; fail the attempt |
| Recovery | Provision a new session; retry the job |
| Verification | Session termination is verified against provider state |
| Cost | Idle or hung time is attributed to the session |

### 3.4 Provider outage or rate limit

| Step | Action |
|---|---|
| Detection | Provider error or timeout |
| Automatic | Backoff with jitter; retry within policy |
| Recovery | Fallback only if policy allows and quality is preserved; otherwise pause the capability |
| Verification | Provider call records and cost entries are stored |
| Cost | Rate-limited calls are not billed unless the provider charges |

### 3.5 Database unavailability

| Step | Action |
|---|---|
| Detection | Connection failure |
| Containment | Workers stop claiming; API returns a clear degraded state |
| Recovery | Resume after database recovery; leases expire safely |
| Verification | No duplicate completion due to lease tokens |
| Cost | No GPU dispatch while the database is down |

### 3.6 Object storage unavailability

| Step | Action |
|---|---|
| Detection | Upload or download failure |
| Containment | Preflight fails before GPU provisioning |
| Recovery | Retry after storage recovery; staging objects are reconciled |
| Verification | Hash verification before promotion |
| Cost | No paid inference starts without storage |

### 3.7 Budget exhaustion

| Step | Action |
|---|---|
| Detection | Budget threshold crossed |
| Containment | New GPU dispatch pauses; running work follows policy |
| Recovery | Administrator raises the budget or waits for reset |
| Verification | Pause and resume are audit events |
| Cost | Spend stops at the configured limit |

### 3.8 Lost GPU session (orphan)

| Step | Action |
|---|---|
| Detection | Watchdog detects no active lease past the idle window |
| Containment | Attempt graceful termination |
| Recovery | If termination fails, page an administrator with the provider session ID |
| Verification | Cost impact is attributed to the originating run as waste |
| Cost | Orphan cost is visible, not hidden |

### 3.9 Cancelled run

| Step | Action |
|---|---|
| Detection | User or policy cancellation |
| Containment | Stop new dispatch; mark in-flight jobs for cancellation |
| Recovery | In-flight jobs reach a safe checkpoint or are terminated at hard timeout |
| Verification | Cancelled jobs cannot transition to `Succeeded` |
| Cost | Already-spent cost is not erased |

### 3.10 Failed stage with valid checkpoint

| Step | Action |
|---|---|
| Detection | Stage failure |
| Recovery | Retry the stage from the checkpoint; reuse validated artifacts by idempotency key |
| Verification | Only failed work is repeated |
| Cost | Completed paid work is not duplicated |

### 3.11 Timing change after motion generation

| Step | Action |
|---|---|
| Detection | Plate timing changes after motion assets exist |
| Containment | Affected motion assets are marked stale |
| Recovery | Regenerate affected shots; preserve unaffected shots |
| Verification | Stale assets cannot be used in the final render |
| Cost | Only affected shots are regenerated |

### 3.12 Provider returns success without artifact

| Step | Action |
|---|---|
| Detection | Missing output after provider success |
| Containment | Treat as failure; do not create an empty asset |
| Recovery | Retry or reconcile; escalate if repeated |
| Verification | Job remains failed until a valid artifact exists |
| Cost | Provider charge is recorded if billed |

## 4. Recovery verification checklist

After any recovery, verify:

- Job state is consistent with artifact state.
- No duplicate provider charges occurred.
- Cost entries match provider billing where possible.
- QC reports are attached to the correct asset versions.
- Run status reflects actual progress.
- Orphaned GPU sessions are terminated.
- Audit events record the failure and recovery.

## 5. Runbooks to be written

- Worker crash recovery.
- GPU session orphan.
- Provider outage.
- Budget breach.
- Database failover.
- Object storage outage.
- Data deletion request.
- Backup restore.
- Security incident containment.

Runbooks are part of the MVP operational bar and must be exercised before release.

## 6. Open questions

- Whether failed jobs should auto-retry after a configuration change.
- How long to retain dead-letter jobs.
- Whether partial export is allowed when non-blocking shots fail.
- How to handle provider success without artifact in automated recovery.

Tracked in `docs/project/OPEN_QUESTIONS.md`.
