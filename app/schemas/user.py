from pydantic import BaseModel,EmailStr
from typing import Optional
from datetime import datetime
from typing import Optional
from enum import Enum

class UserRole(str,Enum):
    admin = 'admin'
    user = 'user'


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole
    is_active: Optional[bool] = True
    

class UserResponse(BaseModel):
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    created: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name:Optional[str] = None
    email:Optional[str] = None
    role:Optional[str] = None
    is_active:Optional[bool] = None
    

class TokenData(BaseModel):
    id:Optional[int] = None