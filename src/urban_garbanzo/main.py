"""FastAPI application factory and main entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .config import settings
from .database import close_db, init_db
from .exceptions import register_exception_handlers
from .routers import evaluations_router, leaderboard_router, prompts_router

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize and close external resources for the application."""

    logger.info("Starting %s %s", settings.app_name, __version__)
    await init_db()
    yield
    await close_db()
    logger.info("Shutting down %s", settings.app_name)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        description=(
            "Stop guessing if your prompts work. Get instant ratings on clarity, "
            "correctness, information density, hallucination risk, and redundancy."
        ),
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(prompts_router, prefix="/api/v1")
    app.include_router(evaluations_router, prefix="/api/v1")
    app.include_router(leaderboard_router, prefix="/api/v1")

    @app.get("/health")
    async def health() -> dict[str, str]:
        """Health check endpoint."""

        return {
            "status": "ok",
            "version": __version__,
            "database_url": settings.database_url,
            "llm_provider": settings.llm_provider,
        }

    return app


app = create_app()
