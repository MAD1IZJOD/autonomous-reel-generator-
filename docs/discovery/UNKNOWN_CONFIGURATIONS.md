# Unknown Configurations

| Field | Value |
|---|---|
| Status | Open register; no item has been verified against founder artifacts |
| Last updated | 2026-11-28 |
| Related | [Founder materials checklist](FOUNDER_MATERIALS_CHECKLIST.md), [existing workflow](EXISTING_WORKFLOW.md), [baseline reproduction plan](BASELINE_REPRODUCTION_PLAN.md) |

## 1. How to read this register

Every configuration that is not directly evidenced is listed here. An item is closed only when one of these is true:

- the founder supplies the artifact and it is inspected;
- the behaviour is measured in a controlled run;
- a written decision explicitly replaces it, with the trade-off recorded.

An item must never be closed by assumption. Where a decision is needed before evidence arrives, the fallback policy below applies and is marked as a temporary product decision, not as a reproduction of the founder's setup.

Fields:

- **Evidence:** what is currently known and how strong it is.
- **Resolution:** the cheapest reliable way to close the item.
- **Blocks:** the milestone that cannot be completed without it.
- **Fallback:** what the project will do if the item cannot be obtained.

## 2. Planning and plate sheet

| ID | Unknown | Why it matters | Evidence | Resolution | Blocks | Fallback |
|---|---|---|---|---|---|---|
| U-001 | Exact plate sheet JSON schema, field names and required/optional fields | The plate sheet is the pipeline's central contract | Prose description only | Inspect three real plate sheets (M-010) | M0 | Define our own schema, mark as incompatible until validated |
| U-002 | How shot duration is chosen (2–6 s rule vs voice timing) | Drives motion clip length, cost and pacing | "2–6 second shot" reported | Compare plate durations with voice track durations | M1 | Derive duration from voice for explainer; fixed max for story |
| U-003 | Whether one plate equals one shot or can contain multiple cuts | Affects IDs, retakes and QC granularity | Not stated | Inspect plate sheets and final videos | M0 | Model one plate as one shot with optional sub-cuts |
| U-004 | Validation rules applied to a plate sheet | Prevents invalid plans reaching paid stages | "Human review" reported | Inspect planner prompts and validator code (M-012) | M0 | Implement schema, timing, reference and completeness checks |
| U-005 | Whether the plate sheet stores absolute times or durations only | Determines re-timing after voice changes | Not stated | Inspect plate sheets | M0 | Store durations plus derived absolute times |
| U-006 | How captions are represented and timed | Affects render and QC | Field exists, format unknown | Inspect plate sheet and render project | M1 | Generate captions from voice alignment |
| U-007 | How SFX cues are represented | Affects mix automation | Field exists, format unknown | Inspect plate sheets and mix script | M1 | Use `{id, at_s}` cue objects |
| U-008 | Whether visual references are asset IDs, paths or prompts | Affects asset linking and reproducibility | Not stated | Inspect plate sheets | M0 | Use versioned asset references with provenance |
| U-009 | Language mix rules and Devanagari policy per field | Pronunciation and caption quality | Devanagari reported for Hindi/English words | Inspect prompts and examples (M-032) | M1 | Store both original and pronunciation text |
| U-010 | Script length limits and target duration rules | Cost and scope control | 60-second shorts reported | Inspect scripts and planner | M1 | Enforce configurable word/duration budgets |

## 3. Voice

| ID | Unknown | Why it matters | Evidence | Resolution | Blocks | Fallback |
|---|---|---|---|---|---|---|
| U-011 | Whether voice is generated as one track or per plate | Retake granularity, storage and timing | Not stated | Inspect outputs and scripts | M0 | Generate per plate, assemble a master track |
| U-012 | Exact ElevenLabs model version string | "Eleven v4" is a family name | Reported v4 | Inspect API calls (M-030, M-031) | M1 | Pin the current v4 model ID at run time and record it |
| U-013 | Whether speaker boost or other flags are enabled | Affects similarity and accent | Not stated | Inspect settings | M1 | Disable unlisted flags and record defaults |
| U-014 | Exact pause-squeeze algorithm and threshold | Reported >0.3 s to ~0.2 s, implementation unknown | Reported | Inspect script (M-033) | M1 | Implement silence detection with documented threshold |
| U-015 | Whether 1.2x speed is applied before or after pause squeeze | Changes timing and pitch handling | Not stated | Inspect script | M1 | Apply pause squeeze, then time-stretch, then loudness |
| U-016 | Loudness normalisation tool and true-peak target | Delivery compliance | -14 LUFS reported; true peak unknown | Inspect mix script (M-062) | M1 | Use FFmpeg loudnorm two-pass, -14 LUFS, -1.5 dBTP |
| U-017 | Pronunciation glossary contents and update process | Major retake driver | Exists, contents unknown | Obtain glossary (M-032) | M1 | Build glossary incrementally from retake causes |
| U-018 | Retry policy for failed pronunciation or CER | Cost and latency | Whisper retake loops reported | Inspect controller | M1 | Cap retries per line, then flag for human |

