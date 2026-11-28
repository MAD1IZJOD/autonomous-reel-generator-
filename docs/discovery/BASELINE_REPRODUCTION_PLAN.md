# Baseline Reproduction Plan

| Field | Value |
|---|---|
| Status | Planned; not executed |
| Last updated | 2026-11-28 |
| Related | [Existing workflow](EXISTING_WORKFLOW.md), [dependency graph](WORKFLOW_DEPENDENCY_GRAPH.md), [unknown configurations](UNKNOWN_CONFIGURATIONS.md), [acceptance criteria](../product/ACCEPTANCE_CRITERIA.md), [cost optimisation](../infrastructure/COST_OPTIMIZATION.md) |

## 1. Objective

Reproduce one existing 60-second short end to end using the founder's own scripts, models and settings, then repeat it once in the same style, and produce evidence that answers four questions:

1. **Can it be reproduced at all** from documented steps and supplied artifacts?
2. **What does it actually cost**, including setup, failed attempts and retries?
3. **How long does each stage actually take**, including provisioning and model loading?
4. **Does the output meet the founder's quality bar**, measured rather than asserted?

This is a measurement exercise, not a product build. No application code is written during Milestone 1 beyond throwaway instrumentation scripts, which are recorded but not merged as product code.

## 2. Non-goals

- Improving quality or reducing cost.
- Replacing any model or provider.
- Building the orchestration platform.
- Automating the whole pipeline.
- Supporting more than one reference video.

Any improvement idea discovered during the run is logged and deferred.

## 3. Entry criteria

The reproduction must not start until:

- every P0 item in [FOUNDER_MATERIALS_CHECKLIST.md](FOUNDER_MATERIALS_CHECKLIST.md) is delivered or explicitly waived;
- the founder confirms which reference video is the target and that it is acceptable to reproduce;
- written permission and a spend cap exist for paid providers (M-083);
- secrets are available through a secure channel, not committed;
- the exact model files and provider versions are identified, not just family names;
- a clean environment can be created on both the Mac and the GPU provider.

If any of these is missing, the run is deferred rather than approximated.

## 4. Reference package

| Item | Description | Source |
|---|---|---|
| Reference script | The approved script for the target video | Founder |
| Reference plate sheet | The plate sheet used to produce it | Founder |
| Reference output | The accepted final video | Founder |
| Source artifacts | Voice, presenter segments, stills, motion clips, project files if retained | Founder |
| Style inputs | Brand kit, proof assets, music/SFX cues | Founder |
| Settings | Model, workflow, provider and render settings | Founder |

The reference output is the comparison target. If source artifacts were not retained, that is recorded as a gap and the comparison uses only the final video.

## 5. Experiment design

Three runs, each with a distinct purpose:

| Run | Name | Starting state | Purpose |
|---|---|---|---|
| A | Cold reproduction | Fresh machine state, empty model cache, new GPU session | Measures true first-run cost and setup overhead |
| B | Warm repeat | Same style, warm model cache where legitimately reusable, new session | Measures repeat-run cost |
| C | Variance repeat | Same inputs as B, independent session | Distinguishes stable measurements from noise |

Run C is optional if A and B already show low variance, but is required if either differs from the founder's reported figures by more than 25%.

### 5.1 Controlled variables

- Same script, plate sheet, references and output specification across runs.
- Same provider accounts and plan tiers.
- Same model files and workflow versions.
- Same hardware class where possible.
- Same time-of-day band to reduce provider contention effects, if practical.

### 5.2 Variables to record, not control

- Provider queue latency.
- GPU availability and assigned region.
- Network throughput during model download.
- Human decision time.
- Retry counts caused by stochastic generation.

## 6. Environment plan

### 6.1 Local machine

| Item | Requirement |
|---|---|
| Hardware | Mac M2 16 GB, or the founder's actual machine if different |
| OS and tools | Recorded exactly, including FFmpeg, Python, Node and Whisper versions |
| Role | Voice post-processing, QC, composition, render |
| State | Fresh user account or documented baseline snapshot for Run A |

### 6.2 GPU environment

| Item | Requirement |
|---|---|
| Provider | RunPod, matching the founder's account and region where possible |
| GPU | The type used in the reference production; L40S or A100 80 GB as candidates |
| Image | The founder's image or a documented equivalent |
| Model storage | Empty for Run A; documented cache state for Runs B and C |
| Network | Measured during download |
| Access | No interactive changes during timed stages; all commands scripted or logged |

### 6.3 Paid providers

- ElevenLabs: founder's plan and clone.
- HeyGen: founder's plan and avatar.
- Billing exports enabled for the run window.

## 7. Run procedure

Each run follows the same sequence. Every step has a start and end timestamp and an evidence artifact.

