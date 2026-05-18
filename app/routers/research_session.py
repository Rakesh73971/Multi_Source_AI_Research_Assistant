from fastapi import APIRouter,Depends,status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.research_session import SessionCreate,SessionResponse
from app.services.session_service import create_session_service,get_sessions_service,get_session_service,delete_session_service
from app.core.oauth2 import get_current_user
from typing import List


router = APIRouter(
    prefix='/research_sessions',
    tags=["Research Session"]
)

@router.post("/",status_code=status.HTTP_201_CREATED,response_model=SessionResponse)
def create_session(session:SessionCreate,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    return create_session_service(db,session)



@router.get("/",status_code=status.HTTP_200_OK,response_model=List[SessionResponse])
def get_sessions(db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    return get_sessions_service(db)



@router.get("/{id}",status_code=status.HTTP_200_OK,response_model=SessionResponse)
def get_session(id:int,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    return get_session_service(db,id)



@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_session(id:int,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    return delete_session_service(db,id)
