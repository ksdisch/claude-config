---
name: project-wiki
description: "Use when working in a project that has wiki sentinel files (PROJECT.md, a Wiki/ directory, or HANDOFF.md) and project state changes, a decision gets made, work pauses, or a new source needs integrating — or when /wiki-init or another skill (e.g. kickoff) asks to initialize a wiki, or when /wiki-backfill asks to backfill a project's history page."
---

# Project Wiki

Maintain a small, evidence-controlled wiki for this project. The goal is to preserve the understanding needed to resume, explain, and extend the project — a **compiled knowledge layer**, not a replacement for original sources.

---

## Mode selection

The wiki **sentinel files** are: `PROJECT.md`, a `Wiki/` directory, or `HANDOFF.md` at the repo root.

- **MAINTAIN** — at least one sentinel file exists and you're integrating new material, recording a decision, or updating status
- **INIT** — no sentinel file exists, or `/wiki-init` (or a parent flow like kickoff) explicitly requested initialization. An explicit request always routes to INIT, even if sentinel files exist — INIT is additive, so this is safe.
- **BACKFILL** — `/wiki-backfill` (or a parent flow) explicitly requested a retroactive history page. Requires an existing wiki sentinel — if none exists, report "no wiki here — run /wiki-init first" and stop. If `Wiki/History.md` already exists, report that and stop (MAINTAIN appends to it; BACKFILL never regenerates or overwrites it).

**INIT is additive and idempotent — never overwrite an existing wiki file.** If some wiki files already exist, create only the missing ones and leave the rest untouched. If `/wiki-init` runs in a fully initialized project (both `PROJECT.md` and `HANDOFF.md` exist), report that the wiki already exists and switch to MAINTAIN — but first run Step 4 if `CLAUDE.md` isn't wired yet.

---

## INIT — Initialize a project wiki

### Step 1: Inventory first

Before creating anything, do a read-only inventory:
- List all existing files in the project root and any `docs/`, `Wiki/`, `sources/` subdirectories
- Read the project's `CLAUDE.md`, `README.md`, and any existing `PROJECT.md` or `HANDOFF.md`
- Identify any existing source documents (briefs, specs, design docs, kickoff notes)

### Step 2: Choose the minimum structure

Report what you found and which files you'll create, **then proceed immediately — do not wait for approval**. (The only approval gate is the up-front confirmation in `/wiki-init --all`; a per-project pause here would stall unattended runs.) Never create empty folders to satisfy structure. The minimum starting set is:

```
PROJECT.md       — always create (if missing)
HANDOFF.md       — always create (if missing)
```

Create the others only when the project actually has the content to fill them:
- `Sources.md` — if there are identifiable authoritative sources
- `Decisions.md` — if any explicit decisions have already been made
- `Wiki/_index.md` + first topic page — if there's substantial domain knowledge worth durable capture

### Step 3: Create the missing files

**`PROJECT.md`** — use this template, filling from what you know about the project:

```markdown
# PROJECT.md

## Purpose
<One-sentence statement of what this project does and why it exists.>

## Scope
<What is explicitly IN scope for the current phase. Then: what is explicitly OUT / deferred / never.>

## Current status
<Active | Paused | Complete — plus one line on where it stands right now.>

## Next actions
1. <First concrete next step>
2. <Second>

## Boundaries
<Constraints: tech, time, data access, integrations, anything that limits what can be done.>
```

**`HANDOFF.md`** — use this template:

```markdown
# HANDOFF.md

_Last updated: <date>_

## What was just done
<1–3 bullet points on the most recent work completed.>

## Where things stand
<Current state in 2–4 sentences. Enough for a fresh session to resume without rereading everything.>

## Immediate next move
<The single most important next step, and why.>

## Open questions / blockers
- <Any unresolved question or missing information that will block progress>

## Files touched recently
- <path> — <why it matters>
```

**`Sources.md`** (when warranted) — use this template:

```markdown
# Sources

| Source | Location | Type | Authoritative for |
|--------|----------|------|-------------------|
| <name> | <path or URL> | brief / spec / export / transcript | <what claims it backs> |
```

**`Wiki/_index.md`** (when warranted) — use this template:

```markdown
# Wiki index

| Page | Covers | Last reviewed |
|------|--------|---------------|
| [<topic>](<topic>.md) | <one-line summary> | <date> |
```

