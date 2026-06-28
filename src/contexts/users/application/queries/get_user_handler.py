from typing import Optional

from src.contexts.users.domain.repositories import UserRepository
from src.shared.application.query import QueryHandler

from .get_user import GetUserQuery


class GetUserHandler(QueryHandler):
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def handle(self, query: GetUserQuery) -> Optional[dict]:
        user = self.user_repository.find_by_id(query.user_id)
        if user is None:
            return None
        return {"id": user.id, "name": user.name, "email": user.email}
