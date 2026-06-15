# Software Requirements Specification — PitchMind AI

**Version:** 0.1 (Planning)
**Standard:** IEEE 830-inspired (lightweight)
**Status:** Draft — awaiting approval

---

## 1. Introduction

### 1.1 Purpose

This SRS defines the functional (FR) and non-functional (NFR) requirements for PitchMind AI. It is the contract between product intent (PRD) and system design (ARCHITECTURE.md). Every requirement must be testable.

### 1.2 Scope

The system covers video ingest, computer-vision analysis, machine-learning prediction, agentic reasoning, dashboards, and reporting. It is **not** in scope to handle live broadcast overlay, refereeing decisions, or betting flows in v1.

### 1.3 Definitions

| Term | Meaning |
| --- | --- |
| **Match** | A unique uploaded video and its derived data |
| **Track** | A persistent identity assigned to a detected player across frames |
| **Heatmap** | 2D spatial density of a track's positions over time |
| **Agent** | A LangGraph node with a defined role, prompt, and tool surface |
| **Run** | One complete pipeline execution against one match |
| **Artifact** | Any persisted output (heatmap PNG, JSON stats, PDF report, model file) |

---

## 2. Overall Description

### 2.1 Product Perspective

PitchMind AI is a self-contained web application with an asynchronous processing pipeline. It is deployed as containerised services (Docker Compose for dev, Kubernetes-ready for prod). Users interact via a browser-based React SPA.

### 2.2 User Classes

| Class | Frequency | Privileges |
| --- | --- | --- |
| End user (coach / analyst / scout) | Daily | Upload, view, query, export own matches |
| Admin | Occasional | All of the above + model registry, job control, user management |
| System (worker) | Continuous | Read/write artifacts, update job state |

### 2.3 Operating Environment

- **Client:** Modern evergreen browsers (Chrome / Firefox / Safari ≥ 2 major versions behind current).
- **Server:** Linux x86_64; Python 3.11+; PostgreSQL 16; Redis 7; NVIDIA GPU (CUDA 12+) for the CV worker; CPU-only fallback supported with degraded throughput.
- **Storage:** S3-compatible object store (MinIO in dev, AWS S3 / Cloudflare R2 in prod).

### 2.4 Design & Implementation Constraints

- Backend language: Python 3.11+.
- Frontend language: TypeScript (strict mode).
- All public APIs versioned (`/api/v1/...`).
- All long-running work executes off the request thread.
- All external secrets via environment variables; no secrets in repo.

---

## 3. Functional Requirements

> Format: **FR-AREA-N: title** — description — *acceptance test*.

### 3.1 Authentication & Account

- **FR-AUTH-1: Email/password sign-up** — A user can register with email + password (≥ 10 chars, with strength check). *AC: `POST /auth/register` returns 201 + JWT; duplicate emails return 409.*
- **FR-AUTH-2: OAuth login** — Google OAuth as an optional alternative. *AC: A Google account creates / merges to existing user by email.*
- **FR-AUTH-3: Session** — JWT access token (15 min) + refresh token (7 d), HttpOnly cookie for refresh. *AC: expired access token triggers silent refresh.*
- **FR-AUTH-4: Logout** — Refresh token revoked server-side. *AC: subsequent refresh attempts return 401.*
- **FR-AUTH-5: Roles** — `user`, `admin`. *AC: admin-only endpoints return 403 for `user`.*

### 3.2 Video Ingest

- **FR-VID-1: Upload** — Chunked (TUS-style or S3 multipart) up to 4 GB. *AC: an interrupted 2 GB upload can be resumed.*
- **FR-VID-2: Validation** — Accept `mp4`, `mov`, `mkv`. Reject other types. *AC: `.txt` upload returns 415.*
- **FR-VID-3: Metadata extraction** — duration, fps, resolution, codec via `ffprobe`. *AC: a 90-min 25fps 1080p file lists those values in `/matches/{id}`.*
- **FR-VID-4: Thumbnail** — Generate 3 thumbnails (start, middle, end). *AC: present in dashboard within 10 s of upload completion.*
- **FR-VID-5: Virus scan** — ClamAV scan before processing. *AC: an EICAR test file is rejected and quarantined.*
- **FR-VID-6: Quotas** — Per-user quota (default 10 matches / month, configurable). *AC: 11th match returns 402.*

