"""Device profile and explicit cloud opt-in.

Cloud is never a silent fallback. A phone with 4 GB RAM and no NPU should
refuse a second model instead of shipping tokens to the network.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DeviceProfile:
    ram_mb: int = 8192
    has_npu: bool = False
    allow_cloud: bool = False
    max_slots: int = 2
    model_budget_mb: int = 4096
    backends: tuple[str, ...] = field(default=("cpu",))


def choose_backend(device: DeviceProfile, prefer: str | None = None) -> str:
    """Pick a local backend. ``cloud`` only if the caller opted in."""
    if prefer == "cloud":
        if not device.allow_cloud:
            raise PermissionError(
                "Cloud fallback is disabled. Set allow_cloud=true on the device profile."
            )
        return "cloud"
    if prefer == "npu" and device.has_npu:
        return "npu"
    if prefer in device.backends:
        return prefer
    if device.has_npu:
        return "npu"
    return "cpu"


def can_load_model(device: DeviceProfile, already_loaded_mb: int, incoming_mb: int) -> bool:
    return already_loaded_mb + incoming_mb <= device.model_budget_mb
