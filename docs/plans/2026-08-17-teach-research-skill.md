# teach-research Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `teach-research` companion skill — mission interview → gated two-phase research fan-out → `RESOURCES.md` + `research/` digests that `/teach` consumes with zero changes to teach itself.

**Architecture:** A single global skill directory `skills/teach-research/` containing `SKILL.md` (numbered procedure + named invariants, no copy-paste shell — see the skill-shell-snippets memory) and `RESEARCH-FORMAT.md` (the digest format it owns). `MISSION.md`/`RESOURCES.md` formats stay owned by teach; this skill only reads them. Reference-doc row + playbook card land in the same commit per the CLAUDE.md sync rule.

**Tech Stack:** Markdown skill files only — no code. Verification = `scripts/check-doc-sync.py` + format-fidelity greps + a live smoke run in a scratch workspace.

**Spec:** `docs/superpowers/specs/2026-08-16-teach-research-design.md` (approved 2026-08-16). The spec wins on any conflict with this plan.

**Branch:** all work on `feat/teach-research-skill` (already exists; spec commit `64ca1af` is on it).

---

### Task 1: Write `RESEARCH-FORMAT.md`

**Files:**
- Create: `skills/teach-research/RESEARCH-FORMAT.md`

- [ ] **Step 1: Create the file with exactly this content**

````markdown
# research/ Digest Format

Each cached source is one file at `research/<slug>.md`, where the slug is the dash-case of the
source title (drop articles and punctuation: "The Rust Programming Language" →
`rust-programming-language`). Digests exist so later lessons can cite and quote sources without
re-fetching the web.

## Template

```md
# {Source title}

- **URL:** {url}
- **Type:** {docs | book | course | video | paper | blog | community}
- **Author/steward:** {who, plus one line on why they are trustworthy}
- **Fetched:** {YYYY-MM-DD — or "not fetched: {reason}" for metadata-only digests}
- **Covers:** {one line: which part of the mission this source serves}

## Structure
{The source's own shape — table of contents, chapter list, video chapters — so a lesson can
cite "chapter 4" without re-fetching.}

## Key concepts
{The load-bearing ideas, compressed. Aim for the 20% a lesson would actually cite.}

## Notable quotes
{Short attributed excerpts, each with a location (section / page / timestamp).}
```

## Rules

- **Digest, not dump.** Select quotes and compressed concepts only — never a verbatim copy of
  the source. This is both a copyright posture and a usefulness one: a dump is as unreadable
  as the original.
- **Metadata-only digests** (books, paywalls, anything unfetchable): keep the header block and
  `Covers`, add one line on where to get the source, and omit `Structure`, `Key concepts`,
  and `Notable quotes` entirely. Never fabricate content for a source that was not fetched.
- **Every digest is linked.** Its `RESOURCES.md` entry carries `Cached: ./research/<slug>.md`;
  a digest no entry links to is an orphan and should be deleted.
- **One source per file.** A digest that covers two sources should be two files.
````

- [ ] **Step 2: Verify the file parses as expected**

Run: `head -5 skills/teach-research/RESEARCH-FORMAT.md`
Expected: the `# research/ Digest Format` title line appears; no frontmatter (format docs in the teach family carry none).

*(Commit comes in Task 4 — the CLAUDE.md sync rule wants skill + row + card in one commit.)*

---

### Task 2: Write `SKILL.md`

**Files:**
- Create: `skills/teach-research/SKILL.md`

Constraints from the spec and the skill-shell-snippets memory, restated because they shape every line:
- Numbered procedure steps + **named invariants** referenced by name — no fenced shell blocks, no shell variables; state *values* ("the topic", "the resolved directory").
- Typed-only (`disable-model-invocation: true`).
- `--auto` skips exactly the curation gate, nothing else.
- The skill writes only `MISSION.md`, `RESOURCES.md`, `research/`.

- [ ] **Step 1: Create the file with exactly this content**

````markdown
---
name: teach-research
description: Research companion for the teach skill — interviews for the mission, fans out parallel finder agents across six source modalities, gates the candidate list through the user, then caches approved sources as digests, leaving MISSION.md, RESOURCES.md, and research/ ready for /teach to consume. The teach skill itself is never modified. Typed-only entry point (/teach-research <topic>) — run it from a dedicated learning directory, not inside a project repo, since it writes workspace files at the root of wherever it runs. Append --auto to skip the curation gate for unattended runs.
disable-model-invocation: true
argument-hint: "What topic should be researched? (append --auto to skip the curation gate)"
---

