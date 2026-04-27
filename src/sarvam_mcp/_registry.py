"""Tool-registration helpers + shared context plumbed into every tool."""

from __future__ import annotations

from dataclasses import dataclass

from sarvam_mcp.audio import AudioSink
from sarvam_mcp.config import Config
from sarvam_mcp.http import SarvamClient


@dataclass
class ServerContext:
    """The bundle every tool needs. Stashed on the FastMCP lifespan context."""

    config: Config
    client: SarvamClient
    audio_sink: AudioSink
