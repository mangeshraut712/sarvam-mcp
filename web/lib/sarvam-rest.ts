const BASE = process.env.SARVAM_API_BASE_URL ?? "https://api.sarvam.ai";

export class SarvamHttpError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

function apiKey(): string {
  const key = process.env.SARVAM_API_KEY;
  if (!key) {
    throw new SarvamHttpError("SARVAM_API_KEY is not set.", 503);
  }
  return key;
}

function errorMessage(status: number, body: unknown): string {
  if (status === 402) {
    return "No credits available. Add credits at https://dashboard.sarvam.ai → Billing.";
  }
  if (typeof body === "object" && body && "error" in body) {
    const err = (body as { error?: { message?: string } | string }).error;
    if (typeof err === "string") return err;
    if (err && typeof err.message === "string") return err.message;
  }
  if (typeof body === "object" && body && "message" in body) {
    const msg = (body as { message?: string }).message;
    if (msg) return msg;
  }
  return `Sarvam HTTP ${status}`;
}

export async function sarvamPostJson<T>(
  path: string,
  jsonBody: Record<string, unknown>,
): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: {
      "api-subscription-key": apiKey(),
      "content-type": "application/json",
      "user-agent": "vaani-webmcp",
    },
    body: JSON.stringify(jsonBody),
  });
  const body = (await response.json().catch(() => ({}))) as T;
  if (!response.ok) {
    throw new SarvamHttpError(errorMessage(response.status, body), response.status);
  }
  return body;
}

export async function sarvamPostMultipart<T>(
  path: string,
  form: FormData,
): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: {
      "api-subscription-key": apiKey(),
      "user-agent": "vaani-webmcp",
    },
    body: form,
  });
  const body = (await response.json().catch(() => ({}))) as T;
  if (!response.ok) {
    throw new SarvamHttpError(errorMessage(response.status, body), response.status);
  }
  return body;
}

export const TTS_LANGS = new Set([
  "en-IN",
  "hi-IN",
  "bn-IN",
  "ta-IN",
  "te-IN",
  "gu-IN",
  "kn-IN",
  "ml-IN",
  "mr-IN",
  "pa-IN",
  "od-IN",
]);

export function coerceTtsLanguage(code: string | undefined): string {
  if (code && TTS_LANGS.has(code)) return code;
  return "hi-IN";
}
