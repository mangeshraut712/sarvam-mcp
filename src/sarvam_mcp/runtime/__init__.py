"""On-device / local runtime helpers (original — not an interview transcript).

Public Sarvam GitHub is cloud-first. This module is the local counterpart:
typed stream events, memory budgets, fair slots, crash isolation, and
explicit cloud opt-in.
"""

from sarvam_mcp.runtime.device import DeviceProfile, can_load_model, choose_backend
from sarvam_mcp.runtime.events import stream_event
from sarvam_mcp.runtime.scheduler import SlotScheduler
from sarvam_mcp.runtime.supervisor import Supervisor, WorkerCrashError, echo_tokens

__all__ = [
    "DeviceProfile",
    "SlotScheduler",
    "Supervisor",
    "WorkerCrashError",
    "can_load_model",
    "choose_backend",
    "echo_tokens",
    "stream_event",
]
