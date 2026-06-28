import asyncio
import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.contexts.auth.interfaces.http import auth_controller
from src.contexts.users.infrastructure.event_handlers.user_created_handler import start_consumers
from src.contexts.users.interfaces.http import user_controller
from src.shared.application.dependency_injection import Container, providers
from src.shared.application.exceptions import AppException
from src.shared.infrastructure.event_bus import RabbitMQEventBus

logging.basicConfig(
    level=getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper()),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

consumer_task: asyncio.Task | None = None
event_bus_instance: RabbitMQEventBus | None = None


@asynccontextmanager
async def lifespan(application: FastAPI):
    global consumer_task, event_bus_instance
    try:
        event_bus_instance = RabbitMQEventBus(container.config.rabbitmq_url())
        await event_bus_instance.connect()
        container.event_bus.override(providers.Object(event_bus_instance))
        consumer_task = asyncio.create_task(start_consumers(container, event_bus_instance))

        def _on_consumer_done(task: asyncio.Task):
            if not task.cancelled():
                exc = task.exception()
                if exc:
                    logger.error("Consumer task failed: %s", exc)

        consumer_task.add_done_callback(_on_consumer_done)
        logger.info("RabbitMQ connected and consumer started")
    except Exception as e:
        logger.warning("RabbitMQ not available, running without event bus: %s", e)

    yield

    if consumer_task:
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            logger.info("Consumer task cancelled")
    if event_bus_instance and event_bus_instance.connection and not event_bus_instance.connection.is_closed:
        await event_bus_instance.connection.close()
        logger.info("RabbitMQ connection closed")


openapi_tags = [
    {
        "name": "auth",
        "description": "**Authentication flow.** Start here: register an account, then login to obtain a JWT token.",
    },
    {
        "name": "users",
        "description": "**User management.** Create users (no token required). List and search require a JWT — click the **Authorize** button after logging in.",  # noqa: E501
    },
    {
        "name": "health",
        "description": "**Health check.** Verify the API is running.",
    },
]

app = FastAPI(
    title="Hexacqrs API",
    lifespan=lifespan,
    openapi_tags=openapi_tags,
    description="""# Hexacqrs API

A FastAPI implementation of a hexagonal architecture with CQRS pattern.

## Features
- **Authentication**: Register and login with JWT bearer tokens
- **User Management**: CRUD with async creation via RabbitMQ event bus
- **CQRS**: Separate command/query handlers per bounded context
- **Hexagonal Architecture**: Clean separation of domain, application, and infrastructure layers

## How to use this API
1. **Register** → `POST /v1/auth/register`
2. **Login** → `POST /v1/auth/login` (copy the token)
3. **Authorize** → click the **Authorize** button and paste the token
4. **Explore** → test the protected endpoints under `/v1/users/`
""",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "API Support",
        "url": "https://github.com/RLFreddy/Fastapi-hexacqrs-starter",
    },
)

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

container = Container()
container.wire(
    modules=[
        "src.contexts.users.interfaces.http.user_controller",
        "src.contexts.auth.interfaces.http.auth_controller",
    ]
)

container.config.rabbitmq_url.from_env("RABBITMQ_URL", required=True)

app.include_router(user_controller.router)
app.include_router(auth_controller.router)


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    logger.info("Starting FastAPI server with Uvicorn...")
    host = os.environ.get("APP_HOST", "0.0.0.0")
    port = int(os.environ.get("APP_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
    logger.info("FastAPI server stopped.")
