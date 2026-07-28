# Fleet manifest + `/reconcile`: make single-source true on demand

**Status:** Idea — not committed. Added by `/brainstorm` (`moonshot` mode) on 2026-06-18.
**Lens:** futurist · **Fit:** identity-shift (stretch) · **Boldness:** audacious

## Premise

claude-config promises single-source (A1) and propagation (A2), but enforces
neither — `/claudify-repo` copies and forgets, the symlink trusts that edits
reach `main`, and the only record of which repos carry the config is prose in an
auto-memory file. The promise is real; the mechanism is faith. Drift is invisible
until it bites, and this week it bit twice. A declared manifest + an on-demand
reconcile verb makes the two core promises checkable without changing what the
repo fundamentally is.

## The bet

The one thing that must be true: **drift is dangerous only because it's invisible.**
`/claudify-repo` is fire-and-forget and keeps no record of which repos it touched,
so the only index of the blast radius is one paragraph in an auto-memory note.
Make the blast radius a declared, machine-checkable artifact the repo owns, and
both failure modes that bit this week become catchable by running one command.
(Targets **A1** — symlink single-source strands on unmerged branches — and **A2**
— vendoring silently drifts/goes stale.)

Veteran reaction: *"A control loop for 7 markdown repos is k8s cosplay — but a
manifest that names what `/claudify-repo` already does silently, and a command
that re-walks it? That's the registry this thing was missing from day one. Why
did vendoring ever forget where it vendored?"*

**Why now:** Both failure modes are live, not hypothetical. `operating-constraints.md`
spent its whole life on `feat/smoke-test-command` and only reached `main` via PR #3
this week; 7 repos carried stale unmerged `feat/operating-constraints` branches that
had to be hunted down, abandoned, and re-vendored by hand. The fleet just crossed
the size (7 consumer repos + Cowork copies) where memory-as-index demonstrably broke.

## Credible first step

Add `fleet.yml` (declared targets: repo path + which commands/skills/constraints
each should carry, seeded from the 7 repos already named in the
`operating-constraints-single-source` memory note) and `commands/reconcile.md` — a
markdown spec that (1) reads `fleet.yml`, (2) for each target greps its `.claude/`
for vendored copies and diffs them against canonical, (3) flags canonical files not
yet on `main` (the A1 case), (4) prints a drift table + ready-to-run merge/re-vendor
PR commands. Pure git + reasoning, no daemon. Then add one line to `claudify-repo.md`
so every future vendor **appends** its target to `fleet.yml` — closing the loop so
the registry can never silently fall behind reality.

## Decisions / open questions

- **fleet.yml granularity:** per-repo list of every vendored command/skill, or coarse
  tiers (`constraints-only` vs `full kit`)? Start coarse; the operating-constraints
  case is the proven need.
- **Report vs act:** does `/reconcile` only report + emit PR commands, or also open the
  PRs (`gh pr create`)? v1 reports; opening stays opt-in to honor act-vs-assess.
- **Where fleet.yml lives:** repo (versioned, shareable) vs `~/.claude/projects` memory
  (private)? Repo — so it's the durable index the memory note currently impersonates —
  but confirm no private repo paths leak into a shareable file.
- **Remote repos:** how does `/reconcile` handle private collaborator repos with no local
  clone — local-clone-only for v1, or `gh` API reads? Scope v1 to local clones.
- **Vs the memory note:** does `fleet.yml` supersede it (note becomes a pointer) or mirror
  it (two sources, new drift)? Must supersede — two indexes recreates A2 one level up.

## Dependencies

- The `operating-constraints-single-source` memory note — seeds the initial `fleet.yml`
  target list (the 7 named repos).
- `commands/claudify-repo.md` — must be edited to append each vendor to `fleet.yml`, or
  the registry desyncs from reality the first time it's bypassed.
- Local clones of the target repos for v1 (git diff against their `.claude/` dirs); `gh`
  CLI for the PR-emission step.
- git/gh already in use across the fleet — no new infra.

