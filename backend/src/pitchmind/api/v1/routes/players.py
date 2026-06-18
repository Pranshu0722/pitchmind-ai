import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pitchmind.api.v1.schemas.player import PlayerCreate, PlayerResponse
from pitchmind.core.deps import require_role
from pitchmind.db.models.player import Player, PlayerPosition
from pitchmind.db.models.team import Team
from pitchmind.db.models.user import UserRole
from pitchmind.db.session import get_db

log = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=list[PlayerResponse])
async def list_players(
    team_id: uuid.UUID | None = Query(default=None),
    position: PlayerPosition | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> list[Player]:
    stmt = select(Player).order_by(Player.name).offset(skip).limit(limit)
    if team_id is not None:
        stmt = stmt.where(Player.team_id == team_id)
    if position is not None:
        stmt = stmt.where(Player.position == position)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(player_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Player:
    result = await db.execute(select(Player).where(Player.id == player_id))
    player = result.scalar_one_or_none()
    if player is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
    return player


@router.post(
    "/",
    response_model=PlayerResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
async def create_player(body: PlayerCreate, db: AsyncSession = Depends(get_db)) -> Player:
    if body.team_id is not None:
        team = await db.execute(select(Team).where(Team.id == body.team_id))
        if team.scalar_one_or_none() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    player = Player(id=uuid.uuid4(), **body.model_dump())
    db.add(player)
    await db.flush()
    log.info("player.created", player_id=str(player.id), name=player.name)
    return player
