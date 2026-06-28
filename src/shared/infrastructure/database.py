from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.shared.infrastructure.config import settings

engine = create_engine(settings.database_url)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