| # | Step | Recorded evidence |
|---|---|---|
| 1 | Freeze inputs and compute hashes | Input manifest with SHA-256 for script, plate sheet and references |
| 2 | Provision GPU session | Provider, GPU type, region, image, start/end, provisioning seconds |
| 3 | Install or start runtime | Versions, commands, duration |
| 4 | Download or mount models | Bytes, duration, throughput, cache state |
| 5 | Validate environment | Preflight results, missing dependencies, failures |
| 6 | Generate plate sheet if reproducing planning | Planner version, prompt version, output, human edits |
| 7 | Generate voice | Provider request IDs, characters, credits, duration, raw output |
| 8 | Post-process voice | Commands, parameters, output duration, loudness |
| 9 | Generate presenter segments | Request IDs, seconds, cost, duration, outputs |
| 10 | Generate stills | Workflow version, seeds, settings, count, duration, outputs |
| 11 | Approve stills | Approval decisions and reasons |
| 12 | Generate motion | Workflow version, seeds, settings, count, duration, outputs |
| 13 | Assemble composition | Project version, assets used, duration |
| 14 | Mix audio | Music/SFX used, processing chain, loudness |
| 15 | Render | Command, settings, duration, output hash |
| 16 | Run QC | Metrics, thresholds, pass/fail, defects |
| 17 | Human review | Reviewer, method, decision, defect list |
| 18 | Export and archive | Final file, manifest, cost ledger |
| 19 | Tear down GPU session | Stop time, idle time, final billing estimate |

### 7.1 Checkpoints

A run may only continue past a checkpoint when the evidence exists:

- **Checkpoint 1:** inputs hashed and environment validated.
- **Checkpoint 2:** voice passes similarity and CER gates, or deviations are recorded.
- **Checkpoint 3:** all stills approved.
- **Checkpoint 4:** all motion clips pass temporal checks.
- **Checkpoint 5:** render is complete and playable.
- **Checkpoint 6:** QC report and human decision are recorded.

## 8. Run manifest

Every run produces one manifest. The schema is provisional but the fields are mandatory.

```json
{
  "run_id": "rep-2026-12-01-a",
  "reference_id": "ref-short-001",
  "mode": "cold",
  "started_at": "2026-12-01T09:00:00Z",
  "finished_at": "2026-12-01T13:42:11Z",
  "inputs": {
    "script_hash": "sha256:...",
    "plate_sheet_hash": "sha256:...",
    "reference_output_hash": "sha256:..."
  },
  "environment": {
    "local": {"hardware": "Mac M2 16GB", "os": "...", "ffmpeg": "...", "python": "..."},
    "gpu": {"provider": "runpod", "type": "L40S", "region": "...", "image": "..."}
  },
  "stages": [
    {
      "name": "voice.synthesize",
      "model_id": "elevenlabs:...",
      "started_at": "...",
      "finished_at": "...",
      "duration_s": 0,
      "attempts": 1,
      "outcome": "succeeded",
      "cost_usd": 0,
      "evidence": ["staging:..."]
    }
  ],
  "artifacts": [
    {"kind": "voice", "storage_ref": "asset:...", "sha256": "...", "bytes": 0}
  ],
  "qc": [
    {"metric": "voice_similarity", "value": 0.0, "threshold": 0.0, "pass": true}
  ],
  "deviations": [
    {"item": "U-014", "decision": "documented fallback", "reason": "artifact not supplied"}
  ],
  "cost": {
    "gpu_usd": 0,
    "paid_api_usd": 0,
    "storage_usd": 0,
    "total_usd": 0
  },
  "human_time_minutes": 0,
  "result": "accepted"
}
```

### 8.1 Mandatory manifest fields

- exact model identifiers and versions, with no "latest";
- workflow or prompt version and hash;
- seeds and generation parameters;
- provider request or job IDs;
- GPU type, region, image and cache state;
- start and end timestamps for every stage;
- attempts, failures and causes;
- cost per stage and total;
- QC values and thresholds;
- deviations from the founder's reported setup.

## 9. Measurement protocol

### 9.1 Time

- Use UTC timestamps from a single clock source.
- Record wall-clock and active stage time separately.
- Record human waiting time and human working time separately.
- Treat provisioning and model download as first-class stages, not overhead to hide.

### 9.2 Cost

- GPU cost = billed session seconds × published or invoiced rate, including provisioning and idle time before termination.
- Paid API cost = provider usage records, not estimates from character counts alone.
- Storage and egress cost = recorded if billed separately.
- Failed attempts are costed, not discarded.
- Reconcile the ledger against provider billing exports where available; where not, mark the figure as estimated.

### 9.3 Quality

Use the metrics in [QUALITY_GATES.md](../ai/QUALITY_GATES.md) where they are defined, and record raw values:

| Metric | Reported baseline | Measurement |
|---|---|---|
| Voice similarity | ~0.96–0.97 | Speaker-embedding cosine similarity, method recorded |
| Whisper CER | ≤ 0.2 | Pinned model, documented text normalisation |
| Mouth opening mean | 0.28 | MediaPipe landmark ratio, method recorded |
| Mouth opening P90 | 0.42 | Same |
| Frames with mouth open | ~68% | Same |
| Frame rate | 25 FPS | Container and frame count check |
| Loudness | -14 LUFS | Integrated loudness, true peak recorded |
| Motion beat length | ≤ 2.4 s where possible | Shot duration distribution |

