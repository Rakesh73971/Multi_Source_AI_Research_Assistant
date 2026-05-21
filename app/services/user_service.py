from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.models.user import User
from app.core.utils import hash_password

def create_user_service(db:Session,user):
    db_user = User(
        full_name = user.full_name,
        email=user.email,
        password = hash_password(user.password),
        role = user.role,
        is_active = user.is_active if user.is_active is not None else True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users_service(db:Session):
    users = db.query(User).all()
    return users

def get_user_service(db:Session,id):
    user = db.query(User).filter(User.id ==id ).first()
    return user


def update_user_service(db: Session, user_id: int, user_update):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["password"] = hash_password(update_data["password"])

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user

def delete_user_service(db:Session,id):
    user = db.query(User).filter(User.id == id).first()
    db.delete(user)
    db.commit()
    return None