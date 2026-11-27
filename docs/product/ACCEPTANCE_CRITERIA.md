# Acceptance Criteria

| Field | Value |
|---|---|
| Status | Foundation; criteria are binding once the referenced capability exists |
| Last updated | 2026-11-27 |
| Related | [PRD](PRD.md), [MVP scope](MVP_SCOPE.md), [quality gates](../ai/QUALITY_GATES.md), [testing strategy](../engineering/TESTING_STRATEGY.md) |

## 1. How to use this document

Every criterion has an identifier, a requirement reference and a verification method. A criterion is satisfied only when the stated evidence exists and is linked from the run record or milestone report.

Rules:

- **No self-certification.** The person who implemented a capability cannot be the only reviewer of its acceptance evidence.
- **No screenshot-only evidence** for media correctness. Screenshots may support UX criteria, but media and QC criteria require files, hashes, manifests and measurements.
- **Fixtures are labelled.** A test using synthetic media proves plumbing, not production quality. It cannot satisfy a quality criterion.
- **Waivers are explicit.** A waived criterion records who approved it, why, the residual risk and the expiry. A waiver is not a pass.
- **Thresholds live in configuration.** Values in this document are the baseline; changing them requires an evaluation record and a routing-policy change.

## 2. Foundation-phase criteria (this phase)

| ID | Criterion | Evidence |
|---|---|---|
| AC-FND-001 | The repository is on `main` with the correct remote and a clean working tree after the final push. | `git status`, `git remote -v` output in the final report |
| AC-FND-002 | Every foundation commit has author and committer `Madhavan <175943252+MAD1IZJOD@users.noreply.github.com>`. | `git log --format=fuller` for all commits |
| AC-FND-003 | No secret, private media or model weight is tracked. | `git ls-files` review and secret scan |
| AC-FND-004 | All required documents exist and contain substantive, cross-referenced content. | Documentation inventory and link check |
| AC-FND-005 | Mermaid diagrams parse and render on GitHub. | Rendered review of each diagram |
| AC-FND-006 | Internal relative links resolve. | Link-check output |
| AC-FND-007 | The documents distinguish tested, rejected, proposed and untested items. | Review of model registry and evaluation docs |
| AC-FND-008 | Unknowns are recorded as open questions rather than invented facts. | Review of `OPEN_QUESTIONS.md` and inline `Unknown` markers |

## 3. Reference reproduction criteria (Milestone 1)

These criteria establish that the team can reproduce the existing system before changing it.

| ID | Criterion | Verification |
|---|---|---|
| AC-REP-001 | One existing 60-second short is reproduced end to end from an approved script and plate sheet. | Run manifest plus the exported file |
| AC-REP-002 | Exact model identifiers and versions are recorded for every stage. | Manifest fields populated; no "latest" placeholders |
| AC-REP-003 | GPU type, provider, region, provisioning time, model-loading time, inference time and render time are recorded. | Timing table with start/end timestamps and source |
| AC-REP-004 | Total GPU cost and paid-API cost are recorded, including setup and failed attempts. | Cost ledger reconciled against provider invoices or billing exports |
| AC-REP-005 | Failures, retries and their causes are recorded. | Run event log |
| AC-REP-006 | QC measurements are recorded for voice and lip-sync. | QC reports with raw metric values and thresholds |
| AC-REP-007 | The founder accepts the output in a blind comparison against the existing workflow, or records specific defects. | Signed review note with comparison method |
| AC-REP-008 | The reproduction does not rely on undocumented manual steps. | Step list reviewed; any manual step is marked and scheduled for automation |
| AC-REP-009 | A repeat run in the same style is measured separately from the first run. | Two manifests and cost entries |
| AC-REP-010 | The measured baseline is compared with the founder's reported figures ($9.06 first short, ~$1 repeat, ~12 min setup, ~75 GB download, InfiniteTalk timings). | Variance table with explanations |

Reproduction is not "done" because a video exists. It is done when the video and the evidence can be inspected independently.

## 4. Functional acceptance criteria

### 4.1 Projects, scripts and plans

| ID | Given / When / Then | Requirement |
|---|---|---|
| AC-001 | Given a signed-in operator, when they create a project and submit a script, then an immutable script version and a draft run snapshot exist. | FR-001, FR-002, FR-003 |
| AC-002 | Given a draft plate sheet, when a required field or duration bound is invalid, then submission for approval is blocked with a field-level error. | FR-010, FR-011, FR-012 |
| AC-003 | Given an approved plate sheet, when a user edits it, then a new draft version is created and the approved version remains unchanged. | FR-014, FR-015 |
| AC-004 | Given an explainer run, when voice is approved, then plate timings are aligned to the voice track and the alignment is stored. | FR-013 |
| AC-005 | Given a character/story run, when keyframes are not approved, then voice and presenter stages cannot start. | FR-031 |

