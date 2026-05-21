from sqlalchemy import Column,Integer,String,ForeignKey,Text,TIMESTAMP,text
from sqlalchemy import Enum as SAEnum
from enum import Enum as PyEnum
from app.db.database import Base
from sqlalchemy.orm import relationship

class SessionStatus(PyEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class ResearchSession(Base):
    __tablename__ = "research_sessions"

    id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey("users.id"),nullable=False)
    name = Column(String,nullable=False)
    description = Column(Text,nullable=True)
    chroma_collection_db = Column(String,unique=True,nullable=False)
    status = Column(SAEnum(SessionStatus,values_callable=lambda x:[e.value for e in x]),default=SessionStatus.ACTIVE,nullable=False)
    summary = Column(Text,nullable=True)
    source_count = Column(Integer,default=0,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),server_default=text('now()'),nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True),server_default=text('now()'),server_onupdate=text('now()'),nullable=False)
    user = relationship('User',back_populates='session')
    sources = relationship('Source',back_populates='session')
    messages = relationship('ConversationMessage',back_populates='session')
