# Folder Structure — PitchMind AI

**Version:** 0.1 (Planning)
**Status:** Proposed — awaiting approval

A pragmatic monorepo: one repo, multiple deployables, shared tooling. No micro-package overhead, but cleanly separated concerns.

```
PitchMind-AI/
├── README.md
├── PRD.md
├── SRS.md
├── ARCHITECTURE.md
├── TECH_REVIEW.md
├── ROADMAP.md
├── FOLDER_STRUCTURE.md
├── GIT_STRATEGY.md
├── FEATURES.md
├── EVALUATION.md
├── PROJECT_PROGRESS.md
├── TODO.md
├── CHANGELOG.md
├── LICENSE
├── .gitignore
├── .gitattributes
├── .editorconfig
├── .env.example
├── docker-compose.yml
├── docker-compose.override.yml          # local overrides (gitignored)
├── Makefile                              # tasks: dev, test, lint, format, migrate, seed
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── docker.yml
│   │   └── release.yml
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
├── docs/
│   ├── adr/                              # Architectural Decision Records
│   │   ├── 0000-template.md
│   │   ├── 0001-task-queue.md
│   │   └── ...
│   ├── api/                              # exported OpenAPI, postman
│   ├── diagrams/                         # mermaid, draw.io, png
│   └── models/                           # model cards (outcome, injury, scout)
│
├── infra/
│   ├── docker/
│   │   ├── api.Dockerfile
│   │   ├── worker-cv.Dockerfile
│   │   ├── worker-ml.Dockerfile
│   │   ├── agent.Dockerfile
│   │   ├── model-server.Dockerfile
│   │   └── web.Dockerfile
│   ├── nginx/
│   │   └── nginx.conf
│   ├── caddy/
│   │   └── Caddyfile
│   ├── grafana/
│   │   ├── provisioning/
│   │   └── dashboards/
│   ├── prometheus/
│   │   └── prometheus.yml
│   └── k8s/                              # helm charts (post-MVP)
│
├── backend/
│   ├── pyproject.toml
│   ├── uv.lock                           # or poetry.lock
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   └── src/
│       └── pitchmind/
│           ├── __init__.py
│           ├── main.py                   # FastAPI app entrypoint
│           ├── config.py                 # pydantic-settings
│           ├── logging.py
│           ├── telemetry.py              # OTEL setup
│           ├── api/
│           │   ├── v1/
│           │   │   ├── routes/
│           │   │   │   ├── auth.py
│           │   │   │   ├── matches.py
│           │   │   │   ├── runs.py
│           │   │   │   ├── chat.py
│           │   │   │   ├── predictions.py
│           │   │   │   └── scout.py
│           │   │   ├── deps.py
│           │   │   └── schemas/
│           │   └── errors.py
│           ├── core/
│           │   ├── security.py           # JWT, hashing
│           │   ├── auth.py
│           │   ├── permissions.py
│           │   ├── rate_limit.py
│           │   └── pagination.py
│           ├── db/
│           │   ├── base.py
│           │   ├── session.py
│           │   ├── models/
│           │   │   ├── user.py
│           │   │   ├── match.py
│           │   │   ├── run.py
│           │   │   ├── track.py
│           │   │   ├── stats.py
│           │   │   ├── prediction.py
│           │   │   ├── chat.py
│           │   │   └── audit.py
│           │   └── repositories/
│           ├── storage/
│           │   ├── object_store.py       # S3/MinIO abstraction
│           │   └── signed_urls.py
│           ├── queue/
│           │   ├── broker.py             # Dramatiq/Celery adapter
│           │   └── tasks.py
│           ├── pipeline/                 # orchestration logic
│           │   ├── states.py
│           │   ├── stages/
│           │   │   ├── probe.py
│           │   │   ├── sample.py
│           │   │   ├── detect.py
│           │   │   ├── track.py
│           │   │   ├── homography.py
│           │   │   ├── metrics.py
│           │   │   └── report.py
│           │   └── runner.py
│           ├── cv/                       # imported by worker-cv
│           │   ├── detectors/
│           │   │   ├── base.py
│           │   │   ├── yolov11.py
│           │   │   └── yolov8.py
│           │   ├── trackers/
│           │   │   ├── base.py
│           │   │   ├── deepsort.py
│           │   │   └── bytetrack.py
│           │   ├── team_assignment.py
│           │   ├── homography.py
│           │   ├── heatmaps.py
│           │   ├── metrics.py
│           │   └── evaluation/           # HOTA, MOTA, mAP
│           ├── ml/
│           │   ├── features/
│           │   │   ├── match_features.py
│           │   │   ├── workload_features.py
│           │   │   └── player_features.py
│           │   ├── models/
│           │   │   ├── outcome.py
│           │   │   ├── injury.py
│           │   │   └── similarity.py
│           │   ├── training/
│           │   │   ├── train_outcome.py
│           │   │   ├── train_injury.py
│           │   │   └── build_embeddings.py
│           │   ├── registry.py           # MLflow wrapper
│           │   └── explain.py            # SHAP utilities
│           ├── agents/
│           │   ├── graph.py              # LangGraph definition
│           │   ├── state.py              # AgentState pydantic
│           │   ├── orchestrator.py
│           │   ├── specialists/
│           │   │   ├── vision.py
│           │   │   ├── tactical.py
│           │   │   ├── stats.py
│           │   │   ├── prediction.py
│           │   │   ├── injury.py
│           │   │   ├── scout.py
│           │   │   └── report.py
│           │   ├── tools/
│           │   │   ├── registry.py
│           │   │   ├── heatmap_tool.py
│           │   │   ├── stats_tool.py
│           │   │   ├── predict_tool.py
│           │   │   ├── scout_tool.py
│           │   │   └── pdf_tool.py
│           │   ├── llm/
│           │   │   ├── base.py
│           │   │   ├── gemini.py
│           │   │   ├── openai.py
│           │   │   ├── anthropic.py
│           │   │   └── ollama.py
│           │   └── guardrails.py
│           └── workers/
│               ├── cv_worker.py
│               └── ml_worker.py
│
├── model_server/
│   ├── pyproject.toml
│   └── src/
│       └── model_server/
│           ├── main.py                   # FastAPI app
│           ├── registry_client.py        # MLflow
│           └── routes.py
│
├── frontend/
│   ├── package.json
│   ├── pnpm-lock.yaml                    # or package-lock.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── postcss.config.cjs
│   ├── eslint.config.js
│   ├── index.html
│   ├── public/
│   ├── tests/
│   │   ├── unit/
│   │   └── e2e/                          # playwright
│   └── src/
│       ├── main.tsx
│       ├── app.tsx
│       ├── router.tsx
│       ├── lib/
│       │   ├── api/                      # OpenAPI-generated client
│       │   ├── auth/
│       │   ├── utils/
│       │   └── i18n/
│       ├── components/
│       │   ├── ui/                       # shadcn/ui primitives
│       │   ├── charts/
│       │   ├── pitch/                    # konva pitch viz
│       │   └── layout/
│       ├── features/
│       │   ├── auth/
│       │   ├── matches/
│       │   ├── upload/
│       │   ├── dashboard/
│       │   ├── heatmaps/
│       │   ├── tracking/
│       │   ├── stats/
│       │   ├── predictions/
│       │   ├── scout/
│       │   └── chat/
│       ├── pages/
│       └── styles/
│
├── packages/                             # shared internal libs (optional)
│   └── ts-types/                         # generated TS types mirroring Pydantic
│
├── scripts/
│   ├── seed_demo_match.py
│   ├── download_models.sh
│   ├── eval_tracker.py
│   ├── eval_outcome_model.py
│   └── generate_openapi.py
│
├── data/                                 # gitignored — local datasets/models
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   ├── models/
│   └── samples/                          # tiny demo clips kept in repo
│
└── ops/
    ├── runbooks/
    │   ├── pipeline_stuck.md
    │   ├── llm_budget_exceeded.md
    │   └── db_restore.md
    └── playbooks/
```

---

## Conventions

- **Python packages:** `src/` layout; never `from pitchmind.backend.xyz`, always `from pitchmind.xyz`.
- **TypeScript modules:** Feature-first under `src/features/<area>`; shared UI under `src/components/ui`.
- **Tests:** mirror source structure; one test file per source file where practical.
- **Migrations:** Alembic only; generated migrations reviewed before merge.
- **Generated code:** TS API client + types are generated from the FastAPI OpenAPI spec via `scripts/generate_openapi.py` + `openapi-typescript`. Generated files committed for diff visibility.

## Ignore Rules (preview for `.gitignore`)

```
# Python
__pycache__/
.venv/
.uv/
*.egg-info/

# Node
node_modules/
.dist/
.cache/

# Editor
.vscode/
.idea/

# Data
data/
!data/samples/

# Secrets
.env
.env.*
!.env.example

# OS
.DS_Store
Thumbs.db

# Tooling
.mypy_cache/
.ruff_cache/
.pytest_cache/
.coverage
htmlcov/
```
