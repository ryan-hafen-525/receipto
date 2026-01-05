"""LangGraph workflow state definition."""

from typing import TypedDict, Literal, Optional
from models.schemas import ReceiptExtraction


class ReceiptState(TypedDict):
    """LangGraph workflow state for receipt processing."""
    receipt_id: str
    image_path: str
    raw_textract_output: Optional[dict]
    cleaned_json: Optional[ReceiptExtraction]
    validation_errors: list[str]
    status: Literal['processing', 'review_required', 'complete']
