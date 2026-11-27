# Risks

| Field | Value |
|---|---|
| Status | Foundation |
| Last updated | 2026-11-27 |
| Related | [Milestones](MILESTONES.md), [execution plan](EXECUTION_PLAN.md), [open questions](OPEN_QUESTIONS.md) |

## 1. Purpose

This register tracks risks that could prevent the project from reproducing the existing workflow, meeting quality or reaching the MVP. Risks are reviewed at each milestone and whenever new information appears.

Severity: `Low`, `Medium`, `High`, `Critical`. Likelihood: `Low`, `Medium`, `High`.

## 2. Risk register

| ID | Risk | Likelihood | Impact | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|
| R-001 | The founder's existing scripts and media are not available or are incomplete | Medium | Critical | Request artifacts early; track as a blocker; design around missing pieces only after audit | Engineering | Open |
| R-002 | The reference reproduction fails or differs materially from the founder's output | Medium | High | Reproduce before changing anything; record variance; iterate with the founder | Engineering | Open |
| R-003 | Premium voice or avatar quality cannot be matched by open alternatives | High | High | Keep premium baselines; evaluate open models only as additions or fallbacks | Product | Open |
| R-004 | InfiniteTalk does not meet quality for Hindi or presenter use | High | High | Keep HeyGen baseline; record limitations; evaluate training only as a separate track | Engineering | Open |
| R-005 | GPU costs exceed budget during development | Medium | High | Cost caps, budget pauses, recorded fixtures, live tests only when approved | Engineering | Open |
| R-006 | Model loading and provisioning waste is not reduced as expected | Medium | Medium | Measure before/after; treat targets as hypotheses | Engineering | Open |
| R-007 | Licensing prevents commercial use of a model or tool already in the workflow | Medium | Critical | Licence review in Milestone 0; block unverified components | Engineering/Legal | Open |
| R-008 | Consent or likeness rights are unclear for the digital twin | Medium | Critical | Obtain and record consent; block export without consent records | Product | Open |
| R-009 | Quality metrics pass while human quality fails | High | High | Keep human review in the gate; treat metrics as screening only | Product | Open |
| R-010 | Accent or register mismatch is not captured by similarity scores | High | Medium | Human review of accent/register; record overrides and reasons | Product | Open |
| R-011 | Scope creep into model training or enterprise features delays the MVP | Medium | High | Explicit deferrals in MVP scope; gate scope changes through open questions | Product | Open |
| R-012 | Premature microservices or infrastructure add operational burden | Medium | Medium | Follow ADR-001; extract only with measured evidence | Engineering | Open |
| R-013 | A provider outage or pricing change disrupts production | Medium | Medium | Provider abstraction, fallback policy, cost monitoring | Engineering | Open |
| R-014 | GPU pod termination fails and causes cost runaway | Medium | High | Watchdog, reconciliation, paging, orphan attribution | Engineering | Open |
| R-015 | Private media is accidentally committed or exposed | Low | Critical | `.gitignore`, secret scan, private buckets, access tests | Engineering | Open |
| R-016 | The team underestimates integration effort for existing scripts | Medium | High | Audit first; wrap before porting; integrate one stage at a time | Engineering | Open |
| R-017 | Quality thresholds are set incorrectly and block or allow the wrong outputs | Medium | Medium | Configurable thresholds with evaluation records | Product/Engineering | Open |
| R-018 | Enterprise requirements are assumed without customer input | Medium | Medium | Defer certification; investigate in Milestone 6 | Product | Open |
| R-019 | Documentation drifts from implementation | Medium | Medium | Docs updated in the same change; progress entries with evidence | Engineering | Open |
| R-020 | A single engineer becomes a bottleneck | Medium | Medium | Clear module boundaries and documented decisions | Engineering | Open |

## 3. Risk review

Risks are reviewed:

- at the start of each milestone,
- when a new dependency or provider is introduced,
- when a quality or cost incident occurs,
- when an open question is resolved.

A risk is closed only when its mitigation is evidenced and the risk no longer applies. Closed risks remain in the register with a closure note.

## 4. New risks

New risks are added with the next available ID and the same fields. A risk without a mitigation and owner is not accepted into the register.

## 5. Open questions

- Which risks should be escalated to the founder immediately.
- Whether to maintain a separate risk register for security incidents.
- Whether cost overruns require founder approval in addition to administrator approval.

Tracked in [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md).
