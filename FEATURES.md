# Innovation & Features Backlog — PitchMind AI

**Version:** 0.1 (Planning)
**Status:** Draft — awaiting approval

This document proposes features **beyond** the MVP and post-MVP scope already in `PRD.md`. Each entry includes:

- **Description**
- **Complexity** (S / M / L / XL)
- **Resume Impact Score** (1 – 10)
- **Business Value**
- **Development Effort** (rough estimate in engineer-weeks)

Pull from this backlog when MVP ships.

---

## 1. Ten Additional Features

### F1. Pitch Control Surface (Spearman-style)

- **Description:** Compute pitch-control probability for every point on the pitch over time. Visualised as a heatmap-over-time and used by the Tactical agent for spatial dominance analysis.
- **Complexity:** L
- **Resume Impact:** 9
- **Business Value:** High — this is the kind of analytics elite clubs pay six figures for.
- **Effort:** 3 weeks.

### F2. Expected Threat (xT) Grid

- **Description:** Map pitch zones to expected-threat values from tracking-derived possession sequences.
- **Complexity:** M
- **Resume Impact:** 8
- **Business Value:** High — strong narrative metric for content + scouting.
- **Effort:** 2 weeks.

### F3. Pass Network Reconstruction

- **Description:** Infer passes from tracking + ball proximity transitions; build a per-team pass network with centralities and weak links.
- **Complexity:** M
- **Resume Impact:** 8
- **Business Value:** High — staple of tactical analysis.
- **Effort:** 2 weeks.

### F4. Set-Piece Detector & Library

- **Description:** Detect corners, free kicks, throw-ins; cluster patterns; build a per-team set-piece library.
- **Complexity:** L
- **Resume Impact:** 8
- **Business Value:** High — set pieces decide ~30% of goals.
- **Effort:** 3 weeks.

### F5. Auto Highlights Reel

- **Description:** Detect goals / shots / big chances / cards and auto-cut a highlight reel (ffmpeg + simple scoring model).
- **Complexity:** M
- **Resume Impact:** 7
- **Business Value:** High — viral hook; content creators love it.
- **Effort:** 2 weeks.

### F6. Coach-Style Voice Briefings

- **Description:** Convert the agent's match report to audio using a TTS model. Optional voice-clone of a coach reading their own report.
- **Complexity:** M
- **Resume Impact:** 7
- **Business Value:** Medium — differentiated UX.
- **Effort:** 1 – 2 weeks.

### F7. Tactical Animation Studio

- **Description:** Replay any sequence on a 2D pitch with movable players; coaches can author drills referencing real events.
- **Complexity:** L
- **Resume Impact:** 8
- **Business Value:** High — coaching-tool stickiness.
- **Effort:** 3 weeks.

### F8. Multi-Match Comparison

- **Description:** Compare two or more matches (e.g., same team across opponents) with diffed metrics and an agent-authored narrative.
- **Complexity:** M
- **Resume Impact:** 7
- **Business Value:** Medium-high.
- **Effort:** 2 weeks.

### F9. Real-Time Live Mode

- **Description:** RTMP / WebRTC ingest with streaming detection; partial results render live; agent answers questions about the match-in-progress.
- **Complexity:** XL
- **Resume Impact:** 10
- **Business Value:** Very high; opens live-coaching market.
- **Effort:** 6 – 8 weeks.

### F10. Mobile Companion App

- **Description:** React Native (or Expo) app for upload-from-phone, push notifications when reports are ready, and quick chat with the agent.
- **Complexity:** L
- **Resume Impact:** 8
- **Business Value:** High — surface where the user actually is.
- **Effort:** 4 weeks.

---

## 2. Five Additional AI / Agent Features

### A1. Tool-Using Multi-Agent Debate

- **Description:** For ambiguous tactical questions, run Tactical vs Statistical agents in a brief debate moderated by Orchestrator; final answer cites both views.
- **Complexity:** L
- **Resume Impact:** 9
- **Effort:** 2 weeks.

### A2. Long-Term Match Memory via RAG

- **Description:** Embed every prior match's report; the agent recalls patterns ("this is the third match they conceded after losing midfield in the second half").
- **Complexity:** M
- **Resume Impact:** 8
- **Effort:** 2 weeks.

### A3. Coach-Style Personas

- **Description:** Selectable persona prompts (Klopp-style, Guardiola-style, Mourinho-style) modifying narrative style without changing data.
- **Complexity:** S
- **Resume Impact:** 7
- **Effort:** 0.5 week.

### A4. Self-Critique & Evaluation Loop

- **Description:** Reports are graded by an Evaluator agent against a rubric; failing reports trigger a rewrite. Metrics tracked over time.
- **Complexity:** M
- **Resume Impact:** 9
- **Effort:** 1 – 2 weeks.

### A5. Voice Q&A Assistant

- **Description:** Whisper-based STT + LLM + TTS — ask the agent tactical questions from your phone during training.
- **Complexity:** M
- **Resume Impact:** 8
- **Effort:** 2 weeks.

---

## 3. Five Additional Machine Learning Features

### M1. Expected Goals (xG) Model

- **Description:** Train an xG model from shot context (location, body part, defenders nearby — inferred from tracks).
- **Complexity:** M
- **Resume Impact:** 9
- **Effort:** 2 weeks.

### M2. Lineup-Strength / Squad-Value Estimator

