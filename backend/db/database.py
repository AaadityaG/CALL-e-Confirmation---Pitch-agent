import asyncpg
from fastapi import HTTPException, Request, status


async def create_pool(dsn: str) -> asyncpg.Pool:
    return await asyncpg.create_pool(dsn, min_size=1, max_size=10)


async def ensure_schema(pool: asyncpg.Pool, database_url: str) -> None:
    db_name = database_url.rsplit("/", 1)[-1].split("?")[0]
    await pool.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id            TEXT PRIMARY KEY,
            email         TEXT NOT NULL UNIQUE,
            name          TEXT NOT NULL,
            picture       TEXT,
            password_hash TEXT,
            google_sub    TEXT UNIQUE,
            created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    print(f"[Postgres] Schema OK — db: '{db_name}'")


def get_db(request: Request) -> asyncpg.Pool:
    pool = getattr(request.app.state, "pg_pool", None)
    if pool is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )
    return pool