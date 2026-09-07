# SUDO X: Project Blueprint

Version: 3.0 | Updated: September 7, 2026 | Status: implementation authorized; first slice in progress

This is the implementation specification and decision record, not a report of working software. All product capabilities and performance numbers below are proposed unless explicitly marked verified. The user has now explicitly requested actual coding, beginning with a futuristic graphical application. Read HANDOFF.md for the actual implementation and test results. Permission to build is not blanket permission for paid inference, microphone/screen capture, remote access, scans, or privileged operations.

## 1. Executive Decision

Build **SUDO X: a Kali-native personal operator that understands your machines, writes and tests code, and helps secure your authorized systems, with memory and permissions you control.**

The initial audience is Kali/Linux developers, security learners, and homelab operators managing their own or explicitly authorized systems. Daily assistance remains essential, but OS understanding, coding, Nmap-backed security checks, and remote administration are first-class product pillars, not incidental extras.

The differentiator is **accountable delegation**: a user gives a goal and a scoped permission envelope; the assistant observes, proposes, acts, checks, and leaves a readable task receipt. After a successful workflow, it can offer a reusable, reviewable skill. Tomorrow it remembers how the user wants that workflow done.

The ambitious vision is a JARVIS-like operator spanning personal work, coding, and security. The hackathon release combines four signature workflows, with one integrated security-to-code demonstration, rather than attempting to demonstrate every installed Kali tool. A voice interface alone, a large tool list, or a chat window wrapped around shell access will not make a compelling entry.

Version 2 incorporates the user's request for broader Kali expertise, Nmap, remote security work, and code creation. The user explicitly said not to constrain ambition around their available time. Work is therefore ordered by capability and safety gates, not an assumed weekly time budget; the official submission deadline still applies. This request expands the plan, not authorization to start scanning, connecting to machines, or building software.

### The Product Promise

> Tell SUDO X what outcome you want. It works inside the boundaries you choose, checks its work, and tells you exactly what happened.

### What We Can And Cannot Promise

- We can design for measurable reliability and a strong submission against published criteria.
- We cannot honestly assign a 90% chance of winning. Competitors, judges, and final execution are unknown.
- We will use 90% as an engineering target for a declared task distribution, not universal intelligence or command accuracy.
- Good scaffolding improves tool use, recovery, and reliability. It cannot make a weak model equal to every frontier model at every task.
- Public decision summaries and evidence are useful. Fabricated internal reasoning traces, unlimited reflection, and claims of copying another model's private reasoning are not.

## 2. Verified Hackathon Requirements

Sources were retrieved September 7, 2026. Official rules take precedence over marketing copy and this document.

| Item | Verified requirement or detail | Project implication |
| --- | --- | --- |
| Event | Nebius x NVIDIA Global AI Hackathon | Submit under this event, not a similarly named event |
| Submission period | Aug 26, 2026, 09:00 Pacific through Oct 30, 2026, 10:00 Pacific | Preserve dated development history |
| Deadline | Oct 30, 2026, 10:00 PDT = 17:00 UTC | Internal submission target Oct 27 |
| Judging | Dec 1, 2026, 09:00 Pacific through Dec 15, 2026, 12:00 Pacific | Keep the test build/demo free and available through judging |
| Winners | On or around Jan 11, 2027 | Do not confuse submission with winner announcement |
| Infrastructure | Runtime Token Factory inference call OR run/deploy on Nebius AI Cloud compute | Local machine control plus real Token Factory inference is a valid architecture |
| Models | At least one NVIDIA open source model | NVIDIA model must do meaningful work, not a decorative ping |
| Personal AI | Always-on, private assistant, persistent memory, reusable skills, selected tools/data, daily workflows | Demonstrate all of these, not only coding |
| Suggested technologies | NemoClaw, OpenShell, Hermes Agent, Nebius Serverless mentioned as examples | Text does not explicitly require every named framework; ask organizer if uncertain |
| Working access | URL to working demo, hosted app, or test build | Supply an installable release plus clear testing instructions; ideally a safe hosted demo |
| Source | Public GitHub/GitLab/Bitbucket repo with all necessary code/assets/instructions | Include an actual detectable LICENSE file, not only a README claim |
| Video | Public YouTube demonstration, rules say less than 3 minutes | Target 2:45; English audio explains Nebius and NVIDIA usage |
| Description | Features, purpose, how it works, selected track | Build a concise, specific narrative |
| Feedback | Feedback on Nebius and NVIDIA technologies used | Keep an evidence-based feedback log during development |
| Existing work | Explain substantial changes during the submission period if based on prior project | Be transparent about the older SUDO prototype |
| Access through judging | Free testing/evaluation access until judging ends | Do not rely only on judges supplying a paid API key |
| Eligibility | Age of majority, residency/legal and conflict-of-interest restrictions | User must check personal eligibility; do not infer it from files or timezone |

The rules explicitly list excluded jurisdictions including Brazil, Quebec, Russia, Crimea, Cuba, Iran, and North Korea, plus other legal/sanctions restrictions. This is not an exhaustive legal eligibility assessment. Read the full rules.

### Judging And Prize Strategy

Four criteria are equally weighted: Technological Implementation, Design, Potential Impact, Quality of the Idea. Tie-breaking compares them in that order.

| Criterion | What our entry should prove | Concrete evidence |
| --- | --- | --- |
| Technological Implementation | Real model/tool loop, enforced permissions, durable jobs, verification | Runtime provider trace, failure recovery, test results, reproducible install |
| Design | A complete experience rather than a research script | Onboarding, useful defaults, approval preview, visible progress, honest completion states |
| Potential Impact | Saves recurring work for a specific audience | Interviews, before/after task timing, repeat-use pilot observations |
| Quality of the Idea | Accountable delegation and reusable personal workflows | Watch-to-action workflow, explicit memory source, receipt, reviewed skill reuse |

Overall prizes shown: $20,000 first, $10,000 second, $6,000 third. Personal AI Track prize: one NVIDIA Jetson Orin Nano, not a separate cash prize. Rules state one overall OR one track award, and one bonus award per project. Best Use of Tavily requires functional runtime Tavily usage; add it only if it improves an actual workflow.

Resources advertise $25 Token Factory credits using activation code `NEBIUS-DEVPOST-GLOBAL26` and another $25 through the Builders Program. Availability and redemption are not verified for this user. Do not assume credits have been claimed or auto-enable paid overflow.

There is a source conflict: resources say attendance is unnecessary for a City Winner Award; official rules say those awards are for entrants attending participating IRL events. Rules prevail; request organizer clarification before claiming eligibility.

## 3. Existing Work And Machine Constraints

Verified locally during planning:

- Parent folder exists: `/home/salman/Documents/Python/`.
- Sibling `sudo/` contains an earlier Python assistant and README. It was not modified or executed.
- Its README describes voice interaction, Groq inference, optional other providers, application/command actions, JSON memory, and reminders. These are documented claims, not independently tested capabilities.
- Its README records a past problem with always-on voice due to ambient noise. Avoid making wake-word quality the critical path.
- The machine reported Python 3.14.6, about 7.7 GiB RAM, and four logical CPUs. Docker executable was present. Runtime readiness was not tested.
- NVIDIA GPU availability is unverified: the attempted query produced no usable GPU information. Do not conclude a suitable GPU exists.

Decisions:

- New directory and clean architecture. Do not import or execute the old module: its module-level behavior has not been audited.
- Do not read or migrate legacy personal memories, API keys, config, histories, or logs without a specific user request.
- If code is reused later, audit it, preserve applicable license notices, record original provenance, and disclose the pre-event baseline and substantial new work honestly.
- Prefer cloud NVIDIA inference for this hardware. No local large-model requirement, no fine-tuning in MVP.
- Target an isolated Python 3.12 environment initially for broad dependency compatibility; verify availability before choosing 3.12/3.13. Do not downgrade or replace system Python.
- Use one worker and at most one browser/sandbox initially. Measure memory use before adding parallel workers or local speech models.

## 4. Four Signature Workflows

### A. Prepare My Work Session

Example: "Get my course project ready. Find the latest notes, open the project and reference links, and give me the three things I should do next."

Inputs: an explicitly enrolled project directory, user-pinned URLs, a preferred editor from an approved app list, and remembered project preferences.

Execution: inspect allowed files and git metadata; distinguish actual unfinished tasks from suggestions; generate a source-linked brief; request approval before launching selected apps; open approved resources; report which actions were verified and which only had a successful launch request.

Acceptance: references resolve to actual permitted files; no home-directory sweep; no secrets in cloud payloads; correct project/app selection; restart preserves approved preferences. If desktop integration cannot confirm the window opened, say "launch requested", not "verified open".

Why it belongs in Personal AI: joins personal context, persistent preferences, files, apps, and an everyday routine. It is not simply a coding agent.

### B. Take Care Of This Folder While I Am Away

Example: "Watch this research inbox. When new notes arrive, create a summary and propose where they belong. Never delete originals."

Inputs: a user-selected inbox, approved output root, file-type/size limits, schedule, notification preference, cloud disclosure choice.

Execution: debounce stable file changes; create one durable job per content version; read allowed plain text/Markdown; treat file instructions as untrusted content; write a digest into the allowed output area; propose file organization; require exact approval for original-file moves; leave a receipt and notification.

