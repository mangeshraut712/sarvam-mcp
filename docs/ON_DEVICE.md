# On-device / local runtime (this fork)

This is **not** a reproduction of anyone’s interview take-home. It is an
original, testable contract for the *kind of thinking* those loops reward:
failure as default, memory ceilings, fair slots, typed streams, explicit
cloud opt-in.

## What official Sarvam GitHub actually contains

| Repo | Fit for on-device work |
|---|---|
| [sarvamai/sarvam-mcp](https://github.com/sarvamai/sarvam-mcp) | Cloud MCP tools. This fork adds `sarvam_mcp.runtime` + Vaani. |
| [sarvamai/sarvam-ai-cookbook](https://github.com/sarvamai/sarvam-ai-cookbook) | Cloud notebooks. Best upstream PR: “route local vs hosted” without shipping 30B. |
| [sarvamai/skills](https://github.com/sarvamai/skills) | Cursor/Claude skills for chat/STT/TTS. On-device skill waits on GGUF. |
| [sarvamai/sarvam-ai-sdk](https://github.com/sarvamai/sarvam-ai-sdk) | Hosted Vercel AI SDK provider. |
| [sarvamai/model-deployments](https://github.com/sarvamai/model-deployments) | Empty README when last checked. |
| [sarvamai/sarvam-30b](https://huggingface.co/sarvamai/sarvam-30b) (HF) | Open weights; laptop GGUF needs patched llama.cpp (`sarvam_moe`). Ollama still blocked. |

## Code in this repo

- `src/sarvam_mcp/runtime/` — device profile, slot scheduler, supervisor
- `sarvam_code_ondevice_runtime` — builder guide (no API calls)
- `sarvam_tools_local_infer` — echo-token demo; put `__CRASH__` in the prompt

```python
from sarvam_mcp.runtime import DeviceProfile, SlotScheduler, Supervisor, choose_backend

choose_backend(DeviceProfile(allow_cloud=False), prefer="cloud")  # PermissionError
```
