type Variant = "success" | "warning" | "error" | "info" | "neutral" | "purple";

const VARIANTS: Record<Variant, string> = {
  success: "bg-emerald-100 text-emerald-700 border-emerald-200",
  warning: "bg-amber-100  text-amber-700  border-amber-200",
  error:   "bg-red-100    text-red-700    border-red-200",
  info:    "bg-blue-100   text-blue-700   border-blue-200",
  neutral: "bg-slate-100  text-slate-600  border-slate-200",
  purple:  "bg-violet-100 text-violet-700 border-violet-200",
};

interface Props {
  label: string;
  variant?: Variant;
  dot?: boolean;
}

export default function Badge({ label, variant = "neutral", dot = false }: Props) {
  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full
      text-xs font-medium border ${VARIANTS[variant]}`}>
      {dot && (
        <span className={`w-1.5 h-1.5 rounded-full ${
          variant === "success" ? "bg-emerald-500" :
          variant === "warning" ? "bg-amber-500"   :
          variant === "error"   ? "bg-red-500"     :
          variant === "info"    ? "bg-blue-500"    :
          variant === "purple"  ? "bg-violet-500"  :
          "bg-slate-400"
        }`} />
      )}
      {label}
    </span>
  );
}

// ── Convenience helpers ────────────────────────────────────────────────────────
export function JobStatusBadge({ status }: { status: string }) {
  const map: Record<string, Variant> = {
    SUCCESS: "success", RUNNING: "info", PENDING: "warning",
    FAILED: "error",    SKIPPED: "neutral",
  };
  return <Badge label={status} variant={map[status] ?? "neutral"} dot />;
}

export function RequestStatusBadge({ status }: { status: string }) {
  const map: Record<string, Variant> = {
    FULFILLED: "success", APPROVED: "info",   PENDING: "warning",
    REJECTED:  "error",
  };
  return <Badge label={status} variant={map[status] ?? "neutral"} />;
}

export function EnvBadge({ env }: { env: string }) {
  const map: Record<string, Variant> = {
    prod: "error", staging: "warning", dev: "info",
  };
  return <Badge label={env.toUpperCase()} variant={map[env] ?? "neutral"} />;
}

export function PiiBadge() {
  return <Badge label="PII" variant="error" />;
}

export function MaskedBadge({ strategy }: { strategy?: string }) {
  if (!strategy) return <Badge label="Plain" variant="neutral" />;
  const map: Record<string, Variant> = {
    HASH: "purple", REDACT: "warning", NULLIFY: "error", PARTIAL: "info",
  };
  return <Badge label={strategy} variant={map[strategy] ?? "neutral"} />;
}
