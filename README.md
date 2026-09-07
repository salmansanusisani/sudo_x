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

The backend environment and GUI dependencies must be installed first:

```bash
cd "/home/salman/Documents/Python/sudo x"
.venv/bin/python -m pip install -e '.[dev]'
cd ui
npm ci
npm run build
cd ..
./launch.sh
```

The launcher binds only to `127.0.0.1`, prints a private session URL, and opens a standalone Chromium app window when available. Do not share the printed URL. Run as a normal user, never with `sudo` or root. To run without opening Chromium, use `.venv/bin/sudo-x`.

To verify the current slice:

```bash
.venv/bin/ruff check src tests
.venv/bin/python -B -m pytest -q -p no:cacheprovider
cd ui && npm run test:e2e
```

## Current Implementation

- Futuristic local GUI with visual workspace, conversation panel, mission history, settings/privacy view, and execution trace.
- Offline geography globe focused on Nigeria with Abuja/Lagos reference points. It explicitly does not claim live news.
- Real read-only local system snapshot: OS, kernel, Python, CPU count, load, and memory from bounded local observations.
- Persistent local SQLite task/event history and restart reconciliation.
- Optional user-selected screen preview using browser permission. Frames remain in the local view and are not sent to AI; computer control is not implemented.
- Optional local browser speech narration if an available local voice exists. Microphone input is not accessed.
- Honest blocked states for general requests, live news, arbitrary shell, security tools, remote machines, and model reasoning.
- Same-origin loopback API with bearer session token, host/origin checks, security headers, request limits, and no external runtime assets.
- Versioned `/api/capabilities` registry and strict non-executable plan envelope. Disabled capabilities expose their effect and blocking reason; they cannot be activated by model output.
- Planner preview control: submits text only to the configured non-executable provider boundary and displays the validated envelope. In the default provider mode it returns an explicit blocked state; no tool is executed.

This is a functioning first slice, not the finished JARVIS vision. Nmap, SSH, coding execution, live news retrieval, Nebius/NVIDIA reasoning, memory skills, and autonomous computer control remain planned integrations.

The user requested planning first. Obtain explicit implementation approval before scaffolding, installing packages, starting services, or making paid API calls.

## Important Facts

- Submission deadline verified from official rules: October 30, 2026, 10:00 am Pacific Daylight Time, or 17:00 UTC.
- Requires a real Nebius Token Factory runtime inference call or execution on Nebius AI Cloud, and at least one NVIDIA open source model.
- Target: at least 90% verified task success on a defined held-out benchmark. This is not an achieved result or a probability of winning.
- Existing sibling project `../sudo/` is separate and must remain untouched. Its README describes an earlier personal assistant prototype.
- Folder: `/home/salman/Documents/Python/sudo x/`. Always quote the path in shell commands. Planned executable name: `sudo-x`, never `sudo`.

Research and planning date: September 7, 2026. Recheck rules and vendor documentation before implementation and submission.
