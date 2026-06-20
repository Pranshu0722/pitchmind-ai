# PitchMind AI

> A Multi-Agent Football Intelligence Platform using Computer Vision, Machine Learning, Predictive Analytics, and Agentic AI.

PitchMind AI ingests football match video and produces tactical, statistical, and predictive insight for coaches, analysts, scouts, and enthusiasts. The platform combines a YOLOv11 + DeepSORT computer-vision pipeline, a multi-model ML stack (XGBoost / LightGBM / SHAP), and a LangGraph-orchestrated multi-agent system that reasons over the extracted signals and produces natural-language reports.

---

## Status

| Item | Value |
| --- | --- |
| Current phase | Phase 6 — Computer Vision Engine (starting) |
| Version | 0.6.0-dev |
| MVP target | Phases 1 – 13 (see `ROADMAP.md`) |
| Backend | FastAPI + PostgreSQL + MinIO + Redis — auth, domain models, video upload, rate limiting, Dramatiq worker |
| Frontend | React + Vite + Tailwind scaffold (placeholder; full UI in Phase 13) |
| Tests | 49 passing (8 unit + 41 integration) |
| CI | GitHub Actions — Python 3.11/3.12 matrix, PostgreSQL + Redis + MinIO |

---

## What's Live (Phases 1–5 + tech debt)

The backend API is fully functional. Start the stack and open `http://localhost:8000/docs` to explore.

### Auth (`/api/v1/auth/`)
| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/auth/register` | Register user (email + password, argon2id) |
| POST | `/auth/login` | Login → access + refresh JWT tokens |
| POST | `/auth/refresh` | Rotate tokens using refresh token |
| GET | `/auth/me` | Get current authenticated user |

### Football Domain (`/api/v1/`)
| Method | Endpoint | Description |
| --- | --- | --- |
| GET/POST | `/teams/` | List teams / create team (admin) |
| GET | `/teams/{id}` | Get team by id |
| GET/POST | `/players/` | List players (filter by team, position) / create (admin) |
| GET | `/players/{id}` | Get player by id |
| GET/POST | `/matches/` | List matches / create match |
| GET/PATCH | `/matches/{id}` | Get or update match |
| GET/POST | `/matches/{id}/events` | List or add match events |

### Video Uploads (`/api/v1/videos/`)
| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/videos/` | Upload video file (mp4/avi/quicktime/webm, max 2 GB) — rate-limited; enqueues `process_video` worker |
| GET | `/videos/` | List uploads (filter by match, status) |
| GET | `/videos/{id}` | Get upload record |
| GET | `/videos/{id}/download` | Generate pre-signed download URL |
| DELETE | `/videos/{id}` | Delete upload + storage object (admin only) |

### Rate Limiting
All auth endpoints (`/login`, `/register`) and video uploads are rate-limited via slowapi + Redis. Exceeding the limit returns HTTP 429 with `{"error": {"code": "RATE_LIMIT_EXCEEDED"}}`.

---

## Documentation

| Document | Purpose |
| --- | --- |
| [`PRD.md`](./PRD.md) | Product Requirements — vision, personas, user stories, success metrics |
| [`SRS.md`](./SRS.md) | Software Requirements Specification — functional & non-functional requirements |
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | System, data, API, agent, ML, CV, deployment, security, monitoring architecture |
| [`TECH_REVIEW.md`](./TECH_REVIEW.md) | Technology review — alternatives, trade-offs, ADR decisions |
| [`FOLDER_STRUCTURE.md`](./FOLDER_STRUCTURE.md) | Monorepo layout — ✅ built vs 📋 planned |
| [`ROADMAP.md`](./ROADMAP.md) | 15-phase development roadmap with acceptance criteria and phase status |
| [`GIT_STRATEGY.md`](./GIT_STRATEGY.md) | Branch strategy, commit conventions, approval rules |
| [`FEATURES.md`](./FEATURES.md) | Innovation backlog: extra features, AI/ML/CV ideas, startup angles |
| [`EVALUATION.md`](./EVALUATION.md) | Project scoring, weaknesses, risks, recommended improvements |
| [`PROJECT_PROGRESS.md`](./PROJECT_PROGRESS.md) | Live progress tracker, technical debt, architecture decisions |
| [`TODO.md`](./TODO.md) | Open tasks by priority |
| [`CHANGELOG.md`](./CHANGELOG.md) | Full changelog per phase |

