from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.clock import utc_now
from app.domain.entities.user import User
from app.domain.errors import NotFoundError
from app.infrastructure.database.models import UserModel
from app.infrastructure.repositories.mappers import to_user


class SqlAlchemyUserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, user_id: str) -> User | None:
        row = self._session.get(UserModel, user_id)
        return to_user(row) if row else None

    def get_by_email(self, email: str) -> User | None:
        row = self._session.scalar(select(UserModel).where(UserModel.email == email))
        return to_user(row) if row else None

    def get_by_username(self, username: str) -> User | None:
        row = self._session.scalar(select(UserModel).where(UserModel.username == username))
        return to_user(row) if row else None

    def add(self, user: User) -> User:
        row = UserModel(
            id=user.id,
            email=user.email,
            username=user.username,
            hashed_password=user.hashed_password,
            display_name=user.display_name,
            xp=user.xp,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        self._session.add(row)
        self._session.flush()
        return to_user(row)

    def add_xp(self, user_id: str, amount: int) -> User:
        row = self._session.get(UserModel, user_id)
        if row is None:
            raise NotFoundError("User not found.")
        row.xp += amount
        row.updated_at = utc_now()
        self._session.flush()
        return to_user(row)
