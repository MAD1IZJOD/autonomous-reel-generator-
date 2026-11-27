# Architecture Review

| Field | Value |
|---|---|
| Status | Phase 2 validation; based on the described pipeline and target architecture |
| Last updated | 2026-11-27 |
| Related | [System architecture](SYSTEM_ARCHITECTURE.md), [data flow](DATA_FLOW.md), [component design](COMPONENT_DESIGN.md), [job lifecycle](JOB_LIFECYCLE.md) |

## 1. Review method and limitation

This review validates the architecture described in the Phase 2 brief and the existing foundation documents. The two attached diagram files could not be inspected directly in this environment because image input is not supported by the available model. Their component lists and intended connections are therefore validated against the textual architecture and the founder's pipeline described in the Phase 1 foundation.

**Action required:** export the diagrams as Mermaid, SVG-with-text, or a structured component list and attach them to a follow-up review. Until then, recommendations below are made against the described target, not against the pixels of the diagrams.

## 2. Architecture intent preserved

The target architecture is consistent with the decisions already recorded:

- A modular monolith control plane with independently scalable CPU and GPU workers.
- PostgreSQL as the durable state and queue backbone.
- S3-compatible object storage for all media.
- Capability-based model routing rather than hardcoded provider calls.
- Resident GPU model servers with warm pools and idle shutdown.
- Human approval gates and shot-level regeneration as first-class domain concepts.

No change is recommended to these fundamentals. The review below focuses on missing components, fragile connections and scaling details.

## 3. Component validation

| Component | Responsibility | Key inputs | Key outputs | Storage | Scaling |
|---|---|---|---|---|---|
| Script ingestion | Validate and freeze script versions | Raw script text | `ScriptVersion` | PostgreSQL | API tier |
| Plate planning | Generate structured plate sheet from script | Script version, profile | `PlateSheet` draft | PostgreSQL | CPU worker |
| Workflow orchestrator | Materialise stage graph and gates | Approved plan, policy | `Run`, `StageRun` | PostgreSQL | API tier |
| Durable job queue | Dispatch, lease, retry, cancel | Domain state change | `Job`, `Attempt` | PostgreSQL | Partitioned by class |
| Model router | Resolve capability to deployment | Capability, policy, quality profile | `RoutingDecision` | PostgreSQL | API tier |
| Provider adapters | Translate domain commands to provider APIs | `ProviderRequest` | `ProviderResult` | PostgreSQL (metadata) | CPU worker |
| GPU scheduler | Select pool, session, batch jobs | Job, routing decision | Session assignment | PostgreSQL | Control plane |
| GPU worker / model server | Execute inference | Inputs, model weights | Output artifacts | Object storage + cache | GPU pool |
| Voice generation | Synthesize and post-process voice | Plate text, voice profile | Audio asset version | Object storage | Provider + CPU |
| Presenter generation | Avatar or lip-sync segment | Audio, references | Video asset version | Object storage | GPU + provider |
| Image generation | Generate keyframes | Plate description, references | Image asset version | Object storage | GPU image pool |
| Image editing | Multi-reference editing | Images, references | Image asset version | Object storage | GPU image pool |
| Video generation | Image-to-video motion | Approved still, plate | Video asset version | Object storage | GPU video pool |
| Lip-sync QC | SyncNet and mouth metrics | Presenter video, audio | `QcReport` | Object storage + PostgreSQL | CPU/QC |
| Editing and composition | HyperFrames composition | Shots, graphics, proof | Composition project | Object storage | CPU worker |
| FFmpeg rendering | Final 25 FPS master | Composition, audio | Render asset version | Object storage | CPU render pool |
| Audio mix and master | Mix and normalise audio | Voice, music, SFX | Audio asset version | Object storage | CPU worker |
| Automated QC | Metrics and gate decisions | Assets, thresholds | `QcReport` | Object storage + PostgreSQL | CPU/QC |
| Human approval | Attributed gate decisions | Evidence, candidate | `Approval` | PostgreSQL | API tier |
| Asset registry | Versioned media identity | Outputs | `Asset`, `AssetVersion` | PostgreSQL + object storage | API tier |
| Object storage | Durable media and manifests | Bytes | Signed URLs | Object storage | Provider-managed |
| Cost ledger | Estimate and actual cost | Jobs, sessions | `CostEntry` | PostgreSQL | API tier |
| Observability | Logs, metrics, traces | Events | Dashboards, alerts | Telemetry backend | Cross-cutting |
| Identity and access | Auth, roles, authorization | Credentials | Sessions | PostgreSQL | API tier |
| Consent registry | Voice and likeness consent | Consent records | Consent links | PostgreSQL | API tier |

