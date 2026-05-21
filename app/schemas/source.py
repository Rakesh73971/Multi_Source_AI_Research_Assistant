from pydantic import BaseModel
from datetime import datetime

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


class SourceResponse(SourceCreate):
    id: int
    user_id: int
    uploaded_at: datetime

    class Config:
        from_attributes = True