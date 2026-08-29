import { spawn } from "child_process";
import { mkdtemp, unlink, writeFile } from "fs/promises";
import { tmpdir } from "os";
import path from "path";

import type { VoicePipelineResult } from "./voice-playground";

function repoRoot(): string {
  return path.resolve(process.cwd(), "..");
}

function pythonBin(): string {
  if (process.env.PYTHON_PATH) {
    return process.env.PYTHON_PATH;
  }
  return path.join(repoRoot(), ".venv", "bin", "python");
}

export async function runVoicePipeline(
  audioBytes: Buffer,
  filename: string,
): Promise<VoicePipelineResult> {
  const ext = path.extname(filename) || ".webm";
  const dir = await mkdtemp(path.join(tmpdir(), "sarvam-voice-"));
  const audioPath = path.join(dir, `recording${ext}`);

  try {
    await writeFile(audioPath, audioBytes);

    const stdout = await new Promise<string>((resolve, reject) => {
      const child = spawn(
        pythonBin(),
        ["-m", "sarvam_mcp.playground", "--audio-path", audioPath],
        {
          cwd: repoRoot(),
          env: process.env,
        },
      );

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
          reject(new Error(err.trim() || `Pipeline exited with code ${code}`));
          return;
        }
        resolve(out);
      });
    });

    const lastLine = stdout.trim().split("\n").pop() ?? "{}";
    return JSON.parse(lastLine) as VoicePipelineResult;
  } finally {
    await unlink(audioPath).catch(() => undefined);
  }
}
