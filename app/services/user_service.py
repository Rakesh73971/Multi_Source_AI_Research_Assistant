from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.utils import hash_password
from app.models.user import User


def _get_user_or_404(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return user


def create_user_service(db: Session, user):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    db_user = User(
        full_name=user.full_name,
        email=user.email,
        password=hash_password(user.password),
        role=user.role,
        is_active=user.is_active,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users_service(db: Session):
    return db.query(User).all()


def get_user_service(db: Session, user_id: int):
    return _get_user_or_404(db, user_id)


def update_user_service(db: Session, user_id: int, user_update):
    user = _get_user_or_404(db, user_id)
    update_data = user_update.model_dump(exclude_unset=True)

    if "email" in update_data:
        existing_user = db.query(User).filter(
            User.email == update_data["email"],
            User.id != user_id,
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

    if "password" in update_data and update_data["password"]:
        update_data["password"] = hash_password(update_data["password"])

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


def delete_user_service(db: Session, user_id: int):
    user = _get_user_or_404(db, user_id)
    db.delete(user)
    db.commit()
    return None