### 3.3 Pipeline Orchestration

- **FR-PIPE-1: Job creation** — On successful upload, a `Run` row is created with `status=queued`. *AC: visible in admin job list within 1 s.*
- **FR-PIPE-2: Stages** — Run executes ordered stages: `probe`, `sample`, `detect`, `track`, `homography`, `metrics`, `report`. *AC: each stage transition is logged with timing.*
- **FR-PIPE-3: Retry policy** — Transient failures retry ≤ 3 times with exponential backoff. *AC: a forced 1-failure on `detect` succeeds on retry.*
- **FR-PIPE-4: Cancel** — A user can cancel their own pending or running job. *AC: status moves to `cancelled` and worker stops within 5 s.*
- **FR-PIPE-5: Idempotency** — Re-running a completed match with same params reuses cached artifacts. *AC: second run completes ≥ 10× faster.*

### 3.4 Computer Vision

- **FR-CV-1: Player detection** — YOLOv11 detects players with class `person` (or fine-tuned `player`) at ≥ 0.5 mAP@0.5 on a held-out validation set. *AC: evaluated nightly on fixture set.*
- **FR-CV-2: Ball detection** — Detect ball; tolerate false-negatives. *AC: ball recall ≥ 0.6 on validation clips.*
- **FR-CV-3: Tracking** — DeepSORT (primary) or ByteTrack (alt) assigns persistent IDs. *AC: ID switch rate ≤ 25% per minute on validation clips (improvable target).*
- **FR-CV-4: Team assignment** — Cluster track jerseys into 2 teams + referee + goalkeepers via colour histogram + k-means. *AC: ≥ 90% correct team labels on validation matches.*
- **FR-CV-5: Homography** — Map image coordinates to a 105 × 68 m pitch plane. *AC: 4-point calibration produces sub-2 m mean error on tagged corner kicks.*
- **FR-CV-6: Frame sampling** — Configurable rate (default 5 fps for detection, 25 fps for tracking interpolation). *AC: documented in run config and reproducible.*

### 3.5 Analytics

- **FR-ANA-1: Heatmap** — Per-player, per-team, per-period heatmaps as 2D arrays + PNG renders. *AC: JSON + PNG in artifacts.*
- **FR-ANA-2: Possession proxy** — % of frames where ball is within X m of a team's nearest track. *AC: numeric value 0 – 100, sums team A + B + uncontested = 100.*
- **FR-ANA-3: Distance covered** — Per-track total + per-period in metres. *AC: total monotonically increases over time.*
- **FR-ANA-4: Sprint count** — Threshold-based (e.g., > 7 m/s sustained ≥ 1 s). *AC: thresholds documented and configurable.*
- **FR-ANA-5: Formation guess** — Cluster off-the-ball positions and label (e.g., 4-3-3) with confidence. *AC: produces a top-1 label + posterior.*

### 3.6 Machine Learning

- **FR-ML-1: Match outcome model** — XGBoost classifier producing (home win, draw, away win) probabilities. *AC: log-loss ≤ baseline (bookmaker market) − 0.05 on holdout.*
- **FR-ML-2: SHAP explanations** — Top-5 feature contributions returned per prediction. *AC: returned alongside probabilities.*
- **FR-ML-3: Injury-risk model** — LightGBM regressor producing 0 – 1 risk score per player per match. *AC: model card published in `/docs/models/injury.md` with cohort, features, limitations.*
- **FR-ML-4: Scout recommender** — Given a query player vector + filters (position, age, budget proxy), return top-K nearest. *AC: similarity distances returned and explainable.*
- **FR-ML-5: Model registry** — All models registered in MLflow with version, dataset hash, metrics. *AC: every served model traceable to an MLflow run ID.*

### 3.7 Agentic Layer (LangGraph)

