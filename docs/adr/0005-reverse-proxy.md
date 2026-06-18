# ADR-0005: Reverse Proxy — Caddy (prod) + Nginx (dev)

**Date:** 2026-06-15
**Status:** Accepted
**Deciders:** Pranshu0722

---

## Context

We need a reverse proxy for TLS termination, routing, and compression. Dev and prod have different requirements: dev prioritises simplicity; prod prioritises automatic TLS.

## Decision

- **Production:** **Caddy 2** — automatic HTTPS via Let's Encrypt, zero config for TLS, simple Caddyfile.
- **Dev Compose:** **Nginx** — widely understood config, no TLS overhead in local environment.

## Alternatives Considered

| Option | Pros | Cons |
| --- | --- | --- |
| Nginx everywhere | Ubiquitous; powerful; huge docs | Manual TLS cert renewal; more config for prod HTTPS |
| **Caddy prod / Nginx dev** | Free auto-HTTPS in prod; familiar Nginx in dev | Two different proxy codebases to understand |
| Traefik | Docker-native; dynamic config | Complex; overkill for v1 |
| HAProxy | Extremely performant | No built-in TLS management |

## Consequences

**Positive:**
- Zero-effort HTTPS in prod — no cert management, no cron renewals.
- Nginx in dev is well-documented and matches most tutorials.

**Negative / Trade-offs:**
- Two config formats to learn (Caddyfile vs nginx.conf).

**Risks:**
- Caddy's ACME challenges require the server to be publicly reachable on port 80/443.

## Follow-up

- [ ] Write `infra/nginx/nginx.conf` for dev compose (Phase 6 — Docker-based infra being built out).
- [ ] Write `infra/caddy/Caddyfile` for prod (Phase 15).
- [ ] Document Caddy env vars for domain + email in `.env.example` (Phase 15).
