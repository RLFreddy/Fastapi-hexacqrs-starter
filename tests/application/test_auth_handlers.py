from unittest.mock import MagicMock

import pytest

from src.contexts.auth.application.commands.register_user import RegisterUserCommand
from src.contexts.auth.application.commands.register_user_handler import RegisterUserHandler
from src.contexts.auth.application.queries.login_user import LoginUserQuery
from src.contexts.auth.application.queries.login_user_handler import LoginUserHandler
from src.contexts.auth.domain.entities import AuthUser


@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.find_by_email.return_value = None
    return repo


class TestRegisterUserHandler:
    def test_register_creates_user(self, mock_repo):
        handler = RegisterUserHandler(mock_repo)
        command = RegisterUserCommand(email="new@test.com", password="secret123")

        user_id = handler.handle(command)

        assert len(user_id) == 36
        mock_repo.save.assert_called_once()

    def test_register_duplicate_email_raises(self, mock_repo):
        mock_repo.find_by_email.return_value = AuthUser.create("dup@test.com", "pass123")
        handler = RegisterUserHandler(mock_repo)
        command = RegisterUserCommand(email="dup@test.com", password="pass123")

        with pytest.raises(ValueError, match="Email already registered"):
            handler.handle(command)

        mock_repo.save.assert_not_called()


class TestLoginUserHandler:
    def test_login_valid_credentials(self, mock_repo):
        user = AuthUser.create("valid@test.com", "correctpass")
        mock_repo.find_by_email.return_value = user
        handler = LoginUserHandler(mock_repo)
        query = LoginUserQuery(email="valid@test.com", password="correctpass")

        result = handler.handle(query)

        assert result["authenticated"] is True
        assert result["user_id"] == user.id
        assert result["token_type"] == "bearer"
        assert len(result["token"]) > 0

    def test_login_user_not_found(self, mock_repo):
        mock_repo.find_by_email.return_value = None
        handler = LoginUserHandler(mock_repo)
        query = LoginUserQuery(email="nobody@test.com", password="pass")

        with pytest.raises(ValueError, match="User not found"):
            handler.handle(query)

    def test_login_wrong_password(self, mock_repo):
        user = AuthUser.create("user@test.com", "correctpass")
        mock_repo.find_by_email.return_value = user
        handler = LoginUserHandler(mock_repo)
        query = LoginUserQuery(email="user@test.com", password="wrongpass")

        with pytest.raises(ValueError, match="Invalid password"):
            handler.handle(query)
