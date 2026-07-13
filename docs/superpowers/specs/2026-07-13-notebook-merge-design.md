# notebook-merge skill — design spec

**Date:** 2026-07-13
**Status:** Approved (workshop session)
**Structure decision:** One phased skill (`skills/notebook-merge/SKILL.md`) with a single plan gate and a separate destructive-op gate. N-way native: merges **2+ notebooks in one pass**.

## Purpose & jobs

Kyle's notebooks accumulate crossover (e.g., the global-workspace paper notebook and the forge-gap paper notebook). This skill integrates N (≥2) existing NotebookLM notebooks into one unified notebook end-to-end:
- migrate sources (all, or strategically selected)
- migrate notes
- regenerate the Studio artifacts worth keeping and propose new cross-notebook ones
- archive (and optionally delete, behind a gate) the originals
- keep sidecars + INDEX.md truthful throughout

Chaining (merging a new notebook into a previously merged one later) is just another run with N=2 — the skill does not need special support for it.

## Interview decisions (locked)

1. **Topology — ask per run, skill recommends.** Absorb into the richest notebook when one clearly dominates; create a new umbrella notebook when contributions are comparable or the merged identity is new. With N≥3, recommend the umbrella by default. User confirms.
2. **Artifacts — curated menu of both lists.** (1) *Recreate*: old artifacts re-fired from recorded focus prompts. (2) *Synthesize*: 3–5 proposed NEW cross-notebook artifacts only the merged notebook makes possible. Nothing regenerates without the go.
3. **Originals — archive-rename, offer delete.** Rename to `[MERGED → <alias>] <old title>`, mark sidecars/INDEX; deletion only behind an explicit per-notebook confirm that lists what dies with it.
4. **Source modes — All vs Strategic** (from the original request); strategic selection becomes mandatory when the union exceeds the notebook source cap.

## Tooling facts (verified in nlm-skill / notebook-init)

- **No copy API — sources move by re-adding, per type:**
  | Origin type | Transfer method | Fidelity |
  |---|---|---|
  | URL / YouTube | `source_add(source_type="url", url=…)` (URL from `source list --url` / sidecar) | Perfect (re-fetched) |
  | Drive doc | `source_add(source_type="drive", document_id=…)` | Perfect (stays synced) |
  | Pasted text | `source content <id>` → `source_add(source_type="text", title=<same>)` | Perfect |
  | Uploaded file | Prefer local original from sidecar `sources/` staging dir → `source_add(source_type="file")`; else `source content` → text re-add | Fallback loses formatting/media — flag in manifest |
- **Artifacts cannot be copied — only regenerated** (`studio_create`). Sidecars record the focus prompts that built them (notebook-init/audio-series/video-series conventions).
- **Notes** migrate via `note` list → `note_create` (cheap text).
- **`cross_notebook_query` is N-native** (`notebook_names="A, B, C"`, `tags=…`, `all=True`) — powers the overlap/complement analysis.
- **Rate limits:** 2s between source adds; 5s between generation calls (notebook-init).
- **Source cap per notebook:** ~50 (free) / ~300 (Pro) — treat as approximate; check the union count at runtime and surface it in the plan.
- **Silent add failures happen** (Medium.com, paywalled URLs) — verify count parity, retry stragglers, log failures (notebook-init pattern).
- Sidecar template fields available: frontmatter (notebook_id, alias, tags, profile), Sources table, Artifacts table, Setup notes with prompts, `sources/` + `artifacts/` dirs.

## Workflow

### Phase 0 — Preflight & selection
- Auth (`server_info` / `nlm login --check`), profile pick if >1.
- Select **2+ notebooks** via: aliases / pick-from-list (10 most recent) / **by tag** (e.g. "everything tagged `ai-papers`"). Confirm the final set.
- Load each notebook's sidecar (back-fill from `notebook_describe` per audio-series convention if missing); pull source lists, artifact inventories (`studio_status`), and notes.
- Compute union source count; compare to the plan cap.

### Phase 1 — Inventory & analysis
- **Union source manifest:** # · title · type · URL/path · origin notebook · overlap flag · fidelity note. Overlap = exact URL match, fuzzy title match.
- Optional thematic pass: `cross_notebook_query` over the selected set ("what themes do these share / where do they diverge?") to inform strategic selection and the synthesize list.
- **Artifact inventory** split: *recorded prompt available* (recreate-able verbatim) vs *unknown provenance* (needs fresh prompt, goes to synthesize list instead).
- Notes inventory.

