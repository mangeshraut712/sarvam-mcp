# WebMCP Challenge — submission pack

Official source: [The WebMCP Challenge rules](https://webmcp.devpost.com/rules) and [hackathon home](https://webmcp.devpost.com/). Plugin output is not the source of truth.

## Deadline

**3 September 2026, 1:00pm PDT** (registration and submission close together). Judging 4–21 Sep; winners around 23 Sep.

Do not edit the Devpost submission, repo, or live site after that close until winners are announced.

## Eligibility (verify yourself)

- Age of majority; OpenAI API supported country/territory.
- **Not** Brazil, China, Hong Kong, Quebec, Russia, Crimea, Cuba, Iran, North Korea, Syria, Venezuela, Donetsk/Luhansk, OFAC-listed, or other excluded places in the official rules.
- India is not on that excluded list as published; still confirm against the live rules and [OpenAI supported countries](https://platform.openai.com/docs/supported-countries) when registering.
- Not a judge, sponsor employee, or conflicted party.

Register at [webmcp.devpost.com](https://webmcp.devpost.com/) (Join Hackathon). Optional Netlify credits form by **1 Sep 12:00pm PT**.

## What judges must receive

| Requirement | Status in this repo | You still do |
| --- | --- | --- |
| WebMCP-powered web app (humans + agents) | `/vaani` registers 6 tools via `document.modelContext.registerTool` | Test in ChatGPT in-app browser or Chrome 149+ `chrome://flags/#enable-webmcp-testing` |
| Working **live URL** (Vercel/Netlify/Cloudflare/Render/ChatGPT Sites, etc.) | Docker + Vercel config in `web/` | Deploy and paste URL on Devpost |
| Public repo with **all source** + run instructions | This GitHub repo | Keep it public |
| **Open-source license** visible on GitHub | Root `LICENSE` (MIT) | Confirm GitHub About shows MIT |
| English text description (fit, UX, human+agent, how WebMCP) | This file + README | Paste into Devpost fields |
| Public **YouTube** demo **&lt; 3 minutes**, with **audio**, no unlicensed music | Not uploadable from this agent | Record and link |
| Function matches video/description | Tools update shared UI | Re-record if the product changes |
| Pre-existing project: document **new WebMCP work in the submission window** | Section below | Point judges at commits from 25 Aug 2026 onward |
| `registerTool` in the repository | `web/components/VaaniWorkspace.tsx` | — |

Judges **may** use the live site; they **may** score from write-up + repo + video only. Keep the live URL free and up through the judging period.

## Judging (equal weight)

1. **WebMCP leverage** — real `registerTool`, shared state, not a thin API wrapper.
2. **Execution** — coherent product, not a PoC dump.
3. **Potential impact** — multilingual / voice-first web for people who do not type English.
4. **Creativity & ambition** — MCP + WebMCP dual surface.

Stage one is pass/fail on theme + actually using WebMCP.

## How to test (paste on Devpost)

1. Open the live URL in **ChatGPT desktop in-app browser**, or Chrome 149+ with WebMCP flag enabled, then restart Chrome.
2. Go to `/vaani`.
3. Confirm the pill says **WebMCP ready · 6 tools**.
4. Prompt the browser agent: “Summarize this in Marathi, then pin a note.”
5. Confirm the **result panel** and **notes** update (same state the human sees).
6. Human path: Hold to speak, Translate, Explain, Summarize, Speak, Pin note.
7. If Sarvam credits are empty, a labeled **demo banner** still mutates UI so the collaboration loop is visible. Add credits at [dashboard.sarvam.ai/billing](https://dashboard.sarvam.ai/billing) for live STT/TTS/LLM/translate. `GET /v1/models` remains unmetered.

## Deploy

```bash
# Vercel (from web/)
cd web && npx vercel --prod --yes
# set SARVAM_API_KEY; optional VAANI_DEMO=0 to disable 402 fallback

# Docker
cd web && docker build -t vaani-web .
docker run --rm -p 8000:8000 -e SARVAM_API_KEY=sk_... -e VAANI_DEMO=1 vaani-web
```

Health: `/health`, `/ready`, `/vaani`, `/api/sarvam-status`.

## Prior work vs Submission Period

- **Before this challenge:** `sarvam-mcp` Python MCP server (STT, TTS, translate, LLM, …) for Cursor/Claude.
- **During Submission Period (from 25 Aug 2026):** Vaani web app, `document.modelContext.registerTool` tools, shared workspace, dual MCP/WebMCP architecture. See git history on `main` / `cursor/vaani-webmcp-0948`.

## Devpost text (draft)

**Why WebMCP:** The agentic web usually assumes English and a keyboard. Vaani lets a human speak Marathi/Hindi while a browser agent calls structured tools that change the same page.

**Better UX:** You see the transcript, translation, summary, and notes the agent writes. No hidden side-channel.

**Together:** “Explain this in Marathi and read it” → `summarize_content` → `translate_content` → `speak_content` → `create_multilingual_note`.

**Implementation:** Page-scoped `registerTool` + `AbortSignal` teardown (current WebML CG draft / Chrome imperative API). Execute handlers call `/api/vaani`, which uses the same Sarvam endpoints as `sarvam-mcp`. Desktop agents still use `uvx sarvam-mcp`.
