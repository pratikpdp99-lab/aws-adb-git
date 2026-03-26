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
  DeckersProduct, CompareResult, RecommendRequest, RecommendResult,
} from "../types";
import {
  MOCK_DOMAINS, MOCK_DATASETS, MOCK_REQUESTS,
  MOCK_JOBS, MOCK_POLICIES, MOCK_LINEAGE,
  MOCK_PRODUCTS, MOCK_RECOMMEND_RESULT,
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

// ── Deckers D2C Products ───────────────────────────────────────────────────────

export async function fetchProducts(filters?: {
  brand?: string; category?: string; gender?: string; in_stock?: boolean;
}): Promise<DeckersProduct[]> {
  // openapi-fetch doesn't yet have /products/ in the generated spec, so we call
  // the backend directly via fetch and fall back to mock on any error.
  try {
    const params = new URLSearchParams();
    if (filters?.brand)    params.set("brand",    filters.brand);
    if (filters?.category) params.set("category", filters.category);
    if (filters?.gender)   params.set("gender",   filters.gender);
    if (filters?.in_stock !== undefined) params.set("in_stock", String(filters.in_stock));
    const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    const res  = await fetch(`${BASE}/products/?${params.toString()}`);
    if (!res.ok) return MOCK_PRODUCTS;
    const json = await res.json();
    return (json.products ?? json) as DeckersProduct[];
  } catch {
    return MOCK_PRODUCTS;
  }
}

export async function compareProducts(productIds: string[]): Promise<CompareResult> {
  try {
    const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    const res  = await fetch(`${BASE}/products/compare`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ product_ids: productIds }),
    });
    if (!res.ok) throw new Error("compare failed");
    return (await res.json()) as CompareResult;
  } catch {
    // Mock fallback: build a minimal CompareResult from selected mock products
    const selected = MOCK_PRODUCTS.filter((p) => productIds.includes(p.product_id));
    const winner   = selected.reduce((a, b) => (a.rating >= b.rating ? a : b));
    return {
      products: selected,
      matrix: [
        { attribute: "price",    values: Object.fromEntries(selected.map((p) => [p.product_id, `$${p.price}` ])) },
        { attribute: "rating",   values: Object.fromEntries(selected.map((p) => [p.product_id, `${p.rating}★`])), winner: winner.product_id },
        { attribute: "in_stock", values: Object.fromEntries(selected.map((p) => [p.product_id, p.in_stock ? "Yes" : "No"])) },
        { attribute: "gender",   values: Object.fromEntries(selected.map((p) => [p.product_id, p.gender])) },
        { attribute: "seasons",  values: Object.fromEntries(selected.map((p) => [p.product_id, p.seasons.join(", ")])) },
        { attribute: "sustainability_score", values: Object.fromEntries(selected.map((p) => [p.product_id, `${p.sustainability_score}/100`])) },
        { attribute: "return_rate_pct",      values: Object.fromEntries(selected.map((p) => [p.product_id, `${p.return_rate_pct}%`])) },
        { attribute: "colors_available",     values: Object.fromEntries(selected.map((p) => [p.product_id, String(p.colors_available)])) },
      ],
      recommended_winner:    winner.product_id,
      recommendation_reason: `${winner.name} earns the top spot with ${winner.rating}★ rating across ${winner.review_count.toLocaleString()} reviews.`,
    };
  }
}

export async function getRecommendations(req: RecommendRequest): Promise<RecommendResult> {
  try {
    const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    const res  = await fetch(`${BASE}/products/recommendations`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(req),
    });
    if (!res.ok) throw new Error("recommend failed");
    return (await res.json()) as RecommendResult;
  } catch {
    return MOCK_RECOMMEND_RESULT;
  }
}
