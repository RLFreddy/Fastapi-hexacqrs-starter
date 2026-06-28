import os
import uuid

os.environ["DATABASE_URL"] = f"sqlite:////tmp/test_{uuid.uuid4().hex}.db"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["RABBITMQ_URL"] = "amqp://guest:guest@localhost:5672/"

import pytest
from dependency_injector import providers
from fastapi.testclient import TestClient

from src.main import app, container
from src.shared.infrastructure.database import Base, engine


@pytest.fixture(scope="session", autouse=True)
def _setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()
    db_path = engine.url.database
    if db_path and os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture(autouse=True)
def _clean_db():
    from sqlalchemy import text

    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(text(f"DELETE FROM {table.name}"))


@pytest.fixture(autouse=True)
def _mock_event_bus():
    class _MockEventBus:
        async def publish(self, exchange, routing_key, message):
            pass

        async def consume(self, queue, callback, exchange=None, routing_key=None):
            pass

    container.event_bus.override(providers.Object(_MockEventBus()))
    yield


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
