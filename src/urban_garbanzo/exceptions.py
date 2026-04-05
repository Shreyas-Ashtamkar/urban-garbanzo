"""Application-specific exceptions and handlers."""

from uuid import UUID

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base class for application errors returned to clients."""

    status_code = 500
    detail = "Unexpected application error"

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.detail
        super().__init__(self.detail)


class PromptNotFound(AppError):
    """Raised when a prompt cannot be found."""

    status_code = 404

    def __init__(self, prompt_id: UUID) -> None:
        super().__init__(f"Prompt '{prompt_id}' was not found")


class EvaluationNotFound(AppError):
    """Raised when an evaluation cannot be found."""

    status_code = 404

    def __init__(self, evaluation_id: UUID) -> None:
        super().__init__(f"Evaluation '{evaluation_id}' was not found")


class EvaluationFailed(AppError):
    """Raised when prompt evaluation cannot be completed."""

    status_code = 502
    detail = "Prompt evaluation failed"


class LLMUnavailable(AppError):
    """Raised when a configured LLM backend is unavailable."""

    status_code = 503
    detail = "The configured LLM provider is unavailable"


async def app_error_handler(_: Request, exc: Exception) -> JSONResponse:
    """Serialize application errors into a consistent JSON response."""

    assert isinstance(exc, AppError)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


def register_exception_handlers(app: FastAPI) -> None:
    """Register application exception handlers on the FastAPI app."""

    app.add_exception_handler(AppError, app_error_handler)
