import { NextResponse } from "next/server";

import { runUnderstandAudio } from "@/lib/vaani-actions";

export const runtime = "nodejs";
export const maxDuration = 60;

export async function POST(request: Request) {
  let formData: FormData;
  try {
    formData = await request.formData();
  } catch {
    return NextResponse.json(
      { ok: false, error: "Send audio as multipart field \"audio\"." },
      { status: 400 },
    );
  }

  const audio = formData.get("audio");
  if (!(audio instanceof File)) {
    return NextResponse.json({ ok: false, error: "Missing audio file." }, { status: 400 });
  }
  if (audio.size === 0) {
    return NextResponse.json({ ok: false, error: "Audio file is empty." }, { status: 400 });
  }

  try {
    const buffer = Buffer.from(await audio.arrayBuffer());
    const result = await runUnderstandAudio(buffer, audio.name || "recording.webm");
    return NextResponse.json(result, { status: result.ok ? 200 : 422 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "understand_audio failed.";
    return NextResponse.json({ ok: false, error: message }, { status: 500 });
  }
}
