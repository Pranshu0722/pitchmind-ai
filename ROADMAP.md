# Development Roadmap — PitchMind AI

**Version:** 0.2 (Active Development)
**Status:** In Progress — Phases 0, 1, 2, 4, 5 complete; Phase 3 partial

15 phases. MVP = Phases 1 – 8 + 12 + 13 (delivers the "video in → tactical insight + chat" loop). Phases 9 – 11 are post-MVP capability expansion. Phases 14 – 15 close out testing and deployment.

For each phase: **Objectives · Deliverables · Dependencies · Acceptance Criteria · Risks · Testing Strategy.**

---

## Phase 0 — Planning ✅ Complete

- **Objectives:** Approved PRD, SRS, architecture, tech review, roadmap, evaluation, features backlog.
- **Deliverables:** Every doc in this repository.
- **Acceptance:** User explicitly approves the planning bundle and the git identity is recorded.
**Status:** ✅ Complete — 2026-06-15

---

## Phase 1 — Project Setup ✅ Complete

**Objectives**
- Reproducible local dev environment.
- Repo hygiene (lint / format / typecheck / tests / CI).
- ADR practice in place.

**Deliverables**
- Monorepo skeleton per `FOLDER_STRUCTURE.md`.
- `docker-compose.yml` with: postgres, redis, minio, mlflow, api stub, worker stub, web stub.
- `Makefile` for `dev`, `lint`, `format`, `typecheck`, `test`, `migrate`, `seed`.
- Pre-commit hooks (ruff, black, mypy, eslint, prettier, tsc).
- GitHub Actions CI: lint + typecheck + unit tests.
- ADR 0000 template + ADR-0001..0006 stubs (open decisions from `TECH_REVIEW.md`).
- `LICENSE`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`.

**Dependencies:** Phase 0 approval; git identity recorded.

**Acceptance Criteria**
- `make dev` boots the stack on a clean machine.
- `make lint && make typecheck && make test` is green.
- CI green on the first PR.

**Risks**
- Stack drift between dev / CI / prod images.
- Pre-commit friction slows velocity.

**Testing**
- Smoke test: services answer `/healthz`.
- CI matrix on Python 3.11 / 3.12.
**Status:** ✅ Complete — 2026-06-16. Docker Compose (PostgreSQL 17, Redis, MinIO), pyproject.toml + uv.lock, GitHub Actions CI (Python 3.11/3.12 matrix), frontend Vite+React scaffold, ADR stubs 0000-0006.

---

## Phase 2 — Backend Foundation ✅ Complete

**Objectives**
- FastAPI app with config, logging, telemetry, auth, error model.

**Deliverables**
- App factory + settings (`pydantic-settings`).
- Auth: register, login, refresh, logout (argon2id, JWT).
- Roles + dependency-injected current-user.
- Error model + exception handlers + `trace_id`.
- Structured JSON logging.
- OpenTelemetry traces (no-op exporter in dev).
- `/healthz`, `/readyz`, `/metrics` (Prometheus).
- Rate limiting (slowapi or self-rolled).

**Dependencies:** Phase 1.

**Acceptance Criteria**
- Auth flow covered by integration tests against ephemeral Postgres.
- Per-route p95 ≤ 50 ms for non-DB endpoints in dev.

**Risks**
- JWT misconfiguration (algorithm confusion, missing audience).
- Cookie / CORS edge cases on local dev.

**Testing**
- Unit: token issuance, hashing, permissions.
- Integration: full register → login → refresh → logout flow.
- Security: argon2 params, expiry, refresh rotation.
**Status:** ✅ Complete — 2026-06-16. auth routes live (`/register`, `/login`, `/refresh`, `/me`), argon2id + JWT, AuditLog, TraceID middleware, structlog, Alembic migration 0001. 20 tests (6 unit + 14 integration).
Note: Rate limiting (slowapi) deferred — Redis wasn't available until Docker was set up.

---

## Phase 3 — Frontend Foundation ⚡ Partial

**Objectives**
- React SPA shell with auth, routing, layout, theme.

**Deliverables**
- Vite + TS strict + Tailwind + shadcn/ui.
- Router (TanStack Router) with auth guard.
- TanStack Query setup + generated OpenAPI client.
- Auth screens (sign in / sign up / forgot).
- App shell: sidebar, header, content slot, theme toggle.
- i18n bootstrapped (English only).
- Playwright e2e skeleton.

**Dependencies:** Phase 2 (auth endpoints).

**Acceptance Criteria**
- Authenticated user lands on an empty dashboard.
- Lighthouse score ≥ 90 perf / 95 a11y on shell.

**Risks**
- Type drift between BE and FE — mitigated by generated client.
- Tailwind / shadcn version skew.

**Testing**
- Unit: component snapshots, auth utilities.
- E2E: sign up → sign in → land on dashboard.
**Status:** ⚡ Partial — Vite + React 18 + TypeScript + Tailwind + shadcn/ui scaffold in place. TanStack Router, auth screens, app shell, and all feature components deferred to Phase 13 (Dashboard Integration). Frontend CI passes (ESLint, Prettier, tsc, vitest).

---

## Phase 4 — Database Design & Domain Models ✅ Complete

**Objectives**
- Authoritative schema for users, matches, runs, tracks, stats, predictions, chat, audit.

**Deliverables**
- SQLAlchemy 2.x models per `ARCHITECTURE.md §4`.
- Alembic migrations.
- pgvector extension enabled and `player_embeddings` indexed (HNSW).
- Seed script for a demo user + sample match metadata.

**Dependencies:** Phase 2.

**Acceptance Criteria**
- Migrations apply / rollback cleanly on a fresh DB.
- Index plan documented; `EXPLAIN` checked for the 5 hottest queries.

**Risks**
- pgvector availability in the chosen Postgres image.
- Naming churn — locked via review before merge.

**Testing**
- Integration: round-trip each model.
- Migration up/down test in CI.
**Status:** ✅ Complete — 2026-06-17. ORM models: Team, Player (PlayerPosition enum), Match (MatchStatus enum), MatchEvent (EventType enum — 10 types). Alembic migration 0002 (4 tables + 3 enums). CRUD API routes for /teams, /players, /matches, /matches/{id}/events. 15 integration tests.
Note: pgvector extension deferred — standalone PostgreSQL 17 lacks it; will be enabled via Docker pgvector image in Phase 8. Seed script deferred.

---

## Phase 5 — Video Upload Pipeline ✅ Complete

**Objectives**
- Robust large-file upload with chunking, validation, virus scan.

**Deliverables**
- `POST /matches` returns signed upload URL.
- Client-side chunked upload to MinIO/S3.
- Backend ingest: ffprobe metadata, thumbnails, virus scan via ClamAV.
- `runs` row created on upload completion (status `queued`).
- Quotas + per-user storage usage tracking.

**Dependencies:** Phase 2 + 3 + 4 + MinIO service in compose.

**Acceptance Criteria**
- 2 GB file uploads reliably over a flaky connection (resume works).
- Disallowed MIME types rejected; EICAR rejected.
- Run row visible in admin job board.

**Risks**
- Multipart edge cases (chunk reorder, last-chunk size).
- ClamAV memory footprint.

**Testing**
- Integration: upload, resume, cancel; ffprobe parse; thumbnail generation.
- Security: EICAR + crafted MIME.
**Status:** ✅ Complete (simplified scope) — 2026-06-17/18. Async S3 storage client (aioboto3), VideoUpload ORM model + UploadStatus enum, Alembic migration 0003, REST API (POST/GET/GET-id/GET-download/DELETE /videos/). File validation: 2 GB max, MIME allowlist (mp4, avi, quicktime, webm). Admin-only delete via RBAC. 10 integration tests. MinIO runs in Docker.
Deferred to follow-up: chunked/resumable upload, ffprobe metadata extraction, thumbnails, ClamAV virus scan, per-user quotas.

---

## Phase 6 — Computer Vision Engine

**Objectives**
- YOLOv11 detection running in the CV worker on GPU (CPU fallback).

**Deliverables**
- `worker-cv` service consuming the queue.
- Stages: `probe`, `sample`, `detect`.
- Configurable sampling rate; batch inference.
- Detection results persisted as `detections.parquet` artifact.
- GPU detection metrics exported.

**Dependencies:** Phase 5.

**Acceptance Criteria**
- A 5-minute clip processes detection in ≤ 3 minutes on RTX 3060.
- mAP@0.5 on validation set ≥ 0.5 for `player`.

**Risks**
- CUDA / driver mismatch in container.
- Decode bottleneck (OpenCV) on long videos.

**Testing**
- Unit: detector wrapper, batching, post-processing.
- Eval harness: COCO-style mAP on annotated clips.
- Bench: throughput on a fixture clip in CI (CPU-only, smoke).

---

## Phase 7 — Player Tracking

**Objectives**
- Persistent IDs via DeepSORT (and ByteTrack alternative); team assignment.

**Deliverables**
- `Tracker` interface; DeepSORT + ByteTrack implementations.
- Team assignment via HSV jersey k-means.
- Tracks + positions persisted to DB + parquet.
- Tracker comparison script (HOTA / MOTA) — picks default.

**Dependencies:** Phase 6.

**Acceptance Criteria**
- ID-switch rate ≤ 25% / minute on validation clips (target; refine post-MVP).
- Team labels ≥ 90% correct on validation matches.

**Risks**
- Occlusion + reID limits.
- Jersey-colour clash with referees / goalkeepers.

**Testing**
- Eval: HOTA on annotated clips.
- Unit: team assignment edge cases (4-colour scene).

---

## Phase 8 — Heatmaps & Analytics

**Objectives**
- Per-player / per-team metrics: heatmaps, possession proxy, distance, sprints, formation.

**Deliverables**
- Homography stage (4-point UI calibration) → pitch coords.
- Heatmap artifacts (JSON + PNG).
- Match stats persisted to DB.
- Formation classifier (clustering + nearest-template).

**Dependencies:** Phase 7.

**Acceptance Criteria**
- All metrics returned via API for a seed match.
- Frontend heatmap viewer renders with overlay on pitch SVG.

**Risks**
- Brittle homography without good calibration UX.
- Possession proxy noisy without true ball ownership.

**Testing**
- Unit: homography invariants; metric calculations.
- Visual snapshot: heatmap render parity.

---

## Phase 9 — Match Outcome Prediction Model

**Objectives**
- XGBoost / LightGBM multiclass model with SHAP.

**Deliverables**
- Feature pipeline from FBref / StatsBomb open data.
- Trainer scripts; MLflow runs.
- Model registered + served by `model-server`.
- Endpoint `POST /predict/outcome`.
- Model card in `docs/models/outcome.md`.

**Dependencies:** Phase 4.

**Acceptance Criteria**
- Log-loss ≤ baseline (market) − 0.05 on holdout.
- Calibration plot in model card.
- SHAP top-5 returned with prediction.

**Risks**
- Data leakage from future to past — strict time CV required.
- Distribution shift between leagues.

**Testing**
- Unit: feature builders deterministic given fixed input.
- Eval: time-respecting CV, per-league slices.

---

## Phase 10 — Injury Risk Prediction

**Objectives**
- LightGBM injury-risk scorer using workload + recovery features.

**Deliverables**
- Feature builder (distance, sprints, accel, recovery, age).
- Trainer + MLflow run.
- Endpoint `POST /predict/injury`.
- Model card with honest scope & limitations.

**Dependencies:** Phase 8 (workload features) + Phase 9 (registry pattern).

**Acceptance Criteria**
- Cross-validated AUC documented; explicit "research-grade" disclosure in UI.
- Top drivers per prediction.

**Risks**
- Open labelled injury data is thin — synthetic + literature priors required.
- Misuse risk → clear disclaimers + admin gate by default.

**Testing**
- Unit: feature ranges + monotonicity sanity checks.
- Eval: calibration on temporal holdout.

---

## Phase 11 — Scouting / Similarity Engine

**Objectives**
- Player embeddings + similarity search with filters.

**Deliverables**
- Player feature pipeline (per-90 stats, role tags).
- Embedding training (MLP head over sentence-transformer or pure tabular).
- `player_embeddings` populated; HNSW index live.
- Endpoint `POST /scout/search` with filters (position, age, budget proxy).

**Dependencies:** Phase 4 (pgvector).

**Acceptance Criteria**
- For seed query players, top-5 results are "reasonable" by domain check.
- Search p95 ≤ 300 ms over 10 k players.

**Risks**
- "Reasonable" is subjective — define a rubric + expert spot-check.
- Cold start on rarely-seen positions.

**Testing**
- Unit: filter logic, distance metrics.
- Eval: hold-out "find me X" expert rubric.

---

## Phase 12 — LangGraph Agent System

**Objectives**
- Orchestrator + specialist agents over the extracted state, with tools and guardrails.

**Deliverables**
- LangGraph graph + `AgentState`.
- Specialists: Vision, Tactical, Stats, Prediction, Injury, Scout, Report.
- Tool registry with typed schemas.
- LLM provider adapter (Gemini / OpenAI / Claude / Ollama) — pluggable.
- Token / cost budget per run with hard halt.
- Persistent chat sessions in Postgres.
- SSE streaming endpoint.

**Dependencies:** Phase 8 (for vision/tactical/stats); Phase 9–11 unlock prediction/injury/scout (post-MVP).

**Acceptance Criteria**
- Routing accuracy ≥ 90% on labelled question set.
- Each numeric claim in agent output is cited to an artifact / row.
- Hostile prompt-injection test does not exfiltrate or escape tool boundary.

**Risks**
- Tool hallucination — schema-validate every tool call.
- LLM cost overrun — per-run budgets + alerts.
- Prompt injection from artifact text.

**Testing**
- Unit: tool schemas, routing classifier.
- Integration: end-to-end question → cited answer.
- Adversarial: red-team prompts.

---

## Phase 13 — Dashboard Integration

**Objectives**
- Frontend wires the full MVP loop together.

**Deliverables**
- Match list + status badges.
- Upload UX with chunked progress.
- Match detail tabs: Overview, Tracking, Heatmaps, Stats, Tactics, Chat, Report.
- Agent chat with streaming + citation panel.
- PDF report download + shareable link.
- Empty / loading / error states everywhere.

**Dependencies:** Phases 5, 6, 7, 8, 12.

**Acceptance Criteria**
- New user can: sign up → upload → run completes → view dashboard → chat → download report.
- Lighthouse perf ≥ 85 on key screens.

**Risks**
- SSE on browsers behind corporate proxies.
- Large heatmaps in browser memory.

**Testing**
- E2E: full happy path on a seed match.
- Visual regression on key screens.

---

## Phase 14 — Testing & Hardening

**Objectives**
- Production-grade quality: tests, security, performance, accessibility.

**Deliverables**
- Test coverage ≥ 80% on backend critical paths.
- Contract tests (schemathesis) against OpenAPI.
- k6 load tests for hot paths.
- ZAP baseline scan; pip-audit; npm-audit in CI.
- a11y audit (axe-core) on key screens.
- Requirements matrix mapping FRs/NFRs → tests.

**Dependencies:** Phase 13.

**Acceptance Criteria**
- All FRs / NFRs traced to at least one test.
- CI runs all suites; nightly perf + security extended runs.

**Risks**
- Late-discovered design issues forcing rework.
- Flaky e2e suite eroding trust in CI.

**Testing**
- Itself. Plus chaos drills (kill worker mid-run; observe recovery).

---

## Phase 15 — Deployment

**Objectives**
- Reproducible production deploy + observability + runbooks.

**Deliverables**
- Caddy reverse proxy in front; TLS via Let's Encrypt.
- Compose-on-VM or single-cluster K8s (Helm).
- Managed Postgres (PITR) + managed Redis.
- Object storage in production (S3 or R2).
- Prometheus + Grafana + Sentry live.
- Backup + restore tested.
- Runbooks (`pipeline_stuck.md`, `llm_budget_exceeded.md`, `db_restore.md`).
- Public README + screenshots + demo video.

**Dependencies:** Phase 14.

**Acceptance Criteria**
- Cold deploy from a clean VM in ≤ 30 min.
- Restore drill from a 24-h-old backup succeeds.
- Health probes / dashboards / alerts active.

**Risks**
- GPU availability in target cloud.
- LLM regional availability.

**Testing**
- Deploy rehearsal in staging.
- DR drill in staging.

---

## Milestones & Releases

| Tag | Phases Closed | Status | Notes |
| --- | --- | --- | --- |
| `v0.1.0` | 1 – 5 | 🟡 In Progress | Backend core: auth + domain models + video upload |
| `v0.2.0` | 6 – 8 | ⬜ Not started | CV + tracking + heatmaps |
| `v0.3.0` | 3, 12, 13 (MVP path) | ⬜ Not started | Full frontend + agents + dashboard |
| `v1.0.0` | 1 – 8, 12, 13, 14 | ⬜ Not started | MVP launch |
| `v1.1.0` | + 9 | ⬜ Not started | Outcome prediction |
| `v1.2.0` | + 10 | ⬜ Not started | Injury prediction |
| `v1.3.0` | + 11 | ⬜ Not started | Scout engine |
| `v1.4.0` | + 15 hardening | ⬜ Not started | Production deploy |

---

## Cross-Phase Practices

- **ADRs** authored as decisions arise.
- **`PROJECT_PROGRESS.md`** updated each phase close.
- **`CHANGELOG.md`** entry per milestone tag.
- **`TODO.md`** kept current; cleaned at phase boundaries.
