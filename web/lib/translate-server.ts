import { spawn } from "child_process";
import path from "path";

export type TranslateResult = {
  ok: boolean;
  translated_text?: string;
  source_language_code?: string;
  target_language_code?: string;
  latency_ms?: number;
  error?: string;
};

function repoRoot(): string {
  return path.resolve(process.cwd(), "..");
}

function pythonBin(): string {
  if (process.env.PYTHON_PATH) {
    return process.env.PYTHON_PATH;
  }
  return path.join(repoRoot(), ".venv", "bin", "python");
}

export async function runTranslate(input: {
  text: string;
  targetLanguage: string;
  sourceLanguage?: string;
}): Promise<TranslateResult> {
  const args = [
    "-m",
    "sarvam_mcp.playground",
    "translate",
    "--text",
    input.text,
    "--target-language",
    input.targetLanguage,
  ];
  if (input.sourceLanguage) {
    args.push("--source-language", input.sourceLanguage);
  }

  const stdout = await new Promise<string>((resolve, reject) => {
    const child = spawn(pythonBin(), args, {
      cwd: repoRoot(),
      env: process.env,
    });

    let out = "";
    let err = "";

    child.stdout.on("data", (chunk: Buffer) => {
      out += chunk.toString();
    });
    child.stderr.on("data", (chunk: Buffer) => {
      err += chunk.toString();
    });
    child.on("error", reject);
    child.on("close", (code) => {
      if (code !== 0 && !out.trim()) {
        reject(new Error(err.trim() || `Translate exited with code ${code}`));
        return;
      }
      resolve(out);
    });
  });

  const lastLine = stdout.trim().split("\n").pop() ?? "{}";
  return JSON.parse(lastLine) as TranslateResult;
}