Additional recorded checks:

- black, frozen and duplicate frames;
- audio/video duration drift;
- caption sync;
- visible artifacts and identity drift;
- lip-sync score, even if the threshold is unknown.

### 9.4 Human review

- The founder reviews Run A and Run B blind against the reference output.
- Order is randomised and labels removed.
- The review records a preference, a confidence level and specific defects.
- Review time is recorded because it is a real production cost.

## 10. Cost and timing reconciliation

Produce a variance table against the founder's reported figures:

| Measure | Reported | Run A | Run B | Run C | Variance | Explanation |
|---|---|---|---|---|---|---|
| GPU setup | ~12 min | | | | | |
| Model download | ~75 GB | | | | | |
| First 60 s short | ~$9.06 | | | | | |
| Repeat short | ~$1 | | | | | |
| InfiniteTalk 480p per 4 s | ~368–425 s | | | | | |
| InfiniteTalk model load | ~465 s | | | | | |
| End-to-end wall clock | Unknown | | | | | |

Any variance above 25% must be explained or left explicitly unexplained. Unexplained variance is a finding, not a failure to hide.

## 11. Acceptance mapping

| Criterion | Evidence produced by this plan |
|---|---|
| AC-REP-001 | Run A output and manifest |
| AC-REP-002 | Manifest `model_id` fields for every stage |
| AC-REP-003 | Timing table with GPU, region, provisioning, load, inference and render |
| AC-REP-004 | Cost ledger reconciled to billing |
| AC-REP-005 | Event log with failures, retries and causes |
| AC-REP-006 | QC reports with raw values and thresholds |
| AC-REP-007 | Blind review note |
| AC-REP-008 | Step list with manual steps marked |
| AC-REP-009 | Run B manifest and cost entry |
| AC-REP-010 | Variance table |

## 12. Failure handling

| Situation | Action |
|---|---|
| Missing P0 artifact | Stop before spending; record the gap |
| Provider outage | Record time and cost; retry within the run window or reschedule |
| GPU unavailable in the required class | Record substitution; do not silently change class |
| Model download failure | Retry once; if it persists, stop and report |
| Quality below baseline | Complete the run, record defects, do not tune mid-run |
| Cost cap reached | Stop immediately; preserve partial evidence |
| Output cannot be compared to reference | Record the limitation; do not claim reproduction |

### 12.1 Stop conditions

- Spend cap reached.
- More than three consecutive failures at the same stage with the same cause.
- A missing artifact that changes the pipeline's shape.
- Any indication that the founder's account terms prohibit automated use.

## 13. Deliverables

1. `runs/rep-.../manifest.json` for each run.
2. Timing table with per-stage durations.
3. Cost ledger with sources and reconciliation notes.
4. QC report with raw metrics.
5. Blind review note signed by the founder.
6. Variance table against reported figures.
7. Manual-step list and automation candidates.
8. Reproduction runbook sufficient for a second engineer to repeat the run.
9. Gap report updating [UNKNOWN_CONFIGURATIONS.md](UNKNOWN_CONFIGURATIONS.md).

## 14. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Founder artifacts are incomplete | High | Run cannot start | Checklist and explicit waivers |
| Provider spend exceeds cap | Medium | Run stopped mid-way | Cap, staged approval, cheap dry runs |
| Model versions have changed since production | Medium | Output differs | Pin files and record hashes |
| GPU class unavailable | Medium | Timing not comparable | Record substitution and compare within class |
| Reference video cannot be matched | Medium | Acceptance ambiguous | Blind review with defect list |
| Human review is delayed | Medium | Milestone slips | Schedule review before the run |
| Licences prevent reproduction | Low–Medium | Run blocked | Resolve M-100 before spending |

## 15. Provisional schedule

| Phase | Effort | Output |
|---|---|---|
| Package intake and validation | 2–4 days | Accepted input manifest |
| Environment build and preflight | 2–3 days | Reproducible environment |
| Run A | 1–2 days plus provider time | Cold-run evidence |
| Run B | 1 day | Repeat-run evidence |
| Run C, if required | 1 day | Variance evidence |
| Analysis and report | 2–3 days | Baseline report |
| Founder blind review | 1–2 days | Acceptance note |

Effort is provisional and excludes provider queue time.

## 16. Exit criteria

The baseline is reproduced when:

- AC-REP-001 through AC-REP-010 are evidenced;
- another engineer can repeat the run from the runbook;
- cost and timing variance is explained or explicitly recorded as unexplained;
- every deviation from the founder's setup is listed;
- the unknown register is updated with what was closed and what remains;
- no product code has been written.
