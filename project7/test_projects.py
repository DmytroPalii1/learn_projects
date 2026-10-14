def test_create_project_authenticated(client):
    client.post(
        "/users",
        json={"username": "alice", "email": "alice@test.com", "password": "password123"}
    )
    
    login_res = client.post(
        "/token",
        data={"username": "alice", "password": "password123"}
    )
    token = login_res.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/projects",
        json={"title": "Alice SaaS", "description": "AI-powered tool"},
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Alice SaaS"
    assert data["owner_id"] is not None


def test_multi_tenancy_isolation(client):
    client.post("/users", json={"username": "alice", "email": "alice@test.com", "password": "pwd"})
    client.post("/users", json={"username": "bob", "email": "bob@test.com", "password": "pwd"})
    
    alice_token = client.post("/token", data={"username": "alice", "password": "pwd"}).json()["access_token"]
    client.post(
        "/projects",
        json={"title": "Alices Secret Project"},
        headers={"Authorization": f"Bearer {alice_token}"}
    )
    
    bob_token = client.post("/token", data={"username": "bob", "password": "pwd"}).json()["access_token"]
    bob_response = client.get(
        "/projects",
        headers={"Authorization": f"Bearer {bob_token}"}
    )
    
    assert bob_response.status_code == 200
    projects = bob_response.json()
    assert len(projects) == 0