from abc import ABC, abstractmethod
from typing import Optional

from .entities import User


class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> None:
        pass

    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_all(self) -> list[User]:
        pass

    @abstractmethod
    def get_all_paginated(self, page: int, size: int) -> tuple[list[User], int]:
        pass
