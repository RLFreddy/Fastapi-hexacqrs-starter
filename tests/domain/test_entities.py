from src.contexts.auth.domain.entities import AuthUser
from src.contexts.users.domain.entities import User


class TestAuthUser:
    def test_create_returns_instance(self):
        user = AuthUser.create("test@test.com", "secret123")
        assert isinstance(user, AuthUser)
        assert user.email == "test@test.com"
        assert user.is_active is True
        assert len(user.id) == 36

    def test_create_hashes_password(self):
        user = AuthUser.create("test@test.com", "secret123")
        assert user.password_hash != "secret123"
        assert user.password_hash.startswith("$2b$")

    def test_verify_password_correct(self):
        user = AuthUser.create("test@test.com", "secret123")
        assert user.verify_password("secret123") is True

    def test_verify_password_incorrect(self):
        user = AuthUser.create("test@test.com", "secret123")
        assert user.verify_password("wrong") is False


class TestUser:
    def test_create_returns_instance(self):
        user = User.create("John", "john@test.com", "secret123")
        assert isinstance(user, User)
        assert user.name == "John"
        assert user.email == "john@test.com"
        assert len(user.id) == 36

    def test_create_hashes_password(self):
        user = User.create("John", "john@test.com", "secret123")
        assert user.password_hash.startswith("$2b$")
