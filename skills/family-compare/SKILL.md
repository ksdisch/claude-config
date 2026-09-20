---
name: family-compare
description: Use when a handful of named steering items — skills, commands, subagents, plugin or vendored copies — seem to overlap, and the question is what each one actually is, when to reach for which, and what to do with each in a retirement sweep. The deep read on one named family, where /retire is the wide sweep. Triggers: "compare these skills / commands", "what's the difference between X, Y and Z", "which of these should I retire", "sort out the <name> family", "these overlap, settle it", "/family-compare". NOT for: sweeping the whole steering surface by temperature (/retire), relocating context bloat that stays (/trim-context), removing product features (/brainstorm subtract), picking a tool for one prompt (/prompt-optimize), grooming backlog items (backlog-hygiene). Recommends only — applies no verdict and edits no compared item.
---

# Family Compare

Kyle names a **family** of steering items that seem to overlap. This skill reads every one of them and every neighbor in full, gathers cheap evidence (size, routing flags, tracked status, twin copies, typed usage, prior arguments), and writes one committed reference doc that settles what each is, when to reach for which, how to run each well, where they genuinely overlap, and what to do with each in a retirement sweep. The doc's last section is a verdict table in `retire`'s ratification format, so it pastes in unchanged.

**This skill is LIGHT** — linear, main thread, read-only until Phase 4. Up to three read-only Explore agents, and only when the neighbor set is large.

**Two prime directives, because both fail under "you already know what these do" pressure:**

1. **Every claim cites a read from this session.** No overlap claim — and no claim of *no* overlap — on a file that was not read this run. A 157-byte shim gets read like a 4 KB engine: the shim is where the routing trap lives, and the flag on the shim decides whether prose can ever reach it.
2. **It recommends; it applies nothing.** Verdicts are input to `retire`'s ratification pass, not actions. No compared item is edited, no verdict executed, no vendored or untracked copy "fixed" to match what the doc found — that edit is unreviewable and lost on the next reinstall. Describe it in the doc; recommend it in the PR body.

## Where it sits

| Item | Job |
|---|---|
| `/retire` | Sweep the whole steering surface by temperature and flags; propose verdicts from counts |
| **`family-compare`** | **Deep-read one named family against its neighbors; produce the reference doc and the evidence a verdict needs** |
| `/trim-context` | Relocate bloat that stays |
| `/brainstorm subtract` | Remove product features, not steering items |
| `/prompt-optimize` | Pick a tool for one prompt; does not compare tools |
| `backlog-hygiene` | Groom backlog items, not tools |

Run this when a `/retire` sweep returns `ask` on a cluster, or when Kyle already knows a cluster is muddled and wants it settled before the sweep gets there.

## Invocation

```
/family-compare <item> <item>… [--vs <neighbor>…] [--exclude <item>…] [<prose>]
```

- **Items** — the leading bare names (`grilling grill-me grill-with-docs wayfinder`). Two or more required; one item is not a family, so say so and stop.
- **`--vs`** — neighbors to compare the family against. Absent → propose them at Gate 1.
- **`--exclude`** — comparisons Kyle rules out on purpose, reason optional in the prose. Exclusions print in the doc's header so a later reader knows the omission was deliberate.
- **Prose** after the flags — asserted facts and scope notes ("X is a shim over Y", "stop and ask if Z"). Confirmed cheaply in Phase 1 and listed at Gate 1 as *treated as verified*.

**In scope:** anything with a file and an invocation surface — skills, commands, subagents, plugin copies, vendored or gitignored loose copies. CLAUDE.md sections, MCP servers, hooks, and settings belong to `/retire`: name the item, point there, drop it from the run. **Record the dropped item and the reason in the doc's exclusions either way**, so the next sweep inherits it rather than losing it. Check whether `/retire` is actually installed before pointing at it — `skills/retire/SKILL.md` or `commands/retire.md` in the repo this session is running in, on the branch it is running on; a copy on another checkout's unmerged branch does not count. Absent, say so plainly rather than routing the operator to a command that is not there.

## Item resolution

Resolve each bare name, in order, against:

1. `skills/<name>/SKILL.md`, `commands/<name>.md`, `agents/<name>.md` in the current repo;
2. the same paths under the `~/.claude/skills` / `~/.claude/commands` / `~/.claude/agents` symlinks — which point at the main checkout when this session runs in a worktree, and are the only way to read a gitignored loose copy from one;
3. `~/.claude/plugins/cache/**/skills/**/<name>/SKILL.md` for plugin copies.

A `plugin:name` form targets the plugin copy directly. A name that resolves to more than one file is reported with every path — twins are a finding, not a nuisance — and the loose copy is the invocation target unless Kyle says otherwise. A name that resolves to nothing stops and asks.

**Reads are read-only everywhere.** In another checkout, run only the read-only git queries Phase 1 needs (`git ls-files`, `git check-ignore -v`, `git log`) — change no branch, stage nothing, write nothing.

