# Environment Setup Checklist

| Field | Value |
|---|---|
| Status | Checklist only; no setup actions have been executed |
| Last updated | 2026-11-27 |
| Related | [Development environment](../infrastructure/DEVELOPMENT_ENVIRONMENT.md), [implementation roadmap](IMPLEMENTATION_ROADMAP.md) |

This checklist is for preparation only. Do not execute setup actions until the architecture and setup plan are reviewed.

## A. Software on the development machine

- [ ] Git installed and configured with the required commit identity.
- [ ] Code editor installed with Markdown and Mermaid preview.
- [ ] Python 3.12 installed (when implementation begins).
- [ ] Node.js LTS installed (when frontend/HyperFrames work begins).
- [ ] Docker Desktop installed (when local stack is needed).
- [ ] FFmpeg and FFprobe installed (when media processing begins).

## B. Cloud infrastructure

- [ ] Decide managed vs self-hosted PostgreSQL.
- [ ] Create S3-compatible storage bucket and access keys.
- [ ] Configure RunPod account and API key (when GPU work begins).
- [ ] Configure observability backend (when needed).

## C. API accounts and credentials

- [ ] ElevenLabs account and API key (when voice reproduction begins).
- [ ] HeyGen account and avatar configuration (when presenter reproduction begins).
- [ ] GitHub repository access and CI configuration.
- [ ] Secret manager or local secret store.

## D. Open-source repositories and dependencies

- [ ] Review licences before acquiring any repository.
- [ ] Acquire repositories only when a milestone requires them.
- [ ] Pin versions and record them in manifests.
- [ ] Do not fork without an ADR and an owner.

## E. Model weights and storage

- [ ] Do not download large model weights in this phase.
- [ ] Plan persistent model cache on the GPU provider.
- [ ] Verify model licences before production use.
- [ ] Store datasets and fixtures on the D: drive, not in Git.

## F. GitHub configuration

- [ ] Confirm branch protection on `main`.
- [ ] Enable secret scanning.
- [ ] Configure CI when application code exists.
- [ ] Confirm commit identity enforcement.

## G. Testing and monitoring

- [ ] Set up unit and integration test runners when code exists.
- [ ] Configure cost-capped live provider tests.
- [ ] Configure dashboards and alerts before production.

## Notes

- The development machine has no NVIDIA GPU; heavy inference stays in the cloud.
- The D: drive is the primary project and storage location.
- No large dependencies or model weights are installed in this phase.
- Review the architecture and setup checklist before executing any item.
