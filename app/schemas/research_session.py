from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict
from app.models.research_session import SessionStatus


class SessionBase(BaseModel):
    description: Optional[str] = None
    status: Optional[SessionStatus] = None
    summary: Optional[str] = None
    source_count: Optional[int] = None


class SessionCreate(SessionBase):
    name: str
    chroma_collection_db: str
    status: SessionStatus = SessionStatus.ACTIVE
    source_count: int = 0


class SessionUpdate(SessionBase):
    name: Optional[str] = None
    chroma_collection_db: Optional[str] = None


class SessionResponse(SessionCreate):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AskRequest(BaseModel):
    question: str
    top_k: int = 4
    source_id: Optional[int] = None


class AskResponse(BaseModel):
    session_id: int
    question: str
    answer: str
    sources: list[dict[str, Any]]
