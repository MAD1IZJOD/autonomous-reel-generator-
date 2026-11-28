# Phase 4 Implementation Plan

| Field | Value |
|---|---|
| Status | In progress |
| Last updated | 2026-11-28 |
| Related | [ADR-006](../architecture/decisions/ADR-006-independent-implementation.md), [component design](../architecture/COMPONENT_DESIGN.md), [job lifecycle](../architecture/JOB_LIFECYCLE.md), [testing strategy](../engineering/TESTING_STRATEGY.md) |

## 1. Objective

Build the first independently runnable execution foundation and prove it with an end-to-end mocked explainer workflow that renders a real 25 FPS video.

The slice must prove:

- projects, scripts, plate sheets and shots are persisted and versioned;
- both workflow profiles are explicit and have different gates;
- jobs are durable, leased, retryable, idempotent and cancellable;
- assets are stored behind a storage port and recorded immutably;
- providers and models are resolved through capability routing, not hardcoded names;
- costs are recorded and spend is guarded;
- approval gates are domain state, not UI flags;
- FFmpeg composition and rendering produce a playable file;
- automated QC measures real properties of that file;
- export produces a video and a run manifest.

## 2. Deliberate exclusions

| Excluded | Reason |
|---|---|
| Real ElevenLabs, HeyGen, RunPod or ComfyUI calls | No credentials, spend approval or GPU access in this phase |
| Model downloads or GPU provisioning | Explicitly forbidden |
| Next.js UI | API and CLI demonstrate the workflow; UI follows once the engine is stable |
| PostgreSQL-specific integration tests | No local PostgreSQL or Docker; SQLite is used for tests and the queue is dialect-aware |
| Real SyncNet, Whisper, MediaPipe or speaker-similarity inference | Heavy dependencies and model weights; interfaces and deterministic metrics are implemented first |
| Production quality claims | Mock media is a fixture, not a creative result |

## 3. Architecture of the slice

```text
FastAPI API / CLI demo
        |
        v
Application services (projects, plans, runs, approvals)
        |
        v
Domain (state machines, profiles, plate validation, invariants)
        |
        v
Durable job engine (PostgreSQL/SQLite, leases, retries, idempotency)
        |
        v
Stage handlers
  |         |          |          |
  v         v          v          v
Providers  Media      QC         Cost
(mocks)    (FFmpeg)   (ffprobe)  (ledger)
        |
        v
Storage port (local filesystem now, S3 adapter later)
```

## 4. Work breakdown

| Step | Deliverable | Verification |
|---|---|---|
| 4.1 | Validated settings and database session | Startup rejects invalid configuration |
| 4.2 | SQLAlchemy schema for all required entities | Tables create; constraints applied |
| 4.3 | Domain state machines, profiles and plate validation | Unit tests |
| 4.4 | Local storage port and content hashing | Unit test |
| 4.5 | Provider ports, deterministic mocks and registry seed | Routing tests |
| 4.6 | Capability routing with licence and quality gates | Unlicensed candidates rejected |
| 4.7 | Cost ledger and spend guard | Budget test |
| 4.8 | FFmpeg probe, render, mix and QC helpers | Media tests |
| 4.9 | Job engine with leases, retries, cancellation and stale-token rejection | Queue tests |
| 4.10 | Stage handlers and run advancement | Integration test |
| 4.11 | FastAPI endpoints | API tests |
| 4.12 | Worker loop and CLI demo | Real end-to-end run |
| 4.13 | Alembic baseline migration | Migration applies to an empty database |
| 4.14 | Documentation and progress evidence | Review |

## 5. First demonstration

Input: a short approved English/Hindi explainer script.

1. Create a project.
2. Store the approved script.
3. Generate a deterministic plate sheet with a mock planner.
4. Validate the plate sheet.
5. Approve the plate sheet.
6. Create an explainer run.
7. Generate one mock WAV fixture per plate.
8. Derive plate timings from the real WAV durations.
9. Generate labelled mock stills.
10. Generate labelled mock motion and presenter clips.
11. Compose the timeline and a contact sheet.
12. Mix voice with a low-level synthetic music bed and normalise to -14 LUFS.
13. Render a real H.264 MP4 at 25 FPS.
14. Measure frame rate, duration drift, black/frozen frames and loudness.
15. Wait at the human review gate.
16. Approve review.
17. Export the video, QC evidence and manifest.

## 6. Data and state rules

- Script versions and approved plate sheets are immutable.
- A run snapshots script, plate sheet, profile, configuration and policy.
- A stage succeeds only when its expected artifact exists and validates.
- A job succeeds only with a valid artifact and a non-stale lease token.
- Approval is an append-only record with actor, role, gate and decision.
- Export is blocked until the human gate is approved.
- Cost entries are append-only.
- Cancellation does not erase cost or completed artifacts.

## 7. Test plan

| Layer | Tests |
|---|---|
| Unit | Profile graphs, plate validation, state transitions, idempotency key, routing filters, spend guard |
| Integration | Job claim/heartbeat/retry/stale completion, run materialisation, approval advancement |
| Media | FFprobe parsing, WAV fixture duration, render frame rate and duration |
| End-to-end | Full mocked explainer run with real MP4, QC, approval and export |
| Negative | Unlicensed model rejected, export before approval rejected, invalid plate rejected |

## 8. Completion criteria

- `pytest` passes on Python 3.12.
- The end-to-end test produces a playable MP4 at 25 FPS with audio.
- QC values are measured from the file, not hardcoded.
- The run stops at human review and only exports after approval.
- The manifest records models, providers, settings hashes, timings, costs and QC evidence.
- No secrets, media, databases or model weights are committed.
- Every file is committed separately and pushed with the required identity.

## 9. Known limitations carried forward

- SQLite is the tested database; PostgreSQL `SKIP LOCKED` is implemented but not integration-tested in this environment.
- The local storage adapter is used; S3 is an adapter boundary, not a tested deployment.
- Voice, image, motion, presenter and music are deterministic mocks.
- QC does not yet run Whisper, SyncNet, MediaPipe or speaker similarity.
- No frontend exists.
- No real provider is enabled.
