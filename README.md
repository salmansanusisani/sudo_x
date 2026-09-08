# SUDO X

**Your Linux machine, working for you. Every action accountable.**

Active implementation for the Nebius x NVIDIA Global AI Hackathon, Personal AI Track.

An always-on, local-first personal operator for Kali Linux that understands its environment, writes and tests code, uses security tools such as Nmap on authorized targets, helps administer enrolled remote machines, and remembers your daily workflows. Inspired by the usefulness of JARVIS, not its branding or fictional capabilities.

## Expanded Vision

- **Kali understanding:** version-aware tool knowledge, machine/service inventory, and tested capability records.
- **Security assistance:** scoped Nmap checks, baseline comparison, evidence-backed findings, and reviewed remediation.
- **Remote operations:** pinned SSH connections to enrolled machines; optional paired remote control designed separately.
- **Coding:** new features, tests, debugging, code review, and verified patches in isolated workspaces.
- **Personal continuity:** durable missions, memory, reusable skills, proactive briefs, and eventual voice interaction.

Flagship demo: notice a new service on your lab server, investigate, prepare and test a fix, request approval, apply it, and verify the result. See blueprint section 20 for detailed contracts and safeguards. This is the plan, not a working capability or a claim of universal Kali mastery.

## Start Here

1. Read [PROJECT_BLUEPRINT.md](PROJECT_BLUEPRINT.md) for the product, architecture, security boundaries, model behavior, evaluation, milestones, and submission strategy.
2. Read [HANDOFF.md](HANDOFF.md) for actual progress, unresolved decisions, and continuation instructions.
3. Read the implementation status below before assuming a capability exists.

## Run The First Slice

Requires Python 3.12+ and Node.js 20.19+ (or 22.12+). The current Windows development setup uses Python 3.14 and Node.js 24. Kali/Linux remains the target for future security-tool integrations; the local dashboard now also runs natively on Windows.

On Windows, from this project directory in a normal PowerShell terminal:

```powershell
.\setup.ps1
.\launch.ps1
```

Setup creates `.venv`, installs backend/frontend dependencies, and builds the GUI. Use `.\setup.ps1 -BrowserTests` to also install Chromium and run browser tests. Use `.\launch.ps1 -NoBrowser` for just the backend. If your PowerShell policy blocks local scripts, use `powershell -ExecutionPolicy Bypass -File .\setup.ps1` (or `launch.ps1`) for that invocation.

