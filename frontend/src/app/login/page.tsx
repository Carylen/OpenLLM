'use client';

import { API_BASE_URL } from '@/lib/config';

export default function LoginPage() {
  return (
    <main className="mx-auto mt-24 max-w-lg rounded-xl border bg-white p-8 shadow-sm">
      <h1 className="text-2xl font-semibold">OpenLLM</h1>
      <p className="mt-2 text-sm text-slate-600">Private invite-only coding assistant.</p>
      <a
        href={`${API_BASE_URL}/auth/google/login`}
        className="mt-6 inline-flex rounded bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
      >
        Sign in with Google
      </a>
    </main>
  );
}
