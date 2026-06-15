# Product Requirements Document — PitchMind AI

**Version:** 0.1 (Planning)
**Owner:** Product / Tech Lead
**Status:** Draft — awaiting approval

---

## 1. Vision

PitchMind AI is an end-to-end football intelligence platform that transforms raw match video into structured, explainable, decision-ready insight. We unify three capabilities that traditionally live in separate, expensive enterprise tools:

1. **Sports computer vision** — player + ball detection and tracking from broadcast or tactical-camera footage.
2. **Predictive analytics** — match outcomes, injury risk, and player similarity using classical ML with explainability.
3. **Agentic reasoning** — a LangGraph multi-agent system that interprets the extracted signals and answers tactical questions in natural language.

We target a category between *Wyscout / StatsBomb* (data) and *Hudl / Veo* (video) — but consumer-priced, open-source-friendly, and AI-first.

---

## 2. Problem Statement

Football analytics today is fragmented:

- **Manual analysis** is time-expensive. A typical post-match breakdown takes a coaching staff 6–12 hours.
- **Pro-grade tools** (Wyscout, StatsBomb, Hudl Pro) cost £5k–£50k / year and are inaccessible to amateur, semi-pro, academy, women's, and grassroots clubs.
- **Existing video tools** show *what happened* but not *why*. They produce clips, not reasoning.
- **Predictive insight is locked away** inside betting models and elite-club data-science teams.

PitchMind AI's wager: a single video upload should produce both the numbers *and* a coach-grade tactical narrative within minutes.

---

## 3. Target Users

### 3.1 Primary Personas

| Persona | Role | Pain Point | What PitchMind Gives Them |
| --- | --- | --- | --- |
| **Carla — Academy Coach** | Coaches U17 squad, no analyst budget | Hours of weekend tagging | Auto heatmaps + tactical report by Monday training |
| **Marco — Semi-Pro Analyst** | One-person video department | Stitching stats from 5 tools | Single dashboard with stats + agent Q&A |
| **Priya — Independent Scout** | Tracks 200+ players | Cannot pre-filter video | Similarity search + auto scouting brief |
| **Tom — Fantasy / Content Creator** | Builds content from match footage | Needs differentiated insight | Predictions + auto-generated highlight commentary |
| **Dr. Lin — Sports Scientist** | Manages player workload | Injury risk is heuristic | Quantified injury-risk score per player |

### 3.2 Secondary Personas

- Football clubs evaluating in-house tooling.
- Recruiters & hiring managers evaluating the project for the engineer who built it (portfolio dimension).

---

## 4. User Stories (MoSCoW)

### Must Have — MVP

1. As a coach, I can upload a match video (MP4, up to 90 min, ≤ 4 GB) and receive a processing-status indicator.
2. As an analyst, I can see player and ball detections rendered on a sample frame.
3. As an analyst, I can view a heatmap per player and per team.
4. As a coach, I can read match statistics (possession proxy, distance covered, sprint count, formation guess).
5. As a coach, I can ask a tactical-analysis agent "Why did we lose midfield in the second half?" and get a grounded answer.
6. As any user, I can log in, browse my uploads, and see per-match dashboards.

### Should Have — Post-MVP

7. As a manager, I can request a match-outcome prediction with win/draw/loss probabilities and SHAP feature attribution.
8. As a sports scientist, I can see injury-risk scores per player with drivers.
9. As a scout, I can query "find me a left-footed inverted winger like Player X under £5m" and get ranked candidates.
10. As a power user, I can chat with a multi-agent assistant that routes between Vision, Tactical, Stats, Prediction, Injury, and Scout agents.

### Could Have

11. Real-time RTMP ingest.
12. Mobile companion app.
13. Multi-language reports.

### Won't Have (v1)

- Live broadcast overlay.
- Refereeing decision review (VAR-style).
- Betting-line generation (legal exposure).

---

## 5. Functional Scope (Summary)

Detailed FRs live in `SRS.md`. High-level:

- **F1. Auth & Tenancy** — email + OAuth, JWT sessions, per-user workspaces.
- **F2. Video Ingest** — upload, validate, chunked transfer, S3-compatible storage, virus scan, thumbnailing.
- **F3. CV Pipeline** — frame sampling → detection (YOLOv11) → tracking (DeepSORT/ByteTrack) → homography → metrics.
- **F4. Analytics** — heatmaps, possession, formations, pass network proxy, distance, sprints.
- **F5. ML Models** — match outcome, injury risk, player similarity / scouting.
- **F6. Agent Layer** — LangGraph orchestrator + specialist agents over the extracted state.
- **F7. Dashboard** — match overview, per-player drilldowns, agent chat, reports.
- **F8. Reporting** — PDF / shareable link export of agent-generated match report.
- **F9. Admin & Observability** — job monitor, retry, model registry, audit log.

