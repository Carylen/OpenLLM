'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';

import { API_BASE_URL } from '@/lib/config';

export function NavBar({ email }: { email: string }) {
  const router = useRouter();

  async function logout() {
    await fetch(`${API_BASE_URL}/auth/logout`, { method: 'POST', credentials: 'include' });
    router.push('/login');
  }

  return (
    <div className="flex items-center justify-between border-b bg-white px-6 py-3">
      <div className="flex gap-4 text-sm">
        <Link href="/chat" className="font-medium text-slate-800">Chat</Link>
        <Link href="/usage" className="font-medium text-slate-600 hover:text-slate-800">Usage</Link>
      </div>
      <div className="flex items-center gap-3 text-sm text-slate-600">
        <span>{email}</span>
        <button onClick={logout} className="rounded border px-3 py-1 hover:bg-slate-100">Logout</button>
      </div>
    </div>
  );
}
