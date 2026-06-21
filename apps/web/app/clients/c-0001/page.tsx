"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

type ClientProfile = { code: string; display_name: string; age: number; community: string; client_type: string; primary_concern: string; existing_support?: string; consent_status?: string; tags: string[] };
type CaseRecord = { id: string; title: string; stage: string; status: string; primary_worker: string };
type CaseNote = { id: string; note_type: string; content_raw: string; content_clean: string; occurred_at: string; pii_detected: boolean; source: string };
type Resource = { code: string; name: string; category: string; match_codes: string[]; status: string; region?: string };
type MatchCandidate = { resource_code: string; resource_name: string; category: string; matched_codes: string[]; requires_human_verification: boolean };
type ServiceGoal = { id: string; title: string; target_state: string; status: string; created_at: string };
type ResourceLink = { id: string; resource_code: string; status: string; agreement_status: string; notes?: string; created_at: string };

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
const box: React.CSSProperties = { border: "1px solid #ddd", borderRadius: 16, padding: 20, background: "#fff" };
const muted: React.CSSProperties = { color: "#666", fontSize: 14 };

export default function ClientWorkspacePage() {
  const [client, setClient] = useState<ClientProfile | null>(null);
  const [caseRecord, setCaseRecord] = useState<CaseRecord | null>(null);
  const [notes, setNotes] = useState<CaseNote[]>([]);
  const [resources, setResources] = useState<Resource[]>([]);
  const [matches, setMatches] = useState<MatchCandidate[]>([]);
  const [goals, setGoals] = useState<ServiceGoal[]>([]);
  const [links, setLinks] = useState<ResourceLink[]>([]);
  const [newNote, setNewNote] = useState("");
  const [goalTitle, setGoalTitle] = useState("");
  const [goalTarget, setGoalTarget] = useState("");
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
    setResources((await resourcesRes.json()).items || []);

    const goalsRes = await fetch(`${API_BASE}/api/v1/cases/${selectedCase.id}/goals`);
    setGoals((await goalsRes.json()).items || []);

    const linksRes = await fetch(`${API_BASE}/api/v1/cases/${selectedCase.id}/referrals`);
    setLinks((await linksRes.json()).items || []);
    setStatus("Workspace loaded. AI is not used in this version.");
  }

  async function submitNote(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!caseRecord || !newNote.trim()) return;
    setStatus("Saving human note...");
    const response = await fetch(`${API_BASE}/api/v1/cases/${caseRecord.id}/notes`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ note_type: "visit", content_raw: newNote.trim() }) });
    if (!response.ok) { setStatus("Failed to save note. Check API logs."); return; }
    setNewNote("");
    await loadWorkspace();
    setStatus("Note saved and visible in timeline.");
  }

  async function submitGoal(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!caseRecord || !goalTitle.trim() || !goalTarget.trim()) return;
    const response = await fetch(`${API_BASE}/api/v1/cases/${caseRecord.id}/goals`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title: goalTitle.trim(), target_state: goalTarget.trim() }) });
    if (!response.ok) { setStatus("Failed to save service goal."); return; }
    setGoalTitle("");
    setGoalTarget("");
    await loadWorkspace();
    setStatus("Manual service goal saved.");
  }

  async function runResourceMatch() {
    if (!client) return;
    setStatus("Running deterministic tag-rule matching...");
    const response = await fetch(`${API_BASE}/api/v1/resources/match`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ need_tag_codes: currentTags }) });
    const payload = await response.json();
    setMatches(payload.candidates || []);
    setStatus("Candidate resources generated. Human verification is still required.");
  }

  async function createResourceLink(resourceCode: string) {
    if (!caseRecord) return;
    const response = await fetch(`${API_BASE}/api/v1/cases/${caseRecord.id}/referrals`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ resource_code: resourceCode, agreement_status: "none", notes: "Created from resource candidate. Manual verification required." }) });
    if (!response.ok) { setStatus("Failed to create resource link."); return; }
    await loadWorkspace();
    setStatus("Resource candidate saved as manual link with agreement_status=none.");
  }

  async function advanceLink(linkId: string) {
    if (!caseRecord) return;
    const response = await fetch(`${API_BASE}/api/v1/cases/${caseRecord.id}/referrals/${linkId}/status`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ status: "referred", agreement_status: "verbal" }) });
    if (!response.ok) { setStatus("Link status blocked. Agreement state is required."); return; }
    await loadWorkspace();
    setStatus("Resource link advanced after explicit agreement state.");
  }

  useEffect(() => { loadWorkspace().catch(() => setStatus("Failed to load workspace. Start the API on port 8000.")); }, []);

  return (
    <main style={{ maxWidth: 1180, margin: "0 auto", padding: 32, fontFamily: "system-ui, sans-serif", background: "#fafafa" }}>
      <header style={{ marginBottom: 24 }}>
        <p style={muted}>CaseBridge v0.1.4-manual-goal-link-gate</p>
        <h1 style={{ fontSize: 34, margin: "4px 0" }}>C-0001 Case Workspace</h1>
        <p style={muted}>{status}</p>
      </header>

      <section style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 20 }}>
        <div style={box}>
          <h2>Client profile</h2>
          {client ? <div style={{ lineHeight: 1.8 }}><div><strong>{client.display_name}</strong> · {client.age} · {client.community}</div><div>Type: <code>{client.client_type}</code></div><div>Agreement status: <code>{client.consent_status || "unknown"}</code></div><p>{client.primary_concern}</p><p style={muted}>Existing support: {client.existing_support || "Not recorded"}</p><div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>{client.tags.map((tag) => <code key={tag} style={{ background: "#eee", padding: "4px 8px", borderRadius: 8 }}>{tag}</code>)}</div></div> : <p>Loading...</p>}
        </div>
        <div style={box}>
          <h2>Case summary</h2>
          {caseRecord ? <div style={{ lineHeight: 1.8 }}><div><strong>{caseRecord.title}</strong></div><div>Stage: <code>{caseRecord.stage}</code></div><div>Status: <code>{caseRecord.status}</code></div><div>Worker: {caseRecord.primary_worker}</div><p style={muted}>Manual-only. AI output is not written to records.</p></div> : <p>Loading...</p>}
        </div>
      </section>

      <section style={{ display: "grid", gridTemplateColumns: "1.2fr 0.8fr", gap: 20 }}>
        <div style={{ display: "grid", gap: 20 }}>
          <div style={box}>
            <h2>Timeline</h2>
            <form onSubmit={submitNote} style={{ marginBottom: 20 }}><textarea value={newNote} onChange={(event) => setNewNote(event.target.value)} placeholder="Add a human visit note." style={{ width: "100%", minHeight: 100, borderRadius: 12, border: "1px solid #ccc", padding: 12 }} /><button type="submit" style={{ marginTop: 8, padding: "10px 14px", borderRadius: 10, border: "1px solid #222", background: "#111", color: "#fff" }}>Save human note</button></form>
            <div style={{ display: "grid", gap: 12 }}>{notes.map((note) => <article key={note.id} style={{ borderLeft: "4px solid #111", paddingLeft: 14 }}><div style={muted}>{note.occurred_at} · {note.note_type} · {note.source}</div><p>{note.content_raw}</p>{note.pii_detected ? <p style={{ color: "#a33" }}>PII detected; clean text stored separately.</p> : <p style={muted}>No PII detected by MVP redactor.</p>}</article>)}</div>
          </div>

          <div style={box}>
            <h2>Service goals</h2>
            <form onSubmit={submitGoal} style={{ display: "grid", gap: 8, marginBottom: 16 }}><input value={goalTitle} onChange={(event) => setGoalTitle(event.target.value)} placeholder="Goal title" style={{ padding: 10, borderRadius: 10, border: "1px solid #ccc" }} /><textarea value={goalTarget} onChange={(event) => setGoalTarget(event.target.value)} placeholder="Target state" style={{ minHeight: 80, padding: 10, borderRadius: 10, border: "1px solid #ccc" }} /><button type="submit" style={{ padding: "10px 14px", borderRadius: 10, border: "1px solid #222", background: "#111", color: "#fff" }}>Create manual goal</button></form>
            <div style={{ display: "grid", gap: 10 }}>{goals.map((goal) => <div key={goal.id} style={{ border: "1px solid #eee", borderRadius: 12, padding: 12 }}><strong>{goal.title}</strong><div style={muted}>{goal.status} · {goal.created_at}</div><p>{goal.target_state}</p></div>)}</div>
          </div>
        </div>

        <aside style={{ display: "grid", gap: 20 }}>
          <div style={box}>
            <h2>Resource matching</h2><p style={muted}>Candidates only. Creating a link still requires manual verification.</p><button onClick={runResourceMatch} style={{ padding: "10px 14px", borderRadius: 10, border: "1px solid #222", background: "#111", color: "#fff" }}>Match resources from current tags</button>
            <div style={{ display: "grid", gap: 10, marginTop: 16 }}>{matches.map((item) => <div key={item.resource_code} style={{ border: "1px solid #ddd", borderRadius: 12, padding: 12 }}><strong>{item.resource_name}</strong><div style={muted}>{item.resource_code} · {item.category}</div><div>Matched: {item.matched_codes.join(", ")}</div><div style={{ color: "#8a5a00" }}>Requires human verification</div><button onClick={() => createResourceLink(item.resource_code)} style={{ marginTop: 8, padding: "8px 10px", borderRadius: 8, border: "1px solid #222" }}>Create manual link</button></div>)}</div>
          </div>

          <div style={box}>
            <h2>Manual resource links</h2>
            <div style={{ display: "grid", gap: 10 }}>{links.map((link) => <div key={link.id} style={{ border: "1px solid #eee", borderRadius: 12, padding: 12 }}><strong>{link.resource_code}</strong><div>Status: <code>{link.status}</code></div><div>Agreement: <code>{link.agreement_status}</code></div><button onClick={() => advanceLink(link.id)} style={{ marginTop: 8, padding: "8px 10px", borderRadius: 8, border: "1px solid #222" }}>Advance with verbal agreement</button></div>)}</div>
          </div>

          <div style={box}>
            <h2>Resource list</h2><div style={{ display: "grid", gap: 10 }}>{resources.map((resource) => <div key={resource.code} style={{ borderBottom: "1px solid #eee", paddingBottom: 8 }}><strong>{resource.name}</strong><div style={muted}>{resource.code} · {resource.category} · {resource.status}</div></div>)}</div>
          </div>
        </aside>
      </section>
    </main>
  );
}
