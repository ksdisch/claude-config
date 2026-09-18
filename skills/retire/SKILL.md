---
name: retire
description: The config's subtract verb. Inventories every global steering surface with usage evidence, proposes a verdict per item, applies only what Kyle ratifies row by row, and measures before → after weight. Forms: `/retire` (sweep), `--report` (read-only), `--surface <name>` (one lane), `/retire <item>…` (targeted). Use when Kyle types /retire or says "retire", "cleanse my config", "declutter claude code", "what can I get rid of", "prune my skills", "what's steering my sessions". NOT for relocating content that stays (/trim-context) or pruning vendored copies in other repos (reported, never edited).
---

# Retire

**The subtract verb.** The config only grows. Everything was added for a reason and nothing has a
removal path, so old intent keeps steering new sessions and every request pays for the bytes.
Retire inventories the whole steering surface with evidence, proposes verdicts, and removes only
what Kyle ratifies — completely, reversibly, with the bookkeeping done.

Inventory script: `scripts/steering_inventory.py` (read-only, stdlib, deterministic).
Apply checklists: `references/bookkeeping.md`. Ledger: `docs/retired.md`.
Design record: `docs/superpowers/specs/2026-09-17-retire-skill-design.md`.

## Prime directives

1. **Ratify before remove.** Nothing is removed for an unratified row. Silence is not consent —
   unanswered rows stay unapplied. Unattended: write the table to the report and stop.
2. **Never `rm -rf`.** Tracked: `git rm`. Untracked: back up to a dated folder, then `mv`.
3. **The script is an Instrument, never a Gate.** It informs the ruling; it never decides. It
   exits non-zero rather than report a zero it did not measure. A failed run stops the skill —
   never proceed on partial evidence.
4. **Never touch a project repo.** Vendored copies are reported in the ledger and PR body, never
   edited.
5. **Untracked settings change only after a per-file confirmation** showing the exact edit list,
   with the file backed up first. Git cannot undo those.
6. **Branch and PR, review scope proposed.** Diffs under `skills/`, `commands/`, `agents/`,
   `CLAUDE.md`, hooks or `settings*.json` are behavioral: propose at least a single round and,
   interactively, stop for Kyle's call.

## Modes

| Form | Behavior |
|---|---|
| `/retire` | Sweep: Steps 0–6. |
| `/retire --report` | Steps 0–2, commit the dated report, stop. No edits. |
| `/retire --surface <name>` | Filter to one surface. Valid on both sweep and report. |
| `/retire <item>…` | Targeted: Step 0, an evidence card per named item, confirm, then Steps 4–6 for those items only. |

Surface names: `skill` `command` `agent` `output-style` `plugin` `mcp` `hook` `memory` `claude-md`.

Targeted names resolve across surfaces — bare (`<name>`), or surface-qualified
(`skill:<name>`, `plugin:<key>`, `claude-md:<heading>`). **An ambiguous bare
name stops and asks.** A ledger row pastes straight in, since ledger ids are surface-qualified.

## Procedure

### Step 0 — Preflight

Confirm a clean tree in the config repo; branch `chore/retire-<date>` from `main`. Never work on
`main`, never stash or reset Kyle's work. Then:

```bash
python3 skills/retire/scripts/steering_inventory.py --json "$SCRATCH/before.json" --md "$SCRATCH/before.md"
```

Exit 2 (source missing or unreadable) or 3 (a surface enumerated to zero where files exist) →
report the stderr line verbatim and **stop**.

### Step 1 — Inventory

Read `$SCRATCH/before.md`. Keep its Totals table; it is the "before" column of Step 5.

### Step 2 — Render the proposals

**The script already computed `proposed` for every item** from the precedence table, so it is
under test and consistent between sweeps. Do not recompute it, and do not argue with it — render
it. Verdict vocabulary: `retire` · `keep` (optional clause) · `pause` · `merge-into <id>` ·
`relocate` · `ask`.

On `--report`: write the script's markdown plus this table to
`docs/reports/<date>-steering-inventory.md`, commit on the branch, and stop.

### Step 3 — Ratification (STOP)

One table. Every row **numbered and titled** — never a bare id. Grouped by surface with
`claude-md` **last**, so the highest-judgment rows come when the rest is settled. Within a group:
`retire` first, then `ask`, then `relocate`. The header carries the caveat that usage evidence is
local to this machine and is therefore a floor.

**Every `ask` row carries its own specific question in the table.** This is the difference between
a table Kyle can answer and a list of forty-eight deferrals — `ask` is not a question, it is a
placeholder for one. Where many rows ask the same question (a batch of connectors gone quiet, a
run of oversized descriptions), say so once above the group and let one answer carry the batch.
Give a UUID-named item a human title from its evidence; a row Kyle cannot read is a row he cannot rule.

