from fastapi import HTTPException,status,Depends
from app.core.oauth2 import get_current_user
from app.models.research_session import ResearchSession
from sqlalchemy.orm import Session

def create_session_service(db:Session,session,current_user=Depends(get_current_user)):
    db_session = ResearchSession(
        user_id = current_user.id,
        name=session.name,
        description=session.description,
        chroma_collection_db=session.chroma_collection_db,
        status=session.status,
        summary=session.summary,
        source_count=session.source_count
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_sessions_service(db:Session):
    sessions = db.query(ResearchSession).all()
    return sessions

def get_session_service(db:Session,id):
    session = db.query(ResearchSession).filter(ResearchSession.id == id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f" Research Session with id {id} not found")
    return session

def delete_session_service(db:Session,id):
    session = db.query(ResearchSession).filter(ResearchSession.id == id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Research Session with id {id} not found")
    db.delete(session)
    db.commit()
    return None