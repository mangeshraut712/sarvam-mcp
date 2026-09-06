"""Crash-isolated inference worker + supervisor.

The worker is allowed to die. The supervisor is not. Clients resume from
``seq`` using the same ``request_id`` so a retry does not duplicate tokens.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field

from sarvam_mcp.runtime.events import stream_event
from sarvam_mcp.runtime.replay import TokenReplayBuffer
from sarvam_mcp.runtime.scheduler import SlotScheduler


class WorkerCrashError(Exception):
    """Raised inside a worker to simulate an inference process dying."""


TokenFn = Callable[[str, int], AsyncIterator[str]]


async def echo_tokens(prompt: str, start_seq: int) -> AsyncIterator[str]:
    """Deterministic backend for tests and demos (not a real LLM)."""
    pieces = prompt.strip().split()
    if not pieces:
        pieces = ["(empty)"]
    for i, word in enumerate(pieces):
        if word == "__CRASH__":
            if start_seq == 0:
                raise WorkerCrashError("inference worker aborted")
            continue
        if i < start_seq:
            continue
        await asyncio.sleep(0)
        yield word


@dataclass
class Supervisor:
    scheduler: SlotScheduler
    generate_tokens: TokenFn = echo_tokens
    _cache: dict[str, list[str]] = field(default_factory=dict)
    replay: TokenReplayBuffer = field(default_factory=lambda: TokenReplayBuffer(maxlen=64))
    restarts: int = 0

    def tokens_for(self, request_id: str) -> list[str]:
        return list(self._cache.get(request_id, []))

    async def stream(
        self,
        prompt: str,
        *,
        request_id: str,
        resume_from_seq: int = 0,
        kind: str = "interactive",
        isolate_crash: bool = True,
    ) -> AsyncIterator[dict]:
        async with self.scheduler.acquire(kind):
            produced = self._cache.setdefault(request_id, [])
            seq = resume_from_seq
            try:
                async for token in self.generate_tokens(prompt, resume_from_seq):
                    produced.append(token)
                    self.replay.append(seq, token)
                    yield stream_event(
                        type="token",
                        request_id=request_id,
                        seq=seq,
                        text=token,
                    )
                    seq += 1
                yield stream_event(
                    type="done",
                    request_id=request_id,
                    seq=seq,
                    finish_reason="stop",
                )
            except WorkerCrashError as exc:
                self.restarts += 1
                if not isolate_crash:
                    raise
                yield stream_event(
                    type="error",
                    request_id=request_id,
                    seq=seq,
                    error=f"worker_crash:{exc}; resume_from_seq={seq}",
                    recoverable=True,
                    code="WORKER_CRASHED",
                )