## Explicitly out of scope (revisit later)

- Any always-on daemon, cron, or reconciliation loop — `/reconcile` is on-demand only.
- Autonomous merging/promotion of PRs without Kyle — reconcile proposes, Kyle disposes.
- A2's Cowork copies (the `SYNCED COPY` blocks) — those loaders can't read `~/.claude` and
  aren't git repos; leave to the existing manual-copy note for now.
- Runtime correctness of the markdown specs themselves (A3) — reconcile checks
  presence/version, not whether a command behaves.
- Discoverability of the ~29 commands (A4) and rollback/staging (A5) — adjacent, not this wedge.

## Identity/positioning note

claude-config gains a declared source-of-truth for its own distribution (`fleet.yml`)
and a new verb, `reconcile` — it shifts from "upstream you hope propagated" to "source
that knows its own blast radius and can audit it." What it does **not** become: an
always-on agent, a daemon, or autonomous fleet management. It stays files-Kyle-edits +
a command-Kyle-invokes; reconcile is on-demand and proposes PRs for Kyle to merge. The
soul ("dotfiles for Claude Code") is intact; the repo just stops being amnesiac about
where it ships.

---

## Status update — 2026-07-28

Still not built. The bet's premise stopped being hypothetical: this seam published third-party
PII across 13 public repos, and removing it took three widening manual passes. Full incident
record, remediation scope, and process lessons live in [`BACKLOG.md`](../../BACKLOG.md) under
this item.

**Two assumptions above are now known wrong** — fix them before designing:
- **"7 consumer repos"** (§ Why now, § Credible first step): it is **18 repos with vendored
  `.claude/commands/`, 13 of them public**. Re-derive the list; don't seed from the memory note.
- **"Start coarse"** (§ Decisions, granularity): a *prune* has to know what should no longer be
  there, which coarse tiers can't express. Revisit.

Also newly relevant: § Decisions asks where `fleet.yml` lives and flags "confirm no private repo
paths leak into a shareable file." `claude-config` is now **public**, and 5 of the 18 fleet repos
are private — that is a live constraint, not a footnote.

## Handoff prompt (ready to paste)

Paste the block below into a fresh session to start this work. It carries the landmines from the
2026-07-28 purge that a cold session would otherwise re-hit.

**Run it as:** `claude --model claude-fable-5 --effort xhigh` — the open design questions need
deciding before code, and the sizing assumption is already stale.

````markdown
# Context handoff — claude-config: fleet manifest + /reconcile (vendoring prune)

## Overview

`claude-config` (`~/Projects/claude-config`, PUBLIC) is "dotfiles for Claude Code" — the
canonical source for global slash commands, skills, and subagents, symlinked into `~/.claude/`.
It is also an upstream: `commands/claudify-repo.md` vendors *copies* into project repos.

You are building the fix for a root cause proven expensively on 2026-07-28: **`/claudify-repo`
copies and never prunes**, so deleting something upstream leaves it live downstream with no
signal. Read first, in order:
1. `docs/ideas/fleet-manifest-reconcile.md` — the full design write-up (this file).
2. `BACKLOG.md` — the `[Exploration] Fleet manifest + /reconcile` item, whose bullets carry a
   worked example and three process lessons from the incident.

## What's done

Nothing on this feature. The 2026-07-28 work was the incident that motivates it (all on `main`):
- PRs #53, #54 — deleted `/mock-sql-interview`, `/mock-sql-demo`, `/mock-sql-audio` (they named
  two real interviewers; the repo is public).
- Fleet remediation, by hand, in three widening passes: 17 repos' default branches → 78 fleet
  branches (55 deleted / 23 stripped) → `claude-config`'s own 17 branches (10 deleted / 7 stripped).

## Hard-won lessons (apply these)

- **The design doc is stale on sizing.** It says 7 consumer repos. Reality: **18 repos with
  vendored `.claude/commands/`, 13 of them public**. Re-derive the list; do not trust the doc's
  count or the memory note.
