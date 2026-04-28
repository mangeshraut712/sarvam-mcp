"""${PROJECT_NAME} — minimal Sarvam voice loop.

Pipeline: audio in → Saarika STT → Sarvam-M reply → Bulbul TTS → audio out.
"""

from __future__ import annotations

import argparse
import base64
import os
import sys

import httpx

SARVAM_BASE = "https://api.sarvam.ai"
REPLY_LANGUAGE = "${REPLY_LANGUAGE}"
DEFAULT_SPEAKER = "${DEFAULT_SPEAKER}"

SYSTEM_PROMPT = (
    "You are a concise, helpful assistant fluent in Indic languages. "
    "Reply in the user's input language unless asked otherwise. Keep answers short."
)


def _api_key() -> str:
    key = os.environ.get("SARVAM_API_KEY")
    if not key:
        sys.exit("SARVAM_API_KEY not set. Get one at https://dashboard.sarvam.ai.")
    return key


def transcribe(audio_path: str, *, language: str = "unknown") -> tuple[str, str]:
    """Audio file → (transcript, detected_language)."""
    with open(audio_path, "rb") as fh:
        files = {"file": (os.path.basename(audio_path), fh, "audio/wav")}
        data = {"model": "saarika:v2.5", "language_code": language, "with_timestamps": "false"}
        resp = httpx.post(
            f"{SARVAM_BASE}/speech-to-text",
            headers={"api-subscription-key": _api_key()},
            data=data,
            files=files,
            timeout=120.0,
        )
    resp.raise_for_status()
    body = resp.json()
    return body.get("transcript", ""), body.get("language_code") or language


def chat(transcript: str) -> str:
    resp = httpx.post(
        f"{SARVAM_BASE}/v1/chat/completions",
        headers={"api-subscription-key": _api_key()},
        json={
            "model": "sarvam-m",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": transcript},
            ],
            "temperature": 0.4,
            "max_tokens": 400,
        },
        timeout=60.0,
    )
    resp.raise_for_status()
    return (resp.json()["choices"][0]["message"]["content"] or "").strip()


def synthesize(text: str, *, language: str, speaker: str, out_path: str) -> None:
    resp = httpx.post(
        f"{SARVAM_BASE}/text-to-speech",
        headers={"api-subscription-key": _api_key()},
        json={
            "inputs": [text],
            "target_language_code": language,
            "speaker": speaker,
            "model": "bulbul:v3",
            "speech_sample_rate": 24000,
        },
        timeout=60.0,
    )
    resp.raise_for_status()
    audio_b64 = resp.json()["audios"][0]
    with open(out_path, "wb") as fh:
        fh.write(base64.b64decode(audio_b64))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("audio_in", help="Input audio file.")
    parser.add_argument("--out", default="reply.wav", help="Output audio path.")
    parser.add_argument("--lang", default="unknown", help="STT language hint.")
    parser.add_argument("--speaker", default=DEFAULT_SPEAKER, help="Bulbul v3 speaker.")
    parser.add_argument("--reply-lang", default=REPLY_LANGUAGE, help="TTS language.")
    args = parser.parse_args()

    print(f"→ transcribing {args.audio_in}…")
    transcript, detected = transcribe(args.audio_in, language=args.lang)
    print(f"  detected: {detected}")
    print(f"  user said: {transcript}\n")

    print("→ asking Sarvam-M…")
    reply = chat(transcript)
    print(f"  reply: {reply}\n")

    print(f"→ synthesizing reply audio…")
    synthesize(reply, language=args.reply_lang, speaker=args.speaker, out_path=args.out)
    print(f"✓ wrote {args.out}")


if __name__ == "__main__":
    main()
