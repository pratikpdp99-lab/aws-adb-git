/**
 * API layer — typed against the FastAPI OpenAPI contract.
 *
 * Every function calls the real backend via the openapi-fetch client (./client.ts).
 * On any network or HTTP error the call silently falls back to mock data so the
 * frontend works in local dev without a running backend.
 *
 * Types are derived from the generated ./api-types.ts — they are the single
 * source of truth; the hand-written types in ../types/index.ts act as aliases
 * and are kept in sync via the generate-client script.
 */

import api from "./client";
import type {
  Domain, Dataset, DataRequest, JobRun, MaskingPolicy,
  TableLineage, MaskingStrategy,
} from "../types";
import {
  MOCK_DOMAINS, MOCK_DATASETS, MOCK_REQUESTS,
  MOCK_JOBS, MOCK_POLICIES, MOCK_LINEAGE,
} from "./mock";

// ── Domains ────────────────────────────────────────────────────────────────────

export async function fetchDomains(): Promise<Domain[]> {
  const { data, error } = await api.GET("/domains/");
  if (error || !data) return MOCK_DOMAINS;
  return data.domains as Domain[];
}

export async function fetchDomain(name: string): Promise<Domain> {
  const { data, error } = await api.GET("/domains/{domain_name}", {
    params: { path: { domain_name: name } },
  });
  if (error || !data) return MOCK_DOMAINS.find((d) => d.name === name) ?? MOCK_DOMAINS[0];
  return data as Domain;
}

// ── Datasets ───────────────────────────────────────────────────────────────────

export async function fetchDatasets(): Promise<Dataset[]> {
  const { data, error } = await api.GET("/datasets/");
  if (error || !data) return MOCK_DATASETS;
  return data.datasets as Dataset[];
}

// ── Requests ───────────────────────────────────────────────────────────────────

export async function fetchRequests(): Promise<DataRequest[]> {
  const { data, error } = await api.GET("/requests/");
  if (error || !data) return MOCK_REQUESTS;
  return data as DataRequest[];
}

export async function createRequest(body: {
  domain: string;
  environment: string;
  row_count: number;
  requester: string;
  purpose?: string;
}): Promise<DataRequest> {
  const { data, error } = await api.POST("/requests/", { body });
  if (error || !data) {
    // Optimistic mock — request is shown immediately while backend is offline
    return {
      id: `REQ-${String(Math.floor(Math.random() * 9000) + 1000)}`,
      ...body,
      status: "PENDING",
      created_at: new Date().toISOString(),
    } as DataRequest;
  }
  return data as DataRequest;
}

// ── Jobs ───────────────────────────────────────────────────────────────────────

export async function fetchJobs(): Promise<JobRun[]> {
  const { data, error } = await api.GET("/jobs/");
  if (error || !data) return MOCK_JOBS;
  // Note: API returns trigger as lowercase ("manual"|"schedule"|"api").
  // Frontend types use uppercase for display consistency — normalise here.
  return (data.runs as unknown[]).map((r) => {
    const run = r as Record<string, unknown>;
    return {
      ...run,
      trigger: String(run.trigger ?? "").toUpperCase(),
    } as JobRun;
  });
}

// ── Masking Policies ───────────────────────────────────────────────────────────

export async function fetchPolicies(): Promise<MaskingPolicy[]> {
  const { data, error } = await api.GET("/masking/policies");
  if (error || !data) return MOCK_POLICIES;
  // API returns strategy as lowercase ("hash"|"redact"…); normalise to uppercase.
  return (data as unknown[]).map((p) => {
    const policy = p as Record<string, unknown>;
    return {
      ...policy,
      rules: (policy.rules as Record<string, unknown>[]).map((r) => ({
        ...r,
        strategy: String(r.strategy ?? "").toUpperCase(),
      })),
    } as MaskingPolicy;
  });
}

export async function upsertPolicy(body: {
  domain: string;
  rules: { field: string; strategy: MaskingStrategy }[];
  created_by: string;
}): Promise<MaskingPolicy> {
  // API expects lowercase strategy values
  const apiBody = {
    ...body,
    rules: body.rules.map((r) => ({ ...r, strategy: r.strategy.toLowerCase() })),
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const castBody = apiBody as any;

  // Try PUT (update existing) first, fall back to POST (create new)
  const putRes = await api.PUT("/masking/policies/{domain}", {
    params: { path: { domain: body.domain } },
    body: castBody,
  });
  if (!putRes.error && putRes.data) return putRes.data as unknown as MaskingPolicy;

  const postRes = await api.POST("/masking/policies", { body: castBody });
  if (!postRes.error && postRes.data) return postRes.data as unknown as MaskingPolicy;

  // Mock fallback
  return {
    id: `POL-${String(Math.floor(Math.random() * 9000) + 1000)}`,
    domain: body.domain,
    rules: body.rules,
    created_by: body.created_by,
    version: 1,
    created_at: new Date().toISOString(),
  } as MaskingPolicy;
}

export async function deletePolicy(domain: string): Promise<void> {
  await api.DELETE("/masking/policies/{domain}", {
    params: { path: { domain } },
  });
  // No-op on error (mock mode)
}

// ── Lineage ────────────────────────────────────────────────────────────────────

export async function fetchLineage(domain: string): Promise<TableLineage> {
  const { data, error } = await api.GET("/lineage/{domain}", {
    params: { path: { domain } },
  });
  if (error || !data) return MOCK_LINEAGE[domain] ?? MOCK_LINEAGE["customer"];
  return data as TableLineage;
}
