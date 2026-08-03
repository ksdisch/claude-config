---
name: portfolio-notebook-sync
description: Use when the research-portfolio NotebookLM notebook (alias `research-portfolio-prep`) may have fallen out of step with `~/Projects/portfolio`, when a portfolio project has just been carded and belongs in it, or when a project's `/research-paper` write-up has been merged and should join the notebook. Triggers on "sync the portfolio notebook", "add <project> to the portfolio notebook", "add <project>'s paper to the notebook", "the paper is merged — put it in the notebook", "is the portfolio notebook stale", "the portfolio notebook is out of date", or `/portfolio-notebook-sync`.
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

## Three modes — and the walls between them

| Mode | Invocation | Does |
|---|---|---|
| **Drift check** | bare | Re-hashes what's already tracked; repairs what moved. |
| **Onboard** | `--add <project>` | Adds a project that isn't in the notebook yet. |
| **Onboard a paper** | `--add-paper <project>` | Adds a merged `/research-paper` write-up for a project already in the notebook. |

**A drift check never onboards.** If a drift check notices a project card with no source —
or a merged paper with no source — say it in the report and stop there. Adding it is
`--add`'s or `--add-paper`'s job, and each runs only when Kyle asks for it by name. Silently
growing the notebook during a "sync" is the failure this wall exists to prevent.

**`--add` and `--add-paper` don't call each other either.** `--add` onboards a project and
does not go looking for its paper; `--add-paper` adds a paper and refuses to onboard the
project underneath it. Each does the one thing it is named for.

**No mode changes git state in `~/Projects/portfolio` or in a project repo.** Read-only git
is not just allowed there, it's **required** — `rev-parse`, `status`, `branch`, `log`,
`ls-tree`, `show`, `symbolic-ref`, and `gh pr list/view` are how you fill `repo_sha`, how you
read merged content, and how you notice an unmerged branch at all.
What is forbidden is anything that changes state or the working tree: commit, checkout,
merge, rebase, pull, push, branch, stash, reset, or any file edit.

**One narrow exception, and it is not `pull`:** `git fetch --no-write-fetch-head origin
<default-branch>` is allowed in a **project** repo. Kyle merges a paper's PR **on GitHub**,
so the local ref does not advance on its own; without a fetch, `--add-paper` reports "the
paper has not landed" about a paper that landed minutes ago, and the read-only rule would
leave the run with no sanctioned way out. A fetch advances a remote-tracking ref only — no
local branch moves, no working tree is touched, nothing is merged. `pull` stays forbidden
precisely because it does both. Every default-branch read below is against
`origin/<default-branch>`, never the local branch, which is also why a stale clone can never
stamp a row with provenance that predates its own content.

If the content you'd snapshot is sitting in an unmerged branch or an open PR, **stop and
tell Kyle** — which tree to snapshot is his call, not a step you resolve on the way past.

**Neither mode edits a project's own repo.** You read `~/Projects/<project>/` to snapshot
it. If a README contradicts itself or a doc is wrong, that is a **finding to report**, not a
file to fix — fixing it here means an unreviewed commit in a repo Kyle didn't open.

**`--add <project>` adds that project. Nothing else.** Stale sources you notice on the way
belong to the drift check, and the drift check has its own table and its own confirm.

## MANIFEST.md format

```
| path-or-url | type | source_id | sha256_12 | snapshot | baseline | repo_sha |
```

