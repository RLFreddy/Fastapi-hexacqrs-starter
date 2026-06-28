import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def authed_client(client: TestClient) -> TestClient:
    client.post("/v1/auth/register", json={"email": "authed@test.com", "password": "pass123"})
    resp = client.post("/v1/auth/login", json={"email": "authed@test.com", "password": "pass123"})
    token = resp.json()["token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


class TestCreateUser:
    def test_create_user_returns_202(self, client: TestClient):
        response = client.post("/v1/users/", json={"name": "Alice", "email": "alice@test.com", "password": "pass123"})
        assert response.status_code == 202
        assert response.json()["message"] == "User creation started"

    def test_create_user_invalid_email(self, client: TestClient):
        response = client.post("/v1/users/", json={"name": "Alice", "email": "bad", "password": "pass123"})
        assert response.status_code == 422

    def test_create_user_short_password(self, client: TestClient):
        response = client.post("/v1/users/", json={"name": "Alice", "email": "alice@test.com", "password": "ab"})
        assert response.status_code == 422


class TestGetUsers:
    def test_get_users_requires_auth(self, client: TestClient):
        response = client.get("/v1/users/")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_get_users_returns_paginated(self, authed_client: TestClient):
        response = authed_client.get("/v1/users/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert isinstance(data["items"], list)


class TestGetUser:
    def test_get_user_requires_auth(self, client: TestClient):
        response = client.get("/v1/users/some-id")
        assert response.status_code == 401

    def test_get_user_not_found(self, authed_client: TestClient):
        user_id = "00000000-0000-0000-0000-000000000000"
        response = authed_client.get(f"/v1/users/{user_id}")
        assert response.status_code == 404
        assert response.json()["detail"] == f"User with id '{user_id}' not found"
