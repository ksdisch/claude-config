# Cross-link repair

Regenerating a NotebookLM artifact does not update it in place — it mints a **new**
`artifact_id` and leaves the old one dead. Two places in home-base hard-reference those ids, and
both break silently: nothing errors, the step or card simply stops resolving.

**This repair is terminal.** A refresh is not complete, and must not be reported complete, while any
reference points at an artifact that no longer exists.

---

## The two reference sites

### 1. The study path — `home-base/backend/data/paths/<notebook_id>.json`

A hand-authored phased spine over a notebook's artifacts. Steps carry `artifact_id` fields.

Scale, for the portfolio notebook (verified 2026-08-07): **37 steps over 32 artifacts.**
Re-recording Season 1 alone invalidates **eight** steps at once. This file is hand-authored — it is
not regenerable, so a broken reference is real lost work, not a rebuild.

Step kinds that carry an `artifact_id` include audio, quiz, video, and mindmap steps. Do not assume
the set; search the file for the id.

### 2. `course.json` — `notebooklm` materials

A `notebooklm` material references a `notebook_id`, which is **stable** across artifact
regeneration, so these usually survive untouched. A material may additionally name an `artifact`
kind or id; that part does need checking.

The hub renders a `notebooklm` material as a live cross-link only when the `notebook_id` resolves in
the machine's sidecar catalog. Elsewhere it degrades to the material's `note` — which is why
`course-builder` requires every such material to carry a `note` that stands alone.

---

## Procedure

1. **Before superseding any artifact**, search both sites for its `artifact_id` and record every hit
   next to that artifact's `DERIVED.md` row. Do this *first* — once the artifact is deleted, the
   only record that a step pointed at it is the step itself, and by then you are searching for a
   string with no meaning.

   Search the whole paths directory, not just the file named for this notebook. A path file for one
   notebook can legitimately reference another notebook's artifact.

2. **Regenerate** (Step 5b of the skill).

3. **Rewrite each recorded reference** to the new id. Match old → new by the artifact's *role* — the
   episode that replaced `Ep 3 — forge-gap` is the new `Ep 3 — forge-gap` — not by position in a
   listing, which reorders.

4. **Re-validate.** If `course.json` changed, commit it through `course-builder`'s CLI `write`
   bridge so it is validated and rolled back on failure. If a path JSON changed, confirm the hub
   still loads the path.

5. **Verify no dead references remain.** Search both sites for every superseded id. Zero hits, or
   the refresh is not done.

---

## When a replacement does not exist

Quota defers episodes. A deferred episode has no new id to point at.

**Leave the old reference in place.** Do not null it, do not delete the step, do not point it at a
neighbouring episode.

- A reference to a soon-to-be-regenerated artifact is recoverable — the next run finishes the job.
- A reference to nothing is not recoverable, and a deleted step takes hand-authored prose with it.

Report every such reference explicitly in the run summary, alongside the `deferred` row in
`DERIVED.md` that will clear it.

## Ordering constraint

**Never delete a superseded artifact before its replacement exists and its references are
rewritten.** Deletion is Gate 2 and is asked separately anyway; the ordering makes the gate safe to
answer "yes" to — at the moment Kyle approves a deletion, nothing depends on the artifact any more.