**Link syntax — always relative markdown, never wikilinks.** These files are read on GitHub as often as locally, and GitHub's markdown renderer has no wikilink support: `[[History]]` renders as literal bracketed text, so the index's navigation is dead in the browser. Relative markdown links work in GitHub *and* in Obsidian-style tools, so there is no case for `[[...]]` anywhere in a wiki file.

- Page within `Wiki/` linking to a sibling → `[History](History.md)`
- Root file (`PROJECT.md`, `HANDOFF.md`) linking into the wiki → `[History](Wiki/History.md)`
- Wiki page linking back to root → `[Decisions](../Decisions.md)`

If you encounter existing `[[...]]` links while editing a wiki file, convert them in passing — the target is the same name plus `.md`.

### Step 4: Wire it to CLAUDE.md

Check if the project has a `CLAUDE.md` (or `.claude/CLAUDE.md`). If yes — and it doesn't already contain a "Project Wiki" section — append this at the bottom:

```markdown
## Project Wiki

This project uses the project-wiki skill. When integrating new sources, recording decisions, or pausing work:
- Update `PROJECT.md` status and next actions
- Update `HANDOFF.md` with what changed and what's next
- Add durable understanding to `Wiki/` topic pages
- Record decisions in `Decisions.md`
- Keep `Wiki/_index.md` current

(`Wiki/`, `Decisions.md`, and `Sources.md` are created on first need — templates live in the skill.)

Invoke the `project-wiki` skill when wiki updates are needed.
```

If no `CLAUDE.md` exists, do not create one just for this — note that there's no CLAUDE.md to update.

### Step 4b: Make the wiki discoverable from README.md

GitHub renders `README.md` on the repo homepage and nothing else, so a wiki with no inbound link from the README is effectively invisible to anyone browsing the repo. If a root `README.md` exists and does not already reference `PROJECT.md`, append a one-line pointer at the bottom:

```markdown
---

📚 **Project wiki:** [PROJECT.md](PROJECT.md) — status, scope, and next actions · [Wiki/_index.md](Wiki/_index.md) — topic pages and history
```

Drop the `Wiki/_index.md` half if this project has no `Wiki/`. This is the only README edit the skill ever makes: append a pointer, never restructure or rewrite existing README content. If there's no `README.md`, don't create one.

### Step 5: Commit

Land the new files per the global git workflow — branch + PR, merged autonomously:

1. Create a `docs/wiki-init` branch
2. Commit **only** the wiki files, the CLAUDE.md edit, and the README.md pointer line — never sweep unrelated dirty files into the commit
3. Push, open a PR, and merge it; include the PR link in the report

Exceptions:
- If INIT is running inside a parent flow that manages its own commits (e.g. the kickoff scaffold), skip this step — the parent flow commits the files
- If the repo has no remote, commit on the branch, merge it into the default branch locally, and delete the branch; note this in the report

### Step 6: Report

Print a concise summary:
```
Wiki initialized in <project-path>
  Created: PROJECT.md, HANDOFF.md [, any others]
  Skipped (already existed): [any]
  CLAUDE.md: updated / already wired / not found
  Landed: <PR link> / merged locally (no remote) / committed by parent flow

Next: fill in PROJECT.md scope and next actions if they're still TBD.
```

---

## BACKFILL — Retroactive project history

Build the project's evolution narrative — `Wiki/History.md` — by mining merged PRs, git history, wrap logs, and ADRs into a milestone-by-milestone story of how the project got here. BACKFILL runs once per project; ongoing upkeep is MAINTAIN's job (see "History page upkeep").

### Step 1: Preconditions

- A wiki sentinel must exist. If none does, report "no wiki here — run /wiki-init first" and stop.
- `Wiki/History.md` must NOT exist. If it does, report that and stop.
- BACKFILL touches **only** `Wiki/History.md` and `Wiki/_index.md` — never PROJECT.md, HANDOFF.md, Sources.md, Decisions.md, or CLAUDE.md.

### Step 2: Mine the history

Adapt the mining recipe from the project-guide skill's history section (`~/.claude/skills/project-guide/SKILL.md`) with these parameters:

