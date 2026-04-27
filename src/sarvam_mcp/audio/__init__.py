"""Audio output strategies: files / resources / both."""

from sarvam_mcp.audio.sinks import (
    AudioSink,
    BothSink,
    FileSink,
    ResourceSink,
    StoredAudio,
    build_sink,
)
from sarvam_mcp.audio.uris import build_resource_uri, parse_resource_uri

__all__ = [
    "AudioSink",
    "FileSink",
    "ResourceSink",
    "BothSink",
    "StoredAudio",
    "build_sink",
    "build_resource_uri",
    "parse_resource_uri",
]
