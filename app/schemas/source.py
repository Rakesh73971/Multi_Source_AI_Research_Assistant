from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SourceCreate(BaseModel):
    session_id: int
    source_type: str
    source_url: str
    file_name: str
    file_path: str
    title: str
    extracted_text: str
    chunk_count: int
    status: str
    task_id: str
    error_message: str

class SourceUpdate(BaseModel):
    session_id: Optional[int] = None
    source_type: Optional[str] = None
    source_url: Optional[str] = None
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    title: Optional[str] = None
    extracted_text: Optional[str] = None
    chunk_count: Optional[int] = None
    status: Optional[str] = None
    task_id: Optional[int] = None
    error_message: Optional[str] = None


class SourceResponse(SourceCreate):
    id: int
    user_id: int
    uploaded_at: datetime

    class Config:
        from_attributes = True