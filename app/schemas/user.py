from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


from app.models.user import UserRole


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER
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

    model_config = ConfigDict(from_attributes=True)


class TokenData(BaseModel):
    id: Optional[int] = None
