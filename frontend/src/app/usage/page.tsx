'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

import { NavBar } from '@/components/NavBar';
import { apiFetch, getMe, Me } from '@/lib/api';

type Usage = {
  period_start: string;
  period_end: string;
  request_count: number;
  input_tokens: number;
  output_tokens: number;
  total_cost_usd: string;
};

export default function UsagePage() {
  const router = useRouter();
  const [me, setMe] = useState<Me | null>(null);
  const [usage, setUsage] = useState<Usage | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      const current = await getMe();
      if (!current) {
        router.push('/login');
        return;
      }
      if (!current.is_active) {
        router.push('/onboarding');
        return;
      }
      setMe(current);
      try {
        const data = await apiFetch<Usage>('/usage');
        setUsage(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load usage');
      }
    })();
  }, [router]);

  if (!me) return <div className="p-6">Loading...</div>;

  return (
    <main className="min-h-screen bg-slate-50">
      <NavBar email={me.email} isAdmin={me.is_admin} />
      <div className="mx-auto mt-6 max-w-3xl rounded-xl border bg-white p-6">
        <h1 className="text-xl font-semibold">Usage dashboard</h1>
        {error ? <p className="mt-3 text-sm text-red-600">{error}</p> : null}
        {usage ? (
          <dl className="mt-4 grid grid-cols-2 gap-4 text-sm">
            <div><dt className="text-slate-500">Period Start</dt><dd>{usage.period_start}</dd></div>
            <div><dt className="text-slate-500">Period End</dt><dd>{usage.period_end}</dd></div>
            <div><dt className="text-slate-500">Requests</dt><dd>{usage.request_count}</dd></div>
            <div><dt className="text-slate-500">Input tokens</dt><dd>{usage.input_tokens}</dd></div>
            <div><dt className="text-slate-500">Output tokens</dt><dd>{usage.output_tokens}</dd></div>
            <div><dt className="text-slate-500">Estimated cost</dt><dd>${usage.total_cost_usd}</dd></div>
          </dl>
        ) : (
          <p className="mt-4 text-sm text-slate-500">Loading usage...</p>
        )}
      </div>
    </main>
  );
}
