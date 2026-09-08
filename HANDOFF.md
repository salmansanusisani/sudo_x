# SUDO X: Continuation Handoff

Updated: September 7, 2026

## Latest Continuation: Windows Environment and Synthetic Provider Transport

The user explicitly requested environment setup, dependency installation, and continued development. This supersedes the historical planning-only rows below. Current workspace: `C:\Users\Erazer\OneDrive\Documents\sudo_x`.

- Installed isolated Python 3.14 dependencies, locked frontend dependencies, and Playwright Chromium. Production GUI build succeeds. New `setup.ps1` and `launch.ps1` provide native Windows setup/launch.
- Removed native Windows blockers: conditional POSIX imports, Windows privilege check, private Windows ACL validation, exclusive file-handle launcher lease, Windows data directory, and portable browser-test commands. Linux storage checks remain intact, but this session has not executed tests on Linux.
- Windows storage grants the current user, SYSTEM, and administrators access; rejects broader grants, foreign owners, reparse points, and hard-linked databases. Runtime data defaults outside OneDrive/the repo to `%LOCALAPPDATA%\sudo-x`. No Linux metrics are fabricated on Windows.
- Added `src/sudo_x/probe.py`, a standalone fixed-synthetic Nebius transport using the existing `PlanEnvelope`. Its default CLI operation only prints the exact disclosure and does not read the API key. Explicit send requires cloud disclosure approval and manual confirmation of an account-side spending limit. At most one request per invocation, 256 completion tokens, a 15-second total deadline, and a 32 KiB response; no redirects or retries. Validates model identity, complete blocked envelope, and usage; never executes a tool. Dollar cost is unknown and account limits/retention are not automatically verified.
- The GUI/general planner remains blocked for Nebius. This probe is not a general assistant integration, and a synthetic response would not by itself demonstrate meaningful hackathon model usage.
- No live model call, key lookup, scan, remote connection, microphone capture, or paid operation was performed. Probe tests use an in-memory HTTP transport and dummy credentials.
- Final verification: **82 Python tests passed**, **10 Playwright browser tests passed** (13.8 seconds), Ruff passed, `pip check` passed, production UI build passed, both PowerShell scripts parsed successfully, and synthetic CLI disclosure preview ran without a credential lookup or network call. Python dependencies emit two upstream TestClient deprecation warnings; no tests failed.
- The sandboxed browser run hit a Chromium screenshot failure and stalled server cleanup. Its identified temporary test server was stopped, then the full browser suite passed with normal Windows process access. No real background service or auto-start was installed.
- Live model discovery was performed with the locally configured Nebius key without exposing it. The account returned four NVIDIA candidates. Initial primary candidate was `nvidia/Nemotron-3-Ultra-550b-a55b` for strongest complex reasoning; benchmark evidence now recommends `nvidia/Nemotron-3_5-Lightning` as the bounded default and Ultra as escalation. Both expose reasoning/tools metadata; SUDO X still grants no tool authority.
- One guarded real Nebius Token Factory request was performed with the Ultra model using only the fixed synthetic fixture. Result: valid `PlanEnvelope` with `capability_id=security.network_scan`, `action=blocked`, empty arguments, 96 prompt tokens, 202 completion tokens, 298 total tokens, and `tools_executed=0`. No files, system snapshot, task history, screen data, Tavily data, or user prompt was sent. Reported cost is unknown; account balance was not queried or written to the repository.
- A fixed three-case benchmark was run against Ultra and Lightning using 18 total bounded requests across three measurement passes; prompts contained only synthetic scenarios. With a 1024-token measurement cap, Lightning produced valid boundary-safe envelopes on 3/3 cases at 3,198-3,559 ms and 688-740 completion tokens. Ultra produced 2/3 valid envelopes at 2,135-2,558 ms and 224-334 completion tokens; its Nigeria case remained incomplete. The benchmark is evidence for routing, not a claim of general model quality.
- The live dashboard planner preview was enabled for Lightning with a 15-second timeout and 1024-token cap. One route-level request succeeded with a validated `system`/`propose` envelope and cloud disclosure. Only the synthetic user prompt was sent; no machine data or tools were available. Mission/task execution remains local and blocked for general requests.
- Bounded Tavily Nigeria research is now available as a separate explicit action. It sends only the fixed public-news query, caps results at five with a 10-second timeout and 64 KiB response limit, validates source URLs, and returns source dates/excerpts plus a Tavily disclosure. The live route returned five sources successfully; it does not create a task or alter the offline geography behavior.
- Planner and research panels now support an explicit review receipt. `POST /api/reviews` hashes canonical content and records a timestamp, kind, and `execution=unavailable`; review never executes a tool, task, file, network, or machine action. The receipt is the current safe approval-shaped workflow, not permission to execute.
- Review receipts are now persisted in the private SQLite database with schema migration from version 1 to version 2 and restart-persistence coverage. Existing task history is preserved.
- Added `src/sudo_x/nmap_fixture.py`, an offline-only bounded Nmap XML parser. It validates IPs against explicit approved CIDRs, caps XML/host/port sizes, rejects malformed or out-of-scope fixtures, and never launches Nmap or performs network I/O.
- Browser voice input is now an opt-in transcript helper. It requests recognition only after the user clicks the microphone control, inserts transcript text for review, never auto-submits, and shows an explicit listening/error state. Unsupported browsers remain text-only.
- Talk mode is now separate from mission submission. `POST /api/chat` sends only the user's conversation message to Nebius, rejects tools, limits response size/tokens/time, discloses cloud handling, and returns `execution=unavailable`. `Send mission` remains the blocked/local task path for actions.
- Security Lab now renders the offline Nmap fixture evidence through a dedicated UI panel. The panel demonstrates explicit CIDR scope, host/port evidence, and the live-scan boundary; it does not run Nmap.

