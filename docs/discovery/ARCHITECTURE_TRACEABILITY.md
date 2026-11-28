# Architecture Traceability

| Field | Value |
|---|---|
| Status | Milestone 0 mapping; target architecture validated in Phase 2 |
| Last updated | 2026-11-28 |
| Related | [Existing workflow](EXISTING_WORKFLOW.md), [component interfaces](../architecture/COMPONENT_INTERFACES.md), [component design](../architecture/COMPONENT_DESIGN.md), [ADRs](../architecture/decisions/), [PRD](../product/PRD.md) |

## 1. Purpose

This document traces each part of the founder's current workflow to the target architecture. It answers four questions for every stage:

1. Which target component owns it?
2. Which port or contract does it cross?
3. Which requirement and decision justify it?
4. Should the existing implementation be wrapped, ported, replaced, rehosted or retired?

The mapping is a plan, not evidence that the current implementation behaves as described. Confidence labels follow [EXISTING_WORKFLOW.md](EXISTING_WORKFLOW.md).

## 2. Integration strategies

| Strategy | Meaning | When to use |
|---|---|---|
| **Wrap** | Keep the existing implementation and call it through an owned adapter | Behaviour is valuable, code is usable, interface can be isolated |
| **Port** | Rewrite the logic inside an owned module while preserving observed behaviour | Logic is valuable but embedded in prompts, notebooks or shell scripts |
| **Replace** | Substitute a new implementation | Existing approach is unlicensed, unreliable, unmaintainable or not a real component |
| **Rehost** | Keep the implementation but move it to a managed runtime | Code is fine; the problem is where or how it runs |
| **Retire** | Remove entirely | No longer needed in the target product |

A component may need more than one strategy, for example wrap the model execution but replace the controller around it.

## 3. Stage-to-architecture map

| Current stage | Target capability | Owning component | Port / contract | Primary requirements | ADR | Strategy | Confidence |
|---|---|---|---|---|---|---|---|
| Approved script | Script versioning and approval | Projects and plans | Domain API, `Approval` | FR-001, FR-002, FR-014 | ADR-001 | Replace (human workflow) | Reported |
| Plate sheet generation | Planning and validation | Projects and plans | `Plate` contract | FR-010–FR-015 | ADR-001 | Port prompts, replace controller | Reported |
| Voice synthesis | Voice generation | Provider adapters + Model routing | `ProviderPort`, `RoutingPort` | FR-020–FR-025 | ADR-003 | Wrap ElevenLabs | Reported |
| Voice post-processing | Media processing | Media and render | Media pipeline contract | FR-022, FR-053 | ADR-001 | Port scripts | Reported |
| Presenter generation | Avatar / lip-sync generation | Provider adapters + Model routing | `ProviderPort` | FR-040–FR-044 | ADR-003 | Wrap HeyGen; wrap InfiniteTalk experimentally | Reported |
| AI stills | Image generation | Provider adapters + GPU lifecycle | `ProviderPort`, `GpuPoolPort` | FR-030, FR-031 | ADR-003, ADR-005 | Wrap ComfyUI workflow, rehost on GPU workers | Reported |
| AI motion | Image-to-video generation | Provider adapters + GPU lifecycle | `ProviderPort`, `GpuPoolPort` | FR-032–FR-036 | ADR-003, ADR-005 | Wrap ComfyUI workflow, rehost on GPU workers | Reported |
| Motion graphics and proof | Composition | Media and render | Render/composition contract | FR-050–FR-052 | ADR-001 | Wrap HyperFrames initially | Reported |
| Music and SFX mix | Audio assembly and mastering | Media and render | Media pipeline contract | FR-052, FR-053 | ADR-001 | Port mix scripts; replace unclear sources | Reported |
| Render at 25 FPS | Final render | Media and render | Render contract | FR-053, FR-054 | ADR-001 | Wrap FFmpeg/HyperFrames output | Reported |
| QC | Automated quality gates | Quality control | `QcReport` | FR-024, FR-042, FR-043 | ADR-001 | Port scripts | Reported |
| Human review | Approval and export gates | Runs and stages + Projects and plans | Approval API | FR-061, FR-066 | ADR-001 | Replace (new UI) | Reported |
| Controller (Claude Code) | Orchestration | Job engine + Runs and stages | `JobQueue` | FR-003, FR-064, NFR-001 | ADR-002 | Replace | Reported |
| Skill files and prompts | Planning rules | Projects and plans | Prompt/template versioning | FR-010–FR-013 | ADR-001 | Port | Reported |
| RunPod pods | GPU capacity | GPU lifecycle | `GpuPoolPort` | FR-072–FR-074, NFR-006 | ADR-005 | Wrap provider, rehost workloads | Reported |
| Local Mac | CPU render and QC | Worker tier | Worker contract | NFR-006 | ADR-001 | Rehost as CPU worker | Reported |
| Billing and credits | Cost accounting | Cost ledger | `CostEntry` | FR-072, FR-073, NFR-008 | ADR-001 | Replace with ledger | Reported |

