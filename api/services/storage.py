"""File storage operations for receipt images."""

import os
import uuid
from pathlib import Path
from config import settings


class StorageService:
    """Handles file storage operations."""

    @staticmethod
    def ensure_storage_directory():
        """Create storage directory if it doesn't exist."""
        Path(settings.STORAGE_PATH).mkdir(parents=True, exist_ok=True)
        print(f"✓ Storage directory ready: {settings.STORAGE_PATH}")

    @staticmethod
    def get_file_path(receipt_id: uuid.UUID, extension: str) -> str:
        """Generate file path for receipt image."""
        filename = f"{receipt_id}{extension}"
        return os.path.join(settings.STORAGE_PATH, filename)

    @staticmethod
    async def save_file(
        receipt_id: uuid.UUID,
        content: bytes,
        content_type: str
    ) -> str:
        """
        Save uploaded file to storage and return path.

        Args:
            receipt_id: UUID of the receipt
            content: File content as bytes
            content_type: MIME type (image/jpeg, image/png, application/pdf)

        Returns:
            Full file path where the file was saved
        """
        # Map content type to extension
        extension_map = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "application/pdf": ".pdf"
        }
        extension = extension_map.get(content_type, ".bin")

        file_path = StorageService.get_file_path(receipt_id, extension)

        # Write file
        with open(file_path, "wb") as f:
            f.write(content)

        return file_path

    @staticmethod
    def get_relative_url(file_path: str) -> str:
        """Convert file path to relative URL for database."""
        return file_path.replace(settings.STORAGE_PATH, "/storage/receipts")
