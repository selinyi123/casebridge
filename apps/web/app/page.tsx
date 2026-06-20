const demoSteps = [
  "Client profile",
  "Visit note",
  "AI draft analysis",
  "Missing info reminders",
  "Resource matching",
  "Service plan",
  "Referral status",
  "Supervision review",
  "Outcome tracking",
];

export default function Home() {
  return (
    <main style={{ maxWidth: 960, margin: "0 auto", padding: 32, fontFamily: "system-ui, sans-serif" }}>
      <section style={{ marginBottom: 32 }}>
        <p style={{ fontSize: 14, color: "#666" }}>CaseBridge v0.1.1-foundation-build</p>
        <h1 style={{ fontSize: 40, margin: "8px 0" }}>CaseBridge</h1>
        <p style={{ fontSize: 18, lineHeight: 1.7 }}>
          AI-native case service and resource collaboration system for Chinese social-work scenarios.
        </p>
      </section>

      <section style={{ border: "1px solid #ddd", borderRadius: 16, padding: 24, marginBottom: 24 }}>
        <h2>Core rule</h2>
        <p>AI assists. Human confirms. AI output is draft-only until reviewed by a social worker.</p>
      </section>

      <section style={{ border: "1px solid #ddd", borderRadius: 16, padding: 24 }}>
        <h2>C-0001 demo loop</h2>
        <ol style={{ lineHeight: 2 }}>
          {demoSteps.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
      </section>
    </main>
  );
}