- `path-or-url` — absolute local path, or the URL as added.
- `type` — **how this row is re-checked**, which is not the same question as what kind of
  source NotebookLM holds: `text` (a local file, read from disk) | `url` (fetched) | `paper`
  (a blob on a project repo's default branch, read with `git show`). A `paper` row is added
  to the notebook as an ordinary **`text`** source — the column records the *basis for
  comparison*, and for a paper that basis is the merged tree, never the working tree.

  Only `--add-paper` creates `paper` rows. The distinction is load-bearing: project repos sit
  on feature branches for long stretches (`ghost-patch` and `dim-stage` are on `chore/add-ci`
  as of 2026-08-02, and that branch already diverges from the default one inside
  `docs/paper/`), so re-hashing a paper from disk reports `changed` about a file nobody
  changed — and `text` + `changed` is auto-repairable, which would replace the notebook's
  merged snapshot with unmerged branch prose under a confirm that said only "changed".
- `sha256_12` — the content hash, for **all three** types. Local `text`:
  `shasum -a 256 <file> | cut -c1-12`. `paper`: hash the **merged blob**, never the file on
  disk. `git show` takes a *repo-relative* path, while `path-or-url` is absolute, so the
  row's own value has to be split before it can be used — see the derivation in the drift
  check's step 2. Passing the absolute path straight through is not a near-miss that
  degrades gracefully: `git show <ref>:/Users/…` exits 128 with *"exists on disk, but not
  in …"*, which the failure rule then turns into "changed nothing" on **every** run,
  forever. The row that has its own type precisely so it can be re-checked becomes the one
  row the check can never read.

  **Never name a shell variable `path` in these snippets.** Kyle's shell is zsh, where `path`
  is tied to `PATH`; assigning it wipes the environment mid-run and every later command dies
  with `command not found`. Use `abs` / `rel`.

  URL: **status first, hash only on 200** —

  ```sh
  tmp=$(mktemp)                       # never a bare relative path — cwd may be a guarded tree
  code=$(curl -sL --max-time 15 -o "$tmp" -w '%{http_code}' "$url"); rc=$?
  if [ "$rc" = 0 ] && [ "$code" = 200 ]; then
    printf '200 rc=0 %s\n' "$(shasum -a 256 < "$tmp" | cut -c1-12)"
  else
    printf '%s rc=%s —\n' "$code" "$rc"
  fi                                    # both branches emit (code, rc) — step 2 keys on the pair
  rm -f "$tmp"
  ```

  **Both the exit status and the code must be clean before you hash.** A transfer that
  times out mid-download still reports `%{http_code} 200` while `rc=28`, so a status-only
  guard hashes a truncated body and reports an unchanged document as `changed`.

  Never pipe `curl` straight into `shasum`: an error page has a body too, so a 404 hashes
  stably and reads as ordinary changed content. A NotebookLM `url` source is a snapshot
  taken at add time, so without a body hash a rewritten repo README stays stale forever and
  every check calls it live-and-fine — but liveness and content are two questions and both
  must be asked.

  **A failed fetch never overwrites a good hash.** `—` means *this row has never had a
  hash* — a source whose body couldn't be fetched at bootstrap. It is not what you write
  when today's fetch fails: a transient `429` or timeout must leave `sha256_12` exactly as
  it was, or the row loses the only baseline it could ever be compared against. Failed
  fetches are reported as `unknown` for the run; they change nothing on disk.
- `snapshot` — ISO date the source was **added to the notebook**. Records what the
  notebook's copy is. **Never rewritten** by a drift check — re-adding a source is what
  moves it.
- `baseline` — ISO date `sha256_12` was last confirmed against the live content. This is
  the column a manifest-only baseline refresh updates. Keeping it separate from `snapshot`
  is the point: when they differ, the row is saying *"the upstream content has moved on and
  Kyle accepted that, and the notebook still holds the `snapshot`-dated copy"* — an
  acknowledged divergence that stays visible instead of being flattened into a row
  indistinguishable from a freshly re-added one.
- `repo_sha` — default-branch HEAD of **the repo this row's content came from**, at snapshot
  time. For card and portfolio-doc rows that is `~/Projects/portfolio`; for paper rows
  (`--add-paper`) it is `~/Projects/<project>`. No new column is needed to tell them apart —
  `path-or-url` already says which repo the row was snapshotted from. Record the sha of the
  **default branch**, never of a feature branch: a branch sha vanishes on squash-merge and
  takes the row's provenance with it.

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
   - `paper` rows — **never touch the working tree.** The manifest carries one absolute path
     and no repo or branch column, so derive all three from it, then ask **existence and
     content as two separate questions** (`ls-tree` answers the first, `git show` the
     second — `git show` alone cannot, because it returns the same 128 for "removed from the
     tree" and "I couldn't read this repo at all"):

     Work **one row at a time, start to finish**, recording that row's answer before moving
     to the next. Per row:

     1. **Derive the repo** from the row's absolute path (`rev-parse --show-toplevel` on its
        directory). Can't resolve it, or resolves empty → `unchecked`, next row.
     2. **Derive the repo-relative path** by stripping the repo root off the absolute one.
        `git show` and `ls-tree` both need the relative form.
     3. **Resolve the default branch *name*** — the bare `main`, not the ref. `symbolic-ref
        --short refs/remotes/origin/HEAD` prints `origin/main`, so **strip the `origin/`
        prefix** (`| sed 's|^origin/||'`). Steps 4 and 5 then compose `origin/<name>`; feeding
        them the unstripped value builds `origin/origin/main`, which is not a valid object
        name and exits 128 — and invariant 1 below would dutifully report that as `unchecked`
        on every row forever, so the mistake reads as a legitimate answer instead of a bug.
        Then fetch that branch, with `--no-write-fetch-head` (this mode sweeps every carded
        repo; none of those fetches should be writing `FETCH_HEAD`). Either step failing →
        `unchecked`, next row.
     4. **Ask existence with `ls-tree`** against `origin/<name>`: non-zero exit →
        `unchecked` · exit 0 with **zero lines** → `deleted` · exit 0 with **one line** → the
        paper is there.
     5. **Only then hash it**, with a failure arm of its own — this step has one for the same
        reason the `url` probe does. Capture `git show origin/<name>:<relative-path>` and
        **check its exit status before hashing**; non-zero → `unchecked`, next row. Never pipe
        `git show` straight into `shasum`: the pipeline reports the *last* command's status, so
        a failed read yields rc 0 and the stable empty-string hash `e3b0c44298fc`, which never
        matches the recorded value and therefore classifies `changed` — the repairable class,
        which would delete the notebook's source and re-ingest an empty body. Only on a clean
        read, compare to the row's recorded `sha256_12`: differs → `changed`, same →
        `unchanged`.

     Five invariants make the difference between this working and quietly corrupting the
     notebook. Each one is here because violating it did exactly that during review:

     - **A git error is never an answer about the paper.** Non-zero exit means *you could not
       look*, which is `unchecked` — never `deleted`, never `unchanged`. `unchecked` also bars
       the run from reporting "in sync"; `unknown` would not, which is why the class differs.
     - **Existence and content are two questions.** `git show` returns the same 128 for
       "removed from the tree" and "couldn't read this repo at all", so it cannot decide
       `deleted`. `ls-tree` can: it exits 0 with no output when a pathspec matches nothing.
     - **Never run `git show <ref>:` with an empty path.** That is not an error — it is the
       **root tree**, exits 0, and hashes stably to a value no paper can match. Every row
       would read `changed`, and `changed` is repairable for `paper` rows, so the check would
       delete the notebook's source and re-ingest a directory listing.
     - **Never run `git -C` with an empty path.** Per `git(1)` that is a no-op, so the command
       silently runs in whatever repo you are standing in and *succeeds* — fetching in a repo
       this skill may not touch and answering about the wrong tree. Prove the repo root is
       non-empty before using it.
     - **A row's derived values must not outlive the row.** Finish each row's classification
       while its repo, branch and relative path are still that row's; carry forward the
       finished answer, never the intermediates.

     Whatever shell you write for this, **test it on a multi-row case in the shell you are
     running.** Single-row tests pass under both `bash` and `zsh` even when the loop is wrong —
     `zsh` does not word-split unquoted expansions, and `continue` outside a loop is a
     fall-through in `bash` but aborts the script in `zsh`. Every one of those cost a review
     round here.
   - `url` rows — classify on the **pair** the probe emits, `(code, rc)`, never on the code
     alone. There are exactly three outcomes and no fourth:
     - `rc=0` **and** `404`/`410`, stable across a retry → `dead`.
     - `rc=0` **and** `200` → hash the body: differs from the row → `changed`, same →
       `unchanged`. This is the **only** branch that produces a hash.
     - **everything else** → `unknown`. That means `000`, `429`, `5xx`, redirects, *and any
       non-zero `rc` whatever the code says* — a mid-download timeout reports `200 rc=28`,
       which is not a 200 for our purposes. Report it; never delete or re-hash on it.

     Keying on the code alone leaves `200 rc=28` in no bucket at all, and an unbucketed row
     gets improvised into a silent "clean".
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
   - **Merged paper with no row** → `unpapered`, **report-only**. For each project the
     manifest already carries, run `--add-paper`'s step-3 detector and step-4 gate against
     that project's repo. Both deliverables present on the default branch, and no `paper` row
     covers them → say so in the table.

     **A repo you couldn't read is `unchecked`, never `unpapered` and never silence.** Branch
     on the git exit status before branching on its output: a project that isn't cloned at
     `~/Projects/<slug>`, isn't a git repo, or whose fetch failed produces empty stdout for
     exactly the same reason a paperless repo does. Reporting nothing for it would let the
     sweep say "current" about projects nobody looked at — the same failure the `PARTIAL:`
     marker exists to prevent. Count them and name them.

     Naming it is the entire job. Adding it is `--add-paper`'s, on Kyle's word — the same
     wall that stops a drift check from onboarding a project stops it from onboarding a
     paper. Without this line a paper that landed months ago is invisible to the one command
     whose whole purpose is answering "is this notebook current?"

4. **Report the drift table before changing anything**, with a row per
   `changed`/`deleted`/`dead`/`unknown`/`unverified`/`vanished`/`unpapered`/`unchecked`
   source. Then get Kyle's confirm. (When another flow dispatched this skill with explicit
   pre-authorization, proceed without the prompt — but still print the table.)

   **`unpapered` and `unchecked` are never repairable here, in any `type`.** They are the two
   classes that name something *outside* the notebook rather than stale inside it — one a
   paper the notebook doesn't carry, the other a repo this run couldn't read — so there is no
   row to fix and no confirm that turns either into one. They appear in the table and nowhere
   else in this mode. **A run reporting any `unchecked` may not call the notebook "in
   sync"**, for the same reason a `PARTIAL:` manifest may not: an unread source is not a
   clean one.

   **Repairability is decided by `type` first, then class.**

   - **The notebook SOURCE behind a `url` row is never auto-repaired — report only, in every
     class.** No automatic `source_delete` + `source_add` on a URL, ever. Three review rounds
     each found a *different* path by which that re-imports an error page as if it were the
     source, and the notebook's copy may be the last surviving snapshot of a URL that has
     since died. Kyle decides, case by case.

     **This is not the same as the manifest baseline, which must stay updatable.** On Kyle's
     confirm that a `changed` URL's new content is legitimate, **rewrite that row's
     `sha256_12` and its `baseline` date — and leave `snapshot` alone** (that column records
     what the notebook's copy is, and the notebook's copy did not change). A manifest-only
     edit, touching nothing in the notebook. Without it a `changed` repo README is reported
     as `changed` on every future run forever, with no action in the skill that can ever
     clear it, and a permanently dirty drift table trains you to ignore the drift table.
     Updating the baseline is bookkeeping; re-adding the source is the dangerous act. Only
     the second one is banned.
   - **`text` rows**, by class: `changed` → delete-and-re-add · `deleted` → delete only
     (nothing to re-add) · `vanished` → re-add, but **only after re-confirming the file
     exists and hashes at the recorded path** · `unknown`/`unverified` → left alone.
   - **`paper` rows** repair like `text` rows with one substitution that is not optional:
     every re-add takes its body from the merged blob, never from the file on disk. **Re-derive
     the repo root, default-branch name and repo-relative path for that row**, by step 2's
     first three steps — do not carry them over from the classification pass. Whatever computed
     them there belongs to the row being classified, and reaching back gets another row's
     values or an empty string; an empty path is the case that bites, since
     `git show origin/<name>:` is the **root tree** rather than an error. `changed` →
     delete-and-re-add from the merged blob · `deleted` → delete only ·
     `vanished` → re-add from the merged blob, after re-confirming it still resolves ·
     `unchecked` → left alone. (`unchecked`, not `unknown`: a `paper` row's git read either
     succeeds or the row never reaches classification, so `unknown` cannot arise here.)
     Re-adding from disk here would ingest whatever branch the repo
     is parked on while the row goes on claiming default-branch provenance.
   - When step 2 and step 3 disagree about a row (`dead` by probe, `vanished` by
     reconciliation), **the more conservative class wins** and it stays report-only.
