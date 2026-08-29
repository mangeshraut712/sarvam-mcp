import {
  coerceTtsLanguage,
  SarvamHttpError,
  sarvamPostJson,
  sarvamPostMultipart,
} from "@/lib/sarvam-rest";
import {
  DEMO_BANNER,
  demoExplain,
  demoSummary,
  demoTranscript,
  demoTranslate,
} from "@/lib/vaani-demo";

export type VaaniAction =
  | "translate_content"
  | "explain_content"
  | "summarize_content"
  | "speak_content"
  | "understand_audio";

export type VaaniResult = {
  ok: boolean;
  action?: VaaniAction | string;
  demo?: boolean;
  demo_banner?: string;
  text?: string;
  transcript?: string;
  detected_language?: string;
  source_language_code?: string;
  target_language_code?: string;
  audio_base64?: string;
  audio_mime_type?: string;
  latency_ms?: number;
  error?: string;
};

function demoEnabled(): boolean {
  return process.env.VAANI_DEMO !== "0";
}

function withDemo(result: Omit<VaaniResult, "ok" | "demo" | "demo_banner">): VaaniResult {
  return {
    ...result,
    ok: true,
    demo: true,
    demo_banner: DEMO_BANNER,
  };
}

async function lid(text: string): Promise<string> {
  const body = await sarvamPostJson<{ language_code?: string }>("/text-lid", {
    input: text,
  });
  const code = body.language_code;
  if (!code || code === "unknown" || code === "auto") return "en-IN";
  return code;
}

export async function runTranslate(input: {
  text: string;
  targetLanguage: string;
}): Promise<VaaniResult> {
  const t0 = Date.now();
  try {
    const src = await lid(input.text);
    const body = await sarvamPostJson<{ translated_text?: string }>(
      "/translate",
      {
        input: input.text,
        source_language_code: src,
        target_language_code: input.targetLanguage,
        model: "mayura:v1",
        mode: "formal",
        numerals_format: "international",
      },
    );
    return {
      ok: true,
      action: "translate_content",
      text: body.translated_text ?? "",
      source_language_code: src,
      target_language_code: input.targetLanguage,
      latency_ms: Date.now() - t0,
    };
  } catch (err) {
    if (err instanceof SarvamHttpError && err.status === 402 && demoEnabled()) {
      return withDemo({
        action: "translate_content",
        text: demoTranslate(input.targetLanguage),
        target_language_code: input.targetLanguage,
        source_language_code: "en-IN",
        latency_ms: Date.now() - t0,
      });
    }
    return fail(err, Date.now() - t0);
  }
}

async function runLlm(input: {
  action: "explain_content" | "summarize_content";
  text: string;
  language: string;
}): Promise<VaaniResult> {
  const t0 = Date.now();
  const mode =
    input.action === "explain_content"
      ? "Explain the content clearly in 2-4 sentences."
      : "Return a structured summary as three numbered points.";
  try {
    const body = await sarvamPostJson<{
      choices?: { message?: { content?: string } }[];
    }>("/v1/chat/completions", {
      model: "sarvam-105b",
      temperature: 0.3,
      max_tokens: 500,
      messages: [
        {
          role: "system",
          content: `You are Vaani. ${mode} Reply entirely in BCP-47 language ${input.language}.`,
        },
        { role: "user", content: input.text },
      ],
    });
    const text =
      body.choices?.[0]?.message?.content?.trim() ??
      (input.action === "explain_content"
        ? demoExplain(input.language)
        : demoSummary(input.language));
    return {
      ok: true,
      action: input.action,
      text,
      target_language_code: input.language,
      latency_ms: Date.now() - t0,
    };
  } catch (err) {
    if (err instanceof SarvamHttpError && err.status === 402 && demoEnabled()) {
      return withDemo({
        action: input.action,
        text:
          input.action === "explain_content"
            ? demoExplain(input.language)
            : demoSummary(input.language),
        target_language_code: input.language,
        latency_ms: Date.now() - t0,
      });
    }
    return fail(err, Date.now() - t0);
  }
}

export async function runExplain(input: {
  text: string;
  language: string;
}): Promise<VaaniResult> {
  return runLlm({ action: "explain_content", ...input });
}

export async function runSummarize(input: {
  text: string;
  language: string;
}): Promise<VaaniResult> {
  return runLlm({ action: "summarize_content", ...input });
}

export async function runSpeak(input: {
  text: string;
  language: string;
}): Promise<VaaniResult> {
  const t0 = Date.now();
  const lang = coerceTtsLanguage(input.language);
  try {
    const body = await sarvamPostJson<{ audios?: string[] }>(
      "/text-to-speech",
      {
        inputs: [input.text.slice(0, 1500)],
        target_language_code: lang,
        speaker: "priya",
        speech_sample_rate: 24000,
        model: "bulbul:v3",
        enable_preprocessing: true,
      },
    );
    const audio = body.audios?.[0];
    if (!audio) {
      return { ok: false, error: "TTS returned no audio.", latency_ms: Date.now() - t0 };
    }
    return {
      ok: true,
      action: "speak_content",
      text: input.text,
      target_language_code: lang,
      audio_base64: audio,
      audio_mime_type: "audio/wav",
      latency_ms: Date.now() - t0,
    };
  } catch (err) {
    if (err instanceof SarvamHttpError && err.status === 402 && demoEnabled()) {
      return withDemo({
        action: "speak_content",
        text: input.text,
        target_language_code: lang,
        latency_ms: Date.now() - t0,
        error: "Demo mode: live TTS needs credits. Text is ready to speak after billing.",
      });
    }
    return fail(err, Date.now() - t0);
  }
}

export async function runUnderstandAudio(
  bytes: Buffer,
  filename: string,
): Promise<VaaniResult> {
  const t0 = Date.now();
  try {
    const form = new FormData();
    const blob = new Blob([new Uint8Array(bytes)], {
      type: filename.endsWith(".wav") ? "audio/wav" : "audio/webm",
    });
    form.append("file", blob, filename);
    form.append("model", "saaras:v3");
    form.append("mode", "transcribe");
    form.append("language_code", "unknown");
    const stt = await sarvamPostMultipart<{
      transcript?: string;
      language_code?: string;
    }>("/speech-to-text", form);
    const transcript = stt.transcript ?? "";
    let language = stt.language_code;
    if (transcript) {
      try {
        language = await lid(transcript);
      } catch {
        /* keep STT language */
      }
    }
    return {
      ok: true,
      action: "understand_audio",
      transcript,
      detected_language: language,
      text: transcript,
      latency_ms: Date.now() - t0,
    };
  } catch (err) {
    if (err instanceof SarvamHttpError && err.status === 402 && demoEnabled()) {
      const demo = demoTranscript();
      return withDemo({
        action: "understand_audio",
        transcript: demo.transcript,
        detected_language: demo.language,
        text: demo.transcript,
        latency_ms: Date.now() - t0,
      });
    }
    return fail(err, Date.now() - t0);
  }
}

function fail(err: unknown, latency_ms: number): VaaniResult {
  const message = err instanceof Error ? err.message : "Vaani action failed.";
  return { ok: false, error: message, latency_ms };
}
