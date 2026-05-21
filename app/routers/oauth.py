from fastapi import APIRouter,status,Depends,HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.db.database import get_db
from app.core.utils import verify_passwords,hash_password
from app.models.user import User
from app.core.oauth2 import create_access_token

router = APIRouter(
    prefix="/login",
    tags=["Authentication"]
)

@router.post("/")
def login(user_credentials:OAuth2PasswordRequestForm=Depends(),
          db:Session=Depends(get_db)
    ):
    user = db.query(User).filter(User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Invalid Credentials')
    
    if not verify_passwords(user_credentials.password,user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials"
        )
    
    access_token = create_access_token(data={"user_id":user.id})
    
    return {
        "access_token":access_token,
        "token_type":"Bearer"
    }