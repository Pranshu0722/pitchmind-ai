import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pitchmind.api.v1.schemas.team import TeamCreate, TeamResponse
from pitchmind.core.deps import get_current_user, require_role
from pitchmind.db.models.team import Team
from pitchmind.db.models.user import UserRole
from pitchmind.db.session import get_db

log = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=list[TeamResponse])
async def list_teams(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> list[Team]:
    result = await db.execute(select(Team).order_by(Team.name).offset(skip).limit(limit))
    return list(result.scalars().all())


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(team_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Team:
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return team


@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role(UserRole.ADMIN))])
async def create_team(body: TeamCreate, db: AsyncSession = Depends(get_db)) -> Team:
    existing = await db.execute(select(Team).where(Team.name == body.name))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Team name already exists")

    team = Team(id=uuid.uuid4(), **body.model_dump())
    db.add(team)
    await db.flush()
    log.info("team.created", team_id=str(team.id), name=team.name)
    return team
