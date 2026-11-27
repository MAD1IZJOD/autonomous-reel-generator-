# Repository Acquisition Plan

| Field | Value |
|---|---|
| Status | Foundation; no repositories are cloned or forked in this phase |
| Last updated | 2026-11-27 |
| Related | [Open-source dependencies](OPEN_SOURCE_DEPENDENCIES.md), [licensing policy](../ai/LICENSING_POLICY.md), [model registry](../ai/MODEL_REGISTRY.md) |

## 1. Purpose

This plan defines how upstream repositories and dependencies will be acquired, evaluated and maintained. It prevents ad hoc cloning and ensures licence and maintenance review before use.

## 2. Acquisition principles

- Do not clone or fork until a milestone requires the component.
- Prefer package managers and pinned versions over cloning source.
- Clone only when source inspection or a custom build is genuinely needed.
- Fork only when a maintained modification is required and an owner is assigned.
- Record licence, version and source in the registry or dependency manifest.
- Review maintenance status before adopting.

## 3. Acquisition criteria

A component may be acquired when:

- it is required by an approved milestone,
- its licence is reviewed and compatible,
- its maintenance status is acceptable,
- its hardware and integration requirements are understood,
- an owner is assigned for updates and security patches.

## 4. Evaluation steps

1. Identify the official repository and release.
2. Review the licence text and commercial restrictions.
3. Check maintenance activity and security posture.
4. Assess integration complexity and hardware requirements.
5. Decide use mode: dependency, standalone service or fork.
6. Record the decision in the registry or dependency manifest.
7. Pin the version or image digest.
8. Add contract tests or smoke tests.

## 5. Acquisition order

| Order | Component | Milestone | Use mode |
|---|---|---|---|
| 1 | Git, Python, Node.js, Docker | M2 | Local tooling |
| 2 | PostgreSQL, MinIO | M2 | Local stack |
| 3 | FFmpeg, FFprobe | M2 | Dependency/service |
| 4 | FastAPI, SQLAlchemy, Alembic, Pydantic | M2 | Dependencies |
| 5 | ComfyUI | M2/M3 | Standalone service |
| 6 | HyperFrames tooling | M2/M3 | Tooling |
| 7 | Whisper, MediaPipe, SyncNet | M2/M3 | Dependencies/services |
| 8 | Qwen and Wan model weights | M1/M2 | Model cache |
| 9 | InfiniteTalk model server | M1/M2 | Model service |
| 10 | OpenTelemetry, Prometheus/Grafana | M2/M3 | Observability |

## 6. Fork policy

A fork is permitted only when:

- a required change cannot be made through configuration or a wrapper,
- the upstream project is unmaintained or unresponsive,
- the change is small and well-understood,
- an owner and maintenance budget are assigned,
- an ADR records the decision.

Forks are a liability. Prefer wrapping or configuring upstream components.

## 7. Version pinning

- Application dependencies are pinned in lock files.
- Container images are referenced by digest in production.
- Model weights are pinned by hash.
- Upgrades are tested in staging before production.

## 8. Security and supply chain

- Verify checksums or signatures where available.
- Scan dependencies and images in CI.
- Review transitive dependencies for licence and vulnerability issues.
- Do not download binaries from unofficial sources.

## 9. Open questions

- Whether GPU image definitions live in this repository or a separate one.
- Whether to mirror dependencies for air-gapped enterprise deployments.
- Whether to maintain a private package index.

Tracked in `docs/project/OPEN_QUESTIONS.md`.
