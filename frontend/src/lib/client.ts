/**
 * Type-safe API client generated from the FastAPI OpenAPI schema.
 *
 * Generated types live in ./api-types.ts (auto-generated — do not edit).
 * Regenerate after backend changes:
 *   make generate-client          # from repo root
 *   npm run generate-client       # from frontend/
 *
 * Uses openapi-fetch: https://openapi-ts.pages.dev/openapi-fetch/
 * Every call returns { data, error } — no try/catch needed at call sites.
 */

import createClient from "openapi-fetch";
import type { paths } from "./api-types";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/**
 * Fully typed HTTP client.
 * Call signatures are inferred from the OpenAPI schema:
 *
 *   const { data, error } = await api.GET("/domains/");
 *   const { data, error } = await api.POST("/requests/", { body: { ... } });
 */
export const api = createClient<paths>({ baseUrl: BASE_URL });

export default api;