---

## 6. Non-Functional Targets (Summary)

Detailed NFRs live in `SRS.md`. Headline targets:

- A 90-minute 1080p video produces a full analytics pack in **≤ 30 minutes** on a single mid-range GPU (RTX 3060-class).
- Dashboard p95 page load **≤ 2 s** on broadband.
- Agent first-token latency **≤ 3 s**; full response **≤ 15 s** for typical tactical questions.
- 99.0% job-completion success rate (excluding malformed input).
- Pipeline must be **deterministic enough** that the same input + same model versions yields identical metrics within ±2%.

---

## 7. Success Metrics

### Product Metrics

- Time-to-insight per match (target ≤ 30 min p50).
- % of uploads producing a complete report without manual retry (target ≥ 95%).
- Median tactical-question answer quality (rubric-scored by reviewers ≥ 4 / 5).

### Engineering / Portfolio Metrics

- Test coverage ≥ 80% on backend critical paths.
- All ML models tracked in MLflow with reproducible runs.
- Architecture diagrams + ADRs published in repo.
- One-command local boot (`docker compose up`) with seed match.

### Adoption Metrics (post-launch)

- 100 unique uploads in first 30 days of public beta.
- ≥ 30% week-2 retention among self-serve sign-ups.

---

## 8. Out of Scope (v1)

- Live RTMP / real-time inference.
- Refereeing / officiating review.
- Player tracking from drone footage.
- Real money / betting integration.
- Multi-tenant billing & enterprise SSO (planned post-launch).

---

## 9. Assumptions

- Input footage is broadcast-style or tactical-camera (single-view, panning).
- A single GPU is available in dev (8 – 12 GB VRAM).
- Public datasets (SoccerNet, StatsBomb Open Data, FBref scrapes) are sufficient to train and validate prediction models.
- The LLM provider (Gemini or OpenAI) is available with a budget cap configurable per environment.

---

## 10. Constraints

- **Cost ceiling (dev / personal):** ≤ £100 / month including LLM API and model storage.
- **Hardware ceiling (dev):** Single-GPU workstation; cloud bursting optional.
- **Legal / IP:** No use of broadcast footage we do not own a license to redistribute; all demo footage must be from open datasets or user uploads.
- **Privacy:** Player faces will not be used as a biometric identifier. Tracking is positional only.

---

## 11. Risks (top 5)

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| YOLOv11 accuracy on broadcast footage with occlusion | High | High | Fine-tune on SoccerNet; ByteTrack fallback; document accuracy envelope |
| LLM cost runaway in agent flow | Medium | High | Per-job token budget; cache; cheaper model for routing |
| Homography (pitch coordinates) brittle without calibration | High | Medium | Camera-model + manual 4-point calibration in UI |
| Scope creep beyond MVP | High | Medium | Strict gating on phase acceptance criteria |
| Synthetic / open data not representative for injury model | Medium | High | Ship as research-grade with clear disclaimers |

Full risk register lives in `EVALUATION.md`.

---

## 12. Release Plan

| Release | Content | Trigger |
| --- | --- | --- |
| **0.1 — Skeleton** | Phases 1 – 4 (setup, backend, frontend, DB) | Internal |
| **0.2 — CV Alpha** | Phases 5 – 7 (upload, CV, tracking) | Internal demo |
| **0.3 — Insights Alpha** | Phases 8, 12, 13 (heatmaps, agent, dashboard) | First external user |
| **1.0 — MVP** | All MVP capabilities working end-to-end | Public portfolio launch |
| **1.x — Predictive** | Phases 9 – 11 (prediction, injury, scout) | Post-MVP iteration |

---

## 13. Open Questions

1. LLM choice — Gemini Flash 2.x vs OpenAI GPT-4o-mini vs OSS (Llama 3.x)? Decision tracked in `TECH_REVIEW.md`.
2. Do we need a vector DB (pgvector vs Qdrant) for player-similarity search?
3. Are we shipping a hosted demo or local-only for v1?
4. Multi-tenant from day 1 or single-user-then-refactor?

These are flagged in `TODO.md` for resolution before Phase 2.
