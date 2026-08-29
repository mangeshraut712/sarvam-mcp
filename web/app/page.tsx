"use client";

import { useCallback, useRef } from "react";
import Link from "next/link";

import { Ornament } from "@/components/Ornament";
import { ApiStatus } from "@/components/ApiStatus";

const JSON_CONFIG = `{
  "mcpServers": {
    "sarvam": {
      "command": "uvx",
      "args": ["sarvam-mcp"],
      "env": {
        "SARVAM_API_KEY": "your_api_key_here"
      }
    }
  }
}`;

const CAPABILITIES = [
  { name: "Speech to Text", detail: "Saaras — 23 Indic languages" },
  { name: "Text to Speech", detail: "Bulbul voices, streaming ready" },
  { name: "Translation", detail: "Mayura across Indian languages" },
  { name: "Language ID", detail: "Script + language detection" },
  { name: "Indic LLM", detail: "Chat completions in the user’s language" },
  { name: "Document AI", detail: "Vision jobs for PDFs and scans" },
];

export default function Home() {
  const iconRef = useRef<SVGSVGElement>(null);

  const copyJson = useCallback(() => {
    void navigator.clipboard.writeText(JSON_CONFIG);
    const icon = iconRef.current;
    if (!icon) return;

    icon.innerHTML =
      '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>';
    icon.style.color = "#1a7a3a";

    setTimeout(() => {
      icon.innerHTML =
        '<rect x="9" y="9" width="13" height="13" rx="2" ry="2" stroke-width="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" stroke-width="2"/>';
      icon.style.color = "";
    }, 1500);
  }, []);

  return (
    <>
      <section className="hero">
        <div className="hero-glow" aria-hidden="true" />
        <p className="eyebrow">India&apos;s sovereign AI, as MCP tools</p>
        <Ornament className="hero-ornament" />
        <h1 className="display">AI for all from India</h1>
        <p className="lede">
          Drop Sarvam speech, language, and document APIs into Cursor, Claude,
          Windsurf, or Zed. One config. Twenty-two languages. No boilerplate.
        </p>
        <div className="hero-actions">
          <Link className="btn btn-solid" href="/playground">
            Try Voice Agent
          </Link>
          <a
            className="btn btn-ghost"
            href="https://dashboard.sarvam.ai/key-management"
            target="_blank"
            rel="noopener noreferrer"
          >
            Get API Key
          </a>
        </div>
        <ApiStatus />
      </section>

      <section className="trust">
        <p className="trust-label">Works inside the agents you already use</p>
        <ul className="trust-row">
          <li>Cursor</li>
          <li>Claude Desktop</li>
          <li>Claude Code</li>
          <li>Windsurf</li>
          <li>Zed</li>
        </ul>
      </section>

      <section className="platform">
        <h2 className="display display-md">The AI platform India builds on</h2>
        <p className="section-copy">
          These are not demo-only functions. The playground uses the same
          primitives your MCP client calls: STT, language ID, LLM, TTS.
        </p>
        <div className="platform-card">
          <div className="platform-tabs">
            <span className="tab is-active">Voice Agents</span>
            <span className="tab">Speech to Text</span>
            <span className="tab">Text to Speech</span>
            <span className="tab">Translation</span>
          </div>
          <div className="platform-body">
            <div>
              <p className="platform-kicker">Same-language loop</p>
              <h3>Speak Marathi. Hear Marathi.</h3>
              <p>
                Hold to speak, watch the tool chain, play the reply. No
                English gate. The user never has to switch languages.
              </p>
              <Link className="btn btn-solid" href="/playground">
                Open playground
              </Link>
            </div>
            <ol className="flow-list">
              <li>STT transcribe</li>
              <li>Language ID</li>
              <li>Indic LLM</li>
              <li>TTS speak</li>
            </ol>
          </div>
        </div>
      </section>

      <section className="caps">
        <h2 className="display display-md">Every public Sarvam API as a tool</h2>
        <div className="caps-grid">
          {CAPABILITIES.map((item) => (
            <article key={item.name} className="cap-card">
              <h3>{item.name}</h3>
              <p>{item.detail}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="setup">
        <h2 className="display display-md">Paste into your MCP client</h2>
        <p className="section-copy">
          API key optional upfront — the server can ask on first use. Or set{" "}
          <code>SARVAM_API_KEY</code> in the JSON.
        </p>
        <button type="button" className="cmd" onClick={copyJson}>
          <code>{JSON_CONFIG}</code>
          <svg
            ref={iconRef}
            className="copy-icon"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2" strokeWidth="2" />
            <path
              d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"
              strokeWidth="2"
            />
          </svg>
        </button>
      </section>

      <section className="cta-band">
        <h2 className="display display-md invert">
          Build the future of India&apos;s AI with Sarvam
        </h2>
        <a
          className="btn btn-solid btn-on-dark"
          href="https://dashboard.sarvam.ai/key-management"
          target="_blank"
          rel="noopener noreferrer"
        >
          Sign up
        </a>
      </section>
    </>
  );
}
