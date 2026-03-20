import type { Dataset } from "../types";
import { EnvBadge } from "./Badge";
import { Database, Shield, ShieldOff } from "lucide-react";

export default function DatasetCard({ dataset }: { dataset: Dataset }) {
  return (
    <div className="card p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3">
        <div className="w-9 h-9 bg-brand-50 rounded-lg flex items-center justify-center flex-shrink-0">
          <Database size={17} className="text-brand-600" />
        </div>
        <div className="min-w-0">
          <p className="text-sm font-semibold text-slate-800 truncate">{dataset.name}</p>
          <div className="flex items-center gap-2 mt-1 flex-wrap">
            <span className="text-xs text-slate-500 capitalize">{dataset.domain}</span>
            <EnvBadge env={dataset.environment} />
          </div>
        </div>
      </div>
      <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
        <span>{dataset.row_count.toLocaleString()} rows</span>
        <span className="flex items-center gap-1">
          {dataset.masking_applied
            ? <><Shield size={12} className="text-emerald-500" /> Masked</>
            : <><ShieldOff size={12} className="text-slate-300" /> Plain</>}
        </span>
      </div>
    </div>
  );
}
