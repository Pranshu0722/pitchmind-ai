# ADR-0006: Python Environment Manager — uv

**Date:** 2026-06-15
**Status:** Accepted
**Deciders:** Pranshu0722

---

## Context

Python packaging has historically been painful. We need a tool that is fast, reproducible, and works well in Docker and CI. Candidates: pip + venv, Poetry, PDM, uv.

## Decision

Use **uv** (Astral) as the Python environment and package manager for the entire backend.

## Alternatives Considered

| Option | Pros | Cons |
| --- | --- | --- |
| pip + venv | Universal; no extra tooling | Slow; no lock file by default; fragile in CI |
| Poetry | Great DX; lock file; widespread | Slow resolver; complex pyproject schema; plugin ecosystem issues |
| PDM | PEP 582 compliant; fast | Smaller community |
| **uv** | 10-100× faster than pip; `uv.lock`; Drop-in pip replacement; Rust-powered | Newer; still evolving API |

## Consequences

**Positive:**
- `uv sync` is dramatically faster than `pip install` or `poetry install` — speeds up CI and Docker builds.
- `uv.lock` is deterministic and cross-platform.
- `uv run` replaces activating a venv — cleaner scripts and Makefile targets.
- Works in Docker: `COPY uv.lock . && RUN uv sync --frozen --no-dev`.

**Negative / Trade-offs:**
- Some developers may not have `uv` installed; onboarding requires `curl -LsSf https://astral.sh/uv/install.sh | sh`.
- API is still maturing; a few edge cases in workspace management.

**Risks:**
- If uv introduces breaking changes, `pip` and `venv` are always a fallback since `pyproject.toml` is standard.

## Follow-up

- [ ] Add `uv` install step to CI (`astral-sh/setup-uv@v4`).
- [ ] Add `uv` install to `infra/docker/api.Dockerfile`.
- [ ] Document `uv` install in `CONTRIBUTING.md`.
