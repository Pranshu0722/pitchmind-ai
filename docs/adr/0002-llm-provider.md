# ADR-0002: LLM Provider Strategy — Multi-Provider Adapter

**Date:** 2026-06-15
**Status:** Accepted
**Deciders:** Pranshu0722

---

## Context

The agent layer requires LLM calls for routing, synthesis, and report generation. Different tasks have different cost/quality trade-offs. Locking into a single provider risks cost overruns and regional availability failures.

## Decision

Build a **provider-agnostic adapter** with two configurable slots:

- **Routing model** (cheap, fast): `Gemini 2.0 Flash` by default.
- **Synthesis model** (strong, slower): `Claude Sonnet 4.6` (Anthropic) by default.
- **Local fallback**: Ollama (Llama 3 / Qwen) for dev without API keys.

The adapter exposes a single `LLMClient` interface; provider is selected via env vars.

## Alternatives Considered

| Option | Pros | Cons |
| --- | --- | --- |
| OpenAI only | Widest tooling support | Cost; rate limits; no offline |
| Gemini only | Generous free tier; fast | Tool-use quality lags Claude |
| **Multi-provider adapter** | Cost optimisation; resilience; offline dev | More code to maintain |
| OSS local only | Free; private | Quality gap on complex synthesis |

## Consequences

**Positive:**
- Route cheap classification calls to Flash; use Claude/GPT-4o only for report generation.
- Dev works offline via Ollama.
- Swap providers in one env-var change — no code change.

**Negative / Trade-offs:**
- Must maintain 3–4 adapter implementations.
- Prompt tuning for one model may not transfer perfectly.

**Risks:**
- Prompt-injection surface differs per provider — test each.

## Follow-up

- [ ] Implement `backend/src/pitchmind/agents/llm/base.py` protocol (Phase 12).
- [ ] Implement `gemini.py`, `anthropic.py`, `openai.py`, `ollama.py` adapters.
- [ ] Add integration test asserting both routing and synthesis paths return valid responses.
