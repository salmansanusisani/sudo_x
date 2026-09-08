import { Code2 } from 'lucide-react'
import { useState } from 'react'

type SandboxResult = { status: string; diff: string; tests: string; changed_files: string[]; original_unchanged: boolean; network: string; credentials: string }

export function CodeWorkspace({ token, api, disabled }: { token: string; api: <T>(path: string, token: string, body?: object) => Promise<T>; disabled: boolean }) {
  const [path, setPath] = useState('scratch/example.py')
  const [content, setContent] = useState('def greet():\n    return "hello from the sandbox"\n')
  const [result, setResult] = useState<SandboxResult | null>(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  async function run() {
    setBusy(true); setError(''); setResult(null)
    try { setResult(await api<SandboxResult>('/sandbox/run', token, { files: { [path]: content } })) }
    catch (e) { setError(e instanceof Error ? e.message : 'Sandbox is unavailable.') }
    finally { setBusy(false) }
  }
  return <section className="wide-panel code-workspace" aria-label="Code workspace sandbox">
    <div className="panel-label"><Code2 size={16}/> CODE WORKSPACE / ISOLATED COPY</div>
    <h2>Test the change before it touches originals.</h2>
    <p className="muted">Edits run in a temporary bubblewrap copy with network disabled and credentials excluded. There is no apply button.</p>
    <label>Relative file path<input value={path} onChange={event => setPath(event.target.value)} /></label>
    <label>Proposed content<textarea value={content} onChange={event => setContent(event.target.value)} rows={8} /></label>
    <button className="primary-button" onClick={() => void run()} disabled={disabled || busy}>Run isolated tests</button>
    {error && <p className="sandbox-error" role="alert">{error}</p>}
    {result && <div className="sandbox-result"><div className="cloud-disclosure"><span className="mono">SANDBOX RECEIPT</span><b>{result.status} · {result.network} · credentials {result.credentials}</b><span>Original files unchanged: {String(result.original_unchanged)}</span></div><h3>Test output</h3><pre>{result.tests}</pre><h3>Exact diff</h3><pre>{result.diff || 'No diff.'}</pre></div>}
  </section>
}
