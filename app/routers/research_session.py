from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.oauth2 import get_current_user
from app.db.database import get_db
from app.schemas.research_session import (
    AskRequest,
    AskResponse,
    SessionCreate,
    SessionResponse,
    SessionUpdate,
)
from app.services.session_service import (
    ask_session_question_service,
    create_session_service,
    delete_session_service,
    get_session_service,
    get_sessions_service,
    update_session_service,
)


router = APIRouter(
    prefix="/research_sessions",
    tags=["Research Session"],
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SessionResponse)
def create_session(
    session: SessionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_session_service(db, session, current_user)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[SessionResponse])
def get_sessions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_sessions_service(db, current_user)


@router.get("/{session_id}", status_code=status.HTTP_200_OK, response_model=SessionResponse)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_session_service(db, session_id, current_user)


@router.post("/{session_id}/ask", status_code=status.HTTP_200_OK, response_model=AskResponse)
def ask_session_question(
    session_id: int,
    request: AskRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ask_session_question_service(
        db=db,
        session_id=session_id,
        question=request.question,
        top_k=request.top_k,
        current_user=current_user,
    )


@router.put("/{session_id}", status_code=status.HTTP_200_OK, response_model=SessionResponse)
def update_complete_session(
    session_id: int,
    session: SessionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return update_session_service(db, session_id, session, current_user)


@router.patch("/{session_id}", status_code=status.HTTP_200_OK, response_model=SessionResponse)
def update_partial_session(
    session_id: int,
    session: SessionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return update_session_service(db, session_id, session, current_user)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return delete_session_service(db, session_id, current_user)
