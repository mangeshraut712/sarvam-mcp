// Server route — calls Sarvam's /translate so the API key never reaches the browser.
import { NextResponse } from "next/server";

export const runtime = "nodejs";

interface Body {
  text: string;
  source: string;
  target: string;
  mode?: "formal" | "modern-colloquial" | "classic-colloquial" | "code-mixed";
}

export async function POST(req: Request) {
  const body = (await req.json()) as Body;
  const { text, source, target, mode = "modern-colloquial" } = body;

  if (!text?.trim()) {
    return NextResponse.json({ error: "text is required" }, { status: 400 });
  }

  const apiKey = process.env.SARVAM_API_KEY;
  if (!apiKey) {
    return NextResponse.json(
      { error: "Server is missing SARVAM_API_KEY. See .env.example." },
      { status: 500 },
    );
  }

  const upstream = await fetch("https://api.sarvam.ai/translate", {
    method: "POST",
    headers: {
      "api-subscription-key": apiKey,
      "content-type": "application/json",
    },
    body: JSON.stringify({
      input: text,
      source_language_code: source || "en-IN",
      target_language_code: target,
      model: "mayura:v1",
      mode,
      numerals_format: "international",
      enable_preprocessing: true,
    }),
  });

  if (!upstream.ok) {
    const detail = await upstream.text();
    return NextResponse.json(
      { error: `Sarvam returned ${upstream.status}`, detail },
      { status: upstream.status },
    );
  }
  const data = (await upstream.json()) as { translated_text: string; request_id?: string };
  return NextResponse.json({
    translated: data.translated_text,
    request_id: data.request_id,
  });
}
