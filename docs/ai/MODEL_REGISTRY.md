# Model Registry

| Field | Value |
|---|---|
| Status | Foundation; entries are based on the founder's reported baseline and must be verified |
| Last updated | 2026-11-27 |
| Related | [Model routing](MODEL_ROUTING.md), [model evaluation](MODEL_EVALUATION.md), [licensing policy](LICENSING_POLICY.md), [provider abstraction](PROVIDER_ABSTRACTION.md) |

## 1. Purpose

The model registry is the single source of truth for what the system can run. Application code resolves capabilities through the registry and routing policy; it never hardcodes a model name.

Every entry records capability, version, provider, licence status, hardware, cost inputs, quality status and evaluation evidence. A model cannot be used in production unless its registry entry is complete and its licence decision is `allowed` or `allowed_with_conditions`.

## 2. Status taxonomy

| Status | Meaning |
|---|---|
| `tested` | Used in the founder's existing workflow; behaviour observed |
| `rejected` | Tested and not selected; reason recorded |
| `proposed` | Candidate suggested by the founder or team; not yet evaluated |
| `untested` | Available but no evaluation evidence |
| `excluded` | Blocked by licence, terms or policy; do not use |
| `deprecated` | Previously used; no longer recommended |

Licence status is independent of quality status:

| Licence status | Meaning |
|---|---|
| `allowed` | Commercial use verified for the intended deployment |
| `allowed_with_conditions` | Usable with recorded conditions |
| `research_only` | Not usable in a commercial product |
| `unclear` | Not yet verified; blocks production use |
| `rejected` | Explicitly not permitted |

## 3. Registry schema (minimum fields)

| Field | Description |
|---|---|
| `model_id` | Stable identifier, not a display name |
| `capability` | e.g. `image.keyframe`, `video.image_to_video`, `voice.synthesize` |
| `provider` | `elevenlabs`, `heygen`, `runpod`, `local`, etc. |
| `version` | Provider or weight version, pinned |
| `deployment_digest` | Image digest or model server version |
| `weight_hash` | Hash of model weights where applicable |
| `status` | Quality status from the taxonomy above |
| `licence_status` | Licence status from the taxonomy above |
| `licence_evidence` | Link to licence text or review record |
| `hardware` | GPU type, VRAM, CPU, RAM requirements |
| `cost_inputs` | Unit cost, setup cost, loading time |
| `quality_profile` | Which quality profile it satisfies |
| `evaluation_id` | Link to evaluation record |
| `languages` | Supported languages and scripts |
| `notes` | Measured limitations and caveats |

## 4. Paid providers (existing baseline)

| Model | Capability | Status | Licence status | Notes |
|---|---|---|---|---|
| HeyGen Avatar 6 | `presenter.avatar` | tested | Contract-dependent | Established baseline; ~$0.089/s of generated face video; portrait and landscape twins; trained digital twin of Avi; consent required |
| HeyGen Avatar IV | `presenter.avatar` | rejected | Contract-dependent | Rejected for visual/mouth differences |
| HeyGen Avatar V | `presenter.avatar` | rejected | Contract-dependent | Rejected for visual/mouth differences |
| ElevenLabs v4 | `voice.synthesize` | tested | Contract-dependent | Professional voice clone on team account; ~1 credit/character; backup Instant Clone exists |
| ElevenLabs Instant Clone | `voice.synthesize` | tested | Contract-dependent | Backup voice clone |

These are the current quality baselines. They are not to be replaced as a release requirement until open alternatives pass evaluation.

## 5. Open-weight models (existing workflow)

| Model | Capability | Status | Licence status | Hardware | Notes |
|---|---|---|---|---|---|
| Qwen-Image + Lightning 8-step LoRA | `image.keyframe` | tested | unclear (verify) | L40 48 GB | Existing image baseline |
| Qwen-Image-Edit-2511 | `image.edit` | tested | unclear (verify) | L40 48 GB | Multi-reference editing |
| Wan 2.2 I2V A14B fp8 + LightX2V 4-step LoRA | `video.image_to_video` | tested | unclear (verify) | L40/L40S 48 GB | Existing motion baseline; keep beats ≤ 2.4 s |
| ComfyUI (headless API) | `orchestration` | tested | Verify per node/custom node | L40 48 GB | Model orchestration runtime |
| InfiniteTalk on Wan 2.1 I2V 14B + LightX2V LoRA | `lipsync.generate` | tested | unclear (verify) | A100 80 GB for tested 720p config; 480p production config observed | Best open lip-sync tested; did not match HeyGen; Hindi audio-encoder limitations; jaw over-stretch observed |

Hardware and licence entries are provisional until verified against the actual weight and image licences.

## 6. Open models tested and rejected

