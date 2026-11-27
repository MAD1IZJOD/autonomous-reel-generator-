# Deployment

| Field | Value |
|---|---|
| Status | Foundation |
| Last updated | 2026-11-27 |
| Related | [Tech stack](../engineering/TECH_STACK.md), [security](SECURITY.md), [data retention](DATA_RETENTION.md), [GPU orchestration](GPU_ORCHESTRATION.md) |

## 1. Environments

| Environment | Purpose | Data |
|---|---|---|
| `development` | Local development | Synthetic or approved fixtures |
| `staging` | Integration and release validation | Sanitised or synthetic data |
| `production` | Real workloads | Real projects and media |

Rules:

- Production credentials are never used in development or staging.
- Staging mirrors production topology as closely as practical.
- Configuration is environment-specific and validated at startup.
- Feature flags control incomplete features.

## 2. Initial production topology

- One Linux host or managed container service for the control plane and CPU workers.
- Managed PostgreSQL where available; self-hosted PostgreSQL is acceptable for a controlled deployment.
- S3-compatible object storage.
- GPU inference on RunPod through the provider adapter.
- TLS termination at the edge.
- An observability backend for logs, metrics and traces.

This is a deliberate simplification for the first deployment. It is not an enterprise topology.

## 3. Container images

- Application images are built from pinned base images.
- Images are scanned for vulnerabilities before release.
- GPU model server images are built and versioned separately.
- Images are referenced by digest in production, not by tag.
- Build artifacts and secrets are never baked into images.

## 4. Configuration and secrets

- All configuration comes from environment variables or a secret manager.
- `.env.example` documents names and safe defaults.
- Secrets are injected at runtime.
- Credential rotation does not require a code change.
- Per-environment values are stored in the deployment platform, not in Git.

## 5. Database migrations

- Migrations run as a separate deploy step, not implicitly on application startup in production.
- Migrations are tested against a production-like dataset.
- Backward-compatible migrations are preferred so rollback is possible.
- Destructive migrations require a documented plan and approval.
- A failed migration stops the deployment.

## 6. Deployment process

1. Merge to `main` after review and CI.
2. Build and scan images.
3. Run database migrations in staging.
4. Deploy to staging and run smoke tests.
5. Run end-to-end tests against staging.
6. Promote the same image to production.
7. Run production smoke tests.
8. Monitor error rates, queue depth and cost.

The same artifact is promoted through environments. Rebuilding for production is not allowed.

## 7. Rollback

- Application rollback uses the previous image digest.
- Database rollback is only possible for backward-compatible migrations; otherwise a forward fix is required.
- Object storage changes are not rolled back automatically; assets are versioned.
- Rollback decisions are recorded with the reason and impact.

## 8. GPU deployment

- GPU pools are configured, not hardcoded.
- Model server images are pinned by digest.
- Weight caches are versioned and verified by hash.
- A new model server is smoke-tested before it receives production traffic.
- Pool configuration changes are audited.

## 9. Backups

- PostgreSQL is backed up on a schedule with point-in-time recovery where available.
- Object storage uses versioning and lifecycle policies.
- Backup restoration is tested at least once before release and periodically after.
- Backups are encrypted and access-controlled.
- Backup retention follows [DATA_RETENTION.md](DATA_RETENTION.md).

## 10. Disaster recovery

- Recovery time and recovery point objectives are defined before production launch.
- A documented runbook covers database restore, storage restore and re-running jobs.
- GPU sessions are not part of the recovery state; they are recreated by the orchestration layer.
- Audit and cost records are prioritized in recovery.
- A post-incident review follows any significant outage.

## 11. Enterprise and private deployment (future)

- Customer-managed PostgreSQL and object storage.
- Model servers inside the customer network.
- SSO and SCIM.
- Per-tenant encryption keys.
- Data residency controls.
- Air-gapped deployment support.
- Customer-managed GPU pools.

These are investigated in Milestone 6 and are not part of the MVP. The architecture is designed to accommodate them through configuration and adapter boundaries.

## 12. Operational runbooks (to be written)

- Deploy and rollback.
- Database migration failure.
- GPU session orphan.
- Provider outage.
- Budget breach.
- Data deletion request.
- Backup restore.
- Security incident containment.

Runbooks are part of the MVP operational bar and must be exercised before release.

## 13. Open questions

- Whether to use managed PostgreSQL or self-host.
- Whether to use a managed container service or a single host.
- Whether GPU images are built in this repository or a separate one.
- Whether to support blue/green deployments in the MVP.
- Whether enterprise deployments use the same image or a separate build.

Tracked in [OPEN_QUESTIONS.md](../project/OPEN_QUESTIONS.md).