### Phase 2 — Merge plan (the single creation gate)
One plan presented for one explicit go:
- **Topology recommendation** + reasoning (absorb vs new umbrella; umbrella default at N≥3). New-umbrella path proposes title/alias/tags (union) via notebook-init conventions.
- **Union count vs cap**, prominently; over cap → strategic selection required.
- **Source mode:** All / Strategic. Strategic reuses notebook-init value tiers with preset selection (Everything / Dedupe-only / High-value only / hand-pick by number — AskUserQuestion is capped at 4 options; hand-pick collects indices as free text).
- **Artifact menu:** *Recreate* list (recorded prompts, adapted titles; exclude whole-notebook artifacts like generic Briefing Docs — re-synthesize those over the union instead; in absorb topology the survivor's artifacts are already live, so the list covers only the non-survivors') and *Synthesize* list (3–5 proposals: bridge deep-dive, comparative report, combined mind map, …).
- **Disposal preview:** what will be archive-renamed; deletion decision deferred to Phase 5.
**Create nothing before the go.**

### Phase 3 — Migrate
- New-umbrella path: `notebook_create` → `nlm alias set` → tags → `chat_configure`, then add ALL selected sources. Absorb path: add only the non-survivor notebooks' selected sources.
- Per-type transfer per the matrix; 2s spacing; then **verify count parity** (planned vs present), retry stragglers once, log failures to the sidecar.
- Migrate notes (`note_create` each).

### Phase 4 — Regenerate artifacts (quota-aware)
- Text artifacts (reports, quizzes, flashcards, mind maps, data tables): big concurrent batches — no audio/video quota.
- Audio: follow [[audio-series]] reference card (batch 5–6, ~11-concurrency ceiling, rolling ~24h account quota, poll-to-completion, rename only after completion, `Ep N —` titling if serialized).
- Video: follow [[video-series]] recon posture (solo smoke if no prior observations, batch 2–3, log quota observations).
- Quota-blocked items → sidecar backlog with verbatim prompts (defer, don't hammer).
- A whole NEW season for the merged notebook is out of scope here — route to [[audio-series]] / [[video-series]] after the merge.

### Phase 5 — Archive & disposal
- Rename each original `[MERGED → <alias>] <old title>` (`notebook_rename`); update its sidecar (status + merged-into pointer) and INDEX.md entry.
- **Delete gate, per notebook:** explicit AskUserQuestion listing exactly what dies (any artifact NOT recreated in Phase 4). Default = keep archived. The skill never deletes without this per-notebook confirm.

### Phase 6 — Verify & summarize
- Source count parity re-check; one spot-check chat query whose answer must ground in content from **each** origin notebook.
- New/updated sidecar: provenance header ("merged from <A>, <B>, … on YYYY-MM-DD"), full manifest with per-source outcome, artifact log, backlog/deferrals. INDEX.md entry for the merged notebook.
- Summary: notebook URL, alias, sidecar path, what's backlogged.

## Error handling
- Auth expiry mid-flow → pause, user runs `nlm login`, resume.
- Silent source-add failures → count parity + one retry + sidecar log (never silently proceed).
- Quota failures mid-regeneration → sibling skills' diagnosis ladders; defer to backlog.
- Abort mid-flow → write sidecar capturing completed state (notebook-init pattern); originals untouched until Phase 5.
- Union over source cap and user insists on Everything → hard stop with the numbers; NotebookLM will reject the overflow anyway.

## Reference card (gotchas the skill encodes)
- Sources move by re-adding (type matrix above); uploaded files prefer the sidecar `sources/` original; text-extract fallback is flagged fidelity loss.
- Artifacts regenerate from recorded prompts — sidecars are the memory; artifacts with no recorded prompt go to the synthesize list.
- Deleting an original kills its un-recreated artifacts — the delete gate must list them.
- One creation gate (Phase 2), one destructive gate per notebook (Phase 5); nothing outward without them.
- Union cap check before anything; strategic selection is the pressure valve.
- 2s add spacing; count-parity verification; Medium/paywalled URLs fail silently.
- Cross-notebook synthesis artifacts are the merge's payoff — always propose some.

## Out of scope
Artifact download/export · merging sidecar git history · Google-Drive-native file copying · special chaining support (a later fold-in is just another N=2 run) · new season design (routes to audio-series / video-series).

## Files touched (implementation)
1. `skills/notebook-merge/SKILL.md` — new (the skill).
2. `skills/notebook-assist/SKILL.md` — one sibling-pointer line (merge requests route here, not to its source-management mode).

## Acceptance test
Supervised pilot merging Kyle's real pair — the global-workspace notebook + the forge-gap notebook — through all phases, with the delete gate exercised but defaulting to keep-archived.
