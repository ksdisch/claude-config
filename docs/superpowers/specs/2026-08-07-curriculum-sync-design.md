# `curriculum-sync` — design spec

**Written:** 2026-08-07 · **Status:** approved by Kyle 2026-08-07 (brainstorm → design → this spec)
**Deliverable:** a new global skill at `skills/curriculum-sync/`, plus its reference-doc row and
usage-playbook card.

---

## 1. The problem

Kyle's learning material is a four-link chain, and only the first link is machine-checked:

```
~/Projects/<repo>   →   notebook sources   →   notebook artifacts    →   home-base course
   (git)                 MANIFEST.md            DERIVED.md §1             DERIVED.md §2
                         EXISTS today           NEW (this spec)           NEW (this spec)
```

`portfolio-notebook-sync` keeps link 1 → 2 honest: `MANIFEST.md` records what every notebook
source was made from and the content hash it was made at, so source drift is a hash comparison,
never a judgment call.

Everything **downstream** of the source layer is judged by hand. The evidence is in the sidecar's
own prose:

- `~/Projects/NotebookLMs/research-portfolio-prep/README.md`: *"Season 1 results did not change, so
  it was not re-recorded."*
- Same file: *"Study aids were NOT regenerated — the source layer is not clean (see MANIFEST's two
  ⚠️ notes), and regenerating now would bake that staleness into four fresh artifacts."*
- Same file: *"Study aids and episodes were NOT regenerated — they predate the hush-gauge M1
  results; regeneration is Kyle's call."*

Those are all correct decisions, and none of them is reproducible. There is no record of **what
each derived artifact was generated from, at what source state** — so every refresh re-derives that
question from scratch, and the answer degrades as memory of the run fades.

The concrete trigger: portfolio projects were updated after the audio series, its study aids, and
the `research-portfolio` home-base course were generated. All three are now stale by an unknown
amount.

## 2. What `curriculum-sync` is

A **thin orchestrator** that owns exactly three things nothing else owns:

1. the **derivation ledger** (`DERIVED.md`),
2. the **staleness diff** computed from it,
3. the **gates** around acting on that diff.

Execution delegates outward and restates none of the delegates' hard-won mechanics:

| Layer | Delegate | What the delegate owns |
|---|---|---|
| Sources | `portfolio-notebook-sync` | `MANIFEST.md`, hash procedure, the read-only-git rules, `--add` |
| Audio / video | `audio-series`, `video-series` | Quota model, wave batching, poll-to-completion, the rename-after-`completed` rule |
| Course | `course-builder` (home-base) | Manifest schema, the `cli write` validate-and-roll-back bridge, pedagogy contract |
| Notebook creation | `notebook-init` | Sidecar template, INDEX entry, source curation |

The orchestrator never reimplements a delegate's rules. Where it needs one, it names the skill and
the rule, so there is one copy of each gotcha.

**Scope:** generic — any notebook paired with a home-base course. Three such pairs exist today
(`research-portfolio-prep` ↔ `research-portfolio`, `jlens-workspace` ↔ `jlens-global-workspace`,
and the `sql-analytics-interview-prep` course). Results are sharpest for pairs that already have a
`MANIFEST.md`; §6 defines the honest degradation for those that don't.

## 3. `DERIVED.md` — the ledger

Lives beside `MANIFEST.md` in the notebook's sidecar: `~/Projects/NotebookLMs/<alias>/DERIVED.md`.

**Division of labour, stated once:** `MANIFEST.md` answers *"is this source current?"*. `DERIVED.md`
answers *"is what we made from that source current?"*. Neither file's rows are re-derived from
scratch; both are read and diffed.

The file has two sections because the two layers derive from different upstreams. A notebook
artifact derives from **notebook sources**. A course lesson derives from **the repos** — the hub
course's prose was authored from project cards, papers, and presenter packs, not from the notebook.

### 3.1 Section 1 — notebook artifacts

```
| artifact | kind | artifact_id | scope | basis | generated | status |
```

- **`artifact`** — the display title as it exists in the notebook (`S2 Ep 4 — hush-gauge`).
- **`kind`** — `audio` | `video` | `quiz` | `study_guide` | `flashcards` | `mind_map`.
- **`artifact_id`** — the NotebookLM artifact UUID. This is the join key for cross-link repair (§7).
- **`scope`** — the `source_ids` the artifact was generated from, or the literal `all` when the
  whole notebook was in scope. This column is what makes selective refresh possible: an artifact
  scoped to three sources is not stale because a fourth source moved.
