def test_create_research_session(authorized_access,test_user):
    payload = {
        "user_id":test_user['id'],
        "name":"RAG Test Session",
        "chroma_collection_db":"rag_test_session_001",
        "status":"active"
    }
    response = authorized_access.post("/research_sessions/",json=payload)
    assert response.status_code == 201
    assert response.json()["name"] == "RAG Test Session"


def test_get_rearch_sessions(authorized_access):
    responses = authorized_access.get("/research_sessions/")
    assert responses.status_code == 200


def test_get_research_session(authorized_access,test_research_session):
    response = authorized_access.get(f"/research_sessions/{test_research_session['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "RAG Test Session"

def test_update_research_session(authorized_access,test_research_session):
    payload = {
        "name":"RAG Test"
    }
    research_id = test_research_session["id"]
    response = authorized_access.patch(f"/research_sessions/{research_id}",json=payload)
    assert response.status_code == 200
    assert response.json()["name"] == "RAG Test"

def test_complete_update_session(authorized_access,test_research_session,test_user):
    payload = {
        "user_id":test_user['id'],
        "name":"RAG Test Session ",
        "chroma_collection_db":"rag_test_session_001",
        "status":"active"
    }
    research_id = test_research_session["id"]
    response = authorized_access.put(f"/research_sessions/{research_id}",json=payload)
    assert response.status_code == 200
    assert response.json()["user_id"] == 1
    

def test_delete_research_session(authorized_access,test_research_session):
    research_id = test_research_session["id"]
    response = authorized_access.delete(f"/research_sessions/{research_id}")
    assert response.status_code == 204
    