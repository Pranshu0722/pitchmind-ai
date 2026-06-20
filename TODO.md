# TODO — PitchMind AI

**Last Updated:** 2026-06-20

---

## 🔴 High Priority (current sprint — Phase 7: Player Tracking)

- [ ] **`Tracker` interface** — abstract base in `cv/trackers/base.py`
- [ ] **DeepSORT implementation** — `cv/trackers/deepsort.py`
- [ ] **ByteTrack implementation** — `cv/trackers/bytetrack.py` (bench vs DeepSORT via HOTA)
- [ ] **Team assignment** — k-means on HSV jersey histogram; assign "home" / "away" / "referee" labels
- [ ] **Persist tracks** — `Track` ORM model + Alembic migration; tracks stored per frame
- [ ] **Streaming video upload** — current upload reads entire file into memory (TD-3); required before large-scale CV use

---

## 🟡 Medium Priority (Phase 8 prep)

- [ ] 4-point homography + pitch coordinate transform
- [ ] Heatmap generator (per-player + per-team + per-period)
- [ ] Match metrics (possession proxy, distance, sprints, formation)
- [ ] HOTA / MOTA evaluation harness
- [ ] Confirm LLM API keys available — Gemini and/or OpenAI for Phase 12

---

## 🟢 Low Priority (post-Phase 7)

### CV Pipeline
- [ ] 4-point homography + pitch coordinate transform
- [ ] Heatmap generator (per-player + per-team + per-period)
- [ ] Match metrics (possession proxy, distance, sprints, formation)
- [ ] HOTA / MOTA evaluation harness

### ML
- [ ] Feature pipeline for outcome model (FBref / StatsBomb)
- [ ] XGBoost outcome model + MLflow run + SHAP
- [ ] LightGBM injury risk model + MLflow run + SHAP
- [ ] Player embedding pipeline (sentence-transformers or MLP)
- [ ] pgvector extension + HNSW index (requires Docker pgvector image, not standalone PG)
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

### Frontend (Phase 13)
- [ ] TanStack Router + auth guard
- [ ] TanStack Query + generated OpenAPI client setup
- [ ] Auth screens (sign in / sign up / forgot)
- [ ] App shell with sidebar + header
- [ ] Match list + status badges
- [ ] Upload UX with chunked progress
- [ ] Match detail tabs (Overview, Tracking, Heatmaps, Stats, Tactics, Chat, Report)
- [ ] Pitch SVG with heatmap overlay (react-konva)
- [ ] Agent chat with streaming + citation panel
- [ ] PDF report download + shareable link
- [ ] i18n bootstrapped (English)

### Testing
- [ ] Unit coverage ≥ 80% on backend critical paths
- [ ] Contract tests (schemathesis vs OpenAPI)
- [ ] E2E tests (Playwright): full happy path
- [ ] Load tests (k6) on hot paths
- [ ] ZAP baseline security scan
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

### Planning (Phase 0)
- [x] PRD.md, SRS.md, ARCHITECTURE.md, TECH_REVIEW.md
- [x] FOLDER_STRUCTURE.md, ROADMAP.md, GIT_STRATEGY.md
- [x] FEATURES.md, EVALUATION.md, PROJECT_PROGRESS.md, TODO.md, CHANGELOG.md, README.md
- [x] ADR-0001 Dramatiq + Redis
- [x] ADR-0002 Multi-provider LLM adapter
- [x] ADR-0003 Tracker interface (DeepSORT vs ByteTrack)
- [x] ADR-0004 pgvector
- [x] ADR-0005 Caddy prod / Nginx dev
- [x] ADR-0006 uv

