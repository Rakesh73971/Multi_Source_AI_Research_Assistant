from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    admin = "admin"
    user = "user"


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.user
    is_active: bool = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created: datetime

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    id: Optional[int] = None
