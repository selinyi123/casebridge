"use client";

import { useEffect, useState } from "react";

type Outcome = {
  id: string;
  gas_score?: number;
  outcome_type: string;
  narrative: string;
  evidence?: string;
  created_at: string;
};

type OutcomeReport = {
  case_id: string;
  outcome_count: number;
  gas_score_count: number;
  latest_gas_score?: number;
  manual_only: boolean;
  items: Outcome[];
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function OutcomeReportPage() {
  const [token, setToken] = useState("");
  const [report, setReport] = useState<OutcomeReport | null>(null);
  const [status, setStatus] = useState("Paste a demo JWT token to load the outcome report.");

  async function loadReport() {
    if (!token.trim()) {
      setStatus("Token required. Use /api/v1/auth/login to get one.");
      return;
    }
    const response = await fetch(`${API_BASE}/api/v1/cases/CASE-0001/outcomes/report`, {
      headers: { Authorization: `Bearer ${token.trim()}` },
    });
    if (!response.ok) {
      setStatus("Failed to load report. Token may be missing or expired.");
      return;
    }
    const payload = await response.json();
    setReport(payload);
    setStatus("Manual outcome report loaded. No AI scoring is used.");
  }

  useEffect(() => {
    setReport(null);
  }, [token]);

  return (
    <main style={{ maxWidth: 960, margin: "0 auto", padding: 32, fontFamily: "system-ui, sans-serif" }}>
      <a href="/clients/c-0001/outcomes">Back to outcomes</a>
      <h1>C-0001 Outcome Report</h1>
      <p style={{ color: "#666" }}>{status}</p>
      <textarea value={token} onChange={(event) => setToken(event.target.value)} placeholder="Bearer token without the Bearer prefix" style={{ width: "100%", minHeight: 80, padding: 10, borderRadius: 10, border: "1px solid #ccc" }} />
      <button onClick={loadReport} style={{ marginTop: 12, padding: "8px 12px", borderRadius: 8, border: "1px solid #222" }}>Load report</button>
      {report ? (
        <section style={{ border: "1px solid #ddd", borderRadius: 14, padding: 16, marginTop: 24 }}>
          <h2>Summary</h2>
          <p>Outcome count: <strong>{report.outcome_count}</strong></p>
          <p>GAS score count: <strong>{report.gas_score_count}</strong></p>
          <p>Latest GAS score: <strong>{report.latest_gas_score ?? "not set"}</strong></p>
          <p>Manual only: <strong>{String(report.manual_only)}</strong></p>
          <h2>Evidence items</h2>
          {report.items.map((item) => (
            <article key={item.id} style={{ borderTop: "1px solid #eee", paddingTop: 12, marginTop: 12 }}>
              <div style={{ color: "#666", fontSize: 14 }}>{item.id} · {item.outcome_type} · {item.created_at}</div>
              <p>GAS: <strong>{item.gas_score ?? "not set"}</strong></p>
              <p>{item.narrative}</p>
              <p style={{ color: "#666" }}>{item.evidence}</p>
            </article>
          ))}
        </section>
      ) : null}
    </main>
  );
}
