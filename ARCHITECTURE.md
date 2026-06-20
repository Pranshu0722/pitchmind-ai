# System Architecture — PitchMind AI

**Version:** 0.2 (Active)
**Status:** Approved — implementation in progress (Phases 1–5 + rate limiting + Dramatiq complete; Phase 6 starting)

This document describes the system, data, API, agent, ML, CV, deployment, security, and monitoring architecture. Trade-offs and alternative choices are captured in `TECH_REVIEW.md`. Phase-by-phase build order is in `ROADMAP.md`.

---

## 1. Architectural Principles

1. **Async by default** — anything > 100 ms off the request thread.
2. **Stateless tier separation** — API, worker, model server are independently scalable.
3. **Artifacts are first-class** — every pipeline stage emits versioned, addressable artifacts.
4. **Tools, not god-objects** — agents access capabilities through a typed tool registry.
5. **Observability is a feature** — logs / metrics / traces baked in from Phase 2.
6. **Local-first** — `docker compose up` boots the whole stack; nothing cloud-only in core code.
7. **Reproducibility** — every Run records model versions, seeds, and configs.

---

## 2. High-Level System Diagram

```
                      ┌────────────────────────────┐
                      │  React + TS + Tailwind SPA │
                      │   (Vite, TanStack Query)   │
                      └────────────┬───────────────┘
                                   │  HTTPS (JWT)
                                   ▼
┌──────────────────────────────────────────────────────────────┐
│                       Nginx / API Gateway                    │
│              (TLS termination, rate limiting)                │
└────────────┬───────────────────────────────┬─────────────────┘
             │                               │
             ▼                               ▼
   ┌──────────────────┐            ┌──────────────────────┐
   │   FastAPI API    │            │   Auth Service       │
   │   (Python 3.11)  │            │ (JWT, OAuth, users)  │
   └─────┬────────┬───┘            └─────────┬────────────┘
         │        │                          │
         │        │ enqueue                  │ read/write
         │        ▼                          ▼
         │   ┌──────────────┐         ┌──────────────────┐
         │   │ Redis Queue  │◀────────┤  PostgreSQL 17   │
         │   │  (Dramatiq)  │  state  │  (+ pgvector)    │
         │   │              │         └──────────────────┘
         │   └──────┬───────┘                    ▲
         │          │ dequeue                    │
         │          ▼                            │
         │   ┌─────────────────────────┐         │
         │   │   CV Worker (GPU)       │         │
         │   │  YOLOv11 + DeepSORT     │─────────┤
         │   │  OpenCV + Homography    │         │
         │   └──────┬──────────────────┘         │
         │          │ artifacts                  │
         │          ▼                            │
         │   ┌──────────────────┐                │
         │   │  Object Store    │                │
         │   │  (MinIO / S3)    │                │
         │   └──────────────────┘                │
         │                                       │
         ▼                                       │
   ┌──────────────────────────┐                  │
   │  Agent Service           │                  │
   │  (LangGraph + LangChain) │──────────────────┤
   │  + Tool Registry         │                  │
   └──────┬───────────────────┘                  │
          │                                      │
          ▼                                      │
   ┌──────────────────────────┐                  │
   │  Model Server            │──────────────────┘
   │  (FastAPI, MLflow models)│
   │  XGBoost / LightGBM      │
   └──────────────────────────┘

   Cross-cutting: MLflow tracking | Prometheus + Grafana | Sentry | OpenTelemetry
```

---

## 3. Service Decomposition

| Service | Language | Responsibility |
| --- | --- | --- |
| `web` | React + TS | SPA dashboard, agent chat, reports |
| `api` | FastAPI | REST endpoints, auth, run orchestration, artifact serving |
| `worker-cv` | Python | YOLOv11 + DeepSORT + OpenCV pipeline (GPU) |
| `worker-ml` | Python | Feature build, prediction model invocation, batch jobs |
| `agent-service` | Python | LangGraph orchestrator + agents + tool registry |
| `model-server` | FastAPI | Serve trained ML models (outcome / injury / similarity) |
| `mlflow` | MLflow | Experiment tracking + model registry |
| `db` | PostgreSQL 17 | OLTP store + pgvector for embeddings |
| `cache+queue` | Redis 7 | Cache + Dramatiq broker + rate limiting |
| `object-store` | MinIO | Artifact store (S3-compatible) |
| `gateway` | Nginx | TLS, routing, rate limit, gzip |

Why split worker-cv from worker-ml? Different resource profiles (GPU vs CPU/RAM) and very different deploy cadence.

