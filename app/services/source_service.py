from sqlalchemy.orm import Session
from app.models.source import Source
from fastapi import Depends,HTTPException,status
from app.core.oauth2 import get_current_user


def create_source_service(source,db:Session,current_user=Depends(get_current_user)):
    db_source = Source(
        session_id = source.session_id,
        user_id = current_user.id,
        source_type = source.source_type,
        source_url = source.source_url,
        file_name = source.file_name,
        file_path = source.file_path,
        title = source.title,
        extracted_text = source.extracted_text,
        chunk_count = source.chunk_count,
        status = source.status,
        task_id = source.task_id,
        error_message = source.error_message
    )
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


def get_sources_service(db:Session):
    sources = db.query(Source).all()
    return sources


def get_source_service(db:Session,source_id):
    source = db.query(Source).filter(Source.id == source_id).first()
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"source with id {source_id} not found")
    return source


def delete_source_service(db:Session,source_id):
    source = db.query(Source).filter(Source.id == source_id).first()
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"source with id {source_id} not found")
    db.delete(source)
    db.commit()
    return None