```
| # | Item | Surface | Evidence | Proposed | Question / why |
|---|---|---|---|---|---|
| 1 | <section title> — what it is | claude-md | 0 trigger hits ever · 1 referrer · 1.1k chars | retire | never fired in 5,449 prompts |
| 2 | <skill name> — what it does | skill | typed 0/90d · 3 all · last 2026-07-02 · 0 refs | ask | cold but recent. Keep for the season it serves, or retire? |
```

After the table, summarize what was omitted and why, by count and name: kept rulings, `new`
items with no other flag, silent `hot`/`warm` keeps (count only), recently paused items, and
anything unmeasured. List the `auto_only` names — a skill the model reaches for that Kyle never
types is worth knowing about even though it changes no proposal.

Then say:

> Answer by row: `1 retire, 2 keep — still earns it, 7 pause, 12 merge-into skill:<target>, rest as proposed`.
> Also available: `keep (hook)` to mark a rule hook-convertible, and "ask me about row N" for a fuller card.
> Unanswered rows are not applied.

**STOP and wait.** `rest as proposed` applies the proposed verdict to every row not named; it
never applies to an `ask` row, because `ask` has no verdict to fall back on.

### Step 4 — Apply

Per ratified row, run that surface's checklist in `references/bookkeeping.md` **in order**,
verifying each step before the next. A step that cannot complete cleanly stops **that item** and
is reported — never a partial removal.

- `keep` with a clause → the ledger's **Kept on purpose** table. The script reads it back, so the
  item is never re-proposed.
- `pause` → rename to `.disabled` (commands, skills) or `claude plugin disable` (plugins). **No
  ledger line.** The index row and card stay, prefixed `(paused <date>)` with a bold **Paused**
  note and the restore instruction. No pause exists for CLAUDE.md sections, MCP servers or hooks.
- `merge-into <id>` → **write a backlog stub naming source and target and remove nothing.** The
  merge PR lands both halves and writes the ledger line "merged into `<id>`". Until then the
  item stays on the surface.
- `relocate` → list under "Hand to /trim-context" in the PR body. Make no edit.
- `keep (hook)` → keep the rule, write a backlog stub to convert it to a hook later.

Untracked settings files get **one confirmation per file per pass**, showing the exact edit list,
after the rows are ratified — not a stop per entry. Back the file up with a dated suffix first.
Use the CLI verbs where they exist: `claude plugin uninstall` (retire) / `claude plugin disable`
(pause) / `claude mcp remove`. Hand-edit JSON only for hook entries and the connector deny list.

**Mentions** — tracked docs that merely name a retired item, as opposed to referrers that route to
it — are edited in the same PR with judgment, and listed under their own PR heading so each edit is
reviewable in the diff.

### Step 5 — Measure

Re-run the inventory to `$SCRATCH/after.json`. **Assert every retired item is absent from every
surface it was on** — verification is a measurement, not a claim. Then:

```bash
python3 skills/retire/scripts/steering_inventory.py --compare "$SCRATCH/before.json" "$SCRATCH/after.json"
```

That prints the per-surface before/after table with deltas for the PR body. If Kyle pastes
`/context` output from fresh sessions before and after, include it as the wire-level check — never
try to produce it yourself.

### Step 6 — Ship

`python3 scripts/check-doc-sync.py` must pass. Commit per surface
(`chore(retire): remove <item> — <why>`), push, and open the PR carrying: the ratification table
as ruled, the before → after table, the ledger diff, "Hand to /trim-context", doc-mention edits
under their own heading, and "Downstream copies (report only)" naming each retired item's vendored
repos. Then propose the review scope and, interactively, **stop** for Kyle's call. Brief him at the
point of action: what changed, commit SHAs, PR link.

## Failure table

| Situation | Do |
|---|---|
| Inventory exits 2 or 3 | Report the stderr line; stop. Never estimate a count. |
| Dirty tree at preflight | Stop and say what is dirty. Never stash. |
| Ambiguous name in targeted mode | List the matches; ask. Never guess. |
| A referrer line cannot be excised cleanly | Leave it; list under "Needs a hand" in the PR. |
| Doc-sync fails after a row/card deletion | Stop that item and report; the reference docs must never describe a file that is gone. |
| Bare `/x` stops resolving after a loose plugin copy is retired | Not a blocker — record the namespaced spelling in the playbook card that mentioned it. |
| A settings edit is refused at the confirmation | Skip that file's entries; report them as unapplied. The row stays ratified for next pass. |

## Handoffs

| Situation | Hand to |
|---|---|
| `relocate` verdict | `/trim-context` — by name, with no edit made here |
| `merge-into` verdict | a backlog stub; the merge PR removes the item |
| a kept rule marked hook-convertible | a backlog stub; converting is its own change |
| retired item has vendored copies | the ledger line and the PR body; a future fleet prune |
