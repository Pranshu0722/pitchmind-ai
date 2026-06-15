# Technology Review — PitchMind AI

**Version:** 0.1 (Planning)
**Status:** Draft — awaiting approval

> Format per technology: **Why it fits → Alternatives → Trade-offs → Recommendation.**
> Items marked **CHANGE PROPOSED** suggest a substitution worth discussing before Phase 1.

---

## 1. Frontend

### 1.1 React

- **Why it fits:** Mature ecosystem, hireable skill, excellent libraries for charts (Recharts / VisX), 3D / canvas (deck.gl, Konva), and SSR if needed.
- **Alternatives:** SvelteKit, Vue 3, SolidJS, Next.js (React meta-framework), Remix.
- **Trade-offs:** React itself is just a view library; needs Router, query, forms.
- **Recommendation:** Keep React, but pair with **Vite + TanStack Router + TanStack Query + Zustand** for a lean SPA. Use Next.js only if SEO becomes a goal — not needed for an authenticated dashboard.

### 1.2 TypeScript

- **Why it fits:** Type safety on a long-lived dashboard; OpenAPI → TS client generation gives end-to-end types.
- **Alternatives:** Plain JS (rejected).
- **Recommendation:** **Keep.** Run in `strict` mode from day 1.

### 1.3 Tailwind CSS

- **Why it fits:** Velocity, design-system without writing one, great with shadcn/ui.
- **Alternatives:** Vanilla CSS Modules, CSS-in-JS (Emotion / Stitches), Panda CSS.
- **Trade-offs:** HTML noise; mitigated with component extraction.
- **Recommendation:** **Keep**, pair with **shadcn/ui + Radix primitives** for accessible components.

### 1.4 Charts / Viz

- **Proposed addition:** Recharts (general charts), **react-konva** or **PixiJS** for pitch playback overlay, **deck.gl** if we layer heatmaps in 2D/3D.
- **Recommendation:** Recharts + react-konva for v1.

---

## 2. Backend

### 2.1 FastAPI

- **Why it fits:** ASGI async, Pydantic v2, auto OpenAPI, great DX, ideal for streaming SSE.
- **Alternatives:** Litestar (faster startup, similar ergonomics), Django REST Framework (heavier, ORM-coupled), Flask (mature but synchronous), Node/NestJS (ecosystem split).
- **Trade-offs:** Async correctness requires discipline; type checking with Pydantic v2 is strict.
- **Recommendation:** **Keep FastAPI.** Consider Litestar only if we hit FastAPI's limits.

### 2.2 Python 3.11+

- **Why it fits:** ML/CV ecosystem, type hints mature, performance improvements continuing.
- **Recommendation:** **Keep**, target 3.11 minimum; test on 3.12.

### 2.3 Pydantic v2

- **Why it fits:** Rust-backed, fast, ergonomic; backbone of FastAPI.
- **Recommendation:** **Keep** + `pydantic-settings` for config.

### 2.4 SQLAlchemy 2.x + Alembic

- **Why it fits:** Battle-tested ORM, async support, parameterised queries by default.
- **Alternatives:** SQLModel (thin layer over SQLAlchemy + Pydantic), Tortoise ORM, raw asyncpg.
- **Recommendation:** **SQLAlchemy 2.x async + Alembic.** SQLModel is fine but we'll outgrow it.

### 2.5 Task Queue

- **Proposed:** Celery + Redis.
- **Alternatives:**
  - **RQ** — simple, Python-native.
  - **Arq** — async-native, fits asyncio.
  - **Dramatiq** — modern, ergonomic, sane defaults.
- **CHANGE PROPOSED:** Consider **Dramatiq** or **Arq** instead of Celery. Celery is heavy and old; both alternatives ship with better DX, better async support, and less arcane config. Decision tracked as ADR-0001.
- **Recommendation:** **Dramatiq + Redis** as primary candidate; Celery as fallback if a library only supports it.

---

## 3. Database

### 3.1 PostgreSQL 16

- **Why it fits:** Relational integrity, JSONB for flexible payloads, pgvector for embeddings, full-text search.
- **Alternatives:** MySQL, CockroachDB, MongoDB (rejected — relational data dominates).
- **Recommendation:** **Keep.** Single store for OLTP + vectors + JSONB.