## 4. Detailed traceability

### 4.1 Script and planning

**Current:** approved script, then a JSON plate sheet produced with Claude Code and skill files.

**Target:**

- `Projects and plans` owns script versions, plate-sheet versions and approvals.
- `Plate` is the canonical contract, defined in [COMPONENT_INTERFACES.md](../architecture/COMPONENT_INTERFACES.md).
- Validation is an explicit module, not a prompt instruction.
- Approval freezes a version and records the actor.

**Gap:** the founder's plate schema and validation rules are unknown (U-001, U-004). The target schema is therefore provisional and must not be presented as compatible.

**Trace:** FR-001–FR-004, FR-010–FR-015; ADR-001.

### 4.2 Voice

**Current:** ElevenLabs Eleven v4 with a professional clone, Devanagari text preparation, pause squeeze, 1.2x speed and -14 LUFS normalisation.

**Target:**

- `ProviderPort` adapter for ElevenLabs, selected by `RoutingPort` for the `voice.synthesize` capability.
- Voice takes are versioned assets linked to text, settings and provider request ID.
- Post-processing is a deterministic media pipeline step, not a hidden script.
- QC produces a `QcReport` with similarity and CER.

**Gap:** exact model string, flags, pause algorithm order and similarity method are unknown (U-011–U-018, U-055, U-056).

**Trace:** FR-020–FR-025; ADR-003, ADR-004.

### 4.3 Presenter and lip-sync

**Current:** HeyGen Avatar 6 at ~$0.089/s, with InfiniteTalk tested as an open alternative.

**Target:**

- HeyGen is a provider adapter with cost metering per generated second.
- InfiniteTalk is an experimental GPU-backed route behind the same capability, admitted only after evaluation.
- Quality floor and licence gates apply before selection.
- Consent records are linked to the avatar assets and provider use.

**Gap:** avatar IDs, segment boundaries, input format and InfiniteTalk settings are unknown (U-019–U-026). The open route is not quality-equivalent today.

**Trace:** FR-040–FR-044; ADR-003, ADR-005; [QUALITY_GATES.md](../ai/QUALITY_GATES.md).

### 4.4 AI stills and motion

**Current:** Qwen-Image with Lightning 8-step LoRA; Wan 2.2 I2V A14B fp8 with LightX2V 4-step LoRA; ComfyUI headless API on rented GPUs.

**Target:**

- ComfyUI workflows are versioned artifacts, not mutable local files.
- GPU workers pull jobs, load only the required models and report timings.
- Every output records workflow hash, model files, seeds and settings.
- Stills are approved before motion; motion cannot invent a new establishing frame.

**Gap:** workflow JSON, sampler settings, resolution, seeds and model file identities are unknown (U-027–U-039). The target cannot claim visual equivalence until the reproduction runs.

**Trace:** FR-030–FR-036; ADR-003, ADR-005; [GPU_ORCHESTRATION.md](../infrastructure/GPU_ORCHESTRATION.md).

### 4.5 Composition, audio and render

**Current:** HyperFrames, HTML, GSAP, Three.js and FFmpeg; editorial design kit; 25 FPS output; -14 LUFS.

**Target:**

- `Media and render` owns composition inputs, audio assembly and final render.
- HyperFrames is wrapped behind a render contract initially; it is not allowed to become the orchestrator.
- Render settings are recorded so a run is reproducible.
- Music and SFX carry licence metadata and are blocked at export if unclear.

**Gap:** project structure, render command, fonts, mix chain and music sources are unknown (U-040–U-054). HyperFrames' licence and long-term fit are not established.

**Trace:** FR-050–FR-054; ADR-001, ADR-004.

### 4.6 QC and review

**Current:** Whisper CER, SyncNet, MediaPipe mouth metrics, custom similarity scripts and human review.

**Target:**

- `Quality control` runs versioned metrics per artifact and on the master.
- Thresholds are configuration, not code constants.
- Failed gates block export unless a human accepts the risk with a recorded reason.
- Review compares at most two scored candidates per shot.

**Gap:** SyncNet threshold, similarity implementation, CER normalisation and per-language calibration are unknown (U-055–U-062).

**Trace:** FR-024, FR-042, FR-043, FR-061–FR-066; [QUALITY_GATES.md](../ai/QUALITY_GATES.md).

### 4.7 Orchestration

**Current:** Claude Code with skill files and individual Python tools acts as the controller.

**Target:**

- `Job engine` and `Runs and stages` replace the controller.
- Jobs are durable, leased and idempotent.
- Stage transitions are explicit; approvals are gates.
- The production path never requires a coding assistant.

**Gap:** the existing controller's actual sequence, retries and manual interventions are unknown (U-005, U-021, U-072). Until the artifacts arrive, the replacement cannot be checked against real behaviour.

