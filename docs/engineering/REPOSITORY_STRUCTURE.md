# Repository Structure

| Field | Value |
|---|---|
| Status | Proposed; to be created during Milestone 2 |
| Last updated | 2026-11-27 |
| Related | [Tech stack](TECH_STACK.md), [component design](../architecture/COMPONENT_DESIGN.md), [development guide](DEVELOPMENT_GUIDE.md) |

## 1. Intent

The repository is a single monorepo. The control plane, CPU workers, web application, domain packages, infrastructure definitions and documentation live together so that a change to a domain invariant and its consumer can be reviewed and deployed atomically. GPU model servers remain separate repositories or image definitions because they have different dependency and release lifecycles.

## 2. Proposed layout

```text
autonomous-reel-generator/
  README.md
  AGENTS.md
  CONTRIBUTING.md
  CHANGELOG.md
  .env.example
  .gitignore
  pyproject.toml
  uv.lock or poetry.lock
  package.json
  pnpm-lock.yaml
  apps/
    api/                      FastAPI control plane and CPU worker entrypoints
      src/arg_api/
      tests/
    web/                      Next.js application
      src/
      tests/
  packages/
    domain/                   Pure domain: entities, state machines, invariants
    application/              Use cases and orchestration services
    orchestration/            Job engine, leases, scheduler
    providers/                Provider adapters and ports
    media/                    FFmpeg, probing, render, composition glue
    qc/                       Metric adapters and gate evaluation
    storage/                  Object storage and database adapters
    routing/                  Model routing and registry access
    telemetry/                Logging, tracing, metrics, audit helpers
    config/                   Settings and environment validation
  infra/
    docker/                   Dockerfiles and compose files
    migrations/               Alembic migrations
    gpu/                      Model server images, bootstrap scripts, pool config
    terraform/ or pulumi/     Optional infrastructure as code
  scripts/
    dev/                      Local development helpers
    audit/                    Reproduction and evidence helpers
  docs/
    ...                       As defined in the foundation phase
  tests/
    e2e/                      End-to-end tests against a running stack
    fixtures/                 Labelled synthetic or approved media
  .github/
    workflows/                CI pipelines
```

## 3. Package boundaries

| Package | May depend on | Must not depend on |
|---|---|---|
| `domain` | Standard library, typing | FastAPI, SQLAlchemy, provider SDKs, storage SDKs |
| `application` | `domain`, ports | FastAPI, SQLAlchemy, provider SDKs |
| `orchestration` | `domain`, `application`, repository ports | HTTP handlers |
| `providers` | `domain`, ports, SDKs | Web framework |
| `storage` | `domain`, database/object SDKs | Business rules |
| `media` | `domain`, FFmpeg, image libs | Web framework |
| `qc` | `domain`, metric libraries | Provider SDKs |
| `routing` | `domain`, registry, policy | Provider SDKs directly |
| `telemetry` | Cross-cutting | Domain rules |
| `config` | Settings validation | Business logic |
| `apps/api` | All packages | Frontend code |
| `apps/web` | API client, UI libs | Python packages |

Dependencies are enforced by import linting or package metadata. A package that needs another package's internals must expose a port instead.

## 4. Application entrypoints

| Entrypoint | Responsibility |
|---|---|
| `apps/api` HTTP server | API requests, auth, signed URLs, run commands |
| `apps/api` CPU worker | Render, probing, QC orchestration, composition |
| `apps/api` GPU agent | Model server health, job execution, artifact upload |
| `apps/web` | Operator and reviewer UI |

The same Python package serves the API and workers; the process role is selected by configuration. This avoids duplicating domain code while allowing independent scaling.

## 5. Configuration and secrets

- `.env.example` documents all variables; `.env` is local-only.
- Settings are validated at startup with clear errors.
- Secrets are referenced by name and resolved at runtime.
- Per-environment values live in the deployment platform, not in the repository.
- Feature flags are database-backed once the application exists.

## 6. Database and migrations

- All schema changes are Alembic migrations.
- Migrations are reviewed and tested against a copy of production-like data before release.
- Destructive migrations require a documented rollback or forward-fix plan.
- Seed data for development is separate from migrations.

## 7. Infrastructure

- `infra/docker` contains Dockerfiles and Compose files for local development.
- `infra/gpu` contains model server images, bootstrap scripts and pool configuration.
- `infra/terraform` or `infra/pulumi` is optional and added only when a cloud deployment requires it.
- Infrastructure code is versioned and reviewed like application code.

## 8. Tests

- Unit and integration tests live next to the package they test where practical.
- Cross-package and end-to-end tests live under `tests/`.
- Fixtures are labelled synthetic or approved and are never committed as private media.
- Golden files are stored under `tests/golden/` with a documented regeneration command.

## 9. Documentation and generated artifacts

- `docs/` is the only place for engineering documentation.
- Generated API clients or schemas, if added, are committed only if they are reviewed and regenerated by CI.
- Build artifacts, caches, media and model weights are ignored.

## 10. Naming conventions

- Python modules and packages use `snake_case`.
- TypeScript uses `camelCase` for variables and functions, `PascalCase` for components and types.
- Database tables use `snake_case` and plural nouns.
- API paths use plural nouns and kebab-case where needed.
- Job and stage identifiers use dotted lowercase (`voice.synthesize`).
- Asset and version identifiers use prefixed ULIDs or UUIDs.

## 11. What must never be committed

- Secrets, tokens, credentials.
- Private footage, voice samples, customer media.
- Model weights, caches, build artifacts.
- Local databases and generated renders.
- Agent or tool state directories.

These are enforced by `.gitignore` and CI secret scanning.

## 12. Open questions

- Whether the frontend and backend share a monorepo or split once the UI stabilizes.
- Whether Python dependencies are managed with `uv`, Poetry or another tool.
- Whether GPU image definitions live in this repository or a dedicated infrastructure repository.
- Whether to publish internal packages or keep them path-based.

Tracked in [OPEN_QUESTIONS.md](../project/OPEN_QUESTIONS.md).
