from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.conversation_message import ConversationMessage
from app.models.research_session import ResearchSession


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


def create_conversion_msg_service(db: Session, message, current_user):
    _get_owned_session(db, message.session_id, current_user)

    conversion_msg = ConversationMessage(
        session_id=message.session_id,
        user_id=current_user.id,
        role=message.role,
        content=message.content,
        sources_used=message.sources_used,
        query_type=message.query_type,
        tokens_used=message.tokens_used,
    )
    db.add(conversion_msg)
    db.commit()
    db.refresh(conversion_msg)
    return conversion_msg


def get_conversion_msgs_service(db: Session, current_user):
    return db.query(ConversationMessage).filter(
        ConversationMessage.user_id == current_user.id
    ).all()


def get_conversion_msg_service(db: Session, msg_id: int, current_user):
    message = db.query(ConversationMessage).filter(
        ConversationMessage.id == msg_id,
        ConversationMessage.user_id == current_user.id,
    ).first()
    if message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation message with id {msg_id} not found",
        )
    return message


def update_conversion_msg_service(db: Session, msg_id: int, message_update, current_user):
    message = get_conversion_msg_service(db, msg_id, current_user)
    update_data = message_update.model_dump(exclude_unset=True)

    if "session_id" in update_data:
        _get_owned_session(db, update_data["session_id"], current_user)

    for key, value in update_data.items():
        setattr(message, key, value)

    db.commit()
    db.refresh(message)
    return message


def delete_conversion_msg_service(db: Session, msg_id: int, current_user):
    message = get_conversion_msg_service(db, msg_id, current_user)
    db.delete(message)
    db.commit()
    return None
