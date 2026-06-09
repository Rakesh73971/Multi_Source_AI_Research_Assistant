import pytest

def test_login_success(client, test_user):
    res = client.post(
        "/login/", 
        data={"username": test_user["email"], "password": "password123"}
    )
    assert res.status_code == 200
    assert "access_token" in res.json()
    assert res.json()["token_type"] == "Bearer"

def test_login_incorrect_password(client, test_user):
    res = client.post(
        "/login/", 
        data={"username": test_user["email"], "password": "wrongpassword"}
    )
    assert res.status_code == 403
    assert res.json().get("detail") == "Invalid Credentials"

def test_login_invalid_user(client):
    res = client.post(
        "/login/", 
        data={"username": "not_exists@example.com", "password": "password123"}
    )
    assert res.status_code == 403
    assert res.json().get("detail") == "Invalid Credentials"
