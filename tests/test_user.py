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