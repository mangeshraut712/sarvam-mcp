"""${PROJECT_NAME} — minimal Sarvam TTS CLI.

Usage:
    python tts.py "नमस्ते दुनिया" --out hello.wav
    python tts.py "Hello world" --lang en-IN --speaker priya --out hello.wav
"""

from __future__ import annotations

import argparse
import base64
import os
import sys

import httpx

SARVAM_BASE = "https://api.sarvam.ai"
DEFAULT_LANGUAGE = "${DEFAULT_LANGUAGE}"
DEFAULT_SPEAKER = "${DEFAULT_SPEAKER}"


def synthesize(text: str, *, language: str, speaker: str, out_path: str) -> None:
    api_key = os.environ.get("SARVAM_API_KEY")
    if not api_key:
        sys.exit("SARVAM_API_KEY not set. Get one at https://dashboard.sarvam.ai.")

    resp = httpx.post(
        f"{SARVAM_BASE}/text-to-speech",
        headers={"api-subscription-key": api_key},
        json={
            "inputs": [text],
            "target_language_code": language,
            "speaker": speaker,
            "model": "bulbul:v3",
            "speech_sample_rate": 24000,
            "enable_preprocessing": True,
        },
        timeout=60.0,
    )
    resp.raise_for_status()
    data = resp.json()
    audio_b64 = (data.get("audios") or [None])[0]
    if not audio_b64:
        sys.exit(f"No audio in response: {data!r}")
    wav = base64.b64decode(audio_b64)
    with open(out_path, "wb") as fh:
        fh.write(wav)
    print(f"✓ wrote {len(wav):,} bytes → {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("text", help="Text to synthesize.")
    parser.add_argument("--lang", default=DEFAULT_LANGUAGE, help=f"BCP-47 code (default: {DEFAULT_LANGUAGE}).")
    parser.add_argument("--speaker", default=DEFAULT_SPEAKER, help=f"Bulbul v3 speaker (default: {DEFAULT_SPEAKER}).")
    parser.add_argument("--out", default="out.wav", help="Output WAV path.")
    args = parser.parse_args()
    synthesize(args.text, language=args.lang, speaker=args.speaker, out_path=args.out)


if __name__ == "__main__":
    main()
