"""LangGraph workflow nodes for receipt processing."""

import asyncio
import json
from decimal import Decimal
from typing import Any
import boto3
from tenacity import retry, stop_after_attempt, wait_exponential
from config import settings
from models.schemas import ReceiptExtraction
from models.database import db_manager
from services.settings_ops import SettingsService
from services.llm_provider import get_llm_provider
from workflow.state import ReceiptState


class WorkflowNodes:
    """Contains all LangGraph workflow nodes."""

    def __init__(self):
        # Initialize AWS Textract client (sync)
        # Note: Will be re-initialized with DB settings if available
        self.textract = boto3.client(
            'textract',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

    async def _get_textract_client(self):
        """Get Textract client with settings from database."""
        async with db_manager.acquire() as conn:
            aws_key = await SettingsService.get_setting(conn, "aws_access_key_id")
            aws_secret = await SettingsService.get_setting(conn, "aws_secret_access_key")
            aws_region = await SettingsService.get_setting(conn, "aws_region")

        # Use DB settings if available, otherwise fall back to env vars
        return boto3.client(
            'textract',
            aws_access_key_id=aws_key or settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=aws_secret or settings.AWS_SECRET_ACCESS_KEY,
            region_name=aws_region or settings.AWS_REGION
        )

    @retry(
        stop=stop_after_attempt(settings.TEXTRACT_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def ocr_node(self, state: ReceiptState) -> ReceiptState:
        """
        Node 1: Extract text from receipt using AWS Textract AnalyzeExpense.

        Uses AnalyzeExpense (not DetectDocumentText) for receipt-specific extraction.
        """
        print(f"[OCR Node] Processing receipt: {state['receipt_id']}")

        try:
            # Get Textract client with current settings
            textract_client = await self._get_textract_client()

            # Read image file
            with open(state['image_path'], 'rb') as image_file:
                image_bytes = image_file.read()

            # Call Textract AnalyzeExpense in thread pool (it's sync)
            response = await asyncio.to_thread(
                textract_client.analyze_expense,
                Document={'Bytes': image_bytes}
            )

            state['raw_textract_output'] = response
            print(f"[OCR Node] Textract analysis complete for {state['receipt_id']}")

        except Exception as e:
            state['validation_errors'].append(f"OCR Error: {str(e)}")
            state['status'] = 'review_required'
            print(f"[OCR Node] Error: {e}")

        return state

    def _format_textract_for_llm(self, textract_output: dict) -> str:
        """
        Convert Textract AnalyzeExpense output to readable text for LLM.

        AnalyzeExpense returns ExpenseDocuments with:
        - SummaryFields (merchant, total, tax, date)
        - LineItemGroups (individual items)
        """
        formatted_text = "=== RECEIPT DATA ===\n\n"

        for doc in textract_output.get('ExpenseDocuments', []):
            # Summary fields
            formatted_text += "SUMMARY FIELDS:\n"
            for field in doc.get('SummaryFields', []):
                field_type = field.get('Type', {}).get('Text', 'Unknown')
                value = field.get('ValueDetection', {}).get('Text', '')
                formatted_text += f"- {field_type}: {value}\n"

            formatted_text += "\nLINE ITEMS:\n"
            # Line items
            for group in doc.get('LineItemGroups', []):
                for item_idx, item in enumerate(group.get('LineItems', []), 1):
                    formatted_text += f"\nItem {item_idx}:\n"
                    for expense_field in item.get('LineItemExpenseFields', []):
                        field_type = expense_field.get('Type', {}).get('Text', 'Unknown')
                        value = expense_field.get('ValueDetection', {}).get('Text', '')
                        formatted_text += f"  - {field_type}: {value}\n"

        return formatted_text

    @retry(
        stop=stop_after_attempt(settings.GEMINI_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def extraction_node(self, state: ReceiptState) -> ReceiptState:
        """
        Node 2: Use configured LLM to extract structured data from OCR output.

        Dynamically selects LLM provider based on database settings.
        """
        print(f"[Extraction Node] Processing receipt: {state['receipt_id']}")

        if not state.get('raw_textract_output'):
            state['validation_errors'].append("No OCR data available")
            state['status'] = 'review_required'
            return state

        try:
            # Format Textract output for LLM
            ocr_text = self._format_textract_for_llm(state['raw_textract_output'])

            # Get LLM provider and model from settings
            async with db_manager.acquire() as conn:
                provider_name = await SettingsService.get_setting(conn, "llm_provider") or "gemini"
                model_name = await SettingsService.get_setting(conn, "llm_model") or "gemini-2.0-flash"

                # Get configured LLM provider
                llm_provider = await get_llm_provider(
                    provider=provider_name,
                    model=model_name,
                    settings_service=SettingsService,
                    conn=conn
                )

            print(f"[Extraction Node] Using {provider_name}/{model_name}")

            # Extract receipt data using configured provider
            extracted_data = await llm_provider.extract_receipt_data(ocr_text)
            state['cleaned_json'] = extracted_data
            print(f"[Extraction Node] Extraction complete for {state['receipt_id']}")

        except Exception as e:
            state['validation_errors'].append(f"Extraction Error: {str(e)}")
            state['status'] = 'review_required'
            print(f"[Extraction Node] Error: {e}")

        return state

    async def validation_node(self, state: ReceiptState) -> ReceiptState:
        """
        Node 3: Validate extracted data.

        Checks:
        1. All required fields present
        2. Sum(line_items) + tax ≈ total (within tolerance)
        """
        print(f"[Validation Node] Validating receipt: {state['receipt_id']}")

        if not state.get('cleaned_json'):
            state['validation_errors'].append("No extracted data to validate")
            state['status'] = 'review_required'
            return state

        extraction = state['cleaned_json']
        errors = []

        # Check required fields
        if not extraction.merchant_name:
            errors.append("Missing merchant name")
        if not extraction.purchase_date:
            errors.append("Missing purchase date")
        if not extraction.line_items:
            errors.append("No line items found")

        # Validate sum
        line_items_sum = sum(item.total_price for item in extraction.line_items)
        expected_total = line_items_sum + extraction.tax_amount
        tolerance = extraction.total_amount * Decimal(str(settings.VALIDATION_TOLERANCE))

        if abs(expected_total - extraction.total_amount) > tolerance:
            errors.append(
                f"Sum validation failed: Line items ({line_items_sum}) + "
                f"Tax ({extraction.tax_amount}) = {expected_total}, "
                f"but total is {extraction.total_amount}"
            )

        if errors:
            state['validation_errors'].extend(errors)
            state['status'] = 'review_required'
            print(f"[Validation Node] Validation failed: {errors}")
        else:
            state['status'] = 'complete'
            print(f"[Validation Node] Validation successful for {state['receipt_id']}")

        return state

    async def persistence_node(self, state: ReceiptState) -> ReceiptState:
        """
        Node 4: Save validated data to PostgreSQL.

        Uses asyncpg to save receipt and line items.
        """
        import uuid
        from models.database import db_manager
        from services.database_ops import DatabaseService

        print(f"[Persistence Node] Saving receipt: {state['receipt_id']}")

        if state['status'] != 'complete' or not state.get('cleaned_json'):
            # Update status to manual_review
            async with db_manager.acquire() as conn:
                await DatabaseService.update_receipt_status(
                    conn,
                    uuid.UUID(state['receipt_id']),
                    'manual_review'
                )
            print(f"[Persistence Node] Receipt marked for manual review: {state['receipt_id']}")
            return state

        try:
            async with db_manager.acquire() as conn:
                # Use transaction for atomicity
                async with conn.transaction():
                    await DatabaseService.save_receipt_data(
                        conn,
                        uuid.UUID(state['receipt_id']),
                        state['cleaned_json']
                    )

            print(f"[Persistence Node] Successfully saved receipt: {state['receipt_id']}")

        except Exception as e:
            state['validation_errors'].append(f"Database Error: {str(e)}")
            state['status'] = 'review_required'
            print(f"[Persistence Node] Error: {e}")

            # Update status in database
            async with db_manager.acquire() as conn:
                await DatabaseService.update_receipt_status(
                    conn,
                    uuid.UUID(state['receipt_id']),
                    'manual_review'
                )

        return state