The user wants a learning workspace stocked with vetted sources before (or between) `/teach`
sessions — so that lesson one is a lesson, not a search. This skill front-loads the
resource-finding work the teach skill would otherwise do inline during teaching sessions.

## Relationship to the teach skill

This skill writes exactly three things at the root of the current directory: `MISSION.md`,
`RESOURCES.md`, and `research/`. The first two are files the teach skill already reads, in
formats the teach skill owns — read [../teach/MISSION-FORMAT.md](../teach/MISSION-FORMAT.md)
and [../teach/RESOURCES-FORMAT.md](../teach/RESOURCES-FORMAT.md) before writing either.
`research/` digests follow [RESEARCH-FORMAT.md](./RESEARCH-FORMAT.md), owned here.

## Invariants

Every procedure step below names the invariants it must uphold. Reference them by name.

- **teach-untouched** — never edit the teach skill's files, and never write any workspace file
  other than the three above. `lessons/`, `reference/`, `learning-records/`, `assets/`,
  `GLOSSARY.md`, and `NOTES.md` belong to the teach skill.
- **mission-grounded** — no discovery begins until `MISSION.md` exists and the user has
  confirmed it this run. Every finder brief carries the mission.
- **never-clobber** — existing `MISSION.md` content and existing `RESOURCES.md` entries are
  merged into, never overwritten or removed. Pruning is the user's move, not this skill's.
- **verified-links** — no URL reaches the candidate table unless the finder that proposed it
  confirmed the URL resolves. A source that cannot be verified is reported as a gap, not
  listed as a source.
- **digest-not-dump** — cache files are digests with select attributed quotes, never verbatim
  copies. Unfetchable sources get metadata-only digests; content is never fabricated.
- **honest-gaps** — every modality no finder could cover, every candidate the user cut for a
  reason worth remembering, and every failed fetch lands in the `## Gaps` section of
  `RESOURCES.md`. Silent omission is the failure mode this invariant exists to prevent.
- **gate-only-auto** — `--auto` skips exactly one thing: the curation gate (step 6). It never
  skips the workspace guard, the mission step, or verification.

## Workspace Guard

Before any other step — including the mission step — check that the current directory is a
dedicated learning workspace:

- If `MISSION.md` already exists here, this is an established workspace: proceed.
- Otherwise, if the directory shows signs of being a software project or other pre-existing
  content (`.git`, `package.json`, `CLAUDE.md`, source code, an existing `assets/` or
  `NOTES.md`), or is the user's home directory, **stop before writing anything**: report the
  resolved current directory and the exact paths this skill would write (`MISSION.md`,
  `RESOURCES.md`, `research/`), suggest a dedicated directory instead (e.g.
  `~/Learning/<topic>/`), and wait for the user to confirm this location or point at another.
  Never create the first workspace file until the location is confirmed.

## Procedure

1. **Parse the invocation.** The argument is the topic; the literal token `--auto` anywhere in
   it sets auto mode (*gate-only-auto*). No topic and no existing `MISSION.md` → ask for one.
2. **Run the Workspace Guard** above.
3. **Mission.** If `MISSION.md` exists, summarize it back to the user in two sentences and ask
   for a brief confirm (in auto mode, an existing mission is taken as confirmed). If it does
   not exist, run a mission interview in the style the teach skill prescribes — push back on
   vagueness, concrete over abstract, one question at a time — and write `MISSION.md` per
   [../teach/MISSION-FORMAT.md](../teach/MISSION-FORMAT.md). In a truly unattended run
   (subagent, cron, cloud one-shot) with no `MISSION.md`, stop and report instead: a mission
   cannot be invented on the user's behalf (*mission-grounded*, *never-clobber*).
4. **Detect top-up mode.** If `RESOURCES.md` exists, this run is a top-up: read every existing
   entry and the current `## Gaps` section. Finders will receive both, hunt only for what is
   missing, and results will merge (*never-clobber*).
