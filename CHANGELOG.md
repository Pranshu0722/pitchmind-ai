# Changelog — PitchMind AI

All notable changes to this project are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

---

## [Unreleased]

### Fixed
- Frontend ESLint CI failure — moved `App` component from `main.tsx` into `src/App.tsx`; `react-refresh/only-export-components` rule now satisfied
- GitHub Actions pip-audit failure — strip editable installs from `uv export` output before auditing; prevents pip-audit following optional `ml` extra (shap → llvmlite 0.36.0, Python <3.10 only)

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
