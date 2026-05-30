def test_create_user(client):
    user_data = {
        "full_name":"N.Rakesh",
        "email":"rakesh@gmail.com",
        "password":"password123",
        "role":"admin"
    }
    response = client.post("/users/",json=user_data)
    assert response.status_code == 201

def test_get_users(authorized_access):
    responses = authorized_access.get("/users/")
    assert responses.status_code == 200


def test_get_user(authorized_access,test_user):
    user_id = test_user["id"]
    response = authorized_access.get(f"/users/{user_id}")
    assert response.status_code == 200

def test_update_user(authorized_access,test_user):
    user_data = {
        "full_name":"Gukesh"
    }
    response = authorized_access.patch(f"/users/{test_user['id']}",json=user_data)

    assert response.status_code == 200
    assert response.json()["full_name"] == "Gukesh"

def test_delete_user(authorized_access,test_user):
    user_id = test_user["id"]
    response = authorized_access.delete(f"/users/{user_id}")
    assert response.status_code == 204
