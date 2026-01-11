"""
Papers API Endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List
from datetime import datetime
import os
import uuid
import shutil
from pathlib import Path

from app.models.schemas import PaperResponse, PaperListResponse, PaperStatus
from app.api.dependencies import get_current_user_id, get_current_workspace_id
from app.config import settings

router = APIRouter()


@router.post("/", response_model=PaperResponse)
async def upload_paper(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    workspace_id: str = Depends(get_current_workspace_id)
):
    """
    Upload a PDF file.
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )
    
    # Validate file size (basic check - FastAPI will handle most of this)
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > settings.max_upload_size:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds maximum allowed size of {settings.max_upload_size / (1024*1024):.1f}MB"
        )
    
    if file_size == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )
    
    file_path = None
    try:
        # Generate unique file ID
        paper_id = str(uuid.uuid4())
        
        # Create filename with paper ID
        file_extension = Path(file.filename).suffix
        saved_filename = f"{paper_id}{file_extension}"
        file_path = os.path.join(settings.upload_dir, saved_filename)
        
        # Save file
        os.makedirs(settings.upload_dir, exist_ok=True)
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # For now, extract basic metadata from filename
        # TODO: Implement actual PDF parsing to extract title, authors, etc.
        title = Path(file.filename).stem  # Use filename without extension as title
        
        # Create response
        paper_response = PaperResponse(
            id=paper_id,
            title=title,
            authors=[],  # TODO: Extract from PDF
            abstract=None,  # TODO: Extract from PDF
            pdf_path=file_path,
            pdf_url=None,  # TODO: Generate URL if serving files
            upload_date=datetime.utcnow(),
            workspace_id=workspace_id,
            user_id=user_id,
            status=PaperStatus.READY,  # TODO: Set to PROCESSING and process in background
            metadata={
                "original_filename": file.filename,
                "file_size": file_size,
            }
        )
        
        return paper_response
        
    except Exception as e:
        # Clean up file if something went wrong
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {str(e)}"
        )


@router.get("/", response_model=PaperListResponse)
async def list_papers():
    """
    List all papers.
    """
    # TODO: Implement actual paper listing from database
    return PaperListResponse(papers=[], total=0)


@router.get("/{paper_id}", response_model=PaperResponse)
async def get_paper(paper_id: str):
    """
    Get a single paper by ID.
    """
    # TODO: Implement actual paper retrieval from database
    raise HTTPException(status_code=404, detail="Paper not found")


@router.delete("/{paper_id}")
async def delete_paper(paper_id: str):
    """
    Delete a paper.
    """
    # TODO: Implement actual paper deletion
    return {"message": "Paper deleted successfully"}
