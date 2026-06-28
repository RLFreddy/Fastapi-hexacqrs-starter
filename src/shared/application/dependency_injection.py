# src/shared/application/dependency_injection.py

from dependency_injector import containers, providers

from src.contexts.auth.application.commands.register_user_handler import RegisterUserHandler
from src.contexts.auth.application.queries.auth_users_handler import GetAuthUsersHandler
from src.contexts.auth.application.queries.login_user_handler import LoginUserHandler
from src.contexts.auth.infrastructure.repositories.sqlalchemy_auth_repository import SQLAlchemyAuthRepository
from src.contexts.users.application.commands.create_user_handler import CreateUserHandler
from src.contexts.users.application.queries.get_user_handler import GetUserHandler
from src.contexts.users.application.queries.get_users_handler import GetUsersHandler
from src.contexts.users.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src.shared.application.ports import EventBus
from src.shared.infrastructure.database import SessionLocal


class _EventBusUnavailable(EventBus):
    async def publish(self, exchange: str, routing_key: str, message: dict):
        raise RuntimeError("Event bus unavailable: RabbitMQ is not connected")

    async def consume(self, queue: str, callback, exchange: str = None, routing_key: str = None):
        raise RuntimeError("Event bus unavailable: RabbitMQ is not connected")


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    db_session = providers.Factory(SessionLocal)

    # event_bus = providers.Singleton(
    #     RabbitMQEventBus,
    #     connection_url=config.rabbitmq_url
    # )
    # Will be overridden dynamically at startup with a real async instance
    event_bus = providers.Object(_EventBusUnavailable())

    # Repositories
    user_repository = providers.Factory(SQLAlchemyUserRepository, session=db_session)
    auth_repository = providers.Factory(SQLAlchemyAuthRepository, session=db_session)

    # Command Handlers
    # users
    create_user_handler = providers.Factory(CreateUserHandler, user_repository=user_repository)
    # auth
    auth_register_handler = providers.Factory(RegisterUserHandler, auth_repository=auth_repository)

    # Query Handlers
    # users
    get_user_handler = providers.Factory(GetUserHandler, user_repository=user_repository)
    get_users_handler = providers.Factory(GetUsersHandler, user_repository=user_repository)
    # auth
    auth_login_handler = providers.Factory(LoginUserHandler, auth_repository=auth_repository)
    auth_users_handler = providers.Factory(GetAuthUsersHandler, auth_repository=auth_repository)
