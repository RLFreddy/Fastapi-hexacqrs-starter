import logging
from typing import TYPE_CHECKING

from src.contexts.users.application.commands.create_user import CreateUserCommand
from src.shared.infrastructure.event_bus import RabbitMQEventBus

if TYPE_CHECKING:
    from src.shared.application.dependency_injection import Container

logger = logging.getLogger(__name__)


async def start_consumers(container: "Container", event_bus: RabbitMQEventBus) -> None:
    async def handle_user_created(data):
        logger.info("Event received: %s", data)
        try:
            handler = container.create_user_handler()

            command = CreateUserCommand(name=data["name"], email=data["email"], password=data["password"])

            user_id = handler.handle(command)
            logger.info("User created: %s", user_id)
        except Exception as e:
            logger.error("Failed to process user.created event: %s", e)

    await event_bus.consume(
        queue="user_created", callback=handle_user_created, exchange="users", routing_key="user.created"
    )
