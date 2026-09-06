"""Fair-share inference slots so background jobs do not starve interactive ones."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass


@dataclass(frozen=True)
class SlotLease:
    kind: str
    weight: int


class SlotScheduler:
    """Weighted semaphore: interactive requests take priority."""

    WEIGHTS = {"interactive": 3, "background": 1}

    def __init__(self, max_slots: int) -> None:
        if max_slots < 1:
            raise ValueError("max_slots must be >= 1")
        self._max = max_slots
        self._in_use = 0
        self._cond = asyncio.Condition()
        self._waiting: dict[str, int] = {"interactive": 0, "background": 0}

    @asynccontextmanager
    async def acquire(self, kind: str = "interactive") -> AsyncIterator[SlotLease]:
        if kind not in self.WEIGHTS:
            raise ValueError(f"unknown slot kind {kind!r}")
        weight = self.WEIGHTS[kind]
        async with self._cond:
            self._waiting[kind] += 1
            try:
                while not self._may_enter(kind):
                    await self._cond.wait()
                self._in_use += 1
            finally:
                self._waiting[kind] -= 1
        try:
            yield SlotLease(kind=kind, weight=weight)
        finally:
            async with self._cond:
                self._in_use -= 1
                self._cond.notify_all()

    def _may_enter(self, kind: str) -> bool:
        if self._in_use >= self._max:
            return False
        starve = (
            kind == "background"
            and self._waiting["interactive"] > 0
            and self._in_use >= self._max - 1
        )
        return not starve

    @property
    def in_use(self) -> int:
        return self._in_use


def aged_priority(base: int, waited_ms: int, *, age_ms: int = 1000) -> int:
    """B9 — priority aging so background work cannot starve forever."""
    if waited_ms < 0:
        raise ValueError("waited_ms must be >= 0")
    return base + waited_ms // age_ms
