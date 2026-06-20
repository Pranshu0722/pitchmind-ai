"""Integration tests for rate limiting (slowapi + Redis)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_rate_limit_exceeded_returns_429(client: AsyncClient) -> None:
    payload = {"email": "noone@example.com", "password": "wrong"}
    status_codes = []
    for _ in range(70):
        r = await client.post("/api/v1/auth/login", json=payload)
        status_codes.append(r.status_code)
    assert 429 in status_codes, "Expected at least one 429 after 70 rapid login attempts"


@pytest.mark.asyncio
async def test_rate_limit_response_body(client: AsyncClient) -> None:
    payload = {"email": "noone@example.com", "password": "wrong"}
    limited = []
    for _ in range(70):
        r = await client.post("/api/v1/auth/login", json=payload)
        if r.status_code == 429:
            limited.append(r)
    assert limited, "Expected at least one 429 response"
    body = limited[0].json()
    assert body["error"]["code"] == "RATE_LIMIT_EXCEEDED"
