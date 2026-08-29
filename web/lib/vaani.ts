import type { VaaniResult } from "@/lib/vaani-actions";

export const VAANI_LANGUAGES = [
  { code: "mr-IN", label: "Marathi" },
  { code: "hi-IN", label: "Hindi" },
  { code: "ta-IN", label: "Tamil" },
  { code: "te-IN", label: "Telugu" },
  { code: "bn-IN", label: "Bengali" },
  { code: "kn-IN", label: "Kannada" },
  { code: "ml-IN", label: "Malayalam" },
  { code: "gu-IN", label: "Gujarati" },
  { code: "pa-IN", label: "Punjabi" },
  { code: "en-IN", label: "English (India)" },
] as const;

export async function callVaani(input: {
  action: string;
  text: string;
  language: string;
}): Promise<VaaniResult> {
  const response = await fetch("/api/vaani", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      action: input.action,
      text: input.text,
      language: input.language,
      targetLanguage: input.language,
    }),
  });
  return (await response.json()) as VaaniResult;
}

export async function understandAudio(blob: Blob): Promise<VaaniResult> {
  const form = new FormData();
  form.append("audio", blob, "recording.webm");
  const response = await fetch("/api/vaani/audio", { method: "POST", body: form });
  return (await response.json()) as VaaniResult;
}
