# SUDO X: Continuation Handoff

Updated: September 7, 2026

## Actual State

**First GUI/backend slice implemented and verified.** Broader implementation remains incomplete.

Current blueprint version: **3.0**. The user explicitly authorized actual coding and requested a futuristic GUI where conversation, live task operation, maps, screen visuals, and evidence are visible. This slice implements the GUI/backend foundation. No scan, remote connection, microphone capture, model call, paid operation, or privileged action was authorized or performed.

The user requested a hackathon-winning-quality plan for an always-on Kali Linux personal assistant, inspired by JARVIS, and explicitly asked not to build yet. They requested a directory named `sudo x` in their Documents Python folder and detailed Markdown so another model can continue after context/token exhaustion.

Created directory: `/home/salman/Documents/Python/sudo x/`.

Current project files:

- `README.md`: entry point and planning status.
- `PROJECT_BLUEPRINT.md`: detailed product/engineering/submission specification.
- `HANDOFF.md`: this actual-state record.
- `ui/`: React/Vite GUI source, offline globe, local screen preview, responsive styles, and browser tests.
- `src/sudo_x/`: FastAPI loopback backend, SQLite task/event store, bounded local task engine, and launcher CLI.
- `src/sudo_x/provider.py`: explicit provider configuration and deterministic non-executable mock planner boundary.
- `src/sudo_x/capabilities.py`: versioned capability registry with effect classes and blocking reasons.
- `launch.sh`: normal-user Chromium app-mode launcher after the GUI build.
- `THIRD_PARTY_NOTICES.md`: geographic and interface dependency attribution.

No service, database outside test/runtime data, sandbox, model calls, live security operation, remote connection, git initialization, commit, deployment, or hackathon registration was performed. The project-local Python virtual environment and Node dependencies were installed for development; runtime task storage defaults to a user-private XDG directory and was not populated as a production session.

## Research Completed

- Read official Devpost overview, rules, and resources.
- Verified deadline: October 30, 2026, 10:00 PDT / 17:00 UTC.
- Verified NVIDIA open source model plus Nebius runtime/API requirement.
- Verified four equally weighted judging criteria and submission requirements.
- Verified testing access must remain free and available through judging ending December 15, 2026.
- Read official Nebius quickstart, docs index, model listing, function calling, and legal quick guide.
- Read official OpenShell and NemoClaw READMEs; both describe alpha-stage software.
- For version 2, read official Kali Nmap documentation and Nmap's XML output guidance. Local Nmap installation/version and remote targets remain unverified.
- Located existing sibling SUDO and read its README. Did not execute or modify it, or read its personal runtime memory/config files.
- Basic machine check reported Python 3.14.6, approximately 7.7 GiB RAM, four logical CPUs, Docker executable present. Docker runtime/rootless mode, desktop session, GPU, and package compatibility remain unverified.
- Node 20.19.2, npm 9.2.0, and Chromium were available. The UI dependency lock was repaired with npm 10 and currently installs with zero reported audit vulnerabilities. A previous npm install left a damaged lock warning; the final `npm ci` and production build succeeded and should be reproduced in a clean clone.
- An attempted research subagent failed due to its provider quota. Research was continued directly; no unresolved reliance on its nonexistent results.

## Locked-In Design Direction

- Product: Kali-native personal operator for OS understanding, authorized security, remote administration, coding, and daily delegation; not unrestricted shell chat.
- Core differentiator: connects machine context, persistent missions, reviewed reusable skills, and verifiable outcomes across tools.
- Four workflows: prepare a work session; watch/process an approved inbox; build/debug code in an isolated copy; monitor an enrolled lab, investigate remotely, prepare a tested fix, and verify after approved application.
- Version 2 flagship: real scoped Nmap observation -> pinned SSH diagnostics -> sandboxed config/code fix -> exact approval -> remote user-app change -> health check and repeat scan.
- Detailed capability inventory, tool catalog, asset authorization, scanner egress, remote dispatcher/leases, and JARVIS-like UX are in blueprint section 20.
- Cloud NVIDIA inference on Nebius, local memory and permission broker, explicit cloud disclosure boundary.
- Text-first, voice later. No universal GUI control or root access in MVP.
- Small Python task loop, SQLite persistence, FastAPI, React UI. Evaluate OpenShell in a timeboxed spike rather than blindly stacking frameworks.
- A model proposes actions; deterministic code authorizes and checks them.
- Target >=90% supported-task success on a frozen benchmark, never claim a 90% chance of winning.
- Leave `../sudo/` and legacy personal configs untouched. Audit/disclose any later reuse.
- GUI-first implementation is now the active branch: local visual scene -> typed task -> persisted events -> real result/blocked state.

## Open Decisions / Blockers

