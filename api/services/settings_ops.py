"""Database operations for settings and categories."""

import uuid
from typing import Optional, List, Dict, Any
from decimal import Decimal
import asyncpg

from models.settings_schemas import (
    CategoryCreate, CategoryUpdate, Category,
    SettingsUpdate, SettingsResponse
)


# Keys that contain sensitive data and should be marked as encrypted
SENSITIVE_KEYS = {
    "aws_access_key_id",
    "aws_secret_access_key",
    "google_api_key",
    "openai_api_key",
    "anthropic_api_key",
}


class SettingsService:
    """Handles database operations for settings."""

    @staticmethod
    async def get_all_settings(conn: asyncpg.pool.PoolConnectionProxy) -> SettingsResponse:
        """Get all settings, masking sensitive values."""
        rows = await conn.fetch("SELECT key, value, encrypted FROM settings")

        settings_dict = {row["key"]: row["value"] for row in rows}

        return SettingsResponse(
            llm_provider=settings_dict.get("llm_provider", "gemini"),
            llm_model=settings_dict.get("llm_model", "gemini-2.0-flash"),
            theme=settings_dict.get("theme", "system"),
            aws_region=settings_dict.get("aws_region", "us-west-2"),
            aws_access_key_configured=bool(settings_dict.get("aws_access_key_id")),
            aws_secret_key_configured=bool(settings_dict.get("aws_secret_access_key")),
            google_api_key_configured=bool(settings_dict.get("google_api_key")),
            openai_api_key_configured=bool(settings_dict.get("openai_api_key")),
            anthropic_api_key_configured=bool(settings_dict.get("anthropic_api_key")),
        )

    @staticmethod
    async def get_setting(
        conn: asyncpg.pool.PoolConnectionProxy,
        key: str
    ) -> Optional[str]:
        """Get a single setting value."""
        row = await conn.fetchrow(
            "SELECT value FROM settings WHERE key = $1",
            key
        )
        return row["value"] if row else None

    @staticmethod
    async def update_settings(
        conn: asyncpg.pool.PoolConnectionProxy,
        updates: SettingsUpdate
    ) -> None:
        """Update multiple settings at once."""
        update_data = updates.model_dump(exclude_none=True)

        async with conn.transaction():
            for key, value in update_data.items():
                encrypted = key in SENSITIVE_KEYS
                await conn.execute(
                    """
                    INSERT INTO settings (key, value, encrypted, updated_at)
                    VALUES ($1, $2, $3, CURRENT_TIMESTAMP)
                    ON CONFLICT (key) DO UPDATE SET
                        value = EXCLUDED.value,
                        encrypted = EXCLUDED.encrypted,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    key, str(value), encrypted
                )

    @staticmethod
    async def delete_setting(
        conn: asyncpg.pool.PoolConnectionProxy,
        key: str
    ) -> None:
        """Delete a setting."""
        await conn.execute("DELETE FROM settings WHERE key = $1", key)


class CategoryService:
    """Handles database operations for categories."""

    @staticmethod
    async def get_all_categories(
        conn: asyncpg.pool.PoolConnectionProxy
    ) -> List[Dict[str, Any]]:
        """Get all categories."""
        rows = await conn.fetch(
            """
            SELECT id, name, monthly_budget_limit, created_at, updated_at
            FROM categories
            ORDER BY name
            """
        )
        return [dict(row) for row in rows]

    @staticmethod
    async def get_category(
        conn: asyncpg.pool.PoolConnectionProxy,
        category_id: uuid.UUID
    ) -> Optional[Dict[str, Any]]:
        """Get a category by ID."""
        row = await conn.fetchrow(
            """
            SELECT id, name, monthly_budget_limit, created_at, updated_at
            FROM categories
            WHERE id = $1
            """,
            category_id
        )
        return dict(row) if row else None

    @staticmethod
    async def create_category(
        conn: asyncpg.pool.PoolConnectionProxy,
        category: CategoryCreate
    ) -> Dict[str, Any]:
        """Create a new category."""
        category_id = uuid.uuid4()

        row = await conn.fetchrow(
            """
            INSERT INTO categories (id, name, monthly_budget_limit, created_at, updated_at)
            VALUES ($1, $2, $3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id, name, monthly_budget_limit, created_at, updated_at
            """,
            category_id,
            category.name,
            category.monthly_budget_limit
        )
        return dict(row)

    @staticmethod
    async def update_category(
        conn: asyncpg.pool.PoolConnectionProxy,
        category_id: uuid.UUID,
        updates: CategoryUpdate
    ) -> Optional[Dict[str, Any]]:
        """Update a category."""
        update_data = updates.model_dump(exclude_none=True)

        if not update_data:
            # No updates, just return current
            return await CategoryService.get_category(conn, category_id)

        # Build dynamic update query
        set_clauses = []
        values = []
        param_idx = 1

        for key, value in update_data.items():
            set_clauses.append(f"{key} = ${param_idx}")
            values.append(value)
            param_idx += 1

        values.append(category_id)

        query = f"""
            UPDATE categories
            SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ${param_idx}
            RETURNING id, name, monthly_budget_limit, created_at, updated_at
        """

        row = await conn.fetchrow(query, *values)
        return dict(row) if row else None

    @staticmethod
    async def delete_category(
        conn: asyncpg.pool.PoolConnectionProxy,
        category_id: uuid.UUID
    ) -> bool:
        """Delete a category. Returns True if deleted."""
        result = await conn.execute(
            "DELETE FROM categories WHERE id = $1",
            category_id
        )
        return result == "DELETE 1"

    @staticmethod
    async def category_exists(
        conn: asyncpg.pool.PoolConnectionProxy,
        name: str,
        exclude_id: Optional[uuid.UUID] = None
    ) -> bool:
        """Check if a category with the given name exists."""
        if exclude_id:
            row = await conn.fetchrow(
                "SELECT 1 FROM categories WHERE name = $1 AND id != $2",
                name, exclude_id
            )
        else:
            row = await conn.fetchrow(
                "SELECT 1 FROM categories WHERE name = $1",
                name
            )
        return row is not None
