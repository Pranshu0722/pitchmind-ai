import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pitchmind.api.v1.schemas.match import MatchCreate, MatchResponse, MatchUpdate
from pitchmind.api.v1.schemas.match_event import MatchEventCreate, MatchEventResponse
from pitchmind.core.deps import require_role
from pitchmind.db.models.match import Match, MatchStatus
from pitchmind.db.models.match_event import MatchEvent
from pitchmind.db.models.team import Team
from pitchmind.db.models.user import UserRole
from pitchmind.db.session import get_db

log = structlog.get_logger(__name__)
router = APIRouter()


async def _get_match_or_404(match_id: uuid.UUID, db: AsyncSession) -> Match:
    result = await db.execute(select(Match).where(Match.id == match_id))
    match = result.scalar_one_or_none()
    if match is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return match


@router.get("/", response_model=list[MatchResponse])
async def list_matches(
    status_filter: MatchStatus | None = Query(default=None, alias="status"),
    competition: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> list[Match]:
    stmt = select(Match).order_by(Match.kickoff_at.desc()).offset(skip).limit(limit)
    if status_filter is not None:
        stmt = stmt.where(Match.status == status_filter)
    if competition is not None:
        stmt = stmt.where(Match.competition == competition)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(match_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Match:
    return await _get_match_or_404(match_id, db)


@router.post("/", response_model=MatchResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role(UserRole.ADMIN))])
async def create_match(body: MatchCreate, db: AsyncSession = Depends(get_db)) -> Match:
    for team_id in (body.home_team_id, body.away_team_id):
        result = await db.execute(select(Team).where(Team.id == team_id))
        if result.scalar_one_or_none() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Team {team_id} not found")

    match = Match(id=uuid.uuid4(), **body.model_dump())
    db.add(match)
    await db.flush()
    log.info("match.created", match_id=str(match.id))
    return match


@router.patch("/{match_id}", response_model=MatchResponse,
              dependencies=[Depends(require_role(UserRole.ADMIN))])
async def update_match(match_id: uuid.UUID, body: MatchUpdate, db: AsyncSession = Depends(get_db)) -> Match:
    match = await _get_match_or_404(match_id, db)
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(match, field, value)
    await db.flush()
    log.info("match.updated", match_id=str(match.id))
    return match


@router.get("/{match_id}/events", response_model=list[MatchEventResponse])
async def list_events(match_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> list[MatchEvent]:
    await _get_match_or_404(match_id, db)
    result = await db.execute(
        select(MatchEvent).where(MatchEvent.match_id == match_id).order_by(MatchEvent.minute)
    )
    return list(result.scalars().all())


@router.post("/{match_id}/events", response_model=MatchEventResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role(UserRole.ADMIN))])
async def create_event(
    match_id: uuid.UUID, body: MatchEventCreate, db: AsyncSession = Depends(get_db)
) -> MatchEvent:
    await _get_match_or_404(match_id, db)
    event = MatchEvent(id=uuid.uuid4(), match_id=match_id, **body.model_dump())
    db.add(event)
    await db.flush()
    log.info("match_event.created", event_id=str(event.id), type=event.event_type)
    return event
