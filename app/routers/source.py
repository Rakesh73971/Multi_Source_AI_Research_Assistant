from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.oauth2 import get_current_user
from app.db.database import get_db
from app.schemas.source import SourceCreate, SourceResponse, SourceUpdate
from app.services.source_service import (
    create_source_service,
    delete_source_service,
    get_source_service,
    get_sources_service,
    update_source_service,
)


router = APIRouter(
    prefix="/sources",
    tags=["Sources"],
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SourceResponse)
def create_source(
    source: SourceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_source_service(db, source, current_user)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[SourceResponse])
def get_sources(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_sources_service(db, current_user)


@router.get("/{source_id}", status_code=status.HTTP_200_OK, response_model=SourceResponse)
def get_source(
    source_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_source_service(db, source_id, current_user)


@router.put("/{source_id}", status_code=status.HTTP_200_OK, response_model=SourceResponse)
def update_complete_source(
    source_id: int,
    source: SourceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return update_source_service(db, source_id, source, current_user)


@router.patch("/{source_id}", status_code=status.HTTP_200_OK, response_model=SourceResponse)
def update_partial_source(
    source_id: int,
    source: SourceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return update_source_service(db, source_id, source, current_user)


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(
    source_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return delete_source_service(db, source_id, current_user)
