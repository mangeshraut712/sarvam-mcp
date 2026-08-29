"""CLI for playground pipelines used by the Next.js app.

Subcommands:
  voice      STT → Lang ID → LLM → TTS  (default if --audio-path is set)
  translate  Shared /translate used by Vaani + WebMCP translate_content
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Sarvam playground CLI for the web app.")
    sub = parser.add_subparsers(dest="command")

    voice = sub.add_parser("voice", help="Run the voice agent pipeline.")
    voice.add_argument("--audio-path", required=True)

    translate = sub.add_parser("translate", help="Translate text via Sarvam /translate.")
    translate.add_argument("--text", required=True)
    translate.add_argument("--target-language", required=True)
    translate.add_argument("--source-language", default="auto")

    # Backward compatible: python -m sarvam_mcp.playground --audio-path …
    parser.add_argument("--audio-path", dest="legacy_audio_path")

    args = parser.parse_args()

    if args.command == "translate":
        from sarvam_mcp.playground.translate import translate_content

        try:
            result = asyncio.run(
                translate_content(
                    args.text,
                    args.target_language,
                    source_language=args.source_language,
                )
            )
        except Exception as exc:
            print(json.dumps({"ok": False, "error": str(exc)}))
            sys.exit(1)
        print(json.dumps(result, ensure_ascii=False))
        if not result.get("ok"):
            sys.exit(1)
        return

    audio = args.legacy_audio_path
    if args.command == "voice":
        audio = args.audio_path
    if not audio:
        parser.error("Provide --audio-path or use the voice/translate subcommands.")

    audio_path = Path(audio)
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
