from src.contexts.auth.domain.entities import AuthUser
from src.contexts.auth.domain.repositories import AuthRepository
from src.shared.application.command import CommandHandler

from .register_user import RegisterUserCommand


class RegisterUserHandler(CommandHandler):
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    def handle(self, command: RegisterUserCommand) -> str:
        existing = self.auth_repository.find_by_email(command.email)
        if existing:
            raise ValueError("Email already registered")
        user = AuthUser.create(command.email, command.password)
        self.auth_repository.save(user)
        return user.id