Why a separate `model-server`? Decouples model deploy from app deploy; lets us shadow-test models.

Why a separate `agent-service`? Agent flows can hold long-lived LLM connections; isolating them protects API tail-latency.

---

## 4. Data Architecture

### 4.1 Logical Data Model (core entities)

```
users ──< matches ──< runs ──< stage_events
                  │
                  ├──< tracks ──< track_positions
                  │
                  ├──< heatmaps
                  ├──< match_stats
                  ├──< formations
                  ├──< predictions (outcome / injury)
                  ├──< reports
                  └──< chat_sessions ──< chat_messages

players (canonical)        ── used by scout similarity ──>  player_embeddings (pgvector)
teams (canonical)
external_matches (FBref)   ── feature store for outcome model
```

### 4.2 Key Tables (sketch)

```sql
-- Identity
users(id, email, password_hash, role, created_at)
api_keys(id, user_id, token_hash, scopes, expires_at)

-- Matches & runs
matches(id, user_id, title, source_url, fps, duration_s, status, created_at)
runs(id, match_id, config_json, status, started_at, finished_at, error)
stage_events(id, run_id, stage, status, started_at, finished_at, metrics_json)

-- CV outputs
tracks(id, run_id, team_label, role_label, color_hex, jersey_number_guess)
track_positions(id, track_id, t_ms, x_m, y_m, vx, vy, conf)
heatmaps(id, run_id, track_id NULL, team_label NULL, period, grid_w, grid_h, blob_url)
formations(id, run_id, team_label, period, label, confidence, snapshot_url)

-- Analytics
match_stats(id, run_id, key, value_num, value_json)

-- ML
predictions(id, run_id, model, version, output_json, shap_json, created_at)

-- Player db / scouting
players(id, name, dob, nationality, primary_position, foot, ...)
player_embeddings(player_id, embedding vector(384), version)

-- Agents / chat
chat_sessions(id, match_id, user_id, agent_graph_version, started_at)
chat_messages(id, session_id, role, content, citations_json, tokens_in, tokens_out, cost_cents)

-- Artifacts
artifacts(id, run_id, kind, blob_url, sha256, size_bytes, created_at)

-- Audit
audit_log(id, actor_id, action, target, meta_json, created_at)
```

Indexes (initial): `runs(match_id, status)`, `track_positions(track_id, t_ms)`, `match_stats(run_id, key)`, `players(name)`, `player_embeddings` HNSW via pgvector.

### 4.3 Storage Conventions

- **Object store keys:** `s3://pitchmind/{user_id}/{match_id}/{run_id}/{stage}/{filename}`.
- **Artifact kinds:** `frame_index`, `detections`, `tracks_parquet`, `heatmap_png`, `heatmap_json`, `report_pdf`, etc.
- **Hot vs cold:** active matches in standard tier; > 30 days moved to cold tier; deletion within 24 h on user request.

### 4.4 Migrations

- Alembic per service that owns tables. Forward-only by default; rollback scripts for the last N migrations.

---

## 5. API Design

### 5.1 Style

- REST + JSON. Cursor pagination. snake_case in JSON.
- Versioning: `/api/v1/`.
- Streaming via Server-Sent Events for agent chat.
- Idempotency keys for POSTs that create resources.

### 5.2 Surface (representative)

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/v1/auth/register` | Register user |
| POST | `/api/v1/auth/login` | Login |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/matches` | Create match (returns upload URL) |
| PUT | (signed S3 URL) | Direct upload to object store |
| POST | `/api/v1/matches/{id}/start` | Trigger pipeline run |
| GET | `/api/v1/matches/{id}` | Match metadata + latest run |
| GET | `/api/v1/matches/{id}/runs/{run_id}` | Run details |
| GET | `/api/v1/matches/{id}/heatmaps?track_id=...` | Heatmap artifacts |
| GET | `/api/v1/matches/{id}/stats` | Match stats |
| GET | `/api/v1/matches/{id}/tracks` | Track list |
| GET | `/api/v1/matches/{id}/tracks/{tid}/positions` | Positions stream |
| POST | `/api/v1/matches/{id}/chat` | Open chat session |
| POST | `/api/v1/chat/{session_id}/messages` | Send message (SSE response) |
| POST | `/api/v1/matches/{id}/report` | Generate / download report |
| POST | `/api/v1/predict/outcome` | Outcome prediction |
| POST | `/api/v1/predict/injury` | Injury prediction |
| POST | `/api/v1/scout/search` | Player similarity search |
| GET | `/healthz` / `/readyz` / `/metrics` | Ops endpoints |

