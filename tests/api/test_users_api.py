import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def authed_client(client: TestClient) -> TestClient:
    client.post("/auth/register", json={"email": "authed@test.com", "password": "pass123"})
    resp = client.post("/auth/login", json={"email": "authed@test.com", "password": "pass123"})
    token = resp.json()["token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


class TestCreateUser:
    def test_create_user_returns_202(self, client: TestClient):
        response = client.post("/users/", json={"name": "Alice", "email": "alice@test.com", "password": "pass123"})
        assert response.status_code == 202
        assert response.json()["message"] == "User creation started"

    def test_create_user_invalid_email(self, client: TestClient):
        response = client.post("/users/", json={"name": "Alice", "email": "bad", "password": "pass123"})
        assert response.status_code == 422

    def test_create_user_short_password(self, client: TestClient):
        response = client.post("/users/", json={"name": "Alice", "email": "alice@test.com", "password": "ab"})
        assert response.status_code == 422


class TestGetUsers:
    def test_get_users_requires_auth(self, client: TestClient):
        response = client.get("/users/")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_get_users_returns_list(self, authed_client: TestClient):
        response = authed_client.get("/users/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestGetUser:
    def test_get_user_requires_auth(self, client: TestClient):
        response = client.get("/users/some-id")
        assert response.status_code == 401

    def test_get_user_not_found(self, authed_client: TestClient):
        response = authed_client.get("/users/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"
