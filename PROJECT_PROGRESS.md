# Project Progress — PitchMind AI

**Last Updated:** 2026-06-18
**Current Phase:** Phase 5 complete — CI hardening; Phase 6 (Computer Vision Engine) is next

---

## Git Identity (CONFIRMED)

| Field | Value |
| --- | --- |
| git user.name | `Pranshu0722` |
| git user.email | `pranshu.0422@gmail.com` |
| GitHub username | `Pranshu0722` |
| Verified | Yes — confirmed by user on 2026-06-15 |

All commits must use this exact identity. No changes without explicit re-confirmation.

---

## Phase Status

| Phase | Title | Status | Started | Completed |
| --- | --- | --- | --- | --- |
| 0 | Planning | ✅ Complete | 2026-06-15 | 2026-06-15 |
| 1 | Project Setup | ✅ Complete | 2026-06-15 | 2026-06-16 |
| 2 | Backend Foundation | ✅ Complete | 2026-06-16 | 2026-06-16 |
| 3 | Frontend Foundation | ⚡ Partial | 2026-06-16 | — |
| 4 | Database Design & Domain Models | ✅ Complete | 2026-06-17 | 2026-06-17 |
| 5 | Video Upload Pipeline | ✅ Complete | 2026-06-17 | 2026-06-18 |
| 6 | Computer Vision Engine | ⬜ Not Started | — | — |
| 7 | Player Tracking | ⬜ Not Started | — | — |
| 8 | Heatmaps & Analytics | ⬜ Not Started | — | — |
| 9 | Match Outcome Prediction | ⬜ Not Started | — | — |
| 10 | Injury Risk Prediction | ⬜ Not Started | — | — |
| 11 | Scouting Engine | ⬜ Not Started | — | — |
| 12 | LangGraph Agent System | ⬜ Not Started | — | — |
| 13 | Dashboard (Full Frontend) | ⬜ Not Started | — | — |
| 14 | Testing & Hardening | ⬜ Not Started | — | — |
| 15 | Deployment | ⬜ Not Started | — | — |

> **Phase 3 note:** React + Vite + Tailwind scaffold is in place; auth screens, routing, and dashboard UI are deferred to Phase 13.

---

## Completed Tasks

### Phase 0 — Planning
- [x] PRD.md, SRS.md, ARCHITECTURE.md, TECH_REVIEW.md
- [x] FOLDER_STRUCTURE.md, ROADMAP.md, GIT_STRATEGY.md
- [x] FEATURES.md, EVALUATION.md, PROJECT_PROGRESS.md, TODO.md, CHANGELOG.md, README.md
- [x] ADR-0001 through ADR-0006 resolved

### Phase 1 — Project Setup
- [x] Monorepo skeleton (backend/, frontend/, docs/, .github/)
- [x] `docker-compose.yml` — PostgreSQL 17, Redis 7, MinIO
- [x] `backend/pyproject.toml` + `uv.lock` — full dependency set
- [x] ruff lint + format, mypy type checking configured
- [x] Pre-commit hooks
- [x] GitHub Actions CI (Python 3.11 + 3.12 matrix, PostgreSQL + Redis + MinIO services)
- [x] Frontend: Vite + React + TypeScript + Tailwind CSS + shadcn/ui scaffold
- [x] ADR stubs (docs/adr/0000-0006)

### Phase 2 — Backend Foundation
- [x] FastAPI app factory + pydantic-settings config
- [x] Auth: `POST /register`, `POST /login`, `POST /refresh`, `GET /me`
- [x] argon2id password hashing (argon2-cffi)
- [x] JWT access (15 min) + refresh (7 day) tokens via python-jose
- [x] Role-based access (`UserRole.USER` / `UserRole.ADMIN`)
- [x] `get_current_user` + `require_role` FastAPI dependencies
- [x] `AuditLog` model — every auth event persisted
- [x] TraceID middleware + structlog structured logging
- [x] Global exception handlers
- [x] SQLAlchemy 2.x async models + Alembic migration `0001_initial_users_audit`
- [x] 6 unit tests (security.py), 14 integration tests (auth routes)

