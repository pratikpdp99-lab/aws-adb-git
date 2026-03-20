/**
 * API client that calls the FastAPI backend.
 * Falls back to mock data on any error (including when backend is not running).
 */

import type {
  Domain, Dataset, DataRequest, JobRun, MaskingPolicy,
  TableLineage, MaskingStrategy,
} from "../types";
import {
  MOCK_DOMAINS, MOCK_DATASETS, MOCK_REQUESTS,
  MOCK_JOBS, MOCK_POLICIES, MOCK_LINEAGE,
} from "./mock";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<T>;
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<T>;
}

async function put<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<T>;
}

async function del(path: string): Promise<void> {
  await fetch(`${BASE}${path}`, { method: "DELETE" });
}

// ── Domains ────────────────────────────────────────────────────────────────────
export async function fetchDomains(): Promise<Domain[]> {
  try {
    const data = await get<{ domains: Domain[] }>("/domains/");
    return data.domains;
  } catch {
    return MOCK_DOMAINS;
  }
}

export async function fetchDomain(name: string): Promise<Domain> {
  try {
    return await get<Domain>(`/domains/${name}`);
  } catch {
    return MOCK_DOMAINS.find((d) => d.name === name) ?? MOCK_DOMAINS[0];
  }
}

// ── Datasets ───────────────────────────────────────────────────────────────────
export async function fetchDatasets(): Promise<Dataset[]> {
  try {
    const data = await get<{ datasets: Dataset[] }>("/datasets/");
    return data.datasets;
  } catch {
    return MOCK_DATASETS;
  }
}

// ── Requests ───────────────────────────────────────────────────────────────────
export async function fetchRequests(): Promise<DataRequest[]> {
  try {
    return await get<DataRequest[]>("/requests/");
  } catch {
    return MOCK_REQUESTS;
  }
}

export async function createRequest(body: {
  domain: string;
  environment: string;
  row_count: number;
  requester: string;
  purpose?: string;
}): Promise<DataRequest> {
  try {
    return await post<DataRequest>("/requests/", body);
  } catch {
    const mock: DataRequest = {
      id: `REQ-${String(Math.floor(Math.random() * 9000) + 1000)}`,
      ...body,
      status: "PENDING",
      created_at: new Date().toISOString(),
    };
    return mock;
  }
}

// ── Jobs ───────────────────────────────────────────────────────────────────────
export async function fetchJobs(): Promise<JobRun[]> {
  try {
    const data = await get<{ runs: JobRun[] }>("/jobs/");
    return data.runs;
  } catch {
    return MOCK_JOBS;
  }
}

// ── Masking Policies ───────────────────────────────────────────────────────────
export async function fetchPolicies(): Promise<MaskingPolicy[]> {
  try {
    return await get<MaskingPolicy[]>("/masking/policies");
  } catch {
    return MOCK_POLICIES;
  }
}

export async function upsertPolicy(body: {
  domain: string;
  rules: { field: string; strategy: MaskingStrategy }[];
  created_by: string;
}): Promise<MaskingPolicy> {
  try {
    // Try PUT first (update), then POST (create)
    try {
      return await put<MaskingPolicy>(`/masking/policies/${body.domain}`, body);
    } catch {
      return await post<MaskingPolicy>("/masking/policies", body);
    }
  } catch {
    const mock: MaskingPolicy = {
      id: `POL-${String(Math.floor(Math.random() * 9000) + 1000)}`,
      domain: body.domain,
      rules: body.rules,
      created_by: body.created_by,
      version: 1,
      created_at: new Date().toISOString(),
    };
    return mock;
  }
}

export async function deletePolicy(domain: string): Promise<void> {
  try {
    await del(`/masking/policies/${domain}`);
  } catch {
    // mock: no-op
  }
}

// ── Lineage ────────────────────────────────────────────────────────────────────
export async function fetchLineage(domain: string): Promise<TableLineage> {
  try {
    return await get<TableLineage>(`/lineage/${domain}`);
  } catch {
    return MOCK_LINEAGE[domain] ?? MOCK_LINEAGE["customer"];
  }
}
