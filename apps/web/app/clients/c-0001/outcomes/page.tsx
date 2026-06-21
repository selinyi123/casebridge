"use client";

import { FormEvent, useEffect, useState } from "react";

type Outcome = {
  id: string;
  case_id: string;
  goal_id?: string;
  assessment_id?: string;
  outcome_type: string;
  gas_score?: number;
  narrative: string;
  evidence?: string;
  recorded_by: string;
  created_at: string;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function OutcomesPage() {
  const [items, setItems] = useState<Outcome[]>([]);
  const [narrative, setNarrative] = useState("");
  const [gasScore, setGasScore] = useState("0");
  const [status, setStatus] = useState("Loading outcomes...");

  async function loadOutcomes() {
    const response = await fetch(`${API_BASE}/api/v1/cases/CASE-0001/outcomes`);
    if (!response.ok) {
      setStatus("Failed to load outcomes. Start the API on port 8000.");
      return;
    }
    const payload = await response.json();
    setItems(payload.items || []);
    setStatus("Outcome tracking loaded. Scores are manually entered by the worker.");
  }

  async function submitOutcome(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!narrative.trim()) return;
    const response = await fetch(`${API_BASE}/api/v1/cases/CASE-0001/outcomes`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ outcome_type: "goal_attainment", gas_score: Number(gasScore), narrative: narrative.trim(), evidence: "Demo follow-up note." }),
    });
    if (!response.ok) {
      setStatus("Failed to save outcome. GAS score must be between -2 and 2.");
      return;
    }
    setNarrative("");
    setGasScore("0");
    await loadOutcomes();
    setStatus("Outcome saved and audit event recorded.");
  }

  useEffect(() => {
    loadOutcomes().catch(() => setStatus("Failed to load outcomes."));
  }, []);

  return (
    <main style={{ maxWidth: 960, margin: "0 auto", padding: 32, fontFamily: "system-ui, sans-serif" }}>
      <a href="/clients/c-0001">Back to C-0001 workspace</a>
      <h1>C-0001 Outcome Tracking</h1>
      <p style={{ color: "#666" }}>{status}</p>
      <form onSubmit={submitOutcome} style={{ border: "1px solid #ddd", borderRadius: 14, padding: 16, marginTop: 24 }}>
        <h2>Record manual outcome</h2>
        <label style={{ display: "block", marginBottom: 8 }}>GAS score (-2 to +2)</label>
        <select value={gasScore} onChange={(event) => setGasScore(event.target.value)} style={{ padding: 8, marginBottom: 12 }}>
          <option value="-2">-2</option>
          <option value="-1">-1</option>
          <option value="0">0</option>
          <option value="1">+1</option>
          <option value="2">+2</option>
        </select>
        <textarea value={narrative} onChange={(event) => setNarrative(event.target.value)} placeholder="Manual outcome narrative" style={{ display: "block", width: "100%", minHeight: 100, padding: 10, borderRadius: 10, border: "1px solid #ccc" }} />
        <button type="submit" style={{ marginTop: 12, padding: "8px 12px", borderRadius: 8, border: "1px solid #222" }}>Save outcome</button>
      </form>
      <section style={{ display: "grid", gap: 12, marginTop: 24 }}>
        {items.map((item) => (
          <article key={item.id} style={{ border: "1px solid #ddd", borderRadius: 14, padding: 16 }}>
            <div style={{ color: "#666", fontSize: 14 }}>{item.id} · {item.outcome_type} · {item.created_at}</div>
            <p>GAS score: <strong>{item.gas_score ?? "not set"}</strong></p>
            <p>{item.narrative}</p>
            <p style={{ color: "#666" }}>{item.evidence}</p>
          </article>
        ))}
      </section>
    </main>
  );
}