> **Implementation status (Phase 5):** Routes with ✅ are live. All others are planned.
> - ✅ `POST /api/v1/auth/register` — `POST /api/v1/auth/login` — `POST /api/v1/auth/refresh` — `GET /api/v1/auth/me`
> - ✅ `GET/POST /api/v1/teams/` — `GET /api/v1/teams/{id}`
> - ✅ `GET/POST /api/v1/players/` — `GET /api/v1/players/{id}`
> - ✅ `GET/POST /api/v1/matches/` — `GET/PATCH /api/v1/matches/{id}` — `GET/POST /api/v1/matches/{id}/events`
> - ✅ `POST/GET /api/v1/videos/` — `GET /api/v1/videos/{id}` — `GET /api/v1/videos/{id}/download` — `DELETE /api/v1/videos/{id}`

### 5.3 Error Model

```json
{
  "error": {
    "code": "MATCH_NOT_FOUND",
    "message": "No match for id 1234",
    "trace_id": "..."
  }
}
```

### 5.4 Auth

- JWT access token in `Authorization: Bearer ...`.
- Refresh token in HttpOnly secure cookie.
- Object-store URLs are short-lived signed URLs.

---

## 6. Computer Vision Pipeline

```
Upload  ─►  Probe (ffprobe metadata)
         ─►  Sample frames (5 fps default)
         ─►  Detect (YOLOv11) ─► player / ball / referee boxes
         ─►  Track (DeepSORT, ByteTrack alt) ─► persistent IDs
         ─►  Team assignment (HSV jersey k-means)
         ─►  Homography (4-pt calibration → pitch coords)
         ─►  Metrics (heatmaps, distance, sprints, possession, formation)
         ─►  Persist artifacts + structured rows
         ─►  Emit `cv.run.completed` event
```

### 6.1 Stage Detail

| Stage | Tools | Output Artifact |
| --- | --- | --- |
| Probe | ffprobe | `metadata.json` |
| Sample | OpenCV | `frames/*.jpg` (or in-memory) |
| Detect | YOLOv11 (Ultralytics) | `detections.parquet` |
| Track | DeepSORT (primary) or ByteTrack | `tracks.parquet` |
| Team | OpenCV + sklearn k-means | `team_assignments.json` |
| Homography | OpenCV `findHomography` + 4-pt UI calibration | `homography.json` |
| Metrics | NumPy / Pandas | `heatmap_*.png/.json`, `stats.json` |

### 6.2 Performance Plan

- Run detection at 5 fps; tracking interpolates between detection frames.
- Batch inference (batch size 16) on GPU.
- Mixed precision (FP16) where stable.
- Pre-allocate writers; avoid per-frame Python overhead.
- Target: 90-min 1080p → ≤ 30 min on RTX 3060-class GPU.

### 6.3 Accuracy Plan

- Bootstrap on COCO `person`; fine-tune on SoccerNet for `player`, `ball`, `goalkeeper`, `referee`.
- Track-quality metric: HOTA on held-out clips.
- Ball: explicit small-object head OR a second specialised model + Kalman smoothing.

### 6.4 Failure Modes

- **No people detected** → fail run with `INSUFFICIENT_DETECTIONS` and a clear message.
- **Severe occlusion** → log low-quality flag; agent layer should disclose uncertainty.
- **Unstable homography** → require manual recalibration in UI.

---

## 7. Machine Learning Architecture

### 7.1 Model Catalogue

| Model | Family | Target | Features (summary) | Output |
| --- | --- | --- | --- | --- |
| Outcome | XGBoost (LightGBM alt) | Multiclass {H, D, A} | rolling form, xG, possession, home/away, rest days, injuries | softmax probabilities + SHAP |
| Injury risk | LightGBM regression / GBT classifier | 0 – 1 risk | distance, sprints, accel/decel, recovery days, age, history | risk score + driver list |
| Scout similarity | sentence-transformers + custom feature MLP | embedding vector | per-90 stats, role, foot, age | top-K nearest in pgvector |
| (Stretch) xG mini | Logistic / GBT | shot xG | location, angle, body part, defenders | probability |

### 7.2 Training Pipeline

```
   Raw sources (FBref / StatsBomb / SoccerNet / our runs)
        ▼
   Feature store (Parquet on S3, registered in MLflow)
        ▼
   Trainer (sklearn pipelines) ─► metrics ─► MLflow run
        ▼
   Promote to registry (staging → production)
        ▼
   Model server pulls latest production artifact
```