5. **Repair, in this order:** `source_delete` the stale `source_id`s → `source_add` fresh
   snapshots under the same title scheme with today's date → rewrite `MANIFEST.md` and the
   sidecar README.

   **URL sources are not repaired here** (step 4) — but their manifest rows still converge:
   - `changed` + Kyle confirms the new content is fine → **update `sha256_12` and `baseline`
     in the manifest only; `snapshot` is untouched.** The notebook keeps its original copy,
     the divergence stays visible in the gap between the two dates, and the row goes
     `unchanged` next run. If instead he wants the notebook to carry the new content, that's
     an explicit re-add he asks for by name.
   - `vanished` (in the manifest, gone from the notebook) → offer to re-add from the
     recorded URL, **after a fresh probe returns `200 rc=0`**; on anything else report and
     leave it. Re-adding is the one action a `vanished` row needs and the one a `dead` row
     must never get, which is why they are listed separately.
   - `dead` → offer a substitute: if the repo went private, add `~/Projects/<project>/README.md`
     as `text` (title `<project> repo README (repo private) — snapshot <date>`) and only
     then delete the dead row. If no local substitute exists, **leave the dead source in
     place** — a stale copy beats no copy.
   - `unknown` → change nothing at all, including the manifest. An unknown is a failed
     measurement, not a fact about the source.
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

