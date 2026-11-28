# Founder Materials Checklist

| Field | Value |
|---|---|
| Status | Open request; nothing received at the time of writing |
| Last updated | 2026-11-28 |
| Related | [Existing workflow](EXISTING_WORKFLOW.md), [unknown configurations](UNKNOWN_CONFIGURATIONS.md), [baseline reproduction plan](BASELINE_REPRODUCTION_PLAN.md) |

## 1. Purpose

Milestone 0 cannot be completed from documentation alone. This checklist defines exactly what is needed from the founder, why it is needed, what format is acceptable, and what "received and usable" means.

Nothing in this repository should be read as a claim that these materials exist in a particular form. The list is a request, not an inventory.

## 2. Priority definitions

| Priority | Meaning | Consequence if missing |
|---|---|---|
| **P0** | Required to finish Milestone 0 | Discovery cannot be closed; Milestone 1 cannot be planned |
| **P1** | Required to run the baseline reproduction | Milestone 1 slips or runs with unverified assumptions |
| **P2** | Required before productisation or commercial launch | Legal or operational risk carried forward |
| **P3** | Helpful for quality or efficiency | Slower optimisation; no hard block |

## 3. Checklist

### A. Controller and scripts

| ID | Item | Why it is needed | Acceptable format | Priority | Status |
|---|---|---|---|---|---|
| M-001 | The Claude Code project or workspace used to run the pipeline | The controller is the actual orchestration logic; without it the workflow is only described, not reproducible | Repository export, zip, or read-only access | P0 | Not received |
| M-002 | All skill files and prompt templates | They encode plate-sheet rules, style rules and stage instructions that are not written elsewhere | Markdown/text files as used | P0 | Not received |
| M-003 | Every Python, shell and JavaScript tool invoked by the controller | Needed to distinguish reusable code from prompts and manual steps | Source files with directory structure | P0 | Not received |
| M-004 | Entry-point commands and the order they are run in | The controller may call tools in a non-obvious sequence | README, shell history or annotated list | P0 | Not received |
| M-005 | Any `.env`, config or settings files, with secrets redacted | Names and defaults reveal providers, paths and model identifiers | Redacted copies; keys replaced with placeholders | P0 | Not received |
| M-006 | Dependency manifests or installed-package lists | Exact versions affect reproducibility and licences | `requirements.txt`, `pyproject.toml`, `package.json`, `pip freeze`, `conda list` | P1 | Not received |
| M-007 | Git history or dated backups, if any | Shows what changed and which version produced which video | Bundle or archive | P3 | Not received |

### B. Planning artifacts

| ID | Item | Why it is needed | Acceptable format | Priority | Status |
|---|---|---|---|---|---|
| M-010 | At least three complete plate sheets used in real productions | The schema, field semantics and timing rules cannot be inferred from prose | Raw JSON plus the script they belong to | P0 | Not received |
| M-011 | Plate sheets for both explainer and character/story profiles | The profiles have different ordering and approval rules | Raw JSON | P1 | Not received |
| M-012 | The prompt or skill text that generates plate sheets | Determines validation rules and planner behaviour | Prompt files or screenshots | P0 | Not received |
| M-013 | Examples of rejected or corrected plate sheets | Reveals failure modes and human corrections | Any format | P2 | Not received |
| M-014 | The script format and approval process | Script is the pipeline's root artifact | Template plus one approved example | P1 | Not received |

### C. Image, motion and lip-sync configuration

| ID | Item | Why it is needed | Acceptable format | Priority | Status |
|---|---|---|---|---|---|
| M-020 | ComfyUI workflow JSON for Qwen-Image stills | The graph, sampler, steps, CFG, resolution and LoRA wiring are otherwise unknown | Exported workflow JSON | P0 | Not received |
| M-021 | ComfyUI workflow JSON for Qwen-Image-Edit-2511 | Same reason for multi-reference editing | Exported workflow JSON | P1 | Not received |
| M-022 | ComfyUI workflow JSON for Wan 2.2 I2V A14B fp8 + LightX2V | Motion quality and cost depend on exact settings | Exported workflow JSON | P0 | Not received |
| M-023 | ComfyUI workflow JSON for InfiniteTalk | Needed for the open lip-sync baseline and evaluation | Exported workflow JSON | P1 | Not received |
| M-024 | Exact model file names, versions, hashes and sources | "Qwen-Image" and "Wan 2.2" are families, not reproducible versions | List with URLs, filenames, sizes and hashes if available | P0 | Not received |
| M-025 | Custom nodes and ComfyUI version | Workflows fail without matching custom nodes | `comfyui.log`, node list, or environment export | P1 | Not received |
| M-026 | Seed policy and candidate count per shot | Determines cost and retake behaviour | Notes or workflow values | P1 | Not received |
| M-027 | Example inputs and outputs for one shot | Allows configuration to be checked against real media | Original stills, prompts, clips | P1 | Not received |

