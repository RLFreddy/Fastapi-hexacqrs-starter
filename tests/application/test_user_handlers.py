from unittest.mock import MagicMock

import pytest

from src.contexts.users.application.queries.get_user import GetUserQuery
from src.contexts.users.application.queries.get_user_handler import GetUserHandler
from src.contexts.users.application.queries.get_users import GetUsersQuery
from src.contexts.users.application.queries.get_users_handler import GetUsersHandler
from src.contexts.users.domain.entities import User


@pytest.fixture
def mock_repo():
    return MagicMock()


class TestGetUserHandler:
    def test_get_user_found(self, mock_repo):
        user = User.create("Alice", "alice@test.com", "pass")
        mock_repo.find_by_id.return_value = user
        handler = GetUserHandler(mock_repo)
        query = GetUserQuery(user_id=user.id)

        result = handler.handle(query)

        assert result["id"] == user.id
        assert result["name"] == "Alice"
        assert result["email"] == "alice@test.com"

    def test_get_user_not_found(self, mock_repo):
        mock_repo.find_by_id.return_value = None
        handler = GetUserHandler(mock_repo)
        query = GetUserQuery(user_id="nonexistent")

        result = handler.handle(query)

        assert result is None


class TestGetUsersHandler:
    def test_get_users_returns_paginated(self, mock_repo):
        users = [
            User.create("Alice", "alice@test.com", "pass"),
            User.create("Bob", "bob@test.com", "pass"),
        ]
        mock_repo.get_all_paginated.return_value = (users, 2)
        handler = GetUsersHandler(mock_repo)
        query = GetUsersQuery(page=1, size=10)

        result = handler.handle(query)

        assert result["total"] == 2
        assert result["page"] == 1
        assert result["size"] == 10
        assert len(result["items"]) == 2
        assert result["items"][0]["name"] == "Alice"
        assert result["items"][1]["name"] == "Bob"

    def test_get_users_empty(self, mock_repo):
        mock_repo.get_all_paginated.return_value = ([], 0)
        handler = GetUsersHandler(mock_repo)
        query = GetUsersQuery(page=1, size=10)

        result = handler.handle(query)

        assert result["total"] == 0
        assert result["items"] == []