MVP handles text/Markdown only. PDF parsing is a post-core addition in an isolated parser, with malformed/oversized-file tests. Do not promise all document formats.

Acceptance: one digest per stable version; original bytes unchanged in automatic mode; paused watcher does nothing; revoking a folder stops queued jobs too; malicious note cannot authorize a tool call or disclosure; restart does not duplicate output.

This is the first always-on implementation slice; workflow D extends it with explicitly scheduled security observations. Always-on means a background service driven by events or approved schedules, not constant microphone recording, screenshots, or paid model polling.

### C. Build, Diagnose, And Prove It

Examples: "Build a small dashboard for my lab services, with tests" and "This project stopped working. Work out why, try a fix safely, and show me the test before changing my files."

Inputs: a selected project or managed new-project directory, requirements, acceptance criteria, a declared test command, a task budget, and bounded write permissions. Code creation includes implementation, tests, debugging, documentation, and an inspectable diff, not merely emitting a code block.

Execution: inspect relevant code and constraints; snapshot/copy explicitly allowed files into an isolated workspace; reproduce a reported failure or define independently reviewable checks for a new feature; implement in small slices; run protected checks; show diff and evidence; request exact approval before applying to originals; revalidate source hashes before applying. Commit, push, pull-request creation, and deployment remain separately authorized operations.

Acceptance: a reported failure is reproduced or a new feature meets explicit requirements; trusted tests pass, tests were not weakened, original user edits survive, and changed originals invalidate old approval. Agent-authored tests are useful but are not independent proof by themselves. If no safe sandbox is available, offer diagnosis/code drafts only and label them unexecuted; never fall back to host execution.

This shows intelligence through experiment and verification. It is a supporting workflow, not the entire entry. Do not let it absorb the time needed for memory, routines, and product design.

### D. Watch My Lab, Investigate Changes, And Help Fix Them

Example: "Watch my enrolled lab server. If its exposed services change, explain what changed, investigate through my approved connection, and prepare a tested fix. Ask before changing the server."

Inputs: explicitly enrolled asset and authorization record, approved scan profile/ports, observation vantage point, scan schedule and traffic budget, pinned SSH host identity, approved diagnostic tools, and separate remediation permission.

Execution: compare a complete current Nmap observation with a comparable baseline; notify about a new reachable service; use bounded remote diagnostics to investigate the relevant user-owned application; connect the finding to its enrolled repository only when supported by evidence; propose and test a code/configuration change in a copy; show the diff, expected effect, health checks, and rollback limits; apply only after exact approval; verify both intended application health and network exposure from the original vantage point.

Acceptance: only approved targets receive probes; incomplete/failed scans never imply services disappeared; banners cannot instruct the assistant; source-to-service links have provenance; the fix does not interrupt the management connection; application health remains good; a repeat scan supports the narrowly worded conclusion. "No longer reachable from this scanner on these ports" is defensible. "The server is now secure" is not.

This is the flagship demonstration for version 2. Implement with an owner-controlled isolated lab service using an unprivileged test port. Do not expose a vulnerable app to the public Internet for the demo. See section 20 for the detailed security and remote-access contracts.

### Repeat-Use Moment

After B succeeds, offer: "Save this as a skill for this inbox?" Show triggers, inputs, allowed tools, destination, disclosure settings, and checks. User confirms. On a later file, the approved skill runs under the same or narrower grants. New destinations or capabilities need new consent.

## 5. Scope And Cut Line

### Must Ship

- Text goal entry, task timeline, cancellation, and readable completion receipts.
- One genuine NVIDIA model through Nebius Token Factory.
- Typed tools, deterministic permission broker, preview/approve flow, and enforceable isolated code execution if workflow C ships.
- Local persistent memory with provenance, correction, and deletion.
- Explicit watcher/scheduled routine that survives application restart.
- Reviewed reusable skills, initially human-authored plus one workflow-to-skill proposal path.
- Four workflows above, including new code creation and a real scoped Nmap/remote-lab workflow. If a gate fails, disclose the reduced release scope rather than pretending the capability works.
- Kali capability inventory, version-aware tool registry, authorized asset registry, and comparable scan baselines.
- Reproducible evaluation and honest demo build.

### Should Ship After Core Gates

- Push-to-talk and optional speech output with text as a complete fallback.
- Actual NVIDIA OpenShell integration if compatibility/resource spike passes.
- Controlled browser read/navigation for known public sites, using a dedicated profile.
- PDF support, user-friendly desktop notifications, basic tray affordance.
- One measured model escalation path if it improves reliability per dollar.

### Explicitly Not MVP

- Arbitrary root/sudo actions, generic unrestricted host shell, self-modifying runtime, or automatic plugin installation.
- Universal GUI control, unrestricted screen streaming, or arbitrary logged-in browser operation.
- Autonomous exploitation, credential extraction, scanning without explicit target authorization, persistence/evasion tooling, or password cracking. Authorized Nmap inventory and defensive remote diagnostics are explicitly in scope.
- Payments, email sending, social posting, deleting arbitrary user files, or unattended system package upgrades.
- A multi-agent swarm, vector database, Kubernetes deployment, full mobile app, or local frontier model.
- Importing the user's entire home folder as memory.

Capability access can grow after the hackathon through narrowly scoped adapters. More power should mean more explicit scope and verification, not fewer safeguards.

## 6. System Architecture

```text
Local browser UI (same origin, authenticated)
             |
Local API + durable task engine (normal user, not root)
             |
   +---------+-------------+----------------+
   |                       |                |
Local memory/skills   Context gateway    Event watchers
SQLite + artifacts    and disclosure     + durable queue
                           |
                    Nebius Token Factory
                    NVIDIA model plans
                           |
                    Proposed typed actions
                           |
                  Deterministic policy broker
                  grants + exact approvals
                           |
            +--------------+----------------+
            |                               |
Narrow host adapters                Isolated executor
files/apps/notifications             copy-only code/tests
            |                               |
            +---------- Tool results -------+
                           |
               Independent outcome checks
                           |
                  Local receipt + UI
```

The broker also dispatches a separate typed network scanner and remote adapter to enrolled assets. These have destination-limited egress and task capabilities; they do not grant network access or SSH credentials to the code sandbox. A credential broker supplies opaque remote identities to the connector, never to model context. The remote side must enforce permissions too; see section 20.

### Stack Decisions

| Layer | Initial choice | Reason / constraint |
| --- | --- | --- |
| Runtime | Python, asyncio, explicit state machine | Small, inspectable control flow; no framework requirement |
| API | FastAPI + Pydantic v2 | Typed boundaries and generated API schema |
| Model client | OpenAI-compatible SDK targeting Nebius | Provider protocol, not OpenAI-hosted inference |
| Persistence | stdlib sqlite3, WAL, versioned migrations | One machine, one user, no external DB needed |
| Frontend | React + TypeScript + Vite; built assets served by FastAPI | Responsive, polished local control surface, one production origin |
| Events | watchdog plus durable SQLite schedule records | Event-driven, no idle inference polling |
| Testing | pytest, Ruff, targeted type checking; Playwright for UI | Verify policies and workflows before aesthetics |
| Isolation | Rootless container executor if supported; OpenShell spike | Never treat a Python subprocess as a sandbox |
| Distribution | Python package + bundled UI build + optional user service | Do not require Node at runtime for judges |
| Memory search | SQLite FTS5 and explicit metadata | No embeddings until retrieval evidence justifies complexity |

Keep dependencies few and pinned in lockfiles when implementation starts. Do not build a generic agent framework or plugin marketplace.

### Framework Tradeoff

OpenShell's official README describes filesystem/network/process policies and controlled inference routing. It currently labels the project alpha. NemoClaw is a reference stack for supported agents inside OpenShell, including onboarding, managed inference, policies, and lifecycle operations; its README also calls it alpha.

Decision: own the small product-specific task loop and broker. Timebox an OpenShell integration spike to one working day. Adopt it only after proving restricted filesystem access, blocked egress, cancellation, Nebius routing, and acceptable resource use on the actual machine. Pin a tested release. Do not layer NemoClaw, Hermes, OpenClaw, and a custom loop together without a demonstrated need.

Fallback: a narrowly configured rootless container executor for project-copy execution, with networking disabled and no host credentials. This is not permission to skip isolation. If neither path works, cut arbitrary project execution instead of running it on the host. Cloud sandboxes are a later opt-in alternative because uploading project copies changes the privacy boundary and may add cost.

OpenShell does not automatically secure host-side app/file adapters. Their permissions and checks remain our responsibility. Avoid inherited automatic credential discovery. Disable optional telemetry where supported and disclose the actual configuration.

## 7. Model Integration And Capability Selection

Verified API base: `https://api.tokenfactory.nebius.com/v1/`.

Verified model discovery: authenticated `GET /models` or SDK `client.models.list()`. Verbose model metadata may include context limits, pricing, and rate limits. Documentation examples are not a current model catalog.

The event mentions Nemotron Ultra, Super, and Nano. Exact serving IDs, availability, tool-call behavior, pricing, and context limits were NOT verified with this user's account. Never invent an ID or silently replace NVIDIA with a nonqualifying model.

### Selection Procedure

