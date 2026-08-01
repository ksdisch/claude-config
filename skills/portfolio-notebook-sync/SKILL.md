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

**Neither mode changes git state in `~/Projects/portfolio`.** Read-only git is not just
allowed there, it's **required** — `rev-parse`, `status`, `branch`, `log`, `ls-tree`, and
`gh pr list/view` are how you fill `repo_sha` and how you notice an unmerged branch at all.
What is forbidden is anything that changes state or the working tree: commit, checkout,
merge, rebase, pull, push, branch, stash, reset, or any file edit.

If the content you'd snapshot is sitting in an unmerged branch or an open PR, **stop and
tell Kyle** — which tree to snapshot is his call, not a step you resolve on the way past.

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
- `sha256_12` — the content hash, for **both** types. Local:
  `shasum -a 256 <file> | cut -c1-12`. URL: **status first, hash only on 200** —

  ```sh
  tmp=$(mktemp)                       # never a bare relative path — cwd may be a guarded tree
  code=$(curl -sL --max-time 15 -o "$tmp" -w '%{http_code}' "$url")
  if [ "$code" = 200 ]; then
    printf '200 %s\n' "$(shasum -a 256 < "$tmp" | cut -c1-12)"
  else
    printf '%s —\n' "$code"           # always emit the code; step 2 needs it to split dead vs unknown
  fi
  rm -f "$tmp"
  ```

  Never pipe `curl` straight into `shasum`: an error page has a body too, so a 404 hashes
  stably and reads as ordinary changed content. A NotebookLM `url` source is a snapshot
  taken at add time, so without a body hash a rewritten repo README stays stale forever and
  every check calls it live-and-fine — but liveness and content are two questions and both
  must be asked. Use `—` only where a body genuinely can't be fetched, and mark that row
  `unverified` rather than clean.
- `snapshot` — ISO date the source was added.
- `repo_sha` — `~/Projects/portfolio` HEAD at snapshot time.

Deliberate exclusions are recorded in the sidecar README, not the manifest: `PROJECT.md`,
`HANDOFF.md`, `Sources.md`, `Wiki/` — status and link-inventory docs that churn too fast to
be worth snapshotting.

**When the manifest doesn't exist yet.** A bare drift check stops (see below). An `--add`
may still proceed — but it seeds the manifest with **only the rows it actually adds**, and
writes this exact machine-readable first line so no later run can miss it:

```
<!-- PARTIAL: N sources in this notebook are unbacked by any row below -->
```

Never back-fill rows for pre-existing sources: their snapshot hashes and dates were never
recorded, so any value you write there is invented, and a hash you invented is worse than a
row you left out. A manifest carrying that marker **can never report "in sync"** — the
reconciliation step classifies every uncovered source as `unverified`. Without it, a
three-row manifest reports clean over twenty-eight unchecked sources.

## Drift check (bare mode)

1. **Read `MANIFEST.md`.** No manifest → **stop and offer to bootstrap one**; drift is
   meaningless without a baseline, but the skill must not dead-end here.
   - Bootstrapping is a **separate action needing Kyle's explicit yes** — it is not part of
     a drift check and never happens silently on the way to one.
   - Build rows from **records, not inference**: the sidecar README's `source_id` → path
     tables, and `notebook_get`'s recorded titles (for `url` sources the title *is* the URL
     as added — that's a record too). Re-deriving what *ought* to be in the notebook by
     walking the repo, or reconstructing a URL from naming convention, is the red flag.
   - Where neither record yields a `path-or-url` — the sidecar's papers table stores prose
     labels like `Global Workspace / transformer-circuits 2026`, and a title may be
     unhelpful — write the label you have, mark the row `unverified`, and ask Kyle to supply
     or confirm the URL. Never invent one.
   - Historical hashes are usually unrecoverable. Write `unknown@<original-date>` rather
     than back-filling a hash from a commit you can't prove the snapshot came from — which
     correctly forces every row to re-verify on the first real check.
   - Then re-run the check against the new manifest and print the table again before
     touching anything.
2. **Classify every row:**
   - local `text` rows — re-hash the path. Missing file → `deleted`. Hash differs →
     `changed`. Same → `unchanged`.
   - `url` rows — **read the status code first, and let it decide before any hashing.**
     A stable `404`/`410` → `dead`. Any other non-200 (`000`, `429`, `5xx`) → `unknown`:
     report it, never auto-delete on it. **Only on `200`** do you hash the body: differs
     from the row → `changed`, same → `unchanged`. Hashing a non-200 body is how a dead
     source gets "repaired" into a source whose content is the words `404: Not Found`.
