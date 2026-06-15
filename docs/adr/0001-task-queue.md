# ADR-0001: Task Queue — Dramatiq + Redis

**Date:** 2026-06-15
**Status:** Accepted
**Deciders:** Pranshu0722

---

## Context

Long-running CV and ML jobs (up to 30 min per match) must execute off the HTTP request thread. We need a reliable task queue with async support, dead-letter handling, retry policies, and observability hooks.

Candidates evaluated: Celery, Dramatiq, Arq, RQ.

## Decision

Use **Dramatiq** as the task broker with **Redis** as the backend.

## Alternatives Considered

| Option | Pros | Cons |
| --- | --- | --- |
| Celery + Redis | Most widely used; huge ecosystem; battle-tested | Complex config; legacy synchronous design; arcane debugging |
| **Dramatiq + Redis** | Clean API; async-first; sane defaults; built-in retries + dead-letter | Smaller community than Celery |
| Arq + Redis | Fully async (asyncio-native); lightweight | Very minimal; fewer built-in primitives |
| RQ + Redis | Simple; Pythonic | No priority queues; limited retry control |

## Consequences

**Positive:**
- Clean `@dramatiq.actor` decorator API.
- Built-in retry with exponential backoff and dead-letter queue.
- Redis backend we already run for caching.
- Easy to swap broker to RabbitMQ later without changing actor code.

**Negative / Trade-offs:**
- Smaller community means fewer Stack Overflow answers.
- Some third-party integrations (e.g. Flower-equivalent) require `dramatiq-dashboard`.

**Risks:**
- If a library strictly requires Celery, we'll need an adapter layer.

## Follow-up

- [ ] Pin `dramatiq[redis]` in `backend/pyproject.toml` (Phase 2).
- [ ] Add `dramatiq-dashboard` for job monitoring (Phase 2).
- [ ] Define retry policy constants in `backend/src/pitchmind/queue/broker.py`.
