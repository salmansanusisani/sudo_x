import { LockKeyhole, ShieldCheck } from 'lucide-react'
import type { CapabilityList } from './api'

export function CapabilityRegistry({ data }: { data: CapabilityList | null }) {
  return <section className="capability-registry" aria-labelledby="capability-registry-title">
    <div className="capability-registry-head">
      <div>
        <div className="panel-label"><ShieldCheck size={14}/> CAPABILITY REGISTRY</div>
        <h3 id="capability-registry-title">What SUDO X can do.</h3>
      </div>
      <span className="mono capability-schema">SCHEMA {data?.version || '--'}</span>
    </div>
    {data ? <div className="capability-cards">{data.capabilities.map(capability => <article className={`capability-card ${capability.enabled ? 'enabled' : 'disabled'}`} key={capability.id}>
      <div className="capability-card-title"><span className={`status-dot ${capability.enabled ? 'green' : ''}`}/><b>{capability.label}</b><span className={`effect ${capability.effect}`}>{capability.effect}</span></div>
      <p>{capability.description}</p>
      <div className="capability-reason"><LockKeyhole size={11}/><span>{capability.reason}</span></div>
    </article>)}</div> : <p className="muted capability-empty">Open an authenticated local session to load capability metadata.</p>}
  </section>
}
