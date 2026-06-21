"use client";

import { useState } from "react";

type Chain = {
  case_id: string;
  plans: Record<string, unknown>[];
  interventions: Record<string, unknown>[];
  outcomes: Record<string, unknown>[];
  manual_only: boolean;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function EvidenceChainPage() {
  const [token, setToken] = useState("");
  const [chain, setChain] = useState<Chain | null>(null);
  const [status, setStatus] = useState("Enter a bearer token to load the service evidence chain.");

  async function loadChain() {
    const response = await fetch(`${API_BASE}/api/v1/cases/CASE-0001/goals/evidence-chain`, {
      headers: { Authorization: `Bearer ${token.trim()}` },
    });
    if (!response.ok) {
      setStatus("Failed to load evidence chain. Check token and role.");
      return;
    }
    const payload = await response.json();
    setChain(payload);
    setStatus("Evidence chain loaded. This view is manual-only and does not use AI scoring.");
  }

  function renderItems(title: string, items: Record<string, unknown>[]) {
    return (
      <section style={{ border: "1px solid #ddd", borderRadius: 14, padding: 16 }}>
        <h2>{title}</h2>
        {items.map((item) => (
          <article key={String(item.id)} style={{ borderTop: "1px solid #eee", paddingTop: 12, marginTop: 12 }}>
            <div style={{ color: "#666", fontSize: 14 }}>{String(item.id)} · {String(item.created_at || "")}</div>
            <pre style={{ whiteSpace: "pre-wrap", background: "#f6f6f6", padding: 12, borderRadius: 10 }}>{JSON.stringify(item, null, 2)}</pre>
          </article>
        ))}
      </section>
    );
  }

  return (
    <main style={{ maxWidth: 1100, margin: "0 auto", padding: 32, fontFamily: "system-ui, sans-serif" }}>
      <a href="/clients/c-0001">Back to workspace</a>
      <h1>C-0001 Service Evidence Chain</h1>
      <p style={{ color: "#666" }}>{status}</p>
      <textarea value={token} onChange={(event) => setToken(event.target.value)} placeholder="Bearer token without the Bearer prefix" style={{ width: "100%", minHeight: 80, padding: 10, borderRadius: 10, border: "1px solid #ccc" }} />
      <button onClick={loadChain} style={{ marginTop: 12, padding: "8px 12px", borderRadius: 8, border: "1px solid #222" }}>Load evidence chain</button>
      {chain ? (
        <div style={{ display: "grid", gap: 16, marginTop: 24 }}>
          <p>Manual only: <strong>{String(chain.manual_only)}</strong></p>
          {renderItems("Service Plans", chain.plans)}
          {renderItems("Interventions", chain.interventions)}
          {renderItems("Outcomes", chain.outcomes)}
        </div>
      ) : null}
    </main>
  );
}
