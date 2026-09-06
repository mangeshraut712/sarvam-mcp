"""B11 — error taxonomy. Clients retry only what is retryable."""

from __future__ import annotations


class InferenceClientError(ValueError):
    """Malformed request — do not retry."""


class TransientInferenceError(RuntimeError):
    """Worker restarting / probe failed — retry with backoff."""


class FatalInferenceError(RuntimeError):
    """Will not recover automatically — surface to the user."""


class ResourceExhaustedError(RuntimeError):
    """Admission refused — RAM or queue full."""
