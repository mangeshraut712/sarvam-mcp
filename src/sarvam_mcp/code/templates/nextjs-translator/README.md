# ${PROJECT_NAME}

Next.js Indic translator UI powered by Sarvam (Mayura v1 + Sarvam-Translate v1).

## Setup

```bash
cp .env.example .env.local        # add your SARVAM_API_KEY
npm install
npm run dev                        # http://localhost:3000
```

Get an API key: https://dashboard.sarvam.ai

## What's inside

- `app/page.tsx` — the translator UI (textarea + language picker + button)
- `app/api/translate/route.ts` — server route that calls Sarvam's `/translate` (your API key never touches the browser)
- `app/lib/languages.ts` — supported language list

Defaults to translating English → `${DEFAULT_TARGET_LANG}`. Edit `app/lib/languages.ts` to extend the picker.

## Deploy

Drop into Vercel: connect the repo, set `SARVAM_API_KEY` in Project Settings → Environment Variables. Done.
