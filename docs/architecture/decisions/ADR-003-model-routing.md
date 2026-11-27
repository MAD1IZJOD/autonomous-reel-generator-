# ADR-003: Capability-based model routing

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-11-27 |
| Deciders | Engineering (Madhavan), Product (Avinash Pandit) |
| Related | [Model routing](../../ai/MODEL_ROUTING.md), [provider abstraction](../../ai/PROVIDER_ABSTRACTION.md), [licensing policy](../../ai/LICENSING_POLICY.md) |

## 1. Context

The current workflow names providers and models directly in scripts and skill files. That makes it hard to compare open-weight and premium options, apply licensing rules, control egress or change a model without editing workflow code. The founder wants to move towards open models where quality and economics justify it, but not at the cost of silent quality loss.

## 2. Decision

The application requests a **capability**, not a model name. A routing engine selects a model version using a recorded policy and the model registry.

Routing inputs:

1. Capability and language.
2. Workspace policy: allowed providers, data class, egress permission.
3. Licence status: production-enabled only.
4. Quality floor for the selected profile.
5. Cost per accepted output and latency target.
6. GPU availability and warm-pool state.
7. Fallback chain and whether the fallback preserves quality.

The routing decision, including rejected candidates and reasons, is stored with the run. A fallback that crosses a quality floor requires approval.

## 3. Alternatives considered

### 3.1 Hardcoded provider calls

Rejected. This is the current state. It prevents comparison, licensing enforcement, fallback and cost-based decisions.

### 3.2 Always choose the cheapest eligible model

Rejected. It optimises a proxy metric and can silently degrade quality. Cost is considered, but only alongside the quality floor and the measured cost per accepted output.

### 3.3 Always choose the highest-quality model

Rejected. It ignores cost and privacy, and would prevent the use of cheaper open models where they are good enough.

### 3.4 Manual selection only

Rejected as the default. Operators can override routing within policy, but the system must make a safe default decision and record it.

## 4. Consequences

Positive:

- Models become replaceable without code changes.
- Licensing and egress policy are enforceable at the point of use.
- Cost and quality trade-offs are visible and auditable.
- Open and premium models can be compared on the same capability.

Negative:

- Routing logic is more complex than a direct call.
- Bad registry data can produce bad decisions; registry hygiene is a prerequisite.
- Quality floors must be calibrated from real evaluation, not guesswork.

Mitigations:

- The registry requires licence status and evaluation status before production enablement.
- Routing decisions are stored and reviewable.
- Overrides require a role and are audited.
- Evaluation gates are defined in [MODEL_EVALUATION.md](../../ai/MODEL_EVALUATION.md).

## 5. Reversal criteria

This decision is expected to persist for the life of the product. The routing inputs and weights will change with evidence. A replacement would require demonstrating that direct selection produces better cost, quality and compliance outcomes, which is unlikely given the stated goals.

## 6. Related documents

- [Model registry](../../ai/MODEL_REGISTRY.md)
- [Model routing](../../ai/MODEL_ROUTING.md)
- [Provider abstraction](../../ai/PROVIDER_ABSTRACTION.md)
- [Quality gates](../../ai/QUALITY_GATES.md)
- [Licensing policy](../../ai/LICENSING_POLICY.md)
