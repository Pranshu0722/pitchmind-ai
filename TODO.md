# TODO — PitchMind AI

**Last Updated:** 2026-06-15

---

## 🔴 High Priority (blocking Phase 1)

- [x] **User approves planning documents** ✅ 2026-06-15
- [x] **Confirm git identity** — Pranshu0722 / pranshu.0422@gmail.com ✅ 2026-06-15
- [x] **Resolve ADR-0001** — Dramatiq + Redis ✅ 2026-06-15
- [x] **Resolve ADR-0002** — Multi-provider adapter (Gemini Flash routing / Claude or GPT-4o synthesis / Ollama fallback) ✅ 2026-06-15
- [x] **Resolve ADR-0003** — `Tracker` interface; bench DeepSORT vs ByteTrack ✅ 2026-06-15
- [x] **Resolve ADR-0004** — pgvector ✅ 2026-06-15
- [x] **Resolve ADR-0005** — Caddy prod / Nginx dev ✅ 2026-06-15
- [x] **Resolve ADR-0006** — uv ✅ 2026-06-15
- [ ] **Choose licence** — MIT / Apache 2.0 / commercial (decide before public repo)
- [ ] **Confirm LLM API keys available** — Gemini and/or OpenAI account ready for Phase 12

---

## 🟡 Medium Priority (Phase 1 deliverables)

- [ ] Create monorepo skeleton per `FOLDER_STRUCTURE.md`
- [ ] Write `docker-compose.yml` (postgres, redis, minio, mlflow, api stub, worker stub, web stub)
- [ ] Write `Makefile` (dev, lint, format, typecheck, test, migrate, seed targets)
- [ ] Configure pre-commit hooks (ruff, black, mypy, eslint, prettier, tsc, commit-msg linter)
- [ ] Set up GitHub Actions CI (lint → typecheck → unit tests)
- [ ] Write ADR template (`docs/adr/0000-template.md`)
- [ ] Write ADR stubs 0001 – 0006 (one per open decision)
- [ ] Add `LICENSE`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`
- [ ] Add `.gitignore`, `.editorconfig`, `.env.example`
- [ ] Pin CUDA base image version for `worker-cv.Dockerfile`

---

## 🟢 Low Priority (post-Phase 1)

### Backend
- [ ] FastAPI app factory + pydantic-settings config
- [ ] Auth: register / login / refresh / logout + argon2id
- [ ] JWT + roles + rate limiting
- [ ] Structured logging + OTEL setup
- [ ] Prometheus `/metrics` endpoint
- [ ] SQLAlchemy 2.x models + Alembic migration pipeline
- [ ] pgvector extension + HNSW index

### Frontend
- [ ] Vite + TS strict + Tailwind + shadcn/ui scaffold
- [ ] TanStack Router + auth guard
- [ ] TanStack Query + generated OpenAPI client setup
- [ ] Auth screens (sign in / sign up / forgot)
- [ ] App shell with sidebar + header
- [ ] i18n bootstrapped (English)

### CV Pipeline
- [ ] `ffprobe` metadata stage
- [ ] Frame sampler (configurable fps)
- [ ] YOLOv11 detection wrapper + batch inference
- [ ] `Tracker` interface + DeepSORT + ByteTrack
- [ ] Team assignment (k-means on HSV jersey histogram)
- [ ] 4-point homography + pitch coordinate transform
- [ ] Heatmap generator (per-player + per-team + per-period)
- [ ] Match metrics (possession proxy, distance, sprints, formation)
- [ ] HOTA / MOTA evaluation harness

### ML
- [ ] Feature pipeline for outcome model (FBref / StatsBomb)
- [ ] XGBoost outcome model + MLflow run + SHAP
- [ ] LightGBM injury risk model + MLflow run + SHAP
- [ ] Player embedding pipeline (sentence-transformers or MLP)
- [ ] pgvector player similarity search
- [ ] Model server (FastAPI) serving registered MLflow models
- [ ] Model cards for all three models

### Agents
- [ ] `AgentState` pydantic model
- [ ] LangGraph graph definition
- [ ] Orchestrator node + intent routing
- [ ] Vision, Tactical, Stats, Prediction, Injury, Scout, Report agent nodes
- [ ] Typed tool registry
- [ ] LLM provider adapter (Gemini, OpenAI, Claude, Ollama)
- [ ] Token / cost budget guardrails
- [ ] Persistent chat sessions
- [ ] SSE streaming endpoint
- [ ] Adversarial prompt-injection test suite

### Dashboard
- [ ] Match list + status badges
- [ ] Upload UX with chunked progress
- [ ] Match detail tabs (Overview, Tracking, Heatmaps, Stats, Tactics, Chat, Report)
- [ ] Pitch SVG with heatmap overlay (react-konva)
- [ ] Agent chat with streaming + citation panel
- [ ] PDF report download + shareable link

### Testing
- [ ] Unit coverage ≥ 80% on backend critical paths
- [ ] Contract tests (schemathesis vs OpenAPI)
- [ ] Integration tests (testcontainers: Postgres, Redis, MinIO)
- [ ] E2E tests (Playwright): full happy path
- [ ] Load tests (k6) on hot paths
- [ ] ZAP baseline security scan
- [ ] pip-audit + npm-audit in CI
- [ ] axe-core a11y audit on key screens
- [ ] Requirements traceability matrix

### Deployment
- [ ] Caddy config with Let's Encrypt
- [ ] Production docker-compose / Helm chart
- [ ] Managed Postgres (PITR) + managed Redis setup
- [ ] Prometheus + Grafana dashboards (API, Pipeline, Agent Cost, Model Serving)
- [ ] Sentry configured for FE + BE
- [ ] Backup + restore tested
- [ ] Runbooks written
- [ ] Public README screenshots + demo video

---

## 📋 Backlog (future phases / post-MVP features)

See `FEATURES.md` for the full innovation backlog:

- [ ] Pitch control surface (F1)
- [ ] Expected threat (xT) grid (F2)
- [ ] Pass network reconstruction (F3)
- [ ] Set-piece detector & library (F4)
- [ ] Auto highlights reel (F5)
- [ ] xG model (M1)
- [ ] Automatic camera calibration (C1)
- [ ] Jersey-number OCR (C2)
- [ ] Pose estimation (C3)
- [ ] Event spotting (C4)
- [ ] Real-time live mode (F9)
- [ ] Long-term match memory via RAG (A2)
- [ ] Public benchmark page (R4)
- [ ] Demo video + write-up (R5)

---

## ✅ Done

- [x] PRD.md
- [x] SRS.md
- [x] ARCHITECTURE.md
- [x] TECH_REVIEW.md
- [x] FOLDER_STRUCTURE.md
- [x] ROADMAP.md
- [x] GIT_STRATEGY.md
- [x] FEATURES.md
- [x] EVALUATION.md
- [x] PROJECT_PROGRESS.md
- [x] TODO.md
- [x] CHANGELOG.md
- [x] README.md
