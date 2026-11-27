# Development Environment

| Field | Value |
|---|---|
| Status | Foundation; setup actions are listed, not executed |
| Last updated | 2026-11-27 |
| Related | [Tech stack](TECH_STACK.md), [repository structure](REPOSITORY_STRUCTURE.md), [environment setup checklist](../project/ENVIRONMENT_SETUP_CHECKLIST.md) |

## 1. Development machine

- OS: Windows 11
- CPU: AMD Ryzen AI 7 350
- Graphics: Radeon 860M integrated (no discrete NVIDIA GPU)
- RAM: 24 GB
- Storage: 1 TB SSD, D: drive is the primary project and storage location

Implications:

- The machine is suitable for control-plane development, editing, QC review and documentation.
- It is not suitable for running Wan, InfiniteTalk or other large models locally.
- Heavy inference runs on cloud GPU workers.
- Local model execution is limited to lightweight or CPU-friendly tools if needed.

## 2. A. Software on the development machine

| Item | Why | Cost | Local install | Docker | GPU | Can wait? |
|---|---|---|---|---|---|---|
| Git | Version control | Free | Yes | No | No | No |
| Python 3.12 | Control plane and workers | Free | Yes | Optional | No | No |
| Node.js LTS | Web app and HyperFrames tooling | Free | Yes | Optional | No | Until M2 |
| Docker Desktop | Local stack | Free/paid tier | Yes | Yes | No | Until M2 |
| FFmpeg / FFprobe | Media processing | Free | Yes | Yes | No | Until M2 |
| VS Code or equivalent | Editing | Free | Yes | No | No | No |
| Markdown/Mermaid preview | Documentation | Free | Yes | No | No | No |

## 3. B. Cloud infrastructure

| Item | Why | Cost | Local install | Docker | GPU | Can wait? |
|---|---|---|---|---|---|---|
| PostgreSQL | Metadata and jobs | Free self-hosted or managed | No | Yes | No | Until M2 |
| S3-compatible storage | Media and artifacts | Free tier or paid | No | Yes (MinIO) | No | Until M2 |
| GPU provider (RunPod) | Heavy inference | Paid | No | No | Yes | Until M1/M2 |
| Observability backend | Logs, metrics, traces | Free tier or paid | No | Yes | No | Until M2 |

## 4. C. API accounts and credentials

| Item | Why | Cost | Can wait? |
|---|---|---|---|
| ElevenLabs | Voice baseline | Paid | Until M1 |
| HeyGen | Avatar baseline | Paid | Until M1 |
| RunPod | GPU inference | Paid | Until M1/M2 |
| GitHub | Repository and CI | Free/paid | No |
| Secret manager | Credential storage | Free/paid | Until M2 |

## 5. D. Open-source repositories and dependencies

- No repositories are cloned or forked in this phase.
- Dependencies are not installed yet.
- The acquisition plan is defined in `REPOSITORY_ACQUISITION_PLAN.md`.
- Licences must be reviewed before production use.

## 6. E. Model weights and storage

- No model weights are downloaded in this phase.
- Model cache is expected to live on a persistent volume or baked image in the GPU provider.
- The D: drive may hold local datasets, fixtures and documentation, not production model weights.

## 7. F. GitHub configuration

- Repository is `MAD1IZJOD/autonomous-reel-generator-`.
- Default branch is `main`.
- Commit identity is fixed.
- CI will be added during Milestone 2.
- Branch protection and secret scanning should be configured before production use.

## 8. G. Testing and monitoring

- Unit and integration tests run locally or in CI.
- Live provider and GPU tests are manual and cost-capped.
- Observability is required before production use but can be minimal in early milestones.

## 9. Setup order

1. Install Git and editor tooling.
2. Configure repository identity.
3. Install Python 3.12 and Node.js LTS when implementation begins.
4. Install Docker Desktop when the local stack is needed.
5. Create cloud accounts and credentials only when Milestone 1 or 2 requires them.
6. Configure CI and secret scanning before production.

No heavy dependencies or model weights are installed in this phase.
