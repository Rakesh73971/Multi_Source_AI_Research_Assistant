from unittest.mock import patch, MagicMock
import pytest
from langchain_core.documents import Document
from app.services.summary_service import generate_map_reduce_summary
from app.models.user import User
from app.models.research_session import ResearchSession


@patch("app.services.summary_service.ChatGoogleGenerativeAI")
@patch("app.services.summary_service.load_summarize_chain")
def test_generate_map_reduce_summary(mock_load_chain, mock_llm_class):
    mock_chain = MagicMock()
    mock_load_chain.return_value = mock_chain
    mock_chain.invoke.return_value = {
        "output_text": " This is the summary bullet 1. \n Bullet 2. "
    }

    docs = [Document(page_content="Some text", metadata={})]
    summary = generate_map_reduce_summary(docs)

    assert summary == "This is the summary bullet 1. \n Bullet 2."
    mock_load_chain.assert_called_once()


@patch("app.rag.vector_store.get_all_documents_in_store")
@patch("app.services.summary_service.generate_map_reduce_summary")
def test_update_session_summary_task(mock_generate, mock_get_all, session):
    from app.tasks.ingestion_tasks import update_session_summary_task

    # 1. Set up db user
    db_user = User(
        full_name="Summary Test User",
        email="summarytest@test.com",
        password="pwd",
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    # 2. Set up db research session
    db_session = ResearchSession(
        user_id=db_user.id,
        name="Summary Test Session",
        chroma_collection_db="sum_col_123",
        status="active",
    )
    session.add(db_session)
    session.commit()
    session.refresh(db_session)

    mock_get_all.return_value = [Document(page_content="hello", metadata={})]
    mock_generate.return_value = "Bullet 1\nBullet 2"

    session_id = db_session.id
    original_close = session.close
    session.close = MagicMock()

    try:
        # Patch the session provider so the task uses our test session
        with patch(
            "app.tasks.ingestion_tasks.SessionLocal", return_value=session
        ):
            result = update_session_summary_task(session_id)

        assert result["status"] == "updated"

        # Reload session and check summary
        refreshed_session = (
            session.query(ResearchSession)
            .filter(ResearchSession.id == session_id)
            .first()
        )
        assert refreshed_session.summary == "Bullet 1\nBullet 2"
    finally:
        session.close = original_close
