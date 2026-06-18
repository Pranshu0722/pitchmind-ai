from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pitchmind.api.errors import AppError, app_error_handler, unhandled_exception_handler
from pitchmind.api.v1 import router as v1_router
from pitchmind.config import settings
from pitchmind.logging import configure_logging
from pitchmind.middleware import TraceMiddleware

configure_logging()
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

    app.add_middleware(TraceMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)

    @app.get("/healthz", tags=["ops"], include_in_schema=False)
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz", tags=["ops"], include_in_schema=False)
    async def readyz() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(v1_router, prefix="/api/v1")

    return app


app = create_app()