## Onboard a paper (`--add-paper <project>`)

The hop from a finished `/research-paper` write-up into this notebook, for a project the
notebook already carries.

1. **Verify the card exists** — `~/Projects/portfolio/projects/<project>.md`. No card → stop.
   Same completion signal `--add` uses.

2. **Verify the project is already in the notebook, and that its paper isn't.** Two checks
   against `MANIFEST.md`, both required:
   - a **card row** for the project exists. If it doesn't, the project has never been
     onboarded, and **that is `--add`'s job, not this one.** Stop and say so. A paper landing
     in a notebook that holds no other context for its project is a source with nothing to
     sit against.
   - **no `paper` row already covers either deliverable path.** If one does, this project's
     paper is already in the notebook — **stop and report it as already-present.** An updated
     paper is a `changed` drift repair, not a second add: re-running `--add-paper` otherwise
     puts a duplicate copy of both files in the notebook and writes a second row for the same
     `path-or-url`, breaking the manifest's one-row-per-source contract. Worse, the duplicate
     then reconciles as `unchanged` forever, so nothing downstream ever flags it. "Did I
     already do this?" is a question the command must answer, not a way to corrupt it.

3. **Locate the deliverables by exact filename, never by globbing the directory.**
   `<slug>` = the project's repo directory name.

   ```
   ~/Projects/<slug>/docs/paper/<slug>-paper.md
   ~/Projects/<slug>/docs/paper/<slug>-presenter-pack.md
   ```

   No `docs/` in that repo → `paper/` at the repo root, the same fallback `/research-paper`
   uses when it writes them. Step 4 resolves which of the two applies (`$dir`) against the
   default-branch tree, so the fallback is tested rather than merely documented.

   **`docs/papers/` — plural — belongs to a different skill and must never be read here.**
   That is `/paper-eli5`'s output: plain-English rewrites of *other people's* papers. The two
   directory names differ by one letter and their contents are categorically different —
   Kyle's own work versus third-party work. Globbing the plural imports strangers' papers
   into an interview-prep notebook about Kyle's portfolio.

   **Globbing the singular is unsafe too**, which is why the rule is exact filenames rather
   than "the two `.md` files in there". `~/Projects/dim-stage/docs/paper/` today holds
   `global-workspace-readable-small-language-models-eli5.md` alongside the two real
   deliverables. Match the two names above and **skip anything matching `*-eli5*`**.

