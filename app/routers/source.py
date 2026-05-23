from typing import List

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.core.oauth2 import get_current_user
from app.db.database import get_db
from app.ingestion.pdf_loader import save_pdf_file
from app.models.source import SourceType
from app.schemas.source import (
    SourceCreate,
    SourceResponse,
    SourceUpdate,
    TaskStatusResponse,
    UrlSourceCreate,
    YoutubeSourceCreate,
)
from app.tasks.celery_app import celery_app
from app.services.source_service import (
    create_pending_pdf_source_service,
    create_pending_text_source_service,
    create_source_service,
    delete_source_service,
    get_source_service,
    get_sources_service,
    set_source_task_id_service,
    update_source_service,
)
from app.tasks.ingestion_tasks import (
    process_pdf_source_task,
    process_url_source_task,
    process_youtube_source_task,
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


@router.post("/pdf", status_code=status.HTTP_201_CREATED, response_model=SourceResponse)
async def upload_pdf_source(
    session_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    file_path = await save_pdf_file(file)

    source = create_pending_pdf_source_service(
        db=db,
        session_id=session_id,
        file_name=file.filename or file_path.name,
        file_path=str(file_path),
        current_user=current_user,
    )

    task = process_pdf_source_task.delay(source.id)
    return set_source_task_id_service(db, source, task.id)


@router.post("/url", status_code=status.HTTP_201_CREATED, response_model=SourceResponse)
async def create_url_source(
    source_request: UrlSourceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    source = create_pending_text_source_service(
        db=db,
        session_id=source_request.session_id,
        source_type=SourceType.URL,
        title=source_request.title or source_request.source_url,
        source_url=source_request.source_url,
        current_user=current_user,
    )

    task = process_url_source_task.delay(source.id)
    return set_source_task_id_service(db, source, task.id)


@router.post("/youtube", status_code=status.HTTP_201_CREATED, response_model=SourceResponse)
def create_youtube_source(
    source_request: YoutubeSourceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    source = create_pending_text_source_service(
        db=db,
        session_id=source_request.session_id,
        source_type=SourceType.YOUTUBE,
        title=source_request.title or source_request.source_url,
        source_url=source_request.source_url,
        current_user=current_user,
    )

    task = process_youtube_source_task.delay(source.id)
    return set_source_task_id_service(db, source, task.id)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[SourceResponse])
def get_sources(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_sources_service(db, current_user)


@router.get("/tasks/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskStatusResponse)
def get_source_task_status(
    task_id: str,
    current_user=Depends(get_current_user),
):
    task_result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None,
    }


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
