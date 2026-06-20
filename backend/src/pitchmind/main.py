from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
import structlog
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from pitchmind.api.errors import (
    AppError,
    ErrorCode,
    _get_trace_id,
    _make_error_response,
    app_error_handler,
    unhandled_exception_handler,
)
from pitchmind.api.limiter import limiter
from pitchmind.api.v1 import router as v1_router
from pitchmind.config import settings
from pitchmind.logging import configure_logging
from pitchmind.middleware import TraceMiddleware

configure_logging()
log = structlog.get_logger(__name__)


async def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return _make_error_response(
        code=ErrorCode.RATE_LIMIT_EXCEEDED,
        message=f"Rate limit exceeded: {exc.detail}",
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        trace_id=_get_trace_id(request),
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    log.info("pitchmind.startup", env=settings.app_env, version="0.1.0")
    redis_client = aioredis.from_url(settings.redis_url)
    try:
        await redis_client.ping()
        log.info("pitchmind.redis.connected")
    except Exception as exc:
        log.warning("pitchmind.redis.unavailable", error=str(exc))
    app.state.redis = redis_client
    yield
    await redis_client.aclose()  # type: ignore[attr-defined]
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

    app.state.limiter = limiter
    app.add_middleware(TraceMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)

    @app.get("/healthz", tags=["ops"], include_in_schema=False)
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz", tags=["ops"], include_in_schema=False)
    async def readyz() -> dict[str, str]:
        try:
            await app.state.redis.ping()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Redis unavailable",
            ) from None
        return {"status": "ok"}

    app.include_router(v1_router, prefix="/api/v1")

    return app


app = create_app()