## Phase 1 — Inventory (read-only)

Read every **item** in full now. Neighbors are read in full too, but only once Gate 1 settles which they are — that read happens between Gate 1 and Phase 3, and the same no-claim-without-a-read rule binds it. Then collect per item:

| Evidence | How |
|---|---|
| bytes | `wc -c` |
| frontmatter flags | `disable-model-invocation`, `allowed-tools`, `argument-hint`, pinned `model` / `effort` (agents); any sidecar beside the file (`agents/openai.yaml` and the like) that restates a flag |
| tracked status | `git ls-files` / `git check-ignore -v` in the item's own repo; the `.gitignore` line when ignored |
| index presence | row in `docs/command-skill-reference.md`, card in `docs/usage-playbook.md` — or **not eligible**, which is the honest answer for an item the index rule never covered (a vendored or gitignored copy), and a different fact from a missing row |
| twins | the other files the name resolved to; `diff` each pair; note the plugin version |
| roster visibility | whether the item appears in this session's own skill listing — the observable form of `disable-model-invocation` |
| typed usage | `~/.claude/history.jsonl`: count of `display` values that **begin** with `/<name>` **and** continue with end-of-string or a character outside `[A-Za-z0-9_-]` — i.e. `^/<name>([^A-Za-z0-9_-]|$)`. Both anchors matter and for opposite reasons: without the left one a prompt that merely mentions the command counts as an invocation, and without the right one `/<name>-coder` counts into `/<name>` — and comparing similarly-named siblings is this skill's whole purpose. Record first and last date, and **how many** distinct projects; the `/<plugin>:<name>` form counted separately |
| artifacts | files the item writes or expects on disk (a map, a spec dir, a report), and **how many** exist under `~/Projects` |
| referrers | other skills, commands, agents, or `CLAUDE.md` text that call or name it |
| prior arguments | files in `docs/ideas/`, `docs/adr/`, `docs/reports/` that mention it |

`disable-model-invocation: true` hides a skill from the model's roster: it fires only when Kyle types `/<name>`, no prose routes to it, and no other skill's instruction can reach it. Record that as a fact about reach, not as a size note.

Two channels can ship the same skill — a loose copy in `~/.claude/skills` firing as `/<name>`, a plugin copy firing as `/<plugin>:<name>` and appearing in the roster a second time when model-invocable. Byte-identical today does not mean identical after the next reinstall; say which it is and at what version you read it.

If `skills/retire/scripts/steering_inventory.py` is present **in the repo this session is running in** — a copy on another checkout's unmerged branch does not count, and is never run — prefer it for typed *and* session-chosen usage and cite its temperature. Otherwise the history grep stands and the doc states that usage counts are typed-only.

**Redaction — this doc gets committed to a public repo.** `~/.claude/history.jsonl` is machine state: its `project` values are absolute paths, and some of them name private work. The doc carries **counts, never names or paths**: "used in 5 projects", not a list; `~`-relative or repo-name-only for any path that reaches the page. This is `retire`'s standing rule for its own committed report, and it binds here for the same reason — `.gitignore` already untracks whole skills because this repo is public. Gather freely; publish counts.

Confirm each asserted fact from the prose at the cheapest possible cost — a `wc`, a `diff`, a `grep`. A confirmed fact is then used as given.

## Phase 2 — Steer (GATE 1, one round)

One `AskUserQuestion` round — or a plain stop when the choices are not bounded — showing:

1. **Resolved items**, with paths and any twins found.
2. **Proposed neighbors**, when `--vs` was absent: items in the same index category as the family, items the family's own files name, items whose descriptions share the family's job words. Kyle adds, removes, or confirms.
3. **Exclusions** — `--exclude` plus anything you noticed and are deliberately leaving out, each with a one-line reason.
4. **Facts treated as verified**, each with the cheap check that confirmed it.

**Stop-and-ask.** Evidence contradicting an asserted fact — the shim is not a shim, the "engine" calls something else, the flag is not set — stops the run here and reports the contradiction instead of writing around it. The doc is never written on a false premise.

"Just do it" compresses this round to a one-line echo of the defaults; it never deletes it. Neighbors and exclusions are the one input the repo cannot supply.

## Phase 3 — Analyze

Produce the five sections. Each rule below is a lesson from the hand-run this skill generalizes.

