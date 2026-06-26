from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.oauth2 import get_current_user
from app.db.database import get_db
from app.schemas.conversation_message import (
    ConversionMessageCreate,
    ConversionMessageResponse,
    ConversionMessageUpdate,
)
from app.services.conversation_message_service import (
    create_conversion_msg_service,
    delete_conversion_msg_service,
    get_conversion_msg_service,
    get_conversion_msgs_service,
    update_conversion_msg_service,
)


router = APIRouter(
    prefix="/conversation_messages",
    tags=["Conversation Messages"],
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ConversionMessageResponse)
def create_conversion_message(
    message: ConversionMessageCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_conversion_msg_service(db, message, current_user)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[ConversionMessageResponse])
def get_conversion_messages(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_conversion_msgs_service(db, current_user)


@router.get("/{msg_id}", status_code=status.HTTP_200_OK, response_model=ConversionMessageResponse)
def get_conversion_message(
    msg_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_conversion_msg_service(db, msg_id, current_user)


@router.put("/{msg_id}", status_code=status.HTTP_200_OK, response_model=ConversionMessageResponse)
@router.patch("/{msg_id}", status_code=status.HTTP_200_OK, response_model=ConversionMessageResponse)
def update_conversion_message(
    msg_id: int,
    conversion_msg: ConversionMessageUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return update_conversion_msg_service(db, msg_id, conversion_msg, current_user)


@router.delete("/{msg_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversion_message(
    msg_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return delete_conversion_msg_service(db, msg_id, current_user)
