"use client";

import { FormEvent, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function CreatePlanPage() {
  const [token, setToken] = useState("");
  const [title, setTitle] = useState("");
  const [assessmentId, setAssessmentId] = useState("");
  const [planData, setPlanData] = useState("{}");
  const [status, setStatus] = useState("Create a manual service plan. AI is not used here.");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    let parsed: Record<string, unknown>;
    try {
      parsed = JSON.parse(planData);
    } catch {
      setStatus("Plan data must be valid JSON.");
      return;
    }
    const response = await fetch(`${API_BASE}/api/v1/cases/CASE-0001/goals/plans`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token.trim()}` },
      body: JSON.stringify({ title, assessment_id: assessmentId.trim() || null, plan_status: "draft", plan_data: parsed }),
    });
    if (!response.ok) {
      setStatus("Failed to create plan. Check token, assessment id, and JSON body.");
      return;
    }
    const payload = await response.json();
    setStatus(`Created plan ${payload.plan.id}`);
  }

  return (
    <main style={{ maxWidth: 960, margin: "0 auto", padding: 32, fontFamily: "system-ui, sans-serif" }}>
      <a href="/clients/c-0001/evidence-chain">Back to evidence chain</a>
      <h1>Create Service Plan</h1>
      <p style={{ color: "#666" }}>{status}</p>
      <form onSubmit={submit} style={{ display: "grid", gap: 12 }}>
        <input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Plan title" style={{ padding: 10, borderRadius: 10, border: "1px solid #ccc" }} />
        <input value={assessmentId} onChange={(event) => setAssessmentId(event.target.value)} placeholder="Optional assessment id" style={{ padding: 10, borderRadius: 10, border: "1px solid #ccc" }} />
        <textarea value={planData} onChange={(event) => setPlanData(event.target.value)} placeholder="JSON plan data" style={{ minHeight: 160, padding: 10, borderRadius: 10, border: "1px solid #ccc" }} />
        <textarea value={token} onChange={(event) => setToken(event.target.value)} placeholder="Bearer token without the Bearer prefix" style={{ minHeight: 80, padding: 10, borderRadius: 10, border: "1px solid #ccc" }} />
        <button type="submit" style={{ padding: "8px 12px", borderRadius: 8, border: "1px solid #222" }}>Create plan</button>
      </form>
    </main>
  );
}
