# Usage Playbook

The judgment companion to [`command-skill-reference.md`](command-skill-reference.md). The
reference doc is the **index** — what exists, what it does, one line each. This doc is the
**how to run it**: for every command, skill, and subagent, a card with a suggested model +
effort level, the concrete situations worth reaching for it in, and what it genuinely pairs
with.

Sections and their order mirror the reference doc exactly, so the two read side by side.
Every reference-doc row links to its card here with `config →`.

## Legend — reading a Run config

The `Run config` line is a model plus an effort level. Both come from the **Planner/Builder
protocol** in [`../CLAUDE.md`](../CLAUDE.md), which is the source of truth — this is a
restatement for convenience, not a second authority:

- **Fable 5.1** plans — judgment-first work: design calls with real tradeoffs, triage and
  routing, coaching, convention-setting. **Opus 5.5** builds — well-specified implementation
  and synthesis-heavy writing. **Sonnet 5.5** grinds — mechanical, checklist-scoped work.
- **Effort** (independent of the model): `ultracode` = broad parallelizable fan-out with
  adversarial verify · `max` / `xhigh` = ONE hard problem, or a design call with real
  tradeoffs · `high` = ordinary build work with judgment in it · `medium` / `low` =
  mechanical and checklist-scoped.
- Launch flags are per-invocation and never touch saved defaults:
  `claude --model claude-opus-5-5 --effort high`.
- **"inherits the session"** means the item runs inside a session you're already in and
  isn't worth switching models for — `/launch`, `pre-compact`, `visual-summary`. Everything
  else names a config because it's worth launching a session *for*.
- **Subagent cards state pinned config** from the agent file's own frontmatter. Those aren't
  recommendations — the dispatch already sets them.

Names in `Pairs well with` link to their card. A few unlinked names have no card here because
they aren't in this repo: `superpowers:*` and other plugin-provided items, and harness
built-ins like `run`. Each is labeled where it appears, so an unlinked name is never a dead
end.

## Keeping the two docs in sync

When a row is added, renamed, or deleted in
[`command-skill-reference.md`](command-skill-reference.md), the matching card changes in the
**same commit** — the two docs stay 1:1. The rule lives in [`../CLAUDE.md`](../CLAUDE.md)
under *Reference Doc Maintenance*, which covers both docs and treats every trigger in its
table as applying to the card as well as the row.

It's checked mechanically, so drift can't ride along unnoticed.
[`scripts/check-doc-sync.py`](../scripts/check-doc-sync.py) verifies that every index row
carries a `config →` link; that each link resolves to a real card rather than to a section
heading or to nothing; that the card a row links **is that row's item** (existence isn't
enough — a copy-pasted anchor or a rename propagated to only one doc leaves a row pointing at
some other item's card); that no two rows claim one card; that no card is an orphan; and that
no two headings collide into one anchor, which GitHub resolves by silently suffixing the second
and re-pointing an existing link at the wrong card.

It checks the *other* direction too: every tracked file matching the standard layout —
`commands/<name>.md`, `agents/<name>.md`, `skills/<name>/SKILL.md` — has a row, no row links
to a file that's been deleted or renamed, and a row's name matches the file it links. That
list comes from `git ls-files`, so a skill deliberately kept out of this public repo
(a gitignored skill folder) is excluded because git doesn't list it — not
because of an exemption list that would quietly drift. A path that looks like an item but
sits outside that layout (a command nested in a subdirectory, a skill folder with no
`SKILL.md`) can't be named, so it's reported as a warning instead of quietly exempted.

It runs as the repo's tracked `pre-push` hook (`.githooks/pre-push`, activated by `install.sh`
via `core.hooksPath`), so a mismatch blocks the push instead of landing — for terminal and
agent pushes alike, with `git push --no-verify` as the deliberate bypass. What it examines is
the **commits being pushed**, not the working tree: a card written before its row — the
natural authoring order — won't block an unrelated branch's push, and pushing an explicit
refspec checks that refspec rather than whatever happens to be checked out. By hand, against
the working tree, from anywhere:

```bash
python3 scripts/check-doc-sync.py
# doc sync check: in sync — <N> index rows, <N> cards, <M> item files.
```

Two things it still does **not** do. It can't verify project-specific items — their files
live in other repos, so an unlinked row is taken on faith. And it can't tell you what a card
should *say*.

One consequence worth knowing: a duplicate item name across projects is a hard error, not a
warning. If a second project ever gains an item that already has a card, both cards take a
project-suffixed heading — a `/verify` (DogHood) card becomes `#verify-doghood` — and both
rows get re-pointed to match.

---

## Global Commands

### Session Lifecycle

#### `/launch`

- **Run config:** inherits the session · `low` — it opens a window and starts a process;
  the judgment already happened in the run-config note it reads.
- **Reach for it when:**
  - A handoff or plan just ended with a paste-able prompt and a run-config note,
    and you want the fresh session open rather than assembled by hand.
  - Pass `--send` when you want it working immediately instead of pausing on your ⌘V.
- **Pairs well with:** `mattpocock-skills:handoff` (plugin — writes the paste-able prompt
  `/launch` opens).