4. **Require BOTH files to be on the default branch — this is the trigger, and it is a tree
   query against the *fetched remote* ref, not a filesystem check and not the local branch.**

   Resolve the default branch rather than assuming `main`, refresh the remote ref, then ask
   for both pathspecs at once:

   ```sh
   repo=~/Projects/<slug>
   def=$(git -C "$repo" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')
   [ -n "$def" ] || { echo "unchecked: cannot resolve default branch for <slug>"; exit 1; }
   git -C "$repo" fetch --no-write-fetch-head origin "$def" \
     || { echo "unchecked: fetch failed for <slug> — ref is stale, no answer is possible"; exit 1; }

   # Probe for the deliverables themselves at each candidate dir, not for a `docs/` directory.
   for d in docs/paper paper; do
     hits=$(git -C "$repo" ls-tree --name-only "origin/$def" \
              -- "$d/<slug>-paper.md" "$d/<slug>-presenter-pack.md") \
       || { echo "unchecked: ls-tree failed for <slug>"; exit 1; }
     [ -n "$hits" ] && { dir=$d; break; }
   done
   ```

   Five things this shape gets right, each of which was wrong when assumed away:

   - **`origin/$def`, after a fetch.** Kyle merges the paper's PR **on GitHub**; the local
     ref does not advance on its own. Querying the local branch reports "not landed" about a
     paper that landed minutes ago — on precisely the happy path the handoff prescribes — and
     stamps `repo_sha` from a tree that predates the content it claims to describe.
   - **Resolved, not hardcoded.** Every other statement here says *default branch*; writing
     `main` into the one command that decides it would silently mean "never landed" in any
     repo on `master` or `trunk`.
   - **Both pathspecs, expecting two lines back.** Step 6 adds two files, so gating one is
     a gate on nothing. **One line back → report the partial and stop**; never add half a
     pair, and never let a merged paper drag an unmerged presenter pack in behind it.
   - **Every failure is terminal, and says so.** A `|| some_helper` that isn't defined
     anywhere returns 127 and lets execution *continue* — so a failed fetch would fall
     through and the gate would answer from exactly the stale ref the fetch existed to
     refresh, resurrecting the "paper has not landed" bug as a swallowed error. Offline, on
     VPN, or against a private clone with expired auth, that is the common case, not the
     exotic one.
   - **The fallback dir is found by looking for the files, not for `docs/`.** `git ls-tree`
     exits **0** when a pathspec matches nothing — absence shows up only as empty stdout — so
     any probe that branches on its exit status has a dead fallback branch and silently
     pins `docs/paper`. Testing `-n "$hits"` is what makes the documented `paper/` fallback
     real rather than decorative.

   Testing the working tree instead reads whatever branch that repo happens to be sitting
   on, which is routinely not the default one — as of 2026-08-02, `ghost-patch` and
   `dim-stage` are both parked on `chore/add-ci` while their papers are merged, and that
   branch already diverges from the default one *inside* `docs/paper/`.

   **Branch on the exit status before the output.** A repo that isn't cloned, isn't a git
   repo, or whose fetch failed prints nothing to stdout — identical to a repo with no paper.
   Non-zero exit → `unchecked`; say the check could not be made. Only a **clean exit with no
   matching lines** means the paper has not landed.

   Not landed → **stop and report**, naming the open PR if `gh pr list` shows one.
   `/research-paper` deliberately opens a **review-only PR it never merges**, so an unmerged
   paper is the *expected* state, not an anomaly to work around. Snapshotting it anyway is
   the red flag this skill already names: a `repo_sha` recorded from a feature branch
   vanishes on squash-merge and takes the row's provenance with it. Merging is Kyle's call,
   made on the PR, not a step taken on the way past.

