import { useEffect, useState } from "react";
import type { User, Domain } from "../types";
import Badge, { PiiBadge, EnvBadge } from "../components/Badge";
import { fetchDomains } from "../lib/api";
import {
  Database, ChevronDown, ChevronRight, Search, Lock,
} from "lucide-react";

interface Props { user: User }

const TYPE_COLORS: Record<string, string> = {
  string: "text-sky-600 bg-sky-50",   date:      "text-violet-600 bg-violet-50",
  double: "text-amber-600 bg-amber-50", integer:  "text-emerald-600 bg-emerald-50",
  boolean: "text-rose-600 bg-rose-50", timestamp: "text-indigo-600 bg-indigo-50",
};

export default function CatalogPage({ user: _user }: Props) {
  const [domains, setDomains]     = useState<Domain[]>([]);
  const [loading, setLoading]     = useState(true);
  const [search, setSearch]       = useState("");
  const [expanded, setExpanded]   = useState<Set<string>>(new Set(["customer"]));
  const [filterPii, setFilterPii] = useState<boolean | null>(null);

  useEffect(() => {
    fetchDomains().then((d) => { setDomains(d); setLoading(false); });
  }, []);

  function toggle(name: string) {
    setExpanded((prev) => {
      const next = new Set(prev);
      next.has(name) ? next.delete(name) : next.add(name);
      return next;
    });
  }

  const filtered = domains.filter((d) => {
    if (search && !d.name.includes(search.toLowerCase()) &&
        !d.description.toLowerCase().includes(search.toLowerCase())) return false;
    if (filterPii !== null && Boolean(d.pii_fields.length) !== filterPii) return false;
    return true;
  });

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900">Data Catalog</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Browse retail data domains, schemas, and PII classifications
        </p>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 min-w-48 max-w-72">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input className="input pl-9" placeholder="Search domains…"
            value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        <div className="flex gap-1">
          {[
            { label: "All domains", value: null },
            { label: "Has PII",     value: true  },
            { label: "No PII",      value: false },
          ].map((opt) => (
            <button key={String(opt.label)}
              onClick={() => setFilterPii(opt.value)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                filterPii === opt.value
                  ? "bg-brand-600 text-white border-brand-600"
                  : "bg-white text-slate-600 border-slate-200 hover:bg-slate-50"}`}>
              {opt.label}
            </button>
          ))}
        </div>
        <span className="text-xs text-slate-400">{filtered.length} domains</span>
      </div>

      {/* Domain cards */}
      <div className="space-y-3">
        {loading ? (
          Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="card p-5 animate-pulse">
              <div className="h-4 bg-slate-100 rounded w-32 mb-2" />
              <div className="h-3 bg-slate-100 rounded w-64" />
            </div>
          ))
        ) : filtered.map((domain) => {
          const isOpen = expanded.has(domain.name);
          const hasPii = domain.pii_fields.length > 0;

          return (
            <div key={domain.name} className="card overflow-hidden">
              {/* Header */}
              <button
                onClick={() => toggle(domain.name)}
                className="w-full px-5 py-4 flex items-center justify-between hover:bg-slate-50
                  transition-colors text-left">
                <div className="flex items-center gap-4 min-w-0">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                    hasPii ? "bg-rose-100" : "bg-emerald-100"}`}>
                    {hasPii
                      ? <Lock size={18} className="text-rose-500" />
                      : <Database size={18} className="text-emerald-500" />}
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className="text-sm font-semibold text-slate-900 capitalize">{domain.name}</h3>
                      {hasPii && <PiiBadge />}
                      {domain.supported_environments.map((env) => (
                        <EnvBadge key={env} env={env} />
                      ))}
                    </div>
                    <p className="text-xs text-slate-400 mt-0.5 truncate">{domain.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4 flex-shrink-0 ml-4">
                  <div className="text-right hidden sm:block">
                    <p className="text-sm font-semibold text-slate-800">
                      {domain.estimated_row_count.toLocaleString()}
                    </p>
                    <p className="text-[10px] text-slate-400">est. rows</p>
                  </div>
                  <div className="text-right hidden sm:block">
                    <p className="text-sm font-semibold text-slate-800">{domain.fields.length}</p>
                    <p className="text-[10px] text-slate-400">columns</p>
                  </div>
                  {isOpen
                    ? <ChevronDown size={16} className="text-slate-400" />
                    : <ChevronRight size={16} className="text-slate-400" />
                  }
                </div>
              </button>

              {/* Expanded schema */}
              {isOpen && (
                <div className="border-t border-slate-100">
                  {/* PII summary */}
                  {hasPii && (
                    <div className="px-5 py-3 bg-rose-50 border-b border-rose-100 flex flex-wrap gap-2">
                      <span className="text-xs text-rose-600 font-medium">PII fields requiring masking:</span>
                      {domain.pii_fields.map((f) => (
                        <Badge key={f} label={f} variant="error" />
                      ))}
                    </div>
                  )}

                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-slate-50 border-b border-slate-100">
                        <tr>
                          <th className="th">Column</th>
                          <th className="th">Type</th>
                          <th className="th">PII</th>
                          <th className="th">Nullable</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-50">
                        {domain.fields.map((field) => (
                          <tr key={field.name}
                            className={`hover:bg-slate-50 transition-colors ${
                              field.pii ? "bg-rose-50/30" : ""}`}>
                            <td className="td font-mono text-xs font-medium text-slate-700">
                              <div className="flex items-center gap-2">
                                {field.name}
                                {field.pii && <PiiBadge />}
                              </div>
                            </td>
                            <td className="td">
                              <span className={`text-[11px] font-semibold px-1.5 py-0.5 rounded
                                ${TYPE_COLORS[field.type] ?? "text-slate-600 bg-slate-100"}`}>
                                {field.type}
                              </span>
                            </td>
                            <td className="td">
                              {field.pii
                                ? <span className="text-rose-500 text-xs font-semibold">Yes</span>
                                : <span className="text-slate-300 text-xs">No</span>}
                            </td>
                            <td className="td">
                              {field.nullable
                                ? <span className="text-slate-400 text-xs">nullable</span>
                                : <span className="text-slate-700 text-xs font-medium">required</span>}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Unity Catalog path */}
                  <div className="px-5 py-3 border-t border-slate-100 bg-slate-50">
                    <p className="text-xs text-slate-400 font-mono">
                      tdm_catalog.tdm_dev.silver_{domain.name}
                      <span className="ml-2 text-slate-300">·</span>
                      <span className="ml-2">tdm_catalog.tdm_dev.bronze_{domain.name}</span>
                    </p>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
