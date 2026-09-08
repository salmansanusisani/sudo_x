export type TaskEvent = { sequence: number; timestamp: string; phase: string; message: string }
export type Snapshot = {
  sampled_at: string; os: string; kernel: string; python: string;
  logical_cpu_count: number | null; load_average: number[] | null;
  memory: { total_bytes: number | null; available_bytes: number | null };
}
export type Task = {
  id: string; prompt: string; kind: 'system' | 'nigeria' | 'request';
  status: 'queued' | 'running' | 'completed' | 'blocked' | 'cancelled' | 'failed';
  created_at: string; updated_at: string; summary: string;
  events: TaskEvent[]; scene: 'system' | 'map' | 'overview';
  result: Snapshot | { label: string; mode: string; news_available: boolean; cities: { name: string; lat: number; lon: number }[] } | null;
}
export type PlannerPreview = {
  provider: 'mock' | 'nebius' | 'not_configured'; model: string | null; message: string;
  envelope: { version: string; capability_id: string; action: string; arguments: Record<string, unknown>; rationale: string };
  cloud_disclosure: { provider: string; model: string | null; base_url: string | null; data_handling: string } | null;
}
export type CapabilityDescriptor = {
  id: string; label: string; enabled: boolean; description: string;
  effect: 'read' | 'visualize' | 'plan' | 'mutate' | 'network'; reason: string;
}
export type CapabilityList = { version: string; capabilities: CapabilityDescriptor[] }
export type ResearchResult = {
  query: string; fetched_at: string; answer: string | null;
  sources: { title: string; url: string; content: string; published_date: string | null }[];
  cloud_disclosure: { provider: string; data_handling: string };
}
export type ReviewReceipt = {
  id: string; kind: 'planner' | 'research'; action_hash: string;
  status: 'reviewed'; reviewed_at: string; execution: 'unavailable';
}
export type ChatResponse = {
  model: string; message: string;
  cloud_disclosure: { provider: string; data_handling: string };
  execution: 'unavailable';
}
export type BackendStatus = {
  mode: string;
  provider: 'not_configured' | 'mock' | 'nebius';
  provider_model: string | null;
  provider_ready: boolean;
  version: string;
  capabilities: { id: string; label: string; enabled: boolean; description: string }[];
}

export function bootstrapToken(): string {
  const fragment = new URLSearchParams(window.location.hash.slice(1))
  const token = fragment.get('token')
  if (token) {
    window.history.replaceState(null, '', window.location.pathname)
    if (/^[A-Za-z0-9_-]{32,256}$/.test(token)) {
      try { sessionStorage.setItem('sudo-x-session', token) } catch { /* Session can run in memory. */ }
      return token
    }
  }
  try { return sessionStorage.getItem('sudo-x-session') || '' } catch { return '' }
}

export async function api<T>(path: string, token: string, body?: object): Promise<T> {
  const response = await fetch(`/api${path}`, {
    method: body ? 'POST' : 'GET',
    headers: { Authorization: `Bearer ${token}`, ...(body ? { 'Content-Type': 'application/json' } : {}) },
    body: body ? JSON.stringify(body) : undefined,
    signal: AbortSignal.timeout(10000),
    credentials: 'omit',
  })
  if (!response.ok) {
    if (response.status === 401) throw new Error('Session expired. Reopen the private URL from the running SUDO X launcher.')
    const result = await response.json().catch(() => null)
    throw new Error(result?.error?.message || `Local request failed (${response.status}).`)
  }
  return response.json() as Promise<T>
}

export const isActive = (task: Task) => task.status === 'queued' || task.status === 'running'
