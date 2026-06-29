# Project Guide — claude-config

*Generated 2026-06-29 · via the `project-guide` skill (first dogfood run, on its own repo).*
*Evidence base: git history (24 commits, PRs #2–#7) and repo contents at this date.*

---

## 1. Snapshot (TL;DR)
**"Dotfiles for Claude Code."** A version-controlled personal config — 18 slash commands, 14 skills, global instructions, and a statusline — that `~/.claude/` symlinks to, so editing the repo *is* editing the live config (same inode). Stack is **Markdown prose specs + Bash** (no application code). ~3 weeks old (Jun 8–28 2026), solo-authored, actively developed. **Run it:** `git clone … && ./install.sh` symlinks everything into `~/.claude`. The most interesting thing: it treats a pile of prompt files as a real engineered system — idempotent installer, security-conscious linking, least-privilege tool grants, single-source constraints.

## 2. Purpose & problem
Claude Code's behavior is shaped by files in `~/.claude` (commands, skills, instructions). Left there, they're unversioned, un-reviewable, and machine-trapped. This repo makes that surface **canonical, git-tracked, and portable**: author once, symlink into `~/.claude`, and `/claudify-repo` vendors copies downstream into individual project repos. It's personal developer tooling — the "user" is one engineer optimizing their own AI-assisted workflow.

## 3. Capabilities — current state
**Working today:**
- **Installer** (`install.sh:39`) — idempotent symlink farm into `~/.claude`, backs up pre-existing real files, warns when linking from a non-`main` branch.
- **Session-lifecycle trio** — `/begin`, `/handoff`, `/wrap` (orient → handoff prompt → recap), each now with opt-in `--audio` (PR #6).
- **Audio engine** — `skills/narrate/` + `render-narration.sh` (local Kokoro TTS → MP3).
- **NotebookLM suite** — `nlm-skill`, `notebook-init`, `notebook-assist`, `audio-series`, `interview-prep` (notebook orchestration, audio "seasons").
- **Project/dev commands** — `/brainstorm`, `/prompt-optimize`, `/smoke-test`, `/tdd`, `/explore-plan`, `/boot_server`, `/envsetup`, the mock-SQL interview trio, `bug-hunt`, `kickoff`, `mini`, etc.
- **`project-guide`** (PR #7) — the skill producing this document.
- **Statusline** (`statusline-command.sh`).

**Stubbed / planned:** `agents/` is empty (`.gitkeep` only) — subagents are referenced but none vendored. `BACKLOG.md` + `docs/ideas/` hold 5 unbuilt explorations (registry/lockfile, fleet-manifest `/reconcile`, usage-telemetry pruning, `CONVENTIONS.md`).

## 4. Architecture & how it works
**Style: a symlink-farm config repo with a git-sourced installer.** Three moving parts:

1. **`install.sh`** links each *top-level git-tracked entry* into `~/.claude`, minus a `DENY` list (`README.md`, `install.sh`, `BACKLOG.md`, `docs`, `.gitignore`). It sources the link set from `git ls-tree`, **not** `ls` — so anything untracked or gitignored (secrets, `*.bak`, machine-local files) can **never** be linked in. Idempotent; backs up real files to `*.pre-claude-config.<timestamp>`.
2. **Content dirs** — `commands/*.md` (slash-command prompt specs; frontmatter `description` / `argument-hint` / `allowed-tools`) and `skills/<name>/SKILL.md` (larger capabilities, sometimes + `references/` or a helper `.sh`). `skills/` is symlinked as a whole dir, so a new skill appears on `git pull` with no re-install.
3. **`CLAUDE.md`** — global instructions loaded every session; `@import`s `operating-constraints.md` (single source) and defines the kickoff / improvement / new-feature modes + the git workflow.

```
repo (canonical)  ──install.sh symlinks──▶  ~/.claude/  ──loaded by──▶  Claude Code
   │  commands/  skills/  agents/  CLAUDE.md  statusline                  │
   └── /claudify-repo  ──vendors copies──▶  individual project repos ◀────┘
```

Two capability families have emerged: the **NotebookLM/audio** cluster and the **session-lifecycle** cluster (now bridged to audio via `narrate`).

## 5. Build history & key decisions
A short, decision-dense history (solo, ~24 commits). The load-bearing calls:

- **Git workflow: "keep me in the loop, don't gate on me"** (PR #2, commit `88698cb`). Claude commits/pushes/opens PRs/merges autonomously and briefs *after*, rather than asking before each step. **Tradeoff:** velocity and momentum over per-action control; mitigated by "branch + PR for every change" as the durable record.
- **Single-source operating constraints via `@import`** (`4b66358`, `fc29d14`). One `operating-constraints.md` governs every skill/command/subagent instead of repeating rules. **Tradeoff:** DRY + one canon vs. an extra indirection.
- **Installer hardening** (`c1fd257`): discover link targets from `git ls-tree` + warn on non-main branch. **Why:** a `ls`-based installer could symlink secrets or backups into live config; sourcing from git makes that structurally impossible. Security-by-construction.
- **Least-privilege frontmatter** (`5dd95ce`, `1ea7f49`): backfilled `allowed-tools` across all commands (14/15, then 15/15). **Why:** each command declares exactly the tools it may use — a readable, auditable capability contract.
- **Subtraction pressure** (PR #4 removed the deprecated `/moonshot` alias; `BACKLOG.md` ideas "commands earn their keep" + "telemetry-forged commands"). Recognizes that an ever-growing spec pile rots; wants usage data to prune.
- **Audio: local Kokoro over NotebookLM** (PR #6). For verbatim narration of a specific brief, local Kokoro (free, no quota, verbatim) beats NotebookLM (can't perform a script). Plus **opt-in flag over always-on** (no cost on normal runs) and a **shared `narrate` engine** the three commands call. **Tradeoff:** a small render dependency vs. DRY + reuse.
- **project-guide** (PR #7): this skill.

*Rationale confidence: high — most PR/commit messages explicitly record the "why," which is itself a strong habit.*

## 6. Concepts & vocabulary
- **Symlink farm / dotfiles** — config kept in a repo, linked into the live location; here `~/.claude` → repo (`install.sh`).
- **Source-of-truth from `git ls-tree`** — deriving the install set from tracked files so untracked/secret files can't leak into config.
- **`@import`** — CLAUDE.md pulling in `operating-constraints.md` as a single canonical include.
- **Frontmatter contract / `allowed-tools`** — per-command least-privilege tool declaration (the `CONVENTIONS.md` backlog item formalizes it).
- **Command vs. skill** — slash-command prompt spec (`commands/*.md`) vs. larger named capability (`skills/<name>/SKILL.md`, may ship references/scripts).
- **Vendoring** — `/claudify-repo` copying upstream specs into a project repo.
- **DENY list / idempotent installer** — installer excludes repo-meta; safe to re-run.
- **Propose-defaults** — interview pattern: propose sensible defaults rather than asking per-parameter (used across skills).
- **Deferred MCP tools / multi-agent fan-out** — on-demand tool schemas; `ultracode`/workflow orchestration referenced by `bug-hunt` and `project-guide`'s thorough mode.

## 7. Recruiter & hiring-manager lens
*Two-sided and candid — the section that preps you to defend the repo.*

**Reads as a strength (lead with these):**
- **Systems thinking applied to "just config."** An idempotent installer with backups, non-main-branch warnings, and a **secrets-can't-leak-by-construction** link source (`git ls-tree` not `ls`) is senior-flavored. Most people's dotfiles are a pile of `cp`.
- **Decision capture & PR hygiene.** PR bodies record *why* and *tradeoffs* (#2, #6). A reviewer reading the history sees an engineer who reasons, not just ships.
- **DRY + self-governance.** Single-source `@import` constraints; least-privilege `allowed-tools`; explicit "what's intentionally NOT here" in the README; belt-and-suspenders secret rules in `.gitignore`.
- **Product self-awareness.** `BACKLOG.md`/`docs/ideas/` show the growth-vs-rot problem is already seen, with designed responses (registry+lockfile, `/reconcile`, usage telemetry).

**Reads as a weakness / "junior smell" / risk (own these):**
- **Zero tests, zero CI.** Defensible for a prose repo — but a reviewer *will* ask. Strong answer: it's intentional (a "docs-as-validator" `CONVENTIONS.md` + frontmatter contract is backlogged), and the credible first lint is cheap (shellcheck the 3 Bash scripts; validate command frontmatter; assert `install.sh` DENY covers new top-level files). Saying that turns a gap into evidence of judgment.
- **Bash without linting; one unverified assumption.** `render-narration.sh` hardcodes the Kokoro endpoint (`:8880`) — documented and overridable, but unproven, and not shellcheck'd in CI.
- **Heavy machine coupling.** Several skills assume specific paths (`~/Cowork/second-brain/…`, `~/steame-sql-practice/…`, `~/Projects/…`). Someone cloning this can't run much. Frame it honestly: *personal tooling, not a library* — generalizing it is explicitly out of scope.
- **Surface-area vs. measured usage.** 18 commands + 14 skills authored fast; some specs are very long. Could read as over-engineering for a solo user. The backlog ("commands earn their keep", telemetry-forged) names this — cite it as the planned correction.

**Before showing this repo to anyone:** nothing dangerous (no committed secrets; `.gitignore` is thorough). The only tidy-up worth doing first is a one-paragraph README note on the machine-coupling/personal-tooling scope, so a cloner isn't surprised.

## 8. Interview readiness
*Questions first; scaffolds below.*
1. Walk me through `install.sh` — why source from `git ls-tree` instead of `ls`?
2. Commands vs. skills — when do you reach for each?
3. How do you test a repo that's almost entirely prose? What *would* you add?
4. Why local Kokoro over NotebookLM for the audio feature?
5. You've got 30+ specs after 3 weeks — how do you keep them from rotting?
6. Why single-source the operating constraints via `@import`?

---

**Scaffolds:**
1. `ls` would link untracked/gitignored files → secrets could leak into live config; `git ls-tree` makes the install set exactly the tracked set — security by construction; plus idempotency + backups.
2. Command = a single slash-invoked prompt with a tool contract; skill = a larger named capability that can ship references/helper scripts and be invoked by name; lifecycle prompts are commands, orchestration/engines are skills.
3. Honestly, none today — deliberate for prose; the cheap, high-value adds are shellcheck on the Bash, a frontmatter validator, and a check that new top-level files are classified in `install.sh`'s DENY; the contract (`CONVENTIONS.md`) is backlogged.
4. NotebookLM can't perform a script verbatim and is quota'd/outward; Kokoro is local, free, repeatable, and reads the exact brief — right tool for narration.
5. Usage telemetry → prune on lived-invocation evidence (the "Coliseum"/`/forge` backlog ideas); subtraction, not just addition.
6. One canonical file governs all specs — change the rule once, no drift across 30+ files.

## 9. Talking points
**Elevator (~45s):** "I version-control my entire Claude Code setup as a repo — slash commands, skills, global instructions — that symlinks into the live config, so editing the repo edits my tooling in place. The interesting part isn't the prompts, it's that I treat it like a real system: an idempotent installer that can't accidentally link secrets, least-privilege tool grants per command, and single-sourced operating rules. It's where I codify how I want to work with AI."

**Deep cut (~2 min):** Lead with the installer-safety story (`git ls-tree` not `ls` → secrets can't leak, idempotent, branch-aware) as the "systems thinking on config" hook; then the audio-feature decision (local Kokoro over NotebookLM for verbatim narration, opt-in flag, shared engine reused across three commands) as the "I pick tools by their actual constraints and design for reuse" story. Close on the self-governance angle: a backlog that plans to *prune* commands on usage data, not just add them.

## 10. Gaps, debt & next moves
1. **`CONVENTIONS.md` + a frontmatter validator** *(S–M, already backlogged)* — documents the command contract and gives the prose repo its first cheap "test." Highest signal-per-effort; do first.
2. **shellcheck the 3 Bash scripts** *(S)* — `install.sh`, `statusline-command.sh`, `render-narration.sh`.
3. **Verify the Kokoro endpoint assumption** in `render-narration.sh` *(S)* — the one unproven runtime bit.
4. **Usage telemetry → prune** *(L, backlogged)* — the Coliseum/`/forge` ideas; address surface-area-vs-usage with data.

## 11. Map of the codebase
| Path | What |
|---|---|
| `install.sh` | Idempotent symlink installer; git-sourced link set + DENY list |
| `CLAUDE.md` | Global instructions; `@import`s constraints; defines modes + git workflow |
| `operating-constraints.md` | Single-source rules governing every spec |
| `commands/*.md` | 18 slash-command prompt specs (frontmatter contract) |
| `skills/<name>/SKILL.md` | 14 skills; NotebookLM/audio cluster + lifecycle/engine skills |
| `skills/narrate/`, `skills/project-guide/` | The two newest (audio + this guide generator) |
| `BACKLOG.md` + `docs/ideas/` | 5 unbuilt explorations (registry, reconcile, telemetry, conventions) |
| `agents/` | Empty (`.gitkeep`) — future subagents |
| `statusline-command.sh` | Custom statusline |

---

**Strong / what I'd flag (one-line summary):**
- **Strong:** installer safety (`git ls-tree`, idempotent, backups), least-privilege `allowed-tools`, single-source constraints, decision-capturing PRs, a self-aware backlog.
- **Flag:** no tests/CI (defensible but ask-bait — have the "here's the cheap lint I'd add" answer ready), unlinted Bash + one unverified endpoint, heavy machine-path coupling (personal tooling, not a library).
