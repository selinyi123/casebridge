"use client";

import { FormEvent, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function CreateClosureDraftPage() {
  const [token, setToken] = useState("");
  const [reason, setReason] = useState("");
  const [status, setStatus] = useState("Create a manual closure draft. This does not close the case.");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const response = await fetch(`${API_BASE}/api/v1/cases/CASE-0001/goals/closure-drafts`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token.trim()}` },
      body: JSON.stringify({ closure_reason: reason }),
    });
    if (!response.ok) {
      setStatus("Failed to create closure draft.");
      return;
    }
    const payload = await response.json();
    setStatus(`Created closure draft ${payload.draft.id}. Case status is unchanged.`);
  }

  return (
    <main style={{ maxWidth: 800, margin: "0 auto", padding: 32, fontFamily: "system-ui, sans-serif" }}>
      <a href="/clients/c-0001/closure/report">Back to closure report</a>
      <h1>Create Closure Draft</h1>
      <p style={{ color: "#666" }}>{status}</p>
      <form onSubmit={submit} style={{ display: "grid", gap: 12 }}>
        <textarea value={reason} onChange={(event) => setReason(event.target.value)} placeholder="Closure reason draft" style={{ minHeight: 120, padding: 10, borderRadius: 10, border: "1px solid #ccc" }} />
        <textarea value={token} onChange={(event) => setToken(event.target.value)} placeholder="Bearer token without the Bearer prefix" style={{ minHeight: 80, padding: 10, borderRadius: 10, border: "1px solid #ccc" }} />
        <button type="submit" style={{ padding: "8px 12px", borderRadius: 8, border: "1px solid #222" }}>Create draft</button>
      </form>
    </main>
  );
}
