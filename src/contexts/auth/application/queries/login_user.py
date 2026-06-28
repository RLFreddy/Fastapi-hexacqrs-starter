from dataclasses import dataclass


@dataclass
class LoginUserQuery:
    email: str
    password: str