5. **Hash the merged blobs — not the files on disk — then surface and confirm.**

   ```sh
   for f in "<slug>-paper.md" "<slug>-presenter-pack.md"; do
     blob=$(git -C "$repo" show "origin/$def:$dir/$f") \
       || { echo "unchecked: cannot read $f from origin/$def"; exit 1; }
     printf '%s\t%s\n' "$f" "$(printf '%s' "$blob" | shasum -a 256 | cut -c1-12)"
   done
   ```

   **Capture the blob and check the status before hashing; never pipe `git show` straight
   into `shasum`.** A pipeline reports its *last* command's status, so a failed read exits 0
   and yields the stable empty-string hash `e3b0c44298fc` — a real-looking value that is
   simply wrong. Here it would be written into the manifest as the paper's hash, and every
   later drift check would compare against it. This file already states the rule for `url`
   sources ("Never pipe `curl` straight into `shasum`"); it holds for `git show` for exactly
   the same reason.

   The gate certifies the merged tree, so the hash and the ingested body must come from that
   same tree. Hashing `<repo>/$dir/<slug>-paper.md` instead certifies one thing and ingests
   another: the notebook ends up holding unmerged branch prose while the manifest asserts
   default-branch provenance — the exact failure step 4 exists to prevent, arriving through
   the back door.

   Print one row per file *before* adding anything:

   | path | type | `sha256_12` | on default branch | already in notebook |
   |---|---|---|---|---|

   The last column is step 2's answer, restated where Kyle can see it at the moment of
   confirming. Then get his confirm. This mode grows the notebook, and growing it silently is
   exactly the failure the drift-check wall exists to prevent — the wall is about the act,
   not about which mode performs it. (Pre-authorized dispatch: proceed without the prompt,
   still print the table.)

