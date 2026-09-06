"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { useLanguage } from "@/lib/language-context";
import { ThemeLangToggle } from "@/components/ThemeLangToggle";
import { ApiError } from "@/lib/api";

export default function RegisterPage() {
  const { register } = useAuth();
  const { t } = useLanguage();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await register(email, password, fullName);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to create your account.");
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
        <h1 className="text-xl font-semibold text-ink-900 dark:text-slate-100">{t("register_title")}</h1>
        <p className="mt-1 text-sm text-ink-600 dark:text-slate-400">{t("register_subtitle")}</p>

        <form onSubmit={onSubmit} className="mt-6 flex flex-col gap-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-ink-800 dark:text-slate-300">
              {t("register_fullName")}
            </label>
            <input className="input" value={fullName} onChange={(e) => setFullName(e.target.value)} />
          </div>
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
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <p className="mt-1 text-xs text-ink-600 dark:text-slate-500">{t("register_passwordHint")}</p>
          </div>
          {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}
          <button className="btn-primary" type="submit" disabled={loading}>
            {loading ? t("register_loading") : t("register_button")}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-ink-600 dark:text-slate-400">
          {t("register_haveAccount")}{" "}
          <Link href="/login" className="font-medium text-brand-600 hover:underline dark:text-brand-400">
            {t("login")}
          </Link>
        </p>
      </div>
    </div>
  );
}
