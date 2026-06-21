"use client";

import { FormEvent, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function CreateInterventionPage() {
  const [token, setToken] = useState("");
  const [planId, setPlanId] = useState("");
  const [goalId, setGoalId] = useState("");
  const [narrative, setNarrative] = useState("");
  const [evidence, setEvidence] = useState("");
  const [status, setStatus] = useState("Create a manual intervention record. AI is not used here.");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const response = await fetch(`${API_BASE}/api/v1/cases/CASE-0001/goals/interventions`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token.trim()}` },
      body: JSON.stringify({ plan_id: planId, goal_id: goalId.trim() || null, intervention_type: "followup", narrative, evidence: evidence || null }),
    });
    if (!response.ok) {
      setStatus("Failed to create intervention. Check token, plan id, goal id, and narrative.");
      return;
    }
    const payload = await response.json();
    setStatus(`Created intervention ${payload.intervention.id}`);
  }

  return (
    <main style={{ maxWidth: 960, margin: "0 auto", padding: 32, fontFamily: "system-ui, sans-serif" }}>
      <a href="/clients/c-0001/evidence-chain">Back to evidence chain</a>
      <h1>Create Intervention</h1>
      <p style={{ color: "#666" }}>{status}</p>
      <form onSubmit={submit} style={{ display: "grid", gap: 12 }}>
        <input value={planId} onChange={(event) => setPlanId(event.target.value)} placeholder="PLAN-0001" style={{ padding: 10, borderRadius: 10, border: "1px solid #ccc" }} />
        <input value={goalId} onChange={(event) => setGoalId(event.target.value)} placeholder="Optional goal id" style={{ padding: 10, borderRadius: 10, border: "1px solid #ccc" }} />
        <textarea value={narrative} onChange={(event) => setNarrative(event.target.value)} placeholder="Manual intervention narrative" style={{ minHeight: 120, padding: 10, borderRadius: 10, border: "1px solid #ccc" }} />
        <textarea value={evidence} onChange={(event) => setEvidence(event.target.value)} placeholder="Optional evidence" style={{ minHeight: 100, padding: 10, borderRadius: 10, border: "1px solid #ccc" }} />
        <textarea value={token} onChange={(event) => setToken(event.target.value)} placeholder="Bearer token without the Bearer prefix" style={{ minHeight: 80, padding: 10, borderRadius: 10, border: "1px solid #ccc" }} />
        <button type="submit" style={{ padding: "8px 12px", borderRadius: 8, border: "1px solid #222" }}>Create intervention</button>
      </form>
    </main>
  );
}
