# Project Evaluation — PitchMind AI

**Version:** 0.2 (Active)
**Status:** Approved — updated as implementation progresses

---

## 1. Scoring Matrix (1 – 10)

| Dimension | Score | Rationale |
| --- | --- | --- |
| **Technical Depth** | 9 | Full async backend, typed CV/ML/agent pipelines, custom tracker interface, SHAP explainability, pgvector, OTEL |
| **AI Sophistication** | 9 | LangGraph multi-agent with orchestrator, typed tool registry, provider-agnostic LLM adapter, per-run cost guardrails, adversarial safeguards |
| **ML Sophistication** | 8 | Three distinct models (outcome, injury, similarity), SHAP explainability, time-respecting CV, calibration, MLflow registry, model cards |
| **Computer Vision Depth** | 8 | YOLOv11 fine-tuning, swappable tracker interface (DeepSORT / ByteTrack), team assignment, homography, HOTA evaluation harness |
| **Software Engineering Quality** | 9 | SOLID + clean architecture, strict types (mypy + TS), ADRs, pre-commit hooks, contract tests, load tests, structured logging, OTEL, Sentry |
| **System Design** | 9 | Six-service decomposition, async worker separation by resource profile, stateless API tier, pluggable storage / queue / LLM, reproducible runs |
| **Resume Impact** | 9 | End-to-end full-stack + CV + ML + Agents; quantified eval harnesses; ADRs; model cards; public demo planned |
| **Recruiter Appeal** | 9 | Tangible domain (football), visual outputs (heatmaps, pitch), live chat demo, architecture diagrams, write-up planned |
| **Portfolio Value** | 9 | Production-quality structure; not a tutorial clone; benchmarks + model cards make claims defensible in interviews |
| **Startup Potential** | 8 | Concrete SaaS opportunities (academy clubs, federation white-label, content API); gap between Wyscout and nothing is real |

**Total (average):** **8.7 / 10**

---

## 2. Weaknesses

### W1. Computer Vision Accuracy on Real Broadcast Footage
YOLOv11 OOTB is not fine-tuned for football. Occlusion, pitch-side advertising boards, and variable camera angles will degrade detection. Without a robust fine-tuning dataset and a proper HOTA benchmark the tracking quality claims are aspirational. This is the single highest-risk technical assumption in the project.

**Mitigation:** Fine-tune on SoccerNet; publish HOTA numbers; be explicit about the accuracy envelope in the UI.

### W2. Homography is Manual and Brittle
The 4-point calibration requires the user to click on known pitch landmarks. If the camera pans too far or doesn't show all four landmarks, calibration fails. All pitch-coordinate metrics (distance, heatmap accuracy, pitch-control) depend on this.

**Mitigation:** Build robust calibration UX with live error preview; research automatic line-based calibration for Phase 16+.

### W3. Injury Model Has Thin, Non-Representative Training Data
Open, labelled injury-occurrence datasets tied to workload metrics are extremely scarce. The model will likely be under-powered and uncalibrated on out-of-distribution players. Misrepresenting it as production-grade injury prediction is harmful.

**Mitigation:** Ship with a clear "research grade — not for medical or contractual decisions" disclaimer; gates in admin layer.

### W4. LLM Agent Reliability Degrades with Tool-Use Depth
Deep agentic chains are notoriously prone to hallucination, tool-call loop failures, and cost blow-up. The more specialist agents we chain, the more failure modes compound.

**Mitigation:** Strict schema validation on every tool output; per-run token budget; unit tests for routing; red-team adversarial prompts.

### W5. Single-GPU Dev Environment May Not Reflect Scale
Development on a single RTX 3060 GPU shapes design decisions that may not hold at scale (batch sizes, memory layouts, model precision). Scaling to multi-GPU or TPU workers will require revisiting these assumptions.

**Mitigation:** Design the CV worker interface with a `batch_size` / `device` config from day 1; document scaling notes in the architecture.

---

## 3. Risks

### Technical Risks

| ID | Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- | --- |
| T1 | YOLOv11 ID-switch rate unacceptably high on crowded scenes | High | High | ByteTrack fallback; StrongSORT evaluation; jersey OCR for anchoring |
| T2 | Homography fails on wide-angle / fisheye tactical cameras | Medium | High | Manual calibration UX; camera profile library |
| T3 | LLM provider API downtime blocks agent flow | Medium | High | Multi-provider adapter; offline fallback to local Ollama |
| T4 | pgvector recall insufficient for scout similarity at scale | Low | Medium | Design abstraction layer; Qdrant migration path documented |
| T5 | CUDA / driver version mismatch in Docker container | High | Medium | Pin CUDA base image; test matrix in CI |
| T6 | ffprobe / OpenCV decode bottleneck on 4K footage | Medium | Medium | `decord` / `PyAV` as accelerated alternative |

