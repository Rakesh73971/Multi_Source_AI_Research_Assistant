from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.research_session import ResearchSession


def create_session_service(db: Session, session, current_user):
    db_session = ResearchSession(
        user_id=current_user.id,
        name=session.name,
        description=session.description,
        chroma_collection_db=session.chroma_collection_db,
        status=session.status,
        summary=session.summary,
        source_count=session.source_count,
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def get_sessions_service(db: Session, current_user):
    return db.query(ResearchSession).filter(
        ResearchSession.user_id == current_user.id
    ).all()


def get_session_service(db: Session, session_id: int, current_user):
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


def update_session_service(db: Session, session_id: int, update_session, current_user):
    session = get_session_service(db, session_id, current_user)
    update_data = update_session.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(session, key, value)

    db.commit()
    db.refresh(session)
    return session


def delete_session_service(db: Session, session_id: int, current_user):
    session = get_session_service(db, session_id, current_user)
    db.delete(session)
    db.commit()
    return None
