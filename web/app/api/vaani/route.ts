import { NextResponse } from "next/server";

import {
  runExplain,
  runSpeak,
  runSummarize,
  runTranslate,
} from "@/lib/vaani-actions";

export const runtime = "nodejs";
export const maxDuration = 60;

type Body = {
  action?: string;
  text?: string;
  targetLanguage?: string;
  language?: string;
};

export async function POST(request: Request) {
  let body: Body;
  try {
    body = (await request.json()) as Body;
  } catch {
    return NextResponse.json(
      { ok: false, error: "JSON body required." },
      { status: 400 },
    );
  }

  const text = typeof body.text === "string" ? body.text.trim() : "";
  const language =
    (typeof body.language === "string" && body.language) ||
    (typeof body.targetLanguage === "string" && body.targetLanguage) ||
    "mr-IN";

  if (body.action !== "speak_content" && !text) {
    return NextResponse.json({ ok: false, error: "text is required." }, { status: 400 });
  }

  try {
    switch (body.action) {
      case "translate_content":
        return NextResponse.json(
          await runTranslate({ text, targetLanguage: language }),
        );
      case "explain_content":
        return NextResponse.json(await runExplain({ text, language }));
      case "summarize_content":
        return NextResponse.json(await runSummarize({ text, language }));
      case "speak_content":
        if (!text) {
          return NextResponse.json(
            { ok: false, error: "text is required." },
            { status: 400 },
          );
        }
        return NextResponse.json(await runSpeak({ text, language }));
      default:
        return NextResponse.json(
          {
            ok: false,
            error:
              "Unknown action. Use translate_content, explain_content, summarize_content, or speak_content.",
          },
          { status: 400 },
        );
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : "Vaani failed.";
    return NextResponse.json({ ok: false, error: message }, { status: 500 });
  }
}
