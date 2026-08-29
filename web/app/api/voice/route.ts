import { NextResponse } from "next/server";

import { runVoicePipeline } from "@/lib/voice-pipeline-server";

export const runtime = "nodejs";
export const maxDuration = 120;

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const audio = formData.get("audio");

    if (!(audio instanceof File)) {
      return NextResponse.json({ ok: false, error: "Missing audio file." }, { status: 400 });
    }

    if (audio.size === 0) {
      return NextResponse.json({ ok: false, error: "Audio file is empty." }, { status: 400 });
    }

    const buffer = Buffer.from(await audio.arrayBuffer());
    const filename = audio.name || "recording.webm";
    const result = await runVoicePipeline(buffer, filename);

    if (!result.ok) {
      return NextResponse.json(result, { status: 422 });
    }

    return NextResponse.json(result);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Voice pipeline failed.";
    return NextResponse.json({ ok: false, error: message, steps: [] }, { status: 500 });
  }
}
