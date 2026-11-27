# Cost Optimization

| Field | Value |
|---|---|
| Status | Foundation |
| Last updated | 2026-11-27 |
| Related | [GPU orchestration](GPU_ORCHESTRATION.md), [observability](../engineering/OBSERVABILITY.md), [model routing](../ai/MODEL_ROUTING.md), [PRD](../product/PRD.md) |

## 1. Purpose

Cost optimization in this product is not about finding the cheapest model. It is about reducing cost per **accepted** output while preserving quality. The founder's observation is that most waste comes from model loading and setup, not inference.

## 2. Baseline measurements

The following are the founder's reported observations from the existing system. They must be independently reproduced before optimisation claims are made.

| Metric | Reported value | Scope |
|---|---|---|
| 60-second short cost | ~$9.06 | Including pod setup and tests |
| Repeat in same style | ~$1 | Same style, presumably with warm setup |
| Pod setup time | ~12 minutes | Secure cloud |
| Model download | ~75 GB | Per session |
| InfiniteTalk 480p | ~368–425 s per 4-second burst | Plus ~465 s model load |
| InfiniteTalk 720p | Out of memory on L40 | Not viable on L40 |
| L40 with DiT offloading | ~190 s/step | Slow |
| L40 int8 | ~300 s/step | Slower |
| A100 80 GB | ~90 s/step | One tested configuration |

These are not vendor benchmarks. They are one environment's measurements.

## 3. Cost model

Total cost per run:

```text
total_cost =
  paid_api_cost
  + gpu_cost
  + storage_cost
  + egress_cost
  + review_cost (if attributed)
```

GPU cost:

```text
gpu_cost =
  sum over sessions of (
    (provisioning + loading + warmup + inference + idle + teardown) * hourly_rate
  )
```

Cost per accepted output:

```text
cost_per_accepted_output =
  total_cost / accepted_outputs
```

Cost per shot:

```text
cost_per_shot =
  (provider_cost + gpu_cost + storage_cost) / shots
```

Waste ratio:

```text
waste_ratio =
  (failed_attempt_cost + orphaned_session_cost + redundant_regeneration_cost)
  / total_cost
```

## 4. Waste sources

| Source | Why it happens | Mitigation |
|---|---|---|
| Model loading | Fresh pod per session | Resident pools, cached weights |
| Pod provisioning | ~12 minutes per session | Reuse sessions, batch jobs |
| Model download | ~75 GB per session | Persistent cache or baked image |
| Failed attempts | No preflight, late discovery | Preflight on CPU |
| Orphaned sessions | Lost leases, failed teardown | Watchdog, reconciliation |
| Idle GPU time | No batching, poor scheduling | Idle shutdown, compatible-job batching |
| Redundant regeneration | No caching or versioning | Idempotency, asset versioning |
| Over-provisioned hardware | Using A100 for image work | Capability-based pools |
| Premium API overuse | No routing policy | Capability routing, quality floors |
| Human review waste | Too many candidates | At most two scored options |

## 5. Optimization levers

### 5.1 GPU residency

- Keep model servers warm across compatible jobs.
- Cache weights on persistent volumes or bake them into images.
- Batch compatible jobs onto warm sessions.
- Measure load time and warm-up time as first-class metrics.

### 5.2 Preflight

- Validate inputs, licences, routing and budget on CPU before provisioning.
- Reject invalid work before it costs money.
- Reserve budget atomically before dispatch.

### 5.3 Right-sizing

- Use L40 for image and Wan video workloads.
- Use A100 only where the measured workload requires it.
- Do not assume H100 is necessary; the founder explicitly warns against it.
- Re-evaluate hardware when models or providers change.

### 5.4 Idle shutdown

- Shut down idle sessions after 5–10 minutes.
- Run an independent watchdog.
- Attribute orphaned session cost as waste.

### 5.5 Caching and reuse

- Reuse artifacts by idempotency key and content hash.
- Cache provider responses where appropriate.
- Do not regenerate a shot when its inputs and settings are unchanged.

### 5.6 Model routing

- Use open-weight models where they meet the quality floor.
- Keep premium APIs where they measurably win.
- Prefer resident warm models when the cost difference is small.
- Do not silently downgrade quality.

### 5.7 Quantisation and speed

- Apply quantisation only when fast kernels support it; the founder observed int8 was slower on L40.
- Evaluate TeaCache, fewer steps and other speedups as experiments, not defaults.
- Measure quality impact of every speed change.

### 5.8 Storage and egress

- Store media in a cost-appropriate tier.
- Archive superseded versions.
- Monitor egress costs from object storage and providers.
- Avoid proxying large media through the API.

## 6. Guardrails

Cost control is not optional:

- Budget thresholds pause new GPU dispatch.
- Per-run and per-shot cost estimates are shown before execution.
- A run cannot exceed its configured budget without approval.
- Failed paid attempts are recorded as cost.
- Orphaned sessions are attributed as waste.
- Cost anomalies trigger alerts.

## 7. Reporting

Cost reports must answer:

- What did this run cost?
- What did each shot cost?
- Which provider or model cost the most?
- How much was waste?
- How does this compare with the baseline?
- What is the cost per accepted output?
- Which runs exceeded budget and why?

Reports are queryable by run, stage, shot, provider, model, GPU type and time period. They do not require log archaeology.

## 8. Optimization workflow

1. Measure the baseline with a reproducible run.
2. Identify the largest waste source.
3. Apply one lever.
4. Re-measure with the same dataset and hardware.
5. Compare cost per accepted output and quality.
6. Accept or reject the change based on evidence.
7. Record the result.

Do not apply multiple levers at once and then claim a combined saving. Attribute changes individually where possible.

## 9. What not to do

- Do not claim a percentage saving without a measured comparison.
- Do not optimise unit price while ignoring pass rate.
- Do not reduce quality to hit a cost target without an explicit, audited decision.
- Do not keep a model resident if utilization does not justify it, unless latency requires it.
- Do not delete cost history to make reports look better.

## 10. Open questions

- What budget thresholds are appropriate for the first deployment.
- Whether to charge internal cost per run or only track it.
- How to attribute shared GPU session cost across jobs.
- Whether to use spot or preemptible instances for non-critical work.
- How to handle provider pricing changes.

Tracked in [OPEN_QUESTIONS.md](../project/OPEN_QUESTIONS.md).
