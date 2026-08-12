---
name: curriculum-sync
description: Keep a NotebookLM notebook's DERIVED content — audio/video seasons, study guides, per-episode quizzes — and its paired home-base course in step with the repos underneath them, or build a whole new notebook→course chain from scratch. Owns a derivation ledger (`DERIVED.md`) that records what every artifact and course material was generated from and at what source state, so staleness is a hash comparison rather than a judgment call; delegates all execution to portfolio-notebook-sync (sources), audio-series / video-series (generation mechanics), and course-builder (the course contract). Four modes — bare drift check, `--adopt`, `--refresh`, `--new`. Use when Kyle says "the audio series is out of date", "my portfolio changed — refresh the notebook and course", "regenerate the episodes and quizzes", "the course is stale", "refresh the study guides", "build a new notebook and course for X", or types `/curriculum-sync`. NOT for: source-layer drift alone (portfolio-notebook-sync), generating a season on a notebook whose sources are already current (audio-series), or building a course with no notebook in play (course-builder).
---

# curriculum-sync — keep the notebook→course chain honest

Kyle's learning material is a four-link chain, and before this skill only the first link was
machine-checked:

```
~/Projects/<repo>   →   notebook sources   →   notebook artifacts   →   home-base course
   (git)                 MANIFEST.md            DERIVED.md §1            DERIVED.md §2
                                                        ↘   study path JSON + course.json
                                                            (hard-reference artifact ids)
```

`portfolio-notebook-sync` keeps link 1 → 2 honest. This skill keeps everything downstream of it
honest, and it does that the same way: **a ledger, and a hash comparison against it.**

**Core principle: `DERIVED.md` is the contract.** `MANIFEST.md` answers *"is this source current?"*
`DERIVED.md` answers *"is what we made from that source current?"* Never re-derive "what needs
regenerating" from scratch or from memory of a previous run — read the ledger and diff against it.

**This skill is a thin orchestrator.** It owns the ledger, the staleness diff, and the gates.
Everything else is delegated, and the delegates' mechanics are named here, never restated:

| Layer | Delegate | What the delegate owns |
|---|---|---|
| Sources | [[portfolio-notebook-sync]] | `MANIFEST.md`, the hash procedure, read-only-git rules, `--add` |
| Audio / video | [[audio-series]], [[video-series]] | Quota model, wave batching, poll-to-completion, the rename rule |
| Course | `course-builder` (home-base `.claude/skills/`) | Manifest schema, the `cli write` bridge, pedagogy |
| New notebook | [[notebook-init]] | Sidecar template, INDEX entry, source curation |

Tool preference: **MCP-first** (`mcp__notebooklm-mcp__*`); `nlm` CLI via Bash as fallback. See
`nlm-skill` for tool docs.

Detailed formats and procedures live in the references — read the one you need before acting:
- [`references/ledger.md`](references/ledger.md) — `DERIVED.md` format, the basis-hash procedure, `--adopt`
- [`references/crosslinks.md`](references/crosslinks.md) — study-path + `course.json` reference repair

---

## Modes, and the walls between them

| Mode | Invocation | Does |
|---|---|---|
| **Drift check** | bare | Read-only. Computes the staleness table across both layers and reports. |
| **Adopt** | `--adopt` | Backfills `DERIVED.md` for a pair that predates the ledger. Run once per pair. |
| **Refresh** | `--refresh` | Executes the refresh for what the check found stale, behind the gates. |
| **New** | `--new` | Builds a fresh notebook→course chain and writes the ledger from birth. |

These walls are borrowed from [[portfolio-notebook-sync]], which earned them:

- **A drift check never generates, deletes, or writes.** The one file this skill may create is
  `DERIVED.md`, and only under `--adopt`.
- **`--refresh` never onboards.** A project with no notebook source, or a project with no course
  module, is a **finding to report**. Adding a source is `portfolio-notebook-sync --add`'s job;
  adding a lesson is a syllabus change (Gate 3). Silently growing the corpus during a "refresh" is
  the failure this wall prevents.
