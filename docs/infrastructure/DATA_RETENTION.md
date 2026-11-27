# Data Retention

| Field | Value |
|---|---|
| Status | Foundation; periods are provisional pending policy and contracts |
| Last updated | 2026-11-27 |
| Related | [Security boundaries](../architecture/SECURITY_BOUNDARIES.md), [asset lifecycle](../architecture/ASSET_LIFECYCLE.md), [deployment](DEPLOYMENT.md) |

## 1. Purpose

Data retention policy balances cost, compliance, recoverability and user control. It defines how long different classes of data are kept, how deletion works and what survives deletion for audit and legal reasons.

Retention periods are provisional. They must be finalised with the founder, any customers and legal review before production launch.

## 2. Data classes

| Class | Examples | Sensitivity |
|---|---|---|
| Source media | Uploaded footage, voice samples, reference images | Confidential/Restricted |
| Generated media | Stills, motion clips, renders, exports | Internal/Confidential |
| Plans and metadata | Scripts, plate sheets, approvals, QC reports | Internal |
| Cost and usage | Cost entries, provider usage | Internal |
| Audit events | Approvals, exports, deletions, role changes | Internal/Restricted |
| Logs and traces | Application logs, traces, metrics | Internal |
| Model artifacts | Weights, caches | Internal |
| Consent records | Voice and likeness consent | Restricted |

## 3. Retention principles

- Retention is defined by data class, not by convenience.
- Deletion is a real operation, not a soft flag that leaves bytes in place.
- Audit and cost records may outlive media by policy or legal requirement.
- Retention is configurable per workspace where enterprise contracts require it.
- Legal holds override deletion.
- Backups follow the same retention intent, subject to backup mechanics.

## 4. Provisional retention periods

| Class | Active use | Archive | Delete | Notes |
|---|---|---|---|---|
| Source media | Project lifetime + 30 days | Optional cold storage | After retention or on request | Restricted data may require shorter periods |
| Generated media | Project lifetime + 30 days | Optional cold storage | After retention or on request | Superseded versions may archive sooner |
| Plans and metadata | Project lifetime + 90 days | Optional | After retention or on request | Needed for reproducibility |
| Cost and usage | 7 years (financial record) | N/A | Not deleted unless legally required | Financial retention may vary by jurisdiction |
| Audit events | 1 year minimum | Optional | Not deleted during legal hold | May be retained longer by policy |
| Logs | 30 days | Optional aggregated metrics | After retention | Debug detail is short-lived |
| Traces | 7–30 days | Optional | After retention | Sampled |
| Consent records | Duration of consent + 7 years | N/A | Not deleted during legal hold | Required for compliance |
| Model artifacts | Until deprecated + 90 days | Optional | After retention | Repro needs old versions |

These periods are provisional and must be reviewed before launch.

## 5. Deletion workflow

1. A deletion request is recorded with actor, scope and reason.
2. The system identifies all media bytes, derived artifacts, caches and references.
3. Media is deleted from object storage, including staging and derived prefixes.
4. Database rows are updated to reflect deletion; audit records remain.
5. Consent records are updated or revoked as appropriate.
6. A deletion report records what was removed and what could not be removed.
7. If a legal hold applies, deletion is blocked and the reason is recorded.

Deletion is asynchronous and idempotent. A failed deletion is retried and alerted.

## 6. Legal holds

- A legal hold blocks deletion of the specified data.
- Holds are recorded with scope, reason, requester and date.
- Holds are reviewed periodically and released when no longer required.
- Audit events record hold creation and release.

## 7. Backups

- Backups follow retention intent but may lag deletion due to backup mechanics.
- A deletion request triggers a best-effort purge from future backups.
- Backup retention periods are documented.
- Backup restoration is tested.

## 8. Customer-managed and enterprise

- Enterprise customers may define their own retention periods.
- Customer-managed storage places deletion responsibility partly with the customer.
- The platform records what it controls and what the customer controls.
- Data residency requirements may affect retention and deletion mechanics.

## 9. Orphan cleanup

- A sweeper compares object storage prefixes with database references.
- Unreferenced staging and derived objects are removed.
- Orphan cleanup is logged and auditable.
- A missing storage object referenced by the database is a critical incident.

## 10. Retention of telemetry

- Logs: short retention (baseline 30 days).
- Metrics: aggregated retention longer than raw logs.
- Traces: short retention with sampling.
- Audit: long retention per policy.
- Cost entries: retained as financial records.

## 11. Open questions

- Final retention periods for each data class.
- Whether archived media moves to cold storage automatically or by administrator action.
- How to verify deletion in provider-side storage.
- Whether customers can configure retention per project.
- Whether cost and audit records can ever be deleted under privacy requests.

Tracked in [OPEN_QUESTIONS.md](../project/OPEN_QUESTIONS.md).
