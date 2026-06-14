import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from app.ingestion.youtube_loader import extract_youtube_video_id, extract_youtube_transcript


def test_extract_youtube_video_id():
    # Standard YouTube links
    assert extract_youtube_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_youtube_video_id("https://youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_youtube_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s") == "dQw4w9WgXcQ"

    # Share links
    assert extract_youtube_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_youtube_video_id("https://www.youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    # Shorts links
    assert extract_youtube_video_id("https://www.youtube.com/shorts/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_youtube_video_id("https://www.youtube.com/shorts/dQw4w9WgXcQ?t=10s") == "dQw4w9WgXcQ"

    # Invalid links
    with pytest.raises(HTTPException) as exc_info:
        extract_youtube_video_id("https://example.com/watch?v=dQw4w9WgXcQ")
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid YouTube URL"

    with pytest.raises(HTTPException) as exc_info:
        extract_youtube_video_id("https://www.youtube.com/watch?not_v=dQw4w9WgXcQ")
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid YouTube URL"


@patch("youtube_transcript_api.YouTubeTranscriptApi")
def test_extract_youtube_transcript_success(mock_class):
    mock_instance = mock_class.return_value

    mock_snippet_1 = MagicMock()
    mock_snippet_1.text = "Hello world"
    mock_snippet_2 = MagicMock()
    mock_snippet_2.text = "This is a test transcript."

    mock_instance.fetch.return_value = [mock_snippet_1, mock_snippet_2]

    title, text = extract_youtube_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert title == "YouTube video dQw4w9WgXcQ"
    assert text == "Hello world\nThis is a test transcript."
    mock_instance.fetch.assert_called_once_with("dQw4w9WgXcQ")


@patch("youtube_transcript_api.YouTubeTranscriptApi")
def test_extract_youtube_transcript_api_error(mock_class):
    mock_instance = mock_class.return_value
    mock_instance.fetch.side_effect = Exception("YouTube error")

    with pytest.raises(HTTPException) as exc_info:
        extract_youtube_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    assert exc_info.value.status_code == 400
    assert "Could not load YouTube transcript" in exc_info.value.detail


@patch("youtube_transcript_api.YouTubeTranscriptApi")
def test_extract_youtube_transcript_empty(mock_class):
    mock_instance = mock_class.return_value
    mock_instance.fetch.return_value = []

    with pytest.raises(HTTPException) as exc_info:
        extract_youtube_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "No transcript text found for this YouTube video"


def test_extract_youtube_transcript_import_error():
    original_import = __import__

    def mock_import(name, *args, **kwargs):
        if name == "youtube_transcript_api":
            raise ImportError("mocked import error")
        return original_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=mock_import):
        with pytest.raises(HTTPException) as exc_info:
            extract_youtube_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

        assert exc_info.value.status_code == 500
        assert "youtube-transcript-api is not installed" in exc_info.value.detail


@patch("app.tasks.ingestion_tasks.SessionLocal")
@patch("app.tasks.ingestion_tasks.extract_youtube_transcript")
@patch("app.tasks.ingestion_tasks.split_text_into_chunks")
@patch("app.tasks.ingestion_tasks.index_source_chunks")
def test_process_youtube_source_task_success(
    mock_index, mock_split, mock_extract, mock_session_local
):
    from app.models.source import SourceStatus
    from app.tasks.ingestion_tasks import process_youtube_source_task

    mock_db = MagicMock()
    mock_session_local.return_value = mock_db

    mock_source = MagicMock()
    mock_source.id = 42
    mock_source.source_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    mock_source.title = None
    mock_source.session.chroma_collection_db = "collection_name"

    mock_db.query.return_value.filter.return_value.first.return_value = mock_source

    mock_extract.return_value = ("YouTube video dQw4w9WgXcQ", "Extracted YouTube text content")
    mock_split.return_value = ["chunk 1", "chunk 2"]
    mock_index.return_value = 2

    result = process_youtube_source_task(42)

    assert result == {"source_id": 42, "status": "ready", "chunk_count": 2}
    assert mock_source.title == "YouTube video dQw4w9WgXcQ"
    assert mock_source.extracted_text == "Extracted YouTube text content"
    assert mock_source.chunk_count == 2
    assert mock_source.status == SourceStatus.READY
    mock_db.commit.assert_called()


@patch("app.tasks.ingestion_tasks.SessionLocal")
@patch("app.tasks.ingestion_tasks.extract_youtube_transcript")
def test_process_youtube_source_task_failure(
    mock_extract, mock_session_local
):
    from app.models.source import SourceStatus
    from app.tasks.ingestion_tasks import process_youtube_source_task

    mock_db = MagicMock()
    mock_session_local.return_value = mock_db

    mock_source = MagicMock()
    mock_source.id = 42
    mock_source.source_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    mock_source.title = None

    mock_db.query.return_value.filter.return_value.first.return_value = mock_source

    mock_extract.side_effect = Exception("Failed to load transcript")

    result = process_youtube_source_task(42)

    assert result == {"source_id": 42, "status": "failed", "error": "Failed to load transcript"}
    assert mock_source.status == SourceStatus.FAILED
    assert mock_source.error_message == "Failed to load transcript"
    mock_db.commit.assert_called()


@patch("app.tasks.ingestion_tasks.SessionLocal")
def test_process_youtube_source_task_not_found(mock_session_local):
    from app.tasks.ingestion_tasks import process_youtube_source_task

    mock_db = MagicMock()
    mock_session_local.return_value = mock_db

    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = process_youtube_source_task(999)
    assert result == {"source_id": 999, "status": "not_found"}