1. With user approval and a configured key, discover current available NVIDIA models and inspect their model cards/licenses.
2. Run a small capability probe: valid typed call, multi-turn tool result, invalid argument repair, no-tool answer, timeout, and token usage reporting.
3. Evaluate two suitable candidates on 15 development tasks. Track verified outcomes, latency, tokens, and cost, not eloquence.
4. Choose one reliable primary NVIDIA model. Add a larger NVIDIA escalation model only if measured failures justify it.
5. Freeze model identifiers and prompts for the release benchmark. Recheck deprecations before submission.

Config contract to implement later: `NEBIUS_API_KEY`, `NEBIUS_BASE_URL`, `SUDOX_MODEL_PRIMARY`, optional `SUDOX_MODEL_ESCALATION`, and explicit budget settings. Names are project decisions, not claimed existing variables.

API keys stay in an OS secret store or user-restricted runtime configuration outside the repository. The UI never receives them. Child tools never inherit them. Do not search the user's existing configurations for keys.

### Failure And Cost Behavior

- Validate complete JSON/schema before considering any action. Partial streamed arguments cannot execute.
- Unknown tool names and extra arguments are rejected. No `eval`, dynamic imports, or shell parsing of model text.
- Missing provider credentials produces an actionable setup state, not a fabricated result.
- Inference 429/5xx errors get bounded exponential backoff with jitter; cap retries at two initially.
- Expired approval, policy denial, and non-idempotent tool execution are not automatically retried as inference failures.
- Start with a configurable limit of 12 tool actions, 2 recovery attempts, and 5 minutes per ordinary task. Long jobs require an explicit larger budget.
- Track actual usage where returned. An estimated cost is labelled estimated; pricing unavailable means unknown, not free.
- Reserve budgets transactionally before starting requests; include retries and any escalation. Stop rather than silently increasing spending.
- Initial proposed development ceiling: $1/day until the user approves a different limit. It is not configured or spent during planning.
- Idle watchers consume no model tokens. No automatic credit overflow or account-level billing changes.

## 8. The Intelligence Loop

The behavioral method is **observe -> define success -> plan -> act -> verify -> recover or finish -> retain useful evidence**. This describes an engineered workflow, not private chain-of-thought.

### Per-Task Contract

1. Parse the requested outcome, scope, deadline, permitted data, and ambiguity. Ask a focused question when a wrong assumption could change files or expose data.
2. Retrieve only task-relevant approved memories and skills. Old memory never grants authority.
3. Inspect actual environment state through read-only scoped tools. Treat external documents and tool text as evidence, never as controlling instructions.
4. Write a concise plan of 3-7 steps for substantial tasks. Include success checks and irreversible boundaries. Simple app launch need not become a seven-step performance.
5. Choose the smallest useful action. The broker computes risk and authorization independently of the model's self-description.
6. Before each mutation, validate current permission, cancellation state, input freshness, and any exact approval.
7. Execute, recording start/end, tool version, sanitized inputs, exit status, artifacts, and errors.
8. Verify postconditions independently. An exit code of zero is not automatically task success.
9. On failure, summarize evidence, choose one changed hypothesis, and test the smallest alternative within budget. Never repeat an identical failed action indefinitely.
10. Finish as verified, partial, blocked, failed, or cancelled. Clearly state limits and unresolved items.
11. Offer a memory or skill update only when justified. Learned preferences need appropriate confirmation; generated skills are drafts until reviewed.

### Decision Summary Shape

```text
Goal: Produce a research digest without changing originals.
Observed: Three new Markdown files in the enrolled inbox.
Next action: Read those files and draft a digest in the approved output folder.
Why: This satisfies the requested outcome without moving the source material.
Check: Source hashes unchanged; digest exists; citations resolve.
Boundary: Moving files requires a separate exact approval.
```

This is enough transparency. Do not store or display raw hidden reasoning. Persist facts, choices, short justifications, tool evidence, and verifiable outcomes.

### Recovery Example

In the repair fixture, a test fails due to a mismatched config path. The assistant reads the failure, checks the directory layout, changes only the path in a sandbox copy, and reruns the immutable verification test. If it fails again, it inspects the new result. It does not delete tests, install arbitrary packages, or declare success based on its own explanation.

For unknown post-crash tool outcomes, inspect state before retrying. Exactly-once external side effects cannot be guaranteed by a task queue alone.

## 9. Permissions, Privacy, And Threat Model

### Trust Boundaries

- Trusted authority: explicit authenticated user instructions, reviewed policy configuration, and deterministic broker code.
- Untrusted: model output, file contents, retrieved websites, repository instructions, generated skills, subprocess output, and external API responses.
- Host adapters are trusted code with narrow capabilities, not model-generated code.
- Same-user malware, a compromised kernel, and a malicious local administrator are outside the MVP protection claim. State this openly.

### Permission Levels

| Level | Example | Default |
| --- | --- | --- |
| Read within granted scope | List selected folder, inspect selected repo | Allowed only after folder enrollment; cloud sharing remains separate |
| Reversible draft in managed area | Create digest or sandbox patch | Allowed within task/routine capability and quota |
| User-visible host effect | Launch app, move original, apply patch | Exact preview and approval, or explicitly reviewed narrow standing grant |
| Active security observation | Nmap probes on enrolled assets | Explicit target/profile/window/traffic grant; not classified as passive local reading |
| Remote application change | Apply a reviewed user-owned app config | Exact asset-bound approval, freshness checks, health verification; no general privileged shell |
| Sensitive or broad action | Access credentials, root command, arbitrary host shell, system security change | Unsupported/denied in MVP |

An approval is bound to task ID, tool name/version, canonical arguments, artifact/diff hash, source preconditions, grant version, expiration, and one-time consumption. Changed parameters invalidate approval. The model cannot approve itself, lower risk, create a new grant, or mark an action verified.

Standing grants must be specific: "create Markdown summaries in this output folder for this inbox, at most ten per day" is acceptable. "Do anything you need forever" is not.

### Filesystem Rules

- Start with no user folders enrolled. Scope file operations to configured roots, not all Documents or home.
- Exclude secret stores, dotfiles, `.env` variants, SSH keys, browser profiles, credential files, and hidden control directories by default even inside an enrolled project.
- Use safe path resolution and descriptor-relative operations; reject traversal, symlinks, and non-regular files for MVP tools. Recheck at execution time to address symlink/race changes.
- Model-supplied paths are never sufficient authority. Prefer opaque artifact/root IDs with broker-owned path mapping.
- Treat hard links, archive extraction, and recursive directory copying as separate attack surfaces. Exclude hard-linked source files where appropriate; do not implement arbitrary archive extraction in MVP.
- Bound file count, depth, individual bytes, aggregate bytes, and output size. Initial proposals: 1 MiB per text file, 20 files per job, 5 MiB aggregate read payload before reduction.
- Create generated files atomically and avoid overwrite by default. Existing-target conflicts require a new name or explicit approval.
- Host patch application requires source-hash match and a stored backup or reversible patch. Undo is conditional: refuse to overwrite subsequent user edits.
- No claim of universal rollback. Opened apps, notifications, network disclosures, and external transactions cannot be fully undone.

### Execution Isolation

- Arbitrary code and tests run only in an isolated copy, never the original project or host shell.
- Rootless container: read-only root filesystem, non-root user, dropped capabilities, no-new-privileges, strict mounts, PID/CPU/memory/time limits, no Docker socket, no host device or desktop socket, no credentials, and network disabled by default.
- `shell=False` and an executable allowlist help typed host tools but do not sandbox interpreters. A Python or shell interpreter can still do arbitrary work if given code.
- Do not pass through inherited environment variables. Build a minimal environment.
- Dependency installation is an explicit separate operation; prefer pinned prebuilt demo fixtures and no network during tests.
- Container isolation is defense in depth, not an absolute guarantee against kernel exploits. Use synthetic code in public demos.

### Cloud Data Boundary

Call the product **local-first with consented cloud reasoning**, not fully offline or "no data ever leaves".

Data flow: authorized local extraction -> selection/minimization -> secret filtering -> disclosure approval or standing disclosure grant -> provider request. Derived summaries inherit the source's sensitivity until explicitly reviewed. Local-only data cannot be silently summarized and uploaded.

Labels: `local_only`, `cloud_allowed`, and `secret_blocked`. Read permission is separate from cloud permission. Credentials remain blocked even when the enclosing folder is cloud-allowed.

Show a "What leaves this machine" panel with provider, model, selected excerpts, and reason. Redaction is a secondary check, not a proof that arbitrary data is safe. Disable third-party tracing/prompt logging by default. Use synthetic demo data.

Nebius's Legal Quick Guide says default behavior may retain prompts/responses for speculative decoding; organization-level Zero Data Retention can be enabled through account settings. Require the owner to verify ZDR and applicable binding terms before processing personal content. Do not claim it is enabled merely because our app has a checkbox. Record manual verification as such, never as API-attested status without an actual supported API.

In local-only/offline mode, existing deterministic approved routines, local search, and receipts can remain usable. New cloud reasoning tasks pause or ask for consent; no promise of an equivalent offline LLM on this hardware.

### Browser And UI Safety

