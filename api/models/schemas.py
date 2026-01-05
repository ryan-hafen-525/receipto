"""Pydantic models for API responses and data validation."""

from pydantic import BaseModel, Field, field_validator
from typing import List, Literal, Optional
from datetime import date
from decimal import Decimal
import uuid


# API Response Models
class UploadResponse(BaseModel):
    """Response model for receipt upload endpoint."""
    receipt_id: str
    status: str
    message: str


# LLM Structured Output Schema
class LineItemExtraction(BaseModel):
    """Line item extracted from receipt by Gemini."""
    description: str = Field(description="Item description/name")
    category: str = Field(
        description="Category: Groceries, Dining, Transportation, Utilities, Entertainment, Healthcare, Clothing, Home & Garden, Personal Care, Shopping, Other"
    )
    quantity: int = Field(default=1, ge=1, description="Quantity purchased")
    unit_price: Decimal = Field(description="Price per unit")
    total_price: Decimal = Field(description="Total price for this line item")


class ReceiptExtraction(BaseModel):
    """Structured receipt data extracted by Gemini."""
    merchant_name: str = Field(
        description="Normalized merchant name (e.g., 'Walmart' not 'Wal-Mrt')"
    )
    purchase_date: date = Field(
        description="Purchase date in ISO format YYYY-MM-DD"
    )
    total_amount: Decimal = Field(description="Total amount paid")
    tax_amount: Decimal = Field(description="Tax amount")
    line_items: List[LineItemExtraction] = Field(
        description="List of purchased items"
    )

    @field_validator('merchant_name')
    @classmethod
    def normalize_merchant(cls, v: str) -> str:
        """Capitalize merchant name."""
        return v.strip().title()


# Database Models
class Receipt(BaseModel):
    """Receipt record for database."""
    id: uuid.UUID
    image_url: str
    merchant_name: Optional[str] = None
    purchase_date: Optional[date] = None
    total_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    status: Literal['pending', 'complete', 'manual_review']


class LineItem(BaseModel):
    """Line item record for database."""
    id: uuid.UUID
    receipt_id: uuid.UUID
    description: str
    category: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal
