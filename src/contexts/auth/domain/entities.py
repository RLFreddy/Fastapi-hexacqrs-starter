from dataclasses import dataclass
from uuid import uuid4

import bcrypt


@dataclass
class AuthUser:
    id: str
    email: str
    password_hash: str
    is_active: bool = True

    @classmethod
    def create(cls, email: str, password: str) -> "AuthUser":
        return AuthUser(id=str(uuid4()), email=email, password_hash=cls._hash_password(password))

    @staticmethod
    def _hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())
