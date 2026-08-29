"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { callVaani, understandAudio, VAANI_LANGUAGES } from "@/lib/vaani";
import type { VaaniResult } from "@/lib/vaani-actions";
import type { ModelContextTool } from "@/lib/webmcp";
import { getModelContext } from "@/lib/webmcp";

const SAMPLE = `The agentic web should not assume everyone types English.
Humans should speak in their language. Browser agents should call
structured tools that update the same page the human sees.`;

type WebmcpStatus = "checking" | "registered" | "unavailable" | "error";
type Note = { id: string; language: string; body: string };

function asString(value: unknown): string {
  return typeof value === "string" ? value : "";
}

export function VaaniWorkspace() {
  const [sourceText, setSourceText] = useState(SAMPLE);
  const [resultText, setResultText] = useState("");
  const [language, setLanguage] = useState("mr-IN");
  const [notes, setNotes] = useState<Note[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [demoBanner, setDemoBanner] = useState<string | null>(null);
  const [lastActor, setLastActor] = useState<"human" | "agent" | null>(null);
  const [lastTool, setLastTool] = useState<string | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [webmcpStatus, setWebmcpStatus] = useState<WebmcpStatus>("checking");
  const [webmcpDetail, setWebmcpDetail] = useState(
    "Looking for document.modelContext…",
  );
  const [phase, setPhase] = useState<"idle" | "recording">("idle");

  const sourceRef = useRef(sourceText);
  const resultRef = useRef(resultText);
  const languageRef = useRef(language);
  sourceRef.current = sourceText;
  resultRef.current = resultText;
  languageRef.current = language;

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);

  const applyResult = useCallback(
    (result: VaaniResult, actor: "human" | "agent", tool: string) => {
      if (result.demo && result.demo_banner) setDemoBanner(result.demo_banner);
      if (!result.ok && result.error) {
        setError(result.error);
        return result;
      }
      setError(null);
      const next =
        result.text ||
        result.transcript ||
        resultRef.current;
      if (result.transcript) setSourceText(result.transcript);
      if (next) setResultText(next);
      if (result.audio_base64) {
        const url = `data:${result.audio_mime_type ?? "audio/wav"};base64,${result.audio_base64}`;
        setAudioUrl(url);
      }
      setLastActor(actor);
      setLastTool(tool);
      return result;
    },
    [],
  );

  const runAction = useCallback(
    async (
      action: string,
      actor: "human" | "agent",
      overrides?: { text?: string; language?: string },
    ) => {
      setBusy(true);
      setError(null);
      try {
        const text = overrides?.text?.trim() || sourceRef.current;
        const lang = overrides?.language || languageRef.current;
        const result = await callVaani({ action, text, language: lang });
        applyResult(result, actor, action);
        return result;
      } catch (err) {
        const message = err instanceof Error ? err.message : "Request failed.";
        setError(message);
        return { ok: false, error: message } satisfies VaaniResult;
      } finally {
        setBusy(false);
      }
    },
    [applyResult],
  );

  useEffect(() => {
    const ctx = getModelContext();
    if (!ctx) {
      setWebmcpStatus("unavailable");
      setWebmcpDetail(
        "No document.modelContext here. ChatGPT’s in-app browser or Chrome 149+ with chrome://flags/#enable-webmcp-testing will discover the six tools below.",
      );
      return;
    }

    const controller = new AbortController();
    let cancelled = false;

    const tools: ModelContextTool[] = [
      {
        name: "understand_audio",
        title: "Understand audio",
        description:
          "Transcribe the latest human recording on this Vaani page and detect language. Updates the shared source panel.",
        inputSchema: { type: "object" as const, properties: {} },
        execute: async () =>
          JSON.stringify({
            ok: false,
            error:
              "Ask the human to hold Speak on this page, or call after a recording. Browser agents cannot attach mic buffers in this demo.",
          }),
      },
      {
        name: "translate_content",
        title: "Translate content",
        description:
          "Translate workspace source (or supplied text) into an Indian language. Writes the shared result panel.",
        inputSchema: {
          type: "object" as const,
          properties: {
            text: { type: "string" },
            targetLanguage: { type: "string" },
          },
          required: ["targetLanguage"],
        },
        execute: async (input: Record<string, unknown>) => {
          const result = await runAction("translate_content", "agent", {
            text: asString(input.text),
            language: asString(input.targetLanguage) || languageRef.current,
          });
          return JSON.stringify(result);
        },
      },
      {
        name: "explain_content",
        title: "Explain content",
        description:
          "Explain the visible source (or supplied text) in the requested language. Updates the shared result panel.",
        inputSchema: {
          type: "object" as const,
          properties: {
            text: { type: "string" },
            language: { type: "string" },
          },
        },
        execute: async (input: Record<string, unknown>) => {
          const result = await runAction("explain_content", "agent", {
            text: asString(input.text),
            language: asString(input.language) || languageRef.current,
          });
          return JSON.stringify(result);
        },
      },
      {
        name: "summarize_content",
        title: "Summarize content",
        description:
          "Summarize workspace content into three points in the requested language.",
        inputSchema: {
          type: "object" as const,
          properties: {
            text: { type: "string" },
            language: { type: "string" },
          },
        },
        execute: async (input: Record<string, unknown>) => {
          const result = await runAction("summarize_content", "agent", {
            text: asString(input.text),
            language: asString(input.language) || languageRef.current,
          });
          return JSON.stringify(result);
        },
      },
      {
        name: "speak_content",
        title: "Speak content",
        description:
          "Speak the result panel (or supplied text) in the requested language via Sarvam TTS. Updates playback on the page.",
        inputSchema: {
          type: "object" as const,
          properties: {
            text: { type: "string" },
            language: { type: "string" },
          },
        },
        execute: async (input: Record<string, unknown>) => {
          const result = await runAction("speak_content", "agent", {
            text: asString(input.text) || resultRef.current || sourceRef.current,
            language: asString(input.language) || languageRef.current,
          });
          return JSON.stringify(result);
        },
      },
      {
        name: "create_multilingual_note",
        title: "Create multilingual note",
        description:
          "Pin the current result (or supplied text) as a visible note in the Vaani workspace the human can see.",
        inputSchema: {
          type: "object" as const,
          properties: {
            text: { type: "string" },
            language: { type: "string" },
          },
        },
        execute: async (input: Record<string, unknown>) => {
          const body =
            asString(input.text) || resultRef.current || sourceRef.current;
          const lang = asString(input.language) || languageRef.current;
          const note = {
            id: `${Date.now()}`,
            language: lang,
            body,
          };
          setNotes((prev) => [note, ...prev]);
          setLastActor("agent");
          setLastTool("create_multilingual_note");
          return JSON.stringify({ ok: true, note });
        },
      },
    ];

    void (async () => {
      try {
        for (const tool of tools) {
          await ctx.registerTool(tool, { signal: controller.signal });
        }
        if (!cancelled) {
          setWebmcpStatus("registered");
          setWebmcpDetail(
            "Registered 6 tools with document.modelContext.registerTool. Lifecycle uses AbortSignal (not unregisterTool).",
          );
        }
      } catch (err) {
        if (!cancelled) {
          setWebmcpStatus("error");
          setWebmcpDetail(
            err instanceof Error ? err.message : "registerTool failed.",
          );
        }
      }
    })();

    return () => {
      cancelled = true;
      controller.abort();
    };
  }, [runAction]);

  const pinNote = (actor: "human" | "agent") => {
    const body = resultText || sourceText;
    setNotes((prev) => [
      { id: `${Date.now()}`, language, body },
      ...prev,
    ]);
    setLastActor(actor);
    setLastTool("create_multilingual_note");
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      chunksRef.current = [];
      const recorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported("audio/webm")
          ? "audio/webm"
          : "audio/mp4",
      });
      mediaRecorderRef.current = recorder;
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };
      recorder.onstop = () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType });
        setPhase("idle");
        if (blob.size === 0) {
          setError("No audio captured.");
          return;
        }
        setBusy(true);
        void understandAudio(blob)
          .then((result) => applyResult(result, "human", "understand_audio"))
          .finally(() => setBusy(false));
      };
      recorder.start();
      setPhase("recording");
    } catch {
      setError("Microphone access denied or unavailable.");
    }
  };

  const stopRecording = () => {
    const recorder = mediaRecorderRef.current;
    if (recorder && recorder.state !== "inactive") recorder.stop();
  };

  return (
    <div className="vaani">
      <p className={`webmcp-pill is-${webmcpStatus}`}>
        {webmcpStatus === "registered"
          ? "WebMCP ready · 6 tools"
          : webmcpStatus === "unavailable"
            ? "WebMCP not in this browser"
            : webmcpStatus === "error"
              ? "WebMCP error"
              : "Checking WebMCP"}
      </p>
      <p className="vaani-spec">{webmcpDetail}</p>
      {demoBanner && <p className="vaani-demo">{demoBanner}</p>}

      <div className="vaani-grid">
        <label className="vaani-pane">
          <span className="label">Shared source</span>
          <textarea
            value={sourceText}
            onChange={(e) => setSourceText(e.target.value)}
            rows={10}
          />
        </label>
        <div className="vaani-pane">
          <span className="label">Shared result (human + agent)</span>
          <div className="vaani-result" aria-live="polite">
            {resultText || (
              <span className="pg-empty">
                translate / explain / summarize / speak write here.
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="vaani-controls">
        <label>
          Language
          <select value={language} onChange={(e) => setLanguage(e.target.value)}>
            {VAANI_LANGUAGES.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.label} ({lang.code})
              </option>
            ))}
          </select>
        </label>
        <button
          type="button"
          className={`btn btn-solid ${phase === "recording" ? "is-live" : ""}`}
          onPointerDown={(e) => {
            e.preventDefault();
            void startRecording();
          }}
          onPointerUp={(e) => {
            e.preventDefault();
            stopRecording();
          }}
          disabled={busy}
        >
          {phase === "recording" ? "Release" : "Hold to speak"}
        </button>
        <button
          type="button"
          className="btn btn-solid"
          disabled={busy}
          onClick={() => void runAction("translate_content", "human")}
        >
          Translate
        </button>
        <button
          type="button"
          className="btn btn-ghost"
          disabled={busy}
          onClick={() => void runAction("explain_content", "human")}
        >
          Explain
        </button>
        <button
          type="button"
          className="btn btn-ghost"
          disabled={busy}
          onClick={() => void runAction("summarize_content", "human")}
        >
          Summarize
        </button>
        <button
          type="button"
          className="btn btn-ghost"
          disabled={busy}
          onClick={() =>
            void runAction("speak_content", "human", {
              text: resultText || sourceText,
            })
          }
        >
          Speak
        </button>
        <button
          type="button"
          className="btn btn-ghost"
          disabled={busy}
          onClick={() => pinNote("human")}
        >
          Pin note
        </button>
        <button
          type="button"
          className="btn btn-ghost"
          disabled={busy}
          onClick={() => void runAction("summarize_content", "agent")}
        >
          Simulate agent
        </button>
      </div>

      {audioUrl && (
        <audio controls src={audioUrl} className="vaani-audio">
          Playback
        </audio>
      )}

      {lastActor && (
        <p className="vaani-actor">
          Last write: <strong>{lastActor}</strong>
          {lastTool ? ` · ${lastTool}` : ""}
        </p>
      )}
      {error && <p className="error">{error}</p>}

      {notes.length > 0 && (
        <section className="vaani-notes">
          <h2 className="label">Notes (visible artifacts)</h2>
          <ul>
            {notes.map((note) => (
              <li key={note.id}>
                <span className="vaani-note-lang">{note.language}</span>
                {note.body}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
