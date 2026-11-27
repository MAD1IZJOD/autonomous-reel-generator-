# Provider Abstraction

| Field | Value |
|---|---|
| Status | Foundation |
| Last updated | 2026-11-27 |
| Related | [Model routing](MODEL_ROUTING.md), [model registry](MODEL_REGISTRY.md), [component design](../architecture/COMPONENT_DESIGN.md), [error handling](../engineering/ERROR_HANDLING.md) |

## 1. Purpose

Providers are suppliers of capabilities, not architectural centres. The application must be able to replace a provider without rewriting domain logic. Provider abstraction makes that possible by defining ports, normalising behaviour and isolating SDK code.

## 2. Port definition

A provider implements a capability port. The port is defined in the application layer and depends only on domain types.

```python
class ProviderPort(Protocol):
    capability: ClassVar[Capability]

    async def execute(
        self,
        request: ProviderRequest,
        ctx: CallContext,
    ) -> ProviderResult: ...

    async def reconcile(
        self,
        provider_job_id: str,
        ctx: CallContext,
    ) -> ProviderResult | None: ...

    async def health(self) -> ProviderHealth: ...
```

Rules:

- A provider adapter is the only place where the provider SDK is imported.
- Domain and application code depend on the port, not the adapter.
- The adapter translates provider-specific errors, usage and cost into application types.
- The adapter does not make routing decisions.

## 3. Request and result contracts

`ProviderRequest` contains:

- capability and model version
- typed inputs (text, asset references, references, dimensions, duration)
- settings canonicalised by the domain
- output specification
- idempotency key
- deadline

`ProviderResult` contains:

- status (`succeeded`, `failed`, `pending`)
- output asset staging references
- provider job identifier
- usage metrics (characters, seconds, images, tokens)
- estimated and actual cost
- timing (queue, processing, upload)
- error classification if failed
- provider-specific metadata needed for reconciliation

The result is validated before it is accepted as a job success.

## 4. Idempotency

- Every provider call carries an idempotency key derived from the job.
- If the provider supports idempotency keys, the adapter uses them.
- If not, the adapter checks for an existing provider job before creating a new one.
- A retry after an ambiguous failure must reconcile before dispatching.
- The idempotency key is stored with the provider call record.

Ambiguous failures are common with network timeouts. The adapter must treat "did the provider charge?" as a first-class question.

## 5. Error normalisation

Adapters must translate all provider errors into the application error taxonomy:

| Provider condition | Application error |
|---|---|
| Invalid request | `VAL_` or `CONFIG_` |
| Authentication failure | `AUTHN_` |
| Rate limit | `PROV_RATE_LIMIT` (retryable) |
| Timeout | `PROV_TIMEOUT` (retryable) |
| Server error | `PROV_SERVER` (retryable) |
| Quota exceeded | `BUDGET_` or `PROV_QUOTA` |
| Content policy rejection | `POLICY_` |
| Missing artifact | `PROV_NO_ARTIFACT` |

The original provider code and request identifier are preserved in logs, never in the UI.

## 6. Configuration and credentials

- Provider credentials are referenced by name and resolved at runtime from a secret manager.
- Endpoint, timeout, retry and rate-limit settings are configuration.
- Model version and deployment digest are registry data, not adapter constants.
- A provider can be disabled by policy without code changes.
- Adapter health checks are exposed and monitored.

## 7. Data handling

- The adapter sends the minimum data required for the capability.
- It records the egress decision and data class.
- It does not log request bodies containing media, prompts with personal data or credentials.
- It validates output MIME type and size before promotion.
- It cleans up temporary files after upload.

## 8. Cost and usage normalisation

- The adapter normalises usage into a standard `ProviderUsage` record.
- Cost is calculated using registry cost inputs, not hardcoded prices.
- Credit-based pricing is converted to a monetary estimate with the conversion rate recorded.
- Failed calls that incur charges create cost entries.
- Usage is attributed to run, stage, shot and provider.

## 9. Health and availability

- `health()` checks connectivity and authentication without generating billable output.
- Health status feeds routing availability and dashboards.
- A provider marked unhealthy is excluded from routing until it recovers or an administrator overrides.
- Health checks are rate-limited to avoid consuming provider quota.

## 10. Adding a new provider

1. Define the capability port if it does not exist.
2. Implement the adapter in `packages/providers`.
3. Add configuration and credential references.
4. Add contract tests with recorded fixtures.
5. Add a documented live smoke test with a cost cap.
6. Register models and deployments in the registry.
7. Complete licence and terms review.
8. Record the provider in the routing policy.
9. Update documentation and ADRs if the provider changes architecture.

A provider is not production-ready until all steps are complete.

## 11. Testing

- Contract tests cover success, validation failure, rate limit, timeout, server error and missing artifact.
- Fixtures are labelled with provider API version and date.
- Live smoke tests are separate, cost-capped and manually triggered.
- Adapters are tested with a fake clock for retries and timeouts where possible.
- No test may run against a production provider account by default.

## 12. Open questions

- Whether to support streaming responses from providers.
- Whether to use a generic HTTP adapter or one per provider.
- How to handle providers that return async job IDs requiring polling.
- Whether to cache provider responses for identical requests.
- How to represent multi-part or multi-asset outputs.

Tracked in [OPEN_QUESTIONS.md](../project/OPEN_QUESTIONS.md).
