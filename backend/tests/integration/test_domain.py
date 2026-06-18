"""Integration tests for teams, players, matches, and match events."""

import uuid

import pytest
from httpx import AsyncClient

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"

ADMIN_USER = {"email": "admin@test.com", "password": "AdminPass1"}
REGULAR_USER = {"email": "user@test.com", "password": "UserPass1"}

TEAM_ARSENAL = {"name": "Arsenal", "short_name": "ARS", "country": "England"}
TEAM_CHELSEA = {"name": "Chelsea", "short_name": "CHE", "country": "England"}


async def _make_admin(client: AsyncClient) -> str:
    """Register a user and manually promote to admin by returning a token
    that bypasses admin check — we seed via direct DB instead."""
    # For tests, register + login as regular user; admin routes tested separately
    await client.post(REGISTER_URL, json=ADMIN_USER)
    resp = await client.post(LOGIN_URL, json=ADMIN_USER)
    return resp.json()["access_token"]


async def _make_user(client: AsyncClient) -> str:
    await client.post(REGISTER_URL, json=REGULAR_USER)
    resp = await client.post(LOGIN_URL, json=REGULAR_USER)
    return resp.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Teams
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_teams_empty(client: AsyncClient):
    resp = await client.get("/api/v1/teams/")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_team_requires_admin(client: AsyncClient):
    token = await _make_user(client)
    resp = await client.post("/api/v1/teams/", json=TEAM_ARSENAL, headers=_auth(token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_create_team_unauthenticated(client: AsyncClient):
    resp = await client.post("/api/v1/teams/", json=TEAM_ARSENAL)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_team_not_found(client: AsyncClient):
    resp = await client.get(f"/api/v1/teams/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_teams_public(client: AsyncClient, db):
    # Seed a team directly via DB (bypass admin guard for simplicity)
    from pitchmind.db.models.team import Team

    team = Team(id=uuid.uuid4(), name="Barcelona", country="Spain")
    db.add(team)
    await db.flush()

    resp = await client.get("/api/v1/teams/")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Barcelona"


@pytest.mark.asyncio
async def test_get_team_by_id(client: AsyncClient, db):
    from pitchmind.db.models.team import Team

    team_id = uuid.uuid4()
    team = Team(id=team_id, name="Real Madrid", country="Spain")
    db.add(team)
    await db.flush()

    resp = await client.get(f"/api/v1/teams/{team_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Real Madrid"


# ---------------------------------------------------------------------------
# Players
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_players_empty(client: AsyncClient):
    resp = await client.get("/api/v1/players/")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_player_requires_admin(client: AsyncClient):
    token = await _make_user(client)
    body = {"name": "Bukayo Saka", "position": "FWD"}
    resp = await client.post("/api/v1/players/", json=body, headers=_auth(token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_get_player_not_found(client: AsyncClient):
    resp = await client.get(f"/api/v1/players/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_players_filter_by_position(client: AsyncClient, db):
    from pitchmind.db.models.player import Player, PlayerPosition

    db.add(Player(id=uuid.uuid4(), name="Keeper One", position=PlayerPosition.GK))
    db.add(Player(id=uuid.uuid4(), name="Forward One", position=PlayerPosition.FWD))
    await db.flush()

    resp = await client.get("/api/v1/players/?position=GK")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["position"] == "GK"


# ---------------------------------------------------------------------------
# Matches
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_matches_empty(client: AsyncClient):
    resp = await client.get("/api/v1/matches/")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_match_requires_admin(client: AsyncClient):
    token = await _make_user(client)
    body = {
        "home_team_id": str(uuid.uuid4()),
        "away_team_id": str(uuid.uuid4()),
        "kickoff_at": "2025-09-01T15:00:00Z",
    }
    resp = await client.post("/api/v1/matches/", json=body, headers=_auth(token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_get_match_not_found(client: AsyncClient):
    resp = await client.get(f"/api/v1/matches/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_match_same_team_validation(client: AsyncClient, db):
    from pitchmind.core.security import create_access_token, hash_password
    from pitchmind.db.models.team import Team
    from pitchmind.db.models.user import User, UserRole

    team_id = uuid.uuid4()
    db.add(Team(id=team_id, name="Juventus", country="Italy"))
    admin = User(
        id=uuid.uuid4(),
        email="admin2@test.com",
        password_hash=hash_password("AdminPass1"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(admin)
    await db.flush()
    token = create_access_token(str(admin.id), admin.role)

    body = {
        "home_team_id": str(team_id),
        "away_team_id": str(team_id),
        "kickoff_at": "2025-09-01T15:00:00Z",
    }
    resp = await client.post("/api/v1/matches/", json=body, headers=_auth(token))
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_full_match_flow(client: AsyncClient, db):
    """Seed two teams + admin user, create match, update score, add event, list events."""
    from pitchmind.core.security import create_access_token, hash_password
    from pitchmind.db.models.team import Team
    from pitchmind.db.models.user import User, UserRole

    home_id, away_id = uuid.uuid4(), uuid.uuid4()
    db.add(Team(id=home_id, name="Inter Milan", country="Italy"))
    db.add(Team(id=away_id, name="AC Milan", country="Italy"))
    admin = User(
        id=uuid.uuid4(),
        email="admin3@test.com",
        password_hash=hash_password("AdminPass1"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(admin)
    await db.flush()
    token = create_access_token(str(admin.id), admin.role)

    # Create match
    create_resp = await client.post(
        "/api/v1/matches/",
        json={
            "home_team_id": str(home_id),
            "away_team_id": str(away_id),
            "kickoff_at": "2025-10-05T20:00:00Z",
        },
        headers=_auth(token),
    )
    assert create_resp.status_code == 201
    match_id = create_resp.json()["id"]
    assert create_resp.json()["status"] == "SCHEDULED"

    # Update score
    patch_resp = await client.patch(
        f"/api/v1/matches/{match_id}",
        json={"status": "FINISHED", "home_score": 2, "away_score": 1},
        headers=_auth(token),
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["home_score"] == 2
    assert patch_resp.json()["status"] == "FINISHED"

    # Add a goal event
    event_resp = await client.post(
        f"/api/v1/matches/{match_id}/events",
        json={"event_type": "GOAL", "minute": 23},
        headers=_auth(token),
    )
    assert event_resp.status_code == 201
    assert event_resp.json()["event_type"] == "GOAL"

    # List events
    events_resp = await client.get(f"/api/v1/matches/{match_id}/events")
    assert events_resp.status_code == 200
    assert len(events_resp.json()) == 1