5. **Discovery fan-out.** Dispatch six finder subagents in parallel, one per modality:
   official docs / primary sources · books · structured courses · video · papers &
   high-signal blogs · communities. Each finder's brief contains: the mission (verbatim
   `Why` and `Success looks like` sections), its single modality, the already-held sources to
   exclude (top-up mode), and the required return shape — for each candidate: title, URL,
   type, author plus one line on why they are trustworthy, what it covers, one line on
   mission fit, and whether it is one of the finder's top 2–3 picks. Each finder must fetch
   every URL it proposes and drop any that does not resolve (*verified-links*); it reports a
   thin modality honestly rather than padding with weak sources (*honest-gaps*).
6. **Curation gate.** Merge the finders' returns, dedup by URL and by near-identical title,
   and present one table grouped by modality — columns: title, type, why trusted, mission
   fit, keep/cut recommendation. The user trims, swaps, or says "take all"; wait for that
   answer. In auto mode (*gate-only-auto*): keep exactly the finders' top picks, cut the
   rest, and record in the closing summary that the gate was skipped.
7. **Caching fan-out.** Batch the kept sources three to four per cacher subagent. Each cacher
   fetches its sources and writes one digest per source at `research/<slug>.md` per
   [RESEARCH-FORMAT.md](./RESEARCH-FORMAT.md) (*digest-not-dump*). A fetch that fails
   mid-run downgrades that source to a metadata-only digest plus a gap note — it never aborts
   the run (*honest-gaps*).
8. **Write `RESOURCES.md`** per
   [../teach/RESOURCES-FORMAT.md](../teach/RESOURCES-FORMAT.md): `## Knowledge` and
   `## Wisdom (Communities)` sections, every entry annotated with its one-line
   what-it-covers/when-to-reach-for-it note plus a final line `Cached: ./research/<slug>.md`
   pointing at its digest. Write the `## Gaps` section from everything *honest-gaps*
   collected. In top-up mode, merge new entries into the existing sections and rewrite
   `## Gaps` to reflect what is still open (*never-clobber* for entries; Gaps is the one
   section this skill rewrites wholesale, because a filled gap is not history worth keeping).
9. **Verify the contract.** Confirm: every `RESOURCES.md` entry's `Cached:` path exists; every
   file in `research/` is linked from some entry; no file outside `MISSION.md`,
   `RESOURCES.md`, `research/` was created or modified (*teach-untouched*).
10. **Close.** Report to the user: sources found per modality, what was cached, the open gaps,
    whether the gate was skipped — and finish with: run `/teach` from this directory; the
    mission is answered and the resources are stocked.

## Unattended runs

Auto mode makes steps 4–10 fully unattended, so `/teach-research <topic> --auto` can run
overnight **in a workspace whose `MISSION.md` already exists** (or interactively, where the
mission interview runs first and everything after is automatic). Unattended with no mission =
stop and report, per step 3.
````

- [ ] **Step 2: Verify frontmatter and invariant integrity**

Run: `head -8 skills/teach-research/SKILL.md`
Expected: frontmatter opens with `name: teach-research` and contains `disable-model-invocation: true`.

Run: `grep -c 'shell\|```bash\|```sh' skills/teach-research/SKILL.md`
Expected: `0` — no shell blocks (the skill-shell-snippets rule).

Run: `grep -oE '\*[a-z-]+\*' skills/teach-research/SKILL.md | sort -u`
Expected: every starred invariant name referenced in the procedure (`*digest-not-dump*`, `*gate-only-auto*`, `*honest-gaps*`, `*mission-grounded*`, `*never-clobber*`, `*teach-untouched*`, `*verified-links*`) matches a name defined in the Invariants section — no orphan references, no unreferenced invariants.

---

### Task 3: Reference-doc row + playbook card

