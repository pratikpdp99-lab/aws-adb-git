import { useState, FormEvent } from "react";
import { useRouter } from "next/router";
import type { User } from "../types";
import { ShieldCheck, ArrowRight, AlertCircle } from "lucide-react";

const DEMO_ACCOUNTS: (User & { password: string })[] = [
  { name: "Alice Chen",  email: "alice@deckers.com",  password: "admin123",    role: "admin"    },
  { name: "Bob Torres",  email: "bob@deckers.com",    password: "engineer123", role: "engineer" },
  { name: "Carol Singh", email: "carol@deckers.com",  password: "analyst123",  role: "analyst"  },
];

interface Props {
  onLogin: (user: User) => void;
}

export default function LoginPage({ onLogin }: Props) {
  const router = useRouter();
  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [error, setError]       = useState("");
  const [loading, setLoading]   = useState(false);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    setTimeout(() => {
      const match = DEMO_ACCOUNTS.find(
        (a) => a.email === email && a.password === password
      );
      if (match) {
        const user: User = { name: match.name, email: match.email, role: match.role };
        localStorage.setItem("tdm-user", JSON.stringify(user));
        onLogin(user);
        router.push("/");
      } else {
        setError("Invalid credentials. Use a demo account below.");
      }
      setLoading(false);
    }, 400);
  }

  function quickLogin(account: typeof DEMO_ACCOUNTS[0]) {
    setEmail(account.email);
    setPassword(account.password);
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-brand-900
      flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-brand-600
            rounded-2xl mb-4 shadow-lg shadow-brand-900/50">
            <ShieldCheck size={28} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white">TDM Platform</h1>
          <p className="text-slate-400 text-sm mt-1">Deckers Retail · Test Data Management</p>
        </div>

        {/* Form */}
        <div className="bg-white rounded-2xl shadow-2xl shadow-black/30 p-8">
          <h2 className="text-lg font-semibold text-slate-900 mb-6">Sign in to your account</h2>

          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200
              rounded-lg mb-4 text-sm text-red-700">
              <AlertCircle size={15} />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">Email address</label>
              <input
                type="email"
                className="input"
                placeholder="you@deckers.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div>
              <label className="label">Password</label>
              <input
                type="password"
                className="input"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <button type="submit" disabled={loading}
              className="btn-primary w-full justify-center py-2.5">
              {loading ? "Signing in…" : (
                <><span>Sign in</span><ArrowRight size={16} /></>
              )}
            </button>
          </form>

          {/* Demo accounts */}
          <div className="mt-6 pt-5 border-t border-slate-100">
            <p className="text-xs text-slate-400 mb-3 font-medium uppercase tracking-wide">
              Demo accounts
            </p>
            <div className="space-y-2">
              {DEMO_ACCOUNTS.map((acc) => (
                <button key={acc.email}
                  onClick={() => quickLogin(acc)}
                  className="w-full flex items-center justify-between px-3 py-2 rounded-lg
                    border border-slate-100 hover:border-brand-200 hover:bg-brand-50
                    transition-colors text-left group">
                  <div>
                    <p className="text-sm font-medium text-slate-700 group-hover:text-brand-700">
                      {acc.name}
                    </p>
                    <p className="text-xs text-slate-400">{acc.email}</p>
                  </div>
                  <span className={`text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full
                    ${acc.role === "admin"    ? "bg-rose-100   text-rose-600" :
                      acc.role === "engineer" ? "bg-sky-100    text-sky-600"  :
                                               "bg-emerald-100 text-emerald-600"}`}>
                    {acc.role}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>

        <p className="text-center text-slate-600 text-xs mt-6">
          AWS us-east-1 · Databricks Unity Catalog · tdm_catalog
        </p>
      </div>
    </div>
  );
}
