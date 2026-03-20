import { useEffect, useState, FormEvent } from "react";
import type { User, DataRequest } from "../types";
import { RequestStatusBadge, EnvBadge } from "../components/Badge";
import { fetchRequests, createRequest } from "../lib/api";
import { MOCK_DOMAINS } from "../lib/mock";
import { Plus, ChevronRight, CheckCircle, Clock } from "lucide-react";

interface Props { user: User }

const STEPS = ["Domain", "Environment", "Configuration", "Review"];

function fmtDate(iso: string) {
  return new Date(iso).toLocaleString("en-US", {
    month: "short", day: "numeric", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

export default function RequestsPage({ user }: Props) {
  const [requests, setRequests] = useState<DataRequest[]>([]);
  const [loading, setLoading]   = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [step, setStep]         = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted]   = useState<DataRequest | null>(null);

  const [domain, setDomain]       = useState("customer");
  const [environment, setEnv]     = useState("dev");
  const [rowCount, setRowCount]   = useState(10000);
  const [purpose, setPurpose]     = useState("");
  const [requester, setRequester] = useState(user.email);

  useEffect(() => {
    fetchRequests().then((r) => { setRequests(r); setLoading(false); });
  }, []);

  const selectedDomain = MOCK_DOMAINS.find((d) => d.name === domain);

  function resetForm() {
    setStep(0); setDomain("customer"); setEnv("dev");
    setRowCount(10000); setPurpose(""); setSubmitted(null);
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    const req = await createRequest({
      domain, environment, row_count: rowCount, requester, purpose,
    });
    setRequests((prev) => [req, ...prev]);
    setSubmitted(req);
    setSubmitting(false);
    setShowForm(false);
    resetForm();
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Data Requests</h1>
          <p className="text-sm text-slate-500 mt-0.5">Request test datasets for your environment</p>
        </div>
        <button onClick={() => { setShowForm(true); resetForm(); }} className="btn-primary">
          <Plus size={16} /> New Request
        </button>
      </div>

      {submitted && (
        <div className="flex items-center gap-3 p-4 bg-emerald-50 border border-emerald-200
          rounded-xl text-sm text-emerald-700">
          <CheckCircle size={18} />
          <div>
            <strong>Request submitted: {submitted.id}</strong>
            <p className="text-emerald-600 text-xs mt-0.5">
              {submitted.domain} / {submitted.environment} · {submitted.row_count.toLocaleString()} rows
            </p>
          </div>
          <button onClick={() => setSubmitted(null)} className="ml-auto text-emerald-400
            hover:text-emerald-600">✕</button>
        </div>
      )}

      {showForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg">
            <div className="px-6 py-5 border-b border-slate-100">
              <h2 className="text-base font-semibold text-slate-900">New Data Request</h2>
              <div className="flex items-center gap-1 mt-3">
                {STEPS.map((s, i) => (
                  <div key={s} className="flex items-center gap-1">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs
                      font-semibold transition-colors ${
                        i < step  ? "bg-brand-600 text-white" :
                        i === step ? "bg-brand-100 text-brand-700 ring-2 ring-brand-300" :
                                    "bg-slate-100 text-slate-400"}`}>
                      {i < step ? "✓" : i + 1}
                    </div>
                    <span className={`text-xs ${i === step ? "text-brand-700 font-medium" : "text-slate-400"}`}>
                      {s}
                    </span>
                    {i < STEPS.length - 1 && <ChevronRight size={12} className="text-slate-300 mx-1" />}
                  </div>
                ))}
              </div>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="px-6 py-5 space-y-4">
                {step === 0 && (
                  <div className="space-y-2">
                    <label className="label">Select data domain</label>
                    {MOCK_DOMAINS.map((d) => (
                      <button key={d.name} type="button"
                        onClick={() => setDomain(d.name)}
                        className={`flex items-start gap-3 p-3 rounded-xl border-2 w-full text-left
                          transition-all ${domain === d.name
                            ? "border-brand-500 bg-brand-50"
                            : "border-slate-200 hover:border-slate-300"}`}>
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center
                          text-xs font-bold flex-shrink-0 ${domain === d.name
                            ? "bg-brand-600 text-white" : "bg-slate-100 text-slate-600"}`}>
                          {d.name.charAt(0).toUpperCase()}
                        </div>
                        <div className="min-w-0">
                          <p className={`text-sm font-semibold capitalize ${
                            domain === d.name ? "text-brand-700" : "text-slate-800"}`}>
                            {d.name}
                          </p>
                          <p className="text-xs text-slate-400 truncate">{d.description}</p>
                          {d.pii_fields.length > 0 && (
                            <p className="text-[10px] text-rose-500 mt-0.5">
                              {d.pii_fields.length} PII fields · masking required
                            </p>
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                )}

                {step === 1 && (
                  <div className="space-y-3">
                    <label className="label">Target environment</label>
                    <div className="grid grid-cols-3 gap-3">
                      {(selectedDomain?.supported_environments ?? ["dev"]).map((env) => (
                        <button key={env} type="button"
                          onClick={() => setEnv(env)}
                          className={`p-4 rounded-xl border-2 text-center transition-all ${
                            environment === env
                              ? "border-brand-500 bg-brand-50"
                              : "border-slate-200 hover:border-slate-300"}`}>
                          <p className={`text-sm font-semibold capitalize ${
                            environment === env ? "text-brand-700" : "text-slate-700"}`}>{env}</p>
                          {env === "prod" && (
                            <p className="text-[10px] text-rose-400 mt-1">Restricted</p>
                          )}
                        </button>
                      ))}
                    </div>
                    {environment === "prod" && (
                      <p className="text-xs text-rose-600 bg-rose-50 px-3 py-2 rounded-lg
                        border border-rose-200">
                        Production datasets require admin approval and full PII masking.
                      </p>
                    )}
                  </div>
                )}

                {step === 2 && (
                  <div className="space-y-4">
                    <div>
                      <label className="label">Row count</label>
                      <input type="number" className="input" min={100} max={1000000}
                        value={rowCount} onChange={(e) => setRowCount(Number(e.target.value))} />
                      <p className="text-xs text-slate-400 mt-1">
                        Estimated source: {(selectedDomain?.estimated_row_count ?? 0).toLocaleString()} rows
                      </p>
                    </div>
                    <div>
                      <label className="label">Requester email</label>
                      <input type="email" className="input" value={requester}
                        onChange={(e) => setRequester(e.target.value)} />
                    </div>
                    <div>
                      <label className="label">Purpose / ticket reference</label>
                      <textarea className="input resize-none" rows={3}
                        placeholder="e.g. JIRA-1234 — Integration test suite for checkout flow"
                        value={purpose} onChange={(e) => setPurpose(e.target.value)} />
                    </div>
                  </div>
                )}

                {step === 3 && (
                  <div className="space-y-3">
                    <p className="text-sm text-slate-600">Review your request before submitting.</p>
                    <div className="bg-slate-50 rounded-xl p-4 space-y-2 text-sm">
                      {([
                        ["Domain",      domain],
                        ["Environment", environment],
                        ["Row count",   rowCount.toLocaleString()],
                        ["Requester",   requester],
                        ["Purpose",     purpose || "—"],
                      ] as [string, string][]).map(([k, v]) => (
                        <div key={k} className="flex justify-between">
                          <span className="text-slate-500">{k}</span>
                          <span className="font-medium text-slate-800 text-right max-w-xs truncate">{v}</span>
                        </div>
                      ))}
                    </div>
                    {(selectedDomain?.pii_fields.length ?? 0) > 0 && (
                      <p className="text-xs bg-amber-50 border border-amber-200 text-amber-700
                        px-3 py-2 rounded-lg">
                        Masking will be applied to: {selectedDomain?.pii_fields.join(", ")}
                      </p>
                    )}
                  </div>
                )}
              </div>

              <div className="px-6 py-4 border-t border-slate-100 flex justify-between">
                <button type="button" onClick={() => { setShowForm(false); resetForm(); }}
                  className="btn-secondary">Cancel</button>
                <div className="flex gap-2">
                  {step > 0 && (
                    <button type="button" onClick={() => setStep((s) => s - 1)}
                      className="btn-secondary">Back</button>
                  )}
                  {step < STEPS.length - 1 ? (
                    <button type="button" onClick={() => setStep((s) => s + 1)}
                      className="btn-primary">
                      Next <ChevronRight size={14} />
                    </button>
                  ) : (
                    <button type="submit" disabled={submitting} className="btn-primary">
                      {submitting ? "Submitting…" : "Submit Request"}
                    </button>
                  )}
                </div>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="card overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-800">All Requests</h2>
          <span className="text-xs text-slate-400">{requests.length} total</span>
        </div>
        <div className="overflow-x-auto">
          {loading ? (
            <div className="px-5 py-12 text-center text-sm text-slate-400">Loading…</div>
          ) : (
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-100">
                <tr>
                  <th className="th">ID</th>
                  <th className="th">Domain</th>
                  <th className="th">Env</th>
                  <th className="th">Rows</th>
                  <th className="th">Purpose</th>
                  <th className="th">Requester</th>
                  <th className="th">Status</th>
                  <th className="th">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {requests.map((req) => (
                  <tr key={req.id} className="hover:bg-slate-50 transition-colors">
                    <td className="td font-mono text-xs text-slate-500">{req.id}</td>
                    <td className="td capitalize font-medium">{req.domain}</td>
                    <td className="td"><EnvBadge env={req.environment} /></td>
                    <td className="td">{req.row_count.toLocaleString()}</td>
                    <td className="td text-slate-500 max-w-xs truncate">{req.purpose ?? "—"}</td>
                    <td className="td text-slate-500 text-xs">{req.requester}</td>
                    <td className="td"><RequestStatusBadge status={req.status} /></td>
                    <td className="td text-slate-400 text-xs whitespace-nowrap">
                      <span className="flex items-center gap-1"><Clock size={11} />{fmtDate(req.created_at)}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