### 3.2 Vector Store

- **Proposed:** pgvector inside Postgres.
- **Alternatives:** Qdrant (dedicated, HNSW, filters), Weaviate, Milvus, Pinecone (hosted).
- **Trade-offs:** pgvector keeps the stack simple; dedicated stores scale further.
- **Recommendation:** **pgvector for v1**, design an abstraction so we can swap to Qdrant if recall / latency degrades.

### 3.3 Cache & Queue Broker

- **Proposed:** Redis 7.
- **Recommendation:** **Keep**, use Redis Streams + RDB persistence in prod.

### 3.4 Object Storage

- **Proposed addition:** **MinIO** locally, **S3 / Cloudflare R2** in prod.
- **Recommendation:** Add now — required from Phase 5.

---

## 4. AI Agents

### 4.1 LangGraph

- **Why it fits:** State graphs over LLMs, persistence hooks, visualisation, integrates with LangChain tools.
- **Alternatives:**
  - **CrewAI** — role-based abstractions, less control.
  - **AutoGen / AG2** — conversation-driven, multi-agent loops, good for research-y flows.
  - **Plain orchestration** — hand-rolled state machine + LLM calls.
  - **LlamaIndex Workflows** — event-driven workflows.
- **Trade-offs:** LangGraph couples us to the LangChain ecosystem; abstraction tax is real but manageable.
- **Recommendation:** **Keep LangGraph** for v1 — explicit graphs map well to our orchestrator + specialists topology and make ADRs visual.

### 4.2 LLM Provider

- **Proposed:** Gemini or OpenAI (configurable).
- **Alternatives:** Anthropic Claude (often strongest reasoning + tool use), Mistral Large, OSS local (Llama 3.x / Qwen via Ollama or vLLM).
- **Trade-offs:** Cost, latency, tool-use reliability, region availability.
- **CHANGE PROPOSED:** Architect as a provider-agnostic adapter (one interface, multiple backends). Default to **Gemini Flash 2.x for routing / cheap calls** and **Claude Sonnet or GPT-4o for synthesis / report generation**. Ship a local fallback via Ollama for demos without an API key.

### 4.3 Embeddings

- **Proposed addition:** **sentence-transformers** (`all-MiniLM-L6-v2` or `bge-small-en-v1.5`) locally.
- **Trade-offs:** Free + offline vs slightly lower quality than hosted embeddings.
- **Recommendation:** Local for v1; switch to hosted if recall is insufficient.

---

## 5. Machine Learning

### 5.1 scikit-learn

- **Why it fits:** Pipelines, preprocessing, baselines, calibration.
- **Recommendation:** **Keep.**

### 5.2 XGBoost

- **Why it fits:** Strong tabular performance; SHAP TreeExplainer first-class.
- **Recommendation:** **Keep**, but benchmark vs LightGBM and CatBoost.

### 5.3 LightGBM

- **Why it fits:** Faster training, lower memory, often equal or better on sports data.
- **Recommendation:** **Keep** as a parallel candidate; pick per-task by holdout metrics.

### 5.4 SHAP

- **Why it fits:** Industry-standard explainability.
- **Recommendation:** **Keep.** Consider also LIME for instance-level alternatives in the report (nice-to-have).

### 5.5 Experiment Tracking

- **Proposed addition:** **MLflow** for tracking + model registry.
- **Alternatives:** Weights & Biases (hosted, fantastic UX), DVC (data + experiments), Neptune.
- **Recommendation:** **MLflow** self-hosted (free, local-first).

### 5.6 Feature Store

- **Proposed addition:** Parquet + a thin Python layer for v1 (avoid full Feast).
- **Recommendation:** Defer Feast until features are reused across ≥ 3 models.

---

## 6. Computer Vision

### 6.1 YOLOv11

- **Why it fits:** State of the art; player + ball detection with strong OOTB performance.
- **Alternatives:** YOLOv8 (mature, more docs), RT-DETR (transformer-based), Detectron2 (research-friendly).
- **Recommendation:** **Start with YOLOv11**; fall back to YOLOv8 if Ultralytics' v11 toolchain proves unstable on our hardware.

