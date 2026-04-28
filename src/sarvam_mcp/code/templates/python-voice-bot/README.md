# ${PROJECT_NAME}

End-to-end Indic voice loop in one file: **STT → Sarvam-M → TTS**.

## Run

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export SARVAM_API_KEY=sk_...
python bot.py voice-memo.wav --out reply.wav
```

## How it works

1. `transcribe()` — Saarika v2.5 (`/speech-to-text`)
2. `chat()` — Sarvam-M (`/v1/chat/completions`)
3. `synthesize()` — Bulbul v3 with speaker `${DEFAULT_SPEAKER}` (`/text-to-speech`)

Tweak the system prompt, model size (`sarvam-m` → `sarvam-105b`), and speaker to taste.
