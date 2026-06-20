"""Integration tests for rate limiting (slowapi + Redis)."""

import asyncio

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_rate_limit_exceeded_returns_429(client: AsyncClient) -> None:
    payload = {"email": "noone@example.com", "password": "wrong"}
    responses = await asyncio.gather(
        *[client.post("/api/v1/auth/login", json=payload) for _ in range(70)]
    )
    status_codes = [r.status_code for r in responses]
    assert 429 in status_codes, "Expected at least one 429 after 70 rapid login attempts"


@pytest.mark.asyncio
async def test_rate_limit_response_body(client: AsyncClient) -> None:
    payload = {"email": "noone@example.com", "password": "wrong"}
    responses = await asyncio.gather(
        *[client.post("/api/v1/auth/login", json=payload) for _ in range(70)]
    )
    limited = [r for r in responses if r.status_code == 429]
    assert limited, "Expected at least one 429 response"
    body = limited[0].json()
    assert body["error"]["code"] == "RATE_LIMIT_EXCEEDED"
