# ADR-004: Storage for metadata and media

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-11-27 |
| Deciders | Engineering (Madhavan), Product (Avinash Pandit) |
| Related | [System architecture](../SYSTEM_ARCHITECTURE.md), [asset lifecycle](../ASSET_LIFECYCLE.md), [data retention](../../infrastructure/DATA_RETENTION.md) |

## 1. Context

The system manages two very different kinds of data: relational metadata (projects, runs, jobs, approvals, cost, audit) and large immutable media objects (audio, video, images, evidence). Media can be gigabytes per run and must support signed access, versioning and lifecycle policies. The first deployment is a single host, but enterprise customers may require customer-managed storage.

## 2. Decision

Use **PostgreSQL for metadata and S3-compatible object storage for media**.

- PostgreSQL stores metadata, job state, cost, audit and the registry.
- Object storage stores source and generated media, QC evidence, renders and exports.
- Media is never stored in PostgreSQL.
- Asset versions are immutable; storage keys are content-addressed or run-scoped.
- Access is through short-lived signed URLs issued after authorization.

## 3. Alternatives considered

### 3.1 Local filesystem

Rejected as the primary. It complicates backup, scaling, signed access and multi-host deployment. A local filesystem may be used as a cache on workers and GPU pods, but never as the source of truth.

### 3.2 Database blobs

Rejected. Storing large media in PostgreSQL bloats the database, slows backups and complicates replication and retention. It also makes signed URL access awkward.

### 3.3 Git LFS

Rejected. Generated media, private footage and model artifacts do not belong in Git. Git history and access controls are the wrong tools for this data.

### 3.4 Proprietary storage SDK

Rejected. An S3-compatible API keeps the product portable across MinIO, AWS S3, Cloudflare R2, Backblaze B2 and customer-managed stores.

## 4. Consequences

Positive:

- Clear separation of relational and object data.
- Durable, cheap storage with lifecycle policies.
- Signed URLs provide controlled access without proxying large files through the API.
- Content-addressed keys support integrity checks and deduplication.
- Portability across providers.

Negative:

- Object storage is not transactional with PostgreSQL; promotion and reconciliation logic is required.
- Egress costs must be monitored.
- Eventual consistency behaviours must be handled in upload validation.
- Backup and restore spans two systems.

Mitigations:

- Uploads use staging keys and content-hash verification before promotion.
- An orphan sweeper removes unreferenced objects.
- Database rows never point to unverified bytes.
- Backup and restore procedures are documented and tested.

## 5. Reversal criteria

Reconsider only if a deployment environment cannot provide an S3-compatible API and the cost of operating one (for example, MinIO) is unacceptable. Customer-managed storage requirements are handled through configuration, not by changing this decision.

## 6. Related documents

- [Asset lifecycle](../ASSET_LIFECYCLE.md)
- [Data retention](../../infrastructure/DATA_RETENTION.md)
- [Security boundaries](../SECURITY_BOUNDARIES.md)
- [Cost optimization](../../infrastructure/COST_OPTIMIZATION.md)
