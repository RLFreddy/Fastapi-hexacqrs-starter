from typing import Optional

from sqlalchemy import Column, String
from sqlalchemy.orm import Session

from src.contexts.users.domain.entities import User
from src.contexts.users.domain.repositories import UserRepository
from src.shared.infrastructure.database import Base


class UserModel(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(100), nullable=False)


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session):
        self.session = session

    def _to_domain(self, model: UserModel) -> User:
        return User(id=model.id, name=model.name, email=model.email, password_hash=model.password_hash)

    def save(self, user: User) -> None:
        user_model = UserModel(id=user.id, name=user.name, email=user.email, password_hash=user.password_hash)
        self.session.add(user_model)
        self.session.commit()

    def find_by_id(self, user_id: str) -> Optional[User]:
        user_model = self.session.query(UserModel).filter_by(id=user_id).first()
        return self._to_domain(user_model) if user_model else None

    def get_all(self) -> list[User]:
        return [self._to_domain(u) for u in self.session.query(UserModel).all()]