Next: package the safe MVP for judging: create a public demo deployment/test build, record the under-three-minute English demo video, finalize Devpost description/track/feedback fields, and document the real Nebius/NVIDIA and Tavily calls. Keep live scans, remote operations, and mutations gated on enrolled assets, exact scope, and a future execution broker.

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
| Implementation authorization | Granted for local building and dependency installation | Continue implementation; separately scope live/cloud operations |
| User availability | User says not to worry about time | Do not block planning on weekly-hours questions; retain release gates/deadline |
| Highest-value real routine | Kali/security/remote/coding explicitly requested | Start with integrated owned-lab mission; confirm first asset |
| Remote meaning | Both server operations and remote personal control planned | Confirm preference; implement server operations first |
| Authorized assets | None enrolled or supplied | User selects owned VM/server and explicit scope; no inferred authorization |
| Cloud consent/budget | Not granted/configured | Ask permission and spending ceiling |
| Nebius account/model | Not tested; no key read | User configures secret securely after approval; discover current NVIDIA model IDs |
| Provider ZDR | Unknown | Owner verifies organization setting and binding terms |
| Sandbox readiness | Docker executable only | Test safe rootless path/OpenShell within approved preflight |
| Python environment | Windows project-local Python 3.14 environment installed | Use `.venv/Scripts/python.exe`; Linux uses `.venv/bin/python` |
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

The synthetic transport and CLI disclosure preview now exist in `src/sudo_x/probe.py` and have offline tests. The dashboard also exposes a local-only synthetic planner preview with cloud-disclosure metadata. Next: validate a separately approved live synthetic call with the user's exact account model and account-side spending limit; then reconcile the standalone probe and GUI disclosure/approval flow before connecting any general planner. Keep general requests blocked until structured tool calling, cloud disclosure, budgets, and deterministic policy checks exist. Nmap fixture parsing and scope validation can proceed independently before any live authorized scan. Remote diagnostics precede remote mutation.

## Resume Prompt

> Continue SUDO X in the current workspace (Windows: `C:\Users\Erazer\OneDrive\Documents\sudo_x`; original Linux location: `/home/salman/Documents/Python/sudo x/`). Read README.md, PROJECT_BLUEPRINT.md, and the latest update at the top of HANDOFF.md first. The first GUI/backend slice, Windows setup/storage port, and standalone synthetic Nebius probe are implemented. Local coding/installing is authorized; do not repeat that question. Live provider calls, scans, remote access, and capture remain separately scoped. No live inference has been verified. Preserve unrelated work and sibling `sudo/`. Continue from the latest next-step record, keep model output without execution authority, and update exact test results before ending.

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