## 4. Presenter and lip-sync

| ID | Unknown | Why it matters | Evidence | Resolution | Blocks | Fallback |
|---|---|---|---|---|---|---|
| U-019 | HeyGen avatar IDs, twin orientation and plan tier | Baseline reproduction and cost | Avatar 6 reported; IDs unknown | Obtain IDs and plan (M-040) | M1 | Use founder-supplied IDs at run time |
| U-020 | How presenter segments are cut (per plate, per block, per scene) | Cost, lip-sync continuity and retakes | "Face blocks" reported | Inspect requests (M-041) | M0 | Cut per plate, merge where continuity requires |
| U-021 | Whether explainer and character profiles are separate code paths | Determines orchestration model | Two profiles reported | Inspect controller (M-001) | M0 | Model profiles as configuration, not code forks |
| U-022 | Exact input format sent to HeyGen (audio + image, script, or both) | Determines API adapter shape | Not stated | Inspect one request | M1 | Support audio-driven generation first |
| U-023 | Resolution, aspect ratio and frame rate requested from HeyGen | Visual match and upscaling needs | Portrait and landscape twins reported | Inspect requests | M1 | Match target output at 1080×1920 or 1920×1080, 25 FPS |
| U-024 | InfiniteTalk production settings and prompt | Open fallback quality | Model named; settings unknown | Inspect workflow (M-023) | M2 | Keep HeyGen as baseline; do not promote open model |
| U-025 | Jaw over-stretch detection method | Reported failure mode without a gate | Reported | Inspect QC scripts (M-070) | M2 | Add visual review flag; no automated gate initially |
| U-026 | Consent scope for the trained twin | Commercial export legality | Agreement referenced, not supplied | Obtain agreement (M-044) | Commercial launch | Block export of twin footage until documented |

## 5. Image generation

| ID | Unknown | Why it matters | Evidence | Resolution | Blocks | Fallback |
|---|---|---|---|---|---|---|
| U-027 | Exact Qwen-Image model file and quantisation | Reproducibility and licence | Family named | Obtain file list (M-024) | M1 | Pin a specific file and record hash |
| U-028 | Lightning LoRA version and weight | Quality and step count | "8-step" reported | Inspect workflow (M-020) | M1 | Pin the workflow's LoRA and strength |
| U-029 | Sampler, scheduler, steps, CFG and shift | Direct quality impact | Unknown | Inspect workflow JSON | M1 | Use workflow values, not community defaults |
| U-030 | Resolution, aspect ratio and crop policy | Composition and upscaling | Unknown | Inspect workflow | M1 | Generate at target aspect, avoid generative upscale |
| U-031 | Reference image strategy and identity anchoring | Character consistency | Qwen-Image-Edit-2511 reported | Inspect workflow and examples (M-027) | M1 | Use explicit reference sets per subject |
| U-032 | Candidate count and selection rule per shot | Cost and quality | Unknown | Inspect controller and billing | M1 | Generate one candidate, retry on QC failure |
| U-033 | Seed policy | Reproducibility vs variety | Unknown | Inspect workflow and logs | M1 | Record seed; reuse for retakes of the same shot |

## 6. Motion generation

| ID | Unknown | Why it matters | Evidence | Resolution | Blocks | Fallback |
|---|---|---|---|---|---|---|
| U-034 | Exact Wan 2.2 I2V model file, fp8 variant and LoRA | Reproducibility | Family named | Obtain file list (M-024) | M1 | Pin exact file and hash |
| U-035 | LightX2V LoRA version and strength | Quality and step count | 4-step reported | Inspect workflow (M-022) | M1 | Use workflow values |
| U-036 | Resolution, frame count, FPS and duration limits | Cost and motion quality | Unknown | Inspect workflow | M1 | Generate 4–5 s at 480p/720p per tested setting |
| U-037 | Sampler, guidance, shift and step count | Quality and speed | Unknown | Inspect workflow | M1 | Use workflow values |
| U-038 | Motion prompt template and negative prompt | Controls motion and artifacts | Unknown | Inspect prompts (M-002) | M1 | Store prompt template as a versioned artifact |
| U-039 | Policy for motion beats longer than 2.4 s | Reported pacing rule | "≤2.4 s where possible" | Inspect planner rules | M2 | Warn, do not hard-fail, until validated |

