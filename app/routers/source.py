from fastapi import APIRouter,Depends,status
from app.services.source_service import create_source_service,get_sources_service,get_source_service,delete_source_service
from sqlalchemy.orm import Session
from app.core.oauth2 import get_current_user
from app.schemas.source import SourceCreate,SourceResponse
from app.db.database import get_db
from typing import List


router = APIRouter(
    prefix="/sources",
    tags=["Sources"]
)


@router.put("/",status_code=status.HTTP_201_CREATED,response_model=SourceResponse)
def create_souce(source:SourceCreate,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    return create_source_service(db,source,current_user)


@router.get("/",status_code=status.HTTP_200_OK,response_model=List[SourceResponse])
def get_sources(db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    return get_sources_service(db)


@router.get("/{id}",status_code=status.HTTP_200_OK,response_model=SourceResponse)
def get_source(id:int,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    return get_source_service(db,id)


@router.delete("/{source_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_source(source_id:int,db:Session=Depends(get_db),current_user=Depends(get_current_user)):
    return delete_source_service(db,source_id)