- **Notes:** the prompt lands on the clipboard on **every** path, including failures, so a
  misfired launch costs one ⌘V rather than a regenerated handoff. Only Warp on macOS can
  truly auto-start the session; other terminals get the window plus the command to run, said
  plainly. It never types into an already-open window — that needs Accessibility permission
  and can hit whatever is focused. Identity of the started session starts from a PID that
  wasn't running before — necessary but not sufficient, since several Claude sessions are
  usually running and `/launch` exists to add another — and is confirmed by checking that
  PID's working directory and the `--model`/`--effort` head of its command line. The report
  names the exact tab to paste into, because a stray ⌘V into some other session looks
  exactly like success. The launched session gets a descriptive name via `claude --name`
  (override with `--name <session-name>`), and the Warp tab title reuses the same string —
  so the resume picker, the session lists, and the paste target all agree on what the
  session is called instead of showing an auto-generated title. CLI session names show in
  `claude --resume` and the desktop app; to have the named session appear in the
  claude.ai/mobile lists too, pass `--remote` — it launches via
  `claude --remote-control '<name>'`, still a normal terminal session locally with the
  phone as an extra control surface. Two `--remote` caveats: it can't combine with
  `--send` (Remote Control takes no initial prompt, so it's always a ⌘V paste), and it
  has claude.ai-side preconditions (paid-plan login, no custom `ANTHROPIC_BASE_URL`)
  that the launcher can't verify up front — a failed start gets reported honestly with
  the command to run by hand.

#### `/handoff-session`

- **Run config:** inherits the session · `medium` — mostly summarization, but it ends on a
  real run-config judgment for the next session.
- **Reach for it when:**
  - Context is getting long and the remaining work would be cleaner in a fresh session.
  - You want hard-won lessons and rejected options captured so the next session doesn't
    relitigate them.
  - Pass `--orchestrator` when the next session should **coordinate** an arc across worker
    sessions rather than build it — it swaps the block's structure for an arc decomposition,
    worker mechanics, gate delegation and boundaries, and lifts the ~600-word cap.
- **Pairs well with:** [`/launch`](#launch) (opens the fresh session and loads the prompt
  into it).
- **Notes:** it **stops the current work** after printing — that's deliberate. The
  run-config note lands outside the paste-able block, never inside it. Under
  `--orchestrator` the run-config guidance flips to Opus 5.5 (1M) at `high` — a coordinator
  reads far more than it writes — and a pick that wants Fable 5.1 is the signal that the
  decomposition isn't settled enough to dispatch yet.

## Global Skills

### Session & Context Management

#### `pre-compact`

- **Run config:** inherits the session · `medium` — everything it saves is already in
  context; the judgment is only in spotting what isn't on disk yet.
- **Reach for it when:**
  - A Matt Pocock-style session (wayfinder, grilling, to-spec, to-tickets, implement) is
    near ~150k and you're about to `/compact` with the work unfinished.
  - You typed `/compact` mid-turn and it arrived as a message instead of running.
  - You want a straight yes/no on whether compacting now would lose anything.
- **Pairs well with:** `mattpocock-skills:handoff` (plugin — the alternative when a fresh
  session beats compacting), [`wayfinder-map`](#wayfinder-map) (re-render after the
  ticket is confirmed and resolved), `mattpocock-skills:grilling` (plugin — the sessions
  it most often checkpoints).
- **Notes:** checkpoint only — it never runs `/compact`, never continues the work, and
  never resolves a grilling ticket before you confirm shared understanding. It pushes the
  feature branch but never touches `main`, merges, or opens PRs, and stages only files
  the session touched. The verdict comes from `git status` and the upstream ahead-count,
  and it never claims a token count. In a folder with no git repo or no remote it never
  creates one — it saves to disk and says "saved to disk, not pushed" instead.

#### `visual-summary`

- **Run config:** inherits the session · `low` — the work is picking three or four visuals
  and rendering them; the gathering is mechanical and the analysis is deliberately shallow.
- **Reach for it when:**
  - You want to *see* what a session or a branch amounted to instead of reading a recap.
  - A diff is large enough that `git diff --stat` tells you nothing about its shape.
  - You want something glanceable to share — the page publishes as an Artifact every run.
- **Pairs well with:** [`wayfinder-map`](#wayfinder-map) (where an effort stands, where
  this shows what a session did).
- **Notes:** mode is an argument — `conversation` (default), `branch`, or `worktree`. **A
  fresh session has no transcript**, so `conversation` only works in the session that did
  the work; use `branch` or `worktree` otherwise. Every number on the page is measured, and
  a section with nothing in it is omitted rather than padded. The page lands in
  `~/Projects/_visual-summaries/`, never in the repo it describes, unless `--out` says
  otherwise. It judges nothing — no risk flags, no next-move advice. `--no-publish`
  keeps it local.

#### `wayfinder-map`

- **Run config:** inherits the session · `low` — the script decides everything the page
  says; the skill only picks the effort, runs it, and publishes.
- **Reach for it when:**
  - You want to see what's takeable on a Wayfinder map without scanning `Blocked by:` lines.
  - You're sharing where an effort stands — the link is stable per effort, so it can be
    re-sent after every resolve.
- **Pairs well with:** [`visual-summary`](#visual-summary) (what a session did, where this
  shows where an effort stands).
- **Notes:** `map.html` is generated output beside `map.md` — never hand-edited, never the
  source of truth. Publishing is the skill's step, never the script's or the hook's; the
  Artifact URL is recorded in the map's Notes as a `Rendered map:` line. The Stop hook is
  installed once per machine with `scripts/install_hook.py` (backs up settings first,
  idempotent); `--no-publish` renders only.

#### `retire`

- **Run config:** Fable 5.1 · `xhigh` — ruling on what still steers you is convention-setting
  judgment with real tradeoffs; the counting underneath is a deterministic script that needs no
  model at all.
- **Reach for it when:**
  - Sessions start heavy, or an old convention keeps steering new work and you want it *gone*,
    not relocated.
  - You're removing one thing and want the bookkeeping done for you — row, card, referrers,
    ignore block, ledger: `/retire <item>`.
  - Quarterly, or before a big config change: `/retire --report` for a read-only look at what
    went cold. `--surface claude-md` makes "audit my CLAUDE.md" a one-liner.
- **Pairs well with:** `/code-review` (the built-in review each apply pass proposes).
- **Notes:** nothing is removed before you ratify its row, and unanswered rows are not applied —
  silence is never consent. Tracked items go through branch + PR; `settings.json`, `~/.claude.json`
  and plugin toggles change only after a per-file confirmation showing the exact edit list, with a
  backup first. Never touches a project repo. The inventory script exits non-zero rather than
  report a zero it didn't measure, so a broken read can't produce a false clean. Restore pointers
  live in [`retired.md`](retired.md).

#### `reweave`

- **Run config:** inherits the session · `medium` — the answer is already in context; never
  switch sessions to fold it in.
- **Reach for it when:**
  - You got an explanation, asked a follow-up, and now want one clean standalone version
    instead of splicing the two in your head.
  - A plan or design doc on disk needs a decision threaded through every dependent section,
    not appended as an addendum.
- **Pairs well with:** [`/handoff-session`](#handoff-session) (a reweaved plan hands off
  cleanly).
- **Notes:** output lands where the target lived — a chat answer returns to chat, a file gets
  rewritten in place. It never re-architects functional source code; a behavior change is an
  ordinary edit.

#### `day`

- **Run config:** Opus 5 · `medium` — sits resident all day; the gate needs judgment (is this
  polish or progress?) but every action is rule-following against a written list. Sonnet 5
  is fine on a light day.
- **Reach for it when:**
  - You're starting a working day driven by one Todoist project and want today's list
    briefed, a must-do set pinned, and a running log as you report outcomes in plain language.
  - You know you'll drift into tooling or polish mid-morning and want one-line pushback plus
    hourly pace check-ins.
  - The day is over and you want what slipped re-dated and the record written.
- **Pairs well with:** [`rebrief-a2c`](#rebrief-a2c) (run it first after a gap of more than
  a day).
- **Notes:** one Todoist project per run; the project hook (`.claude/day.md`, template in the
  skill's `references/`) supplies extra sources, outcome vocabulary, the polish list, and the
  wrap step. Check-ins ride a session cron, so closing the terminal kills them and `/day`
  re-arms them. Never sends anything; a bulk Todoist cleanup is a separate skill.

#### `architecture-viewer`

- **Run config:** Opus 5 · `high` — the extraction is judgment (what counts as a module,
  where a runtime dependency hides), and `high` is what buys the runtime edges an import
  parser would never find. Drop to `medium` for a re-map after correcting the grouping;
  the boundaries are already decided by then.
- **Reach for it when:**
  - You want to review the *structure* rather than the code — "where do the dependencies
    actually run", before a redesign or a big refactor.
  - You suspect a dependency cycle, or want to know which module is the expensive one to
    change.
  - A repo's stated layering rule (in its `CLAUDE.md` or README) needs checking against
    what the tree really does.
- **Pairs well with:** [`visual-summary`](#visual-summary) (what a session or branch did,
  where this is the repo's standing structure).
- **Notes:** no approval gate on the module boundaries, on purpose — the map is cheap to
  regenerate, so it renders first and you correct the grouping after looking. The
  validator is a hard gate: it opens every cited file and checks the line is in range,
  and it fails when modules leave source unaccounted for. **Never lower `--min-coverage`
  to make a run pass** — that number exists to catch the directory the extraction never
  noticed. Output lands in the target repo's `docs/architecture/` unless `--out` says
  otherwise, and a target repo that isn't the one you're working in gets files written
  but nothing committed. Publishing to a claude.ai Artifact is opt-in via `--publish`.
  v0 draws one drill level and no arrows leaving a drilled-in view; "open the code" is a
  click-to-copy `file:line`, never embedded source.

### Learning & Research

#### `youtube-transcript`

- **Run config:** Sonnet 5 · `low` — a fixed fallback chain with no judgment in it. The one
  decision (is Whisper worth it?) is Kyle's, not the model's.
- **Reach for it when:**
  - You have a YouTube URL and want the text — to read, to grep, or to feed something else.
  - A video has no captions at all and you're willing to spend CPU on local Whisper.
- **Pairs well with:** [`youtube-breakdown`](#youtube-breakdown) (the usual consumer — it
  calls this skill automatically for URL input, so you rarely invoke this one directly),
  [`teach-research`](#teach-research) (a talk's transcript is a legitimate source).
- **Notes:** needs `yt-dlp`, which is **not currently installed** — first run will offer
  `brew install yt-dlp`. Whisper is gated behind an explicit yes with the duration and
  audio size quoted, because it's the only step that costs real bandwidth and CPU.
  Conversion runs through `scripts/vtt-to-text.py`, which dedupes **per cue** rather than
  over a window of output lines — rollup captions repeat whatever is still on screen, so
  the overlap is a cue-boundary property, and any line-count window either misses it or
  eats the short utterances ("Yeah.", "Right.") that recur legitimately in interviews. The
  video title reaches the script through `--title-file` rather than the command line,
  because a title containing `$` or a backtick would otherwise execute.

#### `youtube-breakdown`

- **Run config:** Opus 5 · `high` — the four mode prompts are synthesis-heavy writing, and
  Critique mode in particular is real analytical work rather than summarization.
- **Reach for it when:**
  - You watched (or want to triage) a video and want structured notes rather than a
    summary — Study Notes to retain it, Quick Reference to decide if it's worth the time,
    Critique to pressure-test a contrarian claim, Actionable Insights to leave with a plan.
  - You have a transcript from anywhere and want the same four-mode treatment.
- **Pairs well with:** [`youtube-transcript`](#youtube-transcript) (supplies the text for a
  URL),
  [`teach-research`](#teach-research) / [`teach`](#teach) (where a "Further Reading"
  section leads if the topic deserves a workspace),
  [`youtube-breakdown` (home-base)](#youtube-breakdown-home-base) (the hub-native fork,
  which writes to the hub's own stores instead).
- **Notes:** always asks which mode before generating — the four modes are different tools,
  not lengths, and the auto-router that would pick for you is specced but deliberately off.
  Saving asks for the destination every run: it proposes `~/Learning/youtube-notes/` and
  lists the real teach workspaces under `~/Learning/` as alternatives, since filing a
  breakdown into one puts it where `/teach` will read it. One mode per run.

#### `teach-research`

- **Run config:** Opus 5 · `high` — the skill's own finder/cacher fan-out does the parallel
  work; the session around it is orchestration plus synthesis-heavy digesting.
- **Reach for it when:**
  - You're about to start learning a topic with `/teach` and want the workspace stocked
    first — mission captured, sources vetted, digests cached — so lesson one is a lesson,
    not a search.
  - A teach workspace's `RESOURCES.md` is thin, or its `## Gaps` section has grown
    (top-up mode).
- **Pairs well with:** [`teach`](#teach) (the consumer — run it right after this).
- **Notes:** typed-only (`disable-model-invocation: true`) — fires only on `/teach-research`.
  `--auto` skips the interactive pauses (mission confirm + curation gate); the mission
  interview still runs when no `MISSION.md` exists, so a truly unattended run needs
  `MISSION.md` to already exist. Writes only `MISSION.md`, `RESOURCES.md`, and `research/` —
  the teach skill itself is never edited.

## Project-Specific Items

Cards for items that only exist inside their project. Run configs assume you're launching a
session *in that repo*.

### A2C Auctions

#### `replenish-a2c`

- **Run config:** Opus 5 · `ultracode` for a full multi-lane refill — it runs a
  pipeline-audit lane plus N prospecting-lens lanes and an independent default-skeptical
  verifier pass, which is fan-out + adversarial verify. Drop to `high` for a single-lens
  top-up.
- **Reach for it when:**
  - The prospect pipeline has run thin and you need new leads *and* an audit of the gaps in
    what's already listed.
  - A hunting ground is under-worked and you want it mined systematically rather than by
    memory.
- **Pairs well with:** [`stage-a2c`](#stage-a2c) (stages what this drafts),
  [`rebrief-a2c`](#rebrief-a2c) (reconciles what actually happened afterward),
  [`replenish`](#replenish) (the coding original this refactors).
- **Notes:** the project's house rules are gates, not suggestions — a do-not-contact list, a
  never-re-add ruled-out list, channel-specific pitch framing, and no invented contact
  addresses. Two gates: one combined steering round (compressible, never deletable) and one
  merged review hard stop before anything touches the live prospect files. Agent budget is
  stated at launch and hard-capped around 15.

#### `stage-a2c`

- **Run config:** Sonnet 5 · `medium` — reconcile the unsent queue, reuse or write the
  draft, stage per channel. Rule-following work with outward-facing stakes.
- **Reach for it when:**
  - Prospects are found and drafted but the messages are still sitting there unsent.
  - You want the unsent queue reconciled across sources before anything gets staged twice.
- **Pairs well with:** [`replenish-a2c`](#replenish-a2c) (finds and drafts),
  [`rebrief-a2c`](#rebrief-a2c) (catches what went out and what didn't).
- **Notes:** **it never sends** — Gmail drafts and a LinkedIn compose box, and it stops
  there. One HARD STOP confirming the batch (all / some / none) before it touches Gmail or
  the browser; "none" ends the run cleanly. Unverified addresses get a staged draft with an
  empty `To:` and a flag. Trackers are not auto-marked sent.

#### `call-brief`

- **Run config:** Sonnet 5 · `medium` — four fixed sources, a fixed output shape, and a
  reference example to match.
- **Reach for it when:**
  - You're about to dial one prospect and want every line you'd say written out in full.
  - A task's script has gone stale and you need it rebuilt from the files before the call.
- **Pairs well with:** the A2C `day` skill (logs the outcome the brief sets up),
  [`stage-a2c`](#stage-a2c) (the chaser the voicemail section points at), [`narrate`](#narrate)
  (`--audio`).
- **Notes:** one contact per run, and every spoken section comes **twice** — detailed bullets
  to talk from, the full-sentence script blockquoted under them, same ground in the same order
  so his eye can jump between the layers (the voicemail is script only). Numbers in the task
  and `prospects.md` must agree or the header flags it — never resolved by picking one. Only
  the two figures the skill names are ever spoken; every other commercial question routes to
  the principal. `--audio [short|long]` renders a spoken version through `narrate` after the
  brief prints: `short` (default) is the prep briefing for the walk to the car; `long` adds the
  opener and voicemail read as written, the one place in the setup where narration is
  deliberately verbatim. The MP3 and its script land inside the A2C folder, never the shared
  audio dir, because both name a real prospect.

#### `sync-check`

- **Run config:** Opus 5 · `high` — mostly deterministic checkers, but the whitelist boundary
  is real judgment and the thing it edits is a file full of identifiers that must never be
  guessed. Scheduled runs use the same pair; override with `SYNC_CHECK_MODEL`.
- **Reach for it when:**
  - You want to trust tomorrow's calendar block without auditing it first.
  - Several sessions have written to Todoist and you're not sure the blocks kept up.
  - Something was corrected in `prospects.md` and you want to know where the old version
    still lives.
- **Pairs well with:** [`day`](#day) (the sweep is what makes the morning block trustworthy),
  [`rebrief-a2c`](#rebrief-a2c) (re-entry after a gap; the sweep is the standing version of
  the same reconciliation), [`replenish-a2c`](#replenish-a2c) (run the sweep after a refill).
- **Notes:** the whitelist is **closed** and lives in
  `.claude/skills/sync-check/references/whitelist.md`. It adds a missing row, corrects a row's
  time, drops a plainly-transcribed dead row and flags a hand-authored one — nothing else.
  It never changes a name, number, address or company; never deletes, merges or re-dates a
  Todoist task; never edits a past block or a day log's Log/Wrap; and has no send path at
  all, enforced twice (no send tool is loaded, and `bin/run-sync-check.sh` denies every send
  tool at the process boundary). A block that reads back at 7,900+ characters is never
  written, because at that size the read itself may be truncated. `CLEAN` is unreachable when
  a source failed — that becomes `COULD NOT COMPLETE` with the reason. Regression test:
  `python3 .claude/skills/sync-check/scripts/selftest.py`.

#### `morning-briefs`

- **Run config:** Opus 5 · `high` — the orchestrator itself decides little (which tasks are
  dials), but every subagent it spawns is a `call-brief` run, and that is judgment about a
  lead. Scheduled runs use the same pair; override with `MORNING_BRIEFS_MODEL`.
- **Reach for it when:**
  - It is a block morning and you want every brief on disk before the first dial.
  - `/day` shows a dial with no section in today's briefs file (the gap-fill).
  - Tomorrow's roster is set at the wrap and you want tomorrow's briefs built tonight
    (`--date`).
- **Pairs well with:** [`call-brief`](#call-brief) (the thing it fans out; also what
  regenerates a stale section), the A2C `day` skill (prints the file and fills gaps),
  [`sync-check`](#sync-check) (keeps the blocks the job reads trustworthy).
- **Notes:** no write path into the pipeline — no Todoist write, no calendar write, no
  Gmail draft or send — and `bin/run-morning-briefs.sh` denies every one of those tools at
  the process boundary. The dial rule is explicit (inside a block window, no non-dial
  marker, a phone number present); everything else lands in the file's `Skipped:` line so a
  misclassification is visible, never silent. Parts live in `daily/briefs/YYYY-MM-DD/`; a
  part is reused only when its task id and due time are unchanged. Regression test:
  `python3 .claude/skills/morning-briefs/scripts/assemble_briefs.py --selftest`.

#### `rebrief-a2c`

- **Run config:** Sonnet 5 · `medium` — two live sweeps and a reconciliation with a fixed
  tiebreaker rule.
- **Reach for it when:**
  - You're coming back after time away and need to know what actually happened before doing
    anything.
  - Replies, bounces, and never-sent drafts are mixed together and the files disagree with
    reality.
- **Pairs well with:** [`stage-a2c`](#stage-a2c) (the unsent queue it surfaces),
  [`replenish-a2c`](#replenish-a2c) (when the rebrief shows the pipeline is thin),
  [`reorient`](#reorient) (the coding equivalent of this move).
- **Notes:** sent mail is the tiebreaker over the files. Ambiguous records are marked
  "unconfirmed" and raised as questions — never resolved by guessing. One hard gate covers
  every write (status updates, gap-fill tasks, reply-path drafts), and drafts are staged,
  never sent.

### clinical-data-etl

#### `add-source`

- **Run config:** Opus 5 · `high` — end-to-end pipeline wiring across schema, loader, raw
  table, dbt staging, and possibly a new star. Well-specified, many touch-points.
- **Reach for it when:**
  - A brand-new raw data source needs to land in the pipeline without hand-tracing which
    layers it touches.
  - The source introduces a new analytical subject and may need its own star schema.
- **Pairs well with:** [`new-dbt-model`](#new-dbt-model) (the smaller downstream scaffold),
  [`/tdd-loop`](#tdd-loop) (the tests step),
  [`spec-miner`](#spec-miner) (if the pipeline's contracts need writing down).
- **Notes:** ingestion is idempotent by design — a re-run is a no-op and existing rows aren't
  overwritten.

#### `new-dbt-model`

- **Run config:** Sonnet 5 · `low` — a convention-following scaffold with a fixed checklist.
- **Reach for it when:**
  - You need a model in the right layer with the right prefix and the paired `schema.yml`
    entry, without rediscovering the house pattern.
  - An incremental model needs the established config pattern.
- **Pairs well with:** [`add-source`](#add-source) (what usually creates the need).
- **Notes:** the paired `schema.yml` entry with tests is required, not optional; explicit
  column projections only (never `select *`), and architectural guardrails about where labels
  live are enforced rather than negotiated.

### Constellation

#### `new-planet`

- **Run config:** Sonnet 5 · `low` — a contract-following scaffold modeled on an existing
  exemplar.
- **Reach for it when:**
  - The planet is already designed (id, name, hint, gate layout) and you just need every
    side of the contract wired.
  - You want the registry entry placed correctly — registry order *is* the progression.
- **Pairs well with:** [`new-power`](#new-power) (the powers a planet gates on),
  [`/verify-planet`](#verify-planet) (proves it actually plays).
- **Notes:** miss a side of the contract and the level never appears, ships untested, or
  breaks the unlock chain — that's why the skill walks all of them. Assumes the design is
  done; it scaffolds, it doesn't invent a level.

#### `new-power`

- **Run config:** Sonnet 5 · `low` — the same multi-sided scaffold shape.
- **Reach for it when:**
  - A new astronaut power needs its protocol literal, Spellbook tile, puzzle component,
    registration, and cast handler all wired in one pass.
- **Pairs well with:** [`new-planet`](#new-planet) (a planet gates on the power),
  [`/verify-planet`](#verify-planet) (verifies the gate it unlocks).
- **Notes:** the phone-side registration is two edits plus an import — easy to half-wire by
  hand, which is the whole reason this exists.

#### `/verify-planet`

- **Run config:** Sonnet 5 · `medium` — a scripted Playwright verification against a
  documented playbook.
- **Reach for it when:**
  - A planet is scaffolded and you want a headless per-step PASS/FAIL verdict rather than
    playing it yourself.
  - You want the negative tests (the ones that prove a gate actually gates) run consistently.
- **Pairs well with:** [`new-planet`](#new-planet) (what it verifies),
  [`/smoke-test`](#smoke-test) (the manual, project-agnostic counterpart).
- **Notes:** needs the dev server running and the pinned Playwright MCP; it stops and says so
  rather than faking a boot. It polls state and never sleeps, asserts on state fields and
  **never pixels**, and skips negatives that don't apply to the planet under test.

#### `/moonshot`

- **Run config:** deprecated — use [`/brainstorm`](#brainstorm) in Moonshot mode and take its
  card's config (Fable 5 · `ultracode`).
- **Reach for it when:** never, by preference. It still works as an alias that pins
  `/brainstorm` to Moonshot and skips the mode pick, but the multi-mode command is the one to
  reach for.
- **Pairs well with:** [`/brainstorm`](#brainstorm) (what it now delegates to entirely).

### DogHood

#### `adr-new`

- **Run config:** Sonnet 5 · `low` — numbered-template scaffold with an index row.
- **Reach for it when:**
  - A decision was just made and you want it recorded before the reasoning evaporates.
  - You don't want to hand-check which ADR number is next or forget the README row.
- **Pairs well with:** [`/new-scope`](#new-scope) (scope briefs name the ADRs to write),
  [`new-migration`](#new-migration) (schema decisions usually want an ADR).
- **Notes:** never delete an ADR — superseded and deprecated ones stay as historical record.

#### `new-migration`

- **Run config:** Sonnet 5 · `medium` — boilerplate scaffolding, but the RLS and privacy
  content deserves attention.
- **Reach for it when:**
  - A schema change needs a timestamped migration with RLS-by-default rather than
    RLS-remembered.
  - The change touches policies and wants a pgTAP test stub alongside it.
- **Pairs well with:** [`adr-new`](#adr-new) (record the decision),
  [`/verify`](#verify) (picks up pgTAP and the RLS auditor for this diff),
  [`/ship`](#ship) (a migration altering an existing table stamps the high gate tier).
- **Notes:** a migration already on `origin/main` is **never** edited — you write a new one.
  The privacy invariant is hard: no lat/lng column on any user-attributable table. Build-phase
  changes stay additive; drops need a deprecation period.

#### `/new-scope`

- **Run config:** Sonnet 5 · `low` — a template scaffold from the canonical brief format.
- **Reach for it when:**
  - You're starting a unit of shippable work and want the brief that becomes exactly one PR.
  - You want the privacy / no-go check and the ADR list forced into the plan up front.
- **Pairs well with:** [`adr-new`](#adr-new) (the ADRs the brief names),
  [`/ship`](#ship) (consumes the brief's gate fields),
  [`/verify`](#verify) (the checks the brief implies).
- **Notes:** STOPs rather than overwriting an existing brief. Its gate fields (blast radius,
  manual-smoke-required) are what `/ship` reads later — filling them in casually costs you at
  ship time.

#### `/reconcile-backlog`

- **Run config:** Sonnet 5 · `medium` — a fixed cross-check and a drift table.
- **Reach for it when:**
  - The docs claim things the git history doesn't support, or vice versa.
  - You want the drift shown before anything is edited.
- **Pairs well with:** [`/scheduled-reconcile`](#scheduled-reconcile) (the unattended weekly
  twin), [`project-wiki`](#project-wiki) (the wiki equivalent of the same discipline).
- **Notes:** ground truth comes from the code and git, never from another doc's claim about
  the code. It never deletes rows — completed items stay — and it raises genuine uncertainty
  as a question instead of "fixing" it by guessing.

#### `/scheduled-reconcile`

- **Run config:** Sonnet 5 · `medium` — the same reconcile, wrapped for an unattended weekly
  run.
- **Reach for it when:**
  - You want doc drift caught on a schedule instead of noticing it at ship time.
  - Add `--dry-run` to see what it would do without editing.
- **Pairs well with:** [`/reconcile-backlog`](#reconcile-backlog) (the interactive original
  it wraps).
- **Notes:** nobody's watching, so it asks nothing: it either closes the loop quietly
  (docs-only, low tier, merged autonomously) or escalates cleanly with a PR for ambiguous
  cases. It never leaves a half-finished state, and never resolves uncertainty by guessing.

#### `/ship`

- **Run config:** Sonnet 5 · `medium` — a gate-aware commit → push → PR recipe with a fixed
  decision table.
- **Reach for it when:**
  - Work is done and you want it landed with the blast-radius tier stamped and the
    manual-smoke gate honored.
  - You want the guard-hook-safe PR recipe rather than rediscovering why a heredoc failed.
- **Pairs well with:** [`/verify`](#verify) (produces the Verification block for the PR
  body), [`/new-scope`](#new-scope) (the brief it links and reads gates from),
  `/code-review` (the review gate before a merge).
- **Notes:** **it explicitly does not merge.** Stages explicit paths only, pushes and opens
  the PR as separate steps (a guard hook false-positives otherwise), and self-stamps the gate
  tier when no audit exists.

#### `/verify`

- **Run config:** Sonnet 5 · `medium` — deterministic path→check mapping.
- **Reach for it when:**
  - You need to know which checks this specific diff actually requires — typecheck, deno
    check, pgTAP, the RLS auditor — without over- or under-running.
  - You want a paste-ready Verification block for the PR body.
- **Pairs well with:** [`/ship`](#ship) (pastes its output),
  [`/smoke-test`](#smoke-test) (the manual half),
  [`new-migration`](#new-migration) (what pulls in the database checks).
- **Notes:** checks are **cumulative** — every matching row runs, not just the most specific.
  It never reports a check as passed unless it ran in this session, and environment
  fallbacks are stated honestly rather than implied as verification.

### home-base (Learning Hub)

#### `course-builder`

- **Run config:** Opus 5 · `high` — plan-then-autonomous authoring of every material after
  one approval. It fans out one subagent per module on its own, so you don't need `ultracode`
  to get the parallelism.
- **Reach for it when:**
  - You want a full course for a topic — lessons, exercises, visualizations, flashcards,
    quizzes, reading — not a single explainer.
  - You'd rather approve a syllabus once than review 30 materials one at a time.
- **Pairs well with:** [`/build-course`](#build-course) (the thin entry point),
  [`episode-review`](#episode-review) (quizzes the material afterward),
  [`review-next`](#review-next) (ranks what to revisit),
  [`youtube-breakdown`](#youtube-breakdown-home-base) (its notes are usable course input).
- **Notes:** the syllabus approval is the **single** human checkpoint — nothing is authored
  before it, and any deviation from the approved syllabus is reported at the end. NotebookLM
  enrichment is separately gated. Every subagent gets a copy-paste-complete payload so it
  never has to infer authoring context.

#### `episode-review`

- **Run config:** inherits the session · `low` — an interactive quiz and a progress write via
  the backing CLI.
- **Reach for it when:**
  - You just finished an episode and want reflection plus a real quiz rather than a vague
    sense you understood it.
  - You want the score and listened status logged so the planner has signal.
- **Pairs well with:** [`course-builder`](#course-builder) (authors the quizzes),
  [`review-next`](#review-next) (reads what this logs),
  [`audio-series`](#audio-series) (what you just listened to).
- **Notes:** grading, the answer key, and every database write belong to the backing CLI —
  it never grades in its head or reveals answers early. Hints don't cost score.

#### `review-next`

- **Run config:** Sonnet 5 · `low` — read-only ranking out of the progress store.
- **Reach for it when:**
  - You have 20 minutes and want the shakiest material surfaced instead of re-reading what
    you already know.
- **Pairs well with:** [`episode-review`](#episode-review) (writes the signal this reads),
  [`course-builder`](#course-builder) (the material it ranks).
- **Notes:** read-only — SELECTs only, never a write to the store. It prefers the backend
  engine when it's running and falls back to raw queries offline.

#### `youtube-breakdown` (home-base)

- **Run config:** Sonnet 5 · `medium` — a transcript into one of four fixed output formats.
- **Reach for it when:**
  - A video has real content and you want Study Notes, a Quick Reference, a Critique, or
    Actionable Insights out of it — not a summary.
  - You want the output saved hub-native and, optionally, promoted into a tracked topic.
- **Pairs well with:** [`course-builder`](#course-builder) (video notes as course input),
  [`catalog-doctor`](#catalog-doctor) (checks the catalog afterward),
  [`nlm-skill`](#nlm-skill) (the gated NotebookLM bridge).
- **Notes:** it confirms the mode rather than auto-picking silently, never invents citations
  or facts absent from the transcript, and stays read-only toward NotebookLM sidecars.

#### `catalog-doctor`

- **Run config:** Sonnet 5 · `low` — a read-only drift report against a documented
  definition of correct.
- **Reach for it when:**
  - The hub's catalog and what NotebookLM actually holds have drifted and you want the delta
    named.
  - A topic disappeared from the hub and you need to know which layer lost it.
- **Pairs well with:** [`api-types-sync`](#api-types-sync) (the other reconciliation),
  [`review-next`](#review-next) (both read the same stores),
  [`video-series`](#video-series) / [`audio-series`](#audio-series) (what generated the
  artifacts it checks).
- **Notes:** read-only in both directions — it never writes to sidecars or under the
  NotebookLM projects directory, and never runs a mutating `nlm` subcommand. It reports the
  edits *you* should make.

#### `api-types-sync`

- **Run config:** Sonnet 5 · `medium` — mechanical type reconciliation with a house style to
  preserve.
- **Reach for it when:**
  - Backend Pydantic models changed and the frontend types are now lying.
  - A new endpoint shipped and the client imports need to catch up.
- **Pairs well with:** [`catalog-doctor`](#catalog-doctor) (the sibling drift check).
- **Notes:** read-only on the backend — it changes the frontend to match, not the reverse.
  The answer-key-free invariant is hard: never add a correct-answer field to a
  frontend-visible type.

#### `/build-course`

- **Run config:** Opus 5 · `high` — a thin entry point to
  [`course-builder`](#course-builder); same config as the skill.
- **Reach for it when:**
  - You want to start a course by naming a topic and level rather than describing the whole
    workflow.
- **Pairs well with:** [`course-builder`](#course-builder) (the skill it delegates to).
- **Notes:** same single approval gate — syllabus first, author nothing until you approve.

### party-line (project)

#### `party-line`

- **Run config:** inherits the session — it is a messaging surface, not a reasoning task.
  The seats it coordinates are pinned separately (Sonnet 5 per D10).
- **Reach for it when:**
  - Two sessions need to talk while both are alive — a co-op playtest, or a successor
    asking its predecessor something the predecessor can still answer itself.
  - You want an idle session to be woken by traffic rather than polled by hand.
- **Pairs well with:** [`ghost`](#ghost) (the dead-predecessor case — the two compose rather
  than compete), [`/handoff-session`](#handoff-session) (the note is the async channel, this is the live one).
- **Notes:** `watch` is a doorbell that marks nothing seen; `poll` is the only thing that
  delivers, and a watcher fires once — re-arm it or the session silently stops receiving.
  **Trust boundary:** anything that can write the channel directory can speak on the
  channel, and a delivered message starts a turn — never join in a cwd you don't trust.

#### `auto-handoff`

- **Run config:** inherits the session — it fires *inside* whatever session hit the trigger,
  and the handoff it writes is composed by that session. The successor's model and effort come
  from the run-config note it is proposing, not from this skill.
- **Reach for it when:**
  - You don't — it reaches for itself. It fires when a session writes a run-config note naming
    a different model (T1 — the Planner/Builder Protocol makes that handoff mandatory), when a
    milestone's done-bar is discharged with results written or a reviewed branch merges CLEAR
    with nothing already queued (T2), or when the Stop gate blocks at `PARTY_LINE_WATCH_AT`
    percent of context (T3).
  - You want to ask for one anyway: "should we hand off", "propose a handoff".
- **Pairs well with:** [`/handoff-session`](#handoff-session) (whose composition spec it follows — it calls the
  writer itself rather than invoking the command, and where this flow lands at M4),
  [`/launch`](#launch) (step 4a, on yes), [`ghost`](#ghost) (what the successor reaches for
  when the note leaves a gap).
- **Notes:** propose-first by design — the note and the paste-able block are written *before*
  the question, so a declined or unanswered proposal still leaves the artifact. One yes/no, no
  timeout, no third option, and never in a headless seat. Every run appends a row to
  `~/.claude/party-line/proposals.jsonl`; T1/T2 fire once per trigger per session, while T3's
  once-per-crossing discipline lives in the gate. `PARTY_LINE_NOTIFY=off` silences the push
  that announces it; `PARTY_LINE_WATCH=off` silences T3's gate; `auto` is recognised, resolves
  to propose, and warns — full-auto graduates on ledger evidence by a decision, never by an
  env var.

#### `reaper`

- **Run config:** inherits the session — at R2 it fires *inside* the successor, in the turn
  where that session ingested its predecessor's handoff note; at R1 it fires in whatever
  session you said "close it" to. Nothing about it is model-sensitive; every judgment it could
  have made is a check in `handoff/reap.mjs` instead. The one thing the model does own at R1 is
  turning your sentence into a search term, and an ambiguous term makes the flow ask rather
  than pick.
- **Reach for it when:**
  - You don't — it reaches for itself, one turn after a handoff lands. That is R2: this session
    consumed a note, and the session that launched it is still running.
  - You want a window gone and can say which: "close the party-line one", "close that doghood
    window", or plain "close it" when only one is open. That is R1, and it can close either end
    of a launch — the window you point at is as often the successor as the predecessor.
  - You want to see the clutter without proposing anything: `node handoff/cli.mjs
    reaper-status` lists every launch row with a live probe of both ends and kills nothing.
- **Pairs well with:** [`auto-handoff`](#auto-handoff) (whose accepted proposal writes the
  registry row this reads — spawn and teardown are the two halves of one loop),
  [`/launch`](#launch) (whose *Verified-start* identity discipline the kill path inherits, with
  the stakes inverted).
- **Notes:** propose-first, and the ask is the backstop the design leans on — no SIGTERM
  without a yes, one machine-initiated proposal per registry row ever, and a decline is
  permanent *against the machine* (you can still close that session by name later; R1 is you
  acting, not a proposal). Registry-only targeting holds at both signals: a session that never
  handed off through the flow is structurally invisible, and naming it by hand does not change
  that. A dismissal term is matched against the launch's project, the process's directory and
  its Warp tab title — never the command line, because an argv carries the whole opening
  prompt and would match every session ever *told* about the one you meant. Close ≠ destroy: it
  ends a process and frees a window, and no path in it deletes a transcript, a note, or a state
  file. If the target survives SIGTERM it says so and stops — no SIGKILL, no retry. An on-call
  session — one with an armed intercom watcher — is refused with the reason even when you named
  it, and the refusal is transient: fire the watcher and ask again.

#### `ghost`

- **Run config:** inherits the session; the answer itself is produced by a subagent, so no
  API call and no separate model pin.
- **Reach for it when:**
  - A handoff briefing left a gap — "what did they already try?", "where were they when
    they stopped?" — and the session that knows is gone.
  - You want testimony from the predecessor's transcript rather than your own reconstruction
    of what it probably did.
- **Pairs well with:** [`party-line`](#party-line) (use that instead if the predecessor is
  still running), [`/handoff-session`](#handoff-session) (the note names the transcript this reads).
- **Notes:** expect it to be strong on *what happened* and weak on *why* — measured on CLI
  2.1.220, thinking blocks persist with no text, so reasoning that never reached a reply is
  not recoverable. The rendering says so at the top when it applies; absence of a recorded
  rationale is not evidence there wasn't one.

#### `/threshold`

- **Run config:** inherits the session — it reads one file and asks one question; the judgment
  is yours, not the model's.
- **Reach for it when:**
  - You want to be warned about context earlier or later than 85% *in this project* — a repo
    with a different window size, or a stretch of work you'd rather not be interrupted during.
  - T3 just proposed and you want it to stop asking for a while: raise the threshold and the
    gate goes quiet until the new number.
  - You want to know where you stand — the number in force, which layer set it, and the current
    reading with the window size it is a percentage *of*.
- **Pairs well with:** [`auto-handoff`](#auto-handoff) (this sets the number that fires its T3
  trigger), [`/handoff-session`](#handoff-session) (what a firing eventually produces).
- **Notes:** project-scoped and stored, resolved *explicit `PARTY_LINE_WATCH_AT` > the project's
  setting > 85*. The gate is a fresh process per turn boundary, so a change is honoured at the
  very next turn with nothing restarted — and **a change re-arms a gate that already fired**, so
  lowering the threshold below where you already are proposes at that next turn (the picker says
  so before you commit it). A persistent `export PARTY_LINE_WATCH_AT=…` is **not** a machine-wide
  default: there is no stored global layer, and env sits *above* the project layer, so an export
  silently defeats every project setting. It is a stepped picker, not a slider — Claude Code has
  no slider primitive. Turning T3 off entirely is a different setting (`PARTY_LINE_WATCH=off`).

### stopwatch (Tempo)

#### `/add-panel`

- **Run config:** Sonnet 5 · `low` — a registered scaffold plus the four wiring touch-points
  and a cache bump.
- **Reach for it when:**
  - You want a new Rhythm Insights panel that's actually registered, slotted, documented, and
    cached — not just a file.
- **Pairs well with:** [`/new-engine-module`](#new-engine-module) (the same wiring ritual),
  [`/run-tests`](#run-tests) (the deps-injected tests it scaffolds).
- **Notes:** panels take dependencies injected and pin the clock in tests — never module
  globals or the real clock. Per-panel UI state lives in panel state, not the URL hash. It
  does **not** commit; you land it yourself.

#### `/new-engine-module`

- **Run config:** Sonnet 5 · `low` — a wiring scaffold with a fixed four-point checklist.
- **Reach for it when:**
  - A new `js/<name>.js` module needs its script tag at the right load-order slot, the
    CLAUDE.md file-map entry, the service-worker ASSETS entry, and a cache bump.
  - You've been bitten by a module that works locally and 404s from cache in production.
- **Pairs well with:** [`/add-panel`](#add-panel) (the panel-flavored version),
  [`/run-tests`](#run-tests) (verify the wiring).
- **Notes:** it won't skip a step silently — if it can't complete one it stops and says
  which. It reuses existing utilities rather than re-implementing them, and does **not**
  commit.

#### `/fix-bug`

- **Run config:** Opus 5 · `high` — root-cause debugging against known-failure playbooks;
  ordinary build work with real diagnostic judgment.
- **Reach for it when:**
  - Something's broken in Tempo and you want the false alarms ruled out first (a stale
    service-worker cache is the #1 one).
  - You want a regression test before the fix, not after.
- **Pairs well with:** [`/run-tests`](#run-tests) (the verification step),
  `superpowers:systematic-debugging` (the project-agnostic discipline),
  [`/ship-pr`](#ship-pr) (lands the fix).
- **Notes:** never trusts a browser tab opened before the edit. Fixes minimally, per repo
  conventions, and does not push or open a PR unless you ask.

#### `/run-tests`

- **Run config:** Sonnet 5 · `low` — diff-driven suite selection with a documented
  adjudication rule.
- **Reach for it when:**
  - You want the right suites for what you changed, not all of them or the wrong one.
  - A test failed and you want it adjudicated for flake before you believe it.
- **Pairs well with:** [`/fix-bug`](#fix-bug) (what usually calls it),
  [`/ship-pr`](#ship-pr) (the pre-flight needs a trustworthy verdict).
- **Notes:** it will not edit code or tests to silence a failure — it reports and stops. Some
  scripts that look like tests actually write data and are never run as tests.

#### `/ship-pr`

- **Run config:** Sonnet 5 · `medium` — a Definition-of-Done pre-flight plus house-convention
  PR mechanics.
- **Reach for it when:**
  - Work meets the DoD and you want the guard checks pre-run instead of discovering them in
    a blocked commit.
  - You want the branch, commit, push, and PR done to house convention in one pass.
- **Pairs well with:** [`/run-tests`](#run-tests) (feeds the pre-flight),
  [`/fix-bug`](#fix-bug) (the usual upstream),
  `/code-review` (the gate before merging).
- **Notes:** STOPs at merge etiquette by default — never merges or pushes `main` without an
  explicit go-ahead **for this PR**; blanket prior approvals don't carry over. CI gates PRs
  only, which is exactly why the direct-push path stays closed.

### forge-gap

#### `/document-stage`

- **Run config:** Opus 5 · `medium` — teaching plus recall synthesis over a stage you just
  finished.
- **Reach for it when:**
  - A stage in the learning spine is done and the concepts are still fresh enough to be
    tested on.
  - You want the documentation *and* to find out what you can't actually explain yet.
- **Pairs well with:** [`/wrap`](#wrap) (the project-agnostic version of the same instinct),
  [`seed-hunt`](#seed-hunt) (what runs when the whole project closes),
  [`research-paper`](#research-paper) (the end-of-project write-up).
- **Notes:** never describes code it hasn't read. Stages docs by name (never `git add -A`)
  and merges the docs PR on the remote.

---

### Life Nodes

#### `sync` (Life Nodes)

- **Run config:** inherits the session — it closes whatever Code session changed the vault.
- **Reach for it when:**
  - A session in the vault changed skills, notes, or an artifact note and should land now
    with a written message instead of waiting for the hourly auto-committer.
  - You want the auto-committer's health (last push, consecutive failures) in one line.
- **Pairs well with:** [`build-artifact`](#build-artifact-life-nodes) (the `url` it writes
  needs a commit), [`audit`](#audit-life-nodes) (run it first before a phase sign-off).
- **Notes:** Kyle-only (`disable-model-invocation`). Fast-forward only: a diverged remote is
  shown, never merged. A `plugins/` change bumps the patch version, and Cowork needs
  **Update** pressed on the `kyles-nodes` marketplace to see it.

#### `build-artifact` (Life Nodes)

- **Run config:** Opus 5 · `high` — view code built from a written spec, with a palette gate
  and a real publish.
- **Reach for it when:**
  - An artifact note's Views are written and the page doesn't exist yet, or the Views changed.
  - The page needs republishing to the same `url` after a view fix.
- **Pairs well with:** [`rebuild-artifact`](#rebuild-artifact-life-nodes) (its steps run
  inline at the end), the bundled `dataviz` skill (the palette validator it gates on).
- **Notes:** Kyle-only. One artifact per note, forever: a note with a `url` is always
  republished to it. Writes only `index.html` and, on first publish, `url`.

#### `rebuild-artifact` (Life Nodes)

- **Run config:** Sonnet 5 · `low` — deterministic; `scripts/lifenodes.py` computes every
  document.
- **Reach for it when:**
  - `log` or `audit` reports an artifact as stale.
  - A push from Cowork failed, or entries were corrected in a way you want reflected now.
- **Pairs well with:** [`audit`](#audit-life-nodes) (finds staleness),
  [`build-artifact`](#build-artifact-life-nodes) (publishes first when there's no `url`).
- **Notes:** no confirm gate: it changes no vault file and a rerun is always safe. A month
  the vault has emptied is written with no entries, so a retraction clears.

#### `audit` (Life Nodes)

- **Run config:** Sonnet 5 · `medium` — script-driven checks, then careful one-line repairs.
- **Reach for it when:**
  - A phase's acceptance check (it's one of the lines).
  - Something in an artifact looks wrong and you want to know whether the vault or the
    push is at fault.
- **Pairs well with:** [`rebuild-artifact`](#rebuild-artifact-life-nodes) (the fix it
  offers for staleness), [`sync`](#sync-life-nodes).
- **Notes:** report first. Its only write is repairing a malformed line in place, shown and
  confirmed line by line; duplicates and chain problems come back as the retract line for
  Kyle to log through `log`.

#### `add-node` (Life Nodes)

- **Run config:** Opus 5 · `high` — an interview whose schema blocks `log` validates against
  from then on.
- **Reach for it when:**
  - A life area should start being tracked and has no node yet.
- **Pairs well with:** [`edit-node`](#edit-node-life-nodes) (every later change to the note),
  [`design-artifact`](#design-artifact-life-nodes) (once the node has data worth a page).
- **Notes:** writes one note and `Data/<node_id>/.gitkeep`, nothing else. A missing host is
  added first, never invented. The host edge is confirmed with `obsidian backlinks`, or
  reported unverified.

#### `edit-node` (Life Nodes)

- **Run config:** Opus 5 · `high` — every stream change is checked against the lines already
  logged before it's shown.
- **Reach for it when:**
  - A node needs a new stream or field, a new take-home rate, or changed rules.
  - A node is renamed or moves under another host.
- **Pairs well with:** [`design-artifact`](#design-artifact-life-nodes) (a view held back for
  a node change), [`build-artifact`](#build-artifact-life-nodes) (a `## Rules` change reaches
  a page only when it's rebuilt).
- **Notes:** once a stream has data, only a new optional field, a new enum value, or prose is
  allowed; a breaking change is refused and routed to a one-off migration or a new stream.
  The Soft 30 cleaning list is data, changed from Cowork's `log`.

#### `archive-node` (Life Nodes)

- **Run config:** Sonnet 5 · `medium` — a shown list of moves and status pushes, then doing
  exactly that.
- **Reach for it when:**
  - A node, or one artifact, is done or paused and should leave the active vault.
  - Something archived should come back ("revive <Node>").
- **Pairs well with:** [`audit`](#audit-life-nodes) (dangling connections afterwards),
  [`sync`](#sync-life-nodes).
- **Notes:** Kyle-only. Readers are found by query, never a stored list, and `Data/` never
  moves. Unpinning or re-pinning the published page is Kyle's.

#### `design-artifact` (Life Nodes)

- **Run config:** Fable 5 · `high` — ranking views and settling a spec's design calls is
  judgment work, paced by Kyle's answers.
- **Reach for it when:**
  - "Viz ideas for <Node>": step 1 ranks ideas and can stop there.
  - A new artifact, or a redesign of one, needs its note written before a build.
- **Pairs well with:** [`build-artifact`](#build-artifact-life-nodes) (builds exactly what the
  note's Views say), [`edit-node`](#edit-node-life-nodes) (a view waiting on a field the node
  lacks), the bundled `dataviz` skill (each idea's chart form).
- **Notes:** writes one artifact note and never `index.html` or `url`. The name can't match a
  node's, since `audit` would read the `reads` as an artifact reading an artifact. Samples
  resolved entries only, because that's all the page gets.

#### `log` (Life Nodes)

- **Run config:** runs in Cowork, in the Life Nodes project; not launched from Claude Code.
- **Reach for it when:**
  - Reporting anything to record: a dose, a night's Bevel screenshots, drinks, water.
  - Correcting or scratching an entry ("actually it was 7:45").
  - Refreshing Gearhead's scheduled shifts from Google Calendar ("pull my shifts").
- **Pairs well with:** [`review`](#review-life-nodes) (asking about what was logged),
  [`rebuild-artifact`](#rebuild-artifact-life-nodes) (when a push fails).
- **Notes:** one confirm line per node naming every assumption, then an append. Never runs
  git and never edits an existing line.

#### `review` (Life Nodes)

- **Run config:** runs in Cowork, in the Life Nodes project; not launched from Claude Code.
- **Reach for it when:**
  - "How many…", "when did I last…", "what's left today" about logged data.
- **Pairs well with:** [`log`](#log-life-nodes) (it hands logs back to it),
  [`audit`](#audit-life-nodes) (when an answer shows data that looks wrong).
- **Notes:** read-only by instruction and by `allowed-tools`; whether Cowork enforces
  `allowed-tools` is unverified, which is why the body says it too.

---

## Custom Subagents

These are **explicit-dispatch only** — a skill that names them, or you asking directly.
Their config is **pinned in the agent file's frontmatter**, so there's nothing for you to
choose: the cards state what's pinned and who dispatches them.

None right now — the last two were retired 2026-10-16; see [`retired.md`](retired.md).

