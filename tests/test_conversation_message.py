import pytest

@pytest.fixture
def test_conversation_message(authorized_access, test_research_session):
    payload = {
        "session_id": test_research_session["id"],
        "role": "user",
        "content": "What is the capital of France?",
        "query_type": "question"
    }
    response = authorized_access.post("/conversation_messages/", json=payload)
    assert response.status_code == 201
    return response.json()

def test_create_conversation_message(authorized_access, test_research_session):
    payload = {
        "session_id": test_research_session["id"],
        "role": "assistant",
        "content": "The capital of France is Paris.",
        "query_type": "question"
    }
    response = authorized_access.post("/conversation_messages/", json=payload)
    assert response.status_code == 201, response.json()
    data = response.json()
    assert data["content"] == "The capital of France is Paris."
    assert data["role"] == "assistant"

def test_get_conversation_messages(authorized_access, test_conversation_message):
    response = authorized_access.get("/conversation_messages/")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_conversation_message(authorized_access, test_conversation_message):
    msg_id = test_conversation_message["id"]
    response = authorized_access.get(f"/conversation_messages/{msg_id}")
    assert response.status_code == 200
    assert response.json()["id"] == msg_id

def test_update_conversation_message(authorized_access, test_conversation_message):
    msg_id = test_conversation_message["id"]
    payload = {"content": "Updated content"}
    response = authorized_access.patch(f"/conversation_messages/{msg_id}", json=payload)
    assert response.status_code == 200
    assert response.json()["content"] == "Updated content"

def test_delete_conversation_message(authorized_access, test_conversation_message):
    msg_id = test_conversation_message["id"]
    response = authorized_access.delete(f"/conversation_messages/{msg_id}")
    assert response.status_code == 204
    
    res_get = authorized_access.get(f"/conversation_messages/{msg_id}")
    assert res_get.status_code == 404
