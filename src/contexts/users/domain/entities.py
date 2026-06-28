from dataclasses import dataclass
from uuid import uuid4

import bcrypt


@dataclass
class User:
    id: str
    name: str
    email: str
    password_hash: str

    @classmethod
    def create(cls, name: str, email: str, password: str) -> "User":
        return cls(id=str(uuid4()), name=name, email=email, password_hash=cls._hash_password(password))

    @staticmethod
    def _hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