- **PR title sweep (always full):** `gh pr list --state merged --limit 200 --json number,title,mergedAt,additions,deletions,labels`. If the limit saturates, raise it and disclose the true total in the footer.
- **Deep reads (capped at 20):** `gh pr view <n>` only on significant PRs, selected by: size (top decile by additions+deletions), labels (feature/breaking/epic), title signal (feat / refactor / migrate / v1 / launch / redesign / pivot / initial), always including the first and the most recent merged PR.
- **Git:** `git log --oneline --merges`, `git log --oneline --no-merges`, `git tag`.
- **Docs of intent:** wrap logs (`docs/session-logs/`, `.claude/session-logs/`), kickoff briefs, ADRs, and decision ledgers (`Decisions.md`, `DECISIONS.md`, `docs/adr/`) — read ledgers to anchor IDs, never to copy content.

Degenerate cases:
- **Fewer than ~5 merged PRs:** skip PR-driven eras; derive milestones from the commit log clustered by date gaps and conventional-commit prefixes, plus existing docs (kickoff brief, roadmap, wrap logs). A short page is honest — don't pad.
- **Rich decision ledger (D1–D30-style):** History.md is a chronological index that anchors ledger IDs — a "Why" line is at most one clause plus `— see D14 in DECISIONS.md`. Cite by ID + file path only (ledger formats differ; heading anchors are unreliable). Where a ledger row points onward to an ADR, cite the ledger row, not the ADR — single hop.

### Step 3: Write Wiki/History.md

Use this template:

```markdown
# History — <project>

> How this project got here: a chronological narrative of eras and milestones,
> reconstructed from merged PRs, git history, wrap logs, and ADRs.
> PR numbers, merge dates, tags, and SHAs are **Fact** by construction; rationale
> lines carry explicit labels (**Fact** when quoted from a PR body/ADR, **Inference**
> when reconstructed). Decisions are anchored by ID to the project's decision
> ledger — never restated here. **Append-only:** new milestones are added at the
> bottom (above the Mining coverage footer); existing entries are never rewritten.

## Origin — <YYYY-MM>
<2–4 sentences: why it started; first commit date + SHA; kickoff brief path if any.>

## Era: <name> (<YYYY-MM> – <YYYY-MM>)
<1–2 sentences: what phase this was, what changed by the end.>

### <Milestone title> — <YYYY-MM-DD>
- **Landed:** <one line> (PR #N, PR #M; tag vX.Y)
- **Why:** <recovered rationale> [Fact — PR #N body] — see D7 in `DECISIONS.md`
- **Tradeoff:** <chose A over B, paying C> [Inference — rationale not recorded]

---

## Mining coverage
_Backfilled <YYYY-MM-DD> by project-wiki BACKFILL. Entries after this date are
appended live by MAINTAIN._
- PR title sweep: all <N> merged PRs — no cap
- Deep reads: <K> of <N> PRs (size/label/title signal; cap 20)
- Also swept: git log (merges/no-merges), tags, wrap logs, ADRs (<paths or "none">)
- Not mined: <e.g. closed-unmerged PRs, issues>
```

Rules: eras oldest → newest; milestones dated; PRs cited `#N`; rationale lines labeled Fact/Inference; decisions anchored by ledger ID + file path; the footer discloses every source class swept or found absent and the deep-read K-of-N ratio — no silent caps.

### Step 4: Update Wiki/_index.md

- If `Wiki/` doesn't exist, create `Wiki/_index.md` using the INIT template with a single `[History](History.md)` row. (History.md is new synthesized narrative — it exists nowhere else, so this doesn't violate link-don't-duplicate even in repos that skipped `Wiki/` at init.)
- If it exists, append a `[History](History.md)` row — don't restructure. Relative markdown links only, per the INIT link-syntax rule.

### Step 5: Land and report

1. Cut a `docs/wiki-history` branch **from `origin/<default-branch>`** (resolve via `origin/HEAD`; never branch from the current checkout — it may be stale or on an unrelated branch)
2. Commit **only** `Wiki/History.md` and `Wiki/_index.md`
3. Push, open a PR, and merge it; if the repo has no remote, merge locally into the default branch
4. Report: era/milestone counts, PR sweep total N, deep-read count K, `_index.md` created/updated, PR link

---

## MAINTAIN — Update during ongoing work

### Surgical vs. broad changes

A change is **broad** if it touches 3+ wiki pages, restructures `Wiki/_index.md`, or removes/relocates existing content. For broad changes: report the proposed update scope first, then proceed — pause for approval only if the change would delete existing wiki content or move/rename source material. Single-page surgical updates (a HANDOFF refresh, a new decision row, one topic-page edit) need no report — just make them.

