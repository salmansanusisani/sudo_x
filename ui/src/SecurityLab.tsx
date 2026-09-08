import { ShieldCheck } from 'lucide-react'
import type { NmapFixture } from './api'

export function SecurityLab({ data, disabled, onLoad, visible }: { data: NmapFixture | null; disabled: boolean; onLoad: () => void; visible: boolean }) {
  if (!visible) return null
  const evidence = data || {
    hosts: [{ address: '192.0.2.10', status: 'up', ports: [{ port: 8080, protocol: 'tcp', state: 'open', service: 'http' }] }],
    scope: ['192.0.2.0/24'], source: 'offline_fixture',
  }
  return <section className="wide-panel security-evidence" aria-label="Security lab evidence">
    <div className="panel-label"><ShieldCheck size={16}/> SECURITY LAB / OFFLINE EVIDENCE</div>
    <h2>Scope before scanning.</h2>
    <p className="muted">The demo fixture is parsed locally against an explicit CIDR scope. No scanner is launched and no network traffic is generated.</p>
    <button className="primary-button" onClick={onLoad} disabled={disabled}><ShieldCheck size={15}/> Load demo fixture</button>
    <div className="fixture-evidence"><div className="cloud-disclosure"><span className="mono">OFFLINE FIXTURE</span><b>{evidence.hosts.length} host / {evidence.scope.join(', ')}</b><span>Evidence parsed locally. Live scanning is unavailable.</span></div>{evidence.hosts.map(host => <article key={host.address}><b>{host.address} · {host.status}</b>{host.ports.map(port => <span key={`${port.protocol}-${port.port}`}>{port.protocol}/{port.port} · {port.state} · {port.service || 'unknown service'}</span>)}</article>)}</div>
  </section>
}