| Item | Current status | Next action |
| --- | --- | --- |
| Implementation authorization | Not granted; planning requested | Ask before scaffolding or installing |
| User availability | User says not to worry about time | Do not block planning on weekly-hours questions; retain release gates/deadline |
| Highest-value real routine | Kali/security/remote/coding explicitly requested | Start with integrated owned-lab mission; confirm first asset |
| Remote meaning | Both server operations and remote personal control planned | Confirm preference; implement server operations first |
| Authorized assets | None enrolled or supplied | User selects owned VM/server and explicit scope; no inferred authorization |
| Cloud consent/budget | Not granted/configured | Ask permission and spending ceiling |
| Nebius account/model | Not tested; no key read | User configures secret securely after approval; discover current NVIDIA model IDs |
| Provider ZDR | Unknown | Owner verifies organization setting and binding terms |
| Sandbox readiness | Docker executable only | Test safe rootless path/OpenShell within approved preflight |
| Python environment | System Python 3.14.6 | Choose isolated supported interpreter without replacing system Python |
| Existing prototype reuse | Undecided | Default clean new code; ask before reuse/migration |
| Public judge access | Strategy planned, not provisioned | Fund isolated synthetic demo or clarify free testing alternative |
| Eligibility/registration | Unknown | User checks rules and registers personally |
| City award rules conflict | Documented | Ask organizer only if relevant; official rules take precedence |

## Verified Implementation Results

- `.venv/bin/ruff check src tests`: passed.
- `.venv/bin/python -B -m pytest -q -p no:cacheprovider`: **46 passed**.
- `cd ui && npm ci --no-fund`: passed, zero reported vulnerabilities in final install.
- `cd ui && npm run build`: passed with Vite 6.4.3.
- `cd ui && npm run test:e2e`: **9 passed** using Chromium.
- Browser checks cover preview/no external requests, real system snapshot, persistence after refresh, offline Nigeria scene without fabricated news, unsupported request blocking, privacy/settings controls, mobile overflow, expired sessions, keyboard-accessible dialog, and stopping local screen capture tracks.
- Test-only server is `tests/serve_e2e.py`; it uses a temporary data directory and fixture bearer token. Never use that token for a real session.
- Provider boundary tests cover default `not_configured`, deterministic mock planning with no network/action execution, and rejection of incomplete/unsafe Nebius configuration.
- Capability/plan tests cover the authenticated `/api/capabilities` contract, network/mutation effect labels, unknown-field rejection, and rejection of shell/exec/target/url fields in planner envelopes.
- Capability metadata is exposed by the backend; the current GUI continues to show the simpler status view while a richer registry panel is scheduled for the next UI-focused pass.
- Authenticated `POST /api/planner/preview` and GUI `Preview plan` are implemented. Default `not_configured` sessions return `planner_not_ready`; mock sessions render a blocked validated envelope. No preview has execution authority.
- The richer capability-registry UI refactor was intentionally deferred because the existing one-line settings JSX is brittle; `/api/capabilities` remains the source for the next focused UI pass.
- `ui/src/CapabilityRegistry.tsx` now renders `/api/capabilities` as a dedicated Settings panel with effect labels, descriptions, and authority/blocking reasons. The original compact backend status list remains for compatibility.
- Synthetic Nebius/NVIDIA transport is implemented behind the provider boundary. It is deterministic and local-only: no HTTP client is invoked, no API key is retained, and general task execution remains blocked.
- Planner previews now include a cloud-disclosure object with provider, model, base URL, and explicit data-handling language. The frontend renders this disclosure beside the non-executable plan.
- Nebius provider budgets are bounded by `SUDOX_PROVIDER_TIMEOUT_SECONDS` (0.1-30 seconds) and `SUDOX_PROVIDER_MAX_TOKENS` (1-4096); defaults are 5 seconds and 256 tokens. These settings gate the synthetic probe and do not authorize live cloud inference.

## Exact Next Step

The user has approved actual coding and the first visual slice is complete. Before live security, remote work, microphone input, screen upload, or paid inference, confirm the relevant separate permission and budget. Do not ask for API keys, passwords, or private SSH keys in chat. Do not repeat the resolved question about time constraints.

Next: separately approve and implement a real Nebius transport only after confirming cloud consent, budget, current NVIDIA model ID, and provider data-retention terms. The current synthetic transport is not a real provider call. Keep general requests blocked until structured tool calling, cloud disclosure, budgets, and deterministic policy checks exist. After that, implement Nmap fixture parsing and scope validation before any live authorized scan. Remote diagnostics precede remote mutation.

## Resume Prompt

> Continue SUDO X in `/home/salman/Documents/Python/sudo x/`. Read README.md, PROJECT_BLUEPRINT.md, and HANDOFF.md first. The GUI/backend, provider boundary, capability registry, planner preview, and dedicated CapabilityRegistry settings component are implemented and verified. Preserve unrelated work and leave sibling `sudo/` untouched. Do not enable live news, Nebius calls, microphone, Nmap, SSH, arbitrary shell, or computer control without the separate user permission and safety gate. Next consider an explicitly approved synthetic Nebius probe with no tool authority, cloud-disclosure preview, and hard budget/timeout controls. Keep security authority outside the model, run the smallest tests after each change, and update this handoff with actual results before ending.

## Session Update Template

Use this when implementation starts; replace placeholders with facts, not intentions.

```text
Date:
Current milestone:
User authorization / budget changes:
Files changed:
Capabilities actually working:
Commands/tests run and exact outcomes:
Real provider calls made, model ID, and cost if known:
Known failures / limitations:
Security/privacy decisions changed:
Next smallest action:
External approvals or resources needed:
```

Do not place credentials, raw personal data, or hidden chain-of-thought here. Store concise decisions, observed evidence, and executable next steps.
