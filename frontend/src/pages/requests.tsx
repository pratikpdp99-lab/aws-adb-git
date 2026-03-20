import { useState } from "react";

const DOMAINS = ["customer", "order", "product", "inventory", "loyalty"];
const ENVIRONMENTS = ["dev", "staging"];

export default function RequestsPage() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const [form, setForm] = useState({
    requester: "",
    domain: "customer",
    environment: "dev",
    row_count: 1000,
  });
  const [submitted, setSubmitted] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const r = await fetch(`${apiUrl}/requests/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    const data = await r.json();
    setSubmitted(data.id);
  };

  return (
    <main style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>Request Test Data</h1>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem", maxWidth: 400 }}>
        <label>
          Requester
          <input value={form.requester} onChange={(e) => setForm({ ...form, requester: e.target.value })} required />
        </label>
        <label>
          Domain
          <select value={form.domain} onChange={(e) => setForm({ ...form, domain: e.target.value })}>
            {DOMAINS.map((d) => <option key={d}>{d}</option>)}
          </select>
        </label>
        <label>
          Environment
          <select value={form.environment} onChange={(e) => setForm({ ...form, environment: e.target.value })}>
            {ENVIRONMENTS.map((e) => <option key={e}>{e}</option>)}
          </select>
        </label>
        <label>
          Row Count
          <input type="number" value={form.row_count} onChange={(e) => setForm({ ...form, row_count: Number(e.target.value) })} />
        </label>
        <button type="submit">Submit Request</button>
      </form>
      {submitted && <p>Request submitted: <strong>{submitted}</strong></p>}
    </main>
  );
}
