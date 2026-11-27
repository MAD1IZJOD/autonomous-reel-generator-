# Technology Stack

| Field | Value |
|---|---|
| Status | Proposed and provisional until the Milestone 0 code audit |
| Last updated | 2026-11-27 |
| Related | [Repository structure](REPOSITORY_STRUCTURE.md), [development guide](DEVELOPMENT_GUIDE.md), [testing strategy](TESTING_STRATEGY.md), [ADR-001](../architecture/decisions/ADR-001-architecture-style.md) |

## 1. Principles

- Choose boring, well-supported technology for the control plane; reserve novelty for model and media work.
- Keep the number of moving parts small until measurements justify adding them.
- Prefer open standards and portable APIs over vendor-specific SDKs.
- Separate CPU and GPU runtime concerns; do not force GPU dependencies into the control plane.
- Every dependency must have a stated reason and a licence review.
- Provisional choices are marked **(P)** and require validation during the code audit.

## 2. Control plane and API

| Concern | Choice | Notes |
|---|---|---|
| Language | Python 3.12 | Strong ML/media ecosystem; consistent with existing scripts |
| Web framework | FastAPI | Async, OpenAPI, dependency injection |
| Validation | Pydantic v2 | Shared with FastAPI; strict models |
| ORM / migrations | SQLAlchemy 2 + Alembic | Mature; async support; migration discipline |
| API style | REST + JSON, cursor pagination | Simple, cacheable, debuggable |
| Background jobs | PostgreSQL `SKIP LOCKED` (see ADR-002) | No broker initially |
| Task scheduling | In-process scheduler or a small cron worker | Keep to periodic maintenance tasks |
| Configuration | Pydantic settings from environment | Validated at startup |

Python is chosen because the existing tooling and model clients are Python. A future rewrite of a hot path in another language is possible but is not planned.

## 3. Web application

| Concern | Choice | Notes |
|---|---|---|
| Framework | Next.js (App Router) **(P)** | Server/client split, mature ecosystem |
| Language | TypeScript (strict) | Safer client code |
| Styling | Tailwind CSS **(P)** | Utility-first; fast iteration |
| Components | shadcn/ui **(P)** or a comparable accessible library | Accessible primitives |
| State/data | TanStack Query **(P)** | Server state caching |
| Forms | React Hook Form + Zod **(P)** | Validation reuse |
| Media preview | Native HTML5 video/audio + image | Avoid heavy players unless needed |
| Charts | A lightweight chart library **(P)** | Cost and timing dashboards |

The frontend choice is provisional. The audit may reveal that a simpler server-rendered application is sufficient for the operator-first MVP.

## 4. Data and storage

| Concern | Choice | Notes |
|---|---|---|
| Relational database | PostgreSQL 16+ | Jobs, metadata, cost, audit |
| Object storage | S3-compatible API (MinIO locally, S3/R2 in cloud) | Media, evidence, exports |
| Cache | PostgreSQL + application-level memoization initially | Redis only if measured need |
| Search | PostgreSQL full-text initially | Dedicated search only if needed |
| Migrations | Alembic | Reviewed and reversible where possible |

## 5. GPU and model runtime

| Concern | Choice | Notes |
|---|---|---|
| Provider (first) | RunPod | Existing provider; adapter boundary |
| Orchestration | Custom pool manager in Python | Leases, health checks, idle shutdown |
| Image generation | ComfyUI headless API | Existing workflow |
| Lip-sync | InfiniteTalk model server | Existing workflow; A100 baseline |
| Model weights | Persistent volume or baked image | Avoid repeated 75 GB downloads |
| Container runtime | Docker / OCI | Reproducible images |
| Image registry | Any OCI registry | Pinned by digest |

Model servers are separate containers with their own dependencies. They are not part of the control-plane image.

## 6. Media processing

| Concern | Choice | Notes |
|---|---|---|
| Probe | FFprobe | Format and integrity validation |
| Transcode/normalize | FFmpeg | Existing requirement |
| Composition | HyperFrames (HTML, GSAP, Three.js) | Existing editorial kit |
| Rendering | FFmpeg from HyperFrames output | 25 FPS master |
| Audio mastering | FFmpeg + measurement tools | Loudness and true peak |
| Image processing | Pillow or similar | Thumbnails, contact sheets |
| Video metrics | Custom scripts wrapping FFmpeg/Python | Black/duplicate frames, durations |

