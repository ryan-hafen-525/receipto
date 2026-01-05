"""Database connection pool management using asyncpg."""

import asyncpg
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from config import settings


class DatabaseManager:
    """Manages asyncpg connection pool lifecycle."""

    def __init__(self):
        self.pool: asyncpg.Pool | None = None

    async def connect(self):
        """Create connection pool on startup."""
        self.pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=settings.DB_POOL_MIN_SIZE,
            max_size=settings.DB_POOL_MAX_SIZE,
            max_inactive_connection_lifetime=300,
            command_timeout=60,
        )
        print(f"✓ Database pool created: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'connected'}")

    async def disconnect(self):
        """Close connection pool on shutdown."""
        if self.pool:
            await self.pool.close()
            print("✓ Database pool closed")

    @asynccontextmanager
    async def acquire(self) -> AsyncGenerator[asyncpg.pool.PoolConnectionProxy, None]:
        """Acquire a connection from the pool."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")

        conn = await self.pool.acquire()
        try:
            yield conn
        finally:
            await self.pool.release(conn)


# Global instance
db_manager = DatabaseManager()
