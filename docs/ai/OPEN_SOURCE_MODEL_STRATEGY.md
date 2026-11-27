# Open-Source Model Strategy

| Field | Value |
|---|---|
| Status | Foundation |
| Last updated | 2026-11-27 |
| Related | [Model registry](MODEL_REGISTRY.md), [model routing](MODEL_ROUTING.md), [model evaluation](MODEL_EVALUATION.md), [licensing policy](LICENSING_POLICY.md) |

## 1. Objective

Reduce dependence on expensive proprietary AI APIs where open-weight alternatives meet the quality floor and licensing requirements. This is an optimisation goal, not an ideology. Premium APIs remain the baseline where they measurably win.

## 2. Strategy principles

- Quality floors are non-negotiable. A cheaper model is not a replacement unless it passes the same gates.
- Measure cost per accepted output, not unit price.
- Keep premium fallback available where appropriate.
- Do not send private data to external providers without an explicit policy.
- Verify licences per model version; downloadable weights are not automatically usable.
- Evaluate candidates independently; do not let experiments delay the first reproduction milestone.

## 3. Task-by-task assessment

| Task | Current baseline | Open alternative status | Recommendation |
|---|---|---|---|
| Script generation | Not in current pipeline (human-approved script) | LLMs available; licence varies | Use only as a drafting aid; human approval remains mandatory |
| Script analysis / plate planning | Claude Code skill files | LLMs available | Automate with a model only after the manual pipeline is reproduced |
| Voice generation | ElevenLabs v4 | IndicF5 rejected for accent/register; Chatterbox cancelled | Keep ElevenLabs; revisit fine-tuning as a separate track |
| Voice cloning | ElevenLabs professional clone | Open voice cloning options exist; quality and licence unverified | Keep baseline; evaluate under consent and quality gates |
| Image generation | Qwen-Image + Lightning LoRA | Already open-weight and tested | Keep as baseline; verify licence |
| Reference-based image editing | Qwen-Image-Edit-2511 | Already open-weight and tested | Keep as baseline; verify licence |
| Video generation | Wan 2.2 I2V A14B fp8 + LightX2V | Already open-weight and tested | Keep as baseline; verify licence |
| Lip-sync | HeyGen Avatar 6 (baseline), InfiniteTalk (open) | InfiniteTalk best open option tested; did not match HeyGen | Keep HeyGen; InfiniteTalk as fallback or for non-premium shots |
| Music | Licensed or procedural assets | ACE-Step v1.5 XL proposed | Evaluate separately; licensing review required |
| Sound effects | Procedural SFX scripts | ThinkSound proposed | Evaluate separately |
| Speech recognition | Whisper | Already open-weight and tested | Keep |
| Quality assessment | Custom similarity, SyncNet, MediaPipe | Identity consistency scoring proposed | Keep current metrics; add scoring only after evaluation |

## 4. Open-weight candidates to evaluate

| Candidate | Task | Status | Licence status | Notes |
|---|---|---|---|---|
| Qwen-Image + Lightning 8-step LoRA | Image generation | Tested | Unclear (verify) | Existing baseline |
| Qwen-Image-Edit-2511 | Image editing | Tested | Unclear (verify) | Existing baseline |
| Wan 2.2 I2V A14B fp8 + LightX2V LoRA | Video generation | Tested | Unclear (verify) | Existing baseline |
| InfiniteTalk | Lip-sync | Tested | Unclear (verify) | Best open option; limitations recorded |
| Whisper | Transcription | Tested | Verify per version | Baseline QC tool |
| ACE-Step v1.5 XL | Music | Proposed | Unclear (verify) | Future experiment |
| ThinkSound | SFX | Proposed | Unclear (verify) | Future experiment |
| LongCat-Video-Avatar 1.6 | Lip-sync | Untested | Unclear (verify) | Version 1.5 rejected; 1.6 noted as untested |
| Fine-tuned IndicF5 / F5-TTS | Voice | Proposed | Unclear (verify) | Requires evaluation on Avi's recording |

## 5. Rejected approaches (do not reintroduce without evidence)

- IndicF5: high similarity but wrong accent/register; Latin script issues.
- LatentSync 1.6: reduced mouth movement; poor preservation of facial/head movement.
- LongCat-Video-Avatar 1.5: poor quality in tested configuration.
- Chatterbox Multilingual: cancelled after IndicF5 failure.

## 6. Licensing exclusions

The excluded list in `docs/ai/LICENSING_POLICY.md` remains in force. A model with downloadable weights is not automatically commercially usable.

## 7. Model registry requirements

Every model entry must record:

- model name and version
- repository and licence
- required VRAM and hardware
- inference configuration
- quality benchmarks and evaluation ID
- estimated cost
- supported tasks
- known limitations

## 8. Evaluation and routing

- Quality gates are defined in `docs/ai/QUALITY_GATES.md`.
- Evaluation protocol is defined in `docs/ai/MODEL_EVALUATION.md`.
- Routing rules are defined in `docs/ai/MODEL_ROUTING.md`.
- No model is enabled in production without licence verification, evaluation evidence and a smoke test.

## 9. Open questions

- Exact licence terms for the open-weight models in use.
- Whether fine-tuning resolves the IndicF5 accent and script issues.
- Whether LongCat 1.6 improves enough to justify evaluation.
- Whether open music and SFX models meet editorial quality.
- Whether an open LLM can reliably generate or analyse plate sheets.

Tracked in `docs/project/OPEN_QUESTIONS.md`.
