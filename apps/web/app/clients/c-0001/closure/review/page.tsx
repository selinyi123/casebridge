"use client";

import { FormEvent, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function ClosureReviewPage() {
  const [token, setToken] = useState("");
  const [draftId, setDraftId] = useState("");
  const [decision, setDecision] = useState("approved");
  const [status, setStatus] = useState("Review a closure draft. This will not close the case.");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const response = await fetch(`${API_BASE}/api/v1/cases/CASE-0001/goals/closure-drafts/${draftId.trim()}/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token.trim()}` },
      body: JSON.stringify({ decision }),
    });
    if (!response.ok) {
      setStatus("Failed to review closure draft. Supervisor or admin role is required.");
      return;
    }
    const payload = await response.json();
    setStatus(`Reviewed draft ${payload.draft.id}. Case status changed: ${String(payload.case_status_changed)}.`);
  }

  return (
    <main style={{ maxWidth: 800, margin: "0 auto", padding: 32, fontFamily: "system-ui, sans-serif" }}>
      <a href="/clients/c-0001/closure/report">Back to closure report</a>
      <h1>Review Closure Draft</h1>
      <p style={{ color: "#666" }}>{status}</p>
      <form onSubmit={submit} style={{ display: "grid", gap: 12 }}>
        <input value={draftId} onChange={(event) => setDraftId(event.target.value)} placeholder="CLOSE-0001" style={{ padding: 10, borderRadius: 10, border: "1px solid #ccc" }} />
        <select value={decision} onChange={(event) => setDecision(event.target.value)} style={{ padding: 10, borderRadius: 10, border: "1px solid #ccc" }}>
          <option value="approved">approved</option>
          <option value="rejected">rejected</option>
        </select>
        <textarea value={token} onChange={(event) => setToken(event.target.value)} placeholder="Bearer token without the Bearer prefix" style={{ minHeight: 80, padding: 10, borderRadius: 10, border: "1px solid #ccc" }} />
        <button type="submit" style={{ padding: "8px 12px", borderRadius: 8, border: "1px solid #222" }}>Review draft</button>
      </form>
    </main>
  );
}