- **Description:** Estimate a lineup's expected points contribution vs replacement, calibrated against historical results.
- **Complexity:** L
- **Resume Impact:** 8
- **Effort:** 3 weeks.

### M3. Style Embedding for Teams

- **Description:** Self-supervised embedding of team playing style from rolling possession + passing + pressing metrics; powers similarity ("this team plays like 2019 Atalanta").
- **Complexity:** L
- **Resume Impact:** 9
- **Effort:** 3 weeks.

### M4. Player Form Trajectory Forecast

- **Description:** Time-series model (Temporal Fusion Transformer or Prophet) forecasting per-player metrics over next N matches.
- **Complexity:** L
- **Resume Impact:** 8
- **Effort:** 3 weeks.

### M5. Causal Impact of Substitutions

- **Description:** Synthetic-control / uplift modelling on how a substitution changed possession / xT / pressing intensity vs a counterfactual.
- **Complexity:** L
- **Resume Impact:** 9 (rare on resumes; causal sells)
- **Effort:** 3 weeks.

---

## 4. Five Additional Computer Vision Features

### C1. Automatic Camera Calibration

- **Description:** Replace manual 4-point calibration with line + circle detection on pitch markings (TVCalib-style).
- **Complexity:** L
- **Resume Impact:** 9
- **Effort:** 3 weeks.

### C2. Jersey-Number OCR + Identity Anchor

- **Description:** Read jersey numbers with PaddleOCR or a CRNN; use numbers to stabilise track IDs across occlusions.
- **Complexity:** M
- **Resume Impact:** 8
- **Effort:** 2 weeks.

### C3. Pose Estimation per Player

- **Description:** Estimate per-player pose (e.g., RTMPose) for body-orientation, shot mechanics, and posture-based injury cues.
- **Complexity:** L
- **Resume Impact:** 9
- **Effort:** 3 weeks.

### C4. Event Spotting (Shot / Pass / Tackle)

- **Description:** Temporal action localisation on broadcast footage (SoccerNet-v2-style).
- **Complexity:** L
- **Resume Impact:** 9
- **Effort:** 3 – 4 weeks.

### C5. Crowd / Stadium Augmentation Removal

- **Description:** Robust detection that masks crowd false-positives (segment + filter) to reduce noise on tracking.
- **Complexity:** M
- **Resume Impact:** 7
- **Effort:** 1 – 2 weeks.

---

## 5. Five Recruiter-Impressive Features

### R1. Architectural Decision Records + Public Trade-offs Page

- **Description:** A `/docs/adr` directory and a public web page rendering ADRs. Sells engineering maturity.
- **Resume Impact:** 9
- **Effort:** 0.5 week.

### R2. Model Cards + Eval Harness

- **Description:** A published model card per model (purpose, data, metrics, limits) and a one-command evaluation script. Sells ML rigour.
- **Resume Impact:** 9
- **Effort:** 1 week.

### R3. Reproducible Benchmark Suite (CV + ML)

- **Description:** `make bench` runs tracker + outcome model on frozen fixtures and produces an HTML report. Sells discipline.
- **Resume Impact:** 9
- **Effort:** 1 week.

### R4. Public Demo with Live Sample Match

- **Description:** Hosted demo with one canonical match preloaded; visitors can run the agent without signing up.
- **Resume Impact:** 10 (recruiters need to *see* the work)
- **Effort:** 1 week.

### R5. Write-up & Architecture Talk

- **Description:** A long-form blog post + a 15-minute talk recording walking through the system design. Sells communication.
- **Resume Impact:** 10
- **Effort:** 1 week.

---

## 6. Five Startup / Productization Opportunities

### S1. SaaS for Academy Clubs

- **Pitch:** Wyscout-light at £29 / month / coach. Land-grab the gap below pro tools.
- **Defensibility:** Auto-report quality + model fine-tuning on academy footage.
- **Go-to-market:** Academy directors via LinkedIn + a free trial of one match.

### S2. White-Label Analytics for Federations

- **Pitch:** Per-federation deployment for women's leagues / lower divisions; co-branded reports.
- **Defensibility:** Data exclusivity contract + on-prem option.

### S3. Content Engine for Football Media

- **Pitch:** API that produces tactical breakdowns + highlight reels for content sites and bloggers.
- **Defensibility:** Cost per insight vs hiring an analyst.

### S4. Scouting-Lite for Agents

- **Pitch:** Player-agents pay per opponent / prospect report. Lower-end than Transfermarkt's pro tier.
- **Defensibility:** Similarity engine + filterable feed.

### S5. Coaching Education Platform

- **Pitch:** Bundle the agent + reports with curriculum: "analyse your own training session" courses for UEFA B / A licence candidates.
- **Defensibility:** Curriculum + community; courses gate the toolset.

---

## 7. Prioritisation Heuristic

Score each candidate post-MVP feature:

```
priority = 0.4 * resume_impact + 0.4 * business_value + 0.2 * (10 - complexity_weeks)
```

Top 3 from this backlog by that score (illustrative):

1. **F1 Pitch Control** (resume 9 · value 9 · ~3 wk)
2. **C1 Auto Calibration** (resume 9 · value 8 · ~3 wk)
3. **M1 xG Model** (resume 9 · value 8 · ~2 wk)

These should be Phase 16+ candidates after MVP ships.