### 4.2 Voice

| ID | Given / When / Then | Requirement |
|---|---|---|
| AC-010 | Given voice text with Hindi and English words and numeric values, when it is prepared for synthesis, then the recorded prepared text uses the configured Devanagari and number-word rules. | FR-021 |
| AC-011 | Given a generated take, when post-processing completes, then pause squeezing, speed and loudness settings match the run configuration and are recorded. | FR-022 |
| AC-012 | Given a take, when QC runs, then similarity, CER and syllables per second are stored with the transcript and threshold decisions. | FR-024 |
| AC-013 | Given a failed voice take, when the operator retakes it, then approved visuals are not regenerated. | FR-025 |

### 4.3 Visuals, motion and presenter

| ID | Given / When / Then | Requirement |
|---|---|---|
| AC-020 | Given an approved plate, when keyframes are generated, then each candidate records its prompt, references, model version and score. | FR-030 |
| AC-021 | Given an unapproved still, when motion generation is requested, then the job is rejected before GPU provisioning. | FR-032 |
| AC-022 | Given a motion clip longer than 2.4 s, when validation runs, then the clip is split or flagged according to the profile. | FR-033 |
| AC-023 | Given a shot with more than two scored candidates, when review is requested, then only the top two are presented and the rest are retained but hidden. | FR-036 |
| AC-024 | Given a presenter shot, when lip-sync QC completes, then SyncNet and mouth-opening evidence is attached to the asset version. | FR-042 |
| AC-025 | Given a blocking lip-sync failure, when export is requested, then export is blocked unless an authorized override with a reason is recorded. | FR-043, FR-066 |

### 4.4 Graphics, audio and render

| ID | Given / When / Then | Requirement |
|---|---|---|
| AC-030 | Given a composed timeline, when the final render runs, then the output is 25 FPS and the manifest records the renderer version and settings. | FR-053, FR-054 |
| AC-031 | Given a mixed audio track, when mastering is measured, then loudness is approximately -14 LUFS and true peak is between -1 and -1.5 dB, or the deviation is reported. | FR-053 |
| AC-032 | Given a music or SFX asset, when it is used, then its source and licence are recorded. | FR-052 |
| AC-033 | Given a timeline containing a repeated still used as motion, when validation runs, then the shot is flagged rather than silently accepted. | FR-035 |

### 4.5 Review, regeneration and export

| ID | Given / When / Then | Requirement |
|---|---|---|
| AC-040 | Given a run awaiting approval, when a reviewer approves, then the gate closes with user identity, timestamp and comment. | FR-014, FR-061 |
| AC-041 | Given an approved shot, when regeneration is requested, then a new asset version is created and the old version remains retrievable. | FR-062, FR-063 |
| AC-042 | Given a failed stage with a valid checkpoint, when retry is requested, then completed paid work is reused and only the failed work is repeated. | FR-064 |
| AC-043 | Given a run with an open blocking gate, when export is requested, then the system refuses with a specific list of unresolved gates. | FR-066 |
| AC-044 | Given a successful export, when the package is inspected, then it contains the video, captions, thumbnail candidates and a manifest with provenance and cost. | FR-065 |

### 4.6 Administration and cost

| ID | Given / When / Then | Requirement |
|---|---|---|
| AC-050 | Given a new model, when an administrator registers it without a licence decision, then it cannot be enabled for production. | FR-070, FR-071, NFR-007 |
| AC-051 | Given a provider call or GPU session, when it completes or fails with a charge, then a cost entry exists with run, stage and shot attribution. | FR-072 |
| AC-052 | Given a budget threshold, when it is crossed, then new GPU dispatch pauses and an administrator is notified. | FR-073 |
| AC-053 | Given an idle GPU session past the configured window, when the watchdog runs, then the session is terminated and the action is recorded. | FR-074 |
| AC-054 | Given an approval, export or credential change, when it occurs, then an audit event records actor, action, target and time. | FR-075 |

## 5. Quality acceptance

Quality criteria require real media and human review. They cannot be satisfied by unit tests alone.

