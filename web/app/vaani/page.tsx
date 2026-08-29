"use client";

import Link from "next/link";

import { Ornament } from "@/components/Ornament";
import { ApiStatus } from "@/components/ApiStatus";
import { VaaniWorkspace } from "@/components/VaaniWorkspace";

export default function VaaniPage() {
  return (
    <div className="pg">
      <div className="pg-intro">
        <p className="eyebrow">Vaani · WebMCP Challenge Day 1</p>
        <Ornament className="hero-ornament" />
        <h1 className="display display-md">Speak to the agentic web</h1>
        <p className="lede">
          Humans work in their language. Browser agents call structured WebMCP
          tools that mutate the same application state. Powered by Sarvam MCP
          underneath — not a second HTTP client.
        </p>
        <ApiStatus />
      </div>

      <div className="platform-card pg-card">
        <div className="platform-tabs">
          <span className="tab is-active">translate_content</span>
          <span className="tab">Shared state</span>
          <span className="tab">registerTool</span>
        </div>
        <div className="vaani-body">
          <VaaniWorkspace />
        </div>
      </div>

      <p className="footnote">
        Voice loop stays at <Link href="/playground">/playground</Link>. Desktop
        agents still use <Link href="/">uvx sarvam-mcp</Link>. More WebMCP
        tools (explain, summarize, speak, notes) come next — not all 14 MCP
        operations.
      </p>
    </div>
  );
}
