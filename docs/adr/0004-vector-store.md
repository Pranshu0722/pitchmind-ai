# ADR-0004: Vector Store — pgvector (with Qdrant migration path)

**Date:** 2026-06-15
**Status:** Accepted
**Deciders:** Pranshu0722

---

## Context

The scouting similarity engine and long-term agent memory require approximate nearest-neighbour (ANN) search over dense embeddings. We need a vector store that is production-capable, operationally simple, and fits our single-service budget.

## Decision

Use **pgvector** inside the existing PostgreSQL 17 instance. Abstract access behind a `VectorStore` protocol so migration to Qdrant is a one-service swap.

## Alternatives Considered

| Option | Pros | Cons |
| --- | --- | --- |
| **pgvector** | No new service; ACID transactions; SQL joins alongside vectors | Recall may lag dedicated stores at very large scale (>10M vectors) |
| Qdrant | High-performance HNSW; rich filtering; gRPC | New stateful service; operational overhead |
| Weaviate | Multi-modal; schema-based | Heavy; overkill for v1 |
| Pinecone | Managed; simple API | Cost; data leaves our infra |

## Consequences

**Positive:**
- One fewer service to operate.
- Player embeddings live in the same DB as player metadata — JOIN queries work.
- pgvector HNSW index on 10 k–100 k vectors performs well within p95 ≤ 300 ms target.

**Negative / Trade-offs:**
- At millions of vectors or with strict recall SLAs, we'll need to migrate.
- pgvector HNSW build time can be slow on cold start.

**Risks:**
- If recall is insufficient at 10 k players, we evaluate Qdrant immediately.

## Follow-up

- [ ] Enable `pgvector` extension in Alembic migration — deferred from Phase 4. Standalone PostgreSQL 17 does not ship with pgvector; the extension will be enabled in Phase 8 using the `pgvector/pgvector:pg17` Docker image.
- [ ] Create HNSW index on `player_embeddings.embedding` with `lists=100` (Phase 8).
- [ ] Implement `VectorStore` protocol in `backend/src/pitchmind/db/repositories/` (Phase 11).
- [ ] Document Qdrant migration path in `ops/runbooks/vector_store_migration.md` (Phase 15).
