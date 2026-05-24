from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.agents.research_graph import run_research_agent
from app.models.conversation_message import ConversationMessage, MessageRole, QueryType
from app.models.research_session import ResearchSession
from app.models.source import Source, SourceStatus


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


def ask_session_question_service(
    db: Session,
    session_id: int,
    question: str,
    top_k: int,
    current_user,
    source_id: int | None = None,
):
    session = get_session_service(db, session_id, current_user)

    if source_id is not None:
        source = db.query(Source).filter(
            Source.id == source_id,
            Source.session_id == session.id,
            Source.user_id == current_user.id,
        ).first()
        if source is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source with id {source_id} not found in this session",
            )
        if source.status != SourceStatus.READY:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Source with id {source_id} is not ready yet",
            )

    user_message = ConversationMessage(
        session_id=session.id,
        user_id=current_user.id,
        role=MessageRole.USER,
        content=question,
        query_type=QueryType.QUESTION,
    )
    db.add(user_message)
    db.commit()

    agent_result = run_research_agent(
        collection_name=session.chroma_collection_db,
        question=question,
        top_k=top_k,
        source_id=source_id,
    )
    chunks = agent_result["chunks"]
    answer = agent_result["answer"]

    sources = [
        {
            "source_id": chunk["metadata"].get("source_id"),
            "source_title": chunk["metadata"].get("source_title"),
            "chunk_index": chunk["metadata"].get("chunk_index"),
            "score": chunk["score"],
        }
        for chunk in chunks
    ]

    assistant_message = ConversationMessage(
        session_id=session.id,
        user_id=current_user.id,
        role=MessageRole.ASSISTANT,
        content=answer,
        sources_used=sources,
        query_type=QueryType.QUESTION,
    )
    db.add(assistant_message)
    db.commit()

    return {
        "session_id": session.id,
        "question": question,
        "answer": answer,
        "sources": sources,
    }