On Linux, from this project directory:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
cd ui
npm ci
npm run build
cd ..
./launch.sh
```

The launcher binds only to `127.0.0.1`, prints a private session URL, and opens a standalone Chromium app window when available. Do not share the printed URL. Run as a normal user, never with `sudo` or root. To run without opening Chromium, use `.venv/bin/sudo-x`.

To verify the current slice:

```powershell
.\.venv\Scripts\ruff.exe check src tests
.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider
cd ui
npm.cmd run test:e2e
```

Linux equivalents:

```bash
.venv/bin/ruff check src tests
.venv/bin/python -B -m pytest -q -p no:cacheprovider
cd ui
npx playwright install chromium
npm run test:e2e
```

Browser tests use Playwright's managed Chromium by default. Set `CHROMIUM_PATH` to use an existing browser. Runtime data stays outside the repository: `%LOCALAPPDATA%\sudo-x` on Windows, or `$XDG_DATA_HOME/sudo-x` (default `~/.local/share/sudo-x`) on Linux. Windows storage enforces a private user/SYSTEM/administrators ACL and an exclusive launcher lease; Linux retains its owner/mode checks and `flock`. Windows load averages and Linux `/proc` memory counters are unavailable and honestly shown as null.

## Synthetic Nebius Probe

The next provider milestone has a standalone, synthetic-only transport. It does not enable the dashboard planner or execute tasks. First inspect its exact disclosure, without credentials or a network call:

```powershell
.\.venv\Scripts\python.exe -m sudo_x.probe --model nvidia/YOUR_ACCOUNT_MODEL_ID
```

Replace the placeholder with an exact NVIDIA model ID available in your Nebius account. The preview contains the fixed imaginary-service scenario, endpoint, completion cap (at most 256), one-request limit per invocation, 15-second deadline, and 32 KiB response cap. It sends no machine snapshot, files, task history, or user prompts. The transport follows the [Nebius chat completions API](https://docs.tokenfactory.nebius.com/api-reference/inference/create-chat-completion).

After reviewing the disclosure, configuring `NEBIUS_API_KEY` securely in the local environment, and confirming an account-side spending limit, explicitly sending requires all three flags: `--send --approve-synthetic-cloud --confirm-account-spend-limit`. There are no retries or redirects. These confirmations are manual; the app cannot verify the account's spending or retention settings. Cost remains unknown, token/time limits are not dollar limits, and a timed-out call may still be billed. `store=false` does not establish organization-level Zero Data Retention. A real guarded Token Factory call and live Lightning planner preview have now been verified with synthetic content.

## Current Implementation

- Futuristic local GUI with visual workspace, conversation panel, mission history, settings/privacy view, and execution trace.
- Offline geography globe focused on Nigeria with Abuja/Lagos reference points. It explicitly does not claim live news.
- Real read-only local system snapshot: OS, kernel, Python, CPU count, load, and memory from bounded local observations.
- Persistent local SQLite task/event history and restart reconciliation.
- Native Windows setup/launcher and private storage, alongside the Linux implementation.
- Standalone guarded Nebius transport with disclosure preview and offline failure/boundary tests; live validation verified with synthetic content.
- Bounded live model benchmark: `nvidia/Nemotron-3_5-Lightning` is the measured default candidate; `nvidia/Nemotron-3-Ultra-550b-a55b` is retained for escalation. Benchmark evidence is recorded in `HANDOFF.md`.
- Bounded Tavily Nigeria research action: fixed public-news query, five-source cap, source URL/date/excerpt validation, explicit cloud disclosure, and no task/tool execution.
- Review receipts: planner/research output can be explicitly marked reviewed with a canonical SHA-256 action hash and `execution=unavailable`; review cannot trigger actions.
- Review receipts persist in the private SQLite store across application restarts; they are records, not execution permissions.
- Optional browser voice input: microphone access is visibly opt-in, recognition transcripts are inserted for review only, and voice never auto-submits a mission. Browser recognition service behavior must be disclosed by the browser; SUDO X does not upload audio itself.
- Optional user-selected screen preview using browser permission. Frames remain in the local view and are not sent to AI; computer control is not implemented.
- Optional local browser speech narration if an available local voice exists. Microphone input is not accessed.
- Honest blocked states for general requests, live news, arbitrary shell, security tools, remote machines, and model execution; bounded planner preview can use live Nebius inference with explicit disclosure.
- Same-origin loopback API with bearer session token, host/origin checks, security headers, request limits, and no external runtime assets.
- Versioned `/api/capabilities` registry and strict non-executable plan envelope. Disabled capabilities expose their effect and blocking reason; they cannot be activated by model output.
- Planner preview control: submits text only to the configured non-executable provider boundary and displays the validated envelope. Nebius previews disclose that the prompt leaves the machine; no tool is executed.
- Capability registry panel in Settings: shows each registered capability's effect class, description, and blocking reason from the authenticated backend contract.

This is a functioning first slice, not the finished JARVIS vision. Nmap, SSH, coding execution, live news retrieval, Nebius/NVIDIA reasoning, memory skills, and autonomous computer control remain planned integrations.

Local implementation and dependency installation are authorized. Paid inference, live scans, remote access, and sensitive capture still need their specific scope and consent.

## Important Facts

- Submission deadline verified from official rules: October 30, 2026, 10:00 am Pacific Daylight Time, or 17:00 UTC.
- Requires a real Nebius Token Factory runtime inference call or execution on Nebius AI Cloud, and at least one NVIDIA open source model.
- Target: at least 90% verified task success on a defined held-out benchmark. This is not an achieved result or a probability of winning.
- Existing sibling project `../sudo/` is separate and must remain untouched. Its README describes an earlier personal assistant prototype.
- Current Windows workspace: `C:\Users\Erazer\OneDrive\Documents\sudo_x`. Original Linux workspace: `/home/salman/Documents/Python/sudo x/`. Quote paths in shell commands. Executable name: `sudo-x`, never `sudo`.

Research and planning date: September 7, 2026. Recheck rules and vendor documentation before implementation and submission.
