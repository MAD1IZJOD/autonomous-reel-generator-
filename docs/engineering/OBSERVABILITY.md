# Observability

| Field | Value |
|---|---|
| Status | Foundation |
| Last updated | 2026-11-27 |
| Related | [Error handling](ERROR_HANDLING.md), [job lifecycle](../architecture/JOB_LIFECYCLE.md), [cost optimization](../infrastructure/COST_OPTIMIZATION.md) |

## 1. Principles

- Observability is a product feature, not an afterthought. Operators and administrators need it to control cost and quality.
- Every run, stage, shot, job, provider call and GPU session is traceable by correlation ID.
- Metrics are derived from structured events, not log scraping.
- Logs never contain secrets, media, full scripts, tokens or presigned URLs.
- Cost and quality are observed with the same rigour as latency and errors.

## 2. Correlation identifiers

Every request and job carries:

- `request_id` for the originating API request.
- `trace_id` for the distributed trace.
- `run_id`, `stage_id`, `shot_id` where applicable.
- `job_id`, `attempt_id`, `lease_token`.
- `workspace_id`.

These identifiers are propagated through HTTP headers, job records, provider calls, worker logs and GPU sessions. They are the primary debugging tool.

## 3. Logging

- Structured JSON to stdout.
- One event per line with timestamp, level, service, component, correlation IDs and message.
- Log levels: debug, info, warn, error.
- Redact secrets, media, scripts, tokens and presigned URLs.
- Include bounded, relevant payloads (error codes, counts, durations, model versions) but not raw inputs.
- Workers log lifecycle events: claim, start, heartbeat, provider call, upload, validation, completion, failure.
- GPU agents log provisioning, model load, warm-up, job execution, idle and termination.

## 4. Tracing

- OpenTelemetry spans for API requests, use cases, repository calls, provider calls, GPU operations, render steps and QC.
- A trace for one run links the API request, job, provider call, GPU session and render.
- Span attributes include model version, provider, GPU type, shot ID and cost estimate.
- Sampling is configured by environment; errors and slow operations are always sampled.
- Trace IDs are shown in the UI for support.

## 5. Metrics

### 5.1 Application metrics

- Request rate, latency and error rate by endpoint.
- Job counts and latency by class and state.
- Queue depth and age of oldest queued job.
- Lease expirations and reclaims.
- Approval wait time.
- Stage success/failure rates.
- Regeneration counts.

### 5.2 GPU metrics

- Sessions created, terminated and orphaned.
- Provisioning time, model load time, warm-up time, inference time, upload time.
- GPU utilization and memory.
- Idle time before shutdown.
- Pool capacity and saturation.
- Cost per session and per job.

### 5.3 Quality metrics

- Voice similarity distribution.
- Whisper CER distribution.
- Mouth-opening metrics distribution.
- QC pass/fail/warn counts by metric.
- Human override counts and reasons.
- Candidate counts per shot.

### 5.4 Cost metrics

- Estimated and actual cost per run, stage, shot, provider and GPU session.
- Cost per accepted output.
- Budget utilization and pause events.
- Waste: orphaned sessions, failed paid attempts, redundant regenerations.

## 6. Dashboards

Minimum dashboards:

1. **Run overview:** active runs, stage progress, blocked gates, failures.
2. **Queue and workers:** depth, latency, worker health, claim rates.
3. **GPU operations:** sessions, utilization, load times, idle time, cost.
4. **Cost:** per run, per provider, budget utilization, trends.
5. **Quality:** metric distributions, pass rates, overrides.
6. **Errors:** error codes, retry rates, dead-letter growth.

Dashboards are for operators and administrators, not end-user marketing.

## 7. Alerts

Alerts are defined in [ERROR_HANDLING.md](ERROR_HANDLING.md). Observability provides the data and routing:

- Severity levels: info, warning, critical.
- Deduplication and grouping by run or provider.
- Alert payloads include correlation IDs and links to dashboards.
- Cost and budget alerts are routed to administrators.
- Quality degradation alerts are routed to the product owner.

## 8. Cost instrumentation

Cost is a first-class signal and requires explicit instrumentation:

- Every provider call records usage (characters, seconds, images, tokens) and estimated cost.
- Every GPU session records provisioning, model load, inference and teardown durations and cost.
- Cost entries are created at dispatch (estimate) and settled at completion (actual).
- Failed paid attempts create cost entries when the provider charges.
- Budget reservations prevent concurrent overspend.
- Reconciliation jobs compare ledger entries with provider billing exports and flag discrepancies.

Cost metrics feed the dashboards and the run manifest. A run's cost must be queryable without log archaeology.

## 9. Quality instrumentation

- QC reports store raw metric values, thresholds and decisions.
- Metric definitions and versions are recorded so a threshold change does not invalidate historical comparisons.
- Human review outcomes are recorded with reasons.
- Candidate scores are stored, not just the selected candidate.
- Quality trends are visible per model version, provider and hardware.

## 10. Audit integration

Audit events are part of observability for sensitive actions. They are:

- append-only,
- queryable by actor, action, target and time,
- retained according to policy even when media is deleted,
- linked to trace IDs where applicable.

Audit is not a substitute for application logs; it records decisions and access, not debugging detail.

## 11. Data privacy in telemetry

- No raw media, full scripts, voice samples or footage in logs or traces.
- No secrets, tokens, credentials or presigned URLs.
- No personal data beyond what is needed for audit and authorization.
- Error messages are sanitized before being sent to external error trackers.
- Telemetry exports to third parties require a policy decision and are workspace-configurable.

## 12. Retention of telemetry

- Logs: short retention (baseline 30 days) unless needed for incident review.
- Metrics: aggregated retention longer than raw logs.
- Traces: short retention with sampling.
- Audit: long retention per policy.
- Cost entries: retained as financial records.

Retention is configurable per environment and workspace; see [DATA_RETENTION.md](../infrastructure/DATA_RETENTION.md).

## 13. Open questions

- Whether to self-host the observability stack or use a managed service.
- Whether to store telemetry in the same PostgreSQL instance or a separate one.
- How to handle telemetry in customer-managed enterprise deployments.
- Whether to expose cost dashboards to non-admin reviewers.
- Whether to record prompt text for debugging under a privacy policy.

Tracked in [OPEN_QUESTIONS.md](../project/OPEN_QUESTIONS.md).
