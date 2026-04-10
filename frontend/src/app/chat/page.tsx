'use client';

import { FormEvent, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';

import { NavBar } from '@/components/NavBar';
import { apiFetch, getMe, Me } from '@/lib/api';
import { API_BASE_URL } from '@/lib/config';

type ChatSession = { id: string; title: string; updated_at: string };
type ChatMessage = { id: string; role: 'user' | 'assistant'; content: string; model: string; created_at: string };
type SessionDetail = { session: ChatSession; messages: ChatMessage[] };

const MODELS = [
  'openai/gpt-4.1-mini',
  'openai/gpt-5.4-mini',
  'anthropic/claude-sonnet-4.5',
  'openai/gpt-5.4',
];

export default function ChatPage() {
  const router = useRouter();
  const [me, setMe] = useState<Me | null>(null);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [prompt, setPrompt] = useState('');
  const [selectedModel, setSelectedModel] = useState(MODELS[0]);
  const [error, setError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);

  const canSend = useMemo(() => prompt.trim().length > 0 && !sending, [prompt, sending]);

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
      await refreshSessions();
    })();
  }, [router]);

  async function refreshSessions() {
    try {
      const list = await apiFetch<ChatSession[]>('/sessions');
      setSessions(list);
      if (!activeSessionId && list.length > 0) {
        setActiveSessionId(list[0].id);
        await loadSession(list[0].id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sessions');
    }
  }

  async function loadSession(sessionId: string) {
    try {
      const detail = await apiFetch<SessionDetail>(`/sessions/${sessionId}`);
      setActiveSessionId(detail.session.id);
      setMessages(detail.messages);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load session');
    }
  }

  async function createSession() {
    try {
      const session = await apiFetch<ChatSession>('/sessions', {
        method: 'POST',
        body: JSON.stringify({ title: 'New Chat' }),
      });
      setSessions((prev) => [session, ...prev]);
      setActiveSessionId(session.id);
      setMessages([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create session');
    }
  }

  async function sendPrompt(event: FormEvent) {
    event.preventDefault();
    if (!canSend) return;

    setError(null);
    setSending(true);

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: prompt,
      model: selectedModel,
      created_at: new Date().toISOString(),
    };
    const placeholderId = crypto.randomUUID();

    setMessages((prev) => [
      ...prev,
      userMessage,
      { id: placeholderId, role: 'assistant', content: '', model: selectedModel, created_at: new Date().toISOString() },
    ]);

    const payload = {
      session_id: activeSessionId,
      model: selectedModel,
      message: prompt,
    };
    setPrompt('');

    try {
      const res = await fetch(`${API_BASE_URL}/chat/stream`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok || !res.body) {
        throw new Error(`Streaming failed (${res.status})`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const events = buffer.split('\n\n');
        buffer = events.pop() ?? '';

        for (const eventChunk of events) {
          const line = eventChunk
            .split('\n')
            .find((l) => l.startsWith('data: '));
          if (!line) continue;

          const data = JSON.parse(line.replace('data: ', '')) as {
            type: 'delta' | 'done' | 'error';
            content?: string;
            session_id?: string;
            error?: string;
          };

          if (data.type === 'delta') {
            setMessages((prev) =>
              prev.map((m) => (m.id === placeholderId ? { ...m, content: (m.content ?? '') + (data.content ?? '') } : m)),
            );
          } else if (data.type === 'done') {
            if (data.session_id && !activeSessionId) {
              setActiveSessionId(data.session_id);
            }
            await refreshSessions();
          } else if (data.type === 'error') {
            setError(data.error ?? 'Streaming error');
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
    } finally {
      setSending(false);
    }
  }

  if (!me) return <div className="p-6">Loading...</div>;

  return (
    <main className="h-screen bg-slate-50">
      <NavBar email={me.email} />
      <div className="grid h-[calc(100vh-57px)] grid-cols-[280px_1fr]">
        <aside className="border-r bg-white p-4">
          <button onClick={createSession} className="mb-3 w-full rounded bg-slate-900 px-3 py-2 text-sm text-white">
            New Session
          </button>
          <div className="space-y-2">
            {sessions.map((s) => (
              <button
                key={s.id}
                onClick={() => loadSession(s.id)}
                className={`w-full rounded border px-3 py-2 text-left text-sm ${
                  activeSessionId === s.id ? 'border-slate-900 bg-slate-100' : 'border-slate-200 bg-white'
                }`}
              >
                <div className="truncate font-medium">{s.title}</div>
                <div className="text-xs text-slate-500">{new Date(s.updated_at).toLocaleString()}</div>
              </button>
            ))}
          </div>
        </aside>

        <section className="flex h-full flex-col">
          <div className="flex-1 space-y-4 overflow-y-auto p-6">
            {messages.map((m) => (
              <div key={m.id} className={`max-w-3xl rounded-lg p-3 text-sm ${m.role === 'user' ? 'ml-auto bg-slate-900 text-white' : 'bg-white border'}`}>
                <div className="mb-1 text-xs opacity-70">{m.role}</div>
                <div className="whitespace-pre-wrap">{m.content}</div>
              </div>
            ))}
          </div>

          <form onSubmit={sendPrompt} className="border-t bg-white p-4">
            <div className="mb-2 flex items-center gap-3">
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="rounded border px-2 py-1 text-sm"
              >
                {MODELS.map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))}
              </select>
              {error ? <span className="text-sm text-red-600">{error}</span> : null}
            </div>
            <div className="flex gap-2">
              <input
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Ask your coding question..."
                className="flex-1 rounded border px-3 py-2 text-sm"
              />
              <button
                type="submit"
                disabled={!canSend}
                className="rounded bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
              >
                {sending ? 'Sending...' : 'Send'}
              </button>
            </div>
          </form>
        </section>
      </div>
    </main>
  );
}
