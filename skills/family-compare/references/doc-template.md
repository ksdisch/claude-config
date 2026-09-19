# Doc template — `docs/family-compare/<slug>.md`

The skeleton Phase 4 fills. Section order is fixed; section *length* follows substance. Delete no heading; add none. There is no summary section — the ratification table is the end of the document.

---

```markdown
# <Family name> — what each one is, and what to do with them

**Date:** <YYYY-MM-DD>
**Family:** `<item>`, `<item>`, … · **Neighbors:** `<neighbor>`, …
**Read at:** <per item: path — `~`-relative or repo-name-only, never an absolute home path — and the
plugin or upstream version when the copy is vendored>
**Where the files live:** <loose copy / plugin copy / in-repo path per item, same path rule; for
untracked or vendored items, one line on why this doc describes them rather than edits them>
**Excluded from this run:** <item — reason> · <item — reason>  *(omit the line only when nothing was excluded)*
**Usage counts below are typed-only** unless a line says otherwise. <Drop this line when
`steering_inventory.py` supplied session-chosen counts; cite its temperature instead.>

## What each one is

<One tight paragraph per item — enough to tell them apart six months on. Lead with the
structural split: engine vs shim, thing vs alias, one-session vs many. State bytes and routing
visibility in the paragraph. A dependency that is the only thing separating two items gets its
own paragraph, labeled as a dependency, and no row in the ratification table.>

## When to reach for which

| Situation you're actually in | Reach for | Wrong tool for this |
|---|---|---|
| <the situation, not the item's self-description> | `<item>` | <what it would be the wrong pick for> |
| Nobody is around to answer | `<item>` | <the items that block on a human> |

## How to get the most out of each

### `<item>`

- **A good invocation brings:** <what the caller supplies that makes the run worth it>
- **What wastes it:** <the shape of run that gets little back>
- **Run config:** <Model · effort, from the Planner/Builder ladder in CLAUDE.md> — <one-clause why>
- **Typed usage:** <n invocations · first–last date · used in <n> projects — a count, never the names>
- **Traps:** routing (<`disable-model-invocation`, roster twins, a similarly-named skill prose
  pulls instead>) · artifact-or-none (<what the session leaves behind, or nothing>) ·
  human-in-the-loop (<where it blocks on an answer>)

## Where they overlap

| Pair | Label | What the overlap actually is |
|---|---|---|
| `<a>` ↔ `<b>` | redundant \| different shape \| containment \| sequential | <the evidence, qualitative — no score> |

<Pairs with no overlap get one line each, or nothing. Where `docs/ideas/` or an ADR already
argued about one of these pairs, engage it here: what this comparison adds, where it holds,
where it needs revising. Do not restate it.>

## Recommendation

| # | Item | Surface | Evidence | Proposed | Question / why |
|---|---|---|---|---|---|
| 1 | `<name>` — <title> | skill \| command \| agent \| plugin | <bytes · routing · twins · usage · referrers> | keep \| retire \| merge-into `<x>` \| relocate \| pause \| ask | <one line; an `ask` row carries its own specific question> |

Verdicts are recommendations for a `/retire` ratification pass, not actions. Kyle rules by row
number in `retire`'s reply grammar.
```

---

## Field rules

- **Item** — name in backticks plus a title, every time. Never a bare id.
- **Surface** — `skill`, `command`, `agent`, or `plugin`. The surface-qualified ledger id is `<surface>:<name>`.
- **Evidence** — the Phase 1 fields that bear on *this* verdict, dot-separated, numbers included. Not the whole inventory.
- **Redaction** — this doc is committed to a public repo. Project usage is a **count**, never a list of names; every path is `~`-relative or repo-name-only. `~/.claude/history.jsonl` is machine state and its `project` values are absolute paths, some of them naming private work. Same rule `retire` applies to its own committed report.
- **Proposed** — `pause` when the deciding comparison was excluded from this run; `ask` when the evidence is mixed with nothing excluded.
- **Question / why** — one line. An `ask` row carries its own specific question, not a restatement of the uncertainty: `ask` is a placeholder for a question, and a row without one cannot be answered at ratification.

## If `retire` changes

These columns and verdict names track **`retire`'s implemented `skills/retire/SKILL.md`** — its ratification table and the rule that every `ask` row carries a question. Track the implementation, not the design spec: on `feat/retire-skill` the two already disagree (the spec's §5.5 still says `Why`), and the implementation is what Kyle actually answers against. If a landed `retire` renames a column or a verdict, this file is the one edit that follows it — the skill body cites the contract, this file carries it.
