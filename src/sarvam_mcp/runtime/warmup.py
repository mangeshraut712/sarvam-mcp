"""B7 / B10 — warm standby vs cold start after a worker crash."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WarmPool:
    primary_ready: bool = True
    standby_ready: bool = True
    cold_start_ms: int = 2500
    handoff_ms: int = 40

    def recover_ms(self) -> int:
        if self.standby_ready:
            self.primary_ready = True
            self.standby_ready = False
            return self.handoff_ms
        return self.cold_start_ms
