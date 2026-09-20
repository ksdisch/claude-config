# family-compare — design spec

**Date:** 2026-09-18
**Status:** approved design, pre-implementation (brainstorm interview 2026-09-18; approach and design approved by Kyle)
**Deliverable:** one new skill at `skills/family-compare/SKILL.md` (user-invocable as `/family-compare`, model-invocable on its trigger phrases) with `skills/family-compare/references/doc-template.md`; the same-commit row in `docs/command-skill-reference.md` (Global Skills → Quality & Debugging) and card in `docs/usage-playbook.md`. No change to any item it compares, to `retire`, or to the vendored mattpocock skills.
**Lineage:** the 2026-09-18 grill-family run (PR #133, `docs/grill-family-and-wayfinder.md`). A hand-written prompt read four vendored skills and six thinking-and-planning neighbors and produced a reference doc ending in a paste-ready keep / retire table. This skill is that prompt, generalized, with the run's lessons encoded as rules and red flags.

## Purpose

Kyle names a **family** of steering items that seem to overlap (skills, commands, subagents, including plugin or vendored copies). The skill reads every one of them and every neighbor in full, gathers cheap evidence (size, routing flags, tracked status, twin copies, typed usage, prior arguments), and writes one committed reference doc that settles what each is, when to reach for which, how to run each well, where they genuinely overlap, and what to do with each in a retirement sweep. The doc's last section is a verdict table in `retire`'s ratification format so it pastes in unchanged.

It is the **deep read on a handful of items**. `/retire` is the wide, temperature-driven sweep over the whole steering surface; it proposes verdicts from counts and flags and cannot tell a shim from an engine. `family-compare` is what runs when the sweep says `ask`, or when Kyle already knows a cluster is muddled and wants it settled before the sweep gets there.

Success criterion: pointed at the four grill-family skills plus the six neighbors, it reproduces `docs/grill-family-and-wayfinder.md` in substance (same section shape, same verdicts, same evidence classes) without the hand-written prompt, and stops at the review proposal.

## Grounding facts (verified 2026-09-18)

- **`retire`'s output contract** (design spec on `feat/retire-skill`, §5.4, §5.5, §14): verdicts `retire | keep | merge-into <x> | relocate | pause | ask`; ratification columns `# | Item | Surface | Evidence | Proposed | Why`; ledger ids are surface-qualified (`skill:mock-call`, `claude-md:Improvement Mode`). Kyle answers by row number. `merge-into` writes a backlog stub only; the merge itself is a follow-up PR. `retire` is in flight on PR #132 and is not edited by this work; if its landed form changes a column or a verdict name, this skill's template follows it (one edit to `references/doc-template.md`).
- **`disable-model-invocation: true` hides a skill from the model's roster.** Observed in the grill run: `grill-me`, `grill-with-docs`, and `wayfinder` were absent from the session's skill list in both the loose and plugin namespaces; `grilling` was present. Such a skill fires only when Kyle types `/<name>`; no prose routes to it and no other skill's instruction can reach it.
- **Two channels can ship the same skill.** `~/.claude/skills` symlinks to the main checkout's `skills/`; a loose copy there fires as `/<name>`. An enabled plugin's copy fires as `/<plugin>:<name>` and, if model-invocable, appears in the roster a second time. The grill run found all four loose copies byte-identical to `mattpocock-skills` 1.2.3; identical today does not mean identical after the next reinstall.
- **Typed usage is countable; auto-routed usage is not.** `~/.claude/history.jsonl` records each typed prompt with `display`, `timestamp` (ms), and `project`, so `/name` invocations can be counted, dated, and grouped by project. Session-chosen (auto-routed) invocations are not there; `retire`'s inventory script reads transcripts for those. This skill reports typed counts and says so.
- **The pre-push gate** in claude-config is `scripts/check-doc-sync.py`. A new file under `docs/` that is not an index row does not trip it; the skill's own row and card do, so they land in the same commit as the skill.
- **A worktree may not hold the items.** Gitignored loose copies exist only where they were installed (the main checkout). Reading them from a worktree means following the `~/.claude/skills` symlink to the main checkout, read-only, never running git there.

## Decisions (from the interview)

1. **Skill, not command.** Fires on `/family-compare` and on prose; carries a `references/` sidecar for the doc template.
2. **Neighbors: propose, then confirm.** When Kyle names no neighbors, the skill proposes candidates and shows them with its exclusions in the steering round; it never guesses silently.
3. **Name: `family-compare`.**
4. **Linear, main-thread process.** No fan-out by default; up to three read-only Explore agents only when the neighbor set is large. Fan-out is a possible later escalation flag, not built now.
5. **Docs go to `docs/family-compare/<slug>.md`.** The grill doc stays at `docs/grill-family-and-wayfinder.md` until PR #133 lands; moving it is a follow-up.
6. **Output aligned to `retire`.** Columns and vocabulary from `retire`'s ratification table; surface-qualified ids.
7. **Items in scope:** anything with a file and an invocation surface: skills, commands, subagents, plugin copies, vendored or gitignored loose copies. CLAUDE.md sections, MCP servers, hooks, and settings are `retire`'s job and are refused with a pointer.

## Skill design

### Invocation

```
/family-compare <item> <item>… [--vs <neighbor>…] [--exclude <item>…] [<prose>]
```

- **Items** are the leading bare names: `grilling grill-me grill-with-docs wayfinder`. Two or more required; one item is not a family (say so and stop).
- **`--vs`** names neighbors to compare the family against. Absent → the skill proposes them (Phase 2).
- **`--exclude`** names comparisons Kyle rules out on purpose, with an optional reason in the prose. Exclusions are printed in the doc's header so a later reader knows the omission was deliberate.
- **Prose** after the flags is read as asserted facts and scope notes, the way the grill prompt supplied "facts already verified" and "stop-and-ask" conditions. Asserted facts are confirmed cheaply in Phase 1 and listed in the steering round as "treated as verified".

Trigger phrases for the description: "compare these skills / commands", "which of these should I retire", "what's the difference between X, Y and Z", "sort out the <name> family", "these overlap, settle it", "/family-compare". NOT for: a sweep over the whole surface (`/retire`), relocating bloat (`/trim-context`), removing product features (`/brainstorm subtract`), choosing a tool for one prompt (`/prompt-optimize`), grooming backlog items (`backlog-hygiene`).

### Item resolution

A bare name resolves, in order, against: `skills/<name>/SKILL.md`, `commands/<name>.md`, `agents/<name>.md` in the current repo; the same paths under the `~/.claude/skills` / `~/.claude/commands` / `~/.claude/agents` symlink targets (which may be the main checkout when the session is in a worktree); and `~/.claude/plugins/cache/**/skills/**/<name>/SKILL.md` for plugin copies. A `plugin:name` form targets the plugin copy directly. A name that resolves to more than one file is reported with every path (they are all evidence: twins are a finding) and the loose copy is treated as the invocation target unless Kyle says otherwise. A name that resolves to nothing stops and asks.

Reads are read-only everywhere. In another checkout the skill runs only the read-only git queries Phase 1's evidence table needs (`git ls-files`, `git check-ignore -v`, `git log`) — it changes no branch, stages nothing, writes nothing. *(Corrected 2026-09-19, review finding F5: as first written this line forbade the git commands the Phase 1 table below requires, since an item resolved through the `~/.claude` symlink is always in another checkout. `skills/family-compare/SKILL.md` is the operative statement of this rule.)*

### Phase 1 — Inventory (read-only)

Read every item and every neighbor **in full**. No overlap claim, and no claim of *no* overlap, is allowed on a file that was not read this session. Per item, collect:

| Evidence | How |
|---|---|
| bytes | `wc -c` |
| frontmatter flags | `disable-model-invocation`, `allowed-tools`, `argument-hint`, pinned `model` / `effort` (agents) |
| tracked status | `git ls-files` / `git check-ignore -v` in the item's own repo; the `.gitignore` line when ignored |
| index presence | row in `docs/command-skill-reference.md`, card in `docs/usage-playbook.md` |
| twins | other files the name resolved to; `diff` each pair; note the plugin version |
| roster visibility | whether the item appears in this session's own skill listing (the observable form of `disable-model-invocation`) |
| typed usage | `~/.claude/history.jsonl`: count of `display` values starting with `/<name>`, first and last date, distinct projects; the `/<plugin>:<name>` form counted separately |
| artifacts | files the item writes or expects on disk (a map, a spec dir, a report), and whether any exist under `~/Projects` |
| referrers | other skills, commands, agents, or `CLAUDE.md` text that call or name it |
| prior arguments | `docs/ideas/`, `docs/adr/`, `docs/reports/` files that mention it |

If `retire`'s inventory script is present at `skills/retire/scripts/steering_inventory.py`, prefer it for typed and session-chosen usage and cite its temperature; otherwise the history grep stands and the doc says usage is typed-only.

Asserted facts from the prose are confirmed here at the cheapest possible cost (a `wc`, a `diff`, a `grep`). A confirmed fact is used as given. A fact the evidence contradicts triggers the stop-and-ask rule below.

### Phase 2 — Steer (GATE 1, one round)

One `AskUserQuestion` round, or a plain stop when the choices are not bounded, showing:

1. **Resolved items** with paths, and any twins found.
2. **Proposed neighbors** when `--vs` was absent: items in the same index category as the family, items the family's files themselves name, and items whose descriptions share the family's job words. Kyle adds, removes, or confirms.
3. **Exclusions**, from `--exclude` plus anything the skill noticed and is deliberately leaving out, each with a one-line reason.
4. **Facts treated as verified**, from the prose, each with the cheap check that confirmed it.

**Stop-and-ask rule.** If an item's actual behavior contradicts an asserted fact (the shim is not a shim; the "engine" calls something else; the flag is not set), the skill stops here and reports the contradiction rather than writing around it. The doc is not written on a false premise.

"Just do it" compresses this round to a one-line echo of the defaults; it never deletes it. Neighbors and exclusions are the one input the repo cannot supply.

### Phase 3 — Analyze

Produce the five sections. Rules, each one a lesson from the grill run:

1. **What each one is.** One tight paragraph per item, written so Kyle can tell them apart six months on. Lead with the structural split (engine vs shim, thing vs alias, one-session vs many). A dependency that is the only thing separating two items gets its own paragraph, labeled as a dependency, and **no verdict row**. State each item's bytes and routing visibility in the paragraph.
2. **When to reach for which.** A table keyed on the situation Kyle is actually in, not on each item's self-description. Every row names the item to reach for and what it is the **wrong** tool for. Include one row for the unattended case (which of these can run with nobody answering).
3. **How to get the most out of each.** Per item: what a good invocation brings; what wastes it; model and effort from the Planner/Builder ladder in `CLAUDE.md` (judgment-first → Fable, xhigh; mechanical → Sonnet); traps. Traps always cover: routing (`disable-model-invocation`, roster twins, prose that pulls a different skill with a similar name), artifact-or-none (does the session leave anything behind), and human-in-the-loop-only (does it block on answers). Typed usage counts and dates go here, per item.
4. **Where they overlap.** One row per pair that actually overlaps, labeled **redundant** (one could stand in for the other with nothing lost), **different shape** (same purpose, different mechanism), **containment** (one invokes the other), or **sequential** (one's output is the other's input). Pairs with no overlap get one line or nothing. Any prior argument in `docs/ideas/` is engaged: state what the comparison adds to it, where it holds, where it needs revising. Do not restate it.
5. **Recommendation.** The `retire` ratification table (Output contract, below). Verdicts are recommendations; nothing is applied.

Qualitative throughout; no numeric overlap score. Every identifier that reaches Kyle carries a title on first mention, in the doc and in chat.

### Phase 4 — Write

Write `docs/family-compare/<slug>.md` from `references/doc-template.md`, where `<slug>` is the family's kebab name (`grill-family-and-wayfinder`). The header carries: the date; the plugin or upstream version each item was read at; where the files live and, when they are untracked or vendored, why the doc describes rather than edits them; the exclusions with reasons. No summary section; no section that repeats a table above it. Length follows substance.

### Phase 5 — Land (GATE 2: the review proposal)

Standing git workflow from `CLAUDE.md`: branch `docs/family-compare-<slug>` from `main`, run `python3 scripts/check-doc-sync.py` when in claude-config, commit, push, open the PR. PR body: what the doc covers; the verdict table verbatim; interpretation calls the skill made; recommendations for files it deliberately did not touch (`.gitignore`, `THIRD-PARTY.md`, the index docs) when a verdict would eventually require an edit there; what was verified and how; what was not verified and why. Then propose a review scope with the Preflight evidence and **stop**. The skill never merges, never applies a verdict, never edits an item under comparison.

Handoffs: the verdict table → `/retire <item>…` targeted mode, or the next `/retire` sweep, which reads it as evidence. A `merge-into` verdict → a follow-up PR, per `retire`'s rule. A doc-location move for an earlier flat doc → a follow-up.

### Output contract

The doc's last section is exactly:

```
| # | Item | Surface | Evidence | Proposed | Why |
|---|---|---|---|---|---|
| 1 | `grilling` — design-tree interview engine | skill | 1,987 B · model-invocable · twin in plugin 1.2.3 (identical) · 0 typed, reached via shims · 2 referrers | keep | the only engine; retiring the loose copy needs proof the shims' bare-name call still resolves |
```

- **Item**: name in backticks plus a title; never a bare id.
- **Surface**: `skill`, `command`, `agent`, or `plugin`; the surface-qualified ledger id is `<surface>:<name>`.
- **Evidence**: the Phase 1 fields that bear on the verdict, dot-separated, numbers included.
- **Proposed**: one of `retire`, `keep`, `merge-into <x>`, `relocate`, `pause`, `ask`. `pause` is the verdict when the deciding comparison was excluded from this run; `ask` when the evidence is mixed with nothing excluded.
- **Why**: one line.

Kyle rules by row number, in `retire`'s reply grammar, when the table reaches a ratification pass.

### Where it sits

| Item | Job |
|---|---|
| `/retire` | Sweep the whole steering surface by temperature and flags; propose verdicts from counts |
| **`family-compare`** | **Deep-read one named family against its neighbors; produce the reference doc and the evidence a verdict needs** |
| `/trim-context` | Relocate bloat that stays |
| `/brainstorm subtract` | Remove product features, not steering items |
| `/prompt-optimize` | Pick a tool for one prompt; does not compare tools |
| `backlog-hygiene` | Groom backlog items, not tools |

### Red flags — each observed or narrowly avoided in the grill run

| Drift / rationalization | Reality |
|---|---|
| "I know what that skill does" | Read the file this session. Every overlap claim cites a read. |
| "The shim is 157 bytes, skip it" | Shims are where the routing trap lives; the flag on the shim decides whether prose can ever reach it. |
| Treating an asserted fact as verified | Confirm it at the cheapest cost. A contradiction stops the run. |
| "Merge-into is obviously right, apply it" | Verdicts are recommendations. Nothing is applied; `retire` ratifies. |
| Editing a vendored or untracked copy to fix what the doc found | Unreviewable and lost on reinstall. Describe; recommend in the PR body. |
| A summary section at the end | The verdict table is the end. Nothing repeats a table above it. |
| A numeric overlap score | Qualitative labels with evidence, per the house rule. |
| `F2`-style ids in chat | Gloss on first mention; title column in every table. |
| Going past the review proposal | Gate 2 is a stop. Kyle's call is final for that merge. |

## Files

- `skills/family-compare/SKILL.md` — the skill.
- `skills/family-compare/references/doc-template.md` — the five-section doc skeleton with the header block and the ratification table.
- `docs/command-skill-reference.md` — one row under Global Skills → Quality & Debugging.
- `docs/usage-playbook.md` — one card: Fable 5 · `xhigh` · sync; pairs with `retire`, `trim-context`, `prompt-optimize`.
- `docs/superpowers/specs/2026-09-18-family-compare-design.md` — this spec.

## Non-goals

- Executing any verdict, editing any compared item, or touching `retire`.
- Comparing CLAUDE.md sections, MCP servers, hooks, or settings (refuse with a pointer to `/retire`).
- Project-specific items in other repos are in scope only when the session runs in that repo.
- A fan-out mode. If a family ever exceeds ~8 items, split it into two runs or add the flag then.

## Run-config note

Build: Opus 5 · `high` — the spec is complete; the build is one SKILL.md, one template, one row, one card, all mechanical against this document. Launch: `claude --model claude-opus-5 --effort high`. Per the Planner/Builder Protocol's "split only when build ≫ plan" clause, this build is light enough to finish in the planning session instead; Kyle's call.

Run: Fable 5 · `xhigh` · sync — the analysis is a chain of design calls with real tradeoffs, and Gate 1 blocks on Kyle. Launch: `claude --model claude-fable-5-1 --effort xhigh`.
