"use client";

import { useEffect, useState } from "react";

type Note = { id: string; note_type: string; content_raw: string; occurred_at: string };
type AiOutput = { id: string; note_id: string; review_status: string; parsed_output: Record<string, unknown>; created_at: string };

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function AiIntakePage() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [outputs, setOutputs] = useState<AiOutput[]>([]);
  const [status, setStatus] = useState("Loading AI review gate...");

  async function loadData() {
    const notesPayload = await (await fetch(`${API_BASE}/api/v1/cases/CASE-0001/notes`)).json();
    const outputsPayload = await (await fetch(`${API_BASE}/api/v1/cases/CASE-0001/ai/outputs`)).json();
    setNotes(notesPayload.items || []);
    setOutputs(outputsPayload.items || []);
    setStatus("AI review gate loaded. Provider is mock only.");
  }

  async function generateDraft(noteId: string) {
    setStatus("Generating mock intake draft...");
    const response = await fetch(`${API_BASE}/api/v1/cases/CASE-0001/ai/intake`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ note_id: noteId }),
    });
    if (!response.ok) {
      setStatus("Failed to generate draft.");
      return;
    }
    await loadData();
    setStatus("Draft created in ai_outputs with review_status=pending.");
  }

  async function reviewOutput(outputId: string, reviewStatus: "accepted" | "rejected") {
    const response = await fetch(`${API_BASE}/api/v1/cases/CASE-0001/ai/outputs/${outputId}/review`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ review_status: reviewStatus, reviewer_notes: "Reviewed in demo UI." }),
    });
    if (!response.ok) {
      setStatus("Failed to review output.");
      return;
    }
    await loadData();
    setStatus(`Draft marked as ${reviewStatus}. Formal case fields were not changed.`);
  }

  useEffect(() => {
    loadData().catch(() => setStatus("Failed to load. Start the API on port 8000."));
  }, []);

  return (
    <main style={{ maxWidth: 1040, margin: "0 auto", padding: 32, fontFamily: "system-ui, sans-serif" }}>
      <a href="/clients/c-0001">Back to C-0001 workspace</a>
      <h1>AI Intake Gate</h1>
      <p style={{ color: "#666" }}>{status}</p>
      <section style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginTop: 24 }}>
        <div style={{ border: "1px solid #ddd", borderRadius: 14, padding: 16 }}>
          <h2>Human notes</h2>
          {notes.map((note) => (
            <article key={note.id} style={{ borderBottom: "1px solid #eee", paddingBottom: 12, marginBottom: 12 }}>
              <div style={{ color: "#666", fontSize: 14 }}>{note.id} · {note.note_type} · {note.occurred_at}</div>
              <p>{note.content_raw}</p>
              <button onClick={() => generateDraft(note.id)} style={{ padding: "8px 10px", borderRadius: 8, border: "1px solid #222" }}>
                Generate mock AI draft
              </button>
            </article>
          ))}
        </div>
        <div style={{ border: "1px solid #ddd", borderRadius: 14, padding: 16 }}>
          <h2>AI draft outputs</h2>
          {outputs.map((output) => (
            <article key={output.id} style={{ border: "1px solid #eee", borderRadius: 12, padding: 12, marginBottom: 12 }}>
              <div style={{ color: "#666", fontSize: 14 }}>{output.id} · note {output.note_id} · {output.review_status}</div>
              <pre style={{ whiteSpace: "pre-wrap", background: "#f6f6f6", padding: 10, borderRadius: 8 }}>{JSON.stringify(output.parsed_output, null, 2)}</pre>
              <button onClick={() => reviewOutput(output.id, "accepted")} style={{ marginRight: 8, padding: "8px 10px", borderRadius: 8, border: "1px solid #222" }}>Accept draft</button>
              <button onClick={() => reviewOutput(output.id, "rejected")} style={{ padding: "8px 10px", borderRadius: 8, border: "1px solid #222" }}>Reject draft</button>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
