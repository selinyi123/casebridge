"use client";

import { useEffect, useState } from "react";

type Assessment = {
  id: string;
  case_id: string;
  source_note_id: string;
  source_ai_output_id: string;
  provider: string;
  prompt_version: string;
  assessment_type: string;
  assessment_data: Record<string, unknown>;
  reviewer_id: string;
  reviewer_responsibility_accepted: boolean;
  created_at: string;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function AssessmentsPage() {
  const [items, setItems] = useState<Assessment[]>([]);
  const [status, setStatus] = useState("Loading assessments...");

  async function loadAssessments() {
    const response = await fetch(`${API_BASE}/api/v1/cases/CASE-0001/assessments`);
    if (!response.ok) {
      setStatus("Failed to load assessments. Start the API on port 8000.");
      return;
    }
    const payload = await response.json();
    setItems(payload.items || []);
    setStatus("Formal assessments loaded. Each item requires explicit human apply action.");
  }

  useEffect(() => {
    loadAssessments().catch(() => setStatus("Failed to load assessments."));
  }, []);

  return (
    <main style={{ maxWidth: 1040, margin: "0 auto", padding: 32, fontFamily: "system-ui, sans-serif" }}>
      <a href="/clients/c-0001">Back to C-0001 workspace</a>
      <h1>C-0001 Formal Assessments</h1>
      <p style={{ color: "#666" }}>{status}</p>
      <section style={{ display: "grid", gap: 14, marginTop: 24 }}>
        {items.map((item) => (
          <article key={item.id} style={{ border: "1px solid #ddd", borderRadius: 14, padding: 16 }}>
            <div style={{ color: "#666", fontSize: 14 }}>{item.id} · {item.assessment_type} · {item.created_at}</div>
            <p>Source note: <code>{item.source_note_id}</code></p>
            <p>AI output: <code>{item.source_ai_output_id}</code></p>
            <p>Provider: <code>{item.provider}</code> · Prompt: <code>{item.prompt_version}</code></p>
            <p>Reviewer: <code>{item.reviewer_id}</code> · Responsibility accepted: <code>{String(item.reviewer_responsibility_accepted)}</code></p>
            <pre style={{ whiteSpace: "pre-wrap", background: "#f6f6f6", padding: 12, borderRadius: 10 }}>{JSON.stringify(item.assessment_data, null, 2)}</pre>
          </article>
        ))}
      </section>
    </main>
  );
}
