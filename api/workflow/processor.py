"""High-level receipt processing workflow executor."""

import uuid
from workflow.graph import create_receipt_workflow
from workflow.state import ReceiptState


class ReceiptProcessor:
    """High-level processor for receipt workflow."""

    def __init__(self):
        self.workflow = create_receipt_workflow()

    async def process_receipt(
        self,
        receipt_id: uuid.UUID,
        image_path: str
    ) -> ReceiptState:
        """
        Execute the complete receipt processing workflow.

        Args:
            receipt_id: UUID of the receipt
            image_path: Path to the receipt image file

        Returns:
            Final workflow state
        """
        print(f"[Processor] Starting workflow for receipt: {receipt_id}")

        # Initialize state
        initial_state: ReceiptState = {
            'receipt_id': str(receipt_id),
            'image_path': image_path,
            'raw_textract_output': None,
            'cleaned_json': None,
            'validation_errors': [],
            'status': 'processing'
        }

        # Execute workflow
        final_state = await self.workflow.ainvoke(initial_state)

        print(f"[Processor] Workflow complete for {receipt_id}. Status: {final_state['status']}")

        return final_state


# Global instance
receipt_processor = ReceiptProcessor()
