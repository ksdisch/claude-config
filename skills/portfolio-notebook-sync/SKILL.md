---
name: portfolio-notebook-sync
description: Use when the research-portfolio NotebookLM notebook (alias `research-portfolio-prep`) may have fallen out of step with `~/Projects/portfolio`, or when a portfolio project has just been carded and belongs in it. Triggers on "sync the portfolio notebook", "add <project> to the portfolio notebook", "is the portfolio notebook stale", "the portfolio notebook is out of date", or `/portfolio-notebook-sync`.
---

# portfolio-notebook-sync

## Overview

Keeps the **Interview Prep — Research Portfolio** notebook
(`442368c1-0e26-4d17-a2b7-e4225a570be3`, alias `research-portfolio-prep`) in step with
`~/Projects/portfolio/`.

**Core principle: `MANIFEST.md` is the contract.** The sidecar's manifest records what every
source in the notebook was made from and the hash it was made at. Drift is not a judgment
call — it is a hash comparison. Never re-derive "what should be in the notebook" from
scratch; read the manifest and diff against it.

Sidecar: `~/Projects/NotebookLMs/research-portfolio-prep/` — `README.md` (human record),
`MANIFEST.md` (drift backbone).

Tool preference: **MCP-first** (`mcp__notebooklm-mcp__*`); `nlm` CLI via Bash as fallback.
See `nlm-skill` for full tool docs.

## Two modes — and the wall between them

| Mode | Invocation | Does |
|---|---|---|
| **Drift check** | bare | Re-hashes what's already tracked; repairs what moved. |
| **Onboard** | `--add <project>` | Adds a project that isn't in the notebook yet. |

**A drift check never onboards.** If a drift check notices a project card with no source —
say it in the report and stop there. Adding it is `--add`'s job, and `--add` runs only when
Kyle asks for it by name. Silently growing the notebook during a "sync" is the failure this
wall exists to prevent.

**Neither mode touches git in `~/Projects/portfolio`.** That repo is read-only here: no
commit, no checkout, no merge, no push, no branch. If the content you'd snapshot is sitting
in an unmerged branch or an open PR, **stop and tell Kyle** — which tree to snapshot is his
call, not a step you resolve on the way past.

**Neither mode edits a project's own repo.** You read `~/Projects/<project>/` to snapshot
it. If a README contradicts itself or a doc is wrong, that is a **finding to report**, not a
file to fix — fixing it here means an unreviewed commit in a repo Kyle didn't open.

**`--add <project>` adds that project. Nothing else.** Stale sources you notice on the way
belong to the drift check, and the drift check has its own table and its own confirm.

## MANIFEST.md format

```
| path-or-url | type | source_id | sha256_12 | snapshot | repo_sha |
```

- `path-or-url` — absolute local path, or the URL as added.
- `type` — `text` | `url`.
- `sha256_12` — `shasum -a 256 <file> | cut -c1-12`. URLs get `—`.
- `snapshot` — ISO date the source was added.
- `repo_sha` — `~/Projects/portfolio` HEAD at snapshot time.

Deliberate exclusions are recorded in the sidecar README, not the manifest: `PROJECT.md`,
`HANDOFF.md`, `Sources.md`, `Wiki/` — status and link-inventory docs that churn too fast to
be worth snapshotting.

## Drift check (bare mode)

1. **Read `MANIFEST.md`.** No manifest → say so and stop; the notebook predates this skill
   and needs a manifest written before drift means anything.
2. **Classify every row:**
   - local `text` rows — re-hash the path. Missing file → `deleted`. Hash differs →
     `changed`. Same → `unchanged`.
   - `url` rows — check liveness (`curl -s -o /dev/null -w "%{http_code}"`). A repo that
     went private returns 404.
3. **Report the drift table before changing anything**, with a row per stale/deleted/dead
   source. Then get Kyle's confirm. (When another flow dispatched this skill with explicit
   pre-authorization, proceed without the prompt — but still print the table.)
4. **Repair, in this order:** `source_delete` the stale `source_id`s → `source_add` fresh
   snapshots under the same title scheme with today's date → rewrite `MANIFEST.md` and the
   sidecar README.
5. **Offer, don't force, study-aid regeneration** when any content source changed. Kyle
   decides; regenerating four aids is not free.

## Onboard (`--add <project>`)

1. **Verify `~/Projects/portfolio/projects/<project>.md` exists** — the card is the
   completion signal. No card → stop.
2. **Read the card** for the repo URL, its public/private state, and any arXiv link.
3. **Check the project's stage.** A card for work still in flight (milestones undecided,
   gates open) is a judgment call, not an automatic add — surface the stage and let Kyle
   confirm before spending generation quota on it.
