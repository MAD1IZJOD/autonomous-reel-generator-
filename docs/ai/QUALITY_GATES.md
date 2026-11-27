# Quality Gates

| Field | Value |
|---|---|
| Status | Foundation; thresholds are baseline and configurable |
| Last updated | 2026-11-27 |
| Related | [PRD](../product/PRD.md), [model evaluation](MODEL_EVALUATION.md), [acceptance criteria](../product/ACCEPTANCE_CRITERIA.md) |

## 1. Purpose

Quality gates are screening and decision points, not proof of quality. A gate can reject an output, but passing a gate does not guarantee that the output is good. Human review remains part of every exportable result.

The founder's experience shows why this matters: a voice similarity score of 0.94 did not capture an accent mismatch, and lip-sync metrics screen for problems but do not prove naturalness.

## 2. Gate outcomes

| Outcome | Meaning | Effect on export |
|---|---|---|
| `pass` | All required metrics within threshold | May proceed |
| `warn` | Metric outside preferred range but within hard limit | Proceeds with recorded warning |
| `fail` | Metric outside hard limit | Blocks unless overridden |
| `needs_human` | Metric cannot decide; human must review | Blocks export until reviewed |

A gate decision is attached to a specific asset version and threshold configuration.

## 3. Gate levels

| Level | When it runs | Blocking? |
|---|---|---|
| Preflight | Before expensive generation | Blocks dispatch |
| Stage QC | After a stage produces output | Blocks dependent stages |
| Final QC | Before human review | Blocks export |
| Human review | Final gate | Blocks export |

## 4. Voice gates

Baseline from the existing workflow:

| Metric | Baseline threshold | Notes |
|---|---|---|
| Speaker similarity | ~0.96–0.97 | Screening only; accent/register must be confirmed by a human |
| Whisper CER | ≤ 0.2 | Transcription errors may be caused by names or intentional pronunciation |
| Syllables per second | Within configured range | Detects rushed or dragged delivery |
| Loudness | ~-14 LUFS after mastering | Measured on final mix, not raw take |
| Pause distribution | Pauses > 0.3 s squeezed to ~0.2 s | Baseline post-processing rule |

Handling:

- A similarity pass with an accent mismatch is still a failure by human judgement.
- A CER failure caused by a legitimate name can be approved with a recorded pronunciation correction.
- Voice gates block presenter generation in the character/story profile.

## 5. Lip-sync gates

Baseline from Avi's measured footage:

| Metric | Baseline | Notes |
|---|---|---|
| SyncNet score | Recorded and compared | Screening gate |
| Mouth opening mean | 0.28 | Avi's measured baseline |
| Mouth opening P90 | 0.42 | Avi's measured baseline |
| Open frames | ~68% | Avi's measured baseline |
| Jaw over-stretch | Human review | InfiniteTalk was observed to over-stretch the jaw |

Handling:

- Metrics are compared with the measured baseline, not treated as universal constants.
- A model that is faster but reduces mouth movement (such as LatentSync 1.6 in testing) fails the movement-preservation check.
- Jaw over-stretch is detected by metric and confirmed by human review.
- Lip-sync gates block export for presenter shots unless overridden.

## 6. Visual gates

| Check | Rule | Notes |
|---|---|---|
| Keyframe approval | Required for character/story profile | Human gate |
| Motion beat duration | ≤ 2.4 s where possible | Longer beats must be split or explicitly justified |
| Still origin | Every motion clip starts from an approved still | Hard rule |
| Set consistency | One set, lighting direction and colour grade per video | Human review |
| Repeated stills | No artificial zoom pulses on repeated images | Flag, not silent accept |
| Visual relevance | Visuals illustrate the spoken words | Human review |
| Candidate count | At most two scored options presented | Editorial rule |

## 7. Render and audio gates

| Check | Rule |
|---|---|
| Frame rate | 25 FPS |
| Duration | Matches target format within tolerance |
| Black frames | None beyond configured tolerance |
| Duplicate frames | None beyond configured tolerance |
| Audio loudness | ~-14 LUFS |
| True peak | -1 to -1.5 dB |
| Caption sync | Within configured tolerance |
| Aspect ratio | Matches project configuration |

## 8. Evidence requirements

Every gate stores:

- asset version ID
- metric values with units
- threshold configuration used
- model and deployment identifiers
- hardware and region where relevant
- reviewer identity for human gates
- override reason where applicable
- timestamp

Evidence is stored as QC reports and, for visual checks, contact sheets. A gate result without evidence is invalid.

## 9. Overrides

A blocking gate may be overridden only by an authorized role with:

- the gate and asset identifiers,
- the reason,
- the residual risk,
- an expiry or follow-up action,
- a record in the audit trail and manifest.

Overrides do not erase the metric result. They make the decision explicit and reviewable.

Safety, consent and licensing gates cannot be overridden. They must be fixed.

## 10. Threshold management

- Thresholds are configuration, not code constants.
- A threshold change requires an evaluation record and a routing or quality-policy update.
- Historical QC reports retain the threshold configuration used, so old results remain interpretable.
- Thresholds are profile-specific: `draft`, `baseline` and `high`.

## 11. Contact sheets and human review

- Contact sheets are generated for every shot and stored as QC evidence.
- Human reviewers compare at most two scored candidates.
- Reviewer comments are structured and attached to the shot.
- A rejection requires a reason and, where possible, a requested change.

## 12. Metrics are screening gates

The following are explicitly not proof of quality:

- speaker similarity scores,
- SyncNet scores,
- mouth-opening metrics,
- automated artifact detection.

They are necessary filters that reduce the number of candidates a human must review. The final decision rests with the reviewer and the product owner.

## 13. Open questions

- Exact numeric SyncNet threshold for this workflow.
- How to detect jaw over-stretch reliably.
- Whether to add identity-consistency scoring for characters.
- How to calibrate thresholds for non-Avi presenters.
- Whether quality profiles should be user-selectable per run.

Tracked in [OPEN_QUESTIONS.md](../project/OPEN_QUESTIONS.md).
