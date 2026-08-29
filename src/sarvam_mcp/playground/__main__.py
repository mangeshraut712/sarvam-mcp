"""CLI entry for the Voice Agent Playground pipeline.

Used by the Next.js API route to run the Sarvam pipeline without duplicating HTTP clients.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Sarvam Voice Agent Playground pipeline.")
    parser.add_argument("--audio-path", required=True, help="Path to an audio file (webm, wav, etc.)")
    args = parser.parse_args()

    audio_path = Path(args.audio_path)
    if not audio_path.is_file():
        print(json.dumps({"ok": False, "error": f"Audio file not found: {audio_path}"}))
        sys.exit(1)

    from sarvam_mcp.playground.pipeline import run_pipeline

    try:
        result = asyncio.run(run_pipeline(audio_path))
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc), "steps": []}))
        sys.exit(1)

    print(json.dumps(result, ensure_ascii=False))
    if not result.get("ok"):
        sys.exit(1)


if __name__ == "__main__":
    main()