- **`basis`** — the **scope hash** (§3.3). Twelve hex characters.
- **`generated`** — ISO date the artifact was created or last regenerated.
- **`status`** — `current` | `stale` | `unverified` | `deferred`. `unverified` means the row was
  adopted (§5.2) without a confidently reconstructable basis. `deferred` means a planned
  regeneration was blocked by quota and its focus prompt is recorded below the table.

### 3.2 Section 2 — course materials

```
| material | type | path | lesson_id | upstream | basis | generated |
```

- **`material`** — the material's title from `course.json`.
- **`type`** — `lesson` | `exercise` | `flashcards` | `quiz` | `diagram` | `project` | `capstone` |
  `reading` | `notebooklm`.
- **`path`** — course-relative path (`lessons/m3l2.md`), or empty for the file-less types
  (`reading`, `notebooklm`).
- **`lesson_id`** — the owning lesson (`m3l2`), so a stale row maps to a re-authoring unit.
- **`upstream`** — the doc set this material was authored from, as absolute paths or repo blob
  references (e.g. `portfolio/projects/decay-pin.md` + `decay-pin:docs/paper/decay-pin.md@main`).
- **`basis`** — the scope hash over that upstream set (§3.3).
- **`generated`** — ISO date.

A `notebooklm` material is a special case: it references a `notebook_id`, not an artifact, so it
does not go stale when artifacts are regenerated. It goes stale only if the notebook itself is
replaced. Record it with `upstream` = the notebook alias and treat it as `current` unless the
notebook id changes.

### 3.3 The scope hash — procedure

Stated as numbered steps rather than a copy-pasteable command, deliberately. A shell block here
would be executed without its preconditions being read, and the preconditions are the whole point.

For **one** row:

1. Resolve the row's `scope` (§3.1) or `upstream` (§3.2) into an explicit, **sorted** list of
   identifiers. Sorted, because an unsorted list hashes differently on every run and would report
   permanent false drift.
   - §1 rows: sort the `source_ids` lexicographically.
   - §2 rows: sort the upstream paths/blob references lexicographically.
