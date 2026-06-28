from src.contexts.users.domain.repositories import UserRepository
from src.shared.application.query import QueryHandler

from .get_users import GetUsersQuery


class GetUsersHandler(QueryHandler):
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def handle(self, query: GetUsersQuery) -> list[dict]:
        users = self.user_repository.get_all()
        return [{"id": user.id, "name": user.name, "email": user.email} for user in users]