- Bind local API to loopback only. Authenticate reads, mutations, and streaming endpoints; enforce Host/Origin checks, same-site cookies, CSRF defenses for cookie-authenticated mutations, and no permissive CORS.
- Use a one-time local pairing flow; no persistent bearer secrets in URLs, localStorage, screenshots, or logs.
- Escape tool output and render sanitized Markdown; never run embedded HTML/scripts from documents or model responses.
- Approval endpoints are not model tools and are inaccessible to sandbox processes.
- Optional browser automation uses a dedicated empty profile. MVP navigation is public/read-only. Block `file:`, `javascript:`, local-network/metadata URLs, dangerous downloads, and redirects to denied targets.
- A web fetcher must validate resolved IPs and redirects, not only URL strings, to limit SSRF and DNS-rebinding exposure.
- Desktop adapters must not expose a terminal launch with arbitrary arguments as a disguised shell tool.

The browser/fetcher local-network deny rule does not prohibit a separately authorized security adapter from inspecting enrolled private assets. Separate tool identities and egress policies prevent web content from borrowing the scanner's permissions. Personal remote control, if enabled later, follows section 20; it never changes the default loopback-only listener.

### Memory And Local Storage Protection

Use user-private directories and files, no raw secrets, bounded retention, export/delete controls, and OS full-disk encryption where available. SQLite itself is not encrypted by default; do not claim application-level encryption without implementing it. Explain backup and deletion limitations, including WAL and backup copies.

Deletion must remove active memory, search index entries, cached summaries, and derived references or mark dependent summaries for rebuild. Keep minimal non-content audit metadata only with a documented retention rule.

### Emergency Stop

Visible "Pause all" blocks new jobs and actions immediately. Cancel running managed process groups with a bounded grace period, revoke pending approvals, and record partial effects. Do not imply stopping the assistant undoes changes already committed. User can disable its user-level service without root.

## 10. Memory, Skills, And Always-On Operation

### Memory Records

Fields: ID, kind, content, source reference, scope, sensitivity, confirmation status, created/updated timestamps, expiry, supersedes ID, and schema version.

Kinds: explicit preference, confirmed project fact, episodic task summary. Do not store speculative personality assessments or convert a webpage instruction into a user preference.

Retrieval order: explicit task parameters first, current confirmed scoped preferences second, relevant evidence third. Resolve contradictions by asking or using the newest explicitly confirmed fact; do not silently overwrite.

### Skill Contract

Fields: ID/version, description, typed inputs, allowed trigger types, prerequisites, ordered typed steps, capability requirements, disclosure requirements, verifiers, budgets, failure behavior, author/provenance, review status, and content hash.

MVP skills are declarative templates invoking existing tools, not arbitrary downloaded Python. Parameter expansion must preserve scope validation. Skills cannot alter policies, install dependencies, or grant themselves authority.

Lifecycle: draft -> human-reviewed -> enabled -> suspended/retired. A generated update creates a new draft version. Verified successful runs can motivate suggestions but never auto-promote authority.

### Service Lifecycle

Use a user-level systemd service after explicit installation approval. Starting at login is enough for MVP. Running while logged out may require user lingering and has power/privacy implications; do not enable it implicitly. A sleeping or powered-off laptop cannot execute work. Explain missed-schedule behavior after resume.

Queue jobs in SQLite with a lease and heartbeat. Persist before executing. Deduplicate watcher jobs using routine ID + canonical source ID + stable content hash. Debounce proposed initial 2 seconds and verify stable size/hash before reading. Exclude generated output directories to prevent loops.

Use UTC internally and an explicit user timezone for scheduling. Store the intended local schedule and define DST/missed-run policy. Proposed policy: coalesce missed routine triggers into one current run after resume; do not replay every missed minute.

One active mutation task per resource scope initially. Read-only work may later parallelize after tests. Pending user approval is a persisted waiting state, not a model polling loop. A routine needing new consent waits and notifies once.

## 11. Data And API Contracts

These are design contracts, not existing endpoints or migrations.

### Main Tables

| Table | Core fields |
| --- | --- |
| tasks | id, goal, origin, status, created_at, deadline, budget, grant_version, lease, result_summary |
| task_events | task_id, monotonic_sequence, event_type, timestamp, sanitized_payload |
| tool_runs | id, task_id, tool, version, args_hash, status, start/end, error_code, idempotency_key |
| artifacts | id, task_id, managed_path, content_hash, media_type, sensitivity, source_refs |
| grants | id, roots, tools, effects, disclosure_scope, limits, version, expiry, revoked_at |
| approvals | id, task_id, action_hash, preconditions, expiry, consumed_at, decision |
| memories | fields from section 10, with search index |
| skills | id, version, manifest, review_status, content_hash |
| routines | id, trigger, skill_version, scope, grant_id, timezone, enabled, last_trigger |
| usage | task_id, provider, model, tokens, latency, price_snapshot, estimated_cost |
| assets | id, label, endpoint identities, ownership/authorization reference, environment, connection identity, scope version, expiry |
| observations | asset_id, tool/version, profile_hash, vantage_id, coverage, timestamp, completion, artifact_id |
| findings | asset_id, claim, evidence_refs, validation_state, priority_rationale, first/last_seen, disposition |
| capability_checks | machine_id, tool/version, permitted_adapter, tested_operations, last_check, status |

Use foreign keys, transactional state transitions, schema migrations, and uniqueness constraints for idempotency. Artifacts live outside the public repo. Logging is application append-oriented, not tamper-proof against the same OS user; avoid stronger claims.

### Task States

`queued -> observing -> planning -> awaiting_approval -> executing -> verifying -> completed`

`planning` may go directly to `executing` for granted actions. `verifying` may lead to a bounded recovery plan. Any nonterminal state may become `blocked`, `failed`, `cancelled`, or `partial` as appropriate. `paused` preserves resumable work. Terminal completion requires recorded verifier evidence; model text cannot directly set it.

After crash/restart, expired leases become `interrupted` for reconciliation. Inspect effects before retrying. A host mutation without proven idempotency never receives blind replay.

### Tool Result Envelope

```json
{
  "tool_run_id": "run-example",
  "status": "succeeded",
  "summary": "Draft digest created in the managed output area.",
  "artifact_ids": ["artifact-example"],
  "observations": {"source_count": 3},
  "error_code": null,
  "retryable": false,
  "side_effects": ["created_managed_file"]
}
```

Bound and sanitize outputs before sending them to the model. Preserve full eligible artifacts locally with retention controls, not unbounded prompt transcripts.

### Initial Tools

| Tool | Effect | Verification |
| --- | --- | --- |
| files.list/read/search | Scoped reads | Returned sources inside granted roots |
| artifacts.write | Managed output only | File exists, hash and expected schema/content checks |
| git.inspect | Selected repository metadata, no mutation | Actual command/result metadata; disable unsafe config/hooks where relevant |
| apps.launch | Approved application + typed allowed target | Launch acknowledgement; window verification only when supported |
| system.snapshot | Bounded CPU/RAM/disk info | Actual sampled metrics and timestamp |
| sandbox.run | Copy-only approved test or bounded code action | Exit status, protected verifier results, artifacts |
| patches.propose/apply | Propose diff / approved original edit | Source hashes, approved diff, postconditions |
| notify | Local notification | Delivery request result, not assumed user read |
| memory.propose | Draft memory record | Confirmation before durable user preference change |
| network.scan | Typed Nmap profile on approved exact targets | Structured complete output, enforced egress, target/profile/coverage metadata |
| remote.inspect | Pre-enrolled host diagnostics | Host identity, bounded typed results, task nonce, permission checks |
| remote.apply | Approved user-owned app patch/reload | Exact artifact/source hashes, remote approval validation, health and exposure recheck |

Tool registries declare effect classes and argument schemas. Do not offer a generic host `run_command` tool. `git.inspect` still needs care: repository config and external helpers can execute programs, so constrain command options/environment and run risky repository operations in isolation.

### UI API Outline

- `POST /api/tasks`, `GET /api/tasks`, `GET /api/tasks/{id}`.
- `GET /api/tasks/{id}/events` via authenticated SSE with sequence-based resume.
- `POST /api/tasks/{id}/cancel`, `POST /api/control/pause`.
- `GET /api/approvals`, `POST /api/approvals/{id}/decision` with exact action binding.
- Authenticated CRUD for memories, routines, and grants; reviewed transitions for skills.
- `GET /api/privacy/status`, `GET /api/usage`, and sanitized health/capability status.

Replayed or stale approval decisions return a conflict and cannot execute twice. SSE must resume persisted events rather than fabricate progress. Serving user artifacts requires authorization and safe content disposition.

## 12. Product And Interaction Design

Visual direction, revised by explicit user request: a futuristic graphical command center with a cinematic spatial stage, rich globe/map views, live execution evidence, and conversation beside the action. Use deep ink surfaces, precise cyan light, warm amber attention states, restrained grid/orbital geometry, readable typography, and subtle motion. The user wants visual ambition inspired by JARVIS; avoid copying Marvel assets, movie audio, or illegible ornamental HUD clutter. This supersedes version 2's restrained-dashboard-only direction.

Primary layout: a goal input above an active task timeline; supporting areas for approvals, routines, memory, skills, and privacy. Chat is an input method, not the entire product.

### Visual Application Contract