1. **What each one is.** One tight paragraph per item, written so Kyle can tell them apart six months on. Lead with the structural split — engine vs shim, thing vs alias, one-session vs many. State each item's bytes and routing visibility in the paragraph. A dependency that is the only thing separating two items gets its own paragraph, labeled as a dependency, and **no verdict row**.
2. **When to reach for which.** A table keyed on the situation Kyle is actually in, not on each item's self-description. Every row names the item to reach for *and* what it is the **wrong** tool for. Include one row for the unattended case: which of these can run with nobody answering.
3. **How to get the most out of each.** Per item: what a good invocation brings, what wastes it, model and effort from the Planner/Builder ladder in `CLAUDE.md`, all three rungs — judgment-first → Fable 5, well-specified build → Opus 5, mechanical and checklist-scoped → Sonnet 5, with effort picked independently of the model, and traps. Traps always cover routing (`disable-model-invocation`, roster twins, prose that pulls a different skill with a similar name), artifact-or-none (does the session leave anything behind), and human-in-the-loop-only (does it block on answers). Typed usage counts and dates go here, per item.
4. **Where they overlap.** One row per pair that actually overlaps, labeled **redundant** (one could stand in for the other with nothing lost), **different shape** (same purpose, different mechanism), **containment** (one invokes the other), or **sequential** (one's output is the other's input). Pairs with no overlap get one line or nothing. Engage any prior argument found in `docs/ideas/`: state what this comparison adds to it, where it holds, where it needs revising — do not restate it.
5. **Recommendation.** The `retire` ratification table, per the output contract below.

Qualitative throughout; no numeric overlap score. Every identifier that reaches Kyle carries a title on first mention, in the doc and in chat.

### Output contract

The doc's last section is exactly this table — its columns and verdict names track **`retire`'s implemented `skills/retire/SKILL.md`**, not its design spec, which the implementation has already moved past:

```
| # | Item | Surface | Evidence | Proposed | Question / why |
|---|---|---|---|---|---|
| 1 | `grilling` — design-tree interview engine | skill | 1,987 B · model-invocable · twin in plugin 1.2.3 (identical) · 0 typed, reached via shims · 18 referrers | keep | the only engine; retiring the loose copy needs proof the shims' bare-name call still resolves |
```

- **Item** — name in backticks plus a title. Never a bare id.
- **Surface** — `skill`, `command`, `agent`, or `plugin`; the surface-qualified ledger id is `<surface>:<name>`.
- **Evidence** — the Phase 1 fields that bear on the verdict, dot-separated, numbers included.
- **Proposed** — one of `retire`, `keep`, `merge-into <x>`, `relocate`, `pause`, `ask`. `pause` is the verdict when the deciding comparison was excluded from this run; `ask` when the evidence is mixed with nothing excluded.
- **Question / why** — one line. **Every `ask` row carries its own specific question here**, not a restatement of the uncertainty: `ask` is a placeholder for a question, and a row that arrives at ratification without one cannot be answered.

Kyle rules by row number, in `retire`'s reply grammar, when the table reaches a ratification pass. A `merge-into` verdict earns a backlog stub there; the merge itself is a later PR.

## Phase 4 — Write

Write `docs/family-compare/<slug>.md` from `references/doc-template.md`, where `<slug>` is the family's kebab name (`grill-family-and-wayfinder`). The header carries the date; the plugin or upstream version each item was read at; where the files live and, when they are untracked or vendored, why the doc describes rather than edits them; and the exclusions with reasons.

No summary section. No section that repeats a table above it. The verdict table is the end. Length follows substance.

## Phase 5 — Land (GATE 2 — the review proposal)

Standing git workflow from `CLAUDE.md`: branch `docs/family-compare-<slug>` from `main`, run `python3 scripts/check-doc-sync.py` when in claude-config, commit, push, open the PR.

PR body: what the doc covers; the verdict table verbatim; the interpretation calls this run made; recommendations for files deliberately left untouched (`.gitignore`, `THIRD-PARTY.md`, the index docs) when a verdict would eventually require an edit there; what was verified and how; what was not verified and why.

Then propose a review scope with the Preflight evidence and **stop**. This skill never merges, never applies a verdict, and never edits an item under comparison.

Hand off from there: the verdict table feeds `/retire <item>…` in targeted mode, or the next `/retire` sweep, which reads it as evidence.

## Red flags — each observed or narrowly avoided in the run this generalizes

| Drift / rationalization | Reality |
|---|---|
| "I know what that skill does" | Read the file this session. Every overlap claim cites a read. |
| "The shim is 157 bytes, skip it" | Shims are where the routing trap lives; the flag on the shim decides whether prose can ever reach it. |
| Treating an asserted fact as verified | Confirm it at the cheapest cost. A contradiction stops the run at Gate 1. |
| "Merge-into is obviously right, apply it" | Verdicts are recommendations. Nothing is applied; `retire` ratifies. |
| Editing a vendored or untracked copy to fix what the doc found | Unreviewable and lost on reinstall. Describe it; recommend it in the PR body. |
| A summary section at the end | The verdict table is the end. Nothing repeats a table above it. |
| A numeric overlap score | Qualitative labels with evidence, per the house rule. |
| `F2`-style ids in chat | Gloss on first mention; title column in every table. |
| Going past the review proposal | Gate 2 is a stop. Kyle's call is final for that merge. |
