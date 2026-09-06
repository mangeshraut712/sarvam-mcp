from __future__ import annotations

import pytest

from sarvam_mcp.runtime.device import DeviceProfile, can_load_model, choose_backend
from sarvam_mcp.runtime.scheduler import SlotScheduler
from sarvam_mcp.runtime.supervisor import Supervisor, WorkerCrashError


def test_cloud_is_never_silent() -> None:
    device = DeviceProfile(allow_cloud=False)
    with pytest.raises(PermissionError):
        choose_backend(device, prefer="cloud")
    opted = DeviceProfile(allow_cloud=True)
    assert choose_backend(opted, prefer="cloud") == "cloud"


def test_memory_ceiling() -> None:
    phone = DeviceProfile(model_budget_mb=2048)
    assert can_load_model(phone, 1800, 200) is True
    assert can_load_model(phone, 1800, 400) is False


async def test_crash_then_resume_is_idempotent() -> None:
    supervisor = Supervisor(scheduler=SlotScheduler(max_slots=1))
    first = [
        event
        async for event in supervisor.stream(
            "namaste __CRASH__ mitra",
            request_id="gen-1",
        )
    ]
    assert first[-1]["type"] == "error"
    assert supervisor.restarts == 1
    assert supervisor.tokens_for("gen-1") == ["namaste"]

    resume_seq = first[-1]["seq"]
    second = [
        event
        async for event in supervisor.stream(
            "namaste __CRASH__ mitra",
            request_id="gen-1",
            resume_from_seq=resume_seq,
        )
    ]
    texts = [e["text"] for e in second if e["type"] == "token"]
    assert texts == ["mitra"]
    assert second[-1]["type"] == "done"
    assert supervisor.tokens_for("gen-1") == ["namaste", "mitra"]


async def test_unisolated_crash_propagates() -> None:
    supervisor = Supervisor(scheduler=SlotScheduler(max_slots=1))
    with pytest.raises(WorkerCrashError):
        async for _ in supervisor.stream(
            "a __CRASH__ b",
            request_id="x",
            isolate_crash=False,
        ):
            pass


async def test_ondevice_code_tool() -> None:
    from sarvam_mcp.code.ondevice import GUIDE

    assert "sarvam-mcp" in " ".join(GUIDE["sarvam_repos"]["points"])
