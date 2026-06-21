const apiRoutes = [
  "GET /api/v1/clients",
  "GET /api/v1/clients/C-0001",
  "GET /api/v1/cases/CASE-0001",
  "POST /api/v1/cases/CASE-0001/notes",
  "GET /api/v1/resources",
  "POST /api/v1/resources/match",
];

const demoSteps = [
  "Client profile",
  "Case record",
  "Visit note",
  "Timeline",
  "Resource list",
  "Tag-rule matching",
  "Manual service plan later",
  "Review gate later",
  "Outcome tracking later",
];

export default function Home() {
  return (
    <main style={{ maxWidth: 960, margin: "0 auto", padding: 32, fontFamily: "system-ui, sans-serif" }}>
      <section style={{ marginBottom: 32 }}>
        <p style={{ fontSize: 14, color: "#666" }}>CaseBridge v0.1.2-business-skeleton</p>
        <h1 style={{ fontSize: 40, margin: "8px 0" }}>CaseBridge</h1>
        <p style={{ fontSize: 18, lineHeight: 1.7 }}>
          Non-AI business skeleton for the C-0001 case loop. The current node focuses on clients, cases, notes, resources, and deterministic resource matching.
        </p>
      </section>

      <section style={{ border: "1px solid #ddd", borderRadius: 16, padding: 24, marginBottom: 24 }}>
        <h2>Core rule</h2>
        <p>Business loop first. AI later. No model call is required in this version.</p>
      </section>

      <section style={{ border: "1px solid #ddd", borderRadius: 16, padding: 24, marginBottom: 24 }}>
        <h2>C-0001 loop status</h2>
        <ol style={{ lineHeight: 2 }}>
          {demoSteps.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
      </section>

      <section style={{ border: "1px solid #ddd", borderRadius: 16, padding: 24 }}>
        <h2>API routes for this node</h2>
        <ul style={{ lineHeight: 2 }}>
          {apiRoutes.map((route) => (
            <li key={route}><code>{route}</code></li>
          ))}
        </ul>
      </section>
    </main>
  );
}
