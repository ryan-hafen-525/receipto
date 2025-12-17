from typing import Union
import os
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UploadResponse(BaseModel):
    receipt_id: str
    status: str
    message: str

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/receipts/upload", response_model=UploadResponse)
async def upload_receipt(file: UploadFile = File(...)):
    # 1. Validate file type
    allowed_types = ["image/jpeg", "image/png", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not supported. Please upload JPG, PNG or PDF."
        )

    # 2. Validate file size (e.g., max 10MB)
    MAX_SIZE = 10 * 1024 * 1024  # 10MB
    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds the 10MB limit."
        )
    
    try:
        # Simulate processing logic
        # In reality: save to storage, trigger LangGraph, etc.
        receipt_id = str(uuid.uuid4())
        
        return UploadResponse(
            receipt_id=receipt_id,
            status="pending",
            message="Receipt uploaded successfully and is now being processed."
        )
    except Exception as e:
        # Generic error handling for unexpected issues
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the upload."
        )
