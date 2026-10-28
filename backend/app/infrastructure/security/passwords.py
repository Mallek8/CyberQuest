import bcrypt


class BcryptPasswordHasher:
    def __init__(self, rounds: int) -> None:
        self._rounds = rounds
        self._dummy = bcrypt.hashpw(b"dummy-password", bcrypt.gensalt(rounds=rounds)).decode()

    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt(rounds=self._rounds)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def verify_password(self, password: str, password_hash: str | None) -> bool:
        candidate = password_hash or self._dummy
        try:
            matches = bcrypt.checkpw(password.encode("utf-8"), candidate.encode("utf-8"))
        except ValueError:
            return False
        return bool(matches and password_hash)
