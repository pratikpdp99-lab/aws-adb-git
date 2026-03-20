import type { TableLineage, LineageNode } from "../types";
import { MaskedBadge, PiiBadge } from "./Badge";

const NODE_STYLES: Record<string, { bg: string; border: string; label: string; labelBg: string }> = {
  s3:     { bg: "bg-amber-50",   border: "border-amber-300",  label: "S3 Source",  labelBg: "bg-amber-100  text-amber-700"  },
  bronze: { bg: "bg-sky-50",     border: "border-sky-300",    label: "Bronze",     labelBg: "bg-sky-100    text-sky-700"    },
  silver: { bg: "bg-violet-50",  border: "border-violet-300", label: "Silver",     labelBg: "bg-violet-100 text-violet-700" },
};

function GraphNode({ node, transform }: { node: LineageNode; transform?: string }) {
  const s = NODE_STYLES[node.type] ?? NODE_STYLES.bronze;
  return (
    <div className="flex flex-col items-center">
      {transform && (
        <div className="flex flex-col items-center mb-2 text-slate-400">
          <div className="w-16 border-t-2 border-dashed border-slate-300" />
        </div>
      )}
      <div className={`rounded-xl border-2 ${s.bg} ${s.border} p-4 w-52 shadow-sm`}>
        <span className={`inline-block text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md mb-2 ${s.labelBg}`}>
          {s.label}
        </span>
        <p className="text-sm font-semibold text-slate-800 truncate" title={node.name}>
          {node.name}
        </p>
        {node.location && (
          <p className="text-[11px] text-slate-400 mt-1 truncate" title={node.location}>
            {node.location}
          </p>
        )}
      </div>
    </div>
  );
}

function Arrow({ label }: { label: string }) {
  return (
    <div className="flex flex-col items-center justify-center px-2 pt-6">
      <div className="flex items-center gap-0">
        <div className="h-px w-12 bg-slate-300" />
        <div className="border-t-4 border-b-4 border-l-8 border-transparent border-l-slate-400" />
      </div>
      <span className="text-[10px] text-slate-400 mt-1 font-medium">{label}</span>
    </div>
  );
}

export default function LineageGraph({ lineage }: { lineage: TableLineage }) {
  const nodeMap = Object.fromEntries(lineage.nodes.map((n) => [n.id, n]));
  const piiCount = lineage.columns.filter((c) => c.pii).length;
  const maskedCount = lineage.columns.filter((c) => c.masked).length;

  return (
    <div>
      {/* Flow diagram */}
      <div className="card p-6 mb-6">
        <div className="flex items-start justify-center flex-wrap gap-0">
          {lineage.edges.length === 0 ? (
            <p className="text-slate-400 text-sm">No lineage data available.</p>
          ) : (
            <>
              <GraphNode node={nodeMap[lineage.edges[0].from_node]} />
              {lineage.edges.map((edge, i) => (
                <div key={i} className="flex items-start">
                  <Arrow label={edge.transform} />
                  <GraphNode node={nodeMap[edge.to_node]} />
                </div>
              ))}
            </>
          )}
        </div>

        {/* Pipeline run ID */}
        {lineage.pipeline_run_id && (
          <p className="mt-4 text-center text-xs text-slate-400">
            Pipeline run: <span className="font-mono text-slate-600">{lineage.pipeline_run_id}</span>
          </p>
        )}
      </div>

      {/* Summary chips */}
      <div className="flex gap-3 mb-4 flex-wrap">
        <div className="card px-4 py-2 flex items-center gap-2 text-sm">
          <span className="text-slate-500">Columns:</span>
          <span className="font-semibold text-slate-800">{lineage.columns.length}</span>
        </div>
        <div className="card px-4 py-2 flex items-center gap-2 text-sm">
          <span className="text-slate-500">PII columns:</span>
          <span className="font-semibold text-rose-600">{piiCount}</span>
        </div>
        <div className="card px-4 py-2 flex items-center gap-2 text-sm">
          <span className="text-slate-500">Masked:</span>
          <span className="font-semibold text-violet-600">{maskedCount}</span>
        </div>
      </div>

      {/* Column table */}
      <div className="card overflow-hidden">
        <div className="px-5 py-3 border-b border-slate-100">
          <h3 className="text-sm font-semibold text-slate-800">Column-level PII Provenance</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-100">
              <tr>
                <th className="th">Silver Column</th>
                <th className="th">Source Column</th>
                <th className="th">PII</th>
                <th className="th">Masking</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {lineage.columns.map((col) => (
                <tr key={col.column} className="hover:bg-slate-50 transition-colors">
                  <td className="td font-mono text-xs text-slate-700">{col.column}</td>
                  <td className="td font-mono text-xs text-slate-400">
                    {col.source_column !== col.column ? (
                      <span className="flex items-center gap-1">
                        <span className="line-through text-slate-300">{col.source_column}</span>
                        <span className="text-brand-600">→ renamed</span>
                      </span>
                    ) : col.source_column}
                  </td>
                  <td className="td">{col.pii ? <PiiBadge /> : <span className="text-slate-300 text-xs">—</span>}</td>
                  <td className="td">
                    {col.masked
                      ? <MaskedBadge strategy={col.masking_strategy} />
                      : <span className="text-slate-300 text-xs">—</span>
                    }
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
