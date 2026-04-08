"""Database configuration and lifecycle helpers."""

from collections.abc import Sequence

from tortoise import Tortoise

from .config import settings


def get_tortoise_config() -> dict[str, object]:
    """Build the Tortoise ORM configuration from current settings."""

    return {
        "connections": {"default": settings.tortoise_database_url},
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


def _is_sqlite_database_url(database_url: str) -> bool:
    """Return whether the configured database URL points at SQLite."""

    return database_url.startswith("sqlite://")


async def _get_default_connection_table_names() -> set[str]:
    """Return the current set of tables for the default connection."""

    connection = Tortoise.get_connection("default")
    raw_table_names = await connection.execute_query_dict(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )
    return {row["name"] for row in raw_table_names if row["name"] != "sqlite_sequence"}


async def _should_bootstrap_sqlite_schema() -> bool:
    """Detect an uninitialized SQLite database so local startup can self-heal."""

    if settings.database_generate_schemas or not _is_sqlite_database_url(settings.database_url):
        return False

    table_names = await _get_default_connection_table_names()
    expected_tables: Sequence[str] = ("prompts", "evaluations", "users")
    return not all(table_name in table_names for table_name in expected_tables)


async def init_db() -> None:
    """Initialize database connections and optionally create schemas."""

    global TORTOISE_ORM
    if getattr(Tortoise, "_inited", False):  # pragma: no cover - defensive guard
        await Tortoise.close_connections()

    TORTOISE_ORM = get_tortoise_config()
    await Tortoise.init(config=TORTOISE_ORM)

    if settings.database_generate_schemas or await _should_bootstrap_sqlite_schema():
        await Tortoise.generate_schemas()


async def close_db() -> None:
    """Close any open database connections."""

    if getattr(Tortoise, "_inited", False):
        await Tortoise.close_connections()
