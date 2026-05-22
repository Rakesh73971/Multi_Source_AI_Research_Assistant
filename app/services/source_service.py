from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.research_session import ResearchSession
from app.models.source import Source


def _get_owned_session(db: Session, session_id: int, current_user):
    session = db.query(ResearchSession).filter(
        ResearchSession.id == session_id,
        ResearchSession.user_id == current_user.id,
    ).first()
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Research session with id {session_id} not found",
        )
    return session


def create_source_service(db: Session, source, current_user):
    _get_owned_session(db, source.session_id, current_user)

    db_source = Source(
        session_id=source.session_id,
        user_id=current_user.id,
        source_type=source.source_type,
        source_url=source.source_url,
        file_name=source.file_name,
        file_path=source.file_path,
        title=source.title,
        extracted_text=source.extracted_text,
        chunk_count=source.chunk_count,
        status=source.status,
        task_id=source.task_id,
        error_message=source.error_message,
    )
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


def get_sources_service(db: Session, current_user):
    return db.query(Source).filter(Source.user_id == current_user.id).all()


def get_source_service(db: Session, source_id: int, current_user):
    source = db.query(Source).filter(
        Source.id == source_id,
        Source.user_id == current_user.id,
    ).first()
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with id {source_id} not found",
        )
    return source


def update_source_service(db: Session, source_id: int, update_source, current_user):
    source = get_source_service(db, source_id, current_user)
    update_data = update_source.model_dump(exclude_unset=True)

    if "session_id" in update_data:
        _get_owned_session(db, update_data["session_id"], current_user)

    for key, value in update_data.items():
        setattr(source, key, value)

    db.commit()
    db.refresh(source)
    return source


def delete_source_service(db: Session, source_id: int, current_user):
    source = get_source_service(db, source_id, current_user)
    db.delete(source)
    db.commit()
    return None
