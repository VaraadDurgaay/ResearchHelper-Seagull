"""
Pydantic Schemas for API requests and responses
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class PaperStatus(str, Enum):
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class PaperBase(BaseModel):
    title: str
    authors: List[str] = Field(default_factory=list)
    abstract: Optional[str] = None
    doi: Optional[str] = None
    publication_date: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PaperResponse(PaperBase):
    id: str
    pdf_path: Optional[str] = None
    pdf_url: Optional[str] = None
    upload_date: datetime
    workspace_id: str
    user_id: str
    status: PaperStatus
    
    class Config:
        from_attributes = True


class PaperListResponse(BaseModel):
    papers: List[PaperResponse]
    total: int


class ErrorResponse(BaseModel):
    detail: str
