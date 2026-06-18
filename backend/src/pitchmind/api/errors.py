from enum import StrEnum
from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorCode(StrEnum):
    # Auth
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"
    # Resources
    NOT_FOUND = "NOT_FOUND"
    MATCH_NOT_FOUND = "MATCH_NOT_FOUND"
    RUN_NOT_FOUND = "RUN_NOT_FOUND"
    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNSUPPORTED_MEDIA_TYPE = "UNSUPPORTED_MEDIA_TYPE"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    # Rate / quota
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
    # Pipeline
    PIPELINE_FAILED = "PIPELINE_FAILED"
    INSUFFICIENT_DETECTIONS = "INSUFFICIENT_DETECTIONS"
    # Generic
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


class ErrorDetail(BaseModel):
    code: ErrorCode
    message: str
    details: dict[str, Any] | None = None
    trace_id: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class AppError(Exception):
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, resource: str, resource_id: str | int) -> None:
        super().__init__(
            code=ErrorCode.NOT_FOUND,
            message=f"{resource} '{resource_id}' not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class AuthError(AppError):
    def __init__(self, code: ErrorCode = ErrorCode.INVALID_CREDENTIALS) -> None:
        super().__init__(
            code=code,
            message="Authentication failed",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenError(AppError):
    def __init__(self) -> None:
        super().__init__(
            code=ErrorCode.INSUFFICIENT_PERMISSIONS,
            message="You do not have permission to perform this action",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ConflictError(AppError):
    def __init__(self, message: str, code: ErrorCode = ErrorCode.EMAIL_ALREADY_EXISTS) -> None:
        super().__init__(code=code, message=message, status_code=status.HTTP_409_CONFLICT)


def _make_error_response(
    code: ErrorCode,
    message: str,
    status_code: int,
    trace_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            error=ErrorDetail(
                code=code,
                message=message,
                details=details,
                trace_id=trace_id,
            )
        ).model_dump(),
    )


def _get_trace_id(request: Request) -> str | None:
    return getattr(request.state, "trace_id", None)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return _make_error_response(
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        trace_id=_get_trace_id(request),
        details=exc.details,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    import structlog

    log = structlog.get_logger()
    log.error("unhandled_exception", exc_type=type(exc).__name__, path=request.url.path)
    return _make_error_response(
        code=ErrorCode.INTERNAL_ERROR,
        message="An unexpected error occurred",
        status_code=500,
        trace_id=_get_trace_id(request),
    )