### D. Voice configuration

| ID | Item | Why it is needed | Acceptable format | Priority | Status |
|---|---|---|---|---|---|
| M-030 | ElevenLabs model and voice identifiers, with account plan | Reproduces the baseline voice and its cost | IDs and plan name; no API key needed for M0 | P0 | Not received |
| M-031 | Exact request settings per language | Stability, similarity, style and speaker boost affect output | Screenshots or exported settings | P0 | Not received |
| M-032 | Pronunciation glossary and Devanagari transliteration rules | This is a major source of quality and retakes | Document or prompt file | P1 | Not received |
| M-033 | Post-processing scripts | Pause squeeze, 1.2x speed and -14 LUFS are reported but not specified | Scripts or FFmpeg commands | P0 | Not received |
| M-034 | Voice QC scripts and thresholds | Similarity and CER gates must be reproduced | Scripts plus threshold values | P1 | Not received |
| M-035 | Sample source audio and generated voice for the same script | Needed to validate similarity and accent | Audio files | P2 | Not received |

### E. Presenter and avatar

| ID | Item | Why it is needed | Acceptable format | Priority | Status |
|---|---|---|---|---|---|
| M-040 | HeyGen plan, avatar IDs and twin orientation | Baseline presenter generation and cost | IDs and plan name; no credentials in repository | P0 | Not received |
| M-041 | Segment boundaries and input format sent to HeyGen | Determines cost, retries and lip-sync behaviour | Notes plus one example request | P0 | Not received |
| M-042 | Example HeyGen outputs at production settings | Reference for visual and mouth QC | Video files | P1 | Not received |
| M-043 | InfiniteTalk test outputs and failure examples | Documents the gap to HeyGen and the jaw over-stretch issue | Video files plus settings | P2 | Not received |
| M-044 | Avatar consent and likeness agreement | Commercial use of a digital twin requires documented consent | Signed agreement or summary | P2 | Not received |

### F. Composition, graphics and render

| ID | Item | Why it is needed | Acceptable format | Priority | Status |
|---|---|---|---|---|---|
| M-050 | HyperFrames project or template | Composition structure and render settings are unknown | Project archive | P0 | Not received |
| M-051 | HTML/GSAP/Three.js motion-graphic components | Reusable graphics logic and timing rules | Source files | P1 | Not received |
| M-052 | Brand and editorial design kit | Fonts, colours, textures, logos, stickers, grade | Asset archive plus licence notes | P1 | Not received |
| M-053 | Final render command or settings | Resolution, codec, bitrate and audio mapping are unknown | Command, config or screenshot | P0 | Not received |
| M-054 | Caption/subtitle pipeline | Caption timing and styling affect QC and reach | Scripts, templates, examples | P2 | Not received |
| M-055 | One complete project directory | Shows how assets, project files and outputs are laid out | Archive | P1 | Not received |

### G. Audio mix and assets

| ID | Item | Why it is needed | Acceptable format | Priority | Status |
|---|---|---|---|---|---|
| M-060 | Music source and licence terms | Export legality depends on it | Licence documents or account/subscription details | P2 | Not received |
| M-061 | SFX library and procedural SFX scripts | Cue generation and mix depend on them | Files plus scripts | P1 | Not received |
| M-062 | Mix and mastering chain | -14 LUFS and true-peak targets need exact processing | Script, DAW preset or FFmpeg chain | P1 | Not received |
| M-063 | Real proof asset inventory and usage rights | Proof visuals are core to the format and may be client-confidential | Inventory plus rights notes | P2 | Not received |

### H. QC and acceptance

| ID | Item | Why it is needed | Acceptable format | Priority | Status |
|---|---|---|---|---|---|
| M-070 | All QC scripts | Voice similarity, CER, SyncNet, MediaPipe and custom checks are not standard | Source files | P0 | Not received |
| M-071 | Exact thresholds and pass/fail rules | Reported values are partial and may be per-project | Config or code constants | P0 | Not received |
| M-072 | Contact sheet / review template | Human review is part of QC | Template or example | P2 | Not received |
| M-073 | Three accepted final videos with their source scripts and plate sheets | Ground truth for reproduction and blind comparison | Video files plus planning artifacts | P0 | Not received |
| M-074 | Three rejected or reworked examples with reasons | Defines the negative boundary | Video files plus notes | P2 | Not received |

