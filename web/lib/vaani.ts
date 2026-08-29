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

export type TranslateClientResult = {
  ok: boolean;
  translated_text?: string;
  source_language_code?: string;
  target_language_code?: string;
  latency_ms?: number;
  error?: string;
};

export async function translateViaApp(input: {
  text: string;
  targetLanguage: string;
  sourceLanguage?: string;
}): Promise<TranslateClientResult> {
  const response = await fetch("/api/translate", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(input),
  });
  return (await response.json()) as TranslateClientResult;
}
