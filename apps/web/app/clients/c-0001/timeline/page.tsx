"use client";

import { useEffect, useState } from "react";

type TimelineEvent = {
  kind: string;
  id: string;
  at: string;
  title: string;
  payload: Record<string, unknown>;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function TimelinePage() {
  const [items, setItems] = useState<TimelineEvent[]>([]);
  const [status, setStatus] = useState("Loading timeline...");

  async function loadTimeline() {
    const response = await fetch(`${API_BASE}/api/v1/cases/CASE-0001/timeline`);
    if (!response.ok) {
      setStatus("Failed to load timeline. Start the API on port 8000.");
      return;
    }
    const payload = await response.json();
    setItems(payload.items || []);
    setStatus("Unified timeline loaded. AI is not used here.");
  }

  useEffect(() => {
    loadTimeline().catch(() => setStatus("Failed to load timeline."));
  }, []);

  return (
    <main style={{ maxWidth: 960, margin: "0 auto", padding: 32, fontFamily: "system-ui, sans-serif" }}>
      <a href="/clients/c-0001">Back to C-0001 workspace</a>
      <h1>C-0001 Unified Timeline</h1>
      <p style={{ color: "#666" }}>{status}</p>
      <section style={{ display: "grid", gap: 12, marginTop: 24 }}>
        {items.map((item) => (
          <article key={`${item.kind}-${item.id}`} style={{ border: "1px solid #ddd", borderRadius: 14, padding: 16 }}>
            <div style={{ color: "#666", fontSize: 14 }}>{item.at} · {item.kind}</div>
            <h2 style={{ fontSize: 18, margin: "8px 0" }}>{item.title}</h2>
            <pre style={{ whiteSpace: "pre-wrap", background: "#f6f6f6", padding: 12, borderRadius: 10, overflowX: "auto" }}>
              {JSON.stringify(item.payload, null, 2)}
            </pre>
          </article>
        ))}
      </section>
    </main>
  );
}
