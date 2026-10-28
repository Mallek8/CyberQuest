from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: str
    email: str
    username: str
    hashed_password: str
    display_name: str
    xp: int
    created_at: datetime
    updated_at: datetime
