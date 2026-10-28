from datetime import timedelta

import jwt

from app.core.clock import utc_now
from app.domain.errors import UnauthorizedError


class JwtTokenProvider:
    def __init__(self, secret: str, algorithm: str, expire_minutes: int) -> None:
        self._secret = secret
        self._algorithm = algorithm
        self._expire_minutes = expire_minutes

    def create_access_token(self, user_id: str) -> str:
        now = utc_now()
        payload = {
            "sub": user_id,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=self._expire_minutes)).timestamp()),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def read_user_id(self, token: str) -> str:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except jwt.PyJWTError as exc:
            raise UnauthorizedError("Invalid or expired token.") from exc
        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject:
            raise UnauthorizedError("Invalid or expired token.")
        return subject
