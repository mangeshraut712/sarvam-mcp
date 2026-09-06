"""C5 / B7 — O(1) LRU and LRU-K for model-swap eviction."""

from __future__ import annotations

from collections import OrderedDict, deque


class LruCache:
    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self.capacity = capacity
        self._data: OrderedDict[str, int] = OrderedDict()

    def touch(self, key: str, size_mb: int = 0) -> str | None:
        """Insert or refresh. Returns evicted key if over capacity."""
        if key in self._data:
            self._data.move_to_end(key)
            self._data[key] = size_mb
            return None
        evicted = None
        if len(self._data) >= self.capacity:
            evicted, _ = self._data.popitem(last=False)
        self._data[key] = size_mb
        return evicted

    def victim(self) -> str | None:
        return next(iter(self._data), None)


class LruK:
    """Evict the key whose K-th most recent access is oldest."""

    def __init__(self, k: int = 2) -> None:
        if k < 1:
            raise ValueError("k must be >= 1")
        self.k = k
        self._hits: dict[str, deque[int]] = {}
        self._tick = 0

    def touch(self, key: str) -> None:
        self._tick += 1
        hist = self._hits.setdefault(key, deque(maxlen=self.k))
        hist.append(self._tick)

    def victim(self, keys: list[str]) -> str:
        def rank(name: str) -> tuple[int, int]:
            hist = self._hits.get(name)
            if not hist or len(hist) < self.k:
                return (0, hist[0] if hist else -1)
            return (1, hist[0])

        return min(keys, key=rank)
