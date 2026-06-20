# Changelog — PitchMind AI

All notable changes to this project are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

---

## [Unreleased]

### Added
- `backend/src/pitchmind/api/limiter.py` — slowapi `Limiter` backed by Redis (`swallow_errors=True` so Redis outage never kills the API)
- `backend/src/pitchmind/queue/__init__.py` — package marker
- `backend/src/pitchmind/queue/broker.py` — Dramatiq `RedisBroker` with `Retries` middleware (3 retries, 1 s–60 s exponential backoff)
- `backend/src/pitchmind/queue/tasks.py` — `process_video` Dramatiq actor (PENDING → PROCESSING → READY / FAILED); sync psycopg2 DB access via `create_engine`
- `backend/worker.py` — Dramatiq worker entry point (`uv run dramatiq pitchmind.queue.tasks --queues video`)
- `backend/tests/integration/test_rate_limit.py` — 2 integration tests: 429 returned after 70 sequential login requests; response body contains `RATE_LIMIT_EXCEEDED`
- `backend/tests/unit/conftest.py` — unit-test client fixture with `app.state.redis = AsyncMock()` (ASGITransport does not run lifespan)

### Changed
- `backend/src/pitchmind/main.py` — Redis lifespan (ping on startup, `aclose` on shutdown); `app.state.limiter = limiter`; `RateLimitExceeded` → HTTP 429 with `RATE_LIMIT_EXCEEDED` error code; `/readyz` pings `app.state.redis`
- `backend/src/pitchmind/api/v1/routes/auth.py` — `@limiter.limit(settings.rate_limit_default)` on `POST /login` and `POST /register`
- `backend/src/pitchmind/api/v1/routes/video_uploads.py` — `@limiter.limit(settings.rate_limit_upload)` on `POST /`; initial status set to `PENDING`; `process_video.send()` enqueued after flush
- `backend/pyproject.toml` — added `psycopg2-binary>=2.9.0` (sync DB driver for Dramatiq workers); bumped `pydantic-settings>=2.14.2` (GHSA-4xgf-cpjx-pc3j)
- `frontend/package.json` — vitest + @vitest/ui `^2.1.0` → `^3.2.6` (resolves critical esbuild vuln chain)
- `frontend/vite.config.ts` — added `passWithNoTests: true` to vitest config (CI does not fail when no frontend unit tests exist yet)

### Fixed
- Frontend ESLint CI failure — moved `App` component from `main.tsx` into `src/App.tsx`; `react-refresh/only-export-components` rule now satisfied
- GitHub Actions pip-audit failure — strip editable installs from `uv export` output before auditing; prevents pip-audit following optional `ml` extra (shap → llvmlite 0.36.0, Python <3.10 only)
- Integration test `test_readyz` — `app.state.redis` not set when using `ASGITransport` (lifespan not run); fixed by mocking in unit conftest
- Integration test `test_rate_limit_exceeded_returns_429` — `asyncio.gather()` concurrent requests share one `AsyncSession`; replaced with sequential loop
- Integration test `test_upload_video_success` — expected `"READY"` but upload now sets `"PENDING"` and enqueues worker; assertion updated

---

## [0.5.0] — 2026-06-17 to 2026-06-18 (Phase 5 — Video Upload Pipeline)

### Added
- `backend/src/pitchmind/storage/client.py` — async MinIO/S3 client (aioboto3): `ensure_bucket`, `upload_file`, `get_presigned_url`, `delete_file`, `file_exists`
- `backend/src/pitchmind/db/models/video_upload.py` — `VideoUpload` ORM model + `UploadStatus` enum (PENDING / PROCESSING / READY / FAILED)
- `backend/alembic/versions/0003_video_uploads.py` — migration: `video_uploads` table + `upload_status` enum
- `backend/src/pitchmind/api/v1/schemas/video_upload.py` — `VideoUploadResponse`, `PresignedUrlResponse` Pydantic schemas
- `backend/src/pitchmind/api/v1/routes/video_uploads.py` — 5 endpoints: POST/GET/GET-by-id/GET-download/DELETE; file validation (max 2 GB, MIME allowlist); admin-only delete via RBAC
- `backend/tests/integration/test_video_uploads.py` — 10 integration tests (upload, list, get, presigned URL, delete, reject oversized, reject wrong MIME)
- Docker Compose: MinIO service wired; `minio-data` volume added
- GitHub Actions: MinIO service + S3 env vars added to backend CI job

### Fixed
- GitHub Actions CI: `uv sync --all-extras --dev` → `uv sync --dev` to prevent llvmlite build failure (llvmlite 0.36.0 supports Python ≤3.9 only)
- GitHub Actions CI: pip-audit command now writes to temp file instead of process substitution; added `--skip-editable`
- argon2 OOM in tests: pre-compute `_HASHED_PW = hash_password("TestPass1")` once at module level to avoid repeated argon2 memory allocation

---

## [0.4.0] — 2026-06-17 (Phase 4 — Football Domain Models & CRUD API)

