"use client";

import { useEffect, useState } from "react";

type Status = {
  ok: boolean;
  models?: string[];
  chat_default?: string | null;
  error?: string;
};

export function ApiStatus() {
  const [status, setStatus] = useState<Status | null>(null);

  useEffect(() => {
    let cancelled = false;
    void fetch("/api/sarvam-status")
      .then(async (response) => {
        const data = (await response.json()) as Status;
        if (!cancelled) setStatus(data);
      })
      .catch(() => {
        if (!cancelled) setStatus({ ok: false, error: "Could not reach status endpoint." });
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (!status) {
    return <p className="api-status">Checking Sarvam API…</p>;
  }

  if (!status.ok) {
    return (
      <p className="api-status is-warn">
        Key is set but inference needs dashboard credits. Catalog check:{" "}
        {status.error ?? "unavailable"}.
      </p>
    );
  }

  return (
    <p className="api-status is-ok">
      Connected · HTTP 200 · chat model {status.chat_default}
    </p>
  );
}
