# Infrastructure Security

| Field | Value |
|---|---|
| Status | Foundation |
| Last updated | 2026-11-27 |
| Related | [Security boundaries](../architecture/SECURITY_BOUNDARIES.md), [deployment](DEPLOYMENT.md), [data retention](DATA_RETENTION.md) |

## 1. Network

- The control plane is reachable only through TLS.
- Database and object storage are not exposed to the public internet.
- GPU pods have restricted egress to approved endpoints.
- Administrative access uses a VPN or bastion where possible.
- Network segmentation separates application, data and GPU execution zones.
- Firewall rules are documented and reviewed.

## 2. Host and container security

- Hosts run a minimal, patched operating system.
- Containers run as non-root where possible.
- Images are scanned for vulnerabilities before release.
- Only required ports are exposed.
- Read-only root filesystems are used where practical.
- Resource limits are set for CPU, memory and GPU.
- Secrets are not baked into images.

## 3. Secrets management

- Secrets are stored in a secret manager or platform secret store.
- `.env` is local-only and ignored by Git.
- Credential rotation is supported without redeployment.
- Access to secrets is audited where supported.
- A leaked credential is revoked first, then reported.
- CI includes secret scanning.

## 4. Data protection

- Data is encrypted in transit with TLS 1.2 or higher.
- Data at rest is encrypted by the storage provider.
- Restricted data may require application-level encryption.
- Backups are encrypted and access-controlled.
- Presigned URLs are short-lived and scoped.
- Logs and traces exclude secrets and media.

## 5. Object storage security

- Buckets are private by default.
- Public access is blocked unless explicitly required for a product feature.
- Signed URLs are issued only after authorization.
- Uploads are validated for type and size.
- Lifecycle policies handle archival and deletion.
- Bucket policies are reviewed and version-controlled.

## 6. Database security

- Database credentials are rotated and scoped.
- Least-privilege database users are used for application and migration roles.
- Network access is restricted to application hosts.
- Audit and cost tables are append-only at the application level.
- Backups are encrypted and tested.

## 7. GPU pod security

- Pods run pinned images and model weights.
- Pods have no access to the database or secret store.
- Inputs are fetched through scoped, short-lived credentials.
- Outputs are uploaded to staging and validated.
- Outbound network access is restricted.
- Failed or orphaned pods are terminated and reconciled.
- Pod termination is verified against provider state.

## 8. Provider and egress security

- Provider egress is deny-by-default.
- Workspace policy controls allowed providers and data classes.
- Provider credentials are scoped and rotatable.
- Provider terms and data handling are recorded.
- Data sent to providers is the minimum required.

## 9. Vulnerability management

- Dependencies are scanned in CI.
- Container images are scanned before release.
- Model weights and images are verified by hash.
- Security patches are applied within a defined window.
- Third-party components are reviewed before inclusion.
- Security issues are reported privately.

## 10. Incident response

- Detection through alerts, audit review and user reports.
- Triage classifies impact on confidentiality, integrity, availability and cost.
- Containment includes revoking credentials, disabling providers, pausing dispatch and terminating GPU sessions.
- Eradication includes patching, rotating secrets and removing compromised artifacts.
- Recovery includes restoring from backup and re-running affected jobs.
- Post-incident review records timeline, root cause, cost impact and corrective actions.
- Security incidents are not handled through public issues.

## 11. Compliance posture (provisional)

The MVP does not claim compliance with any specific framework. Enterprise requirements such as SOC 2, ISO 27001, GDPR or HIPAA are investigated in Milestone 6. The architecture supports the necessary controls (audit, retention, encryption, access control, data residency) but they are not certified.

## 12. Security acceptance

Security acceptance criteria are defined in [ACCEPTANCE_CRITERIA.md](../product/ACCEPTANCE_CRITERIA.md). No production deployment is permitted without:

- secret scan passing,
- private storage verified,
- provider egress tested against policy,
- authorization tests at the repository boundary,
- audit events for required actions,
- consent records for exported likenesses.

## 13. Open questions

- Whether application-level encryption is required for restricted data in the first deployment.
- Whether GPU pods can be fully isolated from the internet in all provider configurations.
- Whether customer-managed keys are a launch requirement or an enterprise feature.
- How to verify deletion in provider-side storage.
- Which compliance frameworks are required by target customers.

Tracked in [OPEN_QUESTIONS.md](../project/OPEN_QUESTIONS.md).
