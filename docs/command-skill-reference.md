# Command & Skill Reference

A complete index of every custom slash command, skill, and project-specific automation in this setup. Global items are available everywhere; project-specific items live in that project's `.claude/` folder and are only active when you're working in that project.

This doc is the index — *what exists*. Its companion, the
**[Usage Playbook](usage-playbook.md)**, is the judgment layer: *how to run each one* —
suggested model + effort, the situations worth reaching for it in, and what it pairs with.
Every row below links to its card with `config →`.
Items removed on purpose are logged in [`retired.md`](retired.md) with restore pointers.

**How to invoke:**
- **Commands** → type `/command-name` in the Claude Code prompt
- **Skills** → Claude invokes them automatically, or you type `/skill-name`
- **Project-specific** items → same syntax, only available inside that project

---

## Keeping the two docs in sync

The two docs stay 1:1 — a row added, renamed, or deleted here carries its playbook card in the
**same commit**. That's checked rather than asked: the rule lives in
[`../CLAUDE.md`](../CLAUDE.md) under *Reference Doc Maintenance*, and
[`scripts/check-doc-sync.py`](../scripts/check-doc-sync.py) runs as the repo's `pre-push` hook,
so drift blocks the push.

The full mechanics — every condition the check enforces, and the two things it deliberately
does not — live in the playbook's section of the same name:
[Keeping the two docs in sync](usage-playbook.md#keeping-the-two-docs-in-sync).

---

## Global Commands

Available in every Claude Code session. Live in `commands/`.

### Session Lifecycle

| Command | What it does |
|---|---|
| [`/launch`](../commands/launch.md) | Opens a new terminal window in a project directory and starts a fresh Claude Code session there, with the prompt on the clipboard (or auto-submitted via `--send`). Reads directory, model, and effort from the run-config note just produced, and names the session descriptively (`claude --name`) so it's findable in the resume picker later; `--remote` starts it as a Remote Control session so the name reaches the claude.ai/mobile lists too. · [config →](usage-playbook.md#launch) |

## Global Skills

Available everywhere. Live in `skills/`. Claude invokes these automatically when the context matches, or you can request them directly.

### Session & Context Management

| Skill | What it does |
|---|---|
| [`pre-compact`](../skills/pre-compact/SKILL.md) | Checkpoints a session before `/compact` — writes what's settled, open, and deferred plus a next step into the active skill's durable home, commits and pushes the feature branch, and gives an honest "safe to compact" / "not yet, because X" checked against git (or "saved to disk, not pushed" where there's no remote). Keeps the same session alive; `mattpocock-skills:handoff` is for moving to a fresh one. · [config →](usage-playbook.md#pre-compact) |
| [`visual-summary`](../skills/visual-summary/SKILL.md) | Turns a conversation, a branch's diff, or an uncommitted worktree into one self-contained HTML page that's read at a glance — three to five charts and diagrams, one headline, no second block of prose. Saves to `~/Projects/_visual-summaries/` and publishes as an Artifact every run, unless `--no-publish`. · [config →](usage-playbook.md#visual-summary) |
| [`wayfinder-map`](../skills/wayfinder-map/SKILL.md) | Draws a Wayfinder effort's map as one self-contained HTML page — the blocking graph toward the destination, takeable tickets as cards, decisions so far, and the fog — generated deterministically from `map.md` and the issue files into `map.html` beside it, and published to one stable Artifact link per effort. A Stop hook re-renders stale maps. · [config →](usage-playbook.md#wayfinder-map) |
| [`retire`](../skills/retire/SKILL.md) | The config's subtract verb — inventories every global steering surface (CLAUDE.md sections, constraints paragraphs, skills, commands, agents, plugins, MCP servers, hooks, output styles, auto-memory) with usage evidence, proposes a verdict per item from a fixed precedence table, applies only what you ratify row by row with full bookkeeping and a retirement ledger, and measures before → after weight. Sweep, `--report`, `--surface`, or targeted. · [config →](usage-playbook.md#retire) |

### Quality & Debugging

| Skill | What it does |
|---|---|
| [`adversarial-review`](../skills/adversarial-review/SKILL.md) | Pre-merge author↔reviewer↔judge loop, now propose-first — the session recommends SKIP / SINGLE ROUND / FULL LOOP with honest reasoning (Kyle decides interactively; unattended runs decide and record why); whatever runs, a zero-context reviewer files graded findings, the author triages, a judge rules on disputes, and the adjudicated summary lands as a PR comment with a CLEAR / NOT-CLEAR merge verdict. · [config →](usage-playbook.md#adversarial-review) |

## Project-Specific Items

Items only available inside their respective project.

---

### A2C Auctions (`~/Desktop/A2CAuctions/`)

Prospecting and outreach automation for auction consignor leads.

**Skills**

| Skill | What it does |
|---|---|
| `replenish-a2c` | Use when the prospecting pipeline has run thin — refills `prospects.md` by running audit and prospecting lanes in parallel, generating ranked leads and auto-drafted first-touch outreach. · [config →](usage-playbook.md#replenish-a2c) |
| `stage-a2c` | Stages unsent first-touch outreach into Gmail drafts and LinkedIn compose windows. Reconciles which prospects still need messages before writing or reusing drafts. Never auto-sends. · [config →](usage-playbook.md#stage-a2c) |
| `call-brief` | Full briefing for one dial — who they are, where the thread stands, pitch type, then every spoken section twice: detailed bullets to talk from and the written-out script under them, plus the one ask and the voicemail line. One contact per run; never logs or sends. With `--audio [short\|long]`, also delivers the briefing as an MP3 (`short` is the prep briefing, `long` adds the opener and voicemail read as written). · [config →](usage-playbook.md#call-brief) |
| `rebrief-a2c` | Re-entry after time away — sweeps Gmail for replies, bounces, and unsent drafts, sweeps the Todoist A2C project for done/overdue, reconciles both against the prospect files, then briefs and primes the day's or week's work. · [config →](usage-playbook.md#rebrief-a2c) |
| `sync-check` | Consistency sweep across Todoist, the A2C calendar blocks, Gmail, the day logs and the project files. Fixes a closed whitelist of transcription drift (a missing block row, a wrong row time, a dead row) and reports everything else; never rewrites a name, number or address, and never sends. Runs by hand or unattended from `launchd` on Sun/Tue/Thu evenings. · [config →](usage-playbook.md#sync-check) |
| `morning-briefs` | Builds every call brief for one A2C block day ahead of time — reads the day's calendar blocks and Todoist tasks, decides which tasks are dials, runs one `call-brief` subagent per dial, and assembles `daily/briefs/YYYY-MM-DD.md` in dial order. Runs unattended from `launchd` at 06:45 Mon–Fri and by hand from `/day` to fill gaps; never sends or writes the pipeline. · [config →](usage-playbook.md#morning-briefs) |

---

### clinical-data-etl

Data pipeline for clinical health records using dbt and Postgres.

**Skills**

| Skill | What it does |
|---|---|
| `add-source` | Wires a brand-new raw data source into the pipeline end-to-end — pandera schema, idempotent ingestion loader, raw table, dbt staging model, and optionally a new star schema for a new analytical subject. · [config →](usage-playbook.md#add-source) |
| `new-dbt-model` | Scaffolds a new dbt model following established conventions — correct layer + prefix, paired `schema.yml` entry with tests, and the incremental config pattern. · [config →](usage-playbook.md#new-dbt-model) |

---

### Constellation

A planet-and-powers interactive puzzle game.

**Skills**

| Skill | What it does |
|---|---|
| `new-planet` | Scaffolds a new planet across all sides of the planet contract — `planetN.ts` config, colocated test file, and ordered `PLANETS` entry in `registry.ts`. Models on `planet3.ts` ("Nebula Core"). · [config →](usage-playbook.md#new-planet) |
| `new-power` | Scaffolds a new astronaut power across all sides of the power contract — `PowerId` literal, Spellbook tile, puzzle component, registration in `App.tsx`, and cast handler. Models on Freeze Stars. · [config →](usage-playbook.md#new-power) |

**Commands**

| Command | What it does |
|---|---|
| `/verify-planet` | Headlessly verifies a planet end-to-end via Playwright MCP and the `?test=1` bridge — boots the game, runs the AUTONOMY.md playbook subset for that planet, and reports per-step PASS/FAIL + overall verdict. · [config →](usage-playbook.md#verify-planet) |
| `/moonshot` | Deprecated alias — now the "Moonshot" mode of `/brainstorm`. Prefer `/brainstorm` going forward. · [config →](usage-playbook.md#moonshot) |

---

### DogHood

A full-stack dog-walking / pet-care app (Supabase + Postgres + PostGIS).

**Skills**

| Skill | What it does |
|---|---|
| `adr-new` | Scaffolds the next Architecture Decision Record — auto-increments zero-padded number, copies the template, pre-fills title/status/date, and adds a row to `docs/adr/README.md`. · [config →](usage-playbook.md#adr-new) |
| `new-migration` | Scaffolds a new Supabase Postgres + PostGIS migration — timestamped SQL file with RLS-by-default boilerplate, plus an optional pgTAP test stub. · [config →](usage-playbook.md#new-migration) |

**Commands**

| Command | What it does |
|---|---|
| `/new-scope` | Scaffolds a scope brief in `docs/scopes/` from the canonical template. A scope = one unit of shippable work = one PR. · [config →](usage-playbook.md#new-scope) |
| `/reconcile-backlog` | Fixes doc ↔ git drift — cross-checks BACKLOG.md, README, and CHANGELOG against what actually merged, shows the drift table, and applies corrections on a `docs/` branch. · [config →](usage-playbook.md#reconcile-backlog) |
| `/scheduled-reconcile` | Unattended weekly doc-drift reconcile (driven by a Claude Code scheduled trigger). Autonomously fixes unambiguous drift; drafts a PR for ambiguous cases. · [config →](usage-playbook.md#scheduled-reconcile) |
| `/ship` | Gate-aware commit → push → PR for current work. Applies orchestrator blast-radius + manual-smoke gates, uses the guard-hook-safe PR recipe. Explicitly does not merge. · [config →](usage-playbook.md#ship) |
| `/verify` | Derives the right verification tier for the current diff — maps changed paths to exact checks (typecheck, deno check, pgTAP, RLS auditor) and produces a paste-ready Verification block for the PR body. · [config →](usage-playbook.md#verify) |

---

### home-base (Learning Hub)

A personal learning hub — NotebookLM-backed course catalog with audio/video episodes.

**Skills**

| Skill | What it does |
|---|---|
| `course-builder` | Builds a full multi-format course for any topic — interviews for syllabus, gets one approval, then autonomously authors every material: lessons, exercises, visualizations, flashcards, quizzes, reading. · [config →](usage-playbook.md#course-builder) |
| `episode-review` | Post-episode review-and-quiz workflow — runs reflection, quizzes you, and logs score + listened status to the progress store. · [config →](usage-playbook.md#episode-review) |
| `review-next` | Read-only "what to review next" planner — reads the local progress store and ranks the shakiest material by mastery. · [config →](usage-playbook.md#review-next) |
| `youtube-breakdown` | Converts a YouTube transcript or URL into one of four formats: Study Notes, Quick Reference, Critique, or Actionable Insights. Saves the output and integrates with the hub catalog. The hub-native fork of the global [`youtube-breakdown`](#research--writing). · [config →](usage-playbook.md#youtube-breakdown-home-base) |
| `catalog-doctor` | Health-checks the topic catalog — reconciles what the hub parsed against live `nlm studio status` and reports drift. Read-only. · [config →](usage-playbook.md#catalog-doctor) |
| `api-types-sync` | Reconciles the frontend TypeScript API types (`frontend/src/api/types.ts`) with the backend Pydantic models after schema changes. · [config →](usage-playbook.md#api-types-sync) |

**Commands**

| Command | What it does |
|---|---|
| `/build-course` | Thin entry point to `course-builder` — interviews for topic and level, proposes a syllabus, gets approval, then autonomously authors all materials. · [config →](usage-playbook.md#build-course) |

---

### party-line (`~/Projects/party-line/`)

Session-to-session collaboration for Claude Code — a file-mailbox intercom, a two-AI-player
Constellation playtest harness, and handoff notes with a ghost responder, all on the Max
subscription with zero API-credit billing.

**Skills**

| Skill | What it does |
|---|---|
| `party-line` | Live messaging between Claude Code sessions over a file mailbox — join a channel, send, poll, and get woken by a background watcher when a peer writes. · [config →](usage-playbook.md#party-line) |
| `ghost` | Asks the previous session a question, answered as that session from its saved transcript by a subagent — the escape hatch when a handoff briefing leaves a gap. · [config →](usage-playbook.md#ghost) |
| `auto-handoff` | Proposes a handoff and launches the successor at the moment the work calls for one — fires on a planner→builder run-config note (T1), a completion-shaped stopping point (T2), or the Stop gate's context-fullness block (T3). · [config →](usage-playbook.md#auto-handoff) |
| `reaper` | Proposes closing a session's process — the predecessor that launched this one once its handoff note has been consumed (R2), or any open session Kyle names (R1, where an ambiguous name asks rather than guesses) — one SIGTERM after a live identity re-verification and one yes/no; never touches a transcript or a note. · [config →](usage-playbook.md#reaper) |

**Commands**

| Command | What it does |
|---|---|
| `/threshold` | Shows the T3 context-fullness threshold in force for the project, which layer set it, and the reading it will be compared against — then changes it with a stepped picker, effective at the next turn boundary with nothing restarted. · [config →](usage-playbook.md#threshold) |

---

### stopwatch (Tempo)

A biofeedback / rhythm-tracking browser app.

**Commands**

| Command | What it does |
|---|---|
| `/add-panel` | Scaffolds a new Rhythm Insights panel — creates `js/rhythm-panel-<key>.js`, registers it via `RhythmInsights.register`, wires the HTML slot, CLAUDE.md entry, and `sw.js` ASSETS + cache bump. · [config →](usage-playbook.md#add-panel) |
| `/new-engine-module` | Scaffolds a new `js/<name>.js` module and wires all touch-points in one shot — `<script>` tag, CLAUDE.md file-map + Script Load Order chain, `sw.js` ASSETS entry + `CACHE_NAME` bump, test stub. · [config →](usage-playbook.md#new-engine-module) |
| `/fix-bug` | Repo-tuned bug-fix loop — triages against known-failure playbooks first (stale SW cache is the #1 false alarm), root-causes before editing, adds a regression test, fixes minimally, verifies in a fresh browser context. · [config →](usage-playbook.md#fix-bug) |
| `/run-tests` | Runs the appropriate test suites based on the diff — `npm test` (headless engine suite) plus Firestore-rules and Life-OS council suites when their files are in play. Reports with flake-adjudication rules. · [config →](usage-playbook.md#run-tests) |
| `/ship-pr` | Lands current work as a PR — pre-flights the Definition of Done, runs the three pre-commit guard checks, creates the branch/commit with house conventions, pushes and opens the PR. Never merges. · [config →](usage-playbook.md#ship-pr) |

---

### forge-gap

A research / learning project following a structured learning spine.

**Commands**

| Command | What it does |
|---|---|
| `/document-stage` | Documents a just-finished stage in the learning spine, teaches the core concepts, then quizzes you via active recall. · [config →](usage-playbook.md#document-stage) |

---

### Life Nodes (`~/Desktop/Kyles Nodes/`)

Kyle's Obsidian vault for logging life data (doses, sleep, drinks, later Soft 30 and income) as append-only JSONL, viewed through Claude artifacts. Code skills live in `.claude/skills/`; the Cowork skills ship as the `life-nodes-cowork` plugin from the vault's own `kyles-nodes` marketplace.

**Skills (Claude Code)**

| Skill | What it does |
|---|---|
| `sync` | Commits and pushes the vault with a written message, fast-forward only; reports auto-committer health and bumps the Cowork plugin's patch version when `plugins/` changed. Kyle-only. · [config →](usage-playbook.md#sync-life-nodes) |
| `build-artifact` | Builds an artifact's page from its artifact note's Views, validates the palette in both themes, publishes it with only the `db` capability, writes `url` on first publish, then pushes every month of its data. Kyle-only. · [config →](usage-playbook.md#build-artifact-life-nodes) |
| `rebuild-artifact` | Rewrites an artifact's database from the vault, one document per stream per month, and verifies it fresh; the fix for a stale artifact. · [config →](usage-playbook.md#rebuild-artifact-life-nodes) |
| `audit` | Checks the vault for malformed lines, schema mismatches, broken or forked supersede chains, duplicates, dangling connections, and stale artifacts; repairs malformed lines only, one at a time on yes. · [config →](usage-playbook.md#audit-life-nodes) |
| `add-node` | Runs the node interview, then writes one new node note (host, streams and their schema blocks) and its data folder, and confirms the host edge. · [config →](usage-playbook.md#add-node-life-nodes) |
| `edit-node` | Changes a node note in place: a stream or field, a rename, a host move, prose, rules, or a rate table; stream changes are additive only once there's data. · [config →](usage-playbook.md#edit-node-life-nodes) |
| `archive-node` | Archives a node together with the artifacts that read it, archives one artifact alone, or revives either; moves notes under `Archive/`, never `Data/`, and pushes each artifact a final status document. Kyle-only. · [config →](usage-playbook.md#archive-node-life-nodes) |
| `design-artifact` | Ranks visualization ideas for a node's data, then interviews Kyle over the picked ideas and writes the artifact note (`reads`, Views, blank `url`) that `build-artifact` builds from. · [config →](usage-playbook.md#design-artifact-life-nodes) |

**Skills (Cowork plugin `life-nodes-cowork`)**

| Skill | What it does |
|---|---|
| `log` | Routes a message or screenshot to its nodes, appends entries to their JSONL streams after one confirm line per node, and pushes the touched months to every artifact that reads them. On "pull my shifts", also reads Gearhead shifts from Google Calendar, read-only. · [config →](usage-playbook.md#log-life-nodes) |
| `review` | Answers questions about logged data from resolved vault entries (totals, last times, what's left today); writes nothing. · [config →](usage-playbook.md#review-life-nodes) |

---

## Custom Subagents

Global subagents live in `agents/` (symlinked to `~/.claude/agents/`). These are explicit-dispatch only — launched by a skill that names them or by explicit request, never auto-delegated. Other subagent types live outside this repo: `Explore` and `Plan` ship with Claude Code itself, and plugin-provided ones (e.g., `code-reviewer` from Superpowers) come with their plugin.

| Agent | What it does |
|---|---|
| [`adversarial-reviewer`](../agents/adversarial-reviewer.md) | Zero-context, repo-read-only diff reviewer — anchors to HEAD, reviews the branch diff vs merge-base, writes numbered findings graded critical / should-fix / nice-to-have to the review mailbox. Never edits code. · [config →](usage-playbook.md#adversarial-reviewer) |
| [`review-judge`](../agents/review-judge.md) | Neutral zero-context judge — rules only on author-disputed findings (upheld / overruled / downgraded / upgraded), may re-grade severity, owes deference to neither side. Appends one-paragraph rulings to the mailbox. · [config →](usage-playbook.md#review-judge) |
