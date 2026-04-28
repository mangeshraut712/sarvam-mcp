# ${PROJECT_NAME}

Minimal CLI that synthesizes speech via Sarvam's Bulbul v3 TTS.

## Run

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export SARVAM_API_KEY=sk_...     # https://dashboard.sarvam.ai
python tts.py "नमस्ते" --out hello.wav
```

Defaults: language `${DEFAULT_LANGUAGE}`, speaker `${DEFAULT_SPEAKER}`.

## Usage

```bash
python tts.py <text> [--lang <bcp47>] [--speaker <id>] [--out <wav-path>]
```
