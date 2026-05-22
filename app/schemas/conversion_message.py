from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ConversionMessageCreate(BaseModel):
    session_id: int
    role: str
    content: str
    sources_used: str
    query_type: str
    tokens_used: int

class ConversionMessageUpdate(BaseModel):
    session_id: Optional[int] = None
    role: Optional[str] = None
    content: Optional[str] = None
    sources_used: Optional[str] = None
    query_type: Optional[str] = None
    tokens_used: Optional[str] = None


class ConversionMessageResponse(ConversionMessageCreate):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True