### 6.2 OpenCV

- **Recommendation:** **Keep.** Add `decord` or `PyAV` for faster video decode where bottlenecked.

### 6.3 DeepSORT

- **Why it fits:** Mature MOT with appearance features.
- **Alternatives:** **ByteTrack** (often beats DeepSORT on crowded scenes, simpler), **StrongSORT** (DeepSORT++), **OC-SORT**, **BoT-SORT**.
- **CHANGE PROPOSED:** Implement a `Tracker` interface and **bench ByteTrack vs DeepSORT** on validation clips. Ship the winner. Don't pre-commit to DeepSORT.

### 6.4 Re-ID / Jersey OCR

- **Proposed addition:** Optional jersey-number OCR (PaddleOCR) for ID stabilisation.
- **Recommendation:** Stretch; add if ID switches remain high after tracker work.

### 6.5 Homography / Pitch Calibration

- **Recommendation:** Manual 4-point calibration in UI for v1; explore automatic line-detection / TVCalib later.

---

## 7. DevOps

### 7.1 Docker + Docker Compose

- **Recommendation:** **Keep.** Add **`uv`** for fast Python image builds.

### 7.2 CI/CD

- **Proposed addition:** GitHub Actions (free for public, fits this stack).
- **Recommendation:** GitHub Actions; consider Dagger or Earthly later for portable pipelines.

### 7.3 Reverse Proxy

- **Proposed addition:** Nginx or **Caddy** (Caddy gives automatic HTTPS).
- **Recommendation:** **Caddy in prod** for free Let's Encrypt; Nginx in dev compose.

### 7.4 Observability Stack

- **Proposed addition:** Prometheus + Grafana + Loki + Tempo + OpenTelemetry; Sentry for errors.
- **Recommendation:** Lightweight v1: Prometheus + Grafana + Sentry. Loki / Tempo if logs / traces volume warrants.

### 7.5 Kubernetes

- **Recommendation:** **Defer.** Single VM + Docker Compose ships v1. Helm charts come post-MVP.

---

## 8. Version Control

### 8.1 Git + GitHub

- **Recommendation:** **Keep.** Trunk-based with short-lived feature branches (see `GIT_STRATEGY.md`).

---

## 9. Proposed Additions Summary

| Addition | Why |
| --- | --- |
| Vite | Fast dev server, modern bundler |
| TanStack Query | Server-state cache, dedup, retries |
| Zustand | Tiny client-state for non-server state |
| shadcn/ui + Radix | Accessible components |
| Dramatiq (or Arq) | Replace Celery for cleaner async DX |
| MinIO (dev) + S3/R2 (prod) | First-class artifact store |
| MLflow | Experiment tracking + model registry |
| pgvector | Embeddings inside Postgres |
| sentence-transformers | Free local embeddings |
| Caddy | Auto-HTTPS in prod |
| OpenTelemetry | Traces across services |
| Sentry | FE + BE error capture |
| `uv` / Poetry | Reproducible Python envs (pick one; `uv` recommended) |

---

## 10. Proposed Changes Summary

| From | To | Why |
| --- | --- | --- |
| Celery | **Dramatiq** (or Arq) | Less ceremony, better async story |
| LLM = Gemini OR OpenAI | **Provider-agnostic adapter** with Gemini Flash for routing + a stronger model for synthesis; Ollama fallback | Cost control + portability |
| Tracker = DeepSORT (fixed) | **`Tracker` interface; bench DeepSORT vs ByteTrack** | Don't lock in before evidence |
| Nginx (only) | **Caddy in prod**, Nginx in dev | Free auto-HTTPS, less config |

---

## 11. Open Decisions (need approval before Phase 2)

1. **ADR-0001** — Task queue (Dramatiq vs Celery).
2. **ADR-0002** — LLM provider strategy (multi-provider adapter + defaults).
3. **ADR-0003** — Tracker (DeepSORT vs ByteTrack via interface).
4. **ADR-0004** — Vector store (pgvector vs Qdrant) — pgvector default.
5. **ADR-0005** — Reverse proxy (Caddy vs Nginx).
6. **ADR-0006** — Python env manager (`uv` vs Poetry).

Each will live under `docs/adr/` once the planning gate is passed.
