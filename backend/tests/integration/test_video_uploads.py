"""Integration tests for video upload endpoints (requires MinIO running on localhost:9000)."""

import io
import uuid

import pytest
from httpx import AsyncClient

from pitchmind.core.security import create_access_token, hash_password
from pitchmind.db.models.user import User, UserRole

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
VIDEOS_URL = "/api/v1/videos/"

SMALL_VIDEO = b"\x00\x01\x02\x03" * 256  # 1 KB fake video bytes

# Pre-compute once — argon2 is memory-intensive, computing it per-test causes OOM in CI
_HASHED_PW = hash_password("TestPass1")


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _fake_mp4(name: str = "test.mp4") -> tuple:
    return ("file", (name, io.BytesIO(SMALL_VIDEO), "video/mp4"))


async def _seed_user(db, email: str, role: UserRole) -> str:
    user = User(
        id=uuid.uuid4(),
        email=email,
        password_hash=_HASHED_PW,
        role=role,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    return create_access_token(str(user.id), user.role)


@pytest.mark.asyncio
async def test_upload_video_success(client: AsyncClient, db):
    token = await _seed_user(db, "uploader@test.com", UserRole.USER)
    resp = await client.post(
        VIDEOS_URL,
        files=[_fake_mp4()],
        headers=_auth(token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["filename"] == "test.mp4"
    assert data["content_type"] == "video/mp4"
    assert data["status"] == "PENDING"
    assert data["file_size_bytes"] == len(SMALL_VIDEO)


@pytest.mark.asyncio
async def test_upload_requires_auth(client: AsyncClient):
    resp = await client.post(VIDEOS_URL, files=[_fake_mp4()])
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_upload_wrong_content_type(client: AsyncClient, db):
    token = await _seed_user(db, "uploader2@test.com", UserRole.USER)
    resp = await client.post(
        VIDEOS_URL,
        files=[("file", ("test.txt", io.BytesIO(b"hello"), "text/plain"))],
        headers=_auth(token),
    )
    assert resp.status_code == 415


@pytest.mark.asyncio
async def test_list_uploads_empty(client: AsyncClient):
    resp = await client.get(VIDEOS_URL)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_uploads_after_upload(client: AsyncClient, db):
    token = await _seed_user(db, "uploader3@test.com", UserRole.USER)
    await client.post(VIDEOS_URL, files=[_fake_mp4()], headers=_auth(token))
    resp = await client.get(VIDEOS_URL)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_get_upload_not_found(client: AsyncClient):
    resp = await client.get(f"{VIDEOS_URL}{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_upload_by_id(client: AsyncClient, db):
    token = await _seed_user(db, "uploader4@test.com", UserRole.USER)
    upload_resp = await client.post(VIDEOS_URL, files=[_fake_mp4()], headers=_auth(token))
    upload_id = upload_resp.json()["id"]

    resp = await client.get(f"{VIDEOS_URL}{upload_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == upload_id


@pytest.mark.asyncio
async def test_get_download_url(client: AsyncClient, db):
    token = await _seed_user(db, "uploader5@test.com", UserRole.USER)
    upload_resp = await client.post(VIDEOS_URL, files=[_fake_mp4()], headers=_auth(token))
    upload_id = upload_resp.json()["id"]

    resp = await client.get(f"{VIDEOS_URL}{upload_id}/download")
    assert resp.status_code == 200
    data = resp.json()
    assert "url" in data
    assert "localhost:9000" in data["url"] or "minio" in data["url"]


@pytest.mark.asyncio
async def test_delete_requires_admin(client: AsyncClient, db):
    token = await _seed_user(db, "uploader6@test.com", UserRole.USER)
    upload_resp = await client.post(VIDEOS_URL, files=[_fake_mp4()], headers=_auth(token))
    upload_id = upload_resp.json()["id"]

    resp = await client.delete(f"{VIDEOS_URL}{upload_id}", headers=_auth(token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_delete_by_admin(client: AsyncClient, db):
    user_token = await _seed_user(db, "uploader7@test.com", UserRole.USER)
    admin_token = await _seed_user(db, "admin7@test.com", UserRole.ADMIN)

    upload_resp = await client.post(VIDEOS_URL, files=[_fake_mp4()], headers=_auth(user_token))
    upload_id = upload_resp.json()["id"]

    del_resp = await client.delete(f"{VIDEOS_URL}{upload_id}", headers=_auth(admin_token))
    assert del_resp.status_code == 204

    get_resp = await client.get(f"{VIDEOS_URL}{upload_id}")
    assert get_resp.status_code == 404
