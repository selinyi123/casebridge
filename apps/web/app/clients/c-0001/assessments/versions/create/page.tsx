"use client";

import { FormEvent, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function CreateAssessmentVersionPage() {
  const [token, setToken] = useState("");
  const [assessmentId, setAssessmentId] = useState("");
  const [reason, setReason] = useState("");
  const [versionJson, setVersionJson] = useState("{}");
  const [status, setStatus] = useState("Admin token is required to create an assessment version.");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    let parsed: Record<string, unknown>;
    try {
      parsed = JSON.parse(versionJson);
    } catch {
      setStatus("Version data must be valid JSON.");
      return;
    }
    const response = await fetch(`${API_BASE}/api/v1/cases/CASE-0001/assessments/${assessmentId.trim()}/versions`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token.trim()}` },
      body: JSON.stringify({ reason, version_data: parsed }),
    });
    if (!response.ok) {
      setStatus("Failed to create version. Check role, token, assessment id, and JSON body.");
      return;
    }
    const payload = await response.json();
    setStatus(`Created version ${payload.version.version_number}: ${payload.version.id}`);
  }

  return (
    <main style={{ maxWidth: 960, margin: "0 auto", padding: 32, fontFamily: "system-ui, sans-serif" }}>
      <a href="/clients/c-0001/assessments/versions">Back to versions</a>
      <h1>Create Assessment Version</h1>
      <p style={{ color: "#666" }}>{status}</p>
      <form onSubmit={submit} style={{ display: "grid", gap: 12 }}>
        <input value={assessmentId} onChange={(event) => setAssessmentId(event.target.value)} placeholder="ASSESS-0001" style={{ padding: 10, borderRadius: 10, border: "1px solid #ccc" }} />
        <input value={reason} onChange={(event) => setReason(event.target.value)} placeholder="Reason for new version" style={{ padding: 10, borderRadius: 10, border: "1px solid #ccc" }} />
        <textarea value={versionJson} onChange={(event) => setVersionJson(event.target.value)} placeholder="JSON version data" style={{ minHeight: 160, padding: 10, borderRadius: 10, border: "1px solid #ccc" }} />
        <textarea value={token} onChange={(event) => setToken(event.target.value)} placeholder="Bearer token without the Bearer prefix" style={{ minHeight: 80, padding: 10, borderRadius: 10, border: "1px solid #ccc" }} />
        <button type="submit" style={{ padding: "8px 12px", borderRadius: 8, border: "1px solid #222" }}>Create version</button>
      </form>
    </main>
  );
}