| Model | Capability | Status | Reason for rejection |
|---|---|---|---|
| IndicF5 | `voice.synthesize` | rejected | High similarity score but wrong accent/register; could not read Latin script correctly in tested configuration; required one line per generation and Whisper retake loops; fine-tuning on Avi's recording remains untested |
| LatentSync 1.6 | `lipsync.generate` | rejected | Faster but reduced mouth movement; did not preserve original facial/head movement adequately |
| LongCat-Video-Avatar 1.5 | `lipsync.generate` | rejected | Hindi-capable encoder but poor quality in tested configuration; version 1.6 noted as untested |
| Chatterbox Multilingual | `voice.synthesize` | cancelled | Cancelled after IndicF5 failed |

These must not be reintroduced without a new evaluation record. Fine-tuning IndicF5/F5-TTS on Avi's 11-minute recording remains a proposed experiment, not a completed integration.

## 7. Tools and runtimes tested

| Tool | Capability | Status | Notes |
|---|---|---|---|
| Revideo | `render.composition` | rejected | Evaluated for editing; HyperFrames preferred for the existing TypeScript workflow |
| HyperFrames | `render.composition` | tested | HTML, GSAP, Three.js, editorial design kit, paper textures, Anton/Playfair, marker highlights |
| FFmpeg | `render.finalize`, audio mastering | tested | Baseline renderer |
| Whisper | `qc.transcription` | tested | Voice QC |
| SyncNet | `qc.lipsync` | tested | Lip-sync QC |
| MediaPipe | `qc.mouth` | tested | Mouth-opening metrics |
| Blender | `character.consistency` | proposed | Future experiment |
| SeedVR2-7B | `finishing` | proposed | Future experiment |
| RIFE | `finishing` | proposed | Future experiment |

## 8. Licensing exclusions

The following are excluded from commercial use based on the founder's stated restrictions. They must not be reintroduced without a licence review and an ADR.

- Qwen-Image 2.1 / Turbo (research-only licence)
- FLUX.2 dev
- MMAudio
- XTTS-v2
- MMS-TTS
- MusicGen
- Stable Audio Open
- Wav2Lip
- SadTalker face model
- LTX-2 (cited commercial restrictions)
- Remotion (cited company licensing restrictions)
- Duix-Avatar (output usage terms)
- HunyuanVideo-Foley
- Indic-Speak (custom consent conditions)

A model with downloadable weights is not automatically usable. See [LICENSING_POLICY.md](LICENSING_POLICY.md).

## 9. Proposed future experiments

These are candidates, not completed integrations. They must be evaluated independently and must not delay the first reproduction milestone.

| Area | Candidate | Status |
|---|---|---|
| Character consistency | Blender, depth/skeleton info, Qwen-Image-Edit-2511, InstantX Qwen-Image-ControlNet-Union, per-character turnaround sheets, identity consistency scoring, Wan 2.2 I2V from approved keyframes | proposed |
| Choreographed motion | Wan2.2-Animate-2, Wan2.2-VACE-Fun A14B | proposed |
| Audio | ACE-Step v1.5 XL, ThinkSound | proposed |
| Finishing | SeedVR2-7B, RIFE | proposed |
| Training | Fine-tune InfiniteTalk or LatentSync on 30–60 minutes of Avi's footage; Hindi-capable audio encoders; fine-tune IndicF5/F5-TTS on Avi's 11-minute recording; per-character LoRAs; house-style LoRA | proposed |
| Speed | TeaCache, fewer steps, resident model servers, quantisation only with fast kernels | proposed |

## 10. GPU requirements (measured baseline)

| Hardware | Observed use | Measured notes |
|---|---|---|
| L40 48 GB VRAM | Image generation, Qwen image models, Wan video generation | Typical image/video workload |
| L40S 48 GB | Alternative video generation hardware | Alternative to L40 |
| A100 SXM 80 GB | Tested production InfiniteTalk configuration | ~90 s/step in one tested configuration |
| L40 (InfiniteTalk 720p) | Out of memory | Not viable for 720p InfiniteTalk |
| L40 (InfiniteTalk, DiT offloading) | ~190 s/step | Slow |
| L40 (InfiniteTalk int8) | ~300 s/step | Slower; quantisation not beneficial without fast kernels |
| L40 (InfiniteTalk 480p production) | ~368–425 s per 4-second burst + ~465 s model load | Observed production configuration |

These must be independently reproduced. Do not commit to hardware or providers based on these figures alone.

## 11. Registry maintenance rules

- A model is added by registration, not by editing workflow code.
- Every production enablement requires licence evidence and an evaluation record.
- Deprecated or rejected models remain in the registry with their reason; they are not deleted.
- Version pinning is mandatory; `latest` is not a valid production reference.
- A model whose licence status is `unclear` cannot be selected in production.
- Hardware and cost fields are updated when measured, with the measurement linked.

## 12. Open questions

- Exact licence terms for the open-weight models in use.
- Whether Qwen-Image 2.0 or newer versions are commercially usable.
- Whether LongCat 1.6 improves enough to justify evaluation.
- Whether fine-tuning IndicF5 on Avi's recording resolves accent and script issues.
- Whether a house-style LoRA is worth the training cost.
- Whether H100 or other hardware is justified for any workload.

Tracked in [OPEN_QUESTIONS.md](../project/OPEN_QUESTIONS.md).