### Project / Scope Risks

| ID | Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- | --- |
| P1 | Scope creep beyond MVP before v1 ships | High | High | Strict phase-gate acceptance criteria; `FEATURES.md` as the parking lot |
| P2 | Open dataset quality insufficient for outcome model | Medium | High | Supplement with FBref scraping; document limitations |
| P3 | LLM cost runaway during testing / demo | Medium | High | Per-run budget enforced; dev-mode cost caps |
| P4 | Open-source licence incompatibility (CV models, data) | Low | High | Audit licences in Phase 1; document in TECH_REVIEW |

### Business / Ethical Risks

| ID | Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- | --- |
| B1 | Injury model used for contract / selection decisions | Low | Very High | Explicit disclaimer; admin gate; no claim of medical validity |
| B2 | Broadcast footage uploaded without rights | Medium | Medium | ToS requiring user owns the footage; no re-distribution |
| B3 | Player face biometrics legal exposure | Low | High | Tracking is positional only; no face matching |

---

## 4. Missing Features (before v1 can claim completeness)

| Gap | Priority | Notes |
| --- | --- | --- |
| Automatic camera calibration | Should have post-MVP | Manual calibration is a UX friction point that will cause abandonment |
| Pass network inference | Should have | Foundational tactical metric; currently deferred |
| Expected goals (xG) | Should have | Standard metric; expected by any analyst |
| Event detection (shot / tackle / corner) | Nice to have | Needed for highlights + event-anchored chat |
| Multi-language reports | Nice to have | Limits adoption outside English-speaking markets |
| Player face blur / privacy filter | Should have | Legal risk mitigation on footage with crowd |

---

## 5. Recommended Improvements

### R1. Prioritise Automatic Homography (Phase 16+)
Manual calibration is the biggest friction point for new users. Implementing TVCalib or pitch-line detection would remove the single biggest blocker to a frictionless first-run experience.

### R2. Add Pass Network to MVP Scope
A pass network (edges between player positions weighted by connection frequency) is simple to derive from tracking data and is a visual centrepiece that recruiters immediately understand. Move it from the backlog into Phase 8.

### R3. Ship xG as Phase 9a (Parallel to Outcome Model)
xG is a simpler model, uses the same feature pipeline as the outcome model, and provides a compelling standalone metric. It can be shipped in 2 weeks alongside Phase 9.

### R4. Build the Benchmark Page as a Public URL
`/docs/performance` showing live HOTA + log-loss + AUC numbers from the last CI run is a differentiator in interviews and recruiter evaluations. Cost: 0.5 week.

### R5. Record a 5-Minute Demo Video Before Any Job Application
The system is complex; nobody will trace it through the README. A screen-recorded walkthrough (upload → run → chat → report) is the highest-ROI action relative to interview preparation.

### R6. Consider Anthropic Claude as the Primary Strong Model
Given Claude's strong structured tool-use (function calling, JSON mode), long context window, and low hallucination rate on constrained tasks, using Claude Sonnet or Haiku as the synthesis model in the agent layer would likely improve report quality over GPT-4o-mini. The provider-agnostic adapter makes this a one-line config change.

---

## 6. Comparison to Alternatives in the Portfolio Landscape

| Project Type | Complexity | AI Depth | Differentiation vs PitchMind AI |
| --- | --- | --- | --- |
| Todo app + GPT | Very low | Very low | Not comparable |
| RAG chatbot | Low | Medium | No CV, no ML models, no domain specificity |
| Generic recommendation system | Medium | Medium | No real-time media processing, no agents |
| Kaggle comp notebook | Medium | Medium | No deployment, no system design |
| **PitchMind AI** | **Very High** | **Very High** | Full stack: CV + ML + Agents + API + Dashboard + deploy |

PitchMind AI sits in a rarified category: less than 5% of portfolio projects demonstrate end-to-end integration of real-time CV, multi-model ML, and production-grade agentic AI within a single coherent product.

---

## 7. Final Recommendation

Build it. The combination of computer vision, ML, and agentic AI in a tangible, visually rich domain (football) is compelling for:

- Senior engineer / ML engineer / AI engineer job applications at FAANG, sports tech, betting, media.
- Startup fundraising (real problem, real gap in market).
- Technical talks and blog content.

The only risk to portfolio value is **shipping something incomplete**. The phase-gate approach in `ROADMAP.md` is designed to ensure that even if post-MVP phases never arrive, `v1.0.0` is a working, defensible, impressive product.
