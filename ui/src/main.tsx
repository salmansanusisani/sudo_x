import React, { useEffect, useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { Activity, ArrowDownLeft, ArrowUpRight, AudioLines, Check, CheckCheck, ChevronRight, CircleHelp, Code2, Compass, Cpu, Expand, Globe2, Layers3, LockKeyhole, Menu, MicOff, Monitor, Pause, Radio, Send, Settings2, ShieldCheck, Sparkles, Square, Terminal, Volume2, X } from 'lucide-react'
import { api, bootstrapToken, isActive, type BackendStatus, type CapabilityList, type PlannerPreview, type Snapshot, type Task } from './api'
import { Globe } from './Globe'
import { CapabilityRegistry } from './CapabilityRegistry'
import './styles.css'
import './dialog.css'

const initialToken = bootstrapToken()
type View = 'overview' | 'map' | 'system' | 'screen'
type Section = 'control' | 'missions' | 'security' | 'code' | 'settings'
const time = (value: string) => new Date(value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
const gb = (value: number | null | undefined) => value == null ? '--' : (value / 1024 ** 3).toFixed(1)

function App() {
  const [token] = useState(initialToken)
  const [backend, setBackend] = useState<BackendStatus | null>(null)
  const [capabilities, setCapabilities] = useState<CapabilityList | null>(null)
  const [tasks, setTasks] = useState<Task[]>([])
  const [selected, setSelected] = useState<string | null>(null)
  const [view, setView] = useState<View>('overview')
  const [section, setSection] = useState<Section>('control')
  const [prompt, setPrompt] = useState('')
  const [planPreview, setPlanPreview] = useState<PlannerPreview | null>(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [menu, setMenu] = useState(false)
  const [details, setDetails] = useState(false)
  const [motion, setMotion] = useState(!window.matchMedia('(prefers-reduced-motion: reduce)').matches)
  const [speaking, setSpeaking] = useState(false)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const task = tasks.find(t => t.id === selected) || null
  const snapshotTask = tasks.find(t => t.kind === 'system' && t.result)
  const snapshot = snapshotTask?.result as Snapshot | undefined
  const activeCount = tasks.filter(isActive).length

  useEffect(() => {
    if (!token) return
    let cancelled = false
    Promise.all([api<BackendStatus>('/status', token), api<{ tasks: Task[] }>('/tasks', token), api<CapabilityList>('/capabilities', token)])
      .then(([status, data, registry]) => { if (!cancelled) { setBackend(status); setTasks(data.tasks); setCapabilities(registry) } })
      .catch(e => { if (!cancelled) setError(e instanceof Error ? e.message : 'Cannot connect to local backend.') })
    return () => { cancelled = true }
  }, [token])

  useEffect(() => {
    if (!token || !activeCount) return
    let cancelled = false
    let timer: ReturnType<typeof setTimeout>
    async function poll() {
      try {
        const data = await api<{ tasks: Task[] }>('/tasks', token)
        if (!cancelled) setTasks(data.tasks)
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Task connection interrupted.')
      }
      if (!cancelled) timer = setTimeout(poll, 450)
    }
    timer = setTimeout(poll, 150)
    return () => { cancelled = true; clearTimeout(timer) }
  }, [token, activeCount])

  useEffect(() => {
    if (videoRef.current) videoRef.current.srcObject = stream
  }, [stream, view])
  useEffect(() => () => {
    streamRef.current?.getTracks().forEach(track => track.stop())
    window.speechSynthesis?.cancel()
  }, [])
  useEffect(() => {
    const preference = window.matchMedia('(prefers-reduced-motion: reduce)')
    const change = () => setMotion(!preference.matches)
    preference.addEventListener('change', change)
    return () => preference.removeEventListener('change', change)
  }, [])
  useEffect(() => {
    const keyboard = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key === 'k') { event.preventDefault(); inputRef.current?.focus() }
      if (event.key === 'Escape') { setDetails(false); setMenu(false) }
    }
    window.addEventListener('keydown', keyboard)
    return () => window.removeEventListener('keydown', keyboard)
  }, [])

  async function submit(text: string, kind?: Task['kind']) {
    if (!text.trim() || busy) return
    if (!backend) { setError('Open the private session URL printed by the SUDO X launcher to connect.'); return }
    const selectedKind = kind || (/\bnigeria\b/i.test(text) ? 'nigeria' : 'request')
    setBusy(true); setError(''); setSection('control')
    try {
      const created = await api<Task>('/tasks', token, { prompt: text.trim(), kind: selectedKind })
      setTasks(previous => [created, ...previous.filter(t => t.id !== created.id)].slice(0, 50))
      setSelected(created.id); setPrompt(''); setView(created.scene === 'map' ? 'map' : created.scene === 'system' ? 'system' : 'overview')
      // Read immediately as local-only operations can finish before a polling interval.
      const latest = await api<Task>(`/tasks/${created.id}`, token)
      setTasks(previous => previous.map(t => t.id === latest.id ? latest : t))
    } catch (e) { setError(e instanceof Error ? e.message : 'Request failed.') }
    finally { setBusy(false) }
  }

  async function previewPlan() {
    if (!prompt.trim() || !backend) return
    setError(''); setPlanPreview(null)
    try {
      setPlanPreview(await api<PlannerPreview>('/planner/preview', token, { prompt: prompt.trim() }))
    } catch (e) { setError(e instanceof Error ? e.message : 'Planner preview is unavailable.') }
  }

  async function cancelTask(id: string) {
    try {
      const cancelled = await api<Task>(`/tasks/${id}/cancel`, token, {})
      setTasks(previous => previous.map(t => t.id === id ? cancelled : t))
    } catch (e) { setError(e instanceof Error ? e.message : 'Cancellation could not be confirmed.') }
  }

  function stopScreen() {
    streamRef.current?.getTracks().forEach(track => track.stop())
    streamRef.current = null; setStream(null)
  }

  async function shareScreen() {
    if (!navigator.mediaDevices?.getDisplayMedia) { setError('Screen sharing is unavailable in this browser. Try Chromium on the local app URL.'); return }
    try {
      const capture = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: false })
      stopScreen(); streamRef.current = capture; setStream(capture); setView('screen'); setSection('control')
      capture.getVideoTracks()[0].addEventListener('ended', stopScreen, { once: true })
    } catch { setError('Screen sharing was not started. No screen content was captured.'); }
  }

  function narrate() {
    if (speaking) { window.speechSynthesis.cancel(); setSpeaking(false); return }
    if (!window.speechSynthesis) { setError('Local speech output is not supported by this browser.'); return }
    const voice = window.speechSynthesis.getVoices().find(v => v.localService && v.lang.startsWith('en'))
    if (!voice) { setError('No local English speech voice is available. Cloud speech has not been enabled.'); return }
    const utterance = new SpeechSynthesisUtterance(view === 'map'
      ? 'This is an offline geographic view of Nigeria. Abuja is the capital. Lagos is a major coastal city. Live news is not connected, so I cannot report current headlines.'
      : task?.summary || 'SUDO X mission control. This early local build supports read-only system snapshots and an offline Nigeria map. The AI model and machine-control tools are not connected yet.')
    utterance.voice = voice; utterance.rate = 1
    utterance.onend = () => setSpeaking(false)
    utterance.onerror = () => { setSpeaking(false); setError('Local narration could not finish.') }
    setSpeaking(true); window.speechSynthesis.speak(utterance)
  }

  function chooseTask(next: Task) {
    setSelected(next.id); setView(next.scene === 'map' ? 'map' : next.scene === 'system' ? 'system' : 'overview'); setSection('control')
  }

  const sections: { id: Section; label: string; icon: typeof Compass }[] = [
    { id: 'control', label: 'Mission control', icon: Compass },
    { id: 'missions', label: 'Mission history', icon: Layers3 },
    { id: 'security', label: 'Security lab', icon: ShieldCheck },
    { id: 'code', label: 'Code workspace', icon: Code2 },
  ]

  return <div className={`app ${motion ? '' : 'reduced-motion'}`}>
    <aside className={`rail ${menu ? 'open' : ''}`}>
      <a className="brand" href="#" aria-label="SUDO X home" onClick={e => { e.preventDefault(); setSection('control'); setView('overview') }}><span className="brand-mark">X</span></a>
      <div className="rail-divider"/>
      <nav aria-label="Primary navigation">{sections.map(({ id, label, icon: Icon }) => <button key={id} className={`rail-button ${section === id ? 'selected' : ''}`} title={label} aria-label={label} aria-current={section === id ? 'page' : undefined} onClick={() => { setSection(id); setMenu(false) }}><Icon size={20}/><span className="rail-label">{label}</span></button>)}</nav>
      <div className="rail-bottom"><button className={`rail-button ${section === 'settings' ? 'selected' : ''}`} aria-label="Settings and privacy" title="Settings and privacy" onClick={() => { setSection('settings'); setMenu(false) }}><Settings2 size={20}/><span className="rail-label">Settings</span></button><span className="avatar" title="Local operator">OP</span></div>
    </aside>

    <div className="app-body">
      <header className="topbar">
        <div className="wordmark"><button className="icon-button mobile-menu" aria-label="Toggle navigation" onClick={() => setMenu(!menu)}><Menu size={20}/></button><b>SUDO<span> X</span></b><span className="wordmark-divider"/><span className="mono tiny">PERSONAL OPERATING INTELLIGENCE</span></div>
        <div className="top-status"><span className={`status-dot ${backend ? 'green' : ''}`}/><span>{backend ? 'LOCAL SESSION' : 'INTERFACE PREVIEW'}</span><span className="version">v0.1</span></div>
      </header>

      <main>
        <div className="page-heading"><div><div className="eyebrow"><span className="short-line"/> YOUR WORLD. IN FOCUS.</div><h1>{section === 'control' ? 'Mission control' : section === 'missions' ? 'Mission archive' : section === 'security' ? 'Security lab' : section === 'code' ? 'Code workspace' : 'System preferences'}<span className="heading-dot">.</span></h1></div><button className="quiet-button privacy-button" onClick={() => setSection('settings')}><LockKeyhole size={14}/> Local-first by design <ChevronRight size={14}/></button></div>

        {!token && <div className="notice session-notice"><LockKeyhole size={17}/><div><b>Interface preview</b><span>To run local tasks, open the private session URL printed by <code>sudo-x</code>. No model or machine control is connected.</span></div></div>}
        {backend?.provider === 'mock' && <div className="notice"><Sparkles size={17}/><div><b>Provider boundary / mock</b><span>Planning is isolated and non-executable. No external request or machine action is available.</span></div></div>}
        {error && <div className="notice error" role="alert"><CircleHelp size={17}/><span>{error}</span><button className="icon-button" aria-label="Dismiss notification" onClick={() => setError('')}><X size={16}/></button></div>}
        {stream && <div className="sharing-banner"><span className="status-dot green"/> Screen sharing active. Visible only in this local window; not sent to AI.<button onClick={stopScreen}><Square size={12}/> Stop sharing</button></div>}

        {section === 'control' ? <>
          <div className="workspace">
            <section className={`visual-panel ${view === 'map' ? 'geography' : ''}`} aria-label="Visual workspace">
              <div className="panel-top"><div className="panel-label"><span className="live-square"/>{view === 'map' ? 'GEOGRAPHIC BRIEFING' : view === 'system' ? 'MACHINE OBSERVATORY' : view === 'screen' ? 'DESKTOP VIEW' : 'SPATIAL WORKSPACE'}</div><div className="panel-actions"><span className="source-badge">{view === 'system' && snapshot ? 'LOCAL OBSERVATION' : view === 'screen' && stream ? 'USER SHARED' : 'OFFLINE VIEW'}</span><button className="icon-button" aria-label="Expand visual workspace" onClick={async e => { try { const panel = e.currentTarget.closest('section'); if (document.fullscreenElement) await document.exitFullscreen(); else await panel?.requestFullscreen() } catch { setError('Fullscreen is unavailable in this window.') } }}><Expand size={15}/></button></div></div>
              <div className="scene-tabs" role="group" aria-label="Visual scenes">{([{ id: 'overview', name: 'Overview', icon: Compass }, { id: 'map', name: 'Atlas', icon: Globe2 }, { id: 'system', name: 'System', icon: Cpu }, { id: 'screen', name: 'Desktop', icon: Monitor }] as const).map(({ id, name, icon: Icon }) => <button key={id} className={view === id ? 'active' : ''} onClick={() => setView(id)} aria-pressed={view === id}><Icon size={13}/>{name}</button>)}</div>
              {(view === 'overview' || view === 'map') && <div className="map-stage">
                <div className="coordinates mono">{view === 'map' ? <>09.0820° N<br/>08.6753° E</> : <>GLOBAL REFERENCE<br/>AFRICA / ATLANTIC</>}</div>
                <Globe focused={view === 'map'} motion={motion}/>
                {view === 'overview' ? <><div className="globe-label"><span className="status-dot green"/> A world of possibilities<span className="mono">ONE PERSONAL COMMAND CENTER</span></div><div className="scene-caption">Context is everything.<br/><span>Bring your next mission into view.</span></div></> : <><div className="country-title"><span className="eyebrow">WEST AFRICA / NG</span><h2>Nigeria<span>.</span></h2><p>Geography in focus. News awaiting sources.</p></div><div className="map-facts"><div><span>CAPITAL</span><b>Abuja</b></div><div><span>REGION</span><b>West Africa</b></div><div><span>DATA MODE</span><b className="amber">Offline reference</b></div></div></>}
                <div className="map-credit">Natural Earth / world-atlas · geographic reference</div>
              </div>}
              {view === 'system' && <div className="system-stage">
                <div className="eyebrow">YOUR MACHINE / READ-ONLY</div><h2>A clearer picture<span>.</span></h2><p className="muted">A real snapshot, only when you request one.</p>
                {snapshot ? <><div className="metric-grid"><div className="metric"><Cpu size={20}/><strong>{snapshot.logical_cpu_count ?? '--'}<small>logical CPUs</small></strong><span>PROCESSOR</span></div><div className="metric"><Activity size={20}/><strong>{snapshot.load_average?.[0]?.toFixed(2) ?? '--'}<small>1-minute load</small></strong><span>LOAD AVERAGE, NOT CPU %</span></div><div className="metric"><Layers3 size={20}/><strong>{gb(snapshot.memory.available_bytes)}<small>/ {gb(snapshot.memory.total_bytes)} GiB</small></strong><span>MEMORY AVAILABLE</span></div></div><dl className="system-details"><div><dt>Operating system</dt><dd>{snapshot.os}</dd></div><div><dt>Kernel</dt><dd>{snapshot.kernel}</dd></div><div><dt>Python runtime</dt><dd>{snapshot.python}</dd></div><div><dt>Observed at</dt><dd>{new Date(snapshot.sampled_at).toLocaleString()}</dd></div></dl><p className="footnote">Snapshot only. Not continuous monitoring or a security assessment.</p></> : <div className="empty-observation"><div className="empty-icon"><Cpu size={34}/></div><b>No system data collected</b><p>Hostname and personal files are excluded.</p></div>}
                <button className="primary-button" disabled={busy || !backend} onClick={() => submit('Collect a read-only system snapshot.', 'system')}><Activity size={15}/>{snapshot ? 'Refresh snapshot' : 'Inspect this machine'}<ArrowUpRight size={15}/></button>
              </div>}
              {view === 'screen' && <div className="desktop-stage">{stream ? <video ref={videoRef} autoPlay muted playsInline aria-label="Locally shared screen preview"/> : <><div className="desktop-illustration"><Monitor size={62} strokeWidth={1}/><span className="desktop-cross">+</span></div><h2>A window into your work.</h2><p>Choose a screen or app to view here.<br/>You decide what is visible. Nothing is sent to AI.</p><button className="primary-button" onClick={shareScreen}><Monitor size={16}/> Choose a screen</button><span className="footnote">View-only. Computer control is not implemented.</span></>}</div>}
              <div className="visual-footer"><span><span className="status-dot"/>{view === 'map' ? 'Live headlines are not connected' : view === 'system' ? 'No shell commands executed' : view === 'screen' ? 'Your screen, your permission' : 'Waiting for your next mission'}</span><button onClick={narrate} aria-label={speaking ? 'Stop narration' : 'Narrate current view'} className={speaking ? 'narrating' : ''}>{speaking ? <Square size={13}/> : <Volume2 size={15}/>}<span>{speaking ? 'Stop' : 'Narrate'}</span></button></div>
            </section>

            <aside className="conversation-panel" aria-label="Conversation">
              <div className="assistant-header"><div className="assistant-glyph"><AudioLines size={23}/></div><div><h2>SUDO X</h2><span><span className="status-dot green"/> LOCAL INTERFACE</span></div><button className="icon-button" aria-label="About this build" onClick={() => setDetails(true)}><CircleHelp size={17}/></button></div>
              <div className="conversation-scroll" aria-live="polite">
                <div className="conversation-date mono">THIS SESSION / YOUR SPACE</div>
                <div className="assistant-message"><div className="message-label"><Sparkles size={12}/> SUDO X</div><h3>What are we<br/>working on?</h3><p>Your workspace is ready. Bring a place into focus, inspect your machine, or share a window into your work.</p><p className="honesty-note">Early local build. AI reasoning and autonomous tools are not connected yet.</p></div>
                {task && <div className="task-conversation" key={task.id}><div className="user-message">{task.prompt}</div><div className="message-label"><Sparkles size={12}/> SUDO X <span className={`task-state ${task.status}`}>{task.status}</span></div><p>{task.summary || 'Your request is in the local task queue.'}</p>{task.kind === 'nigeria' && <div className="source-needed"><Globe2 size={17}/><span>Map available<br/><small>No current news fetched</small></span></div>}</div>}
              </div>
              <div className="suggestions"><span className="eyebrow">START A MISSION</span><button disabled={busy || !backend} onClick={() => submit('Show me news from Nigeria.', 'nigeria')}><Globe2 size={15}/><span>Bring Nigeria into focus</span><ArrowUpRight size={15}/></button><button disabled={busy || !backend} onClick={() => submit('Collect a read-only system snapshot.', 'system')}><Cpu size={15}/><span>Inspect this machine</span><ArrowUpRight size={15}/></button><button onClick={() => { setView('screen'); setSection('control') }}><Monitor size={15}/><span>Open my desktop view</span><ArrowUpRight size={15}/></button></div>
              <form className="composer" onSubmit={e => { e.preventDefault(); void submit(prompt) }}><label className="sr-only" htmlFor="mission-prompt">Your mission</label><textarea ref={inputRef} id="mission-prompt" value={prompt} maxLength={2000} onChange={e => setPrompt(e.target.value)} placeholder="Tell SUDO X what you have in mind..." rows={2} onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); void submit(prompt) } }}/><div className="composer-tools"><button type="button" className="icon-button" aria-label="Voice input not connected" onClick={() => setError('Voice input is not connected yet. Your microphone has not been accessed. Use text, or Narrate for optional local speech output.')}><MicOff size={17}/></button><button type="button" className="plan-button" onClick={() => void previewPlan()} disabled={!prompt.trim() || busy || !backend}>Preview plan</button><span className="mono">TEXT MODE <kbd>CTRL K</kbd></span><button type="submit" className="send-button" aria-label="Send mission" disabled={!prompt.trim() || busy || !backend}><Send size={17}/></button></div></form>
              {planPreview && <div className="plan-preview" aria-label="Planner preview"><div className="panel-label"><Sparkles size={13}/> NON-EXECUTABLE PLAN <span className="source-badge">{planPreview.provider}</span></div><p>{planPreview.message}</p><div className="plan-envelope"><span className="mono">CAPABILITY</span><b>{planPreview.envelope.capability_id}</b><span className="mono">ACTION</span><b>{planPreview.envelope.action}</b><span className="mono">RATIONALE</span><b>{planPreview.envelope.rationale}</b></div><small>Preview only. No tool, file, network, or machine action was performed.</small></div>}
              <div className="composer-note"><LockKeyhole size={10}/> Your commands stay on this machine.</div>
            </aside>
          </div>

          <section className="execution-panel" aria-label="Execution trace"><div className="execution-heading"><div><div className="panel-label"><Terminal size={14}/> EXECUTION TRACE</div><span>Not just answers. Evidence.</span></div><div className="execution-controls"><span className="mono">{task ? `${task.events.length.toString().padStart(2, '0')} EVENTS` : 'NO ACTIVE MISSION'}</span>{task && isActive(task) && <button className="quiet-button" onClick={() => cancelTask(task.id)}><Pause size={12}/> Cancel</button>}<button className="icon-button" aria-label="View mission history" onClick={() => setSection('missions')}><ArrowUpRight size={16}/></button></div></div>
            {task ? <div className="event-list">{task.events.map(event => <div className={`event-row ${event.phase}`} key={event.sequence}><span className="event-icon">{event.phase === 'complete' || event.phase === 'verify' ? <Check size={12}/> : event.phase === 'blocked' ? <LockKeyhole size={12}/> : <ChevronRight size={12}/>}</span><time>{time(event.timestamp)}</time><span className="event-phase">{event.phase}</span><p>{event.message}</p></div>)}</div> : <div className="execution-empty"><div className="trace-path"><span/><i/><span/><i/><span/></div><p>Your actions will appear here, as they happen.<span>Observed facts, tool results, and explicit boundaries. No simulated execution.</span></p><span className="trace-wait">AWAITING INPUT <span>_</span></span></div>}
          </section>
        </> : section === 'missions' ? <section className="wide-panel"><div className="panel-label"><Layers3 size={16}/> LOCAL MISSION HISTORY <span className="source-badge">{tasks.length} RECENT</span></div><h2>Nothing gets lost in the conversation.</h2><p className="muted">Requests and evidence are stored in your local SQLite database. The most recent 50 appear here.</p>{tasks.length ? <div className="mission-list">{tasks.map(item => <button key={item.id} onClick={() => chooseTask(item)}><span className={`mission-status ${item.status}`}><CheckCheck size={18}/></span><div><b>{item.prompt}</b><span>{time(item.created_at)} · {item.events.length} recorded events</span></div><span className={`task-state ${item.status}`}>{item.status}</span><ArrowUpRight size={18}/></button>)}</div> : <div className="large-empty"><Layers3 size={36}/><h3>A clean slate.</h3><p>Your first mission starts in Mission control.</p><button className="primary-button" onClick={() => setSection('control')}>Start a mission <ArrowUpRight size={14}/></button></div>}</section> : section === 'settings' ? <section className="wide-panel preferences"><div className="panel-label"><Settings2 size={16}/> SETTINGS & PRIVACY</div><h2>Power, with clear boundaries.</h2><div className="settings-grid"><div className="setting-card"><LockKeyhole size={23}/><h3>Local by default</h3><p>Tasks and observations stay in a user-private database. No analytics, external map tiles, or inference calls are made by this build.</p><span className="setting-status">ENFORCED IN THIS BUILD</span></div><div className="setting-card"><Sparkles size={23}/><h3>Reasoning provider</h3><p>Nebius / NVIDIA integration is planned. No API key is collected here. General requests are blocked, never answered with fabricated model output.</p><span className="setting-status amber">NOT CONNECTED</span></div><div className="setting-card"><Monitor size={23}/><h3>Screen & sound</h3><p>Screen sharing requires your browser's chooser. Frames stay in the local view. Narration uses an available local browser voice; microphone input is not connected.</p><button className="quiet-button" onClick={() => { setSection('control'); setView('screen') }}>Open desktop view <ArrowUpRight size={14}/></button></div><div className="setting-card"><Activity size={23}/><h3>Interface motion</h3><p>Globe focus transitions follow your system's reduced-motion preference. You can turn them off here.</p><button className={`toggle ${motion ? 'on' : ''}`} role="switch" aria-checked={motion} aria-label="Interface motion" onClick={() => setMotion(!motion)}><span/>{motion ? 'Motion enabled' : 'Motion reduced'}</button></div></div><div className="capabilities"><h3>Connected capabilities</h3>{backend?.capabilities.map(cap => <div key={cap.id}><span className={`status-dot ${cap.enabled ? 'green' : ''}`}/><b>{cap.label}</b><span>{cap.enabled ? 'Available' : 'Not connected'}</span></div>) || <p>Open an authenticated local session to check backend capabilities.</p>}</div></section> : <section className="wide-panel capability-preview"><div className="panel-label">{section === 'security' ? <ShieldCheck size={16}/> : <Code2 size={16}/>} {section === 'security' ? 'AUTHORIZED SECURITY OPERATIONS' : 'VERIFIED CODING WORKSPACE'}<span className="source-badge">PLANNED / NOT CONNECTED</span></div><div className="preview-hero"><div className="preview-icon">{section === 'security' ? <ShieldCheck size={58} strokeWidth={1}/> : <Code2 size={58} strokeWidth={1}/>}</div><h2>{section === 'security' ? 'Know what changed.\nUnderstand why.' : 'From an idea\nto a tested outcome.'}</h2><p>{section === 'security' ? 'Scoped Nmap observations, enrolled machines, and evidence-backed remediation. No scans or remote connections are available in this first build.' : 'An isolated workspace for implementation, tests, and reviewable changes. Code execution and project access are not available in this first build.'}</p></div><div className="roadmap-strip">{(section === 'security' ? ['Enroll an owned asset', 'Observe with Nmap', 'Investigate & verify'] : ['Define the outcome', 'Build in isolation', 'Review the evidence']).map((label, index) => <div key={label}><span>0{index + 1}</span><b>{label}</b><small>Requires implementation</small></div>)}</div><button className="quiet-button" onClick={() => setSection('control')}>Return to working capabilities <ArrowDownLeft size={14}/></button></section>}
         {section === 'settings' && <CapabilityRegistry data={capabilities}/>}<footer className="app-footer"><span><span className="status-dot green"/> LOCAL-FIRST <span className="footer-divider">/</span> HUMAN IN CONTROL</span><span>SUDO X <span className="footer-divider">/</span> BUILT FOR YOUR WORLD <Radio size={13}/></span></footer>
      </main>
    </div>
    {details && <div className="modal-backdrop" onClick={() => setDetails(false)}><section className="info-modal" role="dialog" aria-modal="true" aria-labelledby="about-title" onClick={e => e.stopPropagation()}><button className="icon-button close-modal" autoFocus aria-label="Close build information" onClick={() => setDetails(false)}><X size={20}/></button><span className="eyebrow">FIRST WORKING SLICE</span><h2 id="about-title">A real foundation.<br/>An ambitious direction.</h2><p>This GUI connects to a local task engine, not an AI model yet. System snapshots are real; Nigeria is an offline geography scene, not current news.</p><p>Security tools, coding execution, autonomous computer control, and voice input are next milestones. They are not silently simulated here.</p><button className="primary-button" onClick={() => { setDetails(false); setSection('settings') }}>View capabilities <ChevronRight size={15}/></button></section></div>}
  </div>
}

createRoot(document.getElementById('root')!).render(<React.StrictMode><App/></React.StrictMode>)
