# Project directory guide

Run all Makefile commands from the repository root. Start with `make help`.

| Directory | Responsibility | Conventions |
| --- | --- | --- |
| `backend/` | FastAPI, SQLite accounts, DSA API | Import using `backend.*`; launch with `python -m backend.app` or `uvicorn backend.app:app`. |
| `backend/content/dsa/` | Server-owned DSA curriculum | JSON is validated by `make validate` and served through `/api/dsa/*`. |
| `backend/requirements/` | Python dependency inputs and locks | `base.txt`/`dev.txt` declare dependencies; `runtime.lock`/`dev.lock` pin tested versions. |
| `frontend/` | Public static web root | Browser URLs remain `/js/*`, `/css/*`, `/tracks/*`, `/assets/*`; do not add `frontend/` to URLs. |
| `frontend/js/data/` | Browser-loaded track data and translations | Keep existing script load order; content packs load after their data files. |
| `frontend/assets/courses/` | Published course materials | Preserve original PDF, notebook, image, dataset, and starter-code files. |
| `docker/` | Docker images, Compose stacks, Caddy | Build context is repository root; production Compose is standalone. |
| `tests/` | Python and dependency-free Node tests | Python imports backend modules; Node tests read files under `frontend/`. |
| `tests/browser/` | Existing Playwright checks | Requires Playwright and a running app; browser URLs do not change. |
| `tools/` | Host/container operational utilities | `validate_dsa.py`, `smoke.py`, and `database.py`; none are web-served. |
| `docs/` | Deployment, implementation notes, content audits | Historical session notes live in `docs/archive/`. Older audits may mention paths before this reorganization. |
| `.github/` | Tests, image publishing, dependency automation | CI publishes passing release images to GHCR; host deployment is manual. |

## Runtime state

Local Python retains the existing root `1991_academy.db` default to preserve
existing accounts. Override `ACADEMY_DB` to place it elsewhere. Docker stores
`/data/academy.db` in an environment-specific named volume. Backups go to the
ignored `backups/` directory; `.env`, `.env.production`, `.venv/`, and caches
are also ignored. Never place secrets or account databases in `frontend/`.

## Entry points

```bash
make setup                  # Python development dependencies
make dev                    # localhost FastAPI with reload
make check                  # Node/Python regressions and curriculum validation
make up                     # Docker development
make docker-test            # disposable Docker test container
make prod-up                # production HTTPS stack (configure .env.production first)
```

The root README gives the quick start. [DEPLOYMENT.md](DEPLOYMENT.md) explains
HTTPS, image releases, persistence, backups, restore, and rollback.
