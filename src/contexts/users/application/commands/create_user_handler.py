from src.contexts.users.domain.entities import User
from src.contexts.users.domain.repositories import UserRepository
from src.shared.application.command import CommandHandler

from .create_user import CreateUserCommand


class CreateUserHandler(CommandHandler):
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def handle(self, command: CreateUserCommand) -> str:
        user = User.create(command.name, command.email, command.password)
        self.user_repository.save(user)
        return user.id
