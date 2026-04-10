'use client';

import { FormEvent, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

import { NavBar } from '@/components/NavBar';
import { apiFetch, getMe, Me } from '@/lib/api';

type AdminUser = {
  id: string;
  email: string;
  name: string | null;
  is_active: boolean;
  plan_id: string | null;
  created_at: string;
};

type Plan = { id: string; code: string; name: string };

type InviteCode = {
  id: string;
  code: string;
  assigned_plan_id: string;
  max_uses: number;
  used_count: number;
  expires_at: string | null;
  is_active: boolean;
  created_at: string;
};

export default function AdminPage() {
  const router = useRouter();
  const [me, setMe] = useState<Me | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [plans, setPlans] = useState<Plan[]>([]);
  const [invites, setInvites] = useState<InviteCode[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [inviteCode, setInviteCode] = useState('');
  const [invitePlanCode, setInvitePlanCode] = useState('starter');
  const [inviteMaxUses, setInviteMaxUses] = useState(1);

  useEffect(() => {
    (async () => {
      const current = await getMe();
      if (!current) return router.push('/login');
      if (!current.is_active) return router.push('/onboarding');
      if (!current.is_admin) return router.push('/chat');
      setMe(current);
      await refreshAll();
    })();
  }, [router]);

  async function refreshAll() {
    try {
      const [usersData, plansData, invitesData] = await Promise.all([
        apiFetch<AdminUser[]>('/admin/users'),
        apiFetch<Plan[]>('/admin/plans'),
        apiFetch<InviteCode[]>('/admin/invite-codes'),
      ]);
      setUsers(usersData);
      setPlans(plansData);
      setInvites(invitesData);
      if (plansData.length > 0) {
        setInvitePlanCode(plansData[0].code);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load admin data');
    }
  }

  async function updateUserPlan(userId: string, planCode: string) {
    try {
      await apiFetch(`/admin/users/${userId}/plan`, {
        method: 'POST',
        body: JSON.stringify({ plan_code: planCode }),
      });
      await refreshAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update plan');
    }
  }

  async function toggleUser(userId: string, isActive: boolean) {
    try {
      await apiFetch(`/admin/users/${userId}/${isActive ? 'disable' : 'enable'}`, { method: 'POST' });
      await refreshAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update user state');
    }
  }

  async function createInvite(event: FormEvent) {
    event.preventDefault();
    try {
      await apiFetch('/admin/invite-codes', {
        method: 'POST',
        body: JSON.stringify({
          code: inviteCode.trim() || null,
          assigned_plan_code: invitePlanCode,
          max_uses: inviteMaxUses,
        }),
      });
      setInviteCode('');
      setInviteMaxUses(1);
      await refreshAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create invite code');
    }
  }

  async function revokeInvite(inviteId: string) {
    try {
      await apiFetch(`/admin/invite-codes/${inviteId}/revoke`, { method: 'POST' });
      await refreshAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to revoke invite');
    }
  }

  if (!me) return <div className="p-6">Loading...</div>;

  return (
    <main className="min-h-screen bg-slate-50">
      <NavBar email={me.email} isAdmin={me.is_admin} />
      <div className="mx-auto grid max-w-7xl gap-6 p-6 lg:grid-cols-2">
        <section className="rounded-xl border bg-white p-4">
          <h2 className="text-lg font-semibold">Users</h2>
          {error ? <p className="my-2 text-sm text-red-600">{error}</p> : null}
          <div className="mt-3 max-h-[560px] overflow-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b text-slate-500">
                  <th className="py-2">Email</th>
                  <th>Plan</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id} className="border-b align-top">
                    <td className="py-2 pr-2">
                      <div>{user.email}</div>
                      <div className="text-xs text-slate-500">{user.name ?? '—'}</div>
                    </td>
                    <td>
                      <select
                        className="rounded border px-2 py-1"
                        value={plans.find((p) => p.id === user.plan_id)?.code ?? ''}
                        onChange={(e) => updateUserPlan(user.id, e.target.value)}
                      >
                        <option value="" disabled>Select plan</option>
                        {plans.map((plan) => (
                          <option key={plan.id} value={plan.code}>{plan.code}</option>
                        ))}
                      </select>
                    </td>
                    <td>
                      <button
                        className="rounded border px-2 py-1"
                        onClick={() => toggleUser(user.id, user.is_active)}
                      >
                        {user.is_active ? 'Disable' : 'Enable'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="rounded-xl border bg-white p-4">
          <h2 className="text-lg font-semibold">Invite Codes</h2>
          <form onSubmit={createInvite} className="mt-3 grid gap-2 md:grid-cols-[1fr_auto_auto_auto]">
            <input
              value={inviteCode}
              onChange={(e) => setInviteCode(e.target.value)}
              placeholder="Code (optional)"
              className="rounded border px-3 py-2 text-sm"
            />
            <select
              value={invitePlanCode}
              onChange={(e) => setInvitePlanCode(e.target.value)}
              className="rounded border px-2 py-2 text-sm"
            >
              {plans.map((plan) => (
                <option key={plan.id} value={plan.code}>{plan.code}</option>
              ))}
            </select>
            <input
              type="number"
              min={1}
              max={10000}
              value={inviteMaxUses}
              onChange={(e) => setInviteMaxUses(Number(e.target.value))}
              className="w-24 rounded border px-2 py-2 text-sm"
            />
            <button type="submit" className="rounded bg-slate-900 px-3 py-2 text-sm text-white">Create</button>
          </form>

          <div className="mt-4 max-h-[460px] overflow-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b text-slate-500">
                  <th className="py-2">Code</th>
                  <th>Plan</th>
                  <th>Usage</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {invites.map((invite) => (
                  <tr key={invite.id} className="border-b align-top">
                    <td className="py-2 font-mono">{invite.code}</td>
                    <td>{plans.find((p) => p.id === invite.assigned_plan_id)?.code ?? invite.assigned_plan_id}</td>
                    <td>{invite.used_count}/{invite.max_uses}</td>
                    <td>
                      {invite.is_active ? (
                        <button className="rounded border px-2 py-1" onClick={() => revokeInvite(invite.id)}>
                          Revoke
                        </button>
                      ) : (
                        <span className="text-slate-500">Revoked</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </main>
  );
}
