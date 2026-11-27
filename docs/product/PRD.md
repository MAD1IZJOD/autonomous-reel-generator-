# Product Requirements Document

| Field | Value |
|---|---|
| Product | Autonomous Reel Generator (working name) |
| Status | Foundation / pre-implementation |
| Owner | Avinash Pandit (product), Madhavan (engineering) |
| Last updated | 2026-11-27 |
| Related | [MVP scope](MVP_SCOPE.md), [user flows](USER_FLOWS.md), [acceptance criteria](ACCEPTANCE_CRITERIA.md), [system architecture](../architecture/SYSTEM_ARCHITECTURE.md) |

## 1. Problem

The existing workflow produces real videos, but it is operated through a coding assistant, skill files, individual Python scripts, paid APIs and rented GPUs that are provisioned and torn down per session. That arrangement has four problems:

1. **It is not a product.** There is no owned control plane, no durable job state, no user model, no audit trail and no reliable recovery when a stage fails.
2. **It wastes GPU time.** Pod setup takes roughly 12 minutes, roughly 75 GB of models are downloaded, and most waste comes from model loading rather than inference. A tested 60-second short cost about $9.06 including setup and tests; a repeat in the same style cost about $1.
3. **Quality is not systematically protected.** QC metrics exist, but similarity scores alone missed an accent mismatch, and lip-sync metrics are screening gates rather than proof of quality.
4. **Model choices are entangled with the workflow.** Provider names, settings and scripts are coupled, making it hard to compare open-weight and premium options, apply licensing rules, or route work by cost, privacy and quality.

## 2. Vision

A studio-grade system that turns an approved script into a finished short-form video through an autonomous, reproducible pipeline with human control at the points that matter: script and plate approval, keyframe approval for character work, and final review.

The system should make the economical choice the safe choice: keep expensive models resident and busy, use open-weight models where they meet the quality floor, keep premium APIs where they measurably win, and never hide a quality trade-off.

## 3. Users

| Persona | Needs | Current pain |
|---|---|---|
| **Studio operator** (primary, initially Avinash) | Create a video from a script, review plates, approve keyframes, review scored options, export | Manual controller work, opaque costs, repeated setup |
| **Editor / reviewer** | Inspect shots, compare at most two scored candidates, request a shot-level regeneration, leave structured feedback | Feedback lives in chat; regeneration is manual |
| **Engineer / administrator** | Add models and providers, manage GPU pools, inspect failures, control spend, audit access | Scripts are coupled; no job history or cost ledger |
| **Client reviewer** (later) | Review a link, approve or request changes without seeing internal tooling | Not supported |

The first release is single-workspace. Multi-user collaboration and external client review are designed for but not shipped in the MVP.

## 4. Product principles

1. **Approve before spending.** Script and plate sheet are approved before voice, keyframes or GPU-heavy generation. Character/story videos additionally require visual keyframe approval before voice.
2. **Evidence over scores.** A metric passing is necessary, not sufficient. Contact sheets, human review and comparison with real footage remain part of the gate.
3. **Reproducibility by default.** Every output records model versions, settings, inputs, code revision, hardware, timing and cost.
4. **No silent degradation.** A fallback may be cheaper or faster, but it must satisfy the same quality floor and be visible in the run record.
5. **Shot-level control.** Regenerating one shot must not require rerunning the whole video.
6. **Cost is a first-class signal.** Every job carries an estimated and actual cost; orphaned GPU sessions are treated as incidents.
7. **Own the workflow, rent the intelligence.** The application controls orchestration and data; models and GPUs are replaceable suppliers.
8. **Privacy is explicit.** Media leaves the trust boundary only when a workspace policy allows that provider and data class.

## 5. Scope

### 5.1 In scope for the product MVP

