# Model Benchmark Plan

| Field | Value |
|---|---|
| Status | Foundation |
| Last updated | 2026-11-27 |
| Related | [Model evaluation](MODEL_EVALUATION.md), [open-source model strategy](OPEN_SOURCE_MODEL_STRATEGY.md), [quality gates](QUALITY_GATES.md), [cost optimization](../infrastructure/COST_OPTIMIZATION.md) |

## 1. Purpose

This plan defines how models are benchmarked before they can replace or supplement the baselines. It ensures comparisons are fair, reproducible and tied to cost per accepted output.

## 2. Benchmark principles

- Use fixed, versioned datasets.
- Pin model version, deployment digest, hardware and settings.
- Run both candidates to completion, including retries.
- Apply the same automated metrics and human rubric.
- Record cost per accepted output, including failures.
- Do not compare a tuned baseline against an untuned challenger without stating the difference.
- Record failure modes, not only averages.

## 3. Benchmark stages

```mermaid
flowchart LR
    A[Register candidate] --> B[Define task and dataset]
    B --> C[Run automated benchmark]
    C --> D[Human review]
    D --> E[Cost analysis]
    E --> F[Decision record]
```

## 4. Datasets

Each capability needs a versioned dataset containing:

- representative scripts and plate sheets,
- character references and proof visuals,
- voice and video references where applicable,
- expected durations and aspect ratios,
- edge cases: mixed languages, numbers, names, short and long beats, low-quality inputs,
- a reviewer rubric and gold standard where possible.

The dataset is stored outside Git in object storage with a manifest hash.

## 5. Hardware configurations

Benchmarks must record:

- GPU type and VRAM
- CPU, RAM and storage
- provider and region
- model cache state (warm or cold)
- container image digest

Results are not transferable across hardware configurations without evidence.

## 6. Metrics

### 6.1 Voice

- Speaker similarity
- Whisper CER
- Syllables per second
- Pronunciation of names, numbers and mixed-language phrases
- Pause distribution and loudness
- Failure and retry rate

### 6.2 Image

- Identity consistency
- Prompt adherence (structured rubric)
- Artifact detection
- Resolution and format validity
- Generation time and cost

### 6.3 Motion

- Frame stability and flicker
- Temporal consistency
- Beat duration compliance
- Failure and retry rate
- Cost per accepted clip

### 6.4 Lip-sync

- SyncNet score
- Mouth-opening metrics vs baseline
- Jaw over-stretch detection
- Facial/head movement preservation
- Hindi/English phoneme handling

### 6.5 Render and audio

- Frame rate correctness
- Loudness and true peak
- Black/duplicate frame detection
- Caption sync
- Reproducibility from manifest

## 7. Cost per accepted output

```text
cost_per_accepted_output =
  (inference + setup + loading + failed attempts + review cost)
  / accepted outputs
```

Include failed attempts, loading time and review cost. Compare against the measured baseline, not a theoretical optimum.

## 8. Human review

- At most two scored candidates per shot.
- Reviewers record identity, method, defects, accept/reject, exportability and override reasons.
- A model that passes automated metrics but fails human review is not production-ready.

## 9. Benchmark schedule

| Phase | Benchmark | Gate |
|---|---|---|
| M1 | Reproduce baseline and record its metrics | Baseline established |
| M4 | Evaluate open image and motion models | Quality floor check |
| M4 | Evaluate open lip-sync models | Quality floor check |
| M4 | Evaluate open voice models | Quality floor check |
| M5 | Re-run benchmarks after any model or provider change | Regression check |

Benchmarks must not delay the first reproduction milestone.

## 10. Decision record

Each benchmark produces a decision record containing:

- candidate and baseline identifiers
- dataset and hardware versions
- raw metric outputs
- human review notes
- cost per accepted output
- conclusion and recommendation
- whether the candidate replaces, supplements or is rejected

The record is linked from the model registry.

## 11. Open questions

- Sufficient dataset size per capability.
- Weighting of human review vs automated metrics.
- Handling nondeterministic providers.
- Whether to benchmark on customer-specific data under consent.

Tracked in `docs/project/OPEN_QUESTIONS.md`.