### Added
- `backend/src/pitchmind/db/models/team.py` — `Team` ORM model
- `backend/src/pitchmind/db/models/player.py` — `Player` ORM model + `PlayerPosition` enum (GK / DEF / MID / FWD)
- `backend/src/pitchmind/db/models/match.py` — `Match` ORM model + `MatchStatus` enum (SCHEDULED / LIVE / FINISHED / CANCELLED / POSTPONED)
- `backend/src/pitchmind/db/models/match_event.py` — `MatchEvent` ORM model + `EventType` enum (10 event types: GOAL, OWN_GOAL, ASSIST, YELLOW_CARD, RED_CARD, SECOND_YELLOW, SUBSTITUTION_IN, SUBSTITUTION_OUT, PENALTY_SCORED, PENALTY_MISSED)
- `backend/alembic/versions/0002_domain_models.py` — migration: `teams`, `players`, `matches`, `match_events` tables + 3 enums
- `backend/src/pitchmind/api/v1/routes/teams.py` — GET list, GET by id, POST (admin)
- `backend/src/pitchmind/api/v1/routes/players.py` — GET list (filter by team_id, position), GET by id, POST (admin)
- `backend/src/pitchmind/api/v1/routes/matches.py` — GET/POST list, GET/PATCH by id, GET/POST events
- Pydantic schemas for all domain models (team, player, match, match_event)
- `backend/tests/integration/test_domain.py` — 15 integration tests

---

## [0.3.0] — 2026-06-16 (Phase 2 — Backend Foundation)

### Added
- `backend/src/pitchmind/core/security.py` — argon2id password hashing + JWT access (15 min) / refresh (7 day) token utilities
- `backend/src/pitchmind/core/deps.py` — `get_current_user`, `require_role`, `require_admin` FastAPI dependencies
- `backend/src/pitchmind/api/v1/schemas/auth.py` — `RegisterRequest` (password strength validation), `LoginRequest`, `RefreshRequest`, `TokenResponse`, `UserResponse`
- `backend/src/pitchmind/api/v1/routes/auth.py` — `POST /register`, `POST /login`, `POST /refresh`, `GET /me`; audit log entry on every auth event
- `backend/src/pitchmind/db/models/user.py` — `User` + `UserRole` (USER / ADMIN)
- `backend/src/pitchmind/db/models/audit.py` — `AuditLog` model
- `backend/alembic/versions/0001_initial_users_audit.py` — migration: `users`, `audit_logs` tables + `user_role` enum
- `backend/src/pitchmind/main.py` — TraceID middleware, global exception handlers, structlog, v1 router
- `backend/tests/unit/test_security.py` — 6 unit tests
- `backend/tests/integration/test_auth.py` — 14 integration tests
- `backend/tests/integration/conftest.py` — async test fixtures; real PostgreSQL (pitchmind_test); per-test table truncation; `get_db` override

### Fixed
- `backend/alembic/env.py` — rewrote to use `create_async_engine` directly (removed broken `engine_from_config` + psycopg2 approach)
- Removed `CREATE EXTENSION IF NOT EXISTS vector` from migration 0001 (pgvector not available on standalone PostgreSQL 17; deferred to Docker-based setup)

---

## [0.2.0] — 2026-06-15 to 2026-06-16 (Phase 1 — Project Setup)

### Added
- Monorepo scaffold: `backend/`, `frontend/`, `docs/adr/`, `.github/workflows/`
- `docker-compose.yml` — PostgreSQL 17, Redis 7-alpine, MinIO with health checks and named volumes
- `backend/pyproject.toml` — full dependency set (FastAPI, SQLAlchemy, Alembic, argon2-cffi, python-jose, aioboto3, structlog, OpenTelemetry, etc.); ruff + mypy + pytest config
- `backend/src/pitchmind/config.py` — pydantic-settings `Settings` with all environment variables
- `backend/src/pitchmind/db/session.py` — async SQLAlchemy engine + `get_db` dependency
- `backend/src/pitchmind/db/base.py` — `Base` + `TimestampMixin`
- `backend/alembic/` — Alembic env wired to async engine
- Frontend scaffold: Vite + React 18 + TypeScript strict + Tailwind CSS + shadcn/ui
- `frontend/src/main.tsx` + `frontend/src/App.tsx` — placeholder shell
- `.github/workflows/ci.yml` — backend (Python 3.11 + 3.12, PostgreSQL + Redis + MinIO services) + frontend (Node 20, ESLint + Prettier + tsc + vitest) + security (pip-audit + npm audit)
- ADR docs: `docs/adr/0000-template.md` through `docs/adr/0006-python-env.md`
- `email-validator` dependency added (required by Pydantic email fields)

---

## [0.0.1] — 2026-06-15 (Phase 0 — Planning)

### Added
- `README.md` — project overview, status, tech stack, hard rules
- `PRD.md` — Product Requirements Document
- `SRS.md` — Software Requirements Specification (FR-AUTH through FR-ADM + non-functional requirements)
- `ARCHITECTURE.md` — system, data, API, CV pipeline, ML, agent, deployment, security, monitoring architecture
- `TECH_REVIEW.md` — technology review with alternatives, trade-offs, recommendations, 6 ADRs
- `FOLDER_STRUCTURE.md` — monorepo layout
- `ROADMAP.md` — 15-phase development roadmap
- `GIT_STRATEGY.md` — binding git rules and approval loop
- `FEATURES.md` — innovation backlog (10 additional, 5 AI, 5 ML, 5 CV, 5 recruiter-impressive, 5 startup)
- `EVALUATION.md` — 10-dimension project scoring (avg 8.7/10)
- `PROJECT_PROGRESS.md`, `TODO.md`, `CHANGELOG.md`

### Notes
- No code written at this tag. All six ADRs resolved on the same date.

---

<!-- Links section updated with each release -->
[Unreleased]: https://github.com/Pranshu0722/PitchMind-AI/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/Pranshu0722/PitchMind-AI/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/Pranshu0722/PitchMind-AI/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/Pranshu0722/PitchMind-AI/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/Pranshu0722/PitchMind-AI/compare/v0.0.1...v0.2.0
[0.0.1]: https://github.com/Pranshu0722/PitchMind-AI/releases/tag/v0.0.1
