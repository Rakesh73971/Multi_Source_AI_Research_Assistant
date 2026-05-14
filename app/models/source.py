from sqlalchemy import Column,Integer,String,ForeignKey,Text,TIMESTAMP,text
from sqlalchemy import Enum as SAEnum
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship
from app.db.database import Base


class SourceType(PyEnum):
    PDF = "pdf"
    URL = "url"
    YOUTUBE = "youtube"

class SourceStatus(PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer,primary_key=True)
    session_id = Column(Integer,ForeignKey('research_sessions.id'),nullable=False)
    user_id = Column(Integer,ForeignKey('users.id'),nullable=False)
    source_type = Column(SAEnum(SourceType,values_callable=lambda x: [e.value for e in x]),nullable=False)
    source_url = Column(String,nullable=True)
    file_name = Column(String,nullable=True)
    file_path = Column(String,nullable=True)
    title = Column(String,nullable=True)
    extracted_text = Column(Text,nullable=True)
    chunk_count = Column(Integer,default=0)
    status = Column(SAEnum(SourceStatus,values_callable=lambda x: [e.value for e in x]),
                    default=SourceStatus.PENDING,nullable=False)
    task_id = Column(String,nullable=True)
    error_message = Column(Text,nullable=True)
    uploaded_at = Column(TIMESTAMP(timezone=True),server_default=text('now()'),nullable=False)
    session = relationship('ResearchSession',back_populates='source')
