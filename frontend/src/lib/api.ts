import { API_BASE_URL } from './config';

export type Me = {
  id: string;
  email: string;
  name: string | null;
  picture_url: string | null;
  is_active: boolean;
  is_admin: boolean;
};

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  });

  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      message = data.detail ?? data.message ?? message;
    } catch {
      // ignore
    }
    throw new Error(message);
  }

  return res.json() as Promise<T>;
}

export async function getMe(): Promise<Me | null> {
  try {
    return await apiFetch<Me>('/me', { method: 'GET' });
  } catch {
    return null;
  }
}