- Project and script version management.
- Plate-sheet generation, structured editing and approval.
- Two workflow profiles: explainer (voice-first timing) and character/story (visual approval first).
- Voice synthesis with the approved ElevenLabs baseline, pronunciation controls and post-processing.
- Keyframe/still generation with the approved Qwen baseline.
- Image-to-video motion with the approved Wan baseline, respecting motion-beat limits.
- Presenter generation through HeyGen Avatar 6 as the baseline, with an adapter boundary for open alternatives.
- Lip-sync generation through InfiniteTalk where the presenter baseline is not used, subject to its measured limitations.
- Motion graphics and editorial composition through HyperFrames/HTML/GSAP, rendered with FFmpeg.
- Music and SFX mixing with licensed or procedurally generated assets.
- Automated QC and human review gates.
- Shot-level regeneration and run recovery.
- Final export in the required aspect ratios and 25 FPS.
- Cost, timing and provider reporting per run.
- A web interface for the operator and reviewer.

### 5.2 Explicitly out of scope for the MVP

- Self-service public sign-up, subscription billing and usage-based invoicing.
- Multi-tenant isolation certification and enterprise SSO/SCIM.
- Automatic publishing to Instagram or YouTube.
- Mobile applications.
- Model training, fine-tuning and custom LoRA production.
- Replacing ElevenLabs or HeyGen with open-weight models as a release requirement.
- Real-time collaborative editing.
- A marketplace of third-party models.
- Guaranteed parity with the founder's manual output on the first attempt; parity is a measured milestone, not an assumption.

## 6. Functional requirements

Requirement identifiers are stable and are referenced by the [acceptance criteria](ACCEPTANCE_CRITERIA.md).

### 6.1 Projects and scripts

| ID | Requirement |
|---|---|
| FR-001 | A user can create a project with a title, format (Reel/Short/long-form), aspect ratio, language mix and workflow profile. |
| FR-002 | A script can be stored as immutable versions; editing creates a new version rather than mutating an approved one. |
| FR-003 | Each run references an exact script version, plate-sheet version, configuration snapshot and code revision. |
| FR-004 | The system records the source of every input asset and whether it is founder-owned, licensed, synthetic or customer-supplied. |

### 6.2 Plate sheet

| ID | Requirement |
|---|---|
| FR-010 | The plate sheet is stored as structured JSON with one row per planned 2–6 second shot. |
| FR-011 | Each plate carries layout, A-roll, B-roll, motion-graphic intent, voiceover line, sound effects, caption and timing. |
| FR-012 | The plate sheet can be generated from an approved script and edited by a human before approval. |
| FR-013 | Plate timing can be derived from the generated voice track for explainers, or from a planned duration for character/story work. |
| FR-014 | Approval is an explicit, attributed action that freezes the approved version for the run. |
| FR-015 | A plate can be regenerated or revised without invalidating unrelated approved plates, subject to dependency rules. |

### 6.3 Voice

| ID | Requirement |
|---|---|
| FR-020 | Voice generation uses the configured provider and voice profile, defaulting to the established ElevenLabs baseline where policy allows. |
| FR-021 | Pronunciation controls include Devanagari rendering for Hindi/English words and numbers written as words, as used in the baseline workflow. |
| FR-022 | Post-processing applies pause squeezing above 0.3 s to approximately 0.2 s, 1.2x speed and -14 LUFS loudness normalisation unless a run explicitly overrides them. |
| FR-023 | Every voice take is versioned and linked to its text, settings and provider request identifier. |
| FR-024 | Voice QC measures speaker similarity, Whisper transcript accuracy/CER and syllables per second, and stores the evidence. |
| FR-025 | A failed voice take can be retaken without regenerating approved visuals. |

### 6.4 Visuals and motion

| ID | Requirement |
|---|---|
| FR-030 | Keyframes are generated from approved plate descriptions and character references. |
| FR-031 | Character/story runs require visual approval of keyframes before voice and presenter generation. |
| FR-032 | Every motion clip starts from an approved still; motion generation cannot invent a new establishing frame. |
| FR-033 | AI motion beats are at or below 2.4 seconds where possible; longer beats must be split or explicitly justified. |
| FR-034 | The run maintains one set, lighting direction and colour grade per video unless the creative brief says otherwise. |
| FR-035 | The system avoids repeated images with artificial zoom pulses and prefers visuals that illustrate the spoken words. |
| FR-036 | At most two already-scored candidates are presented for human review per shot. |

