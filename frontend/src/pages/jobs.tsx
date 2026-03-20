import { useEffect, useState } from "react";
import type { User, JobRun, JobStatus } from "../types";
import { JobStatusBadge } from "../components/Badge";
import { fetchJobs } from "../lib/api";
import {
  RefreshCw, Clock, Zap, AlertCircle, CheckCircle,
  Play, Filter,
} from "lucide-react";

interface Props { user: User }

function duration(start?: string, end?: string): string {
  if (!start) return "—";
  const endMs = end ? new Date(end).getTime() : Date.now();
  const s = (endMs - new Date(start).getTime()) / 1000;
  if (s < 60) return `${Math.round(s)}s`;
  return `${Math.floor(s / 60)}m ${Math.round(s % 60)}s`;
}

function fmtTime(iso?: string) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("en-US", {
    month: "short", day: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

const STATUS_OPTIONS: { label: string; value: JobStatus | "ALL" }[] = [
  { label: "All",     value: "ALL"     },
  { label: "Running", value: "RUNNING" },
  { label: "Success", value: "SUCCESS" },
  { label: "Failed",  value: "FAILED"  },
  { label: "Pending", value: "PENDING" },
];

export default function JobsPage({ user: _user }: Props) {
  const [jobs, setJobs]       = useState<JobRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter]   = useState<JobStatus | "ALL">("ALL");

  function load() {
    setLoading(true);
    fetchJobs().then((j) => { setJobs(j); setLoading(false); });
  }

  useEffect(() => { load(); }, []);

  const displayed = filter === "ALL" ? jobs : jobs.filter((j) => j.status === filter);
  const counts    = {
    running: jobs.filter((j) => j.status === "RUNNING").length,
    success: jobs.filter((j) => j.status === "SUCCESS").length,
    failed:  jobs.filter((j) => j.status === "FAILED").length,
    pending: jobs.filter((j) => j.status === "PENDING").length,
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Job Runs</h1>
          <p className="text-sm text-slate-500 mt-0.5">Databricks pipeline execution history</p>
        </div>
        <button onClick={load} className="btn-secondary">
          <RefreshCw size={15} className={loading ? "animate-spin" : ""} />
          Refresh
        </button>
      </div>

      {/* Summary chips */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: "Running", count: counts.running, icon: <Play size={16} />,         color: "text-blue-600  bg-blue-50  border-blue-200"  },
          { label: "Success", count: counts.success, icon: <CheckCircle size={16} />,  color: "text-emerald-600 bg-emerald-50 border-emerald-200" },
          { label: "Failed",  count: counts.failed,  icon: <AlertCircle size={16} />,  color: "text-red-600   bg-red-50   border-red-200"   },
          { label: "Pending", count: counts.pending, icon: <Clock size={16} />,        color: "text-amber-600 bg-amber-50  border-amber-200" },
        ].map(({ label, count, icon, color }) => (
          <button key={label}
            onClick={() => setFilter(label.toUpperCase() as JobStatus)}
            className={`card p-4 flex items-center gap-3 cursor-pointer border-2
              hover:shadow-md transition-all text-left
              ${filter === label.toUpperCase() ? "ring-2 ring-brand-400 border-brand-200" : ""}`}>
            <div className={`p-2 rounded-lg border ${color}`}>{icon}</div>
            <div>
              <p className="text-xl font-bold text-slate-900">{count}</p>
              <p className="text-xs text-slate-500">{label}</p>
            </div>
          </button>
        ))}
      </div>

      {/* Filter bar */}
      <div className="flex items-center gap-2">
        <Filter size={15} className="text-slate-400" />
        <div className="flex gap-1">
          {STATUS_OPTIONS.map((opt) => (
            <button key={opt.value}
              onClick={() => setFilter(opt.value)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                filter === opt.value
                  ? "bg-brand-600 text-white"
                  : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"}`}>
              {opt.label}
            </button>
          ))}
        </div>
        <span className="text-xs text-slate-400 ml-2">{displayed.length} runs</span>
      </div>

      {/* Jobs table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          {loading ? (
            <div className="px-5 py-12 text-center text-sm text-slate-400">
              <RefreshCw size={20} className="animate-spin mx-auto mb-2 text-slate-300" />
              Loading job runs…
            </div>
          ) : displayed.length === 0 ? (
            <div className="px-5 py-12 text-center text-sm text-slate-400">No jobs match the filter.</div>
          ) : (
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-100">
                <tr>
                  <th className="th">Run ID</th>
                  <th className="th">Job Name</th>
                  <th className="th">Status</th>
                  <th className="th">Trigger</th>
                  <th className="th">Started</th>
                  <th className="th">Duration</th>
                  <th className="th">Pipeline Run</th>
                  <th className="th">Error</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {displayed.map((job) => (
                  <tr key={job.run_id} className="hover:bg-slate-50 transition-colors">
                    <td className="td font-mono text-xs text-slate-500">#{job.run_id}</td>
                    <td className="td">
                      <div className="flex items-center gap-2">
                        <Zap size={13} className="text-brand-400 flex-shrink-0" />
                        <span className="font-medium text-sm">{job.job_name}</span>
                      </div>
                    </td>
                    <td className="td"><JobStatusBadge status={job.status} /></td>
                    <td className="td">
                      <span className={`text-xs px-2 py-0.5 rounded-md font-medium ${
                        job.trigger === "SCHEDULE" ? "bg-violet-100 text-violet-700" :
                        job.trigger === "API"      ? "bg-sky-100    text-sky-700"    :
                                                    "bg-slate-100  text-slate-600"}`}>
                        {job.trigger}
                      </span>
                    </td>
                    <td className="td text-xs text-slate-400 whitespace-nowrap">
                      <span className="flex items-center gap-1">
                        <Clock size={11} />{fmtTime(job.start_time)}
                      </span>
                    </td>
                    <td className="td text-xs text-slate-500 font-mono">
                      {duration(job.start_time, job.end_time)}
                    </td>
                    <td className="td font-mono text-xs text-slate-400">
                      {job.pipeline_run_id ?? "—"}
                    </td>
                    <td className="td">
                      {job.error_message ? (
                        <span className="text-xs text-red-500 flex items-center gap-1">
                          <AlertCircle size={12} />
                          <span className="truncate max-w-xs" title={job.error_message}>
                            {job.error_message}
                          </span>
                        </span>
                      ) : <span className="text-slate-200">—</span>}
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