### Phase 1 — Project Setup
- [x] Monorepo skeleton per FOLDER_STRUCTURE.md
- [x] docker-compose.yml (PostgreSQL 17, Redis 7, MinIO)
- [x] pyproject.toml + uv.lock (full dependency set)
- [x] ruff lint + format, mypy type checking
- [x] Pre-commit hooks
- [x] GitHub Actions CI (Python 3.11 + 3.12, PostgreSQL + Redis + MinIO)
- [x] Frontend scaffold: Vite + React + TypeScript + Tailwind + shadcn/ui
- [x] ADR stubs docs/adr/0000-0006

### Phase 2 — Backend Foundation
- [x] FastAPI app factory + pydantic-settings config
- [x] Auth: register / login / refresh / me (argon2id + JWT)
- [x] JWT + roles (USER / ADMIN) + require_role dependency
- [x] Structured logging (structlog) + TraceID middleware
- [x] Global exception handlers
- [x] AuditLog model — every auth event persisted
- [x] SQLAlchemy 2.x async models + Alembic (migration 0001)
- [x] 6 unit tests + 14 integration tests

### Phase 4 — Database Design & Domain Models
- [x] Team, Player, Match, MatchEvent ORM models
- [x] PlayerPosition, MatchStatus, EventType enums
- [x] Alembic migration 0002 (4 tables + 3 enums)
- [x] CRUD API routes: /teams, /players, /matches, /matches/{id}/events
- [x] 15 integration tests

### Phase 5 — Video Upload Pipeline
- [x] Async MinIO/S3 client (aioboto3)
- [x] VideoUpload ORM model + UploadStatus enum
- [x] Alembic migration 0003
- [x] Video upload / list / get / presigned download / delete API
- [x] File validation (2 GB limit, MIME allowlist)
- [x] Admin-only delete (RBAC)
- [x] 10 integration tests
- [x] Docker MinIO service in compose + CI

### CI Hardening
- [x] pip-audit + npm-audit in CI
- [x] Fixed llvmlite build failure (uv sync --dev, no --all-extras)
- [x] Fixed pip-audit editable-install traversal (strip -e lines before audit)
- [x] Fixed ESLint react-refresh warning (App.tsx split)
- [x] Fixed pydantic-settings GHSA-4xgf-cpjx-pc3j vuln (bumped to ≥2.14.2)
- [x] Fixed vitest critical esbuild vuln chain (vitest 2 → 3.2.6)
- [x] Fixed frontend unit test CI step (passWithNoTests: true)
- [x] Fixed test_readyz 503 in unit tests (mock app.state.redis in unit conftest)
- [x] Fixed rate-limit test concurrent SQLAlchemy session error (sequential loop)
- [x] Fixed test_upload_video_success assertion (READY → PENDING)

### Tech Debt Resolved
- [x] TD-4 Rate limiting — slowapi + Redis on auth + upload endpoints
- [x] TD-5 Dramatiq worker wiring — process_video actor enqueued on upload

### Phase 6 — Computer Vision Engine
- [x] `pyarrow>=18.0.0` added to cv extras
- [x] Sync S3 client (`storage/sync_client.py`) — `download_file_sync` / `upload_file_sync` for Dramatiq workers
- [x] `Detection` dataclass + `Detector` Protocol (`cv/detectors/base.py`)
- [x] `YoloV11Detector` (`cv/detectors/yolov11.py`) — lazy ultralytics import, CPU/GPU via `cv_device` setting
- [x] `probe` stage — OpenCV metadata extraction (fps, duration, resolution)
- [x] `sample_frames` stage — configurable fps sampling, yields (idx, timestamp, frame)
- [x] `detect` stage — batched inference → `pd.DataFrame`; partial-batch flush; empty guard
- [x] `run_pipeline` runner — download → probe → sample → detect → `detections.parquet` → S3 → update DB
- [x] `process_video` actor wired to `run_pipeline` (lazy import — cv extras only in worker)
- [x] `worker-cv.Dockerfile` fixed (`--extra cv` sync; correct dramatiq CMD)
- [x] 8 unit tests — all cv2/pandas/ultralytics mocked; run without cv extras
