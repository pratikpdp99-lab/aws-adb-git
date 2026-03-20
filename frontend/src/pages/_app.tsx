import type { AppProps } from "next/app";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import type { User } from "../types";
import "../styles/globals.css";

const PUBLIC_ROUTES = ["/login"];

export default function App({ Component, pageProps }: AppProps) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("tdm-user");
    if (stored) {
      try { setUser(JSON.parse(stored)); } catch { /* ignore */ }
    }
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    if (!user && !PUBLIC_ROUTES.includes(router.pathname)) {
      router.replace("/login");
    }
  }, [hydrated, user, router]);

  function handleLogout() {
    localStorage.removeItem("tdm-user");
    setUser(null);
    router.push("/login");
  }

  // Prevent flash of unauthenticated content
  if (!hydrated) return null;

  if (PUBLIC_ROUTES.includes(router.pathname)) {
    return <Component {...pageProps} onLogin={setUser} />;
  }

  if (!user) return null;

  return (
    <Layout user={user} onLogout={handleLogout}>
      <Component {...pageProps} user={user} />
    </Layout>
  );
}
