# Development Guide

| Field | Value |
|---|---|
| Status | Provisional; commands will be added when the application exists |
| Last updated | 2026-11-27 |
| Related | [Repository structure](REPOSITORY_STRUCTURE.md), [tech stack](TECH_STACK.md), [testing strategy](TESTING_STRATEGY.md), [CONTRIBUTING.md](../../CONTRIBUTING.md) |

## 1. Prerequisites

The foundation phase requires only:

- Git with the required commit identity configured.
- A Markdown editor with Mermaid preview support.
- Access to this repository and its documentation.

When implementation begins, the expected baseline will be:

- Python 3.12.
- Node.js LTS for the web application and HyperFrames tooling.
- Docker and Docker Compose.
- PostgreSQL 16 client tools.
- FFmpeg and FFprobe.
- A secret manager or local secret store.

Do not install application dependencies during the foundation phase.

## 2. Local development (planned)

The intended local stack is:

```text
docker compose up
```

This will start:

- PostgreSQL
- MinIO (S3-compatible storage)
- API server
- CPU worker
- Web application

GPU inference will not run locally by default. Development against GPU capabilities will use a sandboxed provider or recorded fixtures unless a live run is explicitly approved and cost-capped.

## 3. Working on a change

1. Read `AGENTS.md` or `CONTRIBUTING.md`.
2. Create a branch named `feat/<topic>`, `fix/<topic>`, `docs/<topic>` or `chore/<topic>`.
3. Make the smallest coherent change.
4. Add or update tests for behaviour changes.
5. Run the relevant checks.
6. Update documentation and ADRs.
7. Commit with the required identity and push.

## 4. Code organisation rules

- Domain logic stays in `packages/domain` and has no framework imports.
- Application services orchestrate domain objects and ports.
- Provider SDK code lives only in `packages/providers`.
- Database and storage SDK code lives only in `packages/storage`.
- HTTP handlers stay thin: parse, authorize, call a use case, return.
- Errors are typed and mapped at the boundary; domain code does not know HTTP status codes.

## 5. Database changes

- Every schema change is an Alembic migration.
- Migrations are reviewed for reversibility and data safety.
- Test migrations against a database restored from a backup or a representative fixture.
- Do not edit production schema manually.
- Seed data for development is separate from migrations.

## 6. Running tests (planned)

```text
# Python
pytest

# Type checking
mypy packages/domain packages/application

# Lint and format
ruff check .
ruff format --check .

# Frontend
npm test
npm run lint
npm run typecheck
```

The exact commands will be documented in `pyproject.toml` and `package.json` when those files exist. Until then, documentation changes are validated by link and Markdown review.

## 7. Working with media locally

- Use synthetic or explicitly approved media.
- Keep media under ignored directories such as `media/`, `artifacts/` or `tmp/`.
- Never commit footage, voice samples or generated videos.
- Delete temporary files after tests.
- Use content hashes to verify inputs.

## 8. Working with models and providers

- Do not call premium providers from tests unless the test is explicitly marked as a live, cost-capped smoke test.
- Use recorded contract fixtures for adapter tests; label them clearly.
- Never hardcode model names in domain code; use the registry.
- Check licence status before enabling a model in any environment.
- Record provider request identifiers for debugging.

## 9. Cost awareness

- GPU and premium API calls cost money. Treat them as production actions even in development.
- Use draft quality profiles and low-resolution settings for development where the workflow supports them.
- Terminate GPU sessions manually if automation fails.
- Review cost entries after any live run.
- Do not leave pods running overnight.

## 10. Debugging

- Use correlation IDs and trace IDs from logs and the UI.
- Inspect job attempts, leases and error classifications before retrying.
- Check provider status and cost before assuming an application bug.
- For media issues, inspect the render manifest and FFprobe output.
- For QC issues, inspect raw metric values, not only pass/fail.

## 11. Documentation expectations

- Update docs in the same change as code.
- Record architectural decisions in an ADR.
- Update `docs/project/PROGRESS.md` with evidence.
- Keep `CHANGELOG.md` current for user-visible or operational changes.

## 12. Local environment hygiene

- Keep `.env` out of Git.
- Use separate workspaces or prefixes for experimental data.
- Do not reuse production credentials in development.
- Rotate any credential that is accidentally exposed.

## 13. Open questions

- The exact local development commands and tool versions.
- Whether GPU development uses a remote dev pod or recorded fixtures only.
- Whether database seeding is automated.
- Whether the web app and API share a dev proxy.

Tracked in [OPEN_QUESTIONS.md](../project/OPEN_QUESTIONS.md).
