import { NextResponse } from "next/server";

import { runTranslate } from "@/lib/translate-server";

export const runtime = "nodejs";
export const maxDuration = 60;

export async function POST(request: Request) {
  let body: {
    text?: unknown;
    targetLanguage?: unknown;
    sourceLanguage?: unknown;
  };
  try {
    body = (await request.json()) as typeof body;
  } catch {
    return NextResponse.json(
      { ok: false, error: "JSON body required: { text, targetLanguage }." },
      { status: 400 },
    );
  }

  const text = typeof body.text === "string" ? body.text : "";
  const targetLanguage =
    typeof body.targetLanguage === "string" ? body.targetLanguage : "";
  const sourceLanguage =
    typeof body.sourceLanguage === "string" ? body.sourceLanguage : undefined;

  if (!text.trim()) {
    return NextResponse.json({ ok: false, error: "text is required." }, { status: 400 });
  }
  if (!targetLanguage.trim()) {
    return NextResponse.json(
      { ok: false, error: "targetLanguage is required (e.g. mr-IN)." },
      { status: 400 },
    );
  }

  try {
    const result = await runTranslate({ text, targetLanguage, sourceLanguage });
    if (!result.ok) {
      return NextResponse.json(result, { status: 422 });
    }
    return NextResponse.json(result);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Translate failed.";
    return NextResponse.json({ ok: false, error: message }, { status: 500 });
  }
}
