import pytest
from unittest.mock import patch

@pytest.fixture
def mock_celery_task():
    with patch("app.routers.source.process_url_source_task.delay") as mock_url_task, \
         patch("app.routers.source.process_youtube_source_task.delay") as mock_youtube_task, \
         patch("app.routers.source.process_pdf_source_task.delay") as mock_pdf_task:
        
        class MockTask:
            id = "mock_task_id_123"
            
        mock_url_task.return_value = MockTask()
        mock_youtube_task.return_value = MockTask()
        mock_pdf_task.return_value = MockTask()
        yield

@pytest.fixture
def test_source(authorized_access, test_research_session, mock_celery_task):
    payload = {
        "session_id": test_research_session["id"],
        "source_url": "https://example.com/article",
        "title": "Example Article"
    }
    response = authorized_access.post("/sources/url", json=payload)
    assert response.status_code == 201
    return response.json()

def test_create_url_source(authorized_access, test_research_session, mock_celery_task):
    payload = {
        "session_id": test_research_session["id"],
        "source_url": "https://example.com/another",
        "title": "Another Article"
    }
    response = authorized_access.post("/sources/url", json=payload)
    assert response.status_code == 201, response.json()
    assert response.json()["source_url"] == "https://example.com/another"
    assert response.json()["task_id"] == "mock_task_id_123"

def test_create_youtube_source(authorized_access, test_research_session, mock_celery_task):
    payload = {
        "session_id": test_research_session["id"],
        "source_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "title": "Rick Astley"
    }
    response = authorized_access.post("/sources/youtube", json=payload)
    assert response.status_code == 201, response.json()
    assert response.json()["source_url"] == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert response.json()["task_id"] == "mock_task_id_123"

def test_get_sources(authorized_access, test_source):
    response = authorized_access.get("/sources/")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_source(authorized_access, test_source):
    source_id = test_source["id"]
    response = authorized_access.get(f"/sources/{source_id}")
    assert response.status_code == 200
    assert response.json()["id"] == source_id

def test_update_source(authorized_access, test_source):
    source_id = test_source["id"]
    payload = {"title": "Updated Title"}
    response = authorized_access.patch(f"/sources/{source_id}", json=payload)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"

def test_delete_source(authorized_access, test_source):
    source_id = test_source["id"]
    response = authorized_access.delete(f"/sources/{source_id}")
    assert response.status_code == 204
    
    res_get = authorized_access.get(f"/sources/{source_id}")
    assert res_get.status_code == 404
