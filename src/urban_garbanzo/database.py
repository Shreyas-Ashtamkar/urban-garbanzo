"""Database configuration and lifecycle helpers."""

from tortoise import Tortoise

from .config import settings


def get_tortoise_config() -> dict[str, object]:
    """Build the Tortoise ORM configuration from current settings."""

    return {
        "connections": {"default": settings.database_url},
        "apps": {
            "models": {
                "models": ["urban_garbanzo.models", "aerich.models"],
                "default_connection": "default",
            }
        },
        "use_tz": True,
        "timezone": "UTC",
    }


TORTOISE_ORM = get_tortoise_config()


async def init_db() -> None:
    """Initialize database connections and optionally create schemas."""

    global TORTOISE_ORM
    if getattr(Tortoise, "_inited", False):  # pragma: no cover - defensive guard
        await Tortoise.close_connections()

    TORTOISE_ORM = get_tortoise_config()
    await Tortoise.init(config=TORTOISE_ORM)

    if settings.database_generate_schemas:
        await Tortoise.generate_schemas()


async def close_db() -> None:
    """Close any open database connections."""

    if getattr(Tortoise, "_inited", False):
        await Tortoise.close_connections()
