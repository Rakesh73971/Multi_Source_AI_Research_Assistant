from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel
from app.models.conversation_message import MessageRole, QueryType


class ConversionMessageCreate(BaseModel):
    session_id: int
    role: MessageRole
    content: str
    sources_used: Optional[list[dict[str, Any]]] = None
    query_type: QueryType = QueryType.QUESTION
    tokens_used: Optional[int] = None


class ConversionMessageUpdate(BaseModel):
    session_id: Optional[int] = None
    role: Optional[MessageRole] = None
    content: Optional[str] = None
    sources_used: Optional[list[dict[str, Any]]] = None
    query_type: Optional[QueryType] = None
    tokens_used: Optional[int] = None


class ConversionMessageResponse(ConversionMessageCreate):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
