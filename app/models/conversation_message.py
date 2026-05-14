from sqlalchemy import Column,Integer,ForeignKey,Text,JSON,TIMESTAMP,text
from sqlalchemy import Enum as SAEnum
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship
from app.db.database import Base

class MessageRole(PyEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class QueryType(PyEnum):
    QUESTION = "question"
    SUMMARY = "summary"
    COMPARISON = "comparison"


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(Integer,primary_key=True)
    session_id = Column(Integer,ForeignKey('research_sessions.id'),nullable=False)
    user_id = Column(Integer,ForeignKey('users.id'),nullable=False)
    role = Column(SAEnum(MessageRole,values_callable=lambda x:[e.value for e in x]),nullable=False)
    content = Column(Text,nullable=False)
    sources_used = Column(JSON,nullable=True)
    query_type = Column(SAEnum(QueryType,values_callable=lambda x:[e.value for e in x]),default=QueryType.QUESTION,nullable=False)
    tokens_used = Column(Integer,nullable=True)
    created_at = Column(TIMESTAMP(timezone=True),server_default=text('now()'),nullable=False)
    session = relationship('ResearchSession',back_populates='messages')
    user = relationship('User',back_populates='messages')
    

