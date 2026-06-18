from fastapi import APIRouter

from pitchmind.api.v1.routes import auth

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
