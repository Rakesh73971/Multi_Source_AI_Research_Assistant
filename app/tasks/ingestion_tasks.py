import asyncio

from app.db.database import SessionLocal
from app.ingestion.pdf_loader import extract_pdf_text
from app.ingestion.text_splitter import split_text_into_chunks
from app.ingestion.web_loader import extract_web_page
from app.ingestion.youtube_loader import extract_youtube_transcript
from app.models.source import Source, SourceStatus
from app.rag.vector_store import index_source_chunks
from app.tasks.celery_app import celery_app


def _mark_failed(db, source, error_message: str):
    source.status = SourceStatus.FAILED
    source.error_message = error_message
    db.commit()


def _index_and_mark_ready(db, source, extracted_text: str):
    chunks = split_text_into_chunks(extracted_text)
    indexed_count = index_source_chunks(
        collection_name=source.session.chroma_collection_db,
        source_id=source.id,
        source_title=source.title or source.file_name or source.source_url or "Source",
        chunks=chunks,
    )

    source.extracted_text = extracted_text
    source.chunk_count = indexed_count
    source.status = SourceStatus.READY
    source.error_message = None
    db.commit()
    return indexed_count


@celery_app.task(name="process_pdf_source")
def process_pdf_source_task(source_id: int):
    db = SessionLocal()
    try:
        source = db.query(Source).filter(Source.id == source_id).first()
        if source is None:
            return {"source_id": source_id, "status": "not_found"}

        try:
            extracted_text = extract_pdf_text(source.file_path)
            indexed_count = _index_and_mark_ready(db, source, extracted_text)
            return {"source_id": source.id, "status": "ready", "chunk_count": indexed_count}
        except Exception as exc:
            _mark_failed(db, source, str(exc))
            return {"source_id": source.id, "status": "failed", "error": str(exc)}
    finally:
        db.close()


@celery_app.task(name="process_url_source")
def process_url_source_task(source_id: int):
    db = SessionLocal()
    try:
        source = db.query(Source).filter(Source.id == source_id).first()
        if source is None:
            return {"source_id": source_id, "status": "not_found"}

        try:
            title, extracted_text = asyncio.run(extract_web_page(source.source_url))
            source.title = source.title or title
            indexed_count = _index_and_mark_ready(db, source, extracted_text)
            return {"source_id": source.id, "status": "ready", "chunk_count": indexed_count}
        except Exception as exc:
            _mark_failed(db, source, str(exc))
            return {"source_id": source.id, "status": "failed", "error": str(exc)}
    finally:
        db.close()


@celery_app.task(name="process_youtube_source")
def process_youtube_source_task(source_id: int):
    db = SessionLocal()
    try:
        source = db.query(Source).filter(Source.id == source_id).first()
        if source is None:
            return {"source_id": source_id, "status": "not_found"}

        try:
            title, extracted_text = extract_youtube_transcript(source.source_url)
            source.title = source.title or title
            indexed_count = _index_and_mark_ready(db, source, extracted_text)
            return {"source_id": source.id, "status": "ready", "chunk_count": indexed_count}
        except Exception as exc:
            _mark_failed(db, source, str(exc))
            return {"source_id": source.id, "status": "failed", "error": str(exc)}
    finally:
        db.close()
