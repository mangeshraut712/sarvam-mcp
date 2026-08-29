import { NextResponse } from "next/server";

import { runTranslate } from "@/lib/vaani-actions";

export const runtime = "nodejs";
export const maxDuration = 60;

export async function POST(request: Request) {
  let body: { text?: unknown; targetLanguage?: unknown };
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

  if (!text.trim() || !targetLanguage.trim()) {
    return NextResponse.json(
      { ok: false, error: "text and targetLanguage are required." },
      { status: 400 },
    );
  }

  const result = await runTranslate({ text, targetLanguage });
  return NextResponse.json(result, { status: result.ok ? 200 : 422 });
}