## 7. Composition and render

| ID | Unknown | Why it matters | Evidence | Resolution | Blocks | Fallback |
|---|---|---|---|---|---|---|
| U-040 | HyperFrames version and project structure | Reproduction and portability | Named only | Obtain project (M-050) | M1 | Build our own composition layer; treat HyperFrames as reference |
| U-041 | How HyperFrames is driven (CLI, API, headless browser) | Automation design | Unknown | Inspect scripts | M1 | Use headless browser rendering with deterministic waits |
| U-042 | Fonts, textures, colour tokens and grade | Visual identity | Design kit referenced | Obtain kit (M-052) | M1 | Use founder kit only after licence check |
| U-043 | Layout vocabulary and rules | Plate sheet semantics | Field exists | Inspect plate sheets and components | M1 | Define layout IDs from observed examples |
| U-044 | Transition and timing rules | Pacing and polish | Unknown | Inspect project | M2 | Default to hard cuts and simple wipes |
| U-045 | Final resolution, codec, bitrate, pixel format and audio codec | Delivery compliance | 25 FPS only | Inspect render command (M-053) | M1 | H.264 High, 1080×1920, 25 FPS, AAC 48 kHz |
| U-046 | Render hardware and expected duration | Capacity planning | Mac reported | Measure one render | M1 | CPU render on Mac-class hardware |
| U-047 | Caption burn-in vs sidecar | QC and platform requirements | Unknown | Inspect outputs | M2 | Burn in for shorts; keep sidecar as evidence |
| U-048 | How real proof assets are captured and cleared | Core format differentiator | Referenced | Obtain inventory (M-063) | M2 | Require explicit proof manifest per project |

## 8. Audio mix

| ID | Unknown | Why it matters | Evidence | Resolution | Blocks | Fallback |
|---|---|---|---|---|---|---|
| U-049 | Music source and licence | Export legality | Unknown | Obtain licences (M-060) | Commercial launch | Use only cleared library tracks |
| U-050 | SFX library and procedural generation scripts | Mix quality and automation | Procedural scripts reported | Obtain scripts (M-061) | M1 | Start with a small cleared SFX set |
| U-051 | Ducking and sidechain rules | Voice intelligibility | Unknown | Inspect mix | M2 | Apply documented ducking under voice |
| U-052 | Sample rate and channel layout | Render compatibility | Unknown | Inspect mix and render | M1 | 48 kHz stereo |
| U-053 | Whether music is beat-matched to cuts | Pacing quality | Unknown | Inspect examples | P3 | No beat matching initially |
| U-054 | Loudness measurement method (integrated vs short-term) | QC pass/fail | -14 LUFS reported | Inspect QC script | M1 | Integrated LUFS with true-peak limit |

## 9. QC

| ID | Unknown | Why it matters | Evidence | Resolution | Blocks | Fallback |
|---|---|---|---|---|---|---|
| U-055 | Voice similarity model and exact computation | Reported 0.96–0.97 is not reproducible without the method | Value reported | Obtain script (M-070) | M1 | Use a documented speaker-embedding cosine metric |
| U-056 | Whisper model size and CER normalisation rules | CER depends heavily on normalisation | CER ≤0.2 reported | Obtain script and samples | M1 | Pin model and publish normalisation rules |
| U-057 | SyncNet threshold and window | Lip-sync gate calibration | Not stated | Obtain script (M-070) | M2 | Report score; gate only after calibration |
| U-058 | MediaPipe mouth metrics implementation | Mean 0.28, P90 0.42, ~68% open reported | Values reported | Obtain script | M1 | Reimplement with documented landmarks |
| U-059 | Whether QC runs per artifact or only on the master | Retake cost and latency | Unknown | Inspect controller | M1 | Run per artifact plus master |
| U-060 | Black-frame, duplicate-frame and freeze detection | Delivery defects | Mentioned as checks | Obtain script | M1 | Use FFmpeg blackdetect/freezedetect |
| U-061 | Human review rubric and sign-off | Acceptance depends on judgement | Contact sheets mentioned | Obtain template (M-072) | M1 | Define a structured rubric with defect codes |
| U-062 | Thresholds per language, presenter and profile | One threshold may not fit all | Unknown | Calibrate on accepted outputs | M2 | Single global threshold, flagged as provisional |

