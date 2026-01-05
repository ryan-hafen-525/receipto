"""Pydantic models for settings and categories."""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from decimal import Decimal
from datetime import datetime
import uuid


# LLM Provider options
LLMProvider = Literal["gemini", "openai", "anthropic"]
Theme = Literal["light", "dark", "system"]


# Category Models
class CategoryBase(BaseModel):
    """Base category model."""
    name: str = Field(..., min_length=1, max_length=100)
    monthly_budget_limit: Optional[Decimal] = Field(None, ge=0)


class CategoryCreate(CategoryBase):
    """Model for creating a category."""
    pass


class CategoryUpdate(BaseModel):
    """Model for updating a category."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    monthly_budget_limit: Optional[Decimal] = Field(None, ge=0)


class Category(CategoryBase):
    """Category response model."""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Settings Models
class SettingsUpdate(BaseModel):
    """Model for updating multiple settings at once."""
    llm_provider: Optional[LLMProvider] = None
    llm_model: Optional[str] = None
    theme: Optional[Theme] = None
    aws_region: Optional[str] = None
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    google_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None


class SettingsResponse(BaseModel):
    """Response model for settings (masks sensitive values)."""
    llm_provider: str = "gemini"
    llm_model: str = "gemini-2.0-flash"
    theme: str = "system"
    aws_region: str = "us-west-2"
    # Masked API keys (only show if configured)
    aws_access_key_configured: bool = False
    aws_secret_key_configured: bool = False
    google_api_key_configured: bool = False
    openai_api_key_configured: bool = False
    anthropic_api_key_configured: bool = False


class APIKeyUpdate(BaseModel):
    """Model for updating API keys."""
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: Optional[str] = None
    google_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None


class LLMConfigUpdate(BaseModel):
    """Model for updating LLM configuration."""
    provider: LLMProvider
    model: str


# Available models per provider
LLM_MODELS = {
    "gemini": [
        {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash"},
        {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro"},
        {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash"},
    ],
    "openai": [
        {"id": "gpt-4o", "name": "GPT-4o"},
        {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
        {"id": "gpt-4-turbo", "name": "GPT-4 Turbo"},
    ],
    "anthropic": [
        {"id": "claude-sonnet-4-20250514", "name": "Claude Sonnet 4"},
        {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku"},
        {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet"},
    ],
}


class LLMModelsResponse(BaseModel):
    """Response with available LLM models."""
    providers: dict = Field(default_factory=lambda: LLM_MODELS)
