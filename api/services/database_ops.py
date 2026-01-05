"""Database CRUD operations using asyncpg."""

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional, List
import asyncpg
from models.schemas import ReceiptExtraction, LineItemExtraction


class DatabaseService:
    """Handles all database CRUD operations."""

    @staticmethod
    async def create_initial_receipt(
        conn: asyncpg.pool.PoolConnectionProxy,
        receipt_id: uuid.UUID,
        image_url: str
    ) -> None:
        """Insert initial receipt record with status='pending'."""
        async with conn.transaction():
            await conn.execute(
                """
                INSERT INTO receipts (id, image_url, status, created_at)
                VALUES ($1, $2, 'pending', CURRENT_TIMESTAMP)
                """,
                receipt_id, image_url
            )

    @staticmethod
    async def update_receipt_status(
        conn: asyncpg.pool.PoolConnectionProxy,
        receipt_id: uuid.UUID,
        status: str
    ) -> None:
        """Update receipt status."""
        async with conn.transaction():
            await conn.execute(
                """
                UPDATE receipts
                SET status = $1, updated_at = CURRENT_TIMESTAMP
                WHERE id = $2
                """,
                status, receipt_id
            )

    @staticmethod
    async def save_receipt_data(
        conn: asyncpg.pool.PoolConnectionProxy,
        receipt_id: uuid.UUID,
        extraction: ReceiptExtraction
    ) -> None:
        """
        Save extracted receipt data and line items in a transaction.

        This should be called within a transaction context.
        """
        # Update receipt record
        await conn.execute(
            """
            UPDATE receipts
            SET merchant_name = $1,
                purchase_date = $2,
                total_amount = $3,
                tax_amount = $4,
                status = 'complete',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = $5
            """,
            extraction.merchant_name,
            extraction.purchase_date,
            extraction.total_amount,
            extraction.tax_amount,
            receipt_id
        )

        # Insert line items
        for item in extraction.line_items:
            await conn.execute(
                """
                INSERT INTO line_items (
                    id, receipt_id, description, category,
                    quantity, unit_price, total_price, created_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, CURRENT_TIMESTAMP)
                """,
                uuid.uuid4(),
                receipt_id,
                item.description,
                item.category,
                item.quantity,
                item.unit_price,
                item.total_price
            )
