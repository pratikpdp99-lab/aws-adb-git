import { useEffect, useState } from "react";
import type { User, TableLineage } from "../types";
import LineageGraph from "../components/LineageGraph";
import { fetchLineage } from "../lib/api";
import { Network, RefreshCw } from "lucide-react";

interface Props { user: User }

const DOMAINS = ["customer", "order", "product", "inventory", "loyalty"];

export default function LineagePage({ user: _user }: Props) {
  const [domain, setDomain]       = useState("customer");
  const [lineage, setLineage]     = useState<TableLineage | null>(null);
  const [loading, setLoading]     = useState(true);

  function load(d: string) {
    setLoading(true);
    fetchLineage(d).then((l) => { setLineage(l); setLoading(false); });
  }

  useEffect(() => { load(domain); }, [domain]);

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Data Lineage</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Pipeline flow and column-level PII provenance
          </p>
        </div>
        <button onClick={() => load(domain)} className="btn-secondary">
          <RefreshCw size={15} className={loading ? "animate-spin" : ""} />
          Refresh
        </button>
      </div>

      {/* Domain picker */}
      <div className="card p-4">
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-2 text-sm text-slate-500 mr-2">
            <Network size={16} />
            <span className="font-medium">Select domain:</span>
          </div>
          {DOMAINS.map((d) => (
            <button key={d}
              onClick={() => setDomain(d)}
              className={`px-4 py-2 rounded-lg text-sm font-medium capitalize transition-all ${
                domain === d
                  ? "bg-brand-600 text-white shadow-sm"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"}`}>
              {d}
            </button>
          ))}
        </div>
      </div>

      {/* Lineage content */}
      {loading ? (
        <div className="card p-12 text-center">
          <RefreshCw size={24} className="animate-spin mx-auto mb-3 text-slate-300" />
          <p className="text-sm text-slate-400">Loading lineage for <strong>{domain}</strong>…</p>
        </div>
      ) : lineage ? (
        <>
          {/* Table header */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-brand-100 rounded-lg flex items-center justify-center">
              <Network size={16} className="text-brand-600" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-slate-900 capitalize">{domain} pipeline</h2>
              <p className="text-xs text-slate-400">
                S3 raw → Bronze Delta → Silver masked · Unity Catalog: tdm_catalog.tdm_dev
              </p>
            </div>
          </div>
          <LineageGraph lineage={lineage} />
        </>
      ) : (
        <div className="card p-12 text-center text-sm text-slate-400">
          No lineage data available.
        </div>
      )}
    </div>
  );
}
