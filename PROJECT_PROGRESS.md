# Project Progress — PitchMind AI

**Last Updated:** 2026-06-15
**Current Phase:** Phase 1 — Project Setup

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
| 1 | Project Setup | 🟡 In Progress | 2026-06-15 | — |
| 2 | Backend Foundation | ⬜ Not Started | — | — |
| 3 | Frontend Foundation | ⬜ Not Started | — | — |
| 4 | Database Design | ⬜ Not Started | — | — |
| 5 | Video Upload Pipeline | ⬜ Not Started | — | — |
| 6 | Computer Vision Engine | ⬜ Not Started | — | — |
| 7 | Player Tracking | ⬜ Not Started | — | — |
| 8 | Heatmaps & Analytics | ⬜ Not Started | — | — |
| 9 | Match Outcome Prediction | ⬜ Not Started | — | — |
| 10 | Injury Risk Prediction | ⬜ Not Started | — | — |
| 11 | Scouting Engine | ⬜ Not Started | — | — |
| 12 | LangGraph Agent System | ⬜ Not Started | — | — |
| 13 | Dashboard Integration | ⬜ Not Started | — | — |
| 14 | Testing & Hardening | ⬜ Not Started | — | — |
| 15 | Deployment | ⬜ Not Started | — | — |

---

## Completed Tasks

- [x] PRD.md created
- [x] SRS.md created
- [x] ARCHITECTURE.md created
- [x] TECH_REVIEW.md created
- [x] FOLDER_STRUCTURE.md created
- [x] ROADMAP.md created
- [x] GIT_STRATEGY.md created
- [x] FEATURES.md created
- [x] EVALUATION.md created
- [x] PROJECT_PROGRESS.md created (this file)
- [x] TODO.md created
- [x] CHANGELOG.md created
- [x] README.md created

---

## Pending Tasks

- [ ] User reviews and approves planning documents
- [ ] Git identity confirmed and recorded above
- [ ] ADR-0001 through ADR-0006 decisions resolved
- [ ] Phase 1 kickoff

---

## Open ADRs (decisions needed before Phase 2)

| ID | Topic | Decision | Status |
| --- | --- | --- | --- |
| ADR-0001 | Task queue | **Dramatiq + Redis** | ✅ Resolved 2026-06-15 |
| ADR-0002 | LLM provider strategy | **Multi-provider adapter; Gemini Flash for routing, Claude/GPT-4o for synthesis, Ollama fallback** | ✅ Resolved 2026-06-15 |
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

---

## Technical Debt

None yet — project has not started implementation.

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

---

## Risk Register (live)

| ID | Risk | Status | Notes |
| --- | --- | --- | --- |
| T1 | YOLOv11 ID-switch rate | Open | Mitigation: ByteTrack + jersey OCR |
| T5 | CUDA / driver mismatch | Open | Pin CUDA base image in Phase 1 |
| P1 | Scope creep | Open | Phase-gate acceptance criteria |
| P3 | LLM cost runaway | Open | Per-run budget enforced in Phase 12 |
| B1 | Injury model misuse | Open | Disclaimer + admin gate |

---

## Milestones

| Tag | Status | Date |
| --- | --- | --- |
| Planning docs complete | ✅ Done | 2026-06-15 |
| Initial commit pushed to GitHub | ✅ Done | 2026-06-15 |
| `v0.1.0` (Phases 1 – 4) | ⬜ Not started | — |
| `v0.2.0` (Phases 5 – 7) | ⬜ Not started | — |
| `v0.3.0` (MVP path) | ⬜ Not started | — |
| `v1.0.0` MVP launch | ⬜ Not started | — |

## Repository

- **GitHub:** https://github.com/Pranshu0722/pitchmind-ai
- **Default branch:** main
