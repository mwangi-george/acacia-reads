from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.settings.config import DB_URL


# -----------------------------------------------------------------------------
# Database Engine Configuration
# -----------------------------------------------------------------------------
# Creates an asynchronous SQLAlchemy engine that manages the connection pool to
# the database. The `future=True` flag enables modern SQLAlchemy 2.0 behavior.
# - `statement_cache_size=0`: disables statement caching (useful in some async
#   contexts to avoid issues with prepared statements).
# - `pool_pre_ping=True`: ensures that stale connections are automatically
#   detected and refreshed.
# -----------------------------------------------------------------------------
engine = create_async_engine(
    url=DB_URL,
    future=True,
    connect_args={"statement_cache_size": 0},
    pool_pre_ping=True,
)


# -----------------------------------------------------------------------------
# Session Factory
# -----------------------------------------------------------------------------
# Provides an asynchronous session factory (`SessionLocal`) bound to the engine.
# This is used to create database sessions that are tied to the async engine.
# - `expire_on_commit=False`: prevents objects from being expired after commit,
#   so they can still be accessed without reloading from the database.
# - `autoflush=False`: disables automatic flushing of changes to the database
#   before queries; changes must be explicitly flushed or committed.
# -----------------------------------------------------------------------------
SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


# -----------------------------------------------------------------------------
# Dependency for FastAPI
# -----------------------------------------------------------------------------
# Provides a database session for use inside FastAPI routes.
#
# Usage:
#     async def get_books(db: AsyncSession = Depends(get_db)):
#         result = await db.execute(...)
#
# The function is defined as an async generator (`yield`) so that FastAPI can
# properly manage the lifespan of the session, ensuring it is closed after use.
# -----------------------------------------------------------------------------
async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    """
    Dependency that provides a SQLAlchemy AsyncSession.

    Yields:
        AsyncSession: A database session object that can be used to perform
        queries and transactions.
    """
    async with SessionLocal() as session:
        yield session