- **`~/Projects/new-game-project-idea` has `origin = constellation.git`** — a duplicate clone, not
  its own repo. Any fleet walk must dedupe by remote URL or it double-pushes.
- **Naive line deletion destroys data.** `~/Projects/DogHood/CLAUDE.md` lists *every* command on
  one line. Deleting lines matching a command name would have wiped 21 unrelated entries. A prune
  needs surgical excision plus a **refuse-if-unsure guard**: parse the other `` `/command` ``
  tokens on the line, excise only the target fragments, then assert every other token survived —
  and hard-fail rather than write if it can't excise cleanly.
- **zsh mangles git refspecs.** `$ref:commands/foo.md` and `$sha:refs/heads/$b` hit zsh parameter
  modifiers (`:c`, `:r`) even inside double quotes. Always brace: `"${sha}:refs/heads/${b}"`.
  Running the same script via `bash script.sh` also avoids it.
- **`git cat-file -e "$ref:path"` gave false negatives** (reported 0 of 19 branches; `git ls-tree`
  found 17). **Use `git ls-tree --name-only <ref> <dir>` for ref content checks.**
- **A GitHub API branch sweep silently rate-limited and returned a clean `0`.** Any `/reconcile`
  implementation must detect API errors and truncated trees explicitly, and must never report
  "clean" when calls failed. Two false cleans that session; both caught only by contradicting
  evidence, never by the check itself.
- **Deleting a file on `main` does nothing to branch tips cut earlier.** Any drift check must
  sweep every ref, not just the default branch — including `claude-config`'s own.
- **Hooks that will block you:** `~/.claude/hooks/block-rm-rf.sh` rejects `rm` outside `/tmp/`
  (use unique filenames instead of cleanup); the safety-net blocks `git checkout --` and
  `git reset --hard`. To rewrite a branch tip without a working tree, use plumbing:
  `GIT_INDEX_FILE=… git read-tree <ref>` → `git rm --cached` → `git write-tree` →
  `git commit-tree -p <ref>` → push. This preserves the old tip as parent (no force-push, no lost
  work).
- **Branch protection:** `constellation`, `home-base`, `stopwatch` require up-to-date branches +
  passing checks. Use `gh pr update-branch` and wait for checks. **Kyle's convention: do not use
  `gh pr merge --admin`.**
- **Any change to `commands/` requires the `adversarial-review` loop before merge** (per
  CLAUDE.md). The docs-only escape hatch does not apply. Budget for it.
- **Reference-doc sync rule:** adding `commands/reconcile.md` requires a row in
  `docs/command-skill-reference.md` **in the same commit**.

## Where the plan stands

**In progress:** nothing. This is a fresh start.

**Next concrete action:** re-derive the actual fleet (18 repos, deduped by remote URL) and put the
five open design questions in this file's "Decisions / open questions" section to Kyle before
writing code.

**Decisions pending Kyle — ask, do not assume.** The doc proposes v1 answers; the incident may
change them:
- `fleet.yml` granularity: per-item list vs coarse tiers. A *prune* needs per-item to know what
  should no longer be there — this may override the doc's "start coarse."
- Report vs act: doc says v1 reports only. The incident argues for a `--prune` that opens PRs.
- Whether `fleet.yml` lives in this now-**public** repo. The doc flagged "confirm no private repo
  paths leak" — with 5 private repos in the fleet, that is now a live problem.

**Known follow-ups this feature should cover:** ~95 *local* branches across 14 clones still carry
the deleted command files (75 with no live remote), so a plain `git push origin <branch>` would
republish them to a public repo. Separately, `.claude/skills/interview-prep/SKILL.md` is still
vendored and public in 18 repos while being deliberately gitignored here — the same prune gap,
unfixed.

**Open first:** `docs/ideas/fleet-manifest-reconcile.md`, `BACKLOG.md`,
`commands/claudify-repo.md` (the seam — its PORT mode copies with no delete/prune step).
````
