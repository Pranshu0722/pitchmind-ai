from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pitchmind.config import settings

log = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    log.info("pitchmind.startup", env=settings.app_env, version="0.1.0")
    yield
    log.info("pitchmind.shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title="PitchMind AI",
        version="0.1.0",
        description="Multi-Agent Football Intelligence Platform",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health probes
    @app.get("/healthz", tags=["ops"], include_in_schema=False)
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz", tags=["ops"], include_in_schema=False)
    async def readyz() -> dict[str, str]:
        # TODO Phase 2: check DB + Redis connectivity
        return {"status": "ok"}

    # API routers — registered in Phase 2+
    # from pitchmind.api.v1 import router as v1_router
    # app.include_router(v1_router, prefix="/api/v1")

    return app


app = create_app()