### I. Accounts, billing and infrastructure

| ID | Item | Why it is needed | Acceptable format | Priority | Status |
|---|---|---|---|---|---|
| M-080 | Billing export for a representative production week | Validates the $9.06 / ~$1 figures and reveals hidden costs | CSV or invoice summary with sensitive data redacted | P1 | Not received |
| M-081 | RunPod instance types, regions and images used | Reproduces GPU performance and cost | Screenshots or notes | P0 | Not received |
| M-082 | Pod setup and model download procedure | The ~12-minute setup and ~75 GB download are major waste sources | Script, notes or shell history | P0 | Not received |
| M-083 | Confirmation that reference runs may use existing paid accounts | Needed before any spend in Milestone 1 | Written confirmation and spend cap | P0 | Not received |
| M-084 | Provider rate limits, quotas and plan restrictions | Affects throughput and failure behaviour | Plan details or notes | P2 | Not received |

### J. Environment and machine state

| ID | Item | Why it is needed | Acceptable format | Priority | Status |
|---|---|---|---|---|---|
| M-090 | Mac model, OS version and installed tool versions | Local render and QC depend on them | `system_profiler`, `brew list`, `ffmpeg -version` | P1 | Not received |
| M-091 | Python, Node, FFmpeg, Whisper and MediaPipe versions | Version drift changes behaviour | Command output | P1 | Not received |
| M-092 | Directory layout on the Mac and on pods | Shows where artifacts and models live | Annotated tree | P1 | Not received |
| M-093 | Known local failure workarounds | Encodes operational knowledge | Notes | P2 | Not received |

### K. Legal and commercial

| ID | Item | Why it is needed | Acceptable format | Priority | Status |
|---|---|---|---|---|---|
| M-100 | Licence status of every model and tool in use | Some reported models have commercial restrictions | List with source URLs and terms | P0 | Not received |
| M-101 | Client contracts or usage constraints for proof assets | Determines what can be shown and stored | Summary of constraints | P2 | Not received |
| M-102 | Data retention and deletion expectations | Affects storage and compliance design | Written requirements | P2 | Not received |
| M-103 | Brand usage rules for Avi's likeness and name | Commercial product scope depends on it | Written summary | P2 | Not received |

## 4. Minimum package to close Milestone 0

If the full checklist is impractical, these items are sufficient to close discovery with documented gaps:

1. M-001, M-002, M-003, M-004 — controller and scripts.
2. M-010, M-012 — real plate sheets and the prompt that generates them.
3. M-020, M-022, M-024 — image and motion workflows plus exact model files.
4. M-030, M-031, M-033 — voice settings and post-processing.
5. M-040, M-041 — avatar setup and segment handling.
6. M-050, M-053 — composition project and render settings.
7. M-070, M-071 — QC scripts and thresholds.
8. M-073 — three accepted outputs with their sources.
9. M-081, M-082, M-083 — GPU setup and permission to reproduce.
10. M-100 — licence status.

## 5. Package acceptance criteria

The materials package is considered received when:

- every P0 item is either delivered or explicitly waived in writing;
- delivered scripts run, or their missing dependencies are identified;
- plate sheets parse as JSON and reference real scripts;
- ComfyUI workflows import or their missing custom nodes are listed;
- model identifiers resolve to specific files or provider versions;
- secrets are redacted and no credentials are committed;
- the founder confirms which outputs are considered accepted references.

A delivery that is only described verbally does not satisfy the checklist.

## 6. Handling and security

- Do not send API keys, passwords or session tokens. Redact them before transfer.
- Transfer large media through a private object store or shared drive, not chat attachments.
- Mark client-confidential material explicitly so it is excluded from public documentation.
- Store received material outside the Git repository unless it is safe to commit.
- Record receipt, date and hash for each delivered archive.

## 7. Request message template

> To close Milestone 0 I need the actual artifacts, not a description of them. The highest-value items are: the Claude Code workspace and skill files, three real plate sheets with their scripts, the ComfyUI workflow JSON for Qwen-Image and Wan 2.2 with exact model filenames, the ElevenLabs settings and post-processing scripts, the HeyGen avatar IDs and segment approach, the HyperFrames project and final render settings, all QC scripts with thresholds, three accepted final videos with their source artifacts, and the RunPod setup procedure. Please redact credentials. If an item does not exist in a reusable form, say so explicitly so it can be recorded as a gap rather than assumed.

## 8. Status log

| Date | Event | Result |
|---|---|---|
| 2026-11-28 | Checklist created | No materials received |