| ID | Criterion | Blocking? |
|---|---|---|
| AC-Q-001 | Voice similarity meets the configured baseline (~0.96–0.97) **and** a human confirms accent/register match. | Yes for voice approval |
| AC-Q-002 | Whisper CER is at or below 0.2, or a reviewer documents an accepted pronunciation exception. | Yes for voice approval |
| AC-Q-003 | Lip-sync mouth-opening metrics are compared with the measured baseline (mean 0.28, P90 0.42, ~68% open) and reviewed for jaw over-stretch. | Yes for presenter shots |
| AC-Q-004 | No black frames, duplicate frames or frozen segments beyond the configured tolerance. | Yes for export |
| AC-Q-005 | Contact sheets are generated and reviewed for every shot. | Yes for final review |
| AC-Q-006 | The final cut maintains one set, lighting direction and grade. | Reviewer sign-off |
| AC-Q-007 | Motion beats are at or below 2.4 s where possible; exceptions are recorded. | Warning or block by profile |
| AC-Q-008 | The video uses visuals that illustrate the spoken words and does not rely on repeated stills with zoom pulses. | Reviewer sign-off |
| AC-Q-009 | Audio meets loudness and true-peak targets. | Yes for export |
| AC-Q-010 | The founder accepts the output in a blind comparison for the reference reproduction. | Yes for Milestone 1 |

A metric pass does not override a human rejection. A human override does not erase the metric result.

## 6. Operational acceptance

| ID | Criterion | Verification |
|---|---|---|
| AC-OPS-001 | Killing a worker mid-job leaves the job recoverable; a new worker can reclaim it after lease expiry. | Fault-injection test |
| AC-OPS-002 | Retrying a paid provider call does not create a duplicate charge when the provider supports idempotency. | Provider sandbox or reconciled invoice |
| AC-OPS-003 | A lost GPU session is detected within two heartbeat intervals and reconciled before replacement. | Chaos test with provider stub plus one live test |
| AC-OPS-004 | No GPU session survives beyond the idle window during a normal run. | Provider audit for a full run |
| AC-OPS-005 | A run cannot reach `succeeded` with a missing required artifact. | Domain test and manual attempt |
| AC-OPS-006 | Queue depth, job latency, failure rate, GPU idle time and cost per run are visible on a dashboard. | Dashboard review |
| AC-OPS-007 | A trace for one run links API request, job, provider call and render. | Trace inspection |
| AC-OPS-008 | Backup and restore of metadata and media is exercised and documented. | Restore report |

## 7. Security and privacy acceptance

| ID | Criterion | Verification |
|---|---|---|
| AC-SEC-001 | No credential is present in the frontend bundle, Git history or logs. | Secret scan and bundle inspection |
| AC-SEC-002 | Object storage is private; media access requires a short-lived signed URL scoped to an authorized user. | Access test with an unauthenticated request |
| AC-SEC-003 | A user cannot read or mutate another workspace's records in the MVP schema. | Authorization tests at the repository boundary |
| AC-SEC-004 | External provider egress is denied unless the workspace policy allows the provider and data class. | Policy test and audit event |
| AC-SEC-005 | Consent records exist for every voice and likeness used in an export. | Manifest-to-consent join |
| AC-SEC-006 | Deleting a project removes media and derivatives according to policy while retaining required audit records. | Deletion test and storage inspection |
| AC-SEC-007 | Dependencies and models have a recorded licence decision before production enablement. | Registry review |

## 8. UX acceptance

| ID | Criterion |
|---|---|
| AC-UX-001 | The run view distinguishes queued, running, waiting for approval, failed, cancelled and succeeded without ambiguity. |
| AC-UX-002 | Every blocking state explains what is needed and who can resolve it. |
| AC-UX-003 | Estimated and actual cost are visible before and after a run. |
| AC-UX-004 | Reviewers can inspect QC evidence without leaving the shot context. |
| AC-UX-005 | Destructive or expensive actions require confirmation that states the consequence. |
| AC-UX-006 | The UI never presents a fixture or preview as a final render. |

## 9. Waiver process

A blocking criterion may be waived only by the product owner with:

- The criterion identifier and the reason.
- The residual risk and affected users.
- A compensating control, if any.
- An expiry date or follow-up milestone.
- A link in the run manifest and audit trail.

Waivers do not apply to safety, consent or licensing requirements. Those must be fixed, not waived.

## 10. Evidence standard

Acceptable evidence:

- Run manifest with content hashes, model versions, settings, hardware and cost.
- QC report files with raw values and the threshold configuration used.
- Provider billing export or invoice reconciliation.
- Test output from a named commit, with the command and environment.
- Review note with reviewer identity and comparison method.
- Screenshots for UI state only, paired with the underlying record identifiers.

Unacceptable evidence:

- "It worked" without a run identifier.
- A video with no provenance.
- A metric averaged across unrelated runs.
- A benchmark from a different model version or hardware configuration.
- A licence claim based only on a model card summary without the actual licence text.
