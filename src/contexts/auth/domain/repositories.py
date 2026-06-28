from abc import ABC, abstractmethod
from typing import Optional

from .entities import AuthUser


class AuthRepository(ABC):
    @abstractmethod
    def save(self, user: AuthUser) -> None:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[AuthUser]:
        pass

    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[AuthUser]:
        pass

    @abstractmethod
    def get_all(self) -> list[AuthUser]:
        pass