---

## Capabilities

### Live (Phases 1–5 + tech debt)
- User registration, login, JWT auth with role-based access control
- Football domain: teams, players, matches, match events (full CRUD)
- Match video upload to MinIO object storage with pre-signed download URLs
- Rate limiting on auth + upload endpoints (slowapi + Redis; HTTP 429 on breach)
- Dramatiq background worker — `process_video` actor enqueued on every upload (PENDING → PROCESSING → READY/FAILED)
- 49 tests (8 unit + 41 integration) — all passing, CI green

### Planned — MVP (Phases 6–13)
- YOLOv11 player + ball detection (Phase 6)
- DeepSORT + ByteTrack multi-object tracking (Phase 7)
- Player heatmaps, possession proxy, sprint/distance metrics (Phase 8)
- Match-outcome prediction — XGBoost / LightGBM + SHAP explainability (Phase 9)
- Injury-risk prediction model (Phase 10)
- Player scouting similarity search via pgvector (Phase 11)
- LangGraph multi-agent system — orchestrator + 7 specialist agents (Phase 12)
- React analytics dashboard — upload UX, heatmaps, agent chat, PDF reports (Phase 13)

---

## Tech Stack

| Layer | Technology |
| --- | --- |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui (TanStack Query + Router — Phase 13) |
| **Backend** | FastAPI, Python 3.11+, Pydantic v2, SQLAlchemy 2.x async, Alembic |
| **Workers** | Dramatiq + Redis (task queue for CV/ML jobs) |
| **Database** | PostgreSQL 17, Redis 7, MinIO (object storage), pgvector (Phase 8) |
| **CV** | YOLOv11 (Ultralytics), OpenCV, DeepSORT, ByteTrack (Phase 6–7) |
| **ML** | scikit-learn, XGBoost, LightGBM, SHAP, MLflow (Phase 9–11) |
| **Agents** | LangGraph + LangChain, Gemini Flash / Claude Sonnet / Ollama adapter (Phase 12) |
| **DevOps** | Docker Compose, GitHub Actions CI, Prometheus + Grafana (Phase 14–15) |

---

## Hard Rules (See `GIT_STRATEGY.md`)

- **No git operations are executed by the assistant.** Commands are suggested and require explicit approval.
- All commits use the git identity in `PROJECT_PROGRESS.md`: `Pranshu0722` / `pranshu.0422@gmail.com`.
- `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>` is appended to commits where the assistant generated the bulk of the code.

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — for PostgreSQL, Redis, MinIO
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — Python package manager
- Python 3.11 or 3.12

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Quickstart

```bash
# Clone and enter repo
git clone https://github.com/Pranshu0722/PitchMind-AI.git
cd PitchMind-AI

# 1. Start infrastructure (PostgreSQL 17, Redis 7, MinIO)
docker compose up db cache minio -d

# 2. Install backend dependencies
cd backend
uv sync --dev

# 3. Apply database migrations
uv run alembic upgrade head

# 4. Start the API server (terminal 1)
uv run uvicorn pitchmind.main:app --reload

# 5. Start the background worker (terminal 2)
uv run dramatiq pitchmind.queue.tasks --queues video

# 6. Explore the API
#    Swagger UI    → http://localhost:8000/docs
#    ReDoc         → http://localhost:8000/redoc
#    MinIO console → http://localhost:9001  (login: minioadmin / minioadmin)

# 7. Run the full test suite
uv run pytest -v
```

---

## License

MIT — to be formally added in Phase 14 before public release.
