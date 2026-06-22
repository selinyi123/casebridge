"use client";

import { useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function ClosureReportPage() {
  const [token, setToken] = useState("");
  const [report, setReport] = useState<Record<string, unknown> | null>(null);
  const [status, setStatus] = useState("Load the manual closure support report.");

  async function loadReport() {
    const response = await fetch(`${API_BASE}/api/v1/cases/CASE-0001/goals/closure-report`, {
      headers: { Authorization: `Bearer ${token.trim()}` },
    });
    if (!response.ok) {
      setStatus("Failed to load closure report.");
      return;
    }
    setReport(await response.json());
    setStatus("Report loaded. This does not close the case.");
  }

  return (
    <main style={{ maxWidth: 1000, margin: "0 auto", padding: 32, fontFamily: "system-ui, sans-serif" }}>
      <a href="/clients/c-0001/supervisor-review">Back to supervisor review</a>
      <h1>C-0001 Closure Report</h1>
      <p style={{ color: "#666" }}>{status}</p>
      <textarea value={token} onChange={(event) => setToken(event.target.value)} placeholder="Bearer token without the Bearer prefix" style={{ width: "100%", minHeight: 80, padding: 10, borderRadius: 10, border: "1px solid #ccc" }} />
      <button onClick={loadReport} style={{ marginTop: 12, padding: "8px 12px", borderRadius: 8, border: "1px solid #222" }}>Load report</button>
      {report ? (
        <section style={{ border: "1px solid #ddd", borderRadius: 14, padding: 16, marginTop: 24 }}>
          <pre style={{ whiteSpace: "pre-wrap", background: "#f6f6f6", padding: 12, borderRadius: 10 }}>{JSON.stringify(report, null, 2)}</pre>
        </section>
      ) : null}
    </main>
  );
}
