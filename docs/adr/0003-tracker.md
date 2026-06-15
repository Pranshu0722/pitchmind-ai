# ADR-0003: Object Tracker — Interface First, Evidence-Based Selection

**Date:** 2026-06-15
**Status:** Accepted
**Deciders:** Pranshu0722

---

## Context

Multi-object tracking (MOT) assigns persistent IDs to detected players across frames. Tracker choice significantly affects downstream metric quality (heatmaps, distance, sprint counts). Two leading open-source trackers are DeepSORT and ByteTrack.

## Decision

Define a **`Tracker` protocol** in `backend/src/pitchmind/cv/trackers/base.py`. Implement both **DeepSORT** and **ByteTrack**. Benchmark both on a held-out annotated validation set using HOTA and MOTA; ship the one with better HOTA as the default.

## Alternatives Considered

| Option | Pros | Cons |
| --- | --- | --- |
| DeepSORT (fixed) | Mature; re-ID features help identity through occlusion | Slower; appearance model adds GPU overhead |
| ByteTrack (fixed) | Often beats DeepSORT on crowded scenes; faster; no re-ID model | Less robust for identity through long occlusion |
| StrongSORT | DeepSORT++ with improvements | Higher complexity; maintenance burden |
| **Interface + bench** | Evidence-based; swappable later | 2× implementation cost upfront |

## Consequences

**Positive:**
- Not locked in before we have evidence.
- Swapping tracker is a one-line config change post-decision.
- Eval harness becomes a permanent CI benchmark.

**Negative / Trade-offs:**
- Extra implementation work for the losing tracker (but it stays as a selectable fallback).

**Risks:**
- Benchmark clips may not represent all real-world footage; decision may need revisiting.

## Follow-up

- [ ] Implement `Tracker` protocol (Phase 7).
- [ ] Implement `DeepSORTTracker` and `ByteTrackTracker`.
- [ ] Run `scripts/eval_tracker.py` on validation clips and record HOTA / MOTA in `docs/models/tracker_eval.md`.
- [ ] Set default via `CV_TRACKER` env var.
