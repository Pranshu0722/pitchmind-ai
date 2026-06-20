# Folder Structure — PitchMind AI

**Version:** 0.2 (Active)
**Status:** Partially implemented — Phases 1–5 + tech debt complete. Legend: ✅ exists · 📋 planned

A pragmatic monorepo: one repo, multiple deployables, shared tooling. No micro-package overhead, but cleanly separated concerns.

```
PitchMind-AI/
├── README.md                             ✅
├── PRD.md                                ✅
├── SRS.md                                ✅
├── ARCHITECTURE.md                       ✅
├── TECH_REVIEW.md                        ✅
├── ROADMAP.md                            ✅
├── FOLDER_STRUCTURE.md                   ✅
├── GIT_STRATEGY.md                       ✅
├── FEATURES.md                           ✅
├── EVALUATION.md                         ✅
├── PROJECT_PROGRESS.md                   ✅
├── TODO.md                               ✅
├── CHANGELOG.md                          ✅
├── LICENSE                               📋
├── .gitignore                            ✅
├── .gitattributes                        ✅
├── .editorconfig                         ✅
├── .env.example                          ✅
├── docker-compose.yml                    ✅  (PostgreSQL 17, Redis 7, MinIO)
├── docker-compose.override.yml           📋 local overrides (gitignored)
├── Makefile                              📋 tasks: dev, test, lint, format, migrate, seed
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                        ✅  (backend Python 3.11/3.12 + frontend Node 20 + security)
│   │   ├── docker.yml                    📋
│   │   └── release.yml                   📋
│   ├── ISSUE_TEMPLATE/                   📋
│   └── PULL_REQUEST_TEMPLATE.md          ✅
├── docs/
│   ├── adr/                              ✅
│   │   ├── 0000-template.md              ✅
│   │   ├── 0001-task-queue.md            ✅  (Dramatiq + Redis — resolved)
│   │   ├── 0002-llm-provider.md          ✅  (multi-provider adapter — resolved)
│   │   ├── 0003-tracker.md               ✅  (Tracker interface — resolved)
│   │   ├── 0004-vector-store.md          ✅  (pgvector — resolved)
│   │   ├── 0005-reverse-proxy.md         ✅  (Caddy prod / Nginx dev — resolved)
│   │   └── 0006-python-env.md            ✅  (uv — resolved)
│   ├── api/                              📋 exported OpenAPI, Postman collection
│   ├── diagrams/                         📋 mermaid, draw.io, png
│   └── models/                           📋 model cards (outcome, injury, scout)
│
├── infra/
│   ├── docker/
│   │   ├── api.Dockerfile                📋
│   │   ├── worker-cv.Dockerfile          📋
│   │   ├── worker-ml.Dockerfile          📋
│   │   ├── agent.Dockerfile              📋
│   │   ├── model-server.Dockerfile       📋
│   │   └── web.Dockerfile                📋
│   ├── nginx/                            📋
│   ├── caddy/                            📋
│   ├── grafana/                          📋
│   ├── prometheus/                       📋
│   └── k8s/                              📋 helm charts (post-MVP)
│
├── backend/
│   ├── pyproject.toml                    ✅
│   ├── uv.lock                           ✅
│   ├── alembic.ini                       ✅
│   ├── alembic/
│   │   ├── env.py                        ✅
│   │   └── versions/
│   │       ├── 0001_initial_users_audit.py  ✅
│   │       ├── 0002_domain_models.py        ✅
│   │       ├── 0003_video_uploads.py        ✅
│   │       └── 0004_...                     📋 (pgvector, Phase 8)
│   ├── worker.py                         ✅  Dramatiq entry point (uv run dramatiq pitchmind.queue.tasks)
│   ├── tests/
│   │   ├── conftest.py                   ✅
│   │   ├── unit/
│   │   │   ├── conftest.py               ✅  AsyncMock redis for ASGITransport tests
│   │   │   ├── test_security.py          ✅  (6 tests)
│   │   │   └── test_health.py            ✅  (2 tests)
│   │   └── integration/
│   │       ├── conftest.py               ✅
│   │       ├── test_auth.py              ✅  (14 tests)
│   │       ├── test_domain.py            ✅  (15 tests)
│   │       ├── test_video_uploads.py     ✅  (10 tests)
│   │       └── test_rate_limit.py        ✅  (2 tests — 429 on /login after burst)
│   └── src/
│       └── pitchmind/
│           ├── __init__.py               ✅
│           ├── main.py                   ✅  FastAPI app + middleware + routers
│           ├── config.py                 ✅  pydantic-settings (all env vars)
│           ├── logging.py                ✅  structlog config
│           ├── middleware.py             ✅  TraceID middleware
│           ├── telemetry.py              📋 OTEL setup (Phase 2 follow-up)
│           ├── api/
│           │   ├── errors.py             ✅  global exception handlers
│           │   ├── limiter.py            ✅  slowapi Limiter (Redis-backed, swallow_errors=True)
│           │   └── v1/
│           │       ├── __init__.py       ✅  router registration
│           │       ├── routes/
│           │       │   ├── auth.py       ✅  /register /login /refresh /me
│           │       │   ├── teams.py      ✅  GET/POST /teams/
│           │       │   ├── players.py    ✅  GET/POST /players/
│           │       │   ├── matches.py    ✅  GET/POST/PATCH /matches/ + events
│           │       │   ├── video_uploads.py ✅ GET/POST /videos/ + download/delete
│           │       │   ├── runs.py       📋 (Phase 6)
│           │       │   ├── chat.py       📋 (Phase 12)
│           │       │   ├── predictions.py 📋 (Phase 9)
│           │       │   └── scout.py      📋 (Phase 11)
│           │       └── schemas/
│           │           ├── auth.py       ✅
│           │           ├── team.py       ✅
│           │           ├── player.py     ✅
│           │           ├── match.py      ✅
│           │           ├── match_event.py ✅
│           │           └── video_upload.py ✅
│           ├── core/
│           │   ├── security.py           ✅  argon2id hashing + JWT tokens
│           │   ├── deps.py               ✅  get_current_user, require_role
│           │   └── pagination.py         📋
│           ├── db/
│           │   ├── base.py               ✅  Base + TimestampMixin
│           │   ├── session.py            ✅  async engine + get_db
│           │   ├── models/
│           │   │   ├── __init__.py       ✅
│           │   │   ├── user.py           ✅  User + UserRole
│           │   │   ├── audit.py          ✅  AuditLog
│           │   │   ├── team.py           ✅  Team
│           │   │   ├── player.py         ✅  Player + PlayerPosition
│           │   │   ├── match.py          ✅  Match + MatchStatus
│           │   │   ├── match_event.py    ✅  MatchEvent + EventType
│           │   │   ├── video_upload.py   ✅  VideoUpload + UploadStatus
│           │   │   ├── run.py            📋 (Phase 6)
│           │   │   ├── track.py          📋 (Phase 7)
│           │   │   ├── stats.py          📋 (Phase 8)
│           │   │   ├── prediction.py     📋 (Phase 9)
│           │   │   └── chat.py           📋 (Phase 12)
│           │   └── repositories/         📋
│           ├── storage/
│           │   ├── __init__.py           ✅
│           │   └── client.py             ✅  async S3/MinIO: upload, presign, delete
│           ├── queue/
│           │   ├── __init__.py           ✅  package marker
│           │   ├── broker.py             ✅  RedisBroker + Retries middleware
│           │   └── tasks.py              ✅  process_video actor (PENDING→PROCESSING→READY/FAILED)
│           ├── pipeline/                 📋 (Phase 6)
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
│           ├── cv/                       📋 (Phase 6-7)
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
│           │   └── evaluation/
│           ├── ml/                       📋 (Phase 9-11)
│           │   ├── features/
│           │   ├── models/
│           │   ├── training/
│           │   ├── registry.py
│           │   └── explain.py
│           ├── agents/                   📋 (Phase 12)
│           │   ├── graph.py
│           │   ├── state.py
│           │   ├── orchestrator.py
│           │   ├── specialists/
│           │   ├── tools/
│           │   ├── llm/
│           │   └── guardrails.py
│           └── workers/                  📋 (Phase 6)
│               ├── cv_worker.py
│               └── ml_worker.py
│
├── model_server/                         📋 (Phase 9)
│
├── frontend/
│   ├── package.json                      ✅
│   ├── package-lock.json                 ✅
│   ├── vite.config.ts                    ✅
│   ├── tsconfig.json                     ✅
│   ├── tailwind.config.ts                ✅
│   ├── postcss.config.cjs                ✅
│   ├── eslint.config.js                  ✅
│   ├── index.html                        ✅
│   ├── public/                           ✅
│   └── src/
│       ├── main.tsx                      ✅  React root — imports App
│       ├── App.tsx                       ✅  placeholder shell
│       ├── styles/
│       │   └── globals.css               ✅  Tailwind base styles
│       ├── router.tsx                    📋 TanStack Router (Phase 13)
│       ├── lib/
│       │   ├── api/                      📋 OpenAPI-generated client
│       │   ├── auth/                     📋
│       │   ├── utils/                    📋
│       │   └── i18n/                     📋
│       ├── components/
│       │   ├── ui/                       📋 shadcn/ui primitives (Phase 13)
│       │   ├── charts/                   📋
│       │   ├── pitch/                    📋 konva pitch viz
│       │   └── layout/                   📋
│       ├── features/                     📋 all feature modules (Phase 13)
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
│       └── pages/                        📋
│
├── packages/                             📋 shared internal libs (optional)
│
├── scripts/                              📋
│   ├── seed_demo_match.py
│   ├── download_models.sh
│   ├── eval_tracker.py
│   ├── eval_outcome_model.py
│   └── generate_openapi.py
│
├── data/                                 📋 gitignored — local datasets/models
│
└── ops/
    ├── runbooks/                         📋
    └── playbooks/                        📋
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
