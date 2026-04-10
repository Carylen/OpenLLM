'use client';

import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';

import { apiFetch } from '@/lib/api';

export default function OnboardingPage() {
  const router = useRouter();
  const [inviteCode, setInviteCode] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await apiFetch('/auth/onboarding/complete', {
        method: 'POST',
        body: JSON.stringify({ invite_code: inviteCode.trim() }),
      });
      router.push('/chat');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Onboarding failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto mt-24 max-w-lg rounded-xl border bg-white p-8 shadow-sm">
      <h1 className="text-xl font-semibold">Complete your onboarding</h1>
      <p className="mt-2 text-sm text-slate-600">Enter your invite code to activate your account.</p>
      <form onSubmit={onSubmit} className="mt-6 space-y-4">
        <input
          className="w-full rounded border px-3 py-2"
          placeholder="Invite code"
          value={inviteCode}
          onChange={(e) => setInviteCode(e.target.value)}
          required
        />
        {error ? <p className="text-sm text-red-600">{error}</p> : null}
        <button
          type="submit"
          disabled={loading}
          className="rounded bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {loading ? 'Activating...' : 'Activate account'}
        </button>
      </form>
    </main>
  );
}
