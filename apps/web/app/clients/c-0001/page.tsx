"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

type ClientProfile = {
  code: string;
  display_name: string;
  age: number;
  community: string;
  client_type: string;
  primary_concern: string;
  existing_support?: string;
  consent_status?: string;
  tags: string[];
};

type CaseRecord = {
  id: string;
  title: string;
  stage: string;
  status: string;
  primary_worker: string;
};

type CaseNote = {
  id: string;
  note_type: string;
  content_raw: string;
  content_clean: string;
  occurred_at: string;
  pii_detected: boolean;
  source: string;
};

type Resource = {
  code: string;
  name: string;
  category: string;
  match_codes: string[];
  status: string;
  region?: string;
};

type MatchCandidate = {
  resource_code: string;
  resource_name: string;
  category: string;
  matched_codes: string[];
  requires_human_verification: boolean;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

const box: React.CSSProperties = {
  border: "1px solid #ddd",
  borderRadius: 16,
  padding: 20,
  background: "#fff",
};

const muted: React.CSSProperties = { color: "#666", fontSize: 14 };

export default function ClientWorkspacePage() {
  const [client, setClient] = useState<ClientProfile | null>(null);
  const [caseRecord, setCaseRecord] = useState<CaseRecord | null>(null);
  const [notes, setNotes] = useState<CaseNote[]>([]);
  const [resources, setResources] = useState<Resource[]>([]);
  const [matches, setMatches] = useState<MatchCandidate[]>([]);
  const [newNote, setNewNote] = useState("");
  const [status, setStatus] = useState("Loading workspace...");

  const currentTags = useMemo(() => client?.tags || [], [client]);

  async function loadWorkspace() {
    setStatus("Loading workspace...");
    const clientRes = await fetch(`${API_BASE}/api/v1/clients/C-0001`);
    const clientPayload = await clientRes.json();
    const selectedCase = clientPayload.cases[0];
    setClient(clientPayload.client);
    setCaseRecord(selectedCase);

    const caseRes = await fetch(`${API_BASE}/api/v1/cases/${selectedCase.id}`);
    const casePayload = await caseRes.json();
    setNotes(casePayload.notes || []);

    const resourcesRes = await fetch(`${API_BASE}/api/v1/resources`);
    const resourcesPayload = await resourcesRes.json();
    setResources(resourcesPayload.items || []);
    setStatus("Workspace loaded. AI is not used in this version.");
  }

  async function submitNote(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!caseRecord || !newNote.trim()) return;
    setStatus("Saving human note...");
    const response = await fetch(`${API_BASE}/api/v1/cases/${caseRecord.id}/notes`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ note_type: "visit", content_raw: newNote.trim() }),
    });
    if (!response.ok) {
      setStatus("Failed to save note. Check API logs.");
      return;
    }
    setNewNote("");
    await loadWorkspace();
    setStatus("Note saved and visible in timeline.");
  }

  async function runResourceMatch() {
    if (!client) return;
    setStatus("Running deterministic tag-rule matching...");
    const response = await fetch(`${API_BASE}/api/v1/resources/match`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ need_tag_codes: currentTags }),
    });
    const payload = await response.json();
    setMatches(payload.candidates || []);
    setStatus("Candidate resources generated. Human verification is still required.");
  }

  useEffect(() => {
    loadWorkspace().catch(() => setStatus("Failed to load workspace. Start the API on port 8000."));
  }, []);

  return (
    <main style={{ maxWidth: 1180, margin: "0 auto", padding: 32, fontFamily: "system-ui, sans-serif", background: "#fafafa" }}>
      <header style={{ marginBottom: 24 }}>
        <p style={muted}>CaseBridge v0.1.3-ui-case-loop</p>
        <h1 style={{ fontSize: 34, margin: "4px 0" }}>C-0001 Case Workspace</h1>
        <p style={muted}>{status}</p>
      </header>

      <section style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 20 }}>
        <div style={box}>
          <h2>Client profile</h2>
          {client ? (
            <div style={{ lineHeight: 1.8 }}>
              <div><strong>{client.display_name}</strong> · {client.age} · {client.community}</div>
              <div>Type: <code>{client.client_type}</code></div>
              <div>Agreement status: <code>{client.consent_status || "unknown"}</code></div>
              <p>{client.primary_concern}</p>
              <p style={muted}>Existing support: {client.existing_support || "Not recorded"}</p>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                {client.tags.map((tag) => <code key={tag} style={{ background: "#eee", padding: "4px 8px", borderRadius: 8 }}>{tag}</code>)}
              </div>
            </div>
          ) : <p>Loading...</p>}
        </div>

        <div style={box}>
          <h2>Case summary</h2>
          {caseRecord ? (
            <div style={{ lineHeight: 1.8 }}>
              <div><strong>{caseRecord.title}</strong></div>
              <div>Stage: <code>{caseRecord.stage}</code></div>
              <div>Status: <code>{caseRecord.status}</code></div>
              <div>Worker: {caseRecord.primary_worker}</div>
              <p style={muted}>This version is manual-only. No AI output is written to case records.</p>
            </div>
          ) : <p>Loading...</p>}
        </div>
      </section>

      <section style={{ display: "grid", gridTemplateColumns: "1.2fr 0.8fr", gap: 20 }}>
        <div style={box}>
          <h2>Timeline</h2>
          <form onSubmit={submitNote} style={{ marginBottom: 20 }}>
            <textarea
              value={newNote}
              onChange={(event) => setNewNote(event.target.value)}
              placeholder="Add a human visit note. It will preserve raw text and store redacted clean text separately."
              style={{ width: "100%", minHeight: 100, borderRadius: 12, border: "1px solid #ccc", padding: 12 }}
            />
            <button type="submit" style={{ marginTop: 8, padding: "10px 14px", borderRadius: 10, border: "1px solid #222", background: "#111", color: "#fff" }}>
              Save human note
            </button>
          </form>

          <div style={{ display: "grid", gap: 12 }}>
            {notes.map((note) => (
              <article key={note.id} style={{ borderLeft: "4px solid #111", paddingLeft: 14 }}>
                <div style={muted}>{note.occurred_at} · {note.note_type} · {note.source}</div>
                <p>{note.content_raw}</p>
                {note.pii_detected ? <p style={{ color: "#a33" }}>PII detected; clean text stored separately.</p> : <p style={muted}>No PII detected by MVP redactor.</p>}
              </article>
            ))}
          </div>
        </div>

        <aside style={{ display: "grid", gap: 20 }}>
          <div style={box}>
            <h2>Resource matching</h2>
            <p style={muted}>Deterministic tag-rule matching. AI is not used.</p>
            <button onClick={runResourceMatch} style={{ padding: "10px 14px", borderRadius: 10, border: "1px solid #222", background: "#111", color: "#fff" }}>
              Match resources from current tags
            </button>
            <div style={{ display: "grid", gap: 10, marginTop: 16 }}>
              {matches.map((item) => (
                <div key={item.resource_code} style={{ border: "1px solid #ddd", borderRadius: 12, padding: 12 }}>
                  <strong>{item.resource_name}</strong>
                  <div style={muted}>{item.resource_code} · {item.category}</div>
                  <div>Matched: {item.matched_codes.join(", ")}</div>
                  <div style={{ color: "#8a5a00" }}>Requires human verification</div>
                </div>
              ))}
            </div>
          </div>

          <div style={box}>
            <h2>Resource list</h2>
            <div style={{ display: "grid", gap: 10 }}>
              {resources.map((resource) => (
                <div key={resource.code} style={{ borderBottom: "1px solid #eee", paddingBottom: 8 }}>
                  <strong>{resource.name}</strong>
                  <div style={muted}>{resource.code} · {resource.category} · {resource.status}</div>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}