2. For each identifier in that list, look up its current content hash:
   - §1 rows: read `sha256_12` from that source's row in `MANIFEST.md`. **Do not re-hash the
     source yourself** — `MANIFEST.md` is the contract for source state, and a second hashing path
     is a second chance to disagree with it.
   - §2 rows: hash the upstream doc. Local files hash from disk. Repo blobs on a default branch
     follow `portfolio-notebook-sync`'s canonical `paper` read — `git -C <repo> show
     origin/<branch>:<path>` redirected to a fresh temp file, and **if that read fails, stop for
     this row**: classify it `unchecked`, write no basis cell, move to the next row.
3. If **any** identifier in the list has no hash available — a missing `MANIFEST.md` row, a failed
   blob read — the row's basis is **not** computed. Mark it `unverified` and report it. A basis
   computed over a partial list is worse than no basis: it is a hash that looks authoritative and
   silently ignores an input.
4. Concatenate the `(identifier, hash)` pairs in sorted order with a fixed separator, hash the
   result with SHA-256, and take the first twelve hex characters. That is the basis.

**The staleness test:** recompute the basis today and compare it to the stored one. Equal →
`current`. Different → `stale`. Uncomputable → `unverified`, which the refresh lane treats as stale
rather than trusting it.

**Invariant — one basis, one scope.** A row's basis is only comparable to a basis computed over the
same scope. If an artifact's scope changes (a source was added to its `source_ids`), the old basis
is not "different", it is **void** — mark the row `stale`, and record the new scope when the
artifact is regenerated.

### 3.4 Sidecar writes go through Bash

The home-base `guard-sidecars` hook blocks `Write`/`Edit` under the NotebookLM root. Every
`DERIVED.md` write uses Bash (heredoc), exactly as `portfolio-notebook-sync` does for
`MANIFEST.md`. This is not a style preference; the direct-write path is blocked and will fail.

## 4. Modes, and the walls between them

| Mode | Invocation | Does |
|---|---|---|
| **Drift check** | bare | Read-only. Computes the staleness table across both layers and reports. |
| **Adopt** | `--adopt` | Backfills `DERIVED.md` for a pair that predates the ledger. |
| **Refresh** | `--refresh` | Executes the refresh for what the check found stale, behind gates. |
| **New** | `--new` | Builds a fresh chain end to end and writes the ledger from birth. |

The walls are borrowed in spirit from `portfolio-notebook-sync`, which earned them:

- **A drift check never generates, deletes, or writes.** It may create `DERIVED.md` only under
  `--adopt`, never under a bare run.
- **`--refresh` never onboards.** Noticing a project with no notebook source, or a project with no
  course module, is a **finding to report**. Adding a source is `portfolio-notebook-sync --add`'s
  job; adding a lesson is a syllabus change (§5.3, gate 3). Silently growing the corpus during a
  "refresh" is the failure this wall prevents.
- **`--new` never touches an existing notebook.** If the alias resolves to a live notebook, stop
  and say so.
- **No mode changes git state in a source repo.** Read-only git is required (`rev-parse`, `show`,
  `ls-tree`, `log`, `status`), plus the one sanctioned exception `portfolio-notebook-sync` already
  defines: `git -C <repo> fetch --no-write-fetch-head origin <default-branch>`, because Kyle merges
  on GitHub and a local ref does not advance on its own. `pull` stays forbidden.
- **No mode edits a source repo's files.** A wrong README is a finding, not a fix.

## 5. The refresh lane

### 5.1 Order is not negotiable — top-down, and it stops on a dirty floor

1. **Source layer first.** Run the source-layer drift check (delegate to `portfolio-notebook-sync`
   bare for the portfolio pair; for other notebooks, compare `MANIFEST.md` if one exists).

   **Hard gate: never regenerate onto an unclean source layer.** If any source row is `changed`,
   `deleted`, or `unchecked`, the refresh stops and reports. Repairing sources is
   `portfolio-notebook-sync`'s job and needs its own confirm; only once the source layer reports
   clean does the derived refresh proceed. This is Kyle's own recorded decision from 2026-08-05
   promoted to a rule — regenerating over dirty sources bakes the staleness into fresh artifacts,
   which is strictly worse than leaving them stale, because the new artifacts *look* current.

2. **Cheap text artifacts** — study guides, quizzes, flashcards, mind maps. No audio quota, and
   they tolerate large concurrent batches. Regenerate every `stale` and `unverified` §1 row of
   these kinds in one or two waves.

   Carry `audio-series`' recorded lesson: **`focus_prompt` alone does not steer `report` or
   `mind_map` generation.** Scope those by `source_ids` or they come back about the wrong material.

3. **Audio and video — season-level re-record.** Kyle's chosen policy (2026-08-07): if any source
   behind a season moved, the **whole season** is re-recorded, for internal consistency across
   episodes that reference each other.

   The plan step does the quota arithmetic **before** anything fires and stages it across days.
   Concretely, for the portfolio notebook today: Season 1 is 8 episodes, Season 2 is 6, against an
   observed rolling ~15-per-24h **account-wide** cap. Two seasons do not fit in one window with any
   retry headroom, so a two-season refresh is a multi-day plan and must be presented as one.

   All wave mechanics delegate to `audio-series` and are **not** restated here: batch ~5–6, poll to
   completion, and rename only on `status:"completed"` (an early rename is overwritten by
   NotebookLM's auto-title). Quota-blocked episodes are logged as `deferred` rows in `DERIVED.md`
   with their verbatim focus prompts, so the next run re-fires what is left instead of re-planning.

4. **Course materials.** Re-author only the lessons whose §2 basis moved, then commit through
   `cd backend && .venv/bin/python -m app.courses.cli write --slug <slug> --from-file <manifest>` —
   it validates atomically and rolls back on failure. Per `course-builder`'s update-in-place rule,
   stale material files the new manifest no longer references are **not** auto-removed; delete them
   so the directory matches the manifest.

   **Minimal-diff rule.** Preserve flashcard fronts and quiz stems wherever the underlying fact did
   not change. A flashcard's front text **is** its identity in the hub's per-card SM-2 store, so
   rewording a front that didn't need rewording silently resets that card's review schedule. Change
   the back, the rationale, or the numbers freely; change a front only when the card is genuinely
   about something else now.

5. **Cross-link repair — mandatory and terminal** (§7).

### 5.2 `--adopt` — baselining what already exists

Required once per pair before `--refresh` is meaningful, because the portfolio pair predates the
ledger by design. Best-effort, and explicitly honest about its limits:

1. Enumerate live notebook artifacts (`studio_status`, or `notebook_describe`) and reconcile them
   against the sidecar README's tables. Report both directions of mismatch — an artifact in the
   notebook with no README row, and a README row with no live artifact.
2. For each artifact, reconstruct `scope` from the README's recorded prose where it is explicit
   (the portfolio README records, for instance, that `S2 Ep 4 — hush-gauge` was scoped to the
   README + paper + pack and deliberately **not** to the card, and that the study guide and mind
   map were scoped to portfolio docs). Where scope is not recorded, mark the row `unverified`.
3. Compute a basis only for rows with a confidently reconstructed scope. Every other row gets
   `status: unverified` and **no** basis cell.
4. For §2, reconstruct `upstream` per lesson from `course.json` (the lesson's `reading` URLs and
   `notebooklm` links) plus the project the lesson is named for. The `research-portfolio` course
   maps cleanly — each of m2–m4's lessons is named for one project — so `upstream` is that
   project's card plus its paper/pack where one exists. Anything ambiguous is `unverified`.
5. Write `DERIVED.md`, and report the counts three ways: rows baselined with a real basis, rows
   marked `unverified`, and reconciliation mismatches.

**`unverified` is treated as stale by `--refresh`.** A guessed basis that later compares equal
would certify staleness as freshness; refusing to guess costs one regeneration and buys a ledger
that can be trusted from then on.

Known adopt scale for the portfolio pair: roughly 32 notebook artifacts (8 + 6 audio, 12 quizzes,
4 video, 4 study aids) and roughly 60 course materials across 5 modules / 15 lessons.

### 5.3 Gates

- **Gate 1 — the plan gate (the load-bearing one).** Present the full staleness table for both
  layers plus a **costed** plan: how many audio/video generations, against how much quota, which
  day each wave lands on, what will be deleted, and which cross-links will be rewritten. One
  explicit go-ahead covers execution of that plan.
- **Gate 2 — deletion, asked separately.** Deleting a superseded audio/video artifact is
  irreversible and needs Kyle's word on its own, not folded into gate 1. This matches
  `audio-series`' existing stance (`confirm=True` needs the user's word, not the assistant's).
- **Gate 3 — syllabus changes re-enter `course-builder`'s gate.** Editing an existing lesson needs
  no new approval; **adding or removing a lesson or module** is a syllabus change and goes through
  `course-builder`'s single approval gate, which owns that decision.

## 6. Honest degradation for notebooks without a `MANIFEST.md`

`stoicism`, `ai-stack`, `engineering-abstractions` and others have sidecars but no manifest, so
§3.3 step 2 has nothing to read and no scope hash can be computed.

In that case:

- §1 rows record `scope` and `generated` but carry `basis: —` and `status: unverified`.
- Staleness falls back to comparing `generated` against each in-scope source's `updated_at` from
  `notebook_describe`.
- **The report must say which mode it used.** A date comparison is a weaker claim than a hash
  comparison — a source edited and reverted looks changed, and a source replaced with identical
  content looks changed. Reporting a date-based result in hash-grade language is the failure mode
  to avoid.
- Offer, but never perform unasked, the upgrade path: a manifest for that notebook is
  `portfolio-notebook-sync`-shaped work and is out of scope for this skill.

## 7. Cross-link repair

Regenerating an artifact mints a **new** `artifact_id`. Two places in home-base hard-reference
those IDs, and both break silently:

1. **The study path** — `home-base/backend/data/paths/<notebook_id>.json`. The portfolio one is a
   hand-authored 37-step path whose steps carry `artifact_id` fields (verified 2026-08-07:
   `bec82da6…`, `d1352488…`, `58cc6ca1…`, and so on across all 32 artifacts). Re-recording Season 1
   invalidates eight of those steps at once.
2. **`course.json`** — `notebooklm` materials reference a `notebook_id` (which is stable across
   artifact regeneration, so these usually survive) and may optionally name an `artifact`.

The procedure:

1. **Before** superseding any artifact, search the paths directory and `course.json` for its
   `artifact_id`, and record every hit alongside the artifact's `DERIVED.md` row.
2. Regenerate.
3. Rewrite each recorded reference to the new ID.
4. Re-validate the course through the `cli write` bridge if `course.json` changed.

**This step is terminal, in `audio-series`' sense of the word.** A refresh is not complete — and
must not be reported complete — while any study-path step or course material points at an artifact
that no longer exists. If a reference cannot be rewritten (the new artifact was quota-deferred),
say so explicitly and leave the old reference in place rather than pointing it at nothing.

## 8. The `--new` lane

Builds a chain that starts life with a ledger:

1. **Notebook** — delegate to `notebook-init` (interview, source curation, creation, sidecar,
   INDEX entry). If the user names an existing notebook instead, this is not `--new`; route to
   `--adopt`.
2. **Audio series + study aids** — delegate to `audio-series`, which owns the season design
   interview, the quota-aware waves, and the `Ep N —` mobile titling scheme.
3. **Course** — delegate to `course-builder`, including its single syllabus approval gate. Link the
   notebook into the course as a `notebooklm` material, per `course-builder`'s §5 path 1 (link an
   existing notebook — no quota).
4. **Ledger** — write `DERIVED.md` from what the run just created. Scope and basis are known
   exactly here, so a `--new` chain has **zero** `unverified` rows. That is the argument for using
   `--new` rather than assembling the pieces by hand.
5. **Study path** — optional and offered, never assumed. Note that the portfolio path was
   hand-authored; generating one is not in scope for this spec.

## 9. Files delivered

| File | Contents |
|---|---|
| `skills/curriculum-sync/SKILL.md` | Modes, walls, chain order, gates, delegation contract, reference card |
| `skills/curriculum-sync/references/ledger.md` | `DERIVED.md` format, the basis-hash procedure, the adopt procedure |
| `skills/curriculum-sync/references/crosslinks.md` | Study-path + `course.json` reference repair |
| `docs/command-skill-reference.md` | One row under Global Skills |
| `docs/usage-playbook.md` | One card: Run config · Reach for it when · Pairs well with |

The reference-doc row and the playbook card ship **in the same commit** as the skill — the repo's
tracked `pre-push` hook (`scripts/check-doc-sync.py`) blocks the push otherwise.

**Authoring constraint:** procedures are written as numbered steps with named invariants, **not**
copy-pasteable shell. Kyle's standing finding (21 review rounds' worth of evidence) is that shell
snippets in skill files are a defect generator — they get executed without their preconditions
being read, and a non-terminal failure arm in a snippet has already caused four separate defects in
`portfolio-notebook-sync`. Name the command and its repo-scoping flags in prose; do not hand over a
block that runs.

## 10. Non-goals

- **Does not onboard sources or projects.** That is `portfolio-notebook-sync --add` /
  `--add-paper`.
- **Does not create a `MANIFEST.md`** for a notebook that lacks one.
- **Does not generate study paths.**
- **Does not edit source repos**, including fixing a doc it notices is wrong.
- **Does not restate delegate mechanics** — no second copy of the quota model, the rename rule, or
  the course manifest schema.
- **Does not re-record audio outside the season policy** — no per-episode surgical re-record; Kyle
  chose season-level consistency.

## 11. Risks and open items

- **The season policy is quota-expensive by construction.** 8 + 6 episodes against ~15/24h means a
  full portfolio refresh spans at least two days, with essentially no retry headroom on day one.
  Accepted deliberately for cross-episode consistency; mitigated by staging the plan across days
  and by `deferred` rows that make resumption cheap.
- **Adopt is best-effort.** Some portfolio rows will land `unverified` and cost one regeneration to
  clear. Accepted over guessing a basis.
- **Course quiz/flashcard identity is fragile.** The minimal-diff rule (§5.1 step 4) is a discipline
  a re-authoring subagent can violate; the fan-out payload must carry it verbatim.
- **`studio_status` mis-reports mind maps as `flashcards`** with a bogus `flashcard_count` — the
  portfolio README records this explicitly. Adopt must not "correct" a known mind-map row from the
  live listing.
- **Untested against a second pair.** The design is generic, but only the portfolio pair has been
  examined in depth. The `jlens-workspace` ↔ `jlens-global-workspace` pair is the natural second
  test and may surface shape assumptions this spec does not know it is making.

---

**Run-config note.** Build this on **Opus 5** at **`high`** effort — the spec is settled, so this is
well-specified build work with real judgment inside it (the ledger format and the wall/gate wording
carry the weight), not a design exercise and not mechanical. Start the builder session **fresh from
this file**, not from the brainstorming transcript.

```
claude --model claude-opus-5 --effort high
```