### Phase 4 — Database Design & Domain Models
- [x] `Team` ORM model
- [x] `Player` ORM model + `PlayerPosition` enum (GK/DEF/MID/FWD)
- [x] `Match` ORM model + `MatchStatus` enum (SCHEDULED/LIVE/FINISHED/CANCELLED/POSTPONED)
- [x] `MatchEvent` ORM model + `EventType` enum (10 event types)
- [x] Alembic migration `0002_domain_models` (4 tables + 3 enums)
- [x] CRUD API routes — `/teams`, `/players`, `/matches`, `/matches/{id}/events`
- [x] Pydantic schemas for all domain models
- [x] 15 integration tests

### Phase 5 — Video Upload Pipeline
- [x] Async S3 storage client (`storage/client.py`) via aioboto3
- [x] `ensure_bucket`, `upload_file`, `get_presigned_url`, `delete_file`, `file_exists`
- [x] `VideoUpload` ORM model + `UploadStatus` enum (PENDING/PROCESSING/READY/FAILED)
- [x] Alembic migration `0003_video_uploads`
- [x] REST API — `POST /videos/`, `GET /videos/`, `GET /videos/{id}`, `GET /videos/{id}/download`, `DELETE /videos/{id}`
- [x] File validation: max 2 GB, allowed MIME types (mp4, avi, quicktime, webm)
- [x] Admin-only delete (RBAC)
- [x] 10 integration tests
- [x] Docker-based MinIO service wired into `docker-compose.yml` and CI