### Before integrating a new source or making broad wiki changes:

1. Read `PROJECT.md`, `Sources.md` (if it exists), and `Wiki/_index.md` (if it exists)
2. Inspect the new source or change
3. Identify which existing pages are affected
4. Report the proposed update scope (per the broad-change rule above) — don't silently reorganize
5. Make surgical updates to affected pages only
6. Preserve useful existing content; don't rewrite things that are still accurate
7. Add or update source references
8. Record contradictions and unresolved questions explicitly
9. Update `Wiki/_index.md` if you added or materially changed a page
10. Update `HANDOFF.md` if the project's state or next actions changed

**Do not reorganize the entire wiki because a new source was added.**

MAINTAIN updates ride the session's normal commits under the standard git workflow — no separate wiki branch or PR.

### History page upkeep

If the project has `Wiki/History.md` and the change you're landing is **milestone-significant** — a merged PR that completes a feature or phase, a pivot, a version tag, or a decision that changes direction — append one milestone entry at the bottom of the current era (or open a new `## Era:` heading if the project has clearly entered a new phase), **above the Mining coverage footer**. Follow the page's own header rules: append-only, PR/date facts unlabeled, rationale labeled Fact/Inference, decisions anchored by ledger ID, never restated. This is a surgical single-page update — no report needed. Routine commits, typo fixes, and dependency bumps do not get entries.

### Source rules (enforce these always)

- Treat original documents and raw exports as sources of truth
- Do not move, rename, rewrite, or delete source material unless explicitly authorized
- Link to authoritative sources instead of making uncontrolled duplicates
- Identify the source for every substantive factual claim

### Distinguish claim types explicitly

Always label claims with one of:
- **Fact** (source-supported)
- **Inference** (analysis derived from sources)
- **Recommendation** (a suggested course of action)
- **Decision** (approved — record in Decisions.md)
- **Proposed** (not yet approved)
- **Unresolved** (open question — use TBD or Unknown)
- **Contradiction** (sources disagree — flag explicitly, do not silently pick one)

### Wiki page format

Each durable `Wiki/` topic page should contain:

```markdown
# <Topic>

## Purpose
<What this page covers and why it exists in this wiki.>

## Key understanding
<The durable facts and inferences worth preserving.>

## Sources
- <Link or path to authoritative source> — <why it's relevant>

## Uncertainties & contradictions
- <What's unknown or disputed>

## Related pages
- [other-page](other-page.md) — <why it's related>

## Relevance to current work
<How this affects current or upcoming decisions.>

_Last reviewed: <date>_
```

### Decisions.md format

```markdown
# Decisions

| ID | Decision | Status | Date | Source/Rationale |
|----|----------|--------|------|-----------------|
| D1 | <What was decided> | Approved / Rejected / Proposed / Unresolved / Superseded | <date> | <why> |
```

The table is **append-only**: never rewrite or delete an existing row. When a decision replaces an older one, add a new row and mark the old row `Superseded (by D<n>)`.

---

## Cross-project knowledge

Project-specific information stays in this project. If a finding is useful across several projects, **identify it as a candidate** for a shared resource but do not automatically promote it. State:
- The proposed shared location
- The knowledge to promote
- The supporting projects or sources

Then wait for approval before moving anything outside this project.

---

## What NOT to do

- Do not overwrite an existing wiki file during INIT — create only what's missing
- Do not create empty folders or placeholder files to satisfy structure
- Do not move, rename, or delete source material without explicit authorization
- Do not silently choose between contradicting sources — flag the contradiction
- Do not reorganize the entire wiki when adding a single new source
- Do not duplicate source content — link to it instead
- Do not state "TBD" without flagging it as an open question to resolve
- Do not rewrite or delete Decisions.md rows — append and supersede
- Do not regenerate or reorder Wiki/History.md — it is append-only; BACKFILL runs once, MAINTAIN appends
- Do not restate decision-ledger or ADR content in History.md — anchor the ID and link the file
- Do not write `[[wikilinks]]` in any wiki file — GitHub renders them as dead literal text; use relative markdown links
- Do not rewrite or restructure a project's README.md — the only permitted edit is appending the wiki pointer line
