# AGENTS.md

Instructions for AI coding agents working in this repository.

This project is an engineering product, not a demo. Agents are expected to behave like careful staff engineers: inspect before changing, state uncertainty, preserve evidence, and never present unverified work as complete.

## 1. Read order before changing anything

1. `README.md` for scope and current status.
2. `docs/project/PROGRESS.md` for the actual state of work.
3. `docs/project/OPEN_QUESTIONS.md` for blockers and unresolved decisions.
4. The relevant architecture decision record under `docs/architecture/decisions/`.
5. The relevant engineering or AI document for the area you will touch.

If documents conflict, stop and resolve the conflict in the documents before writing code. Do not silently choose one interpretation.

## 2. Current phase

The repository is in the **foundation phase**. Application code, dependency installation and service scaffolding are intentionally absent. Do not start Milestone 2 implementation until Milestone 0 (discovery and code audit) and Milestone 1 (reference reproduction) have produced the artifacts described in `docs/project/MILESTONES.md`.

## 3. Non-negotiable engineering rules

- **No fake outputs.** Never generate placeholder video, audio or QC results and present them as inference. Test fixtures must be labelled as fixtures.
- **No mock success.** A job may only be marked `succeeded` when its real output exists, has passed validation, and is recorded with provenance.
- **No invented benchmarks, model capabilities, prices or licence claims.** Cite the founder's measured baseline, a primary source, or mark the statement as an assumption.
- **No secrets in Git.** Never commit API keys, tokens, private footage, customer media or model weights. Use `.env.example` to document variable names.
- **No destructive operations.** Do not delete, reset, rebase, amend published commits or force-push. Preserve history.
- **No silent quality degradation.** A cheaper model or setting may only replace the baseline after evaluation against the quality gates and an explicit routing-policy change.
- **No hardcoded model names in application logic.** Resolve models through the registry and capability-based routing described in `docs/ai/PROVIDER_ABSTRACTION.md`.
- **No unlicensed commercial use.** A model with downloadable weights is not automatically usable. Follow `docs/ai/LICENSING_POLICY.md`.
- **No premature microservices.** Respect the modular-monolith decision in ADR-001.

## 4. Git rules

The only permitted commit identity is:

```text
Author:    Madhavan <175943252+MAD1IZJOD@users.noreply.github.com>
Committer: Madhavan <175943252+MAD1IZJOD@users.noreply.github.com>
```

Never add an AI co-author trailer, a session identifier, or an alternate identity. Never rewrite published history. Never force-push. Never create commits through the GitHub API.

Commit discipline:

- One logical change per commit; for documentation work in the foundation phase, one file per commit unless a reviewed change genuinely requires otherwise.
- Commit messages describe why the change exists, in a real engineer's voice. Avoid "update docs", "AI generated" and similar.
- Stage only intended files. Check `git diff --cached` before committing.
- Push after committing and verify the remote branch points at the new commit.
- If a push fails, stop and investigate. Do not resolve it by force-pushing.

## 5. Code and architecture expectations

- Follow `docs/engineering/REPOSITORY_STRUCTURE.md` and `docs/engineering/TECH_STACK.md`.
- Keep domain logic independent of FastAPI, SQLAlchemy and provider SDKs where practical.
- Every externally visible operation that can be retried must be idempotent or carry an idempotency key.
- Every long-running operation must have a durable job record, a lease/heartbeat, a timeout and a cancellation path.
- Every generated artifact must record: model identifier and version, provider, settings hash, input asset versions, code revision, GPU type, timing and cost.
- Human approval gates are part of the domain model, not UI-only state.
- Errors must be classified and surfaced; never swallow an exception and continue as if a stage succeeded.

## 6. Media and data handling

- Do not commit media. Use object storage for source footage, generated assets, contact sheets and renders.
- Do not send private media to an external provider unless the workspace's policy explicitly allows that provider and data class.
- Do not log raw media, full prompts containing personal data, access tokens or presigned URLs.
- Delete temporary local files created during tests, and keep them inside the repository's ignored directories.

## 7. Testing expectations

- Unit tests for domain rules and state machines.
- Integration tests against real PostgreSQL and S3-compatible storage (containers), not mocks of the database.
- Contract tests for every provider adapter; recorded fixtures are acceptable only when labelled and when a live smoke test is separately documented.
- Golden-file tests for deterministic render/graphics outputs where feasible.
- End-to-end tests must use synthetic or approved media and must never claim production quality.
- A change is not done because tests pass; it is done when the acceptance criteria for the milestone are evidenced.

## 8. Documentation expectations

- Update the affected documents in the same change as the code.
- Record decisions in an ADR when they affect architecture, data, security, cost or model quality.
- Keep `docs/project/PROGRESS.md` current with evidence links.
- Mark unknowns as `Unknown`, `Provisional` or `Blocked`; do not fill gaps with plausible-sounding fiction.
- Cross-reference rather than duplicate. One canonical home per fact.

## 9. When to stop and ask

Stop and report instead of guessing when:

- The repository state is unexpected (uncommitted user changes, unexpected branch, remote divergence).
- A required credential, private asset or founder-owned script is missing.
- A licence is unclear for a model intended for commercial use.
- A quality threshold cannot be measured with the available tooling.
- A requested change would require rewriting published history or changing commit identity.
- A cost or GPU commitment would be made without measured evidence.

## 10. Definition of done for an agent task

A task is complete only when:

1. The change is implemented and reviewed against the relevant acceptance criteria.
2. Tests and validation have actually been run, with results recorded.
3. Documentation and ADRs are consistent with the change.
4. The commit has the required author and committer and has been pushed.
5. The final report separates **verified facts**, **assumptions** and **remaining unknowns**.
