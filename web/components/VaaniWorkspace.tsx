"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { translateViaApp, VAANI_LANGUAGES } from "@/lib/vaani";
import { getModelContext } from "@/lib/webmcp";

const SAMPLE = `The agentic web should not assume everyone types English.
Humans should speak in their language. Browser agents should call
structured tools that update the same page the human sees.`;

type WebmcpStatus = "checking" | "registered" | "unavailable" | "error";

export function VaaniWorkspace() {
  const [sourceText, setSourceText] = useState(SAMPLE);
  const [targetLanguage, setTargetLanguage] = useState("mr-IN");
  const [translatedText, setTranslatedText] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastActor, setLastActor] = useState<"human" | "agent" | null>(null);
  const [webmcpStatus, setWebmcpStatus] = useState<WebmcpStatus>("checking");
  const [webmcpDetail, setWebmcpDetail] = useState(
    "Looking for document.modelContext…",
  );

  const sourceRef = useRef(sourceText);
  const targetRef = useRef(targetLanguage);
  sourceRef.current = sourceText;
  targetRef.current = targetLanguage;

  const applyTranslation = useCallback(
    async (text: string, language: string, actor: "human" | "agent") => {
      setBusy(true);
      setError(null);
      try {
        const result = await translateViaApp({
          text,
          targetLanguage: language,
        });
        if (!result.ok) {
          setError(result.error ?? "Translation failed.");
          return result;
        }
        setTranslatedText(result.translated_text ?? "");
        setLastActor(actor);
        return result;
      } catch (err) {
        const message = err instanceof Error ? err.message : "Request failed.";
        setError(message);
        return { ok: false, error: message };
      } finally {
        setBusy(false);
      }
    },
    [],
  );

  useEffect(() => {
    const ctx = getModelContext();
    if (!ctx) {
      setWebmcpStatus("unavailable");
      setWebmcpDetail(
        "This browser has no document.modelContext. Humans can still translate; ChatGPT’s in-app browser or Chrome with WebMCP will discover the tool.",
      );
      return;
    }

    const controller = new AbortController();
    let cancelled = false;

    void (async () => {
      try {
        await ctx.registerTool(
          {
            name: "translate_content",
            title: "Translate content",
            description:
              "Translate the visible Vaani workspace text (or supplied text) into an Indian language. Updates the same translation panel the human sees.",
            inputSchema: {
              type: "object",
              properties: {
                text: {
                  type: "string",
                  description:
                    "Text to translate. Omit to use the source currently shown in the page.",
                },
                targetLanguage: {
                  type: "string",
                  description:
                    "BCP-47 target such as mr-IN, hi-IN, ta-IN, or en-IN.",
                },
              },
              required: ["targetLanguage"],
            },
            annotations: {
              readOnlyHint: false,
              untrustedContentHint: false,
            },
            execute: async (input) => {
              const language =
                typeof input.targetLanguage === "string"
                  ? input.targetLanguage
                  : targetRef.current;
              const supplied =
                typeof input.text === "string" ? input.text.trim() : "";
              const text = supplied || sourceRef.current;
              const result = await applyTranslation(text, language, "agent");
              return JSON.stringify(result);
            },
          },
          { signal: controller.signal },
        );
        if (!cancelled) {
          setWebmcpStatus("registered");
          setWebmcpDetail(
            "Registered translate_content via document.modelContext.registerTool. Unregister uses AbortSignal, not unregisterTool().",
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
  }, [applyTranslation]);

  const onHumanTranslate = () => {
    void applyTranslation(sourceText, targetLanguage, "human");
  };

  const onSimulateAgent = () => {
    void applyTranslation(sourceText, targetLanguage, "agent");
  };

  return (
    <div className="vaani">
      <p className={`webmcp-pill is-${webmcpStatus}`}>
        {webmcpStatus === "registered"
          ? "WebMCP ready"
          : webmcpStatus === "unavailable"
            ? "WebMCP not in this browser"
            : webmcpStatus === "error"
              ? "WebMCP error"
              : "Checking WebMCP"}
      </p>
      <p className="vaani-spec">{webmcpDetail}</p>

      <div className="vaani-grid">
        <label className="vaani-pane">
          <span className="label">Source (human + agent share this)</span>
          <textarea
            value={sourceText}
            onChange={(e) => setSourceText(e.target.value)}
            rows={10}
          />
        </label>
        <div className="vaani-pane">
          <span className="label">Translation (same state the agent writes)</span>
          <div className="vaani-result" aria-live="polite">
            {translatedText || (
              <span className="pg-empty">
                Result appears here after you or a browser agent runs
                translate_content.
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="vaani-controls">
        <label>
          Target language
          <select
            value={targetLanguage}
            onChange={(e) => setTargetLanguage(e.target.value)}
          >
            {VAANI_LANGUAGES.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.label} ({lang.code})
              </option>
            ))}
          </select>
        </label>
        <button
          type="button"
          className="btn btn-solid"
          onClick={onHumanTranslate}
          disabled={busy}
        >
          {busy ? "Translating…" : "Translate (human)"}
        </button>
        <button
          type="button"
          className="btn btn-ghost"
          onClick={onSimulateAgent}
          disabled={busy}
        >
          Simulate agent call
        </button>
      </div>

      {lastActor && (
        <p className="vaani-actor">
          Last write: <strong>{lastActor}</strong> — both update this panel.
        </p>
      )}
      {error && <p className="error">{error}</p>}
    </div>
  );
}
