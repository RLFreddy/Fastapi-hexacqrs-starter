from fastapi.testclient import TestClient


class TestRegister:
    def test_register_success(self, client: TestClient):
        response = client.post("/auth/register", json={"email": "new@test.com", "password": "secret123"})
        assert response.status_code == 201
        data = response.json()
        assert "user_id" in data
        assert len(data["user_id"]) == 36

    def test_register_duplicate_email(self, client: TestClient):
        client.post("/auth/register", json={"email": "dup@test.com", "password": "secret123"})
        response = client.post("/auth/register", json={"email": "dup@test.com", "password": "secret123"})
        assert response.status_code == 400
        assert response.json()["detail"] == "Email already registered"

    def test_register_invalid_email(self, client: TestClient):
        response = client.post("/auth/register", json={"email": "not-an-email", "password": "secret123"})
        assert response.status_code == 422

    def test_register_short_password(self, client: TestClient):
        response = client.post("/auth/register", json={"email": "user@test.com", "password": "ab"})
        assert response.status_code == 422


class TestLogin:
    def test_login_success(self, client: TestClient):
        client.post("/auth/register", json={"email": "login@test.com", "password": "secret123"})
        response = client.post("/auth/login", json={"email": "login@test.com", "password": "secret123"})
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
        assert "token" in data
        assert data["token_type"] == "bearer"

    def test_login_user_not_found(self, client: TestClient):
        response = client.post("/auth/login", json={"email": "nobody@test.com", "password": "pass"})
        assert response.status_code == 400
        assert response.json()["detail"] == "User not found"

    def test_login_wrong_password(self, client: TestClient):
        client.post("/auth/register", json={"email": "wrongpw@test.com", "password": "secret123"})
        response = client.post("/auth/login", json={"email": "wrongpw@test.com", "password": "wrongpass"})
        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid password"


class TestGetAuthUsers:
    def test_list_users(self, client: TestClient):
        client.post("/auth/register", json={"email": "u1@test.com", "password": "pass123"})
        client.post("/auth/register", json={"email": "u2@test.com", "password": "pass123"})
        response = client.get("/auth/users")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["email"] == "u1@test.com"
