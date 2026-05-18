from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SessionCreate(BaseModel):
    name: str
    description: str
    chrome_collection_db: str
    status: str
    summary: str
    source_count: int

class SessionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    chrome_collection_db: Optional[str] = None
    status: Optional[str] = None
    summary: Optional[str] = None
    source_count: Optional[int] = None


class SessionResponse(SessionCreate):
    id: int
    user_id : int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True