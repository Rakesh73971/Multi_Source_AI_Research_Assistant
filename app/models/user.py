from sqlalchemy import Column,Integer,String,Boolean,TIMESTAMP,text
from app.db.database import Base
from sqlalchemy import Enum as SAEnum
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship


class UserRole(PyEnum):
    ADMIN = "admin"
    user = "USER"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True)
    full_name = Column(String,nullable=False)
    email = Column(String,unique=True,nullable=False)
    password = Column(String,nullable=False)
    role = Column(SAEnum(UserRole, values_callable=lambda x: [e.value for e in x]),default=UserRole.user, nullable=False)
    is_active = Column(Boolean,server_default='True',nullable=False)
    created = Column(TIMESTAMP(timezone=True),server_default=text('now()'),nullable=False)
    sessions = relationship('ResearchSession',back_populates='user')
    messages = relationship('ConversationMessage',back_populates='user')