- **`--new` never touches an existing notebook.** If the alias resolves to a live notebook, stop
  and route to `--adopt`.
- **No mode changes git state in a source repo.** Read-only git (`rev-parse`, `show`, `ls-tree`,
  `log`, `status`, `gh pr list/view`) is required — it is how you fill hashes at all. The single
  sanctioned exception is the one [[portfolio-notebook-sync]] already defines: a
  `fetch --no-write-fetch-head` against `origin` in a project repo, because Kyle merges on GitHub
  and a local ref does not advance on its own. `pull` stays forbidden — it also merges.
- **No mode edits a source repo's files.** A README that contradicts itself is a finding, not a fix.
- **No mode deletes anything without a separate confirm** (Gate 2).

---

## Step 1 — Identify the pair

1. Resolve the **notebook**: by alias, from `~/Projects/NotebookLMs/INDEX.md`, or by asking. Capture
   `notebook_id`, `alias`, and the sidecar path `~/Projects/NotebookLMs/<alias>/`.
2. Resolve the **course**: a home-base course under `COURSES_DIR` (default
   `~/Projects/home-base/backend/data/courses/<slug>/`) whose `course.json` carries a `notebooklm`
   material referencing this `notebook_id`. That reference **is** the pairing; do not pair by name
   similarity.
3. If no course references the notebook, say so and continue with §1 only. A notebook without a
   course is a valid pair-of-one, not an error.
4. Note which of `MANIFEST.md` and `DERIVED.md` exist. Their absence routes the run:
   - no `DERIVED.md` → only `--adopt` and `--new` can proceed; a bare check reports "no ledger" and
     offers `--adopt`.
   - no `MANIFEST.md` → degraded mode; see **Degradation** below.

## Step 2 — The source layer comes first, and it is a hard gate

**Never compute derived staleness — and never regenerate anything — on top of an unclean source
layer.**

1. Run the source-layer drift check: for the portfolio pair, delegate to
   [[portfolio-notebook-sync]] (bare). For other notebooks, compare `MANIFEST.md` yourself using
   that skill's hash procedure.
2. If any source row comes back `changed`, `deleted`, or `unchecked`, **stop the refresh**. Report
   the source drift and hand it to `portfolio-notebook-sync`, which owns the repair and its own
   confirm. Only once the source layer reports clean does the derived refresh proceed.

This is Kyle's own recorded decision promoted to a rule. The sidecar states it plainly:
*"Study aids were NOT regenerated — the source layer is not clean … regenerating now would bake
that staleness into four fresh artifacts."* Regenerating over dirty sources is **worse** than
leaving artifacts stale, because the replacements carry a fresh date and look current.

A bare drift check may still *report* derived staleness on a dirty source layer — it changes
nothing — but it must label the result provisional and say the source layer has to be repaired
first.

## Step 3 — Compute the staleness table

For every row in both sections of `DERIVED.md`, recompute the basis and compare
(see [`references/ledger.md`](references/ledger.md) for the procedure).

- Equal → `current`
- Different → `stale`
- Uncomputable, or scope changed since the row was written → `unverified`, **treated as stale**

Reconcile both directions and report both:
- a live artifact / course material with **no ledger row** (never adopted, or created outside this
  skill), and
- a ledger row with **no live artifact / no file on disk** (deleted out from under the ledger).

Present as one table per section, sorted by section then by status.

## Step 4 — Gate 1: the costed plan

The load-bearing gate. Present, in one message:

1. The staleness table for both layers.
2. **The cost.** How many audio and video generations the plan requires, against the observed
   rolling **~15-per-24h account-wide** audio cap; which wave lands on which day; and what the plan
   does if quota runs out mid-season.
3. **What gets deleted** — every superseded artifact, by title and id.
4. **What cross-links will be rewritten** — every study-path step and `course.json` material that
   references an artifact this plan replaces (see [`references/crosslinks.md`](references/crosslinks.md)).
5. Which course lessons will be re-authored, and which will be left alone.

One explicit go-ahead covers execution of that plan. Audio is expensive and outward-facing —
**generate nothing without it.**

