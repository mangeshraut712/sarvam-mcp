import { NextResponse } from "next/server";

export const runtime = "nodejs";

/**
 * Unmetered Sarvam catalog check. Inference APIs (STT/TTS/LLM/translate)
 * consume credits; GET /v1/models does not and returns 200 with a valid key.
 */
export async function GET() {
  const key = process.env.SARVAM_API_KEY;
  if (!key) {
    return NextResponse.json(
      { ok: false, error: "SARVAM_API_KEY is not set in this process." },
      { status: 503 },
    );
  }

  const response = await fetch("https://api.sarvam.ai/v1/models", {
    headers: {
      "api-subscription-key": key,
      "user-agent": "sarvam-mcp-web",
    },
    cache: "no-store",
  });

  const body = (await response.json()) as {
    data?: { id: string }[];
    error?: unknown;
  };

  if (!response.ok) {
    return NextResponse.json(
      { ok: false, status: response.status, error: body },
      { status: response.status === 402 ? 503 : response.status },
    );
  }

  const models = (body.data ?? []).map((item) => item.id);
  return NextResponse.json({
    ok: true,
    status: 200,
    models,
    chat_default: models.includes("sarvam-105b")
      ? "sarvam-105b"
      : models[0] ?? null,
  });
}
