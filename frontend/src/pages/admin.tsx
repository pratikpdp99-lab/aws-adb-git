import { useEffect, useState, FormEvent } from "react";
import type { User, MaskingPolicy, MaskingStrategy } from "../types";
import { MaskedBadge, PiiBadge } from "../components/Badge";
import { fetchPolicies, upsertPolicy, deletePolicy } from "../lib/api";
import { MOCK_DOMAINS } from "../lib/mock";
import {
  ShieldCheck, Plus, Pencil, Trash2, Save, X, AlertTriangle,
} from "lucide-react";

interface Props { user: User }

const STRATEGIES: MaskingStrategy[] = ["HASH", "REDACT", "NULLIFY", "PARTIAL"];
const STRATEGY_DESC: Record<MaskingStrategy, string> = {
  HASH:    "SHA-256 tokenization — reversible with salt",
  REDACT:  "Replace with fixed placeholder (e.g. [REDACTED])",
  NULLIFY: "Set field to NULL",
  PARTIAL: "Mask middle portion (e.g. ***-**-1234)",
};

export default function AdminPage({ user }: Props) {
  const [policies, setPolicies] = useState<MaskingPolicy[]>([]);
  const [loading, setLoading]   = useState(true);
  const [editDomain, setEditDomain] = useState<string | null>(null);
  const [saving, setSaving]         = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);

  // Edit form state
  const [rules, setRules] = useState<{ field: string; strategy: MaskingStrategy }[]>([]);
  const [createdBy, setCreatedBy] = useState(user.email);

  useEffect(() => {
    fetchPolicies().then((p) => { setPolicies(p); setLoading(false); });
  }, []);

  function openEdit(domain: string) {
    const existing = policies.find((p) => p.domain === domain);
    setRules(existing?.rules.map((r) => ({ ...r })) ?? []);
    setCreatedBy(user.email);
    setEditDomain(domain);
  }

  function addRule() {
    const domainDef = MOCK_DOMAINS.find((d) => d.name === editDomain);
    const piiFields = domainDef?.pii_fields ?? [];
    const usedFields = new Set(rules.map((r) => r.field));
    const nextField = piiFields.find((f) => !usedFields.has(f));
    if (nextField) setRules((prev) => [...prev, { field: nextField, strategy: "HASH" }]);
  }

  function removeRule(i: number) {
    setRules((prev) => prev.filter((_, idx) => idx !== i));
  }

  function updateRule(i: number, key: "field" | "strategy", value: string) {
    setRules((prev) => prev.map((r, idx) =>
      idx === i ? { ...r, [key]: value } : r
    ));
  }

  async function handleSave(e: FormEvent) {
    e.preventDefault();
    if (!editDomain) return;
    setSaving(true);
    const updated = await upsertPolicy({ domain: editDomain, rules, created_by: createdBy });
    setPolicies((prev) => {
      const idx = prev.findIndex((p) => p.domain === editDomain);
      if (idx >= 0) return prev.map((p, i) => i === idx ? updated : p);
      return [...prev, updated];
    });
    setSaving(false);
    setEditDomain(null);
  }

  async function handleDelete(domain: string) {
    await deletePolicy(domain);
    setPolicies((prev) => prev.filter((p) => p.domain !== domain));
    setDeleteTarget(null);
  }

  const domainsWithPolicies = new Set(policies.map((p) => p.domain));
  const domainsWithoutPolicies = MOCK_DOMAINS.filter(
    (d) => d.pii_fields.length > 0 && !domainsWithPolicies.has(d.name)
  );

  if (user.role !== "admin") {
    return (
      <div className="max-w-2xl mx-auto mt-20 text-center">
        <AlertTriangle size={40} className="text-amber-400 mx-auto mb-4" />
        <h2 className="text-lg font-semibold text-slate-800">Admin access required</h2>
        <p className="text-sm text-slate-500 mt-1">
          Only admins can manage masking policies.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Masking Policies</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Define per-domain field masking rules applied during Silver layer transforms
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <ShieldCheck size={14} className="text-brand-500" />
          {policies.length} active policies
        </div>
      </div>

      {/* Missing policy warnings */}
      {domainsWithoutPolicies.length > 0 && (
        <div className="flex items-start gap-3 p-4 bg-amber-50 border border-amber-200 rounded-xl">
          <AlertTriangle size={16} className="text-amber-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-amber-800">Domains without masking policies</p>
            <p className="text-xs text-amber-600 mt-0.5">
              These domains have PII fields but no active masking policy:{" "}
              {domainsWithoutPolicies.map((d) => (
                <button key={d.name}
                  onClick={() => openEdit(d.name)}
                  className="font-semibold underline hover:text-amber-800 capitalize mr-2">
                  {d.name}
                </button>
              ))}
            </p>
          </div>
        </div>
      )}

      {/* Policy cards */}
      <div className="space-y-4">
        {loading ? (
          Array.from({ length: 2 }).map((_, i) => (
            <div key={i} className="card p-5 animate-pulse">
              <div className="h-4 bg-slate-100 rounded w-32 mb-3" />
              <div className="h-3 bg-slate-100 rounded w-64" />
            </div>
          ))
        ) : policies.map((policy) => {
          const domainDef = MOCK_DOMAINS.find((d) => d.name === policy.domain);
          return (
            <div key={policy.domain} className="card overflow-hidden">
              {/* Policy header */}
              <div className="px-5 py-4 flex items-center justify-between border-b border-slate-100">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 bg-rose-100 rounded-lg flex items-center justify-center">
                    <ShieldCheck size={17} className="text-rose-500" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-sm font-semibold text-slate-900 capitalize">{policy.domain}</h3>
                      <span className="text-xs text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
                        v{policy.version}
                      </span>
                      {domainDef?.pii_fields && <PiiBadge />}
                    </div>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Updated by {policy.created_by} · {policy.rules.length} rules
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button onClick={() => openEdit(policy.domain)} className="btn-secondary py-1.5 px-3">
                    <Pencil size={13} /> Edit
                  </button>
                  <button onClick={() => setDeleteTarget(policy.domain)} className="btn-danger py-1.5 px-3">
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>

              {/* Rules table */}
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-50 border-b border-slate-100">
                    <tr>
                      <th className="th">Field</th>
                      <th className="th">Strategy</th>
                      <th className="th">Description</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {policy.rules.map((rule) => (
                      <tr key={rule.field} className="hover:bg-slate-50">
                        <td className="td font-mono text-xs font-medium">
                          <div className="flex items-center gap-2">
                            {rule.field}
                            <PiiBadge />
                          </div>
                        </td>
                        <td className="td"><MaskedBadge strategy={rule.strategy} /></td>
                        <td className="td text-xs text-slate-400">
                          {STRATEGY_DESC[rule.strategy as MaskingStrategy] ?? "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          );
        })}
      </div>

      {/* Add policy for domains without one */}
      {domainsWithoutPolicies.length > 0 && (
        <div className="card p-5 border-dashed border-slate-300">
          <h3 className="text-sm font-semibold text-slate-700 mb-3">Add policy for domain</h3>
          <div className="flex flex-wrap gap-2">
            {domainsWithoutPolicies.map((d) => (
              <button key={d.name} onClick={() => openEdit(d.name)}
                className="btn-secondary capitalize">
                <Plus size={14} /> {d.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Edit modal */}
      {editDomain && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-xl max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between sticky top-0 bg-white z-10">
              <div>
                <h2 className="text-base font-semibold text-slate-900 capitalize">
                  {editDomain} masking policy
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Define which fields to mask and how
                </p>
              </div>
              <button onClick={() => setEditDomain(null)} className="text-slate-400 hover:text-slate-600">
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleSave} className="px-6 py-5 space-y-5">
              {/* Rules */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <label className="label mb-0">Masking rules</label>
                  <button type="button" onClick={addRule} className="btn-secondary py-1 px-3 text-xs">
                    <Plus size={12} /> Add rule
                  </button>
                </div>
                {rules.length === 0 ? (
                  <div className="text-center py-8 text-sm text-slate-400 bg-slate-50 rounded-xl">
                    No rules defined. Add a rule to configure masking.
                  </div>
                ) : (
                  <div className="space-y-2">
                    {rules.map((rule, i) => {
                      const domainDef = MOCK_DOMAINS.find((d) => d.name === editDomain);
                      const fieldOptions = domainDef?.fields.map((f) => f.name) ?? [];
                      return (
                        <div key={i} className="flex items-center gap-2 p-3 bg-slate-50 rounded-xl">
                          <select className="select flex-1 text-xs"
                            value={rule.field}
                            onChange={(e) => updateRule(i, "field", e.target.value)}>
                            {fieldOptions.map((f) => (
                              <option key={f} value={f}>{f}</option>
                            ))}
                          </select>
                          <select className="select flex-1 text-xs"
                            value={rule.strategy}
                            onChange={(e) => updateRule(i, "strategy", e.target.value as MaskingStrategy)}>
                            {STRATEGIES.map((s) => <option key={s} value={s}>{s}</option>)}
                          </select>
                          <button type="button" onClick={() => removeRule(i)}
                            className="text-slate-400 hover:text-red-500 flex-shrink-0">
                            <X size={14} />
                          </button>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              <div>
                <label className="label">Updated by</label>
                <input className="input" value={createdBy}
                  onChange={(e) => setCreatedBy(e.target.value)} />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button type="button" onClick={() => setEditDomain(null)} className="btn-secondary">
                  Cancel
                </button>
                <button type="submit" disabled={saving} className="btn-primary">
                  <Save size={15} /> {saving ? "Saving…" : "Save Policy"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete confirm modal */}
      {deleteTarget && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6">
            <div className="text-center mb-5">
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Trash2 size={20} className="text-red-500" />
              </div>
              <h3 className="font-semibold text-slate-900">Delete policy?</h3>
              <p className="text-sm text-slate-500 mt-1">
                This will remove the masking policy for{" "}
                <strong className="capitalize">{deleteTarget}</strong>. This action cannot be undone.
              </p>
            </div>
            <div className="flex gap-3">
              <button onClick={() => setDeleteTarget(null)} className="btn-secondary flex-1 justify-center">
                Cancel
              </button>
              <button onClick={() => handleDelete(deleteTarget)} className="btn-danger flex-1 justify-center">
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
