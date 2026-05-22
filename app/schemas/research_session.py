from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.research_session import SessionStatus


class SessionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    chroma_collection_db: str
    status: SessionStatus = SessionStatus.ACTIVE
    summary: Optional[str] = None
    source_count: int = 0


class SessionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    chroma_collection_db: Optional[str] = None
    status: Optional[SessionStatus] = None
    summary: Optional[str] = None
    source_count: Optional[int] = None


class SessionResponse(SessionCreate):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
