from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict
from app.models.source import SourceStatus, SourceType


class SourceBase(BaseModel):
    source_url: Optional[str] = None
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    title: Optional[str] = None
    extracted_text: Optional[str] = None
    chunk_count: Optional[int] = None
    status: Optional[SourceStatus] = None
    task_id: Optional[str] = None
    error_message: Optional[str] = None


class SourceCreate(SourceBase):
    session_id: int
    source_type: SourceType
    chunk_count: int = 0
    status: SourceStatus = SourceStatus.PENDING


class SourceUpdate(SourceBase):
    session_id: Optional[int] = None
    source_type: Optional[SourceType] = None


class TextSourceCreate(BaseModel):
    session_id: int
    source_url: str
    title: Optional[str] = None


class UrlSourceCreate(TextSourceCreate):
    pass


class YoutubeSourceCreate(TextSourceCreate):
    pass


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None


class SourceResponse(SourceCreate):
    id: int
    user_id: int
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)
