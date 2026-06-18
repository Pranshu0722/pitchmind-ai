from fastapi import APIRouter

from pitchmind.api.v1.routes import auth, matches, players, teams

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(teams.router, prefix="/teams", tags=["teams"])
router.include_router(players.router, prefix="/players", tags=["players"])
router.include_router(matches.router, prefix="/matches", tags=["matches"])
