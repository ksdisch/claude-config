# CONVENTIONS.md: the command frontmatter contract + a copy-paste stub

**Status:** Idea — not committed. Added by `/brainstorm` (`quickwin` mode) on 2026-06-23.
**Lens:** force-multiplier · **Fit:** stretch · **Size:** M

## Premise

When an interface is defined by hand-written prose that nothing can lint or test
(A3), the cheapest correctness mechanism is a written contract plus a copy-paste
template: it moves "is the shape right?" from invoke-time discovery to author-time
defaults, for the cost of one short doc.

## The bet

Targets **A3** (specs are hand-written markdown prose; no tests/CI; correctness only
shows at runtime). A veteran would nod: when you can't lint a prose-defined interface,
you write the contract down and hand over a known-good template, so the shape is right
at author-time instead of caught at invoke-time. It is the lightest possible "schema"
for a system that can't run one — documentation as the validator.

**Why now:** Command frontmatter is provably non-uniform — 3 commands (`begin`, `wrap`,
`handoff`) omit `argument-hint` (correctly — they take no `$ARGUMENTS`), and `allowed-tools`
was just backfilled onto the other 15. With the contract now *de facto* complete, writing
it down while the shape is fresh (two clean exemplars: `smoke-test.md`, `boot_server.md`)
is far cheaper than reconstructing it from 30+ files later.

## Credible first step

Create `CONVENTIONS.md` at the repo root (frontmatter contract + copy-paste stub + the
omit-rules), and add a one-line link to it from `README.md`. Document the three fields
(`description` → `argument-hint` → `allowed-tools`, in that order) and exactly when each is
optional. Crucially: do **not** fabricate argument-hints for `begin`/`wrap`/`handoff` — they
read session context, not a positional arg; they are the canonical "omit argument-hint when
the command takes no argument" example. Point the exemplars at `commands/smoke-test.md` and
`commands/boot_server.md`.

## Decisions / open questions

- **Standalone `CONVENTIONS.md` vs. a `## Authoring` section in README:** recommend standalone
  — it vendors cleanly via `/claudify-repo` as a unit and keeps README focused on what-the-repo-is.
- **`allowed-tools` rule:** state it (omit = inherit all tools / may prompt; specify = pre-approve
  the listed tools — it does NOT hard-block) but do not re-litigate the 15-command backfill here.
- **Skills frontmatter:** out of scope for the win — command frontmatter is the provably-non-uniform
  surface; mention `skills/<name>/SKILL.md` as a one-line "see examples" pointer at most.
- **`install.sh` interaction:** `CONVENTIONS.md` is a top-level doc that must NOT be symlinked into
  `~/.claude` — when created, add it to the `DENY` list in `install.sh` (alongside `README.md`,
  `BACKLOG.md`, `docs`).

## Dependencies

- None. No new tooling, no `settings.json`/hook changes, no `install.sh` logic change beyond adding
  the filename to `DENY`. Pure markdown additions that take effect on commit.

## Explicitly out of scope (revisit later)

- Any lint script / git hook / CI that *enforces* the convention — that is the A3-automation moonshot
  (`/retro`, `/forge`), not this QuickWin; keep it prose.
- A `skills/SKILL.md` authoring contract.
- Re-doing or re-scoping the `allowed-tools` backfill (already shipped).

## Identity/positioning note

Tethered — none. It documents existing house style; it doesn't change what the repo is.
