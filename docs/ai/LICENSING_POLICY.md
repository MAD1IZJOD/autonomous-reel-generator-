# Licensing Policy

| Field | Value |
|---|---|
| Status | Foundation |
| Last updated | 2026-11-27 |
| Related | [Model registry](MODEL_REGISTRY.md), [model evaluation](MODEL_EVALUATION.md), [security boundaries](../architecture/SECURITY_BOUNDARIES.md), [data retention](../infrastructure/DATA_RETENTION.md) |

## 1. Purpose

This product may be commercialised. Therefore every model, tool, dataset, font, asset and provider used in production must have a licence or contract that permits the intended use. A downloadable weight or an open-source repository is not automatically safe to use commercially.

## 2. Principles

- **No unverified commercial use.** A component whose licence is unclear is blocked from production.
- **Licence status is data.** It lives in the registry and is enforced by routing.
- **Review before enablement.** A model or tool is reviewed before it is used in any environment that produces customer-facing output.
- **Conditions are recorded.** A licence with conditions must have those conditions documented and enforced.
- **Consent is separate from licence.** A model may be licensed while a person's likeness or voice is not consented for the intended use.
- **When in doubt, do not ship.** A waiver does not apply to licensing requirements.

## 3. Scope

This policy covers:

- model weights and checkpoints,
- inference runtimes and frameworks,
- editing and rendering tools,
- fonts, textures, templates and design assets,
- music and sound effects,
- datasets used for evaluation or training,
- provider APIs and their terms,
- third-party code dependencies,
- customer- or founder-supplied media.

## 4. Licence categories

| Category | Meaning | Production use |
|---|---|---|
| `allowed` | Commercial use verified for the intended deployment | Yes |
| `allowed_with_conditions` | Commercial use permitted with recorded conditions | Yes, if conditions are enforced |
| `research_only` | Non-commercial or research-only terms | No |
| `unclear` | Not yet verified | No |
| `rejected` | Explicitly not permitted | No |

## 5. Review process

Before a component is enabled in production:

1. Obtain the actual licence text, not a summary or model card.
2. Record the component, version, source URL, licence name and licence text hash in the registry.
3. Determine the category and any conditions.
4. Identify restrictions on redistribution, modification, output use, attribution and data use.
5. Record the review date, reviewer and evidence link.
6. If the component is used in a customer-facing output, verify that the licence permits that use.
7. If the licence changes between versions, re-review.

A component without a completed review cannot be selected by routing.

## 6. Model-specific rules

- Model weights must be pinned by version and hash.
- A new model version requires a new licence review; licences can change between versions.
- Fine-tuning or merging weights may create a derivative work with different obligations.
- A model licensed for research cannot be used for a commercial product, even if it is "open".
- A model with a custom licence or consent condition requires legal review, not just engineering judgement.
- Model cards and README summaries are not authoritative.

## 7. Tool and dependency rules

- Every dependency must have a stated reason and a licence review.
- Copyleft licences require explicit review before inclusion in a commercial product.
- Font licences must permit embedding and commercial use in video output.
- Design assets (textures, stickers, templates) must have a recorded source and licence.
- FFmpeg and HyperFrames usage must comply with their respective licences and any codec patents relevant to the deployment region.

## 8. Data and media rules

- Source footage, voice samples and likeness data must have documented ownership or consent.
- Customer-supplied media is used only according to the customer's contract and data-processing terms.
- Generated outputs containing a real person's likeness or voice require consent records.
- Training or fine-tuning on a person's likeness or voice requires explicit consent for that purpose.
- Third-party music and SFX require a licence or a documented royalty-free source.
- Procedurally generated audio must not incorporate unlicensed training data.

## 9. Provider terms

- Premium provider terms govern data retention, deletion, output ownership and usage restrictions.
- Provider terms are recorded in the registry with the provider account.
- A provider that retains or trains on customer data requires explicit workspace policy approval.
- Deletion guarantees from providers must be verified or documented as unverifiable.
- Cost and usage limits are operational constraints, not licence terms, but must be respected.

## 10. Excluded components

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

This list is a starting point from the founder's email. Each entry must be verified against the actual licence text before being treated as final.

## 11. Consent records

Consent is required for:

- voice cloning,
- avatar or digital twin generation,
- likeness use in generated video,
- training or fine-tuning on a person's data.

A consent record includes:

- subject identity
- scope and permitted uses
- granting party
- date and expiry
- revocation process
- link to the assets and providers that use it

Revocation blocks new generation and export using that likeness or voice. Existing exports are handled according to policy and contract.

## 12. Enforcement

- Routing refuses to select a model whose licence status is not `allowed` or `allowed_with_conditions`.
- CI or release checks verify that no excluded dependency or model is introduced.
- A licence change is treated as a breaking change and requires re-evaluation.
- Violations are reported as incidents, not accepted as technical debt.

## 13. Open questions

- Exact licence terms for the open-weight models currently used.
- Whether Qwen-Image 2.0 or newer versions are commercially usable.
- Whether customer-managed deployments change licence obligations.
- How to verify deletion in provider-side storage.
- Whether model weights can be redistributed or cached under their licences.
- Whether fine-tuning creates obligations not present in the base model licence.

Tracked in [OPEN_QUESTIONS.md](../project/OPEN_QUESTIONS.md).