- **FR-AGT-1: Orchestrator** — Routes user queries to specialist agents based on intent classification. *AC: a tactical question is routed to the Tactical agent ≥ 90% of the time on a labelled test set.*
- **FR-AGT-2: Vision agent** — Reads CV artifacts and answers spatial questions ("where did Player 9 spend most of the second half?"). *AC: cites a heatmap artifact.*
- **FR-AGT-3: Tactical agent** — Synthesises formation, possession, and pressing metrics into a narrative. *AC: output references at least 3 grounded numbers.*
- **FR-AGT-4: Stats agent** — Returns precise numeric answers from the analytics store. *AC: each numeric claim has a source row reference.*
- **FR-AGT-5: Prediction agent** — Invokes the ML outcome model and returns probabilities + SHAP. *AC: response includes probabilities and top-3 features.*
- **FR-AGT-6: Injury agent** — Invokes injury model per requested player. *AC: response includes risk score + uncertainty band.*
- **FR-AGT-7: Scout agent** — Queries player-similarity index. *AC: top-K results with similarity ≥ threshold.*
- **FR-AGT-8: Report agent** — Composes a multi-section PDF report from other agents' outputs. *AC: produces a > 3-page report with cover, summary, sections, footnotes.*
- **FR-AGT-9: Tool surface** — Agents access tools (Postgres, vector store, model server, file store) via a typed tool registry. *AC: no agent has unscoped DB access.*
- **FR-AGT-10: Token / cost guardrails** — Per-run LLM token budget enforced; exceedance aborts cleanly with an explanation. *AC: synthetic abuse test triggers the guard.*

### 3.8 Dashboard (Frontend)

- **FR-UI-1: Match list** — Paginated list of user's matches with status badges. *AC: 100 matches paginate at 20 / page in < 500 ms.*
- **FR-UI-2: Match detail** — Tabs: Overview, Tracking, Heatmaps, Stats, Tactics, Chat, Report. *AC: all tabs render with seed data.*
- **FR-UI-3: Agent chat** — Streaming responses with citations. *AC: first token ≤ 3 s; citations clickable to artifact.*
- **FR-UI-4: Report download** — One-click PDF + shareable read-only link. *AC: shared link viewable in private window without auth, revocable by owner.*
- **FR-UI-5: Accessibility** — WCAG 2.1 AA basics (keyboard nav, contrast, alt text). *AC: axe-core lint < 5 violations on key screens.*

### 3.9 Admin & Observability

- **FR-ADM-1: Job board** — Admin sees all runs with filter by status. *AC: present.*
- **FR-ADM-2: Force retry** — Admin can re-queue a failed run. *AC: status returns to `queued`.*
- **FR-ADM-3: Audit log** — Auth, upload, and admin actions logged immutably. *AC: log entry exists for every privileged action in tests.*
- **FR-ADM-4: Health & metrics** — `/healthz`, `/readyz`, `/metrics` (Prometheus). *AC: scrape returns standard metrics + custom job counters.*

---

## 4. Non-Functional Requirements

### 4.1 Performance

- **NFR-PERF-1:** 90-min 1080p match → full analytics pack in **≤ 30 min** on RTX 3060 (12 GB) class GPU.
- **NFR-PERF-2:** API p95 response ≤ 300 ms for non-pipeline endpoints (excluding LLM streaming).
- **NFR-PERF-3:** Agent first-token latency ≤ 3 s; full response ≤ 15 s for typical questions.
- **NFR-PERF-4:** Frontend Largest Contentful Paint ≤ 2 s on broadband.

### 4.2 Scalability

- **NFR-SCAL-1:** Horizontal worker scaling — N CV workers behind a single queue.
- **NFR-SCAL-2:** Database designed to handle 100 k matches / 10 M tracks without query > 1 s for indexed lookups.
- **NFR-SCAL-3:** Stateless API tier; sticky sessions not required.

### 4.3 Reliability & Availability

