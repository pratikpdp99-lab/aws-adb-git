import { useRouter } from "next/router";
import Link from "next/link";
import type { ReactNode } from "react";
import type { User } from "../types";
import {
  LayoutDashboard, DatabaseZap, Inbox, Briefcase,
  Network, ShieldCheck, LogOut, ChevronRight, BarChart3,
} from "lucide-react";

interface NavItem {
  href: string;
  label: string;
  icon: ReactNode;
}

const NAV: NavItem[] = [
  { href: "/",        label: "Dashboard",    icon: <LayoutDashboard size={18} /> },
  { href: "/catalog", label: "Data Catalog", icon: <DatabaseZap size={18} />    },
  { href: "/compare", label: "Compare & Rec",icon: <BarChart3 size={18} />      },
  { href: "/requests",label: "Requests",     icon: <Inbox size={18} />          },
  { href: "/jobs",    label: "Jobs",         icon: <Briefcase size={18} />      },
  { href: "/lineage", label: "Lineage",      icon: <Network size={18} />        },
  { href: "/admin",   label: "Admin Policy", icon: <ShieldCheck size={18} />    },
];

function roleColor(role: User["role"]) {
  return role === "admin" ? "text-rose-300" :
         role === "engineer" ? "text-sky-300" : "text-emerald-300";
}

interface Props {
  children: ReactNode;
  user: User;
  onLogout: () => void;
}

export default function Layout({ children, user, onLogout }: Props) {
  const router = useRouter();

  return (
    <div className="min-h-screen flex bg-slate-50">
      {/* ── Sidebar ──────────────────────────────────────────────────────── */}
      <aside className="w-60 flex-shrink-0 bg-slate-900 flex flex-col">
        {/* Logo */}
        <div className="px-5 py-5 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center">
              <span className="text-white text-xs font-bold">TD</span>
            </div>
            <div>
              <p className="text-white text-sm font-semibold leading-none">TDM Platform</p>
              <p className="text-slate-500 text-xs mt-0.5">Deckers Retail</p>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
          <p className="px-3 mb-2 text-[10px] font-semibold text-slate-600 uppercase tracking-widest">
            Navigation
          </p>
          {NAV.map((item) => {
            const active = router.pathname === item.href;
            return (
              <Link key={item.href} href={item.href}
                className={`sidebar-link ${active ? "active" : ""}`}>
                {item.icon}
                <span>{item.label}</span>
                {active && <ChevronRight size={14} className="ml-auto" />}
              </Link>
            );
          })}
        </nav>

        {/* User */}
        <div className="px-3 py-4 border-t border-slate-800">
          <div className="flex items-center gap-3 px-3 py-2">
            <div className="w-8 h-8 rounded-full bg-brand-600 flex items-center justify-center flex-shrink-0">
              <span className="text-white text-xs font-semibold">
                {user.name.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-white text-sm font-medium truncate">{user.name}</p>
              <p className={`text-xs capitalize truncate ${roleColor(user.role)}`}>
                {user.role}
              </p>
            </div>
            <button onClick={onLogout} title="Sign out"
              className="text-slate-500 hover:text-white transition-colors flex-shrink-0">
              <LogOut size={15} />
            </button>
          </div>
        </div>
      </aside>

      {/* ── Main content ─────────────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <header className="h-14 border-b border-slate-200 bg-white px-6 flex items-center
          justify-between flex-shrink-0 shadow-sm">
          <div className="flex items-center gap-1 text-sm text-slate-500">
            <span className="font-medium text-slate-800">
              {NAV.find((n) => n.href === router.pathname)?.label ?? "TDM Platform"}
            </span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-400 hidden sm:block">
              AWS us-east-1 · tdm_catalog
            </span>
            <div className="w-2 h-2 rounded-full bg-emerald-400" title="API online" />
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-6 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