## Step 5 — Execute, top-down

Order is not negotiable. Each layer's basis is the layer above it.

### 5a. Cheap text artifacts — no quota

Study guides, quizzes, flashcards, mind maps. These are text artifacts, are **not** subject to the
audio quota, and tolerate large concurrent batches (14–16 fire fine). Regenerate every `stale` and
`unverified` row of these kinds in one or two waves, then rename to the notebook's existing scheme.

Carry one recorded lesson from this notebook's history: **`focus_prompt` alone does not steer
`report` or `mind_map` generation** — both come back about the wrong material with
`custom_instructions` null. Scope them with `source_ids`, which is a hard boundary.

### 5b. Audio and video — season-level re-record

**Policy (Kyle's call, 2026-08-07): if any source behind a season moved, the whole season is
re-recorded**, so episodes that reference each other stay internally consistent. There is no
per-episode surgical re-record mode.

1. Do the quota arithmetic **before firing anything** and stage the plan across days. A season of 8
   plus a season of 6 does not fit in one ~15/24h window with any retry headroom.
2. Delegate every generation mechanic to [[audio-series]] / [[video-series]]: batch ~5–6 (the
   concurrency cap is ~11), poll to completion, and **rename only on `status:"completed"`** — an
   early rename is overwritten by NotebookLM's auto-title, and `unknown` + a non-null `audio_url` is
   the lag window, not the green light.
3. A wave is not done until every artifact in it that completed has been renamed.
4. Quota-blocked episodes become `deferred` rows in `DERIVED.md` **with their verbatim focus
   prompts**, so the next run re-fires what is left instead of re-planning the season. Capacity
   returns ~24h after the saturating batch, not at midnight.
5. Record the new `artifact_id`s as you go — they are the input to cross-link repair.

### 5c. Course materials

1. Re-author only the lessons whose §2 basis moved. Leave the rest byte-identical.
2. **Minimal-diff rule.** Preserve flashcard fronts and quiz stems wherever the underlying fact did
   not change. A flashcard's front text **is** its identity in the hub's per-card SM-2 store, so
   rewording a front that did not need rewording silently resets that card's review schedule.
   Change backs, rationales, and numbers freely; change a front only when the card is genuinely
   about something else now. If you fan out re-authoring to subagents, this rule goes in the
   payload verbatim.
3. Commit through `course-builder`'s CLI bridge — the `write` subcommand under the home-base
   backend's `.venv`, which validates atomically, rolls back on failure, and exits non-zero on
   `ok:false`. Never hand-edit `course.json` around the bridge.
4. Per `course-builder`'s update-in-place rule, stale material files the new manifest no longer
   references are **not** auto-removed. Delete them so the directory matches the manifest.

### 5d. Cross-link repair — mandatory and terminal

Regenerating an artifact mints a **new** `artifact_id`, and two places in home-base hard-reference
the old one. Follow [`references/crosslinks.md`](references/crosslinks.md).

**A refresh is not complete, and must not be reported complete, while any study-path step or course
material points at an artifact that no longer exists.** If a reference cannot be rewritten because
its replacement was quota-deferred, say so explicitly and **leave the old reference in place** —
a reference to a soon-to-be-regenerated artifact is recoverable; a reference to nothing is not.

### 5e. Write the ledger and the sidecar

1. Update `DERIVED.md`: new `artifact_id`s, new bases, new `generated` dates, `deferred` rows with
   their prompts.
2. Update the sidecar `README.md` tables (audio seasons, quizzes, video, study aids) to match, and
   add a dated setup-note entry describing what this run did and — as the existing entries do —
   **what it deliberately did not do, and why**.
3. **Sidecar writes go through Bash** (heredoc). The home-base `guard-sidecars` hook blocks
   `Write`/`Edit` under the NotebookLM root; Bash is the sanctioned path.

---

## Gates

- **Gate 1 — the costed plan** (Step 4). Covers execution of the approved plan.
- **Gate 2 — deletion, asked separately.** Deleting a superseded audio or video artifact is
  irreversible and needs Kyle's word on its own, never folded into Gate 1. `confirm=True` needs the
  user's word, not yours.
- **Gate 3 — syllabus changes re-enter `course-builder`'s gate.** Editing an existing lesson needs
  no new approval. **Adding or removing a lesson or module** is a syllabus change and goes through
  `course-builder`'s single approval gate, which owns that decision.

## Degradation — notebooks without a `MANIFEST.md`

Several sidecars (`stoicism`, `ai-stack`, `engineering-abstractions`) have no manifest, so no scope
hash can be computed.

- §1 rows record `scope` and `generated` but carry no basis, and status `unverified`.
- Staleness falls back to comparing `generated` against each in-scope source's `updated_at` from
  `notebook_describe`.
- **Say which mode the report used.** A date comparison is a weaker claim than a hash comparison —
  a source edited and reverted looks changed, and a source replaced with identical content looks
  changed. Reporting a date-based result in hash-grade language is the failure to avoid.
- Offer, but never perform unasked, the upgrade: building a manifest for that notebook is
  `portfolio-notebook-sync`-shaped work and out of scope here.

## `--new` — a chain that starts life with a ledger

1. **Notebook** — delegate to [[notebook-init]] (interview, source curation, creation, sidecar,
   INDEX entry).
2. **Audio series + study aids** — delegate to [[audio-series]], which owns the season design
   interview, the quota-aware waves, and the `Ep N —` mobile titling scheme.
3. **Course** — delegate to `course-builder`, including its single syllabus approval gate. Link the
   notebook in as a `notebooklm` material via that skill's "link an existing notebook" path, which
   costs no quota.
4. **Ledger** — write `DERIVED.md` from what the run just created. Scope and basis are known
   exactly here, so a `--new` chain has **zero** `unverified` rows. That is the whole argument for
   `--new` over assembling the pieces by hand.
5. **Study path** — offer, never assume. Generating one is out of scope for this skill.

---

## What this skill does NOT do

- **Does not onboard sources or projects** — `portfolio-notebook-sync --add` / `--add-paper`.
- **Does not create a `MANIFEST.md`** for a notebook that lacks one.
- **Does not generate study paths.**
- **Does not edit source repos**, including fixing a doc it notices is wrong.
- **Does not restate delegate mechanics** — no second copy of the quota model, the rename rule, or
  the course manifest schema. If a rule needs to change, it changes in the delegate.
- **Does not re-record audio outside the season policy** — no per-episode surgical re-record.

## Reference card — the gotchas this skill exists to encode

- **`DERIVED.md` is the contract.** Staleness is a hash comparison, never memory of a prior run.
- **Dirty source layer ⇒ stop.** Regenerating over stale sources bakes staleness into artifacts that
  then *look* current. This has already been caught by hand twice in this notebook's history.
- **`unverified` is treated as stale.** A guessed basis that later compares equal would certify
  staleness as freshness. Refusing to guess costs one regeneration and buys a trustworthy ledger.
- **Sorted scope, or permanent false drift.** An unsorted identifier list hashes differently every
  run.
- **Partial scope ⇒ no basis.** A hash computed over a partial input list looks authoritative and
  silently ignores an input. Mark `unverified` instead.
- **Season-level audio, staged across days.** 8 + 6 episodes against ~15/24h is a multi-day plan;
  discovering that mid-wave is the failure.
- **Rename only on `completed`** — delegated to [[audio-series]], but the refresh inherits it, and a
  wave with auto-titled artifacts left in it is not done.
- **Cross-link repair is terminal.** The portfolio study path hard-references artifact ids across 37
  steps; re-recording Season 1 invalidates eight of them at once.
- **Flashcard fronts are identities.** Rewording one resets its SM-2 schedule silently.
- **`studio_status` mis-reports mind maps as `flashcards`** with a bogus `flashcard_count`. Do not
  "correct" a known mind-map row from the live listing.
- **Sidecar writes go through Bash** — `guard-sidecars` blocks `Write`/`Edit` under the NotebookLM root.
