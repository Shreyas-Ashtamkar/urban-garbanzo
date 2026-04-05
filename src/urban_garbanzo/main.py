"""FastAPI application factory and main entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import __version__


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager.

    Handles startup and shutdown events.
    """
    # Startup
    print(f"Starting urban-garbanzo {__version__}")
    yield
    # Shutdown
    print("Shutting down urban-garbanzo")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured application instance
    """
    app = FastAPI(
        title="urban-garbanzo",
        description="Stop guessing if your prompts work. Get instant ratings on clarity, correctness, information density, hallucination risk, and redundancy.",
        version=__version__,
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoint
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "ok", "version": __version__}

    return app


# Create app instance
app = create_app()
