from typing import Optional

from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import Session

from src.contexts.auth.domain.entities import AuthUser
from src.contexts.auth.domain.repositories import AuthRepository
from src.shared.infrastructure.database import Base


class AuthUserModel(Base):
    __tablename__ = "auth_users"
    id = Column(String(36), primary_key=True)
    email = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class SQLAlchemyAuthRepository(AuthRepository):
    def __init__(self, session: Session):
        self.session = session

    def _to_domain(self, model: AuthUserModel) -> AuthUser:
        return AuthUser(id=model.id, email=model.email, password_hash=model.password_hash, is_active=model.is_active)

    def save(self, user: AuthUser) -> None:
        user_model = AuthUserModel(
            id=user.id, email=user.email, password_hash=user.password_hash, is_active=user.is_active
        )
        self.session.add(user_model)
        self.session.commit()

    def find_by_email(self, email: str) -> Optional[AuthUser]:
        user_model = self.session.query(AuthUserModel).filter_by(email=email).first()
        return self._to_domain(user_model) if user_model else None

    def find_by_id(self, user_id: str) -> Optional[AuthUser]:
        user_model = self.session.query(AuthUserModel).filter_by(id=user_id).first()
        return self._to_domain(user_model) if user_model else None

    def get_all(self) -> list[AuthUser]:
        return [self._to_domain(u) for u in self.session.query(AuthUserModel).all()]
