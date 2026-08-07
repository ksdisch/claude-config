# `DERIVED.md` — the derivation ledger

Lives beside `MANIFEST.md` in the notebook's sidecar: `~/Projects/NotebookLMs/<alias>/DERIVED.md`.

**Division of labour, stated once.** `MANIFEST.md` answers *"is this source current?"*
`DERIVED.md` answers *"is what we made from that source current?"* Neither file's rows are
re-derived from scratch; both are read and diffed.

Two sections, because the two layers derive from different upstreams. A notebook artifact derives
from **notebook sources**. A course lesson derives from **the repos** — the hub course's prose was
authored from project cards, papers, and presenter packs, not from the notebook.

**All writes go through Bash** (heredoc). The home-base `guard-sidecars` hook blocks `Write`/`Edit`
under the NotebookLM root.

---

## Section 1 — notebook artifacts

```
| artifact | kind | artifact_id | scope | basis | generated | status |
```

| Column | Meaning |
|---|---|
| `artifact` | The display title as it exists in the notebook (`S2 Ep 4 — hush-gauge`). |
| `kind` | `audio` · `video` · `quiz` · `study_guide` · `flashcards` · `mind_map` |
| `artifact_id` | The NotebookLM artifact UUID. **The join key for cross-link repair.** |
| `scope` | The `source_ids` the artifact was generated from, or the literal `all`. |
| `basis` | The scope hash (below). Twelve hex characters, or `—` when uncomputable. |
| `generated` | ISO date the artifact was created or last regenerated. |
| `status` | `current` · `stale` · `unverified` · `deferred` |

**`scope` is what makes selective refresh possible at all.** An artifact scoped to three sources is
not stale because a fourth source moved. Where an artifact was deliberately scoped *away* from a
source, record that in a note under the table — this notebook's history contains exactly such a
case (`S2 Ep 4` was scoped to the README + paper + pack and deliberately **not** to the project
card, because the card was a milestone behind).

**`deferred`** means a planned regeneration was blocked by quota. Its verbatim focus prompt goes in
a `## Deferred` block below the table so the next run re-fires it without re-planning.

## Section 2 — course materials

```
| material | type | path | lesson_id | upstream | basis | generated |
```

| Column | Meaning |
|---|---|
| `material` | The material's title from `course.json`. |
| `type` | `lesson` · `exercise` · `flashcards` · `quiz` · `diagram` · `project` · `capstone` · `reading` · `notebooklm` |
| `path` | Course-relative path (`lessons/m3l2.md`); empty for the file-less types. |
| `lesson_id` | The owning lesson (`m3l2`) — a stale row maps to a re-authoring unit. |
| `upstream` | The doc set this material was authored from: absolute paths and/or repo blob references. |
| `basis` | Scope hash over that upstream set. |
| `generated` | ISO date. |

**`notebooklm` materials are a special case.** They reference a `notebook_id`, not an artifact, so
they do **not** go stale when artifacts are regenerated. Record `upstream` as the notebook alias and
treat the row as `current` unless the notebook id itself changes.

**`reading` materials** are external URLs. They have no local hash; record `upstream` as the URL and
leave `basis` as `—`. Their staleness is not this skill's problem.

---

## The scope hash — procedure

Written as numbered steps rather than a runnable block, deliberately: a shell block here would be
executed without its preconditions being read, and the preconditions are the point.

For **one** row:

1. **Resolve the row's identifier list and sort it.**
   - §1 rows: the `source_ids` in `scope`, sorted lexicographically.
   - §2 rows: the upstream paths / blob references, sorted lexicographically.

   **Sorted, always.** An unsorted list hashes differently on every run and reports permanent false
   drift on rows nobody touched.

2. **Look up each identifier's current content hash.**
   - §1 rows: read `sha256_12` from that source's row in `MANIFEST.md`. **Do not re-hash the source
     yourself.** `MANIFEST.md` is the contract for source state; a second hashing path is a second
     chance to disagree with it.
   - §2 rows, local file: hash the file on disk with SHA-256, first twelve hex characters.
   - §2 rows, repo blob on a default branch: follow `portfolio-notebook-sync`'s canonical `paper`
     read — every git command names its repo with `-C`, the blob is read from
     `origin/<default-branch>` (never the working tree, never a local branch), the read is
     redirected to a **fresh** temp file made for this one deliverable, and the hash is taken from
     that file.

     **If that read fails, stop for this row.** Do not hash, do not write a basis cell. Classify the
     row `unverified` and move to the next. This is a hard stop, not a warning — the same stop that
     has been dropped or written non-terminally four times in `portfolio-notebook-sync`'s review
     history.

3. **If any identifier has no hash available — a failed blob read, a deleted file — do not compute a
   basis.** Mark the row `unverified` and report it.

   A basis computed over a partial list is worse than no basis: it is a hash that looks
   authoritative and silently ignores an input.

   **One case is not `unverified` — it is definitive staleness.** A `source_id` in an artifact's
   scope that is **absent from `MANIFEST.md` entirely** does not mean "I couldn't hash it". It means
   that source was **deleted and replaced** — `portfolio-notebook-sync` repairs a changed source by
   `source_delete` + `source_add`, which mints a new id. The revision the artifact was generated
   from no longer exists in the notebook. Record `stale`, not `unverified`, and say which sources
   were replaced.

   This is a **stronger** signal than a hash mismatch, and it is the one that fires in practice: the
   2026-08-05 seven-row repair on the portfolio notebook left seven of the S2/standalone episodes
   pointing at ids that are gone.