6. **Add both to the notebook as `text` sources, with bodies from `git show`** — never
   `file` (per the shared rule), and never read from the working tree. Write each blob to a
   `mktemp` file and add from that. Titles:

   - `<project> paper — snapshot <date>`
   - `<project> presenter pack — snapshot <date>`

7. **Write the manifest rows**, one per deliverable, with `type` = **`paper`** — the row is
   re-checked against the merged blob, not the path, and that column is what tells the drift
   check so. `repo_sha` is `git -C "$repo" rev-parse "origin/$def"`: the tree the snapshot
   actually came from, not `~/Projects/portfolio`'s HEAD and not the local branch's.
   `baseline` equals `snapshot` on a fresh add — the hash was taken and confirmed the same
   day.

   `path-or-url` is `$repo/$dir/<file>` — the **absolute** path, matching every other row in
   the manifest and keeping step 2's already-present check answerable next time.

   **The drift check must be able to split that string back into `repo` + `rel`, and this
   step is what guarantees it can.** `git show` takes a repo-relative path; the manifest
   stores an absolute one and has no repo or branch column, so the re-check derives all three
   (`rev-parse --show-toplevel`, `${abs#"$repo"/}`, `symbolic-ref`) from this one value.
   Write the path any other way — a `~`, a symlinked parent, a trailing `./` — and the
   derivation silently stops matching, which surfaces as a paper row that is `unchecked` on
   every run instead of as an error. Store the same absolute path the gate resolved.

8. **Figures are reported, not ingested.** `mute-map/docs/paper/` carries six rendered PNGs
   and `dim-stage/docs/paper/` a `figures/` directory. A NotebookLM `text` source cannot
   carry an image, so list them in the report as present-and-not-added. Saying the notebook
   has the paper when it has the prose and not the figures is the kind of half-truth that
   costs Kyle an answer in a live interview.

9. **Artifact generation is offered, never assumed.** Unlike `--add`, this mode does not
   presume an episode — a paper may warrant one, or may belong to a season that already
   closed. Offer an `audio` + `quiz` scoped to the new sources with `source_ids`, and apply
   `--add` step 6's precondition unchanged: if the source layer isn't currently clean,
   say so and skip rather than baking staleness into fresh artifacts.

10. **Update** `MANIFEST.md` and the sidecar README. `INDEX.md` describes the notebook as a
    whole and does not change when one project gains a paper.

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
- **Verify an artifact's type from its CREATION response, not from a listing.** A
  `studio_create(artifact_type="mind_map")` returns `mind_map_json`, `root_name` and
  `children_count` — that is the authoritative signal, and it's what you record.

  The listings disagree with each other, so neither is a safe check. Observed 2026-08-01 on
  artifact `d1352488`, created as a mind map and confirmed by its `mind_map_json`: **MCP
  `studio_status` reported `type: flashcards` with `flashcard_count: 9`**, while `nlm studio
  status` reported it correctly as a mind map with no `flashcard_count`. This skill is
  MCP-first, so the wrong reading is the one you'll hit by default.

  Consequences, both directions: a notebook with one mind map can look like it has two
  flashcard sets under MCP — so **never "correct" a sidecar `mind_map` entry from an MCP
  listing** — and a genuine type mismatch is still worth catching, so check the creation
  response and cross-check with the CLI when it matters.
- **All generation calls pass `confirm=True`.**

## Common mistakes

