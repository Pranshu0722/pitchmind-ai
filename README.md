# PitchMind AI

> A Multi-Agent Football Intelligence Platform using Computer Vision, Machine Learning, Predictive Analytics, and Agentic AI.

PitchMind AI ingests football match video and produces tactical, statistical, and predictive insight for coaches, analysts, scouts, and enthusiasts. The platform combines a YOLOv11 + DeepSORT computer-vision pipeline, a multi-model ML stack (XGBoost / LightGBM / SHAP), and a LangGraph-orchestrated multi-agent system that reasons over the extracted signals and produces natural-language reports.

---

## Status

| Item | Value |
| --- | --- |
| Current phase | Phase 5 complete — Video Upload Pipeline |
| Version | 0.5.0-dev |
| MVP target | Phases 1 – 13 (see `ROADMAP.md`) |
| Backend | FastAPI + PostgreSQL + MinIO — auth, domain models, video upload live |
| Frontend | React + Vite + Tailwind scaffold (placeholder; full UI in Phase 13) |
| Tests | 47 passing (8 unit + 39 integration) |
| CI | GitHub Actions — Python 3.11/3.12 matrix, PostgreSQL + Redis + MinIO |

---

## Planning Documents

| Document | Purpose |
| --- | --- |
| [`PRD.md`](./PRD.md) | Product Requirements — vision, personas, user stories, success metrics |
| [`SRS.md`](./SRS.md) | Software Requirements Specification — functional & non-functional requirements |
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | System, data, API, agent, ML, CV, deployment, security, monitoring architecture |
| [`TECH_REVIEW.md`](./TECH_REVIEW.md) | Technology review with alternatives, trade-offs, and recommendations |
| [`FOLDER_STRUCTURE.md`](./FOLDER_STRUCTURE.md) | Monorepo layout |
| [`ROADMAP.md`](./ROADMAP.md) | 15-phase development roadmap with acceptance criteria |
| [`GIT_STRATEGY.md`](./GIT_STRATEGY.md) | Branch strategy, commit conventions, approval rules |
| [`FEATURES.md`](./FEATURES.md) | Innovation backlog: extra features, AI/ML/CV ideas, startup angles |
| [`EVALUATION.md`](./EVALUATION.md) | Project scoring, weaknesses, risks, recommended improvements |
| [`PROJECT_PROGRESS.md`](./PROJECT_PROGRESS.md) | Live progress tracker, architecture decisions, git identity record |
| [`TODO.md`](./TODO.md) | Open tasks by priority |
| [`CHANGELOG.md`](./CHANGELOG.md) | Professional changelog |

---

## High-Level Capabilities (MVP)

1. Match-video upload and validation
2. YOLOv11 player + ball detection
3. DeepSORT multi-object tracking
4. Player heatmaps and movement maps
5. Match statistics (possession, distance, sprints, passes proxy)
6. Tactical analysis via LangGraph agent
7. React analytics dashboard
8. LangGraph orchestrator + first-class agents

## Post-MVP Capabilities

9. Match-outcome prediction (XGBoost / LightGBM, SHAP explainability)
10. Injury-risk prediction
11. Scouting recommendation engine
12. Full multi-agent collaboration (Vision, Tactical, Statistics, Prediction, Injury, Scout, Report, Orchestrator)
13. Natural-language football assistant

---

## Tech Stack

- **Frontend:** React 18 + TypeScript + Tailwind CSS + Vite + shadcn/ui (TanStack Query + Router in Phase 13)
- **Backend:** FastAPI (Python 3.11+), Pydantic v2, SQLAlchemy 2.x async, Alembic, Dramatiq workers
- **Database:** PostgreSQL 17, Redis 7 (cache + queue), MinIO (object storage), pgvector (embeddings — Phase 8)
- **CV:** YOLOv11 (Ultralytics), OpenCV, DeepSORT + ByteTrack (Phase 6–7)
- **ML:** scikit-learn, XGBoost, LightGBM, SHAP, MLflow (Phase 9–11)
- **Agents:** LangGraph + LangChain core, Gemini / Claude / OpenAI / Ollama adapter (Phase 12)
- **DevOps:** Docker Compose, GitHub Actions CI (Python 3.11/3.12 matrix), Prometheus + Grafana
- **Version control:** Git + GitHub

---

## Hard Rules (See `GIT_STRATEGY.md`)

- **No git operations are executed by the assistant.** Commands are suggested and require explicit approval.
- All commits use the git identity recorded in `PROJECT_PROGRESS.md` (`Pranshu0722` / `pranshu.0422@gmail.com`).

---

## Quickstart (backend + infra)

```bash
# 1. Start infrastructure (PostgreSQL, Redis, MinIO)
docker compose up db cache minio -d

# 2. Apply database migrations
cd backend
uv run alembic upgrade head

# 3. Start the API server
uv run uvicorn pitchmind.main:app --reload

# 4. Open API docs
#    Swagger UI  → http://localhost:8000/docs
#    MinIO console → http://localhost:9001  (minioadmin / minioadmin)

# 5. Run tests
uv run pytest -v
```

---

## License

TBD — to be selected during Phase 1.
