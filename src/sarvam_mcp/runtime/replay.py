"""B8 — bounded ring buffer so a dropped SSE/IPC client can resume."""

from __future__ import annotations

from collections import deque


class TokenReplayBuffer:
    """Keeps the last ``maxlen`` emitted tokens for one generation."""

    def __init__(self, maxlen: int = 64) -> None:
        if maxlen < 1:
            raise ValueError("maxlen must be >= 1")
        self._maxlen = maxlen
        self._items: deque[tuple[int, str]] = deque(maxlen=maxlen)

    def append(self, index: int, text: str) -> None:
        self._items.append((index, text))

    def replay_from(self, index: int) -> list[tuple[int, str]] | None:
        """Return tokens with seq >= index, or None if that prefix aged out."""
        if not self._items:
            return [] if index == 0 else None
        oldest = self._items[0][0]
        if index < oldest:
            return None
        return [(i, t) for i, t in self._items if i >= index]

    def __len__(self) -> int:
        return len(self._items)