### 7.3 Explainability

- SHAP TreeExplainer for outcome + injury.
- Per-prediction top-N feature contributions persisted alongside the prediction.

### 7.4 Validation

- Time-respecting CV (no leakage from future to past).
- Calibration plots; Brier score; log-loss vs baseline.
- Cohort slicing (league, season) to surface distribution shift.

### 7.5 Model Lifecycle

- Datasets versioned by hash.
- Every model version → MLflow run → artifact in registry → served by model server.
- Shadow mode: a new candidate model receives traffic in parallel for evaluation before promotion.

---

## 8. Agent Architecture (LangGraph)

### 8.1 Graph Topology

```
                        ┌────────────────┐
                        │  Orchestrator  │
                        └───┬────────────┘
       ┌──────────┬────────┼─────────┬────────┬────────┐
       ▼          ▼        ▼         ▼        ▼        ▼
   Vision     Tactical   Stats   Prediction Injury  Scout
       │          │        │         │        │        │
       └──────────┴───┬────┴─────────┴────────┴────────┘
                     ▼
                ┌──────────┐
                │  Report  │
                └──────────┘
```

### 8.2 Agent Responsibilities

| Agent | Reads | Writes / Calls | Output Form |
| --- | --- | --- | --- |
| Orchestrator | user query + chat state | routes to specialist | routing decision + plan |
| Vision | tracks, heatmaps, formations | n/a | grounded answer + artifact citation |
| Tactical | stats + formations + heatmaps | n/a | narrative + numeric anchors |
| Stats | match_stats, tracks | n/a | precise numeric answer |
| Prediction | match features | model server | probabilities + SHAP |
| Injury | per-player workload | model server | risk + drivers |
| Scout | player query | similarity index (pgvector) | ranked list |
| Report | all of the above | object store (PDF) | report artifact ID |

### 8.3 State Management

- Graph state = pydantic model `AgentState` containing: `query`, `chat_history`, `routing`, `intermediates`, `citations`, `cost_budget_remaining`.
- Persisted to Postgres `chat_sessions` so a chat can resume across requests.
- Short-term memory: in-graph state. Long-term memory: per-match summaries stored as embeddings.

### 8.4 Tool Registry

Tools are typed and versioned:

```python
class Tool(Protocol):
    name: str
    version: str
    input_schema: type[BaseModel]
    output_schema: type[BaseModel]
    requires_roles: set[str]
    def __call__(self, ctx: Ctx, **kwargs) -> Any: ...
```

Examples: `get_heatmap`, `get_match_stats`, `predict_outcome`, `predict_injury`, `scout_similar`, `generate_pdf`.

### 8.5 LLM Strategy

- **Routing**: cheap fast model (e.g., Gemini Flash / GPT-4o-mini).
- **Synthesis**: stronger model only when query complexity warrants it.
- **Embeddings**: sentence-transformers locally (cost = 0) or hosted embedding model.

### 8.6 Safety & Guardrails

- Per-run token budget; halts gracefully on exceed.
- Tool whitelist per agent.
- No raw SQL from LLMs — only via parameterised tool calls.
- Prompt-injection mitigation: never execute instructions embedded in artifact text without sanitisation; cite, don't obey.
- Output validation against pydantic schemas before user display.

### 8.7 Failure Handling

- Tool failure → agent receives structured error → may retry once with different params, then surfaces graceful failure.
- LLM provider 5xx → exponential backoff → fall back to secondary provider if configured.
- Orchestrator-level circuit breaker on repeated agent failures.

---

## 9. Deployment Architecture

### 9.1 Environments

| Env | Purpose | Differences |
| --- | --- | --- |
| `local` | dev laptop | docker compose; MinIO; CPU-or-GPU |
| `staging` | pre-prod, demo | hosted; cheaper instances; shadow models |
| `prod` | public | autoscaling; backups; alerts |

### 9.2 Compose Topology (dev)

```
gateway (nginx) ─► web (react), api (fastapi)
api ─► db (postgres), cache (redis), minio
api ─► agent-service ─► model-server
worker-cv ─► db, minio, redis
worker-ml ─► db, minio, redis, mlflow
mlflow ─► db, minio
prometheus + grafana scrape /metrics
```

### 9.3 Production Topology (target)

