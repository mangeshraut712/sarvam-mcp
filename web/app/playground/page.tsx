"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Image from "next/image";
import Link from "next/link";

import {
  blobToPlayableUrl,
  languageLabel,
  type PipelineStep,
  type VoicePipelineResult,
} from "@/lib/voice-playground";

type Phase = "idle" | "recording" | "processing" | "done" | "error";

export default function PlaygroundPage() {
  const [phase, setPhase] = useState<Phase>("idle");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<VoicePipelineResult | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const cleanupStream = useCallback(() => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
  }, []);

  useEffect(() => {
    return () => {
      cleanupStream();
      if (audioUrl) URL.revokeObjectURL(audioUrl);
    };
  }, [audioUrl, cleanupStream]);

  const submitAudio = useCallback(async (blob: Blob) => {
    setPhase("processing");
    setError(null);
    setResult(null);
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
      setAudioUrl(null);
    }

    const formData = new FormData();
    formData.append("audio", blob, "recording.webm");

    try {
      const response = await fetch("/api/voice", {
        method: "POST",
        body: formData,
      });
      const data = (await response.json()) as VoicePipelineResult;

      if (!response.ok || !data.ok) {
        setPhase("error");
        setError(data.error ?? "Voice pipeline failed.");
        setResult(data);
        return;
      }

      setResult(data);
      if (data.audio_base64) {
        const url = await blobToPlayableUrl(
          data.audio_base64,
          data.audio_mime_type ?? "audio/wav",
        );
        setAudioUrl(url);
      }
      setPhase("done");
    } catch (err) {
      setPhase("error");
      setError(err instanceof Error ? err.message : "Request failed.");
    }
  }, [audioUrl]);

  const startRecording = useCallback(async () => {
    if (phase === "recording" || phase === "processing") return;

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
        cleanupStream();
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType });
        if (blob.size > 0) {
          void submitAudio(blob);
        } else {
          setPhase("error");
          setError("No audio captured. Hold the button while speaking.");
        }
      };

      recorder.start();
      setPhase("recording");
      setError(null);
    } catch {
      setPhase("error");
      setError("Microphone access denied or unavailable.");
    }
  }, [cleanupStream, phase, submitAudio]);

  const stopRecording = useCallback(() => {
    const recorder = mediaRecorderRef.current;
    if (recorder && recorder.state !== "inactive") {
      recorder.stop();
    }
  }, []);

  const playResponse = useCallback(() => {
    if (audioRef.current) {
      void audioRef.current.play();
    }
  }, []);

  const detected = result?.detected_language ?? null;
  const steps: PipelineStep[] = result?.steps ?? [];

  return (
    <div className="playground">
      <div className="playground-card">
        <div className="playground-header">
          <Image
            src="/sarvam-logo.png"
            alt="Sarvam"
            width={100}
            height={28}
            className="logo"
            priority
          />
          <Link href="/" className="back-link">
            ← MCP setup
          </Link>
        </div>

        <h1>Sarvam Voice Agent</h1>
        <p className="subtitle">Speak naturally in an Indian language.</p>

        <button
          type="button"
          className={`record-btn ${phase === "recording" ? "recording" : ""}`}
          onPointerDown={(e) => {
            e.preventDefault();
            void startRecording();
          }}
          onPointerUp={(e) => {
            e.preventDefault();
            stopRecording();
          }}
          onPointerLeave={() => {
            if (phase === "recording") stopRecording();
          }}
          disabled={phase === "processing"}
        >
          {phase === "processing"
            ? "Processing…"
            : phase === "recording"
              ? "🎙 Release to send"
              : "🎙 Hold to Speak"}
        </button>

        {phase === "processing" && <p className="status">Running STT → Lang ID → LLM → TTS…</p>}
        {error && <p className="error">{error}</p>}

        {detected && (
          <div className="section">
            <div className="label">Detected</div>
            <div className="value">{languageLabel(detected)}</div>
          </div>
        )}

        {result?.transcript && (
          <div className="section">
            <div className="label">You said</div>
            <div className="transcript">{result.transcript}</div>
          </div>
        )}

        {steps.length > 0 && (
          <div className="section">
            <div className="label">Tool flow</div>
            <ul className="timeline">
              {steps.map((step) => (
                <li key={step.name} className={`timeline-item ${step.status}`}>
                  <span className="timeline-check">
                    {step.status === "ok" ? "✓" : "✗"}
                  </span>
                  <span className="timeline-name">{step.name}</span>
                  <span className="timeline-ms">{Math.round(step.latency_ms)} ms</span>
                  {step.detail && (
                    <span className="timeline-detail">{step.detail}</span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}

        {result?.reply_text && (
          <div className="section">
            <div className="label">Assistant</div>
            <div className="transcript">{result.reply_text}</div>
          </div>
        )}

        {audioUrl && (
          <div className="playback">
            <audio ref={audioRef} src={audioUrl} preload="auto" />
            <button type="button" className="play-btn" onClick={playResponse}>
              ▶ Play response
            </button>
          </div>
        )}

        <p className="footnote">
          Same Sarvam primitives are MCP tools — STT, language ID, LLM, and TTS work in Cursor too.
        </p>
      </div>
    </div>
  );
}
