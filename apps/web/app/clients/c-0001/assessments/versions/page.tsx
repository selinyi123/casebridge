"use client";

import { useState } from "react";

type VersionItem = {
  id: string;
  assessment_id: string;
  version_number: number;
  version_data: Record<string, unknown>;
  reason: string;
  created_by: string;
  created_at: string;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function AssessmentVersionsPage() {
  const [token, setToken] = useState("");
  const [assessmentId, setAssessmentId] = useState("");
  const [items, setItems] = useState<VersionItem[]>([]);
  const [status, setStatus] = useState("Enter assessment id and bearer token to load versions.");

  async function loadVersions() {
    if (!token.trim() || !assessmentId.trim()) {
      setStatus("Assessment id and token are required.");
      return;
    }
    const response = await fetch(`${API_BASE}/api/v1/cases/CASE-0001/assessments/${assessmentId.trim()}/versions`, {
      headers: { Authorization: `Bearer ${token.trim()}` },
    });
    if (!response.ok) {
      setStatus("Failed to load versions.");
      return;
    }
    const payload = await response.json();
    setItems(payload.items || []);
    setStatus("Assessment versions loaded.");
  }

  return (
    <main style={{ maxWidth: 960, margin: "0 auto", padding: 32, fontFamily: "system-ui, sans-serif" }}>
      <a href="/clients/c-0001/assessments">Back to assessments</a>
      <h1>C-0001 Assessment Versions</h1>
      <p style={{ color: "#666" }}>{status}</p>
      <input value={assessmentId} onChange={(event) => setAssessmentId(event.target.value)} placeholder="ASSESS-0001" style={{ display: "block", width: "100%", padding: 10, borderRadius: 10, border: "1px solid #ccc", marginBottom: 12 }} />
      <textarea value={token} onChange={(event) => setToken(event.target.value)} placeholder="Bearer token without the Bearer prefix" style={{ width: "100%", minHeight: 80, padding: 10, borderRadius: 10, border: "1px solid #ccc" }} />
      <button onClick={loadVersions} style={{ marginTop: 12, padding: "8px 12px", borderRadius: 8, border: "1px solid #222" }}>Load versions</button>
      <section style={{ display: "grid", gap: 12, marginTop: 24 }}>
        {items.map((item) => (
          <article key={item.id} style={{ border: "1px solid #ddd", borderRadius: 14, padding: 16 }}>
            <div style={{ color: "#666", fontSize: 14 }}>{item.id} · v{item.version_number} · {item.created_at}</div>
            <p>Created by: <code>{item.created_by}</code></p>
            <p>Reason: {item.reason}</p>
            <pre style={{ whiteSpace: "pre-wrap", background: "#f6f6f6", padding: 12, borderRadius: 10 }}>{JSON.stringify(item.version_data, null, 2)}</pre>
          </article>
        ))}
      </section>
    </main>
  );
}
