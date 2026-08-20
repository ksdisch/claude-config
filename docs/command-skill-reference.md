# Command & Skill Reference

A complete index of every custom slash command, skill, and project-specific automation in this setup. Global items are available everywhere; project-specific items live in that project's `.claude/` folder and are only active when you're working in that project.

This doc is the index — *what exists*. Its companion, the
**[Usage Playbook](usage-playbook.md)**, is the judgment layer: *how to run each one* —
suggested model + effort, the situations worth reaching for it in, and what it pairs with.
Every row below links to its card with `config →`.

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
| [`/begin`](../commands/begin.md) | Open a session — orients on project state (branch, recent commits, open PRs), recaps from the last `/wrap` log, offers a recall question, then routes into the project's session-start spec. · [config →](usage-playbook.md#begin) |
| [`/wrap`](../commands/wrap.md) | End-of-session close-out — recaps the work, explains the why, builds vocabulary, quizzes via active recall, and suggests next moves. Saves a dated log to `.claude/`. · [config →](usage-playbook.md#wrap) |
| [`/catchup`](../commands/catchup.md) | Mid-session audio catch-up — narrates the session so far (or just the most recent output) as an MP3, then keeps working. Does not end the session. · [config →](usage-playbook.md#catchup) |
| [`/handoff`](../commands/handoff.md) | Generates a self-contained handoff prompt you can paste into a fresh session to continue work without losing context. Also prints a plain-English "what's next & why" briefing. · [config →](usage-playbook.md#handoff) |
| [`/launch`](../commands/launch.md) | Opens a new terminal window in a project directory and starts a fresh Claude Code session there, with the prompt on the clipboard (or auto-submitted via `--send`). Reads directory, model, and effort from the run-config note just produced, and names the session descriptively (`claude --name`) so it's findable in the resume picker later; `--remote` starts it as a Remote Control session so the name reaches the claude.ai/mobile lists too. · [config →](usage-playbook.md#launch) |
| [`/learn`](../commands/learn.md) | Mines the current session for reusable patterns and — after a confirmation gate — saves each as a proper skill (house layout + reference-doc row + playbook card), landed via branch + PR. · [config →](usage-playbook.md#learn) |

### Planning & Exploration

| Command | What it does |
|---|---|
| [`/explore-plan`](../commands/explore-plan.md) | Explore → plan → confirm before any code. Reads relevant code, proposes 2–3 ranked approaches, and waits for approval before implementing. · [config →](usage-playbook.md#explore-plan) |
| [`/brainstorm`](../commands/brainstorm.md) | Multi-mode structured brainstorm using blind parallel agent teams. Modes: Moonshot, QuickWin, Subtract, Harden, Premortem, Friction, Delight, Positioning, Reach. Produces vision docs + backlog stubs. · [config →](usage-playbook.md#brainstorm) |
| [`/autonomous-milestone`](../commands/autonomous-milestone.md) | With a target → autonomously plan/build/test/verify end-to-end. With no target → triages the backlog into ranked candidates, lets you pick, then builds. Uses multi-agent ultracode orchestration. · [config →](usage-playbook.md#autonomous-milestone) |
| [`/prompt-optimize`](../commands/prompt-optimize.md) | One-shot prompt rewriter — diagnoses a rough draft, recommends the right workflow archetype + model + effort level, and returns a ready-to-paste optimized prompt. Advisory only; never executes. · [config →](usage-playbook.md#prompt-optimize) |
| [`/reframe-orchestrator`](../commands/reframe-orchestrator.md) | Restructures a repo's `.claude/orchestrator.md` from a human-paused dispatch persona into a mode-independent invariants-and-gates doc. Docs only. · [config →](usage-playbook.md#reframe-orchestrator) |

### Development Workflows

| Command | What it does |
|---|---|
| [`/tdd`](../commands/tdd.md) | Test-first loop — write failing tests for a spec, confirm they fail for the right reason, commit them, then write implementation until they pass without modifying the tests. · [config →](usage-playbook.md#tdd) |
| [`/screenshot-iterate`](../commands/screenshot-iterate.md) | Visual loop — implement against a mock, screenshot the running app, compare to target, fix diffs, repeat until it matches. · [config →](usage-playbook.md#screenshot-iterate) |
| [`/smoke-test`](../commands/smoke-test.md) | Sets up a manual smoke test — figures out what to verify, opens needed pages in Chrome, then gives you a precise do-this / see-that checklist. · [config →](usage-playbook.md#smoke-test) |
| [`/trim-context`](../commands/trim-context.md) | Finds and fixes token bloat in a repo — oversized CLAUDE.md, bloated memory files, large always-loaded files, `.claude/` cruft. · [config →](usage-playbook.md#trim-context) |

### Environment & Setup

| Command | What it does |
|---|---|
| [`/boot_server`](../commands/boot_server.md) | Detects how the project is served, starts the dev server in the background, waits until ready, and opens the running page in Chrome. Pass `"live"` to open the deployed page instead. · [config →](usage-playbook.md#boot_server) |
| [`/envsetup`](../commands/envsetup.md) | Opens the project's `.env` in your editor and the credential-generation page in Chrome, with a key stub + source comment pre-added. · [config →](usage-playbook.md#envsetup) |
| [`/claudify-repo`](../commands/claudify-repo.md) | Vendors chosen global commands/skills into a repo (so they work in cloud/web sessions and for collaborators) and launches the recommender to design project-specific automations. · [config →](usage-playbook.md#claudify-repo) |
| [`/wiki-init`](../commands/wiki-init.md) | Initialize a project wiki — creates PROJECT.md, HANDOFF.md, and minimum structure for the current project (no args), a specific path, or all top-level projects under ~/Projects/ (`--all`). Idempotent (never overwrites an existing wiki); lands changes via branch + PR. · [config →](usage-playbook.md#wiki-init) |
| [`/wiki-backfill`](../commands/wiki-backfill.md) | Backfills a retroactive `Wiki/History.md` evolution narrative — mines merged PRs, git history, tags, wrap logs, and ADRs into a milestone-by-milestone, append-only history page for one project or all wiki-bearing projects (`--all`). Refuses to overwrite an existing History.md; lands changes via branch + PR. · [config →](usage-playbook.md#wiki-backfill) |

---

## Global Skills

Available everywhere. Live in `skills/`. Claude invokes these automatically when the context matches, or you can request them directly.

### Project Kickoff & Setup

| Skill | What it does |
|---|---|
| [`kickoff`](../skills/kickoff/SKILL.md) | Turns a raw idea into a structured launch — runs a deep adaptive discovery interview, produces an approved kickoff brief + phased plan, then scaffolds the project folder, git repo, and private GitHub repo. Automatically initializes a project wiki. · [config →](usage-playbook.md#kickoff) |
| [`mini`](../skills/mini/SKILL.md) | Kicks off a new mini coding project under `~/Projects/mini/` — short discovery interview (idea, problem, scope, tech) then full repo scaffold. · [config →](usage-playbook.md#mini) |
| [`project-wiki`](../skills/project-wiki/SKILL.md) | Maintain an evidence-controlled project wiki — three modes: INIT (idempotently create PROJECT.md, HANDOFF.md, and topic pages that synthesize across sources; never overwrites, never leaves a `Wiki/` holding only an index), MAINTAIN (surgical updates when integrating sources, recording decisions, updating status, or appending History.md milestones), and BACKFILL (mine merged-PR and git history into an append-only Wiki/History.md evolution narrative). Auto-invoked in any project that has wiki sentinel files. · [config →](usage-playbook.md#project-wiki) |
| [`grill-me`](../skills/grill-me/SKILL.md) | Typed-only entry point (`/grill-me`) that starts a `grilling` session — a relentless interview to sharpen a plan or design before acting on it. · [config →](usage-playbook.md#grill-me) |
| [`grilling`](../skills/grilling/SKILL.md) | Interviews you relentlessly about a plan, decision, or idea until shared understanding — works the design tree in rounds of numbered questions, each with a recommended answer, until no branch is left silently assumed. · [config →](usage-playbook.md#grilling) |

### Session & Context Management

| Skill | What it does |
|---|---|
| [`reorient`](../skills/reorient/SKILL.md) | Use when returning to a project after a real gap (days to months). Rebuilds fluency and routes the next move to the right skill. NOT for ordinary session starts (use `/begin`). · [config →](usage-playbook.md#reorient) |
| [`onboard`](../skills/onboard/SKILL.md) | Role-played new-hire onboarding — Claude plays a senior teammate briefing you on the current project (and optionally the whole lineup) in five segments, each ending in a Q&A where it suggests the questions you ask; leaves a dated onboarding packet. · [config →](usage-playbook.md#onboard) |
| [`reweave`](../skills/reweave/SKILL.md) | Re-integrates a follow-up answer into the original response at the source so you get one clean standalone version instead of mentally splicing the update back in. · [config →](usage-playbook.md#reweave) |
| [`ship-and-route`](../skills/ship-and-route/SKILL.md) | End-of-build "take it from here" flow — safely lands any outstanding git work behind a review gate, walks through findings, then routes the next move (2–3 ranked options). · [config →](usage-playbook.md#ship-and-route) |
| [`backlog-hygiene`](../skills/backlog-hygiene/SKILL.md) | Operates on an already-stocked backlog to decide what's next — grooming, sequencing, decomposing, phase planning. Decision-first; builds nothing and invents nothing. · [config →](usage-playbook.md#backlog-hygiene) |
| [`replenish`](../skills/replenish/SKILL.md) | Use when a project's backlog has run dry — combines bug-hunt and multiple brainstorm modes as parallel lanes to refill it with bugs and new ideas in one session. · [config →](usage-playbook.md#replenish) |

### Quality & Debugging

| Skill | What it does |
|---|---|
| [`bug-hunt`](../skills/bug-hunt/SKILL.md) | Proactively hunts for bugs you don't know about — fans out specialized finder agents, adversarially verifies every finding, and presents a ranked triage list. Optionally hands bugs to systematic-debugging. · [config →](usage-playbook.md#bug-hunt) |
| [`adversarial-review`](../skills/adversarial-review/SKILL.md) | Pre-merge author↔reviewer↔judge loop — a zero-context reviewer files graded findings on the branch diff, the author triages (accept/dispute), a neutral judge rules on disputes, fixes get re-checked (capped review rounds), and the adjudicated summary lands as a PR comment with a CLEAR / NOT-CLEAR merge verdict. · [config →](usage-playbook.md#adversarial-review) |
| [`artifacts-audit`](../skills/artifacts-audit/SKILL.md) | Audits a codebase against a canonical artifact taxonomy, then produces a concrete generation + maintenance plan. Plans only; does not write artifacts. · [config →](usage-playbook.md#artifacts-audit) |
| [`artifacts-generate`](../skills/artifacts-generate/SKILL.md) | Implements an artifact plan produced by `artifacts-audit`. Supports one-at-a-time (maximum oversight) or batch generation of READMEs, ADRs, design docs, diagrams, runbooks, etc. · [config →](usage-playbook.md#artifacts-generate) |
| [`seed-hunt`](../skills/seed-hunt/SKILL.md) | Post-research-project workflow — verifies the repo is truly closed, harvests lessons into the selection bar, sweeps arXiv for candidate papers, scores a shortlist, and presents a decision brief. · [config →](usage-playbook.md#seed-hunt) |

### NotebookLM

| Skill | What it does |
|---|---|
| [`notebook-init`](../skills/notebook-init/SKILL.md) | Bootstraps a new NotebookLM notebook end-to-end — interview, source curation, creation, baseline artifact generation, local sidecar. · [config →](usage-playbook.md#notebook-init) |
| [`notebook-assist`](../skills/notebook-assist/SKILL.md) | Works with existing notebooks in three modes: refine an artifact idea, brainstorm new artifacts by reading the notebook, or manage sources (add/list/refresh/remove). · [config →](usage-playbook.md#notebook-assist) |
| [`notebook-merge`](../skills/notebook-merge/SKILL.md) | Merges 2+ existing notebooks into one unified notebook — migrates sources and notes, regenerates artifacts, proposes new cross-notebook synthesis, archives originals. · [config →](usage-playbook.md#notebook-merge) |
| [`audio-series`](../skills/audio-series/SKILL.md) | Generates an episodic NotebookLM audio course from an existing notebook — a flagship "building" season plus standalones, with optional Study Guide + Quiz per episode. · [config →](usage-playbook.md#audio-series) |
| [`video-series`](../skills/video-series/SKILL.md) | Generates an episodic NotebookLM video course from an existing notebook — same episodic structure as `audio-series` but video overviews with per-season visual style. · [config →](usage-playbook.md#video-series) |
| [`portfolio-notebook-sync`](../skills/portfolio-notebook-sync/SKILL.md) | Keeps the research-portfolio notebook in step with `~/Projects/portfolio` — a manifest-backed drift check, `--add <project>` to onboard a newly carded project, or `--add-paper <project>` to add a merged `/research-paper` write-up. · [config →](usage-playbook.md#portfolio-notebook-sync) |
| [`curriculum-sync`](../skills/curriculum-sync/SKILL.md) | Keeps a notebook's derived content (audio/video seasons, study guides, per-episode quizzes) and its paired home-base course in step with the repos underneath — a ledger-backed drift check, `--adopt` to baseline an existing pair, `--refresh` to regenerate what's stale, `--new` to build a whole chain. · [config →](usage-playbook.md#curriculum-sync) |
| [`nlm-skill`](../skills/nlm-skill/SKILL.md) | Expert guide for the `nlm` CLI and NotebookLM MCP server — use when interacting with NotebookLM programmatically. · [config →](usage-playbook.md#nlm-skill) |

### Research & Writing

| Skill | What it does |
|---|---|
| [`research-paper`](../skills/research-paper/SKILL.md) | End-of-project write-up for reproduce-and-measure research projects. From a completed repo's recorded results — produces a professional research paper and a presenter pack. · [config →](usage-playbook.md#research-paper) |
| [`paper-eli5`](../skills/paper-eli5/SKILL.md) | Rewrites someone else's research paper into plain English 1:1 (same headings, same paragraph order, nothing summarized or dropped). Equations, tables, and inline math stay verbatim with a plain-words gloss, and every display equation also gets a "named form" — the same equation with each variable replaced by what it actually is, plus a `where:` legend — with math normalized to canonical `$…$` so `/paper-gloss` can typeset it. · [config →](usage-playbook.md#paper-eli5) |
| [`paper-gloss`](../skills/paper-gloss/SKILL.md) | Post-processes a `paper-eli5` output into an interactive HTML artifact: AI proposes jargon terms with plain-English expansions, you trim the list, then every occurrence becomes a clickable term that reveals the expansion in a popup, plus a full-glossary toggle panel. Typesets equations and inline math as real notation instead of raw LaTeX, and renders each equation's named form and legend as a grouped block between the equation and its plain-words gloss. Delivers a `-glossed.html` file and a published claude.ai Artifact link. Pages carry a highlight-and-note annotation layer with Markdown/JSON export. Run after `/paper-eli5`; `--retrofit` repairs math and `--annotate` adds the annotation layer to an already-published page at its existing URL. · [config →](usage-playbook.md#paper-gloss) |
| [`paper-figures`](../skills/paper-figures/SKILL.md) | Retrofits the real figure images into an already-generated `paper-eli5` output — re-finds the original source, harvests the figures (direct download or browser screenshot), and fills the `[Figure N]` placeholders in both the markdown and the glossed HTML, with one contact-sheet approval gate. Web sources only. Run after `/paper-eli5` or `/paper-gloss`. · [config →](usage-playbook.md#paper-figures) |
| [`project-guide`](../skills/project-guide/SKILL.md) | Generates a comprehensive point-in-time guide to any project — what it is now, history of how it was built, vocabulary to discuss it fluently, and a recruiter/interview lens. · [config →](usage-playbook.md#project-guide) |
| [`narrate`](../skills/narrate/SKILL.md) | Renders written text to speech (MP3) using local Kokoro TTS. The reusable audio-delivery engine used by catchup, handoff, and other skills. · [config →](usage-playbook.md#narrate) |
| [`youtube-transcript`](../skills/youtube-transcript/SKILL.md) | Downloads a YouTube video's transcript with yt-dlp — manual captions, then auto-generated, with local Whisper as a gated last resort — and converts it to deduplicated plain text. · [config →](usage-playbook.md#youtube-transcript) |
| [`youtube-breakdown`](../skills/youtube-breakdown/SKILL.md) | Turns a transcript or YouTube URL into a structured breakdown in one of four modes — Study Notes, Quick Reference, Critique, or Actionable Insights — then offers to save it under `~/Learning`. Always asks which mode first; mining a video for Claude Code ideas is `cc-yt-idea-mine`'s lane. · [config →](usage-playbook.md#youtube-breakdown) |
| [`cc-yt-idea-mine`](../skills/cc-yt-idea-mine/SKILL.md) | Exhaustively mines a video transcript for every segment implementable in your Claude Code setup — a tiered, dedup-tagged, leverage-ranked report saved under `~/Learning`, then a gated, verified capture of picked ideas into claude-config's backlog. Proposes only; never builds. · [config →](usage-playbook.md#cc-yt-idea-mine) |

### Personal Coaching

| Skill | What it does |
|---|---|
| [`career-coach`](../skills/career-coach/SKILL.md) | ICF MCC-level career and life coaching — progressive clarity on your next career move, grounded in values, life stage, and what you actually want. Supports multi-session continuity via [SNAPSHOT] / [UPDATE] / [FOCUS] tags. Auto-triggers when you feel stuck, unfulfilled, or at a professional crossroads. · [config →](usage-playbook.md#career-coach) |
| [`teach`](../skills/teach/SKILL.md) | Multi-session tutor that treats the current directory as a persistent teaching workspace — mission-grounded HTML lessons sized to your zone of proximal development, printable reference docs, and ADR-style learning records. Typed-only (`/teach`); run from a dedicated learning directory. · [config →](usage-playbook.md#teach) |
| [`teach-research`](../skills/teach-research/SKILL.md) | Research companion for `teach` — mission interview, parallel six-modality source discovery, a curation gate, then cached digests plus a curated `RESOURCES.md` that `/teach` consumes unchanged. Typed-only (`/teach-research`); run from the learning directory. · [config →](usage-playbook.md#teach-research) |

### UI & Frontend

| Skill | What it does |
|---|---|
| [`match-the-mock`](../skills/match-the-mock/SKILL.md) | Implements a UI against a visual target using see-and-correct iteration — screenshot → compare → fix → repeat. The auto-triggering sibling of `/screenshot-iterate`. · [config →](usage-playbook.md#match-the-mock) |

---

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
| `rebrief-a2c` | Re-entry after time away — sweeps Gmail for replies, bounces, and unsent drafts, sweeps the Todoist A2C project for done/overdue, reconciles both against the prospect files, then briefs and primes the day's or week's work. · [config →](usage-playbook.md#rebrief-a2c) |

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

## Custom Subagents

Global subagents live in `agents/` (symlinked to `~/.claude/agents/`). These are explicit-dispatch only — launched by a skill that names them or by explicit request, never auto-delegated. Other subagent types live outside this repo: `Explore` and `Plan` ship with Claude Code itself, and plugin-provided ones (e.g., `code-reviewer` from Superpowers) come with their plugin.

| Agent | What it does |
|---|---|
| [`adversarial-reviewer`](../agents/adversarial-reviewer.md) | Zero-context, repo-read-only diff reviewer — anchors to HEAD, reviews the branch diff vs merge-base, writes numbered findings graded critical / should-fix / nice-to-have to the review mailbox. Never edits code. · [config →](usage-playbook.md#adversarial-reviewer) |
| [`review-judge`](../agents/review-judge.md) | Neutral zero-context judge — rules only on author-disputed findings (upheld / overruled / downgraded / upgraded), may re-grade severity, owes deference to neither side. Appends one-paragraph rulings to the mailbox. · [config →](usage-playbook.md#review-judge) |
| [`silent-failure-hunter`](../agents/silent-failure-hunter.md) | Read-only auditor that hunts silent failures — swallowed errors, empty catches, dangerous fallbacks, broken error propagation, missing boundary handling — over a given scope, graded on `bug-hunt`'s critical/high/medium/low rubric. It is the dedicated finder for that skill's silent-failure lens, and also runs standalone. Never edits code. · [config →](usage-playbook.md#silent-failure-hunter) |
| [`spec-miner`](../agents/spec-miner.md) | Opus-pinned brownfield spec extractor — without a capability input it maps the repo into capabilities; with one it mines that capability into a flat Requirement/Invariant spec file with machine-parseable metadata. Writes only `openspec/specs/<capability>/spec.md`, and never overwrites an existing spec unless dispatched with `OVERWRITE=yes`. · [config →](usage-playbook.md#spec-miner) |
