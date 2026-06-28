from dataclasses import dataclass


@dataclass
class GetUsersQuery:
    page: int = 1
    size: int = 10
