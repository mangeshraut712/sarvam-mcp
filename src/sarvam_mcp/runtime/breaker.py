"""B6 — circuit breaker for a hardware backend (closed / open / half-open)."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Literal

State = Literal["closed", "open", "half_open"]


class CircuitBreaker:
    def __init__(
        self,
        *,
        failure_threshold: int = 2,
        cooldown_s: float = 1.0,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.cooldown_s = cooldown_s
        self._clock = clock or time.monotonic
        self.state: State = "closed"
        self.failures = 0
        self._open_until = 0.0

    def allow(self) -> bool:
        if self.state == "closed":
            return True
        if self.state == "open":
            if self._clock() >= self._open_until:
                self.state = "half_open"
                return True
            return False
        return True  # one probe in half-open

    def record_success(self) -> None:
        self.failures = 0
        self.state = "closed"

    def record_failure(self) -> None:
        self.failures += 1
        if self.state == "half_open" or self.failures >= self.failure_threshold:
            self.state = "open"
            self._open_until = self._clock() + self.cooldown_s