## 4. Missing components identified

The following are implied by the pipeline but must be explicit in the diagrams and implementation:

1. **Workflow state store** — run, stage and gate state must be durable and queryable, not held in memory or chat.
2. **Idempotency store** — prevents duplicate paid calls and duplicate GPU sessions.
3. **Budget reservation** — atomic headroom check before dispatch; otherwise concurrent jobs overspend.
4. **Model cache manager** — persistent weight cache and versioned cache updates; prevents the observed 75 GB download per session.
5. **Artifact promoter** — moves validated staging objects to content-addressed keys; database must never point to missing bytes.
6. **QC evidence store** — contact sheets, extracted frames and metric reports are first-class artifacts.
7. **Consent registry** — links voice and likeness consent to exported assets.
8. **Watchdog / orphan detector** — terminates idle GPU sessions independently of the job that created them.
9. **Notification path** — alerts operators when a run needs review, fails or breaches budget.
10. **Preflight validator** — cheap CPU-side validation before GPU provisioning.
11. **Cancellation coordinator** — stops new dispatch and terminates owned GPU sessions.
12. **Export packager** — assembles video, captions, thumbnails and manifest.

## 5. Fragile or incorrect connections to correct

1. **UI must not call providers directly.** All provider access goes through the control plane and policy.
2. **Media must not be stored in PostgreSQL.** Only metadata, hashes and storage keys belong in the database.
3. **GPU pods must not access the database or secret store.** They receive scoped, short-lived credentials for the claimed job only.
4. **No stage may be marked successful without a validated artifact.** Process exit is not success.
5. **Timing changes must invalidate downstream motion assets.** A voice edit that changes duration cannot silently reuse old motion.
6. **QC metrics are screening gates, not proof.** Diagrams should show human review as a required node, not an optional annotation.
7. **Cost must be attributed per run, stage, shot and provider.** A pipeline diagram without a cost ledger hides the primary waste source.
8. **Approval gates must be represented as states, not UI conveniences.** A rejected gate must block dispatch at the job layer.
9. **Model names must not appear in workflow nodes.** Nodes request capabilities; routing resolves models.
10. **GPU provisioning must be gated by preflight.** Provisioning before validation recreates the observed cost waste.

## 6. Recommendations to the target diagrams

- Add explicit nodes for PostgreSQL, object storage, model cache volume and telemetry backend.
- Separate the control plane, CPU workers, GPU agents and model servers into distinct runtime boxes.
- Show approval gates (`plates.approve`, `keyframes.approve`, `review.human`) as blocking states.
- Show QC as a node with evidence output, not a side note.
- Show cost ledger and audit as first-class components.
- Show preflight before GPU provisioning.
- Show idle shutdown and watchdog as part of the GPU lifecycle.
- Show asset versioning and provenance on the media path.
- Show consent links on presenter and voice paths.
- Label data movement: metadata vs bytes, internal vs external egress.

## 7. Scaling notes

- API tier and CPU workers scale horizontally; job claims use `SKIP LOCKED`.
- GPU pools scale by session count and queue depth, not by API request rate.
- Object storage is provider-managed and must not be proxied for large media.
- Model cache volumes must scale with the number of distinct deployed model versions.
- QC and render pools should be separate from inference pools to avoid head-of-line blocking.

## 8. Open questions carried forward

- Exact throughput targets for concurrent runs and shots.
- Whether GPU agents pull jobs or are driven by a control channel.
- Whether model weights can be baked into images for all providers.
- How to verify deletion in provider-side storage.
- Whether per-tenant GPU pools are required for enterprise.

These are tracked in `docs/project/OPEN_QUESTIONS.md`.
