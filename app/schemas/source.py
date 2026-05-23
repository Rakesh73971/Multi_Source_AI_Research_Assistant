from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel
from app.models.source import SourceStatus, SourceType


class SourceCreate(BaseModel):
    session_id: int
    source_type: SourceType
    source_url: Optional[str] = None
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    title: Optional[str] = None
    extracted_text: Optional[str] = None
    chunk_count: int = 0
    status: SourceStatus = SourceStatus.PENDING
    task_id: Optional[str] = None
    error_message: Optional[str] = None


class UrlSourceCreate(BaseModel):
    session_id: int
    source_url: str
    title: Optional[str] = None


class YoutubeSourceCreate(BaseModel):
    session_id: int
    source_url: str
    title: Optional[str] = None


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None


class SourceUpdate(BaseModel):
    session_id: Optional[int] = None
    source_type: Optional[SourceType] = None
    source_url: Optional[str] = None
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    title: Optional[str] = None
    extracted_text: Optional[str] = None
    chunk_count: Optional[int] = None
    status: Optional[SourceStatus] = None
    task_id: Optional[str] = None
    error_message: Optional[str] = None


class SourceResponse(SourceCreate):
    id: int
    user_id: int
    uploaded_at: datetime

    class Config:
        from_attributes = True