- Kubernetes-ready (Helm charts). For v1 a single-VM Docker host with Caddy/Nginx is acceptable.
- Object store: AWS S3 or Cloudflare R2.
- DB: managed Postgres (RDS / Neon / Supabase) with PITR.
- Queue: managed Redis (Upstash / Elasticache).
- GPU worker on a separate node pool / VM.
- Secrets: cloud secret manager or sealed-secrets.

### 9.4 CI/CD

- GitHub Actions: lint → typecheck → unit tests → build images → integration tests → push to registry → deploy on tag.
- Migrations gated by manual approval in prod.

---

## 10. Security Architecture

### 10.1 Identity

- argon2id password hashing.
- JWT access (15 min) + refresh (7 d, HttpOnly cookie).
- OAuth (Google) via Authlib; merge by verified email.
- Role-based authorisation (`user`, `admin`).

### 10.2 Transport

- TLS everywhere; HSTS in prod.
- CORS allow-list per environment.

### 10.3 Storage

- Object-store access via short-lived signed URLs.
- DB SSL required in prod; client certificates for service-to-service is a stretch goal.

### 10.4 Application

- Input validation via Pydantic; SQLAlchemy parameterised queries only.
- Rate limiting at gateway + per-route in API.
- Audit log for privileged actions.
- Dependency vulnerability scanning in CI.
- CSP, X-Content-Type-Options, X-Frame-Options on frontend.

### 10.5 LLM-Specific

- Prompt-injection defence (see §8.6).
- Output schema validation.
- Sensitive content filtering (toxicity, PII) at the boundary.

### 10.6 Privacy

- Players' faces never used as biometric ID.
- Right to delete (24-hour SLA) including derived artifacts.
- Logs scrubbed of PII; user IDs hashed in logs.

---

## 11. Monitoring & Observability

### 11.1 Three Pillars

- **Logs:** Structured JSON with `trace_id`, `run_id`, `user_id_hash`. Aggregation: Loki or self-hosted ELK; Cloud option: Grafana Cloud.
- **Metrics:** Prometheus scraping API + workers + model server + GPU exporter. Custom counters for `runs_started`, `stage_duration_seconds`, `llm_tokens_used`, `llm_cost_cents`.
- **Traces:** OpenTelemetry SDK on API, agent-service, workers. Exporter: Tempo / Jaeger.

### 11.2 Dashboards (Grafana)

1. **API Health** — RPS, p95, error rate, queue depth.
2. **Pipeline** — runs/h, stage timings, success/failure, GPU utilisation.
3. **Agent Cost** — tokens, $ per run, per user.
4. **Model Serving** — latency, error rate, model version in use.

### 11.3 Alerts

- API 5xx > 1% for 5 min → page.
- Queue depth > N for 15 min → page.
- LLM budget burn-rate > 2× → warn.
- Job-completion rate < 99% rolling 24 h → warn.

### 11.4 Error Capture

- Sentry on FE and BE; release tracking tied to git SHA.

---

## 12. Cross-Cutting Concerns

### 12.1 Configuration

- 12-factor: config via env vars. `pydantic-settings` for typed config.
- Per-environment `.env.{local,staging,prod}` checked into the secrets vault, not the repo.

### 12.2 Feature Flags

- Minimal flag system (env-driven for v1). Hooks left for OpenFeature.

### 12.3 Internationalisation

- i18next on frontend. Backend returns machine-readable error codes; UI maps to localised strings.

### 12.4 Testing

- Unit (pytest, vitest).
- Integration (testcontainers for Postgres / Redis / MinIO).
- Contract (schemathesis against OpenAPI).
- E2E (Playwright).
- Load (k6) on hot paths.
- ML model evaluation harness with frozen test sets.
- CV evaluation harness with annotated clips (HOTA, MOTA).

### 12.5 Architectural Decision Records

- Stored in `docs/adr/NNNN-title.md`. Every cross-cutting choice (queue, ORM, LLM provider, tracker) gets one. Template in Phase 1.

---

## 13. Open Architectural Questions

1. **Queue:** Celery vs RQ vs Arq vs Dramatiq. Default Celery; revisit if Celery's heaviness shows.
2. **Tracker:** DeepSORT vs ByteTrack vs StrongSORT. Ship DeepSORT; bench ByteTrack on validation set.
3. **Vector store:** pgvector vs Qdrant. pgvector for v1 (fewer moving parts).
4. **Embeddings:** local sentence-transformers vs hosted. Local for v1 (cost).
5. **Realtime:** SSE for agent streaming for v1; WebSocket only if multi-channel needed.

All five tracked as open ADRs in `TODO.md`.