- App experience: standalone desktop-style window with responsive GUI. Initial implementation is a local web UI served by the Python backend, runnable in Chromium app mode; native packaging follows a tested shell integration. Do not describe browser app mode as a finished native desktop package.
- Layout: slim navigation rail; mission header; central visual stage; conversation/command pane; real task evidence timeline; explicit capability/privacy state.
- Scene types: overview/globe, geographic briefing, real local system snapshot, user-shared screen, and later code diffs, terminal tool output, asset/service relationships, and scan comparisons.
- A scene uses a typed schema referencing task IDs, source artifacts, timestamps, and permission state. Model output chooses only approved scene types and validated parameters; never arbitrary HTML, JavaScript, iframe, shell, or remote URL rendering.
- Nigeria example: a globe focuses on Nigeria and identifies Abuja/Lagos, then sourced headlines appear and narration refers to their citations. Country geometry must come from an attributed geographic dataset. Distinguish publication time, retrieval time, article location, and approximate country centroid. A location visualization does not establish where an event occurred.
- First slice may show offline geography with an explicit label and blocked news result. Do not invent current headlines, imply web searches happened, or claim the offline demonstration fulfilled a news request.
- Later news adapter: approved provider/source fetch, bounded results, source URLs/publish timestamps, deduplication, conflicting-claim handling, and quoted content treated as untrusted. Unknown event coordinates stay unknown. Map tiles/search/speech providers need disclosure consent; prefer bundled map geometry for offline privacy.
- Narration: user-initiated, interruptible, synchronized to cited scene facts. Initial optional speech output uses only browser voices marked local. Speech input is not enabled until its local/cloud processing is implemented and disclosed.
- Watch the work: expose actual tool start/end/results, file diffs, scanner evidence, and supported browser screenshots. Never animate a fictional terminal or cursor as though the computer is executing actions.
- Live desktop view: user explicitly selects a display/window through the browser/OS capture dialog; persistent sharing indicator and Stop button; video stays in the local UI, with no frames uploaded, saved, or sent to the model by default. Screen viewing does not grant control or perception to the model.
- Empty/unavailable states must be designed, not hidden: no connected model, no selected screen, unsupported microphone, offline sources, expired session, disconnected backend, and interrupted task.
- Accessibility: keyboard/focus support, reduced-motion scene transitions, readable contrast, semantic controls, and mobile layout. Idle visuals have no inference cost and must not imply autonomous activity.

Implementation sequencing decision: the user requests a GUI-first start. Build a real local snapshot -> durable task/events -> visual result slice and a clearly labelled offline map while model account/budget and sandbox gates remain open. This does not mark the entire M0/M1 complete. Use authenticated polling first; durable event IDs allow migration to SSE when long-running tools justify it. No simulated waits solely to make the agent look busy.

Every task card shows outcome, scope, current phase, changes, verification evidence, and cost when known. Approvals show exact affected paths, before/after diff, why approval is required, and whether undo is available. Keep destructive actions out of the MVP rather than hiding them behind a vague warning.

First-run flow: explain local/cloud split -> configure provider without exposing key -> select allowed folder -> choose cloud disclosure mode -> show grant summary -> run synthetic safe example. No automatic home scan, microphone access, service installation, or app launch.

Desktop and mobile-width layouts must load cleanly. At narrow widths use one column and a compact navigation drawer. Remote control is a separate explicit opt-in, not a consequence of responsive layout; see section 20. Keyboard navigation, visible focus, reduced motion, readable contrast, and non-color status labels are release requirements.

Voice, if added: push-to-talk, clear listening indicator, local audio deletion, text review for ambiguous task targets, and no voice-only approval for sensitive host effects. Local STT/TTS is preferred if it fits resource limits; cloud speech needs separate disclosure consent. Do not reproduce copyrighted character voices or Iron Man branding.

## 13. Evaluation: Define The 90% Target Honestly

### Task Success Metric

A supported task passes only when its declared postconditions are satisfied, required verifiers pass, scope/disclosure policy is respected, and completion is reported truthfully. Partial work, incorrect refusal, timeout, abandoned approval flow under the test protocol, and unsupported claims are failures on ordinary supported tasks.

Expected refusal/clarification cases live in a separate safety suite so refusing everything cannot inflate task-success accuracy.

Build at least 40 development tasks and freeze 90 distinct held-out task fixtures before the final tuning cycle:

| Category | Held-out tasks | Examples |
| --- | --- | --- |
| Session preparation | 15 | Similar project names, missing editor, correct source references |
| Inbox/routine work | 15 | Duplicate events, changed files, no original deletion |
| Memory/skill reuse | 10 | Restart, corrected preference, disabled skill, scoped retrieval |
| Sandbox diagnosis/repair | 10 | Known failing fixture, minimal patch, protected checks |
| Cross-workflow recovery | 10 | Interrupted task, provider timeout, stale source, cancelled action |
| Kali diagnostics and new code | 10 | Version-aware tool choice, feature creation with independent checks, user-service diagnosis |
| Authorized security observation | 10 | Nmap parsing, comparable baselines, partial coverage, justified findings |
| Remote workflow | 10 | Pinned host, remote diagnosis, approved app repair, disconnection reconciliation |

Run each held-out task three times with reset fixtures and fresh execution state, while preserving only memory explicitly required by that case. Target >=243/270 passing executions and >=80% in each category. Record all attempts. The three repetitions are correlated; report both per-task and per-run results, with uncertainty and no broad population claim from this small suite. The target is not achieved during planning.

If any workflow is reduced, revise and freeze the benchmark before release testing; disclose the supported scope change rather than quietly dropping failures after seeing results. Successful lab tasks do not establish unrestricted Kali mastery or production security assurance.

### Separate Safety Suite

At least 50 deterministic/adversarial fixtures covering traversal, symlink races, secret filenames, malicious notes, malicious tool output, grant revocation, approval replay, expired approvals, changed hashes, output XSS, budget bypass, sandbox egress, sandbox host access, and cancellation races. Include out-of-scope targets, IPv4/IPv6 normalization, changed DNS, shared-hosting addresses, unauthorized profiles, unbounded target expansion, hostile XML, SSH host-key mismatch, remote command injection, expired remote leases, disconnection, and forged findings.

Release gate: zero observed unauthorized side effects or secret disclosures in this suite. This is a tested result on a finite suite, not proof of universal safety. A critical escape, leakage, or uncontrolled mutation blocks release regardless of the 90% task score.

### Ground Truth And Anti-Gaming

- Evaluate filesystem state, checksums, process state, immutable tests, citation resolution, and event logs where possible.
- Agent cannot modify evaluator code or expected outputs. Mount verifier fixtures read-only and run outside the agent's writable area.
- For summary quality, use a blinded human rubric for factuality, coverage, and source attribution. Define thresholds before seeing outputs; model-as-judge is optional supporting evidence only.
- Record model ID, prompt/skill version, commit, fixture version, timing, tool count, cost, approval count, failure reason, and outcome evidence.
- No demo-specific hardcoded answers, precomputed fixes presented as live reasoning, or cherry-picked denominator.

### Does The Method Actually Help?

Compare the same model on the same development tasks with the same safety envelope:

1. Basic tool loop without durable memory, explicit postcondition checks, or bounded repair.
2. SUDO X with verifiers and bounded repair.
3. SUDO X plus reviewed skills and task-relevant memory.

Keep resource limits comparable and report added latency/cost as well as success. Never disable security to create a baseline. This ablation demonstrates the value of the execution method rather than claiming the prompt makes a model intrinsically smarter.

### Other Proposed Gates

- One-hour idle soak: zero idle inference calls; proposed backend idle RSS under 250 MiB, excluding browser, sandbox, and optional speech model.
- 24-hour watcher soak before release: no duplicate effects or unbounded queue growth; CPU/memory measured and reported.
- UI request acknowledgement p95 under 500 ms locally; cloud task latency reported separately, not hidden.
- Stop dispatching new tools within one second of cancellation; terminate managed child groups within five seconds where supported, with partial-effect reporting.
- Core daily workflow completion p95 target under 90 seconds excluding human approval; validate on actual hardware/provider.
- Track notification precision in a small pilot; aim >=80% of notifications rated useful, with easy muting.

These are initial engineering targets, not official judging requirements. Adjust unrealistic targets with rationale before frozen evaluation, not after failures to manufacture a pass.

## 14. Build Milestones And Acceptance Gates

The user asks not to constrain the vision by assumed available time. The dates below are planning checkpoints toward the fixed hackathon deadline, not a limit on the long-term product. Capability dependencies and exit gates remain mandatory even if more engineering time is available.

