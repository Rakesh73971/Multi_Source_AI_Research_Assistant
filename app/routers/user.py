from fastapi import APIRouter,Depends,status
from app.db.database import get_db
from app.core.oauth2 import get_current_user
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate,UserResponse
from app.services.user_service import create_user_service,get_users_service,get_user_service,update_user_service,delete_user_service
from typing import List


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/",status_code=status.HTTP_201_CREATED,response_model=UserResponse)
def create_user(user:UserCreate,db:Session=Depends(get_db)):
    return create_user_service(db,user)



@router.get("/",status_code=status.HTTP_200_OK,response_model=List[UserResponse])
def get_users(db:Session=Depends(get_db)):
    return get_users_service(db)



@router.get("/{id}",status_code=status.HTTP_200_OK,response_model=UserResponse)
def get_user(id:int,db:Session=Depends(get_db)):
    return get_user_service(db,id)



@router.patch("/{id}",status_code=status.HTTP_202_ACCEPTED,response_model=UserResponse)
def update_user(id:int,user:UserCreate,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    return update_user_service(db,id,user)



@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id:int,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    return delete_user_service(db,id)
