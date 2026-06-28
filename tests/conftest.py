import os

os.environ["DATABASE_URL"] = "sqlite:///test.db"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["RABBITMQ_URL"] = "amqp://guest:guest@localhost:5672/"

import pytest
from dependency_injector import providers
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from src.main import app, container
from src.shared.infrastructure.database import Base


@pytest.fixture(scope="session", autouse=True)
def _setup_db():
    engine = create_engine("sqlite:///test.db")
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()


@pytest.fixture(autouse=True)
def _clean_db():
    from src.shared.infrastructure.database import SessionLocal

    session = SessionLocal()
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    session.close()


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
