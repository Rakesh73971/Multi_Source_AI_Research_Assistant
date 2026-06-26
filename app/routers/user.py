from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.oauth2 import get_admin_user, get_current_user
from app.db.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import (
    create_user_service,
    delete_user_service,
    get_user_service,
    get_users_service,
    update_user_service,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


def _ensure_self_or_admin(user_id: int, current_user):
    role_value = current_user.role.value if hasattr(current_user.role, "value") else current_user.role
    if current_user.id != user_id and role_value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this user",
        )


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user_service(db, user)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user=Depends(get_admin_user),
):
    return get_users_service(db)


@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _ensure_self_or_admin(user_id, current_user)
    return get_user_service(db, user_id)


@router.put("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponse)
@router.patch("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponse)
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _ensure_self_or_admin(user_id, current_user)
    return update_user_service(db, user_id, user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _ensure_self_or_admin(user_id, current_user)
    return delete_user_service(db, user_id)
