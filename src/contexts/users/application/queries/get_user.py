from dataclasses import dataclass


@dataclass
class GetUserQuery:
    user_id: str
