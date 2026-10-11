def test_register_user(client):
    response = client.post(
        "/users",
        json={"username": "testuser", "email": "test@test.com", "password": "securepassword123"},
    )
    
    assert response.status_code == 201
    
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@test.com"
    assert "id" in data
    assert "hashed_password" not in data


def test_login_and_get_token(client):
    client.post(
        "/users",
        json={"username": "loginuser", "email": "login@test.com", "password": "mypassword"}
    )
    
    response = client.post(
        "/token",
        data={"username": "loginuser", "password": "mypassword"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert data["token_type"] == "bearer"