### 6.5 Presenter and lip-sync

| ID | Requirement |
|---|---|
| FR-040 | Presenter segments can be generated through a premium avatar provider using a trained, consented digital twin. |
| FR-041 | The provider abstraction allows an open lip-sync pipeline to be selected when it meets the quality floor for the language and shot. |
| FR-042 | Presenter and lip-sync outputs are checked with SyncNet and MediaPipe mouth-opening metrics against the measured baseline. |
| FR-043 | The system blocks export when lip-sync QC falls below configured gates unless a human explicitly accepts the risk with a recorded reason. |
| FR-044 | Voice and likeness consent records are linked to the assets and providers that use them. |

### 6.6 Graphics, audio and render

| ID | Requirement |
|---|---|
| FR-050 | Motion graphics are composed from the editorial kit (HTML, GSAP, Three.js where needed, paper textures, Anton/Playfair typography, marker highlights, stamps, logos, stickers). |
| FR-051 | Real proof visuals supplied by the founder are preserved and not replaced by synthetic approximations. |
| FR-052 | Music and SFX are mixed with licensed or generated assets; the system records the licence and source of every track. |
| FR-053 | Final renders are produced at 25 FPS with audio normalised to approximately -14 LUFS and true peak between -1 and -1.5 dB. |
| FR-054 | Renders are reproducible from the recorded manifest, subject to provider nondeterminism being documented. |

### 6.7 Review, regeneration and export

| ID | Requirement |
|---|---|
| FR-060 | The UI shows stage progress, current job, elapsed time, estimated and actual cost, and the reason for any wait. |
| FR-061 | A reviewer can approve, reject or request changes at each gate with structured comments. |
| FR-062 | A single shot can be regenerated, and the rest of the timeline is preserved. |
| FR-063 | Regeneration creates new asset versions; prior approved versions remain recoverable. |
| FR-064 | Failed stages can be retried from the last valid checkpoint without repeating completed paid work. |
| FR-065 | The final export includes the video, caption/subtitle assets, thumbnail candidates and a run manifest. |
| FR-066 | Export is blocked while required approvals or blocking QC gates are unresolved. |

### 6.8 Administration and cost

| ID | Requirement |
|---|---|
| FR-070 | Administrators can register providers, credentials and model versions without changing application code. |
| FR-071 | The model registry records capability, version, licence status, hardware requirements, cost inputs and evaluation status. |
| FR-072 | Every provider call and GPU session produces a cost entry with run, stage, shot and provider attribution. |
| FR-073 | Budget thresholds can pause new GPU work and notify an administrator. |
| FR-074 | The system can terminate idle GPU sessions automatically after a configured window (baseline target: 5–10 minutes). |
| FR-075 | An audit trail records approvals, configuration changes, credential changes and export actions. |

## 7. Non-functional requirements

| ID | Requirement |
|---|---|
| NFR-001 | Durable jobs: a process restart must not lose accepted work; jobs resume or fail visibly. |
| NFR-002 | Idempotency: retries of paid provider calls must not duplicate charges where the provider supports idempotency keys; otherwise the system must reconcile before retrying. |
| NFR-003 | Observability: every run, stage, shot and provider call is traceable by correlation ID. |
| NFR-004 | Security: secrets are stored in a secret manager, never in the frontend or Git; media access uses short-lived signed URLs. |
| NFR-005 | Privacy: external provider egress is deny-by-default and allowlisted per workspace. |
| NFR-006 | Portability: the control plane runs on a single Linux host with PostgreSQL and S3-compatible storage; GPU workers are replaceable. |
| NFR-007 | Licence compliance: a model or tool whose commercial status is unverified cannot be selected in production. |
| NFR-008 | Cost visibility: cost per run and cost per accepted output are queryable without log archaeology. |
| NFR-009 | Recovery: a failed shot can be retried without rerunning the full video; a failed GPU session is detectable within one heartbeat interval. |
| NFR-010 | Accessibility of review: reviewers can compare candidates, inspect QC evidence and approve from a desktop browser. |
| NFR-011 | Data retention: deletion requests remove media and derived artifacts according to policy, with audit records retained as required. |
| NFR-012 | No fake success: the UI must distinguish queued, running, failed, cancelled, awaiting approval and succeeded states truthfully. |