| Mistake | Why it bites |
|---|---|
| Rebuilding the source list from the repo instead of the manifest | You lose the record of what was deliberately excluded, and re-add churn docs. |
| Onboarding a project during a bare drift check | Kyle asked what moved, not for a bigger notebook — and it spends audio quota he didn't budget. |
| Snapshotting an unmerged branch without asking | The manifest's `repo_sha` vanishes on squash-merge, breaking every future drift check. |
| "Correcting" a sidecar `mind_map` entry to `flashcards` because an MCP listing says so | MCP `studio_status` mis-types mind maps (the CLI doesn't). You'd corrupt a correct record with a known-bad signal. |
| Treating a `changed` URL row as unfixable because URL sources aren't auto-repaired | The manifest baseline is still updatable on confirm — otherwise the row reports `changed` forever and the drift table becomes noise. |
| Steering a `report` or `mind_map` with `focus_prompt` alone | Both ignored it in practice — the paper sources dominated and the artifact came back about the source paper, not the portfolio. Scope with `source_ids` instead. |
| Loop-retrying a quota-blocked audio call | The cap is rolling ~24h. Retrying burns time and changes nothing. |
| Adding the `github.com/...` HTML page as a repo source | Every other repo source is the `raw.` README; the HTML page pulls in nav chrome. |
| Letting an `--add` grow into a full refresh | One project's onboarding quietly became 7 deletes and 4 regenerated aids in testing — none of it asked for, all of it spending quota. |
| Fixing a defect you found inside a project's repo | Report it. An unreviewed commit in someone else's repo is not a sync step. |
| Reading `docs/papers/` (plural) for a project's paper | That's `/paper-eli5`'s output — other people's papers, rewritten. You'd file a stranger's work in Kyle's portfolio notebook. |
| Globbing `docs/paper/` instead of matching the two exact filenames | The directory is not clean: `dim-stage/docs/paper/` holds an eli5 of someone else's paper next to the real deliverables. |
| Checking the working tree to decide whether a paper is merged | It reads whatever branch the repo is parked on. `git ls-tree origin/<default>` is the question you actually mean. |
| Querying the **local** default branch instead of `origin/<default>` | Kyle merges the PR on GitHub. Without a fetch the local ref never moves, so the command denies a paper that landed minutes ago. |
| Gating on the tree but hashing the file on disk | You certify the merged blob and ingest the branch's. The row then claims provenance the content doesn't have. |
| Re-running `--add-paper` to "make sure" | Without the step-2 already-present check that's a duplicate source *and* a duplicate row, and the duplicate reconciles `unchanged` forever. |
| Treating a git error as "no paper" | A missing clone and a paperless repo both print nothing. Exit status first, output second — otherwise the sweep reports clean over repos nobody read. |
| Passing a manifest row's absolute path to `git show <ref>:…` | It exits 128 (*"exists on disk, but not in …"*), so the row is never actually checked on any run. Split it into repo + repo-relative first. |
| Branching on `git ls-tree`'s exit status to detect absence | It exits 0 when the pathspec matches nothing. Absence is empty stdout; only a non-zero exit means unreadable. |
| Using `git show` alone to decide whether a paper was deleted | It returns 128 for "removed from the tree" *and* "couldn't read the repo". `ls-tree` separates them; `git show` is for the body once existence is settled. |
| Naming a shell variable `path` in these snippets | Kyle's shell is zsh, where `path` is tied to `PATH`. The assignment wipes the environment and every later command dies with `command not found`. |
| Writing `\|\| echo unknown` (or any non-terminal arm) as a failure handler | `echo` returns 0, so execution continues with the variable unset. Failure arms must end the row (`continue`) or the run (`exit 1`). |
| Running `git -C "$repo"` without checking `$repo` is non-empty | `git -C ""` is a documented no-op: it runs in the agent's own cwd repo, succeeds, and the wrong answer looks clean. |
| Adding a paper during `--add`, or a project during `--add-paper` | Each mode does the one thing it is named for; the other is a separate confirmed run. |

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
- You're about to snapshot a paper that `ls-tree` didn't find on `origin/<default>` — or
  you're reaching for the working-tree file after the tree query came back empty.
- You're about to add a file from `docs/papers/` (plural), or one whose name contains `eli5`.
- You're reading a paper's body or hash from a path on disk rather than from `git show`.
- A `git` command exited non-zero and you're about to report its empty output as a fact.
- You're adding a paper whose `path-or-url` already has a `paper` row in the manifest.
- You're about to run `git pull` in a project repo because `fetch` felt insufficient.
- A `git -C "$repo"` is about to run and you haven't proved `$repo` is non-empty — the empty
  case doesn't fail, it silently runs in whatever repo you're standing in.
- A failure arm in a snippet you're writing doesn't `continue` or `exit` — check what the
  next line does with the variable that arm failed to set.
