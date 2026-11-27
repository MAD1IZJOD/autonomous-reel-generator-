# Error Handling

| Field | Value |
|---|---|
| Status | Foundation |
| Last updated | 2026-11-27 |
| Related | [Job lifecycle](../architecture/JOB_LIFECYCLE.md), [component design](../architecture/COMPONENT_DESIGN.md), [observability](OBSERVABILITY.md) |

## 1. Principles

- Errors are classified, not swallowed.
- A failure must be visible in the UI, logs and metrics with enough context to act.
- Retryable and non-retryable failures are distinguished by code, not by string matching.
- Partial work is preserved as evidence; it is not discarded or hidden.
- The system prefers failing cheaply over retrying into a larger bill.
- No stage is marked successful because its process exited cleanly; success requires a validated artifact.

## 2. Error taxonomy

| Category | Code prefix | Retryable | Examples |
|---|---|---|---|
| Validation | `VAL_` | No | Invalid plate, missing field, bad timing, unsupported media |
| Authorization | `AUTHZ_` | No | Insufficient role, cross-workspace access, denied egress |
| Authentication | `AUTHN_` | No | Invalid credentials, expired session |
| Policy / licence | `POLICY_` | No | Unlicensed model, denied provider, missing consent |
| Configuration | `CONFIG_` | No | Missing setting, unknown provider, bad pool config |
| Provider | `PROV_` | Sometimes | Rate limit, timeout, 5xx, invalid request |
| GPU infrastructure | `GPU_` | Sometimes | Provisioning failure, preemption, OOM, health check failure |
| Storage | `STOR_` | Sometimes | Upload failure, hash mismatch, missing object |
| Media processing | `MEDIA_` | Sometimes | FFmpeg failure, corrupt input, unsupported codec |
| Quality gate | `QC_` | No (job succeeds, gate fails) | Metric below threshold, failed human review |
| Internal | `INT_` | Sometimes | Bug, unexpected exception, invariant violation |
| Budget | `BUDGET_` | No until reset | Threshold exceeded, insufficient headroom |

The taxonomy is extensible, but new codes must be documented here.

## 3. Error record

Every failure stores:

- error code and category
- human-readable message safe for the UI
- technical detail for logs (no secrets or media)
- retryable flag
- recommended action (retry, fix input, contact admin, wait)
- provider error code and request identifier where applicable
- job, attempt, run, stage and shot identifiers
- trace ID
- timestamp

## 4. Propagation rules

- Domain code raises typed domain errors. It does not know HTTP status codes.
- Application services translate domain errors into use-case results or typed exceptions.
- Provider adapters translate SDK and HTTP errors into the application error taxonomy.
- HTTP handlers map typed errors to status codes and the standard error envelope.
- Workers map errors to job attempt outcomes and retry decisions.
- UI maps error codes to actionable messages and next steps.

No layer may catch a broad exception and continue as if the operation succeeded. A catch-all at a boundary must rethrow or record a failure.

## 5. Retryability

Retryability is determined by error code and job class policy, not by the worker's opinion.

Retryable examples:

- Provider rate limit or transient 5xx.
- GPU preemption.
- Network timeout to object storage.
- Lease loss followed by reclamation.

Non-retryable examples:

- Invalid plate structure.
- Missing licence or consent.
- Unsupported media format.
- Budget exceeded.
- QC failure that requires human judgement.

A retry must not repeat completed paid work. It checks for an existing artifact by idempotency key and for an existing provider job before creating a new one.

## 6. Partial failure and checkpoints

- A stage with many shots can have some shots fail while others succeed.
- Failed shots are marked failed with reasons; successful shots remain usable.
- A stage that requires all shots cannot complete until the failures are resolved or the shots are removed by policy.
- Checkpoints are recorded after each validated shot so a retry does not repeat successful work.
- Partial artifacts from a failed attempt are quarantined, not published as candidates.
- A cancelled job stops new work but does not erase completed artifacts or cost entries.

## 7. Provider error handling

- Provider errors are normalized into the taxonomy with the original code preserved in logs.
- Rate limits trigger backoff with jitter and respect provider retry headers.
- Timeouts terminate the request and classify the failure; they are not retried blindly.
- A provider that returns success without an artifact is treated as a failure.
- Provider outages mark the capability as degraded; fallback occurs only if policy allows and quality is preserved.
- Provider job identifiers are stored for reconciliation and support.

## 8. GPU error handling

- OOM is classified as a GPU failure and may trigger a retry on a larger pool if policy allows.
- A hung model server is detected by step timeout and health check; the session is terminated.
- Preemption fails the attempt and creates a new session; completed shots are reused.
- Provisioning failure fails preflight or the attempt; it does not silently fall back to a more expensive pool.
- An unrecoverable session is reconciled against provider state before replacement.

## 9. Storage and media errors

- Upload hash mismatch quarantines the object and fails the job.
- A missing storage object referenced by the database is a critical incident; the asset is not served as complete.
- FFmpeg failures include the command, exit code and a bounded tail of stderr in logs, never in the UI.
- Corrupt inputs are detected in preflight before GPU provisioning.

## 10. User-facing messages

- Messages state what happened, why it matters and what the user can do next.
- They do not expose stack traces, provider internals or secrets.
- They include a correlation ID for support.
- A blocking gate explains which gate, who can resolve it and how.
- Cost-related failures state whether money was spent and whether it is recoverable.

## 11. Dead-letter and escalation

- Jobs that exhaust attempts or hit non-retryable errors enter dead-letter.
- Dead-letter jobs remain queryable with full attempt history.
- Operators can retry after fixing configuration or inputs.
- Repeated failures of the same class trigger alerts.
- Budget breaches pause dispatch and notify an administrator.

## 12. Alerting

Alerts are defined for:

- Queue depth or job latency above threshold.
- GPU session orphaned or termination failed.
- Budget threshold crossed.
- Provider error rate above threshold.
- Dead-letter growth.
- Missing storage object.
- Audit or consent violation.
- Backup failure.

Alerts include run and job identifiers where applicable. Alert fatigue is managed by severity and deduplication.

## 13. Invariant violations

An invariant violation is an `INT_` error and is treated as a bug, not a user error. It should:

- fail the affected job,
- be logged with full context (redacted),
- open an issue or alert,
- not be retried automatically unless the retry policy explicitly allows it.

## 14. Open questions

- Whether to expose provider retry counts to users.
- Whether a failed job should auto-retry after a configuration change.
- How long to retain dead-letter jobs.
- Whether to support partial export when non-blocking shots fail.

Tracked in [OPEN_QUESTIONS.md](../project/OPEN_QUESTIONS.md).
