import type { ReactNode } from "react";

interface Props {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: ReactNode;
  accent?: "indigo" | "emerald" | "amber" | "rose" | "violet";
}

const ACCENT_CLASSES: Record<string, { bg: string; text: string; ring: string }> = {
  indigo:  { bg: "bg-indigo-50",  text: "text-indigo-600",  ring: "ring-indigo-100"  },
  emerald: { bg: "bg-emerald-50", text: "text-emerald-600", ring: "ring-emerald-100" },
  amber:   { bg: "bg-amber-50",   text: "text-amber-600",   ring: "ring-amber-100"   },
  rose:    { bg: "bg-rose-50",    text: "text-rose-600",    ring: "ring-rose-100"    },
  violet:  { bg: "bg-violet-50",  text: "text-violet-600",  ring: "ring-violet-100"  },
};

export default function StatCard({ title, value, subtitle, icon, accent = "indigo" }: Props) {
  const a = ACCENT_CLASSES[accent];
  return (
    <div className="card p-5 flex items-start gap-4">
      <div className={`p-2.5 rounded-lg ring-1 ${a.bg} ${a.text} ${a.ring}`}>
        {icon}
      </div>
      <div className="min-w-0">
        <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">{title}</p>
        <p className="mt-1 text-2xl font-bold text-slate-900 leading-none">
          {typeof value === "number" ? value.toLocaleString() : value}
        </p>
        {subtitle && <p className="mt-1 text-xs text-slate-400">{subtitle}</p>}
      </div>
    </div>
  );
}