**Trace:** FR-003, FR-064, NFR-001, NFR-002, NFR-009, NFR-012; ADR-002.

### 4.8 GPU lifecycle

**Current:** manual RunPod pods, ~12 minutes setup, ~75 GB download per session, manual teardown.

**Target:**

- `GpuPoolPort` with acquire, release, terminate and reconcile.
- Resident pools by capability and hardware class.
- Preflight, model cache, idle shutdown and orphan detection.
- Cost metering per session and per job.

**Gap:** current setup script, image, cache strategy and teardown discipline are unknown (U-063–U-067). The reported waste is the justification, not a measured baseline.

**Trace:** FR-072–FR-074, NFR-006, NFR-009; ADR-005.

### 4.9 Cost and audit

**Current:** provider dashboards and aggregate figures; no per-stage ledger reported.

**Target:**

- `Cost ledger` records provider calls and GPU sessions with run, stage, shot and provider attribution.
- `Audit` records approvals, configuration changes, credential changes and exports.
- Cost per accepted output is queryable.

**Gap:** no historical per-stage cost data exists (U-068–U-070). The ledger design is sound but unvalidated against real billing.

**Trace:** FR-072, FR-073, FR-075, NFR-008; ADR-001, ADR-004.

## 5. Requirement coverage by component

| Component | Functional requirements | Non-functional requirements |
|---|---|---|
| Identity and access | FR-001, FR-061, FR-075 | NFR-004, NFR-005 |
| Workspace policy | FR-004, FR-052, FR-066 | NFR-005, NFR-007, NFR-011 |
| Projects and plans | FR-001–FR-004, FR-010–FR-015 | NFR-012 |
| Runs and stages | FR-003, FR-014, FR-060–FR-066 | NFR-001, NFR-003, NFR-009, NFR-012 |
| Asset registry | FR-002, FR-004, FR-023, FR-063 | NFR-004, NFR-011 |
| Job engine | FR-064 | NFR-001, NFR-002, NFR-009 |
| Model routing | FR-020, FR-041, FR-070, FR-071 | NFR-007 |
| Provider adapters | FR-020, FR-040, FR-041 | NFR-002, NFR-005 |
| GPU lifecycle | FR-030, FR-032, FR-074 | NFR-006, NFR-009 |
| Media and render | FR-022, FR-050–FR-054, FR-065 | NFR-006 |
| Quality control | FR-024, FR-042, FR-043, FR-061 | NFR-010 |
| Cost ledger | FR-072, FR-073 | NFR-008 |
| Audit | FR-075 | NFR-011 |

## 6. Gaps between current and target

| Gap | Current state | Target requirement | Consequence |
|---|---|---|---|
| No durable job model | Coding assistant executes steps | Durable, leased jobs | Controller must be replaced, not wrapped |
| No explicit approval gates | Human judgement in conversation | Attributed approvals that freeze versions | Workflow changes, not just software |
| No asset registry | Files in folders and chat | Immutable versions with provenance | Migration and naming work required |
| No cost attribution | Aggregate provider spend | Per-stage, per-shot ledger | Instrumentation must be added from day one |
| No licence gate | Models chosen ad hoc | Unverified licence cannot be selected | Some current models may be excluded |
| No automated QC gate on export | Human review | Blocking gates with recorded overrides | Process change for the founder |
| No GPU lifecycle management | Manual pods | Pools, preflight, idle shutdown | Largest measurable waste source |
| Prompts as configuration | Skill files in a coding assistant | Versioned templates and validation | Prompt logic must be ported carefully |
| Undocumented render project | HyperFrames project | Reproducible render manifest | Reproduction depends on founder artifacts |

## 7. What must not be claimed

- That the target architecture is a refactor of existing code. Most of it is new.
- That wrapping ComfyUI preserves the founder's quality. Only the reproduction run can show that.
- That the target `Plate` schema matches the founder's.
- That open models meet the HeyGen baseline.
- That reported costs are unit economics. They are observations.
- That HyperFrames is a long-term dependency. It is an initial composition option.

## 8. Verification checklist

Traceability is complete for Milestone 0 when:

- every current stage has an owning target component;
- every component has at least one requirement and one ADR trace;
- every integration strategy has a stated reason;
- every unknown that affects a mapping is in [UNKNOWN_CONFIGURATIONS.md](UNKNOWN_CONFIGURATIONS.md);
- no mapping depends on an unstated assumption;
- the reproduction plan can test the highest-risk mappings first.

## 9. Highest-risk mappings to test in Milestone 1

1. ComfyUI workflow wrapping preserves still and motion quality.
2. Plate schema port preserves timing and layout semantics.
3. Voice post-processing port preserves similarity and pacing.
4. HyperFrames wrapping preserves composition output.
5. QC metric port reproduces the reported values.
6. GPU session measurement confirms or refutes the reported waste.

If any of these fails, the affected strategy changes from wrap or port to replace, and the roadmap effort must be revised.
