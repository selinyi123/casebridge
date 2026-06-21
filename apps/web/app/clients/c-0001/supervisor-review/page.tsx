"use client";

import { FormEvent, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

type Readiness = {
  ready: boolean;
  blockers: string[];
  evidence_summary: Record<string, number>;
  manual_only: boolean;
};

export default function SupervisorReviewPage() {
  const [token, setToken] = useState("");
  const [note, setNote] = useState("");
  const [decision, setDecision] = useState("needs_more_work");
  const [readiness, setReadiness] = useState<Readiness | null>(null);
  const [status, setStatus] = useState("Load closure readiness, then create a manual supervisor review.");

  async function loadReadiness() {
    const response = await fetch(`${API_BASE}/api/v1/cases/CASE-0001/goals/closure-readiness`, {
      headers: { Authorization: `Bearer ${token.trim()}` },
    });
    if (!response.ok) {
      setStatus("Failed to load readiness. Check token and role.");
      return;
    }
    setReadiness(await response.json());
    setStatus("Closure readiness loaded. This is not an automatic closure decision.");
  }

  async function submitReview(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const response = await fetch(`${API_BASE}/api/v1/cases/CASE-0001/goals/supervisor-reviews`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token.trim()}` },
      body: JSON.stringify({ review_type: "closure_readiness", decision, note }),
    });
    if (!response.ok) {
      setStatus("Failed to create review. Supervisor or admin role is required.");
      return;
    }
    const payload = await response.json();
    setStatus(`Created supervisor review ${payload.review.id}`);
  }

  return (
    <main style={{ maxWidth: 1000, margin: "0 auto", padding: 32, fontFamily: "system-ui, sans-serif" }}>
      <a href="/clients/c-0001/evidence-chain">Back to evidence chain</a>
      <h1>C-0001 Supervisor Review</h1>
      <p style={{ color: "#666" }}>{status}</p>
      <textarea value={token} onChange={(event) => setToken(event.target.value)} placeholder="Bearer token without the Bearer prefix" style={{ width: "100%", minHeight: 80, padding: 10, borderRadius: 10, border: "1px solid #ccc" }} />
      <button onClick={loadReadiness} style={{ marginTop: 12, padding: "8px 12px", borderRadius: 8, border: "1px solid #222" }}>Load readiness</button>
      {readiness ? (
        <section style={{ border: "1px solid #ddd", borderRadius: 14, padding: 16, marginTop: 24 }}>
          <h2>Closure Readiness</h2>
          <p>Ready: <strong>{String(readiness.ready)}</strong></p>
          <p>Manual only: <strong>{String(readiness.manual_only)}</strong></p>
          <pre style={{ whiteSpace: "pre-wrap", background: "#f6f6f6", padding: 12, borderRadius: 10 }}>{JSON.stringify(readiness, null, 2)}</pre>
        </section>
      ) : null}
      <form onSubmit={submitReview} style={{ display: "grid", gap: 12, marginTop: 24 }}>
        <select value={decision} onChange={(event) => setDecision(event.target.value)} style={{ padding: 10, borderRadius: 10, border: "1px solid #ccc" }}>
          <option value="needs_more_work">needs_more_work</option>
          <option value="continue_service">continue_service</option>
          <option value="ready_for_closure">ready_for_closure</option>
        </select>
        <textarea value={note} onChange={(event) => setNote(event.target.value)} placeholder="Supervisor review note" style={{ minHeight: 140, padding: 10, borderRadius: 10, border: "1px solid #ccc" }} />
        <button type="submit" style={{ padding: "8px 12px", borderRadius: 8, border: "1px solid #222" }}>Create supervisor review</button>
      </form>
    </main>
  );
}
