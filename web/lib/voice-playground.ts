export type PipelineStep = {
  name: string;
  status: string;
  latency_ms: number;
  detail?: string;
};

export type VoicePipelineResult = {
  ok: boolean;
  error?: string;
  transcript?: string;
  detected_language?: string | null;
  script_code?: string | null;
  reply_language?: string;
  reply_text?: string;
  audio_base64?: string | null;
  audio_mime_type?: string;
  steps?: PipelineStep[];
};

export function languageLabel(code: string | null | undefined): string {
  const labels: Record<string, string> = {
    "mr-IN": "Marathi",
    "hi-IN": "Hindi",
    "en-IN": "English",
    "ta-IN": "Tamil",
    "te-IN": "Telugu",
    "bn-IN": "Bengali",
    "gu-IN": "Gujarati",
    "kn-IN": "Kannada",
    "ml-IN": "Malayalam",
    "pa-IN": "Punjabi",
    "od-IN": "Odia",
  };
  if (!code) return "Unknown";
  return labels[code] ?? code;
}

export async function blobToPlayableUrl(
  base64: string,
  mimeType = "audio/wav",
): Promise<string> {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  const blob = new Blob([bytes], { type: mimeType });
  return URL.createObjectURL(blob);
}