## 10. Infrastructure, cost and operations

| ID | Unknown | Why it matters | Evidence | Resolution | Blocks | Fallback |
|---|---|---|---|---|---|---|
| U-063 | RunPod GPU types, regions and images | Cost and performance reproduction | L40/L40S/A100 mentioned | Obtain notes (M-081) | M1 | Start with L40S and A100 80 GB candidates |
| U-064 | Pod setup and model download procedure | ~12 min and ~75 GB per session | Reported | Obtain script (M-082) | M1 | Build cached image and volume strategy |
| U-065 | Whether model weights are baked, mounted or downloaded | Startup time and licence constraints | Unknown | Inspect setup | M2 | Cache on network volume; never commit weights |
| U-066 | ComfyUI version and custom node set | Workflow compatibility | Unknown | Obtain environment export (M-025) | M1 | Pin versions in a worker image |
| U-067 | How GPU sessions are started and stopped today | Cost leakage and orchestration design | Manual pod setup reported | Inspect controller | M2 | Owned pool lifecycle with idle shutdown |
| U-068 | Actual per-stage timing in a clean run | Baseline and capacity planning | Only aggregate figures reported | Measure in M1 | M1 | Instrument every stage from the first run |
| U-069 | Actual cost per stage, including retries | Unit economics | Aggregate ~$9.06 / ~$1 reported | Reconcile billing (M-080) | M1 | Cost ledger with provider usage records |
| U-070 | Storage locations and retention today | Data model and compliance | Unknown | Inspect layout (M-092) | M2 | Object storage with explicit retention policy |
| U-071 | Concurrency and throughput achieved today | Queue and pool sizing | Unknown | Measure or inspect logs | M3 | Start single-run, scale after measurement |
| U-072 | Failure and retry rates per stage | Reliability targets | Anecdotal | Instrument M1 | M2 | Record every failure; no invented targets |

## 11. Legal and commercial

| ID | Unknown | Why it matters | Evidence | Resolution | Blocks | Fallback |
|---|---|---|---|---|---|---|
| U-073 | Commercial licence status of each model in use | Product cannot ship on unclear licences | Some exclusions already known | Obtain licence list (M-100) | Commercial launch | Treat unclear as non-commercial |
| U-074 | Whether generated outputs may be used commercially per provider terms | Client delivery | Unknown | Review provider terms | Commercial launch | Legal review before first paid delivery |
| U-075 | Rights to proof assets and client material | Publication risk | Unknown | Obtain constraints (M-101) | Commercial launch | Require rights confirmation per asset |
| U-076 | Data residency and retention obligations | Deployment design | Unknown | Obtain requirements (M-102) | Enterprise | Default to documented retention policy |
| U-077 | Brand and likeness usage constraints | Marketing and product scope | Unknown | Obtain summary (M-103) | Commercial launch | No public use of likeness without approval |
| U-078 | Whether the founder's accounts may be used for automated production | Terms-of-service risk | Unknown | Review provider terms | Commercial launch | Design for customer-owned accounts |

## 12. Temporary decisions if evidence does not arrive

If Milestone 1 must start before all items are closed, only these temporary decisions are permitted, and each must be recorded in the run manifest as a deviation:

| Area | Temporary decision | Explicitly not claimed |
|---|---|---|
| Plate sheet | Use the schema in [COMPONENT_INTERFACES.md](../architecture/COMPONENT_INTERFACES.md) | Not the founder's schema |
| Voice | Per-plate generation, FFmpeg post-processing | Not the founder's exact chain |
| Presenter | HeyGen only | Open model quality not reproduced |
| Image | Workflow values as supplied, else pinned defaults | Not the founder's quality |
| Motion | 4–5 s clips, recorded settings | Not the founder's quality |
| Render | H.264, 25 FPS, 1080×1920 | Not confirmed delivery spec |
| QC | Documented metrics with provisional thresholds | Not the founder's thresholds |
| Cost | Measured, not reconciled to invoices | Not a validated unit cost |

## 13. Register maintenance

- Add an item when a configuration is referenced but not evidenced.
- Close an item only with a link to the artifact, measurement or decision.
- When an item is closed, update [EXISTING_WORKFLOW.md](EXISTING_WORKFLOW.md) and [ARCHITECTURE_TRACEABILITY.md](ARCHITECTURE_TRACEABILITY.md).
- Keep the register ordered by area; do not renumber closed items.
