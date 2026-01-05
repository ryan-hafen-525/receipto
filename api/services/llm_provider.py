"""LLM provider abstraction for multi-provider support."""

from abc import ABC, abstractmethod
from typing import Type
import asyncio
from pydantic import BaseModel

from models.schemas import ReceiptExtraction


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def extract_receipt_data(
        self,
        ocr_text: str,
        schema: Type[BaseModel] = ReceiptExtraction
    ) -> ReceiptExtraction:
        """Extract structured receipt data from OCR text."""
        pass


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        from google import genai
        self.client = genai.Client(api_key=api_key)
        self.model = model

    async def extract_receipt_data(
        self,
        ocr_text: str,
        schema: Type[BaseModel] = ReceiptExtraction
    ) -> ReceiptExtraction:
        from google.genai import types

        prompt = self._build_prompt(ocr_text)

        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
            )
        )

        return schema.model_validate_json(response.text)

    def _build_prompt(self, ocr_text: str) -> str:
        return f"""
You are a receipt data extraction expert. Extract structured information from this receipt OCR data.

IMPORTANT INSTRUCTIONS:
1. Normalize merchant names (e.g., "Wal-Mrt Super" → "Walmart")
2. Convert dates to ISO 8601 format (YYYY-MM-DD)
3. Extract all line items with descriptions, categories, quantities, and prices
4. Categorize items appropriately: Groceries, Dining, Transportation, Utilities, Entertainment, Healthcare, Clothing, Home & Garden, Personal Care, Shopping, Other
5. Ensure decimal precision for all monetary values
6. If quantities are not specified, assume 1

RECEIPT DATA:
{ocr_text}

Extract the complete structured data.
"""


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model

    async def extract_receipt_data(
        self,
        ocr_text: str,
        schema: Type[BaseModel] = ReceiptExtraction
    ) -> ReceiptExtraction:
        prompt = self._build_prompt(ocr_text)

        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a receipt data extraction expert."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        return schema.model_validate_json(response.choices[0].message.content)

    def _build_prompt(self, ocr_text: str) -> str:
        return f"""Extract structured information from this receipt OCR data.

IMPORTANT INSTRUCTIONS:
1. Normalize merchant names (e.g., "Wal-Mrt Super" → "Walmart")
2. Convert dates to ISO 8601 format (YYYY-MM-DD)
3. Extract all line items with descriptions, categories, quantities, and prices
4. Categorize items: Groceries, Dining, Transportation, Utilities, Entertainment, Healthcare, Clothing, Home & Garden, Personal Care, Shopping, Other
5. Ensure decimal precision for all monetary values
6. If quantities are not specified, assume 1

Return a JSON object with this structure:
{{
  "merchant_name": "string",
  "purchase_date": "YYYY-MM-DD",
  "total_amount": number,
  "tax_amount": number,
  "line_items": [
    {{
      "description": "string",
      "category": "string",
      "quantity": number,
      "unit_price": number,
      "total_price": number
    }}
  ]
}}

RECEIPT DATA:
{ocr_text}
"""


class AnthropicProvider(LLMProvider):
    """Anthropic Claude LLM provider."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    async def extract_receipt_data(
        self,
        ocr_text: str,
        schema: Type[BaseModel] = ReceiptExtraction
    ) -> ReceiptExtraction:
        prompt = self._build_prompt(ocr_text)

        response = await asyncio.to_thread(
            self.client.messages.create,
            model=self.model,
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract JSON from response
        content = response.content[0].text

        # Try to find JSON in the response
        import json
        import re

        # Look for JSON block
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            json_str = json_match.group()
            return schema.model_validate_json(json_str)

        raise ValueError("Could not extract JSON from Anthropic response")

    def _build_prompt(self, ocr_text: str) -> str:
        return f"""Extract structured information from this receipt OCR data.

IMPORTANT INSTRUCTIONS:
1. Normalize merchant names (e.g., "Wal-Mrt Super" → "Walmart")
2. Convert dates to ISO 8601 format (YYYY-MM-DD)
3. Extract all line items with descriptions, categories, quantities, and prices
4. Categorize items: Groceries, Dining, Transportation, Utilities, Entertainment, Healthcare, Clothing, Home & Garden, Personal Care, Shopping, Other
5. Ensure decimal precision for all monetary values
6. If quantities are not specified, assume 1

Return ONLY a valid JSON object (no markdown, no explanation) with this structure:
{{
  "merchant_name": "string",
  "purchase_date": "YYYY-MM-DD",
  "total_amount": number,
  "tax_amount": number,
  "line_items": [
    {{
      "description": "string",
      "category": "string",
      "quantity": number,
      "unit_price": number,
      "total_price": number
    }}
  ]
}}

RECEIPT DATA:
{ocr_text}
"""


async def get_llm_provider(
    provider: str,
    model: str,
    settings_service,
    conn
) -> LLMProvider:
    """
    Factory function to get the appropriate LLM provider.

    Args:
        provider: Provider name (gemini, openai, anthropic)
        model: Model ID
        settings_service: SettingsService class for fetching API keys
        conn: Database connection

    Returns:
        Configured LLM provider instance
    """
    if provider == "gemini":
        api_key = await settings_service.get_setting(conn, "google_api_key")
        if not api_key:
            # Fall back to environment variable
            from config import settings
            api_key = settings.GOOGLE_API_KEY
        if not api_key:
            raise ValueError("Google API key not configured")
        return GeminiProvider(api_key=api_key, model=model)

    elif provider == "openai":
        api_key = await settings_service.get_setting(conn, "openai_api_key")
        if not api_key:
            raise ValueError("OpenAI API key not configured")
        return OpenAIProvider(api_key=api_key, model=model)

    elif provider == "anthropic":
        api_key = await settings_service.get_setting(conn, "anthropic_api_key")
        if not api_key:
            raise ValueError("Anthropic API key not configured")
        return AnthropicProvider(api_key=api_key, model=model)

    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
