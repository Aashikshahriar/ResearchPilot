"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { useLanguage } from "@/lib/language-context";
import { ThemeLangToggle } from "@/components/ThemeLangToggle";
import { ApiError } from "@/lib/api";

export default function LoginPage() {
  const { login } = useAuth();
  const { t } = useLanguage();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to log in.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center bg-hero-glow bg-slate-50 px-6 dark:bg-ink-900">
      <div className="absolute right-6 top-6">
        <ThemeLangToggle />
      </div>
      <div className="card w-full max-w-sm p-8">
        <Link href="/" className="mb-6 flex items-center gap-2 text-lg font-semibold text-ink-900 dark:text-slate-100">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-brand-500 to-accent-500 text-white">
            R
          </span>
          {t("appName")}
        </Link>
        <h1 className="text-xl font-semibold text-ink-900 dark:text-slate-100">{t("login_title")}</h1>
        <p className="mt-1 text-sm text-ink-600 dark:text-slate-400">{t("login_subtitle")}</p>

        <form onSubmit={onSubmit} className="mt-6 flex flex-col gap-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-ink-800 dark:text-slate-300">{t("email")}</label>
            <input className="input" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-ink-800 dark:text-slate-300">{t("password")}</label>
            <input
              className="input"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}
          <button className="btn-primary" type="submit" disabled={loading}>
            {loading ? t("login_loading") : t("login_button")}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-ink-600 dark:text-slate-400">
          {t("login_noAccount")}{" "}
          <Link href="/register" className="font-medium text-brand-600 hover:underline dark:text-brand-400">
            {t("login_signUp")}
          </Link>
        </p>
      </div>
    </div>
  );
}