4. **Concatenate the `(identifier, hash)` pairs in sorted order with a fixed separator, hash the
   result with SHA-256, take the first twelve hex characters.** That is the basis. Use the same
   separator every time; changing it invalidates every stored basis in the file.

### The staleness test

Recompute today and compare to the stored value:

| Outcome | Status |
|---|---|
| Equal | `current` |
| Different | `stale` |
| Uncomputable (step 3) | `unverified` — **treated as stale by `--refresh`** |
| The row's scope itself changed | `stale`, and the old basis is **void**, not "different" |

**Invariant — one basis, one scope.** A basis is only comparable to a basis computed over the same
scope. If an artifact's scope changed (a source was added to its `source_ids`), the stored basis
answers a different question. Mark the row `stale` and record the new scope when the artifact is
regenerated.

---

## `--adopt` — baselining a pair that predates the ledger

Required once per pair before `--refresh` is meaningful. Best-effort by design, and explicitly
honest about where it could not reconstruct the truth.

1. **Enumerate live notebook artifacts** (`studio_status`, or `notebook_describe`) and reconcile
   them against the sidecar `README.md` tables. Report **both** directions of mismatch:
   - a live artifact with no README row (created outside the recorded history), and
   - a README row with no live artifact (deleted out from under the record).

2. **Reconstruct `scope` per artifact** from what the sidecar records explicitly. The README's prose
   is the primary evidence — it records source-scoping decisions in sentences, not tables. Where
   scope is stated, use it. Where it is not, mark the row `unverified`; **do not infer scope from
   the artifact's title.**

3. **Compute a basis only for rows with a confidently reconstructed scope — and only when the basis
   would be honest.** Adopt computes hashes from **today's** manifest, but the artifact was generated
   at some **past** source state, so a naively computed basis can certify staleness as freshness.

   The date test that makes it honest, using `MANIFEST.md`'s `snapshot` column (the date the
   notebook's copy of that source was added) against the artifact's generation date `G`:

   | Condition | Meaning | Record |
   |---|---|---|
   | Any in-scope source has `snapshot` **after** `G` | The notebook's copy was replaced after the artifact was made | `stale`, **no basis** |
   | Every in-scope `snapshot` is **at or before** `G`, and all hashes currently match | The content the artifact was made from is still exactly what the notebook holds | `current`, basis is valid |
   | Any in-scope source currently mismatches the manifest | Upstream moved since the manifest last confirmed it | `stale`, no basis |

   Only the middle row earns a basis. This is what lets adopt say `current` about anything at all
   without inventing history.

4. **Take generation dates from the sidecar README, not from the API.** `studio_status.created_at`
   is not provenance — on the portfolio notebook it reports the Season 1 episodes as 2026-08-01 when
   the README records them created 2026-07-21 and never re-recorded, and stamps most artifacts with
   a date that appears nowhere in the sidecar's history. Treat it as a last-touched timestamp.

5. **Expect `source_ids` to be empty for non-audio types.** The API returns scope for audio and not
   for quizzes, reports, videos, mind maps, or flashcards — even when the sidecar states those
   artifacts *were* source-scoped. Those rows are `unverified` unless the sidecar records the scope
   explicitly. Do not infer scope from a title.

6. **Reconstruct §2 `upstream` per material** from `course.json` (the lesson's `reading` URLs and
   `notebooklm` links) plus the project the lesson is named for. A course whose modules map
   one-lesson-per-project reconstructs cleanly: `upstream` is that project's card plus its paper and
   presenter pack where those exist. Anything ambiguous is `unverified`.

7. **Write `DERIVED.md`** and report three counts separately: rows baselined with a real basis, rows
   marked `unverified`, and reconciliation mismatches. Do not blend them into one "adopted N rows"
   number.

**`unverified` is treated as stale by `--refresh`.** A guessed basis that later compares equal would
certify staleness as freshness. Refusing to guess costs one regeneration and buys a ledger that can
be trusted from then on.

### Two adopt-specific traps

- **`studio_status` mis-reports mind maps as `flashcards`**, with a bogus `flashcard_count`. The
  portfolio sidecar records this explicitly and names the affected ids. Trust the sidecar's recorded
  `kind` over the live listing; do not "correct" a known mind-map row.
- **Titles are not identities.** NotebookLM auto-titles artifacts on creation and they are renamed
  afterward. Match on `artifact_id` first, title second.

---

## File skeleton

```markdown
# DERIVED.md — <notebook title>

Notebook: <notebook_id> · alias `<alias>`
Course: <slug> (<COURSES_DIR>/<slug>)
Upstream contract: MANIFEST.md   ·   Maintained by: the `curriculum-sync` skill
Last run: <ISO date> (<mode>)

## §1 Notebook artifacts

| artifact | kind | artifact_id | scope | basis | generated | status |
|---|---|---|---|---|---|---|

### Scope notes
<deliberate scope exclusions, one line each, with the reason>

### Deferred
<title · kind · verbatim focus_prompt · source_ids · date deferred>

## §2 Course materials

| material | type | path | lesson_id | upstream | basis | generated |
|---|---|---|---|---|---|---|

### Unverified rows
<row · why the basis could not be computed>
```
