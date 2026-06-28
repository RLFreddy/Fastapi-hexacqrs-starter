from src.contexts.auth.domain.repositories import AuthRepository
from src.shared.application.auth import create_access_token
from src.shared.application.query import QueryHandler

from .login_user import LoginUserQuery


class LoginUserHandler(QueryHandler):
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    def handle(self, query: LoginUserQuery) -> dict:
        user = self.auth_repository.find_by_email(query.email)
        if not user:
            raise ValueError("User not found")

        if not user.verify_password(query.password):
            raise ValueError("Invalid password")

        token = create_access_token(user.id)
        return {"authenticated": True, "user_id": user.id, "token": token, "token_type": "bearer"}
