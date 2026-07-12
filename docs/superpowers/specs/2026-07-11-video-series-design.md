# video-series skill — design spec

**Date:** 2026-07-11
**Status:** Approved (workshop session)
**Structure decision:** Fork sibling of `audio-series` — standalone `skills/video-series/SKILL.md`, self-contained, sharing conventions by reference. No refactor of audio-series beyond a one-line sibling pointer.

## Purpose & jobs

Generate an episodic series of NotebookLM **video overviews** for an existing notebook — a flagship "building" season (Ep 1→N, each assumes the last) plus standalone episodes — with phone-legible titling, quota-aware batched generation, sidecar logging, and optional per-episode study aids.

Primary jobs (per interview):
1. **Visual-heavy learning** — material where seeing structure matters (schemas, architectures, SQL, math). Video shows what audio can't carry.
2. **Second-pass reinforcement** — a second modality over material that already has an audio season.

Explicitly NOT jobs: shareable/polished artifacts (no mp4 download flow), capability exploration.

## Tooling facts (verified in nlm-skill references)

- `studio_create(notebook_id, artifact_type="video", video_format=…, visual_style=…, focus_prompt=…, confirm=True)` — MCP-first, `nlm video create` CLI fallback.
- `video_format`: `explainer` (workhorse) | `brief` (short).
- `visual_style`: `auto_select`, `classic`, `whiteboard`, `kawaii`, `anime`, `watercolor`, `retro_print`, `heritage`, `paper_craft`.
- **Focus prompts are supported for video** — this is what makes sequential "assumes Eps 1–N" episodes possible.
- Documented generation time 3–7 min each; real-world may run longer.
- **Video quota/concurrency limits are undocumented** — unlike audio's empirically known rolling ~24h cap and ~11-concurrent ceiling. The skill must encode a reconnaissance posture, not assumed numbers.
- No video equivalent of audio's `debate`/`critique` formats.

## Workflow (deltas from audio-series in bold)

### 1. Identify the notebook
Unchanged from audio-series: alias / pick-from-list / most-recent; capture notebook_id, alias, sidecar path (`~/Projects/NotebookLMs/<alias>/`); back-fill sidecar if missing; pull existing artifacts for dedupe.

### 2. Interview
- Focus/weighting (free text) — unchanged.
- **Conditional branch — only when an existing audio season is detected** (via sidecar or artifact list): ask **Mirror / Complement / Fresh**.
  - **Mirror:** same Ep 1→N arc re-expressed visually; adapt the sidecar's existing episode focus prompts; episode count matches the audio season.
  - **Complement:** new arc covering what audio couldn't show; explicitly avoid topic overlap; lean into diagrams/schemas/structure.
  - **Fresh:** design independently; use the audio season only for title dedupe.
- Flagship season size: **default 4–6 episodes** (audio defaults 6–8) — video quota is scarcer and watching costs foreground attention.
- **Season visual style:** ask for ONE explicit style for the whole flagship season ("visual identity"). Never `auto_select` for series episodes — per-episode auto picks could break coherence. Standalones may vary.
- Format mix: `explainer` for series episodes and whole-topic standalones; `brief` for the micro/snackable tier. **No opinion lane** — point users wanting debate/critique to audio-series.
- Study aids (Study Guide + Quiz per episode): same question as audio-series, plus rule: **Mirror seasons skip study aids when the audio season already generated them** (same topics → duplicates).

### 3. Design the curriculum
Same shape as audio-series: read sources (`notebook_describe`) + existing artifacts; produce full plan (flagship + standalone tiers + recommended launch batch); **create nothing without an explicit go**. Optional thorough mode (ultracode fan-out: drafters per lane → editor) carried over.

Per-episode plan output: title, `video_format`, `visual_style`, focus_prompt, seriesOrder.

**New prompt guideline (video-only):** focus prompts should also direct the visual treatment — e.g. "show the schema as a diagram; walk the join step by step." Visuals are a promptable lever audio doesn't have.

**Titling:** identical to audio-series — series episodes `Ep N — <short topic>`, standalones `<short topic>`. Audio and video artifacts live in separate Studio-panel sections, so a Mirror season sharing titles with its audio twin is intentional pairing, not a collision. Sidecar disambiguates by medium.

### 4. Generate — reconnaissance quota posture
- **Smoke test first:** on any run where the sidecar has no prior video-quota observations, fire ONE video solo before batching: validates params, confirms rename-after-completion behavior matches audio's.
- Then **batches of 2–3**, poll to completion before the next batch: background `sleep` (`run_in_background:true`) → `TaskOutput(block:true)` → `studio_status`; `jq` the persisted status file (`studio_status` returns the whole notebook).
- Rename only AFTER completion (assume audio's auto-title-overwrite behavior until the smoke test confirms).
- Failure-diagnosis ladder (adapted from audio-series):
  1. Jobs in flight → concurrency; let them finish, retry overflow.
  2. Failure with 0 in flight → daily/rolling video quota. Diagnose, don't hammer: create a cheap non-video artifact (`mind_map`) to prove auth/server health; throwaway-notebook test to prove account-wide vs per-notebook; `notebook_delete` the throwaway.
  3. Defer blocked episodes to the sidecar with prompts intact; offer to re-fire later.
  4. `refresh_auth` only reloads cached tokens; stale login needs user-run `nlm login`.
- **Learn-and-encode loop:** log every quota-boundary observation (batch size, in-flight count, error text, timing) to a "Video quota observations" section in the sidecar. Once numbers are confirmed across runs, propose a PR updating this skill's reference card — claude-config is the skill's home, so the loop closes.
- Expectation-setting to the user: ~3–7+ min per video; a 5-episode season ≈ 30–45 min wall-clock. Keep polling; don't defer mid-run.

### 5. Study aids (if chosen)
Carried over verbatim from audio-series: `report`/Study Guide + `quiz` per episode via focus_prompt; text artifacts — no video quota, large batches fine, independent of whether the video exists yet. Titles `Ep N — Study Guide` / `Ep N — Quiz`. Mirror-season skip rule from §2 applies.

### 6. Sidecar logging
Same `~/Projects/NotebookLMs/<alias>/README.md` conventions ([[notebook-init]]):
- Video series table: Ep · title · **format** · **style** · status · artifact ID.
- Standalone backlog with verbatim focus prompts and ✅ markers.
- Study aids section (naming scheme + topic tags).
- Quota deferrals + **Video quota observations** (empirical log until confirmed).
- Refresh INDEX.md entry if scope changed.

## Reference card (gotchas the skill encodes)

- Video quota UNKNOWN: smoke-test 1 → batch 2–3 → observe → log → eventually PR confirmed numbers into the skill.
- Style = season identity: one explicit style per flagship season; never auto_select for series.
- Focus prompts direct visuals, not just content.
- No debate/critique formats → opinion content stays with audio-series.
- Mirror seasons: reuse the audio arc's titles (pairing is intentional); skip duplicate study aids.
- `Ep N —` mobile titling; rename only after completion; `jq` the persisted status file; nothing created without an explicit go.

## Out of scope

mp4 download flows · mixed-media seasons · one-off single videos (→ notebook-assist) · slides/infographics · any refactor of audio-series beyond the sibling-pointer line.

## Files touched (implementation)

1. `skills/video-series/SKILL.md` — new (the skill).
2. `skills/audio-series/SKILL.md` — add one sibling line to "When to use which sibling skill".

## Acceptance test

Supervised pilot on a real notebook: run the skill end-to-end — interview → plan → explicit go → solo smoke video → one batch of 2–3 → rename → sidecar update. The smoke-test-first order exists precisely so the first run is the test.
