import time
from collections import defaultdict, deque
from threading import Lock

from app.domain.errors import RateLimitError


class InMemoryRateLimiter:
    """Process-local limiter. It does not coordinate across multiple API workers."""

    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def reset(self) -> None:
        with self._lock:
            self._events.clear()

    def check(self, key: str, *, limit: int, window_seconds: int) -> None:
        now = time.monotonic()
        with self._lock:
            events = self._events[key]
            while events and now - events[0] > window_seconds:
                events.popleft()
            if len(events) >= limit:
                raise RateLimitError("Too many requests. Wait a moment and try again.")
            events.append(now)


rate_limiter = InMemoryRateLimiter()
