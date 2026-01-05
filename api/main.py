"""FastAPI application for Receipto receipt processing."""

from contextlib import asynccontextmanager
import os
import uuid
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from models.database import db_manager
from models.schemas import UploadResponse
from models.settings_schemas import (
    CategoryCreate, CategoryUpdate, Category,
    SettingsUpdate, SettingsResponse,
    LLMConfigUpdate, APIKeyUpdate, LLMModelsResponse, LLM_MODELS
)
from services.storage import StorageService
from services.database_ops import DatabaseService
from services.settings_ops import SettingsService, CategoryService
from workflow.processor import receipt_processor


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI startup/shutdown.

    Initializes:
    - Database connection pool
    - Storage directory
    - LangGraph workflow
    """
    # Startup


    print("🚀 Starting Receipto API...")

    # Initialize database pool
    await db_manager.connect()

    # Ensure storage directory exists
    StorageService.ensure_storage_directory()

    print("✅ Receipto API ready")

    yield

    # Shutdown
    print("🛑 Shutting down Receipto API...")
    await db_manager.disconnect()
    print("✅ Receipto API stopped")


# Create FastAPI app with lifespan
app = FastAPI(
    title="Receipto API",
    description="Receipt processing API with AWS Textract and Google Gemini",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "Receipto"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check including dependencies."""
    health_status = {
        "status": "healthy",
        "database": "unknown",
        "storage": "unknown"
    }

    # Check database
    try:
        async with db_manager.acquire() as conn:
            await conn.fetchval("SELECT 1")
        health_status["database"] = "healthy"
    except Exception as e:
        health_status["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"

    # Check storage
    if os.path.exists(settings.STORAGE_PATH):
        health_status["storage"] = "healthy"
    else:
        health_status["storage"] = "unhealthy: directory not found"
        health_status["status"] = "unhealthy"

    return health_status


async def process_receipt_background(receipt_id: uuid.UUID, file_path: str):
    """
    Background task to process receipt through LangGraph workflow.

    This runs asynchronously to prevent upload endpoint timeout.
    """
    try:
        await receipt_processor.process_receipt(receipt_id, file_path)
    except Exception as e:
        print(f"❌ Background processing error for {receipt_id}: {e}")
        # Update receipt status to manual_review on error
        async with db_manager.acquire() as conn:
            await DatabaseService.update_receipt_status(
                conn, receipt_id, 'manual_review'
            )


@app.post("/receipts/upload", response_model=UploadResponse)
async def upload_receipt(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Upload receipt image/PDF for processing.

    Steps:
    1. Validate file type and size
    2. Generate receipt ID
    3. Save file to storage
    4. Insert initial DB record with status='pending'
    5. Trigger background processing task
    6. Return immediately with receipt ID
    """
    # 1. Validate file type
    allowed_types = ["image/jpeg", "image/png", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not supported. Please upload JPG, PNG or PDF."
        )

    # 2. Validate file size (max 10MB)
    MAX_SIZE = 10 * 1024 * 1024  # 10MB
    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds the 10MB limit."
        )

    try:
        # 3. Generate receipt ID
        receipt_id = uuid.uuid4()

        # 4. Save file to storage
        file_path = await StorageService.save_file(
            receipt_id,
            contents,
            file.content_type
        )
        image_url = StorageService.get_relative_url(file_path)

        # 5. Insert initial database record
        async with db_manager.acquire() as conn:
            await DatabaseService.create_initial_receipt(
                conn, receipt_id, image_url
            )

        # 6. Trigger background processing
        background_tasks.add_task(
            process_receipt_background,
            receipt_id,
            file_path
        )

        return UploadResponse(
            receipt_id=str(receipt_id),
            status="pending",
            message="Receipt uploaded successfully and is now being processed."
        )

    except Exception as e:
        print(f"❌ Upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the upload."
        )


# =============================================================================
# Settings Endpoints
# =============================================================================

@app.get("/settings", response_model=SettingsResponse)
async def get_settings():
    """Get all application settings."""
    async with db_manager.acquire() as conn:
        return await SettingsService.get_all_settings(conn)


@app.patch("/settings", response_model=SettingsResponse)
async def update_settings(updates: SettingsUpdate):
    """Update application settings."""
    async with db_manager.acquire() as conn:
        await SettingsService.update_settings(conn, updates)
        return await SettingsService.get_all_settings(conn)


@app.patch("/settings/api-keys", response_model=SettingsResponse)
async def update_api_keys(updates: APIKeyUpdate):
    """Update API keys."""
    settings_update = SettingsUpdate(**updates.model_dump(exclude_none=True))
    async with db_manager.acquire() as conn:
        await SettingsService.update_settings(conn, settings_update)
        return await SettingsService.get_all_settings(conn)


@app.patch("/settings/llm", response_model=SettingsResponse)
async def update_llm_config(config: LLMConfigUpdate):
    """Update LLM provider and model configuration."""
    # Validate model is valid for provider
    valid_models = [m["id"] for m in LLM_MODELS.get(config.provider, [])]
    if config.model not in valid_models:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid model '{config.model}' for provider '{config.provider}'"
        )

    updates = SettingsUpdate(llm_provider=config.provider, llm_model=config.model)
    async with db_manager.acquire() as conn:
        await SettingsService.update_settings(conn, updates)
        return await SettingsService.get_all_settings(conn)


@app.get("/llm/models", response_model=LLMModelsResponse)
async def get_llm_models():
    """Get available LLM providers and models."""
    return LLMModelsResponse()


# =============================================================================
# Categories Endpoints
# =============================================================================

@app.get("/categories", response_model=List[Category])
async def get_categories():
    """Get all categories."""
    async with db_manager.acquire() as conn:
        categories = await CategoryService.get_all_categories(conn)
        return categories


@app.post("/categories", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate):
    """Create a new category."""
    async with db_manager.acquire() as conn:
        # Check for duplicate name
        if await CategoryService.category_exists(conn, category.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category '{category.name}' already exists"
            )

        return await CategoryService.create_category(conn, category)


@app.get("/categories/{category_id}", response_model=Category)
async def get_category(category_id: uuid.UUID):
    """Get a category by ID."""
    async with db_manager.acquire() as conn:
        category = await CategoryService.get_category(conn, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        return category


@app.patch("/categories/{category_id}", response_model=Category)
async def update_category(category_id: uuid.UUID, updates: CategoryUpdate):
    """Update a category."""
    async with db_manager.acquire() as conn:
        # Check category exists
        existing = await CategoryService.get_category(conn, category_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

        # Check for duplicate name if name is being updated
        if updates.name and updates.name != existing["name"]:
            if await CategoryService.category_exists(conn, updates.name, exclude_id=category_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category '{updates.name}' already exists"
                )

        result = await CategoryService.update_category(conn, category_id, updates)
        return result


@app.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: uuid.UUID):
    """Delete a category."""
    async with db_manager.acquire() as conn:
        deleted = await CategoryService.delete_category(conn, category_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