**Files:**
- Modify: `docs/command-skill-reference.md` (Personal Coaching skills table — teach's row is line 141 at time of writing; insert directly below it)
- Modify: `docs/usage-playbook.md` (Personal Coaching section — insert a card after teach's card, which starts at line 941 at time of writing; also add a cross-link in teach's card)

- [ ] **Step 1: Add the reference row directly below teach's row**

```markdown
| [`teach-research`](../skills/teach-research/SKILL.md) | Research companion for `teach` — mission interview, parallel six-modality source discovery, a curation gate, then cached digests plus a curated `RESOURCES.md` that `/teach` consumes unchanged. Typed-only (`/teach-research`); run from the learning directory. · [config →](usage-playbook.md#teach-research) |
```

- [ ] **Step 2: Add the playbook card after teach's card in the Personal Coaching section**

```markdown
#### `teach-research`

- **Run config:** Opus 5 · `high` — the skill's own finder/cacher fan-out does the parallel
  work; the session around it is orchestration plus synthesis-heavy digesting.
- **Reach for it when:**
  - You're about to start learning a topic with `/teach` and want the workspace stocked
    first — mission captured, sources vetted, digests cached — so lesson one is a lesson,
    not a search.
  - A teach workspace's `RESOURCES.md` is thin, or its `## Gaps` section has grown
    (top-up mode).
- **Pairs well with:** [`teach`](#teach) (the consumer — run it right after this),
  [`career-coach`](#career-coach) (when the question is *what* to learn, not how).
- **Notes:** typed-only (`disable-model-invocation: true`) — fires only on `/teach-research`.
  `--auto` skips the curation gate only; the mission interview still runs, so a truly
  unattended run needs `MISSION.md` to already exist. Writes only `MISSION.md`,
  `RESOURCES.md`, and `research/` — the teach skill itself is never edited.
```

- [ ] **Step 3: Cross-link from teach's card**

In teach's card's **Pairs well with** line (docs/usage-playbook.md:949-952 at time of writing), add as the first entry:

```markdown
[`teach-research`](#teach-research) (stocks the workspace with vetted, cached sources before lesson one),
```

- [ ] **Step 4: Verify anchors agree**

Run: `grep -n 'teach-research' docs/command-skill-reference.md docs/usage-playbook.md`
Expected: the row's `config →` link targets `usage-playbook.md#teach-research`; a `#### \`teach-research\`` heading exists; teach's card links `#teach-research`.

---

### Task 4: Doc-sync check + single commit

**Files:** none new — verification and commit of Tasks 1–3.

- [ ] **Step 1: Run the sync checker**

Run: `python3 scripts/check-doc-sync.py`
Expected: passes — new skill file has a row, row has a card, no orphan links. (This same check runs at `git push` as the pre-push hook, so it must pass here.)

- [ ] **Step 2: Commit everything from Tasks 1–3 as one commit**

Stage: `skills/teach-research/SKILL.md`, `skills/teach-research/RESEARCH-FORMAT.md`, `docs/command-skill-reference.md`, `docs/usage-playbook.md`.

Commit message (harness footer lines — Co-Authored-By and Claude-Session — appended per session convention):

```
feat: teach-research skill — research companion for teach

Mission interview -> gated two-phase fan-out (six modality finders,
curation gate, batched cachers) -> RESOURCES.md + research/ digests
consumed by /teach with zero changes to teach. Reference row +
playbook card in this commit per the sync rule.
```

---

### Task 5: Live smoke run

**Files:** none in the repo — scratch workspace at `~/Learning/_smoke-teach-research/`.

The point: prove the outputs match teach's formats and that the flow survives contact with the real web. To bound cost, pre-seed the mission (skipping the interview) and run in auto mode; cap each finder at 3 candidates for this run only — a smoke-run cap, not a skill rule.

- [ ] **Step 1: Create the scratch workspace and pre-seed `MISSION.md`**

Create `~/Learning/_smoke-teach-research/MISSION.md` containing:

```markdown
# Mission: Sourdough Baking

## Why
Bake a consistently good sourdough loaf at home within two months, well enough to stop buying
bread.

## Success looks like
- Maintain a starter that reliably doubles after feeding
- Bake a loaf with an open crumb and real oven spring, twice in a row

## Constraints
- Home oven, no special equipment beyond a dutch oven
- Weekend bakes only

## Out of scope
- Commercial/professional baking
- Non-sourdough breads
```

- [ ] **Step 2: Execute the skill's procedure in the scratch directory**

From `~/Learning/_smoke-teach-research/`, follow `skills/teach-research/SKILL.md` end to end as `/teach-research sourdough baking --auto` would: guard (passes — `MISSION.md` exists), mission confirmed from file, six finders (3-candidate smoke cap), auto-keep top picks, cache, write `RESOURCES.md`.

- [ ] **Step 3: Verify the contract**

Check, from the scratch directory:
- `RESOURCES.md` has `## Knowledge`, `## Wisdom (Communities)`, and (if anything was uncoverable) `## Gaps` headings — teach's RESOURCES-FORMAT shape.
- Every entry has an annotation line and a `Cached: ./research/<slug>.md` line, and every such path exists: `grep -o 'research/[a-z0-9-]*\.md' RESOURCES.md | sort -u | xargs ls` lists them all without error.
- Every file in `research/` is linked from `RESOURCES.md` (no orphans), and each fetched digest has the header block plus `Structure` / `Key concepts` / `Notable quotes`; metadata-only digests have header + `Covers` only.
- Directory contains **only** `MISSION.md`, `RESOURCES.md`, `research/` — nothing else was written.
- `MISSION.md` is byte-identical to the pre-seeded version (never-clobber): compare against the content in Step 1.

- [ ] **Step 4: Fix-forward if the smoke run exposes a skill defect**

Any failure here is a SKILL.md or RESEARCH-FORMAT.md bug: fix the skill file, re-run the failing part, and commit the fix on the branch with a `fix:` message describing the defect the smoke run caught. (If the fix reworks the `description:` frontmatter, update the reference row and card in the same commit per the sync rule.)

- [ ] **Step 5: Delete the scratch workspace**

Remove `~/Learning/_smoke-teach-research/` once verification passes — it was created by this plan for this purpose (single directory delete; not covered by any repo).

---

### Task 6: Push, PR, adversarial review, merge

- [ ] **Step 1: Push the branch**

Run: `git push -u origin feat/teach-research-skill`
Expected: pre-push hook runs `check-doc-sync.py` on the pushed commits and passes.
Note (from the deploy-wiring memory): run the push as its own command, separate from any command whose text contains "main", to avoid the hook false-positive.

- [ ] **Step 2: Open the PR**

Title: `feat: teach-research skill — research companion for teach`. Body: summary of the skill, link to the spec file (`docs/superpowers/specs/2026-08-16-teach-research-design.md`), note that teach is untouched and the smoke run passed (with the scratch-run evidence from Task 5 Step 3), harness PR footer appended.

- [ ] **Step 3: Run the adversarial-review loop**

This diff adds a skill — the trivial-diff escape hatch explicitly excludes skills, so the full loop runs: reviewer → author triage → judge on disputes → fix → re-check, per the `adversarial-review` skill. Critical and should-fix findings must be resolved before merge; nice-to-haves become follow-ups listed in the PR comment.

- [ ] **Step 4: Merge, clean up, end live**

Merge the PR once the verdict is CLEAR; delete the remote feature branch (routine cleanup for a self-created, merged branch); locally check out `main` and pull — the `~/.claude/skills` symlink makes the skill live only once `main` is pulled. Brief Kyle: what merged, SHA, PR link, review verdict.

---

## Self-review notes (run against the spec)

- **Spec coverage:** §3 identity/flags → Task 2 frontmatter + step 1/gate-only-auto; §4 flow steps 1–5 → SKILL.md procedure 3–10; §5 workspace contract → teach-untouched invariant + procedure 9 + smoke Step 3; §6 top-up/failures/scale → procedure 4, 7 (batching, downgrade), never-clobber; §7 landing → Tasks 3–6; §8 out-of-scope → no task touches teach, no syllabus/glossary output anywhere. No gaps found.
- **Placeholder scan:** all file content is verbatim in Tasks 1–3; smoke mission verbatim in Task 5. No TBDs.
- **Consistency:** invariant names in the procedure match the Invariants section 1:1 (checked in Task 2 Step 2's grep); `research/<slug>.md` slug rule defined once (RESEARCH-FORMAT.md) and referenced elsewhere; anchor `#teach-research` consistent across row, card, and cross-link.

---

**Run-config note:** Opus 5 · `high` — the file contents are embedded verbatim above, so this is well-specified build work; the judgment lives in the smoke run and review triage. Launch: `claude --model claude-opus-5 --effort high`
