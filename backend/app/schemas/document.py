from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class DocumentCreate(BaseModel):
    title: str
    content: str
    source: Optional[str] = None
    metadata_info: Optional[Dict[str, Any]] = None

class DocumentChunkResponse(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    content: str
    metadata_info: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    id: str
    title: str
    source: Optional[str] = None
    content: str
    metadata_info: Optional[Dict[str, Any]] = None
    chunks_count: Optional[int] = 0
    created_at: datetime

    class Config:
        from_attributes = True

class SearchQuery(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(default=4, ge=1, le=20)
    score_threshold: float = Field(default=0.4, ge=0.0, le=1.0)

class SearchResult(BaseModel):
    document_id: str
    document_title: str
    source: Optional[str] = None
    content: str
    chunk_index: int
    score: float
