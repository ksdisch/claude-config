---
name: project-wiki
description: Maintain an evidence-controlled project wiki. Two modes: INIT (create the minimum structure for a new or existing project) and MAINTAIN (surgical updates when integrating new sources, recording decisions, or updating status). Invoked automatically when Claude detects wiki sentinel files (PROJECT.md, Wiki/, HANDOFF.md), or explicitly via /wiki-init.
---

# Project Wiki

Maintain a small, evidence-controlled wiki for this project. The goal is to preserve the understanding needed to resume, explain, and extend the project — a **compiled knowledge layer**, not a replacement for original sources.

---

## Mode selection

Determine the mode from context:
- **INIT** — no wiki files exist yet, or `/wiki-init` was invoked
- **MAINTAIN** — wiki files already exist and you're integrating new material, recording a decision, or updating status

If called without explicit context, check for `PROJECT.md` or `Wiki/` in the repo root. If present, run MAINTAIN; otherwise run INIT.

---

## INIT — Initialize a project wiki

### Step 1: Inventory first

Before creating anything, do a read-only inventory:
- List all existing files in the project root and any `docs/`, `Wiki/`, `sources/` subdirectories
- Read the project's `CLAUDE.md`, `README.md`, and any existing `PROJECT.md` or `HANDOFF.md`
- Identify any existing source documents (briefs, specs, design docs, kickoff notes)

### Step 2: Propose the minimum structure

Report what you found and recommend only the files the project actually needs right now. Never create empty folders to satisfy structure. The minimum useful starting set is:

```
PROJECT.md       — always create this
HANDOFF.md       — always create this
```

Create the others only when the project actually has the content to fill them:
- `Sources.md` — if there are identifiable authoritative sources
- `Decisions.md` — if any explicit decisions have already been made
- `Wiki/_index.md` + first topic page — if there's substantial domain knowledge worth durable capture

### Step 3: Create the files

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

### Step 4: Wire it to CLAUDE.md

After creating the wiki files, check if the project has a `CLAUDE.md` (or `.claude/CLAUDE.md`). If yes, add this section (before the last heading or at the bottom):

```markdown
## Project Wiki

This project uses the project-wiki skill. When integrating new sources, recording decisions, or pausing work:
- Update `PROJECT.md` status and next actions
- Update `HANDOFF.md` with what changed and what's next
- Add durable understanding to `Wiki/` topic pages
- Record decisions in `Decisions.md`
- Keep `Wiki/_index.md` current

Invoke the `project-wiki` skill when wiki updates are needed.
```

If no `CLAUDE.md` exists, do not create one just for this — note that there's no CLAUDE.md to update.

### Step 5: Report

Print a concise summary:
```
Wiki initialized in <project-path>
  Created: PROJECT.md, HANDOFF.md [, any others]
  CLAUDE.md: updated / not found
  
Next: fill in PROJECT.md scope and next actions if they're still TBD.
```

---

## MAINTAIN — Update during ongoing work

### Before integrating a new source or making broad wiki changes:

1. Read `PROJECT.md`, `Sources.md` (if it exists), and `Wiki/_index.md` (if it exists)
2. Inspect the new source or change
3. Identify which existing pages are affected
4. **Report the proposed update scope before making broad changes** — don't silently reorganize
5. Make surgical updates to affected pages only
6. Preserve useful existing content; don't rewrite things that are still accurate
7. Add or update source references
8. Record contradictions and unresolved questions explicitly
9. Update `Wiki/_index.md` if you added or materially changed a page
10. Update `HANDOFF.md` if the project's state or next actions changed

**Do not reorganize the entire wiki because a new source was added.**

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
- [[other-page]] — <why it's related>

## Relevance to current work
<How this affects current or upcoming decisions.>

_Last reviewed: <date>_
```

### Decisions.md format

```markdown
# Decisions

| ID | Decision | Status | Date | Source/Rationale |
|----|----------|--------|------|-----------------|
| D1 | <What was decided> | Approved / Rejected / Proposed / Unresolved | <date> | <why> |
```

---

## Cross-project knowledge

Project-specific information stays in this project. If a finding is useful across several projects, **identify it as a candidate** for a shared resource but do not automatically promote it. State:
- The proposed shared location
- The knowledge to promote
- The supporting projects or sources

Then wait for approval before moving anything outside this project.

---

## What NOT to do

- Do not create empty folders or placeholder files to satisfy structure
- Do not move, rename, or delete source material without explicit authorization
- Do not silently choose between contradicting sources — flag the contradiction
- Do not reorganize the entire wiki when adding a single new source
- Do not duplicate source content — link to it instead
- Do not state "TBD" without flagging it as an open question to resolve