| Milestone | Proposed dates | Deliverable | Exit gate |
| --- | --- | --- | --- |
| M0: approve/preflight | Sep 7-10 | User decisions, rules recheck, model/sandbox capability spike | Eligible path, budget, safe executor choice, one NVIDIA tool call |
| M1: safe vertical slice | Sep 11-17 | Text task -> typed read -> managed artifact -> receipt | Deterministic policy tests, real provider smoke test, no host shell |
| M2: durable operator | Sep 18-24 | Queue, approvals, cancellation, restart reconciliation, files/apps | Stale approval and interrupted-effect tests pass |
| M3: personal continuity | Sep 25-Oct 1 | Local memory, inbox watcher, reviewed skills | Routine survives restart; memory corrected/deleted; no duplicate writes |
| M4: experiment/verify | Oct 2-8 | Isolated repair, immutable checks, receipts, bounded recovery | Failure reproduced and repaired without original edits before approval |
| M4-S: Kali/security | Before M5 | Capability registry, asset grants, typed Nmap, baselines | Real owned-lab scan, enforced target boundaries, truthful partial results |
| M4-R: remote mission | After M2 and M4-S, before M5 | Pinned SSH, remote diagnostics, approved user-app repair, rescanning | Remote permissions, replay/expiry/disconnect tests, integrated workflow D |
| M5: complete product | Oct 9-15 | Polished UI, onboarding, optional push-to-talk, small pilot | All four workflows understandable without developer explanation |
| M6: release hardening | Oct 16-22 | Frozen evaluation, adversarial tests, installable build, demo deployment | Reliability/safety gates and fresh-machine installation pass |
| M7: submission | Oct 23-27 | Video, README, license, feedback, Devpost entry | Submitted and links checked from logged-out browser |
| Buffer | Oct 28-30 | Final access checks and urgent fixes before cutoff | Final submission confirmed before 17:00 UTC Oct 30 |

Do not wait until M5 to render a UI. Ship a basic task/approval UI in M1 and improve it alongside the backend. Make a rough recorded demo after M3 to expose confusing interactions early.

### Implementation Order Within M1

1. Create package/config and pure schemas with unit tests. No background service install yet.
2. Implement scoped read/managed-write tools and deterministic broker with temporary fixture roots.
3. Implement SQLite task events and a deterministic fake provider for reproducible CI; clearly label it test-only.
4. Add Nebius adapter and explicit paid smoke-test command using synthetic content.
5. Add verifier and receipt generation tied to actual tool evidence.
6. Add minimal authenticated UI and a single end-to-end demo fixture.

### Cut Order If Time Is Short

Cut wake word, then speech, then generic browser operation, then PDF support, then model routing. If isolation is unavailable, narrow repair to diagnosis/proposed patch with no untrusted execution. Preserve privacy controls, memory, one real always-on routine, skill reuse, evidence-backed completion, scoped Nmap, and the authorized remote lab mission. An unverified remote security path must be disabled and reported as deferred rather than shipped to satisfy a feature count.

### Proposed Repository Shape After Approval

```text
sudo x/
  README.md
  PROJECT_BLUEPRINT.md
  HANDOFF.md
  LICENSE
  pyproject.toml
  src/sudo_x/
    api.py
    config.py
    engine.py
    models.py
    policy.py
    storage.py
    memory.py
    routines.py
    provider.py
    tools/
    verifiers/
  ui/
  skills/
  tests/
    unit/
    integration/
    safety/
    e2e/
  evals/
    fixtures/
    reports/
  docs/
    security.md
    testing.md
    provenance.md
    feedback.md
  packaging/
```

Create modules when needed, not an empty forest of abstractions. Keep runtime state under XDG user directories, separate from source and public evaluation artifacts. Planned commands such as `uv run pytest` and `uv run ruff check .` become valid only after a project environment is actually configured.

## 15. Demo And Submission Plan

### Narrative

"Your coding assistant does not remember your lab. Your scanner does not fix your code. SUDO X connects your Kali workspace, authorized machines, and personal routines: it notices a change, investigates, prepares a tested fix, and proves what happened with your approval."

This is a positioning hypothesis, not a verified claim that no competing product has these features. Before submission, review 3-5 current adjacent products on delegated routines, local memory, permission granularity, receipts, and recovery. Emphasize our demonstrated combination and audience rather than claiming invention of agents or sandboxes.

### 2:45 Video Storyboard

| Time | Footage and purpose |
| --- | --- |
| 0:00-0:15 | Kali desktop, enrolled lab server, personal goal: watch my project while I am away |
| 0:15-0:35 | Approved monitor detects a new reachable lab service; show baseline and actual Nmap evidence |
| 0:35-1:00 | Pinned remote diagnostics identify the relevant user-app config; memory supplies the correct project context |
| 1:00-1:35 | Create minimal fix in a copy, run health/security regression checks, display exact diff and approval |
| 1:35-2:00 | Apply approved user-app change, repeat scan from same vantage, verify normal app still works |
| 2:00-2:20 | Save reviewed guard routine; restart/resume; show personal brief and one out-of-scope request blocked |
| 2:20-2:45 | Evidence receipt, measured benchmark, actual NVIDIA/Nebius role, privacy controls and honest limitations |

Record actual functioning software on the intended Linux desktop. Seeded fixtures are allowed but label them demo fixtures. Disclose cuts/time compression. Never fake tool traces, runtime calls, test passes, or speed. Keep a full uncut internal recording as supporting evidence. No copyrighted soundtrack, movie clips, or unauthorized logos.

### Safe Judge Access

Primary artifact: publicly downloadable versioned test build with bundled frontend, fixture setup, clear Kali/Linux instructions, and release checksum.

Preferred supplementary access: isolated hosted demo containing synthetic files and the same task engine. No network path from that demo to the user's laptop; no exposed local API tunnel; no arbitrary shell or user-supplied code. Each session gets an isolated workspace and reset/expiry. Provider keys remain server-side. Budget caps and abuse protection must not prevent organizer/judge access.

For workflow D, the hosted scanner/connector may reach only a dedicated isolated demo target through enforced network rules. Visitors cannot enter arbitrary IPs, domains, SSH destinations, credentials, or scan flags. Remote-control credentials for personal machines never exist in the public demo environment.

A static replay is useful as a fallback explanation but not sufficient as the only working demo. A public download requiring judges to buy inference credits is also not a reliable interpretation of free access. Provision funded judge access or ask the organizer to confirm an alternative well before submission. Maintain the submitted build and access through Dec 15, 2026; budget for this period, not only October.

### Submission Checklist

- [ ] User registered and checked eligibility/team representation.
- [ ] Personal AI selected; actual track functionality demonstrable.
- [ ] NVIDIA model does meaningful runtime planning/tool selection via Nebius.
- [ ] Public repository, actual open source license, notices, reproducible dependencies, no secrets/personal data.
- [ ] README names exact supported platform, capabilities, limitations, setup, and test commands.
- [ ] Working test-build/demo URL and free judging access instructions.
- [ ] English public YouTube video less than 3 minutes, with working footage and provider explanation.
- [ ] Description and screenshots accurately match the released build.
- [ ] Dated pre-existing-work disclosure and new contributions, if applicable.
- [ ] Provider/tool feedback includes concrete reproduction, impact, and improvement suggestions.
- [ ] Evaluation report shows denominator, failures, model/version, and cost/latency tradeoffs.
- [ ] Rules rechecked, final links tested logged out, entry actually submitted before deadline.
- [ ] Freeze/release provenance retained; do not silently change the submitted claims after cutoff.

## 16. User Validation And Impact

Within the first two build weeks, interview 3-5 Linux users about their last real repeated workflow. Ask what they do, how often, where mistakes happen, what they would never authorize, and what would make them trust an assistant. Avoid asking only whether "JARVIS would be cool".

Choose one recurring routine per pilot user. Measure manual time, assistant time including approvals/corrections, successful completion, data comfort, and whether they reuse the skill a week later. Proposed pilot: five people for a week, if feasible; report actual numbers and selection bias.

If users find the inbox workflow irrelevant, adjust its domain before M3 while preserving the architecture. Do not broaden to "everyone with a computer". A credible narrow benefit is stronger than imaginary global impact.

## 17. Risks And Decisions To Revisit

| Risk | Response |
| --- | --- |
| Scope becomes a fictional universal assistant | Keep four release workflows, explicit capability levels, and a published cut order |
| Model cannot reliably call tools | Capability probe, strict validation, measure candidate models, bounded recovery |
| Kali desktop/session differences | Detect display environment, use narrow adapters, report unsupported capabilities honestly |
| Low RAM / sandbox overhead | One worker, cloud inference, timeboxed integration spike, measure memory |
| Python 3.14 dependency issues | Isolated tested Python version; no system interpreter replacement |
| Prompt injection / secret leakage | Treat content as untrusted, separate grants/disclosure, external broker and safety tests |
| Agent modifies tests to pass | Protected independent verifiers |
| Provider downtime / cost surprise | Persistent queues, explicit offline state, budgets, no silent paid fallback |
| "Private" claim conflicts with cloud | Explicit disclosure, verified ZDR, local-only mode with limited capabilities |
| Existing SUDO provenance | Separate project, audit any reuse, honest pre-event disclosure |
| Framework alpha instability | Pin tested version, narrow fallback, avoid combining stacks |
| Weak differentiation | Show routine continuity, reviewed skills, measured recovery, user evidence |
| Demo cost after deadline | Plan funded synthetic judge access through December |
| Award/eligibility uncertainty | Ask organizers, do not infer legal eligibility |

### Questions For The User Before Implementation

1. Which owned lab VM or server should be the first remote-security target? Do not send credentials in chat.
2. Does remote mean operating enrolled servers from Kali, controlling SUDO X from another device, or both? The plan covers both, with server operations first.
3. Is Nebius cloud reasoning with explicit excerpt sharing acceptable, and what is the maximum spend?
4. Should this be a fresh project inspired by SUDO, or should any old code be reviewed for reuse?
5. Is text-first acceptable with voice added after reliability, as recommended?