## 8. Quality requirements

The baseline settings and thresholds below come from the founder's existing workflow. They are starting gates, not universal truths, and must be re-measured during reproduction.

| Area | Baseline | Source status |
|---|---|---|
| Frame rate | 25 FPS for all deliverables | Tested workflow requirement |
| AI motion beat | ≤ 2.4 s where possible | Editorial requirement |
| Voice similarity | ~0.96–0.97 | Existing threshold; metric alone proved insufficient |
| Whisper CER | ≤ 0.2 | Existing threshold |
| Mouth opening | Mean 0.28, P90 0.42, ~68% frames open | Avi's measured baseline |
| Loudness | ~-14 LUFS, true peak -1 to -1.5 dB | Existing mastering target |
| Review options | At most two scored candidates | Editorial rule |

Quality gates and their failure handling are specified in [QUALITY_GATES.md](../ai/QUALITY_GATES.md). Thresholds are configuration, not code constants, and changes require an evaluation record.

## 9. Success metrics

The MVP is successful when:

1. One existing 60-second short is reproduced end to end through the application, with output quality accepted by the founder in a blind comparison against the existing workflow.
2. The reproduction records exact model versions, GPU type, provisioning time, model-loading time, inference time, render time, total cost, retries and QC measurements.
3. A shot can be regenerated without rerunning the full pipeline, and the resulting version is traceable.
4. No GPU session outlives its configured idle window during a normal run.
5. Cost per accepted output is measurable and compared with the baseline ($9.06 for the first tested short and about $1 for a same-style repeat, both including their stated scope).
6. A failed stage resumes from a checkpoint or fails with an actionable error; it never appears successful.
7. Every generated asset has a complete provenance record.

Cost reduction is a target to be measured, not a promised percentage. See [COST_OPTIMIZATION.md](../infrastructure/COST_OPTIMIZATION.md).

## 10. Constraints and dependencies

- The founder's existing scripts, skill files, workflows and reference media are required for Milestone 0; they are not yet in this repository.
- Premium voice and avatar quality are product requirements until open alternatives pass evaluation. ElevenLabs and HeyGen are the current quality baselines.
- InfiniteTalk is the best open lip-sync option tested, but it did not match HeyGen and has Hindi audio-encoder limitations.
- Several candidate models are excluded for licensing or quality reasons; see [LICENSING_POLICY.md](../ai/LICENSING_POLICY.md) and [MODEL_REGISTRY.md](../ai/MODEL_REGISTRY.md).
- GPU availability and pricing change; infrastructure decisions must be revisited with measured data.
- The product name, brand and commercial licence are unresolved.

## 11. Assumptions

- The founder can supply the existing pipeline artifacts and at least one reference input/output pair for reproduction.
- The existing paid accounts (ElevenLabs team account, HeyGen twin, RunPod) remain available for baseline reproduction.
- The first deployment is single-tenant and operated by the founder's team.
- A 60-second short is a sufficient first reference; longer videos follow once the shot-level model is stable.
- Object storage and PostgreSQL are acceptable dependencies for the target deployment.

Assumptions that become blocking are tracked in [OPEN_QUESTIONS.md](../project/OPEN_QUESTIONS.md).

## 12. Release criteria

The MVP is not released until the [acceptance criteria](ACCEPTANCE_CRITERIA.md) are met, the security and retention documents are reflected in the implementation, and the run manifest can reproduce a reviewed export without undocumented manual steps.
