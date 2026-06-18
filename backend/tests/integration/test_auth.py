import pytest
from httpx import AsyncClient

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
REFRESH_URL = "/api/v1/auth/refresh"
ME_URL = "/api/v1/auth/me"

VALID_USER = {"email": "test@example.com", "password": "Secret123"}


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    resp = await client.post(REGISTER_URL, json=VALID_USER)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == VALID_USER["email"]
    assert data["role"] == "user"
    assert data["is_active"] is True
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    await client.post(REGISTER_URL, json=VALID_USER)
    resp = await client.post(REGISTER_URL, json=VALID_USER)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_register_weak_password_no_digit(client: AsyncClient):
    resp = await client.post(REGISTER_URL, json={"email": "a@b.com", "password": "NoDigitHere"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_weak_password_no_uppercase(client: AsyncClient):
    resp = await client.post(REGISTER_URL, json={"email": "a@b.com", "password": "nouppercase1"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient):
    resp = await client.post(REGISTER_URL, json={"email": "a@b.com", "password": "Sh0rt"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post(REGISTER_URL, json=VALID_USER)
    resp = await client.post(LOGIN_URL, json=VALID_USER)
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post(REGISTER_URL, json=VALID_USER)
    resp = await client.post(LOGIN_URL, json={**VALID_USER, "password": "WrongPass1"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_email(client: AsyncClient):
    resp = await client.post(
        LOGIN_URL, json={"email": "nobody@example.com", "password": "Secret123"}
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_authenticated(client: AsyncClient):
    await client.post(REGISTER_URL, json=VALID_USER)
    login_resp = await client.post(LOGIN_URL, json=VALID_USER)
    token = login_resp.json()["access_token"]
    resp = await client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == VALID_USER["email"]


@pytest.mark.asyncio
async def test_me_unauthenticated(client: AsyncClient):
    resp = await client.get(ME_URL)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_invalid_token(client: AsyncClient):
    resp = await client.get(ME_URL, headers={"Authorization": "Bearer notavalidtoken"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_success(client: AsyncClient):
    await client.post(REGISTER_URL, json=VALID_USER)
    login_resp = await client.post(LOGIN_URL, json=VALID_USER)
    refresh_token = login_resp.json()["refresh_token"]
    resp = await client.post(REFRESH_URL, json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_refresh_with_access_token_fails(client: AsyncClient):
    await client.post(REGISTER_URL, json=VALID_USER)
    login_resp = await client.post(LOGIN_URL, json=VALID_USER)
    access_token = login_resp.json()["access_token"]
    resp = await client.post(REFRESH_URL, json={"refresh_token": access_token})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient):
    resp = await client.post(REFRESH_URL, json={"refresh_token": "garbage"})
    assert resp.status_code == 401