3. **Reconcile the manifest against the notebook — always, report-only, and in both
   directions.** Call `notebook_get` and compare its `source_id`s to the manifest's.
   - **In the notebook, not in the manifest** → `unverified`. Not clean, and not deletable
     (reading `notebook_get` to **report** a gap is required; treating its output as a
     delete list is the red flag). A manifest that doesn't cover every live source —
     including one `--add` seeded with only its own rows — **may never report "in sync"**.
     Say how many are unbacked and offer to finish the bootstrap.
   - **In the manifest, not in the notebook** → `vanished`. Step 2 only ever looks at the
     local file, so without this a source deleted out of the notebook reports `unchanged`
     forever and the notebook silently shrinks. Report it and offer to re-add from the
     recorded path; never treat it as drift to repair by deleting anything.

4. **Report the drift table before changing anything**, with a row per
   `changed`/`deleted`/`dead`/`unknown`/`unverified`/`vanished` source. Then get Kyle's
   confirm. (When another flow dispatched this skill with explicit pre-authorization,
   proceed without the prompt — but still print the table.) Repairability by class:
   `changed` → delete-and-re-add · `deleted` → delete only (the file is gone; there is
   nothing to re-add) · `dead` → **substitute, never re-add the same URL** (below) ·
   `vanished` → re-add only · `unknown` and `unverified` → reported, left alone.
5. **Repair, in this order:** `source_delete` the stale `source_id`s → `source_add` fresh
   snapshots under the same title scheme with today's date → rewrite `MANIFEST.md` and the
   sidecar README.

   **A `dead` URL is the exception — never delete-then-re-add the same URL.** The URL is
   dead; re-adding it either fails or imports an error page as if it were the source, and
   the notebook's copy is the last surviving snapshot of that content. Substitute instead:
   if the project's repo went private, add `~/Projects/<project>/README.md` as `text`
   (title `<project> repo README (repo private) — snapshot <date>`) and only then delete the
   dead row. If no local substitute exists, **leave the dead source in place** and report
   it — a stale copy beats no copy.
6. **Offer, don't force, study-aid regeneration** when any content source changed. Kyle
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
5. **Generate the episode** (`audio`, `deep_dive`) plus its `quiz`
   (`question_count=8, difficulty=medium`) scoped to it.
   - **Title to match the scheme already in the notebook** — read the sidecar's audio table
     first. Today that is `Ep <n> — <topic>`. Do not invent a prefix: `audio-series` bans a
     shared leading prefix because every episode then truncates identically on a phone.
   - **Propose the slot, confirm with Kyle.** "Next free number" is not automatic — a season
     may end on a designed finale (the current one closes with `Ep 8 — Skeptic Grilling`),
     and appending past a capstone is a curriculum decision, not arithmetic.
6. **Regenerate the four notebook-wide study aids** (delete-and-regen), recording new ids —
   **but only if the source layer is currently clean.** If a drift check would flag stale or
   dead sources, regenerating now bakes that staleness into four fresh artifacts. Say so,
   skip the step, and recommend a drift check first; it is a separate, separately-confirmed
   run.
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
- **One delete bar, stated once.** A **source** delete needs *both*: its `source_id` is a row
  in `MANIFEST.md`, **and** Kyle confirmed this run's drift table. Being recorded is
  necessary, never sufficient. No manifest → no source deletes, full stop; bootstrap first.
  **Artifacts** live only in the sidecar README, so an artifact delete reads that instead —
  same two-part shape: recorded there, plus this run's confirm. An untracked item is a
  discrepancy to report, never a thing to guess about.
- **Authorization does not travel between documents.** Both halves of the bar above must be
  satisfied *in this run*. A plan file, an approved refresh doc, or a prior session's
  enumerated id list authorizes **that** run, not yours — even when it names the exact id
  you want and even when it's the same notebook. Citing another document's §-number as your
  warrant is the tell that you don't have one.
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

- You're about to run a **state-changing** `git` command in `~/Projects/portfolio` (reads
  are fine and expected).
- You're about to `source_delete` an id you got from `notebook_get` rather than the manifest.
- You're about to add a project because you noticed it, not because Kyle said `--add`.
- You can't find `MANIFEST.md` and are about to reconstruct it by guessing.
- The drift table hasn't been shown to Kyle yet and you're already deleting.
- You're citing another document's section number as authorization to delete.
- You're checking where a guard hook is registered rather than just using Bash.
- You're about to edit a file in `~/Projects/portfolio` or `~/Projects/<project>`.
- An `--add` has grown a second phase that touches sources unrelated to the project.