- **NFR-REL-1:** Job-completion success rate ≥ 99.0% (excluding malformed input).
- **NFR-REL-2:** Pipeline crash on stage N preserves outputs of stages 1 .. N-1.
- **NFR-REL-3:** Target 99% monthly availability for the API (single-region acceptable for v1).

### 4.4 Security

- **NFR-SEC-1:** Passwords hashed with argon2id, parameters per OWASP cheat sheet.
- **NFR-SEC-2:** JWT signing key in env, rotated quarterly.
- **NFR-SEC-3:** All endpoints behind HTTPS; HSTS in prod.
- **NFR-SEC-4:** Object-storage URLs are time-limited signed URLs (15 min default).
- **NFR-SEC-5:** OWASP Top-10 covered in code review checklist; injection-safe ORM-only DB access.
- **NFR-SEC-6:** Rate limiting (default 60 req/min/user; 10 uploads/hour/user).
- **NFR-SEC-7:** Dependency scanning in CI (pip-audit, npm-audit).
- **NFR-SEC-8:** No PII in logs; structured logs scrubbed.

### 4.5 Privacy & Compliance

- **NFR-PRIV-1:** Faces are not used as a biometric identifier; tracking is positional.
- **NFR-PRIV-2:** Users can delete a match and all derived artifacts within 24 h.
- **NFR-PRIV-3:** Data-processing terms documented; GDPR-ready data export.

### 4.6 Observability

- **NFR-OBS-1:** Structured JSON logs with `trace_id`, `run_id`, `user_id` (hashed).
- **NFR-OBS-2:** Prometheus metrics for HTTP, queue depth, stage timings, GPU utilisation.
- **NFR-OBS-3:** Grafana dashboards for: API, Pipeline, ML serving, Agent costs.
- **NFR-OBS-4:** Sentry (or equivalent) for FE + BE error capture.

### 4.7 Maintainability

- **NFR-MAINT-1:** All public functions typed (`mypy --strict` on `backend/`, TS strict on `frontend/`).
- **NFR-MAINT-2:** Backend test coverage ≥ 80% on critical paths.
- **NFR-MAINT-3:** Architectural Decision Records (ADR) for every cross-cutting choice.
- **NFR-MAINT-4:** Pre-commit hooks: ruff + black + isort + mypy (BE), eslint + prettier + tsc (FE).

### 4.8 Portability

- **NFR-PORT-1:** Local-first: `docker compose up` brings the whole stack (API, worker, DB, Redis, MinIO, MLflow).
- **NFR-PORT-2:** No cloud-specific APIs in core code; storage and queue swappable via interface.

### 4.9 Cost

- **NFR-COST-1:** LLM spend per match capped (default $0.50; configurable). Soft-budget alerts at 80%.
- **NFR-COST-2:** Cold-storage tier for artifacts older than 30 days.

### 4.10 Usability

- **NFR-USE-1:** First-time user can upload and view a result without documentation.
- **NFR-USE-2:** All long-running operations show progress with ETA.
- **NFR-USE-3:** Error messages are actionable, not stack traces.

### 4.11 Reproducibility

- **NFR-REPR-1:** Run config (model versions, thresholds, seeds) stored with every Run.
- **NFR-REPR-2:** Re-running with identical config + input yields metrics within ±2%.

### 4.12 Internationalisation

- **NFR-I18N-1:** UI strings externalised (i18next). English ships in v1; Spanish + Portuguese planned.

---

## 5. Assumptions

- Public open datasets are sufficient to bootstrap CV and ML models.
- A single GPU node is available for development.
- LLM provider API is available in deployment regions.

## 6. Dependencies

- **External services:** LLM provider (Gemini / OpenAI), optional OAuth (Google), object storage.
- **Datasets:** SoccerNet, StatsBomb Open Data, FBref (for prediction features), open injury datasets where licensed.
- **Models:** Ultralytics YOLOv11 weights, DeepSORT base, sentence-transformers (for similarity).

## 7. Verification

Every FR and NFR maps to at least one automated test, contract test, performance test, or manual checklist item, tracked in `tests/REQUIREMENTS_MATRIX.md` (created in Phase 14).
