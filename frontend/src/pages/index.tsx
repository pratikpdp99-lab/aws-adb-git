import { useEffect, useState } from "react";
import Link from "next/link";
import type { User, JobRun, DataRequest, Dataset } from "../types";
import StatCard from "../components/StatCard";
import { JobStatusBadge, RequestStatusBadge, EnvBadge } from "../components/Badge";
import { fetchJobs, fetchRequests, fetchDatasets } from "../lib/api";
import { MOCK_DOMAINS } from "../lib/mock";
import {
  Database, Briefcase, Inbox, LayoutGrid,
  ArrowUpRight, Clock,
} from "lucide-react";

function fmtTime(iso?: string) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("en-US", {
    month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
  });
}

function duration(start?: string, end?: string): string {
  if (!start || !end) return "—";
  const s = (new Date(end).getTime() - new Date(start).getTime()) / 1000;
  if (s < 60) return `${Math.round(s)}s`;
  return `${Math.floor(s / 60)}m ${Math.round(s % 60)}s`;
}

interface Props { user: User }

export default function Dashboard({ user }: Props) {
  const [jobs, setJobs]         = useState<JobRun[]>([]);
  const [requests, setRequests] = useState<DataRequest[]>([]);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading]   = useState(true);

  useEffect(() => {
    Promise.all([fetchJobs(), fetchRequests(), fetchDatasets()]).then(([j, r, d]) => {
      setJobs(j);
      setRequests(r);
      setDatasets(d);
      setLoading(false);
    });
  }, []);

  const runningJobs  = jobs.filter((j) => j.status === "RUNNING").length;
  const pendingReqs  = requests.filter((r) => r.status === "PENDING").length;
  const failedJobs   = jobs.filter((j) => j.status === "FAILED").length;

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Page heading */}
      <div>
        <h1 className="text-xl font-bold text-slate-900">Dashboard</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Welcome back, {user.name.split(" ")[0]}. Here's what's happening today.
        </p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Datasets"         value={loading ? "…" : datasets.length}  subtitle={`across ${MOCK_DOMAINS.length} domains`} icon={<Database size={20} />}   accent="indigo"  />
        <StatCard title="Active Jobs"      value={loading ? "…" : runningJobs}       subtitle={`${failedJobs} failed recently`}         icon={<Briefcase size={20} />} accent="emerald" />
        <StatCard title="Pending Requests" value={loading ? "…" : pendingReqs}       subtitle="awaiting approval"                       icon={<Inbox size={20} />}     accent="amber"   />
        <StatCard title="Domains"          value={MOCK_DOMAINS.length}               subtitle="customer, order, product…"               icon={<LayoutGrid size={20} />}accent="violet"  />
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Recent jobs */}
        <div className="card overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-slate-800 flex items-center gap-2">
              <Briefcase size={15} className="text-slate-400" />
              Recent Jobs
            </h2>
            <Link href="/jobs" className="text-xs text-brand-600 hover:text-brand-700
              font-medium flex items-center gap-1">
              View all <ArrowUpRight size={12} />
            </Link>
          </div>
          <div className="divide-y divide-slate-50">
            {loading ? (
              <div className="px-5 py-8 text-center text-sm text-slate-400">Loading…</div>
            ) : jobs.slice(0, 5).map((job) => (
              <div key={job.run_id} className="px-5 py-3 flex items-center justify-between
                hover:bg-slate-50 transition-colors">
                <div className="min-w-0">
                  <p className="text-sm font-medium text-slate-800 truncate">{job.job_name}</p>
                  <p className="text-xs text-slate-400 flex items-center gap-1 mt-0.5">
                    <Clock size={11} />
                    {fmtTime(job.start_time)}
                    {job.end_time && ` · ${duration(job.start_time, job.end_time)}`}
                  </p>
                </div>
                <JobStatusBadge status={job.status} />
              </div>
            ))}
          </div>
        </div>

        {/* Recent requests */}
        <div className="card overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-slate-800 flex items-center gap-2">
              <Inbox size={15} className="text-slate-400" />
              Recent Requests
            </h2>
            <Link href="/requests" className="text-xs text-brand-600 hover:text-brand-700
              font-medium flex items-center gap-1">
              View all <ArrowUpRight size={12} />
            </Link>
          </div>
          <div className="divide-y divide-slate-50">
            {loading ? (
              <div className="px-5 py-8 text-center text-sm text-slate-400">Loading…</div>
            ) : requests.slice(0, 5).map((req) => (
              <div key={req.id} className="px-5 py-3 flex items-center justify-between
                hover:bg-slate-50 transition-colors">
                <div className="min-w-0">
                  <p className="text-sm font-medium text-slate-800 flex items-center gap-2">
                    <span className="font-mono text-xs text-slate-500">{req.id}</span>
                    <span className="capitalize">{req.domain}</span>
                    <EnvBadge env={req.environment} />
                  </p>
                  <p className="text-xs text-slate-400 mt-0.5 truncate">{req.purpose}</p>
                </div>
                <RequestStatusBadge status={req.status} />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick actions */}
      <div className="card p-5">
        <h2 className="text-sm font-semibold text-slate-800 mb-3">Quick Actions</h2>
        <div className="flex flex-wrap gap-3">
          <Link href="/requests" className="btn-primary">
            <Inbox size={15} /> New Data Request
          </Link>
          <Link href="/catalog" className="btn-secondary">
            <Database size={15} /> Browse Catalog
          </Link>
          <Link href="/lineage" className="btn-secondary">
            <LayoutGrid size={15} /> View Lineage
          </Link>
          {user.role === "admin" && (
            <Link href="/admin" className="btn-secondary">
              <Briefcase size={15} /> Manage Policies
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}
