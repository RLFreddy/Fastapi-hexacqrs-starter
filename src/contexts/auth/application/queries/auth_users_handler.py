from src.contexts.auth.domain.repositories import AuthRepository
from src.shared.application.query import QueryHandler

from .auth_users import GetAuthUsersQuery


class GetAuthUsersHandler(QueryHandler):
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    def handle(self, query: GetAuthUsersQuery) -> list[dict]:
        users = self.auth_repository.get_all()
        return [{"id": user.id, "email": user.email, "is_active": user.is_active} for user in users]
