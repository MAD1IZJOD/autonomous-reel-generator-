# Open-Source Dependencies

| Field | Value |
|---|---|
| Status | Foundation; licences and versions must be verified before production use |
| Last updated | 2026-11-27 |
| Related | [Tech stack](../engineering/TECH_STACK.md), [licensing policy](../ai/LICENSING_POLICY.md), [model registry](../ai/MODEL_REGISTRY.md), [repository acquisition plan](REPOSITORY_ACQUISITION_PLAN.md) |

## 1. Purpose

This document audits the open-source projects under consideration. It separates repository licences from model-weight licences and records whether each project is used as a dependency, a standalone service or (only with justification) a fork.

## 2. Audit table

| Project | Official repository | Licence | Commercial use | Hardware | Maintenance | Integration | Use mode | Why it belongs | Alternatives | Benefit |
|---|---|---|---|---|---|---|---|---|---|---|
| ComfyUI | `comfyanonymous/ComfyUI` | GPL-3.0 (verify current) | Review required; GPL implications for distribution | L40 48 GB+ for target models | Active | Medium | Standalone service | Existing image/video orchestration runtime | A1111, Fooocus, custom diffusers | Reuses tested workflows |
| FFmpeg | `FFmpeg/FFmpeg` | LGPL/GPL depending on build | Review build configuration and codecs | CPU | Active | Low | Dependency/service | Probe, transcode, render, mastering | GStreamer, HandBrake CLI | Universal media processing |
| Temporal | `temporalio/temporal` | MIT | Permissive (verify) | Server + DB | Active | High | Not in MVP | Durable workflows | Our PostgreSQL queue, Celery | Candidate if complexity grows |
| Celery | `celery/celery` | BSD-3 | Permissive (verify) | Redis/RabbitMQ | Active | Medium | Not in MVP | Distributed task queue | Our PostgreSQL queue | Familiar; deferred |
| PostgreSQL | `postgres/postgres` | PostgreSQL Licence | Permissive | CPU | Active | Low | Dependency | Metadata, jobs, cost, audit | MySQL, SQLite | Strong consistency and queueing |
| Redis | `redis/redis` | RSALv2/SSPL/AGPLv3 depending on version | Review version and use | CPU | Active | Low | Optional cache | Caching, rate limiting | PostgreSQL, in-memory | Low latency; deferred |
| S3-compatible storage | MinIO, Ceph, cloud providers | AGPLv3 (MinIO) / varies | Review per implementation | CPU/storage | Active | Low | Service/dependency | Media, evidence, exports | Local filesystem, GCS | Durable signed access |
| OpenTelemetry | `open-telemetry/*` | Apache-2.0 | Permissive | CPU | Active | Medium | Dependency | Traces, metrics, logs | Vendor SDKs | Vendor-neutral observability |
| HyperFrames | Existing project repo (verify) | Verify | Review before commercial use | Node.js + browser | Verify | Medium | Service/tool | Editorial composition | Revideo, Remotion | Existing editorial workflow |
| Whisper | `openai/whisper` | MIT | Permissive (verify) | GPU/CPU depending on size | Active | Low | Dependency/service | Transcription QC | faster-whisper, Vosk | Baseline QC tool |
| MediaPipe | `google/mediapipe` | Apache-2.0 | Permissive | CPU | Active | Medium | Dependency | Mouth metrics | Custom CV | Baseline QC tool |
| SyncNet | Research implementation | Verify | Review; often research/non-commercial | CPU/GPU | Varies | Medium | Dependency/service | Lip-sync QC | Custom metrics | Baseline QC tool |
| Qwen image models | Model repos | Verify per version | Must verify; do not assume | L40 48 GB | Active | Medium | Model service | Image generation/editing | Other open image models | Existing baseline |
| Wan video models | Model repos | Verify per version | Must verify; do not assume | L40/L40S 48 GB | Active | Medium | Model service | Motion generation | Other open video models | Existing baseline |
| InfiniteTalk | Model repo | Verify per version | Must verify; do not assume | A100 80 GB (tested) | Verify | High | Model service | Open lip-sync candidate | LatentSync, LongCat | Best open option tested |

## 3. Licensing rules

- Repository licences and model-weight licences are separate and both must be reviewed.
- GPL/AGPL components may be used as services or dependencies with implications for distribution; review before shipping.
- A fork is justified only when we need a modified version and can maintain it.
- No component is production-enabled without a licence decision in the registry.

## 4. Use-mode guidance

- **Dependency:** imported into our codebase; must be licence-compatible with commercial distribution.
- **Standalone service:** runs as a separate process or container; licence obligations are contained but still reviewed.
- **Fork:** only when a genuine maintenance need exists; requires an ADR and an owner.

## 5. Decisions

- PostgreSQL, OpenTelemetry and FFmpeg (with a reviewed build) are foundational.
- ComfyUI, Whisper, MediaPipe and SyncNet are used as services or dependencies with licence review.
- Temporal and Celery are deferred; the PostgreSQL queue is sufficient initially.
- Redis is optional and deferred.
- Qwen, Wan and InfiniteTalk are model services; their licences must be verified per version.
- HyperFrames is retained based on the existing workflow; its licence and maintenance status must be verified.
- No forks are proposed at this time.

## 6. Open questions

- Exact licences for ComfyUI, HyperFrames, SyncNet and the model weights.
- Whether MinIO or another S3-compatible implementation is acceptable for commercial distribution.
- Whether Redis is needed for caching or rate limiting.
- Whether Temporal becomes justified at scale.

Tracked in `docs/project/OPEN_QUESTIONS.md`.