4. **Add sources:**
   - the card itself as `text`, title `portfolio/projects/<project>.md — snapshot <date>`;
   - the repo README as `url` in **raw** form —
     `https://raw.githubusercontent.com/ksdisch/<project>/main/README.md` — matching every
     other repo source in this notebook. If the card says the repo is private, snapshot
     `~/Projects/<project>/README.md` as `text` instead;
   - the source paper, if the card names one, as an arXiv **`/pdf/`** URL. `/abs/` pages
     yield only the abstract.
5. **Generate** `S<n> Ep <m> — <project>` (`audio`, `deep_dive`) at the next free slot in the
   current season — propose the slot, confirm with Kyle — plus its `quiz`
   (`question_count=8, difficulty=medium`) scoped to that episode.
6. **Regenerate the four notebook-wide study aids** (delete-and-regen), recording new ids.
7. **Update** `MANIFEST.md`, the sidecar README, and `~/Projects/NotebookLMs/INDEX.md`.

## Shared rules

- **Rate limits:** 2s between source ops, 5s between generation calls, 2s between status
  polls.
- **Quota:** audio is a rolling ~24h **account-wide** cap (concurrency ~11; batch 5–6). On a
  failure with 0 jobs in flight, that's the quota — **defer, don't loop-retry**: log the
  blocked items with their focus prompts in the sidecar and tell Kyle when capacity returns.
  **Quizzes, reports, flashcards and mind maps are text artifacts and are NOT subject to the
  audio quota** — fire them in large batches regardless of audio deferrals.
- **Sidecar writes go through Bash** (heredoc). The home-base `guard-sidecars` hook blocks
  Write/Edit under the NotebookLM root — but Bash-only is the **standing convention here
  regardless of whether that hook fires in your session**. Do not go looking for which
  settings file registers the guard, or reason from "it isn't active in this repo" to using
  Write/Edit. Where a guard happens not to reach is not permission.
- **Never delete a source or artifact that isn't recorded** in `MANIFEST.md` or the sidecar
  README. An untracked item is a discrepancy to report, never a thing to guess about.
- **Authorization does not travel between documents.** A delete is authorized by two things
  only: the id is in the manifest, and Kyle confirmed *this* run. A plan file, an approved
  refresh doc, or a prior session's enumerated id list authorizes **that** run, not yours —
  even when it names the exact id you want and even when it's the same notebook. Citing
  another document's §-number as your warrant is the tell that you don't have one.
- **Add local docs as `text`, never as `file`.** `file` sources inherit a bare filename, so
  `projects/decay-pin.md` and a since-deleted `learn/decay-pin.md` both land as
  `decay-pin.md` — indistinguishable in every later listing. `text` sources take the title
  you give them.
- **Assert the returned artifact type matches what you asked for.** `studio_create` has
  silently produced a `flashcards` artifact for a `mind_map` request; the sidecar recorded
  the request, so the error survived undetected for eleven days. Check `studio_status`
  before writing the id down.
- **All generation calls pass `confirm=True`.**

## Common mistakes

| Mistake | Why it bites |
|---|---|
| Rebuilding the source list from the repo instead of the manifest | You lose the record of what was deliberately excluded, and re-add churn docs. |
| Onboarding a project during a bare drift check | Kyle asked what moved, not for a bigger notebook — and it spends audio quota he didn't budget. |
| Snapshotting an unmerged branch without asking | The manifest's `repo_sha` vanishes on squash-merge, breaking every future drift check. |
| Trusting the sidecar's recorded artifact *type* | It records what was requested. Verify against `studio_status`. |
| Loop-retrying a quota-blocked audio call | The cap is rolling ~24h. Retrying burns time and changes nothing. |
| Adding the `github.com/...` HTML page as a repo source | Every other repo source is the `raw.` README; the HTML page pulls in nav chrome. |
| Letting an `--add` grow into a full refresh | One project's onboarding quietly became 7 deletes and 4 regenerated aids in testing — none of it asked for, all of it spending quota. |
| Fixing a defect you found inside a project's repo | Report it. An unreviewed commit in someone else's repo is not a sync step. |

## Red flags — stop

- You're about to run `git` anything in `~/Projects/portfolio`.
- You're about to `source_delete` an id you got from `notebook_get` rather than the manifest.
- You're about to add a project because you noticed it, not because Kyle said `--add`.
- You can't find `MANIFEST.md` and are about to reconstruct it by guessing.
- The drift table hasn't been shown to Kyle yet and you're already deleting.
- You're citing another document's section number as authorization to delete.
- You're checking where a guard hook is registered rather than just using Bash.
- You're about to edit a file in `~/Projects/portfolio` or `~/Projects/<project>`.
- An `--add` has grown a second phase that touches sources unrelated to the project.
