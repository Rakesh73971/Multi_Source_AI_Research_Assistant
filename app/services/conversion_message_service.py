from fastapi import Depends,HTTPException,status
from app.models.conversation_message import ConversationMessage
from app.core.oauth2 import get_current_user
from sqlalchemy.orm import Session

def create_conversion_msg_service(db:Session,message,current_user=Depends(get_current_user)):
    conversion_msg = ConversationMessage(
        session_id = message.id,
        user_id = current_user.id,
        role = message.role,
        content = message.content,
        sources_used = message.sources_used,
        query_type = message.query_type,
        tokens_used = message.tokens_used
    )
    db.add(conversion_msg)
    db.commit()
    db.refresh(conversion_msg)
    return conversion_msg


def get_conversion_msgs_service(db:Session):
    messages = db.query(ConversationMessage).all()
    return messages


def get_conversion_msg_service(db:Session,msg_id):
    message = db.query(ConversationMessage).filter(ConversationMessage.id == msg_id).first()
    if message is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"message with id {msg_id} is not found")
    return message

def update_conversion_msg_service(db:Session,msg_id,conversion_msg_update):
    message = db.query(ConversationMessage).filter(ConversationMessage.id == msg_id).first()
    if message is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"conversion message with id {msg_id} not found")
    updated_msg = conversion_msg_update.model_dump(exclude_unset=True)
    for key,value in updated_msg.items():
        setattr(message,key,value)
    db.commit()
    db.refresh(message)
    return message

def delete_conversion_msg_service(db:Session,msg_id):
    msg = db.query(ConversationMessage).filter(ConversationMessage.id == msg_id).first()
    if msg is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"message with id {msg_id} not found")
    db.delete(msg)
    db.commit()
    return None
