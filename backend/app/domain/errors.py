class DomainError(Exception):
    code = "domain_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    code = "not_found"


class UnauthorizedError(DomainError):
    code = "unauthorized"


class ForbiddenError(DomainError):
    code = "forbidden"


class ConflictError(DomainError):
    code = "conflict"


class InvalidSubmissionError(DomainError):
    code = "invalid_submission"


class RateLimitError(DomainError):
    code = "rate_limited"


class HintLimitError(DomainError):
    code = "hint_limit"