These do not block writing this plan. They do block assumptions about spending, private data use, legacy migration, and implementation scope. Ask the highest-impact questions first rather than forcing a long questionnaire.

## 18. Instructions For Any Implementing Model

- Read README.md, this blueprint, and HANDOFF.md before editing. Honor the user's latest direction over stale design decisions.
- Confirm implementation is authorized. "Continue the planning" is not permission to install an always-on agent.
- Inspect relevant existing files and git status before changes. Preserve unrelated edits and never alter `../sudo/` without explicit permission.
- Work milestone by milestone. State the acceptance criteria before implementing a slice.
- Use the same evidence-based method expected of SUDO X: inspect, form a concise hypothesis, make the smallest change, test, inspect failure, revise, and document the outcome.
- Security authority belongs in code, not a system prompt. Test broker boundaries independently from model behavior.
- Do not trade away safety or privacy to get a cleaner demo. Report blocked or partial results honestly.
- Do not install dependencies globally, enable services, change system security, use root, or incur costs without the required user approval.
- Keep API keys and personal material out of prompts, git, logs, screenshots, and handoffs.
- Distinguish unit/mock tests from real provider tests. Never describe a mocked integration as verified Nebius usage.
- Keep tasks small enough to finish and verify before context runs out. Update HANDOFF.md after every meaningful milestone and before ending the session.
- Save decisions, public rationale, changed files, test commands/results, known failures, and exact next step. Do not save hidden reasoning or unbounded chat transcripts.
- Do not commit/push/create a repository or Devpost submission without explicit user authorization.
- If reality invalidates a design decision, record the evidence and revised decision instead of rigidly following an obsolete plan.

## 19. Source Register

All links below were read during planning unless noted. Vendor facts can change; refresh them before depending on them.

| ID | Source | Used for |
| --- | --- | --- |
| S1 | https://nebiusglobalaihackathon.devpost.com/ | Overview, track descriptions, prizes, judging |
| S2 | https://nebiusglobalaihackathon.devpost.com/rules | Binding schedule, eligibility, runtime definition, submission/testing requirements, equal weights |
| S3 | https://nebiusglobalaihackathon.devpost.com/resources | Credits, Builders Program, city-award inconsistency |
| S4 | https://docs.tokenfactory.nebius.com/ | OpenAI-compatible API quickstart and base URL |
| S5 | https://docs.tokenfactory.nebius.com/llms.txt | Official documentation index |
| S6 | https://docs.tokenfactory.nebius.com/api-reference/examples/list-of-models.md | Model discovery, verbose metadata |
| S7 | https://docs.tokenfactory.nebius.com/ai-models-inference/function-calling.md | Tool protocol; backend executes, model only proposes |
| S8 | https://docs.tokenfactory.nebius.com/legal/legal-quick-guide.md | Retention, ZDR, location, controlling legal document caveat |
| S9 | https://github.com/NVIDIA/OpenShell | Isolation/policy architecture, supported runtime categories, alpha status, telemetry |
| S10 | https://raw.githubusercontent.com/NVIDIA/NemoClaw/main/README.md | Reference-stack role, supported agents, alpha status |
| S11 | https://www.kali.org/tools/nmap/ | Kali Nmap documentation, capabilities, Ndiff; documentation is not proof of local installation |
| S12 | https://nmap.org/book/output-formats-xml-output.html | Official recommendation for machine-readable XML and observation fields |
| L1 | ../sudo/README.md | Earlier prototype's documented features and voice limitations; not execution-verified |

Binding Nebius terms/privacy/DPA are linked from S8 but were not fully reviewed in this planning session. Exact NVIDIA serving IDs, per-model licenses, account ZDR state, credit balance, and judge-access interpretation remain to be verified. No paid model calls were made.

## 20. Kali, Security, Remote Operations, And JARVIS Experience

This section makes version 2's expanded product requirements implementable. All capabilities remain planned. No local scans, remote logins, installations, or security changes were performed while writing it.

### 20.1 What Mastering Kali Means In Practice

Do not make "master of Kali" a magic system prompt. Build an OS knowledge and capability system that knows what it can actually do on this installation.

| Domain | Intended capability | How competence is established |
| --- | --- | --- |
| OS identity | Release, kernel, shell, display session, package tool versions | Bounded local observations with timestamps; no assumptions from a Kali label |
| Files and permissions | Explain ownership/mode issues, inspect permitted project trees, propose precise changes | Fixtures for permissions and conflicts; no global chmod/chown fixes |
| Processes/services | Explain resource use, inspect user services and selected logs, diagnose failed launches | Structured state and bounded journal reads; redact log secrets |
| Packages/environments | Identify missing tools, package versions, Python environments, dependency conflicts | Read-only package metadata; package installation is a separate approved step |
| Networking | Distinguish local listeners, routes, DNS resolution, TLS observations, and remote reachability | Compare actual observations and vantage points; never infer Internet exposure solely from a local listener |
| Desktop | Open approved apps/files, resume chosen workspace, explain unsupported desktop operations | X11/Wayland/session capability detection and explicit launch verification limits |
| Security tools | Select a reviewed tool/profile, explain findings and uncertainty, preserve evidence | Versioned adapters with parser fixtures and real owned-lab integration tests |
| Coding | Read/write projects, implement features, run tests, debug, review diffs, prepare docs | Independent acceptance checks and preservation of original work |

Inventory only after consent; enumerate approved binaries and safe metadata, not the whole user's filesystem. Prefer machine-readable output. Resolve tool binaries from trusted paths, record their version, and invalidate relevant capability checks after upgrades. Do not execute arbitrary discovered binaries just because they implement `--help`.

Use installed manual pages and pinned official Kali/upstream docs as reference material. Record source/version; treat documentation as untrusted content, not authority to execute examples. If installed flags differ from documentation, inspect safe help for the trusted tool or ask; do not improvise risky options.

Capability levels displayed in the UI: `documented`, `available`, `fixture_tested`, `lab_verified`, `enabled_for_this_scope`. Knowing a tool exists does not mean it is approved or reliable. A tool adapter needs schema, effect class, permission rules, resource limits, result parser, error mapping, independent checks, and safety tests before enrollment.

### 20.2 Initial Security Tool Catalog

| Adapter | Scope and use | Delivery tier |
| --- | --- | --- |
| Nmap | Approved TCP reachability inventory; optional explicitly approved light service detection | Core release |
| Scan comparison | Parsed observation comparison, optionally Ndiff after validation | Core release |
| Local socket/service status | Structured listener/process and user-service observations | Core release |
| SSH diagnostics | Bounded user-app status, logs, hashes, and config observations on enrolled host | Core release |
| DNS/TLS checks | Selected record/certificate/expiry checks on enrolled endpoints | Next capability pack |
| Dependency/static analysis | Reviewed tools such as pip-audit, Bandit, or Semgrep in isolated project copies | Next capability pack; validate versions/licenses and network requirements first |
| Host audit | Reviewed read-only Lynis-style checks with explicit coverage/privilege limitations | Later capability pack, not an excuse to run the whole agent as root |
| Packet analysis | Summarize user-provided PCAP with an isolated parser | Later capability pack; no implicit live capture |
| Web assessment | Narrow reviewed checks against owned lab apps | Later capability pack with per-check traffic/impact review |

Names beyond Nmap/Ndiff are candidate integrations, not verified installed tools or implemented adapters. Avoid adding every scanner at once. Importing a new tool's description or an MCP server does not bypass adapter review.

### 20.3 Authorization And Asset Model

Remote reachability is not authorization. Enroll each asset with a stable ID, owner/authorizer, scope reference, exact approved endpoints or tightly bounded address ranges, environment (lab/staging/production), allowed techniques/ports, time window, maximum traffic, allowed scanner location, and expiry. Access credentials and authorization to scan are separate.

The asset registry is a user-managed record, not automatic legal verification. Public demo accepts only pre-provisioned fixtures. For real work, require an explicit ownership or authorization declaration; never infer ownership from private addressing, DNS control alone, a successful SSH login, or an existing browser session.

Domains hosted on third-party/shared infrastructure require host/network permission for IP-level scanning. A permission to test one web application does not authorize scanning its entire CDN/shared IP. Treat unresolved scope as a clarification requirement.

Normalize IPv4/IPv6 and expand ranges under hard caps before approval. Resolve names outside the model, pin the approved address set for execution, and reauthorize changes. Disable uncontrolled reverse lookups and reject broadcast, multicast, random targets, metadata endpoints, or expansion outside scope. Private/loopback targets require explicit enrollment rather than a global exemption.

Sample initial lab limits: up to four exact hosts, up to 32 approved TCP ports each, one scan at a time, and a 120-second wall-clock cap. Profile-specific connection/traffic limits must be tested with packet observation; do not assume an Nmap option alone guarantees an absolute packet ceiling. Low impact is not zero impact. Fragile/production systems need operator-agreed limits and a maintenance window where appropriate.

### 20.4 Nmap Adapter Contract