HyperFrames uses Node.js tooling. The control plane invokes it as a process or container; it does not need to be a Python dependency.

## 7. AI and quality control

| Concern | Choice | Notes |
|---|---|---|
| Voice baseline | ElevenLabs API | Premium baseline |
| Avatar baseline | HeyGen Avatar 6 | Premium baseline |
| Open image | Qwen-Image + Lightning LoRA via ComfyUI | Existing workflow |
| Open image editing | Qwen-Image-Edit-2511 | Existing workflow |
| Open video | Wan 2.2 I2V A14B fp8 + LightX2V LoRA | Existing workflow |
| Open lip-sync | InfiniteTalk on Wan 2.1 I2V 14B | Existing workflow; measured limitations |
| Transcription | Whisper | Voice QC |
| Lip-sync QC | SyncNet, MediaPipe | Screening gates |
| Similarity | Speaker similarity model/script | Existing workflow |
| Model registry | Application data in PostgreSQL | Not a separate service |

Open-weight model choices are subject to evaluation and licensing review. See [MODEL_REGISTRY.md](../ai/MODEL_REGISTRY.md).

## 8. Observability

| Concern | Choice | Notes |
|---|---|---|
| Tracing | OpenTelemetry | Standard, vendor-neutral |
| Metrics | OpenTelemetry + Prometheus-compatible backend | Dashboards and alerts |
| Logs | Structured JSON to stdout | Collected by the deployment platform |
| Errors | Sentry or equivalent **(P)** | Optional; redact media and secrets |
| Dashboards | Grafana or managed equivalent **(P)** | Cost and GPU utilization |
| Audit | PostgreSQL append-only table | Not a separate audit product |

## 9. Testing

| Concern | Choice | Notes |
|---|---|---|
| Unit/integration | pytest | Python standard |
| API tests | FastAPI TestClient / httpx | In-process where possible |
| Database tests | Testcontainers PostgreSQL | Real database, not mocks |
| Object storage tests | Testcontainers MinIO or local MinIO | Real S3 API |
| Frontend tests | Vitest + Playwright **(P)** | Unit + E2E |
| Contract tests | Recorded HTTP fixtures + live smoke tests | Labelled fixtures |
| Lint/format | Ruff | Python |
| Type checking | mypy (strict for domain) | Python |
| Frontend lint | ESLint + TypeScript | Standard |
| CI | GitHub Actions | Existing repository host |

## 10. Security and supply chain

| Concern | Choice | Notes |
|---|---|---|
| Password hashing | Argon2id | Modern standard |
| Secrets | Environment/secret manager | Never in Git |
| Dependency scanning | Dependabot or equivalent + `pip-audit`/`npm audit` | CI |
| Container scanning | Trivy or equivalent **(P)** | CI |
| SAST | Bandit/Ruff security rules + CodeQL **(P)** | CI |
| Licence review | Manual plus tooling where available | Required before production enablement |

## 11. Deployment and operations

| Concern | Choice | Notes |
|---|---|---|
| Dev environment | Docker Compose | Reproducible local stack |
| Production (initial) | Containers on a Linux host or managed container service | Single region |
| Enterprise (future) | Kubernetes or customer-approved platform | Not in MVP |
| Migrations | Alembic in CI/CD or deploy job | Reviewed |
| Feature flags | Simple database-backed flags initially | Avoid a vendor until needed |
| Backups | Managed PostgreSQL + object storage lifecycle | Tested restore |

## 12. Explicitly not chosen

| Technology | Why not now |
|---|---|
| Redis as primary queue | Adds a system; PostgreSQL queue is sufficient initially |
| Temporal | Operational complexity not justified yet |
| Kubernetes | Premature for the first deployment |
| Microservices | Premature; see ADR-001 |
| A separate model registry service | PostgreSQL is sufficient |
| A separate media processing service | Workers are sufficient; extract if needed |
| A commercial video editor SDK | Not aligned with the HyperFrames workflow |

## 13. Provisional decisions requiring audit validation

- Frontend framework and component library.
- Whether to use Redis for caching or rate limiting.
- Whether HyperFrames runs as a process or in a container.
- Whether GPU agents pull jobs or are driven by a control channel.
- Whether to adopt a vendor for errors/metrics or self-host.
- Whether to use managed PostgreSQL or self-host.

These are recorded in [OPEN_QUESTIONS.md](../project/OPEN_QUESTIONS.md) and must be resolved with evidence during Milestone 0 and Milestone 2.
