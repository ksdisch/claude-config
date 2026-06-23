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