Typed input: `asset_ids`, `profile_id`, `port_set_id`, `vantage_id`, `authorization_id`. No arbitrary command string, flags field, target-list file, output filename, script path, or proxy option from model output.

Initial profiles: unprivileged TCP connect inventory and a separately approved low-intensity service-identification profile. No default aggressive bundle, OS fingerprinting, UDP sweep, NSE execution, evasion/spoofing, brute force, or exploit checks. Future NSE support requires individual script/version review; a category named "safe" is not sufficient approval.

The adapter constructs argv from reviewed definitions, writes output to a broker-controlled artifact, enforces a clean environment and deadline, and executes in a dedicated constrained scanner context. Only the approved destination set is reachable. The general code sandbox retains no-network policy. Do not give the scanner host networking or root merely to make setup easier; inability to enforce scope blocks enabling active scans.

Parse XML, as recommended by official Nmap documentation, using a hardened parser with entity expansion and external resource loading disabled. Ignore stylesheet instructions; do not fetch a DTD. Bound input size and nesting, validate expected fields, and mark unsupported/malformed/truncated output as partial or failed. Test parser behavior against the actual pinned tool version.

Persist target set, profile/version hash, ports/protocols, scanner vantage identity, start/end, return code, per-host completion, observed states, service evidence and confidence, and artifact hash. Parse output as data; banners, hostnames, and script text cannot become instructions or HTML.

No open-port finding is automatically a vulnerability. Port-based service guesses differ from probed identification. Version banners can be inaccurate or backported; any advisory match is a candidate until relevant package/config evidence supports it. Use cited vendor advisories and observed conditions, not invented CVEs or severity scores.

### 20.5 Findings, Drift, And Evidence

Store an asset/service/project relationship map in SQLite relations, not a new graph database. Relationships have source evidence, observed time, confidence, and expiry. Distinguish confirmed mapping from hypothesis; a similar project name is not proof that it runs a service.

A baseline comparison requires compatible scanner vantage, target identity, profile, coverage, and completion. `filtered`, `closed`, `unreachable`, and `not tested` remain distinct. Timeout or network loss cannot silently resolve a finding. Suppress duplicate notifications without hiding unverified changes.

Finding states: `observation`, `suspected_issue`, `validated_issue`, `remediation_proposed`, `verification_pending`, `resolved_with_evidence`, `accepted_risk`. Record expected exposure separately so a deliberate new service can be accepted after review rather than repeatedly "fixed".

Prioritize using asset importance, actual reachability, impact evidence, confidence, and user context. Keep scanner output, inference, and recommendation visually separate. Every claimed resolution links to after-checks and remaining coverage gaps.

Routine example: approved nightly bounded inventory of two lab hosts; compare against their baseline; call the model only for a meaningful change; notify once; prepare suggestions automatically but wait for mutation approval. Schedule checks are active traffic, unlike passive filesystem watchers, and need their own grants and quotas.

### 20.6 Remote Has Two Separate Meanings

**Remote machine operations, core:** SUDO X on Kali uses an explicitly configured connector to inspect and operate enrolled lab servers. First transport: SSH with pinned host keys, dedicated least-privilege identity, no password collection in chat, no root login, no agent forwarding, and no arbitrary port forwarding. Host-key mismatch blocks the task; never disable checking to repair connectivity.

For the demo, use a small reviewed remote dispatcher invoked through a fixed SSH command. It accepts bounded typed requests over stdin, not model-interpolated shell strings. Enforce destination-side capability, nonce/replay protection, expiry, allowed user-app paths, action hash, and source preconditions. Prevent unrestricted shell/subsystem access for that identity. SFTP, if later added, needs its own path-limited authorization.

Remote mutation requests carry a short-lived authorization signed by the local approval broker using a standard cryptographic library and a separately protected signing identity. The remote dispatcher pins its verification key and verifies asset ID, action hash, scope version, expiry, and nonce; a request field saying `approved: true` is never sufficient. Model and tool-worker processes cannot mint authorizations. Revocation blocks new issuance immediately; already-issued remote capabilities expire within a documented short lease, so do not promise instant revocation during a partition. Test clock skew and replay handling without designing a custom cryptographic protocol.

The connector may reference a dedicated key through a private configuration or secret broker; it never returns key material. Do not inherit broad personal SSH configuration, ProxyCommand, agent identities, or ControlMaster sessions. Enrollment config is explicit and reviewed. Real client/server implementation details must be tested before making a security claim.

Remote changes are user-owned application file patches and allowlisted user-service operations first. Fix system-owned configs or firewall/SSH settings by presenting a reviewed manual plan until a separately audited privileged helper exists. Never install a passwordless general sudo rule or give the model access to a sudo password.

**Remote personal control, later opt-in:** a paired laptop/phone can submit tasks, inspect receipts, pause work, and approve eligible actions through a user-managed private authenticated channel. Start with a reviewed SSH tunnel/private-network design; keep the API loopback-bound, preserve origin/CSRF checks, and enforce per-device identity, revocation, session expiry, and step-up authentication for sensitive approvals. Private networking alone is not authentication. No public unauthenticated port, exposed terminal, or chat-bot command channel by default.

Remote control design must be separately validated before release; a mobile-looking UI is not a secure remote product. The public hackathon demo cannot connect to personal devices. No VPN or tunnel is configured during planning.

### 20.7 Remote Failure And Recovery

Each remote job carries a short execution lease and a local remote-side watchdog. Loss of controller contact prevents new steps; an in-progress bounded action may finish or time out. The UI must show `cancellation_unconfirmed` when disconnected instead of falsely claiming the remote process stopped. The local five-second cancellation target does not imply immediate remote cancellation under a network partition.

Reconnect using pinned identity, reconcile task nonce, artifact hashes, logs, and health state before any retry. Do not replay a possibly applied change. Read-only checks also need bounded retries and rate limits.

Do not modify the same SSH/firewall/network path required for management in the release demo. Future high-risk administration needs console access or a verified out-of-band recovery path, staged changes, timed rollback where supported, and explicit downtime approval. A backup file alone is not a remote recovery guarantee.

### 20.8 Integrated Demonstration Fixture

Create an isolated owned lab with a normal user application health endpoint and a separate debug listener on an unprivileged port. The seeded issue is a configuration regression that binds the debug listener more broadly than the intended policy. The scanner, remote dispatcher, and test target have deliberately restricted connectivity, with no public exposure.

The assistant observes the unexpected listener from a declared scanner vantage, uses remote app status/config evidence to identify the cause, changes the relevant configuration in a copy, and runs an immutable regression check for intended binding plus normal application health. After approval it applies the exact config and allowlisted user-service reload on the lab target. Recheck the debug exposure from the original scanner and normal health from its appropriate authorized vantage; preserve evidence from both.

The "wow" is not that Nmap found a port. It is continuity across monitoring, machine knowledge, personal context, code/config editing, experimentation, approval, and proof. Demonstrate a second run where the reviewed routine remembers expected exposure without repeating setup.

### 20.9 Improvements That Make It Feel Like JARVIS

| Feature | User experience | Implementation rule |
| --- | --- | --- |
| Mission memory | "Continue the server issue from yesterday" restores verified context and pending work | Durable task/artifact links, freshness checks; memory never restores expired authority |
| Machine map | "Which app is using this port?" links service, process, repo, and owner when known | Evidence-backed relationships and uncertainty, not guessed topology |
| Morning brief | Summarizes project progress, meaningful lab changes, and pending approvals | Opt-in digest, source links, quiet hours, zero fabricated urgency |
| Rehearsal mode | "Show me what you'd do first" produces exact planned effects and checks | Clearly distinguish preview from executing a sandbox rehearsal; previews are not proof |
| Teach-and-repeat | "Do it this way next time" proposes a reusable scoped skill | Human-reviewed versions; no automatic privilege growth |
| Explain-as-you-go | Optional concise explanations teach Kali and coding concepts while working | Public rationale and evidence, not private reasoning dumps |
| Hands-free presence | Push-to-talk, interruptible speech, eventual local wake word | Explicit listening state, resource/noise tests, text fallback and nonvoice sensitive approval |
| Research when uncertain | Retrieve official docs/advisories and cite the applicable version | Untrusted-source boundaries, approved fetches; optional Tavily only if genuinely useful |

Avoid fabricated emotions, absolute certainty, or excessive talking. The personality should be calm, concise, interruptible, and aware of unfinished commitments. Competence comes from correct context and checked outcomes, not calling the user "sir".

### 20.10 Expanded Build And Evaluation Gates

Implement OS inventory and tool capability records first; Nmap XML parser fixtures next; scope validation and scanner egress tests before live owned-lab probes; comparable baselines next; pinned SSH read-only diagnostics next; approved remote user-app patches last. The full coding workflow shares existing sandbox, diff, approval, and verifier components rather than a second agent runtime.

Additional release evidence: packet capture or equivalent network observation proving test runs stayed in scope; malformed scan output handled safely; host identity mismatch blocked; remote expiry/replay/disconnection behavior verified; no secret material in model requests; trusted before/after application tests; and at least one repeat routine across a process restart.

An unlimited development horizon does not remove authorization, software licensing, model costs, hardware constraints, or the event deadline. Keep the broad vision, publish actual capability coverage, and claim only what the submitted build can demonstrate.