### CI Hardening
- [x] GitHub Actions: added MinIO service + S3 env vars to backend job
- [x] Fixed `uv sync --all-extras` → `uv sync --dev` (llvmlite can't build on Python 3.12)
- [x] Fixed pip-audit: strip editable installs from requirements before auditing (prevents pip-audit following optional ml/cv extras → shap → llvmlite)
- [x] Fixed frontend ESLint: moved `App` component from `main.tsx` to `App.tsx` (react-refresh/only-export-components rule)
- [x] Total test suite: 8 unit + 39 integration = **47 tests** — all green locally

---

## Pending Tasks

- [ ] Phase 6 — Computer Vision Engine (YOLOv11 + DeepSORT in `worker-cv`)
- [ ] Rate limiting (slowapi) — Redis now available via Docker
- [ ] Dramatiq task queue wiring (Redis available)
- [ ] Phase 3 completion — auth screens, TanStack Router, dashboard shell (Phase 13)

---

## Open ADRs

| ID | Topic | Decision | Status |
| --- | --- | --- | --- |
| ADR-0001 | Task queue | **Dramatiq + Redis** | ✅ Resolved 2026-06-15 |
| ADR-0002 | LLM provider strategy | **Multi-provider adapter; Gemini Flash routing, Claude/GPT-4o synthesis, Ollama fallback** | ✅ Resolved 2026-06-15 |
| ADR-0003 | Tracker implementation | **`Tracker` interface; bench DeepSORT vs ByteTrack; ship winner** | ✅ Resolved 2026-06-15 |
| ADR-0004 | Vector store | **pgvector** (Qdrant migration path documented) | ✅ Resolved 2026-06-15 |
| ADR-0005 | Reverse proxy | **Caddy in prod, Nginx in dev compose** | ✅ Resolved 2026-06-15 |
| ADR-0006 | Python env manager | **uv** | ✅ Resolved 2026-06-15 |

---

## Blockers

| # | Blocker | Impact | Owner | Resolution |
| --- | --- | --- | --- | --- |
| B1 | Planning docs not yet approved | Cannot start Phase 1 | User | ✅ Approved 2026-06-15 |
| B2 | Git identity not confirmed | Cannot create any commits | User | ✅ Confirmed 2026-06-15 |
| B3 | Docker VT-x disabled | Cannot run Redis/MinIO in Docker | User | ✅ Enabled Intel VT-x in BIOS 2026-06-17 |
| B4 | PostgreSQL WinError 10055 | Socket exhaustion, uvicorn crashes | User | ✅ PC restart cleared socket state |

---

## Technical Debt

| ID | Item | Impact | Notes |
| --- | --- | --- | --- |
| TD-1 | pgvector extension deferred | Player embedding search unavailable | Standalone PG17 lacks extension; available in Docker pgvector image. Wire up in Phase 8. |
| TD-2 | Frontend placeholder only | No auth screens / routing / UI | Full frontend deferred to Phase 13. |
| TD-3 | Video upload reads entire file into memory | 2 GB uploads hold 2 GB RAM | Replace with streaming/multipart upload in Phase 5 follow-up. |
| TD-4 | No rate limiting yet | Auth endpoints open to brute-force | slowapi + Redis available; add in next sprint. |
| TD-5 | No Dramatiq worker wiring | Background tasks not yet dispatched | Worker service exists in compose; wiring deferred to Phase 6 prep. |

---

## Architecture Decisions (Log)

| Date | Decision | Rationale |
| --- | --- | --- |
| 2026-06-15 | Provider-agnostic LLM adapter | Avoid lock-in; cost control via routing cheap vs strong models |
| 2026-06-15 | pgvector for v1 embeddings | Fewer services; abstraction layer allows Qdrant migration |
| 2026-06-15 | `Tracker` interface (DeepSORT + ByteTrack) | Evidence-based selection; bench both before committing |
| 2026-06-15 | Async task queue (off-thread CV + ML) | GPU work must not block HTTP request thread |
| 2026-06-15 | Artifact-first pipeline | Every stage produces versioned, addressable output |
| 2026-06-15 | MLflow model registry | Reproducibility + version control for served models |
| 2026-06-17 | Switched from Celery to Dramatiq | Dramatiq has simpler API, Redis backend already available |
| 2026-06-17 | MinIO via Docker (not standalone) | Redis also needs Docker; running all infra in compose is consistent |
| 2026-06-18 | pip-audit strips editable installs | Optional ml/cv extras (shap→llvmlite) must not be audited in core CI |

---

## Risk Register (live)

| ID | Risk | Status | Notes |
| --- | --- | --- | --- |
| T1 | YOLOv11 ID-switch rate | Open | Mitigation: ByteTrack + jersey OCR |
| T5 | CUDA / driver mismatch | Open | Pin CUDA base image before Phase 6 |
| P1 | Scope creep | Open | Phase-gate acceptance criteria |
| P3 | LLM cost runaway | Open | Per-run budget enforced in Phase 12 |
| B1 | Injury model misuse | Open | Disclaimer + admin gate |
| T6 | In-memory video upload (2 GB cap) | Open | Replace with streaming before Phase 6 |

---

## Milestones

| Tag | Status | Date |
| --- | --- | --- |
| Planning docs complete | ✅ Done | 2026-06-15 |
| Initial commit pushed to GitHub | ✅ Done | 2026-06-15 |
| Phase 1–2 complete (auth + CI) | ✅ Done | 2026-06-16 |
| Phase 4–5 complete (domain models + video upload) | ✅ Done | 2026-06-18 |
| `v0.1.0` (Phases 1–5 backend core) | 🟡 In Progress | — |
| `v0.2.0` (Phases 6–8: CV + tracking + heatmaps) | ⬜ Not started | — |
| `v0.3.0` (MVP path + agents) | ⬜ Not started | — |
| `v1.0.0` MVP launch | ⬜ Not started | — |

## Repository

- **GitHub:** https://github.com/Pranshu0722/pitchmind-ai
- **Default branch:** main
