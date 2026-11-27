# Contributing

This repository is being built as a commercial product. Contributions must preserve reproducibility, quality and the trust of the people whose likeness and voice are used in generated videos.

AI agents must also read `AGENTS.md`; the rules there are binding.

## Current phase

The project is in the foundation phase. There is no runnable application and no dependency manifest. Contributions at this stage are documentation, architecture decisions, audit findings and reproduction evidence. Do not open a pull request that scaffolds application services before Milestone 0 and Milestone 1 are complete.

## Before you start

1. Read `README.md`, `docs/project/PROGRESS.md` and `docs/project/OPEN_QUESTIONS.md`.
2. Check whether your change is already covered by an ADR or open question.
3. For a non-trivial change, open an issue or discussion describing the problem, the proposed approach and the evidence you will use. Architecture, security, cost and model-quality changes require an ADR.
4. Never work with private founder footage, customer media or credentials in a public fork.

## Development setup

Not available yet. When Milestone 2 begins, this section will be replaced with the supported Python/Node versions, local PostgreSQL and S3-compatible storage setup, migration commands and the test command. Until then, the only requirement is Git and a Markdown editor with Mermaid preview support.

## Branching and commits

- `main` is the only long-lived branch and must remain deployable once a deployable artifact exists.
- Work on a short-lived branch named `feat/<topic>`, `fix/<topic>`, `docs/<topic>` or `chore/<topic>`.
- Commit in small, logical units. Foundation-phase documentation is committed one file at a time.
- Commit messages use the imperative mood and explain intent, for example:
  - `docs: define the job state machine and retry semantics`
  - `feat: add idempotent stage execution to the worker`
  - `fix: prevent duplicate GPU sessions on lease expiry`
- Do not add AI co-author trailers, session identifiers or alternate identities.
- Do not amend, rebase or force-push published commits. If history needs correction, add a new commit.

### Required commit identity

```text
Madhavan <175943252+MAD1IZJOD@users.noreply.github.com>
```

Both author and committer must match. Verify with `git log -1 --format=fuller` before pushing.

## Pull requests

A pull request must include:

- The problem and why it matters.
- What changed and what deliberately did not change.
- Evidence: test output, measured timings, QC reports, screenshots of UI states, or links to stored artifacts.
- Cost impact if the change affects GPU use, paid APIs or storage.
- Security and privacy impact if the change touches media, credentials, provider egress or tenancy.
- Documentation updates, including ADRs and `docs/project/PROGRESS.md`.
- Known limitations and follow-up work.

Reviewers should reject changes that:

- Claim a model, benchmark or licence fact without a source.
- Mark work successful without real output and validation.
- Bypass approval gates or QC thresholds silently.
- Hardcode provider model names, credentials or workspace-specific values in domain logic.
- Add a dependency without a stated reason and licence review.
- Send media to an external provider without an explicit policy.

## Coding standards

These will be enforced once code exists. The intended baseline:

- Python 3.12, type hints on public interfaces, Ruff for lint/format, mypy in strict mode for domain packages.
- TypeScript strict mode for the web application.
- Domain logic separated from transport, persistence and provider SDKs.
- Explicit error types; no bare `except` blocks that hide failures.
- Structured logging with correlation identifiers; no media or secrets in logs.
- Database changes through migrations; no manual schema edits.
- Configuration through environment variables validated at startup; no secrets in source.

## Testing

Follow `docs/engineering/TESTING_STRATEGY.md`. At minimum:

- New domain behaviour has unit tests.
- New persistence or queue behaviour has integration tests against real PostgreSQL.
- New provider adapters have contract tests and a documented live smoke test.
- Bug fixes include a regression test.
- Test fixtures are synthetic or approved for use and are labelled.

## Documentation

- One canonical home per fact; cross-reference instead of duplicating.
- Mermaid diagrams must render on GitHub.
- Relative links must resolve.
- Mark unresolved facts as `Unknown`, `Provisional` or `Blocked`.
- Update `CHANGELOG.md` for user-visible or operationally significant changes.

## Security and privacy

- Never commit secrets. If a secret is exposed, revoke it first, then report it privately.
- Never commit private footage, voice samples, customer data or generated videos containing real people without explicit permission.
- Report vulnerabilities privately to the repository owner; do not open a public issue with exploit details.
- Follow `docs/infrastructure/SECURITY.md` and `docs/infrastructure/DATA_RETENTION.md`.

## Definition of done

A contribution is done when it is implemented, validated, documented, reviewed, committed with the required identity and pushed. "Works on my machine" is not evidence; include the command and its output or the measured artifact.

## Licensing of contributions

No open-source licence has been selected for this repository. Do not assume that contributing grants or receives reuse rights. This is tracked in `docs/project/OPEN_QUESTIONS.md`.
