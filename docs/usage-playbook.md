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

- **Fable 5** plans — judgment-first work: design calls with real tradeoffs, triage and
  routing, coaching, convention-setting. **Opus 5** builds — well-specified implementation
  and synthesis-heavy writing. **Sonnet 5** grinds — mechanical, checklist-scoped work.
- **Effort** (independent of the model): `ultracode` = broad parallelizable fan-out with
  adversarial verify · `max` / `xhigh` = ONE hard problem, or a design call with real
  tradeoffs · `high` = ordinary build work with judgment in it · `medium` / `low` =
  mechanical and checklist-scoped.
- Launch flags are per-invocation and never touch saved defaults:
  `claude --model claude-opus-5 --effort high`.
- **"inherits the session"** means the item runs inside a session you're already in and
  isn't worth switching models for — `/begin`, `/catchup`, `reweave`, `narrate`. Everything
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
(`skills/interview-prep/` is gitignored) is excluded because git doesn't list it — not
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

#### `/begin`

- **Run config:** inherits the session · `low` — it reads git state and the last wrap log and
  briefs you; there's no judgment worth paying for.
- **Reach for it when:**
  - You're opening a session and want branch, recent commits, and open PRs in one screen
    before deciding anything.
  - You want the last `/wrap` log's recommendation surfaced instead of re-deriving where you
    left off.
- **Pairs well with:** [`/wrap`](#wrap) (writes the log `/begin` reads),
  [`reorient`](#reorient) (use that instead after a real gap), [`/catchup`](#catchup)
  (`--audio` routes through the same narration).
- **Notes:** offers exactly one optional recall question and takes a skip cleanly — it won't
  quiz you into the ground.

#### `/wrap`

- **Run config:** inherits the session · `medium` — recap plus active-recall synthesis needs
  a little care, not a model switch.
- **Reach for it when:**
  - You're closing out real work and want the *why* recorded, not just the diff.
  - You want the next move written down while it's still obvious to you.
- **Pairs well with:** [`/begin`](#begin) (reads the dated log this writes),
  [`/handoff`](#handoff) (when the next session is a fresh one, not tomorrow's),
  [`/learn`](#learn) (mines the same session for what's worth keeping as a skill),
  [`narrate`](#narrate) (the `--audio` engine).
- **Notes:** with `--audio` it never claims an MP3 exists if Kokoro was down — the written
  wrap still stands.

#### `/catchup`

- **Run config:** inherits the session · `low` — it narrates context you already have.
- **Reach for it when:**
  - You're mid-session, about to walk away from the keyboard, and want the state of play in
    your ears.
  - Pass `last` when you only want Claude's most recent output narrated, not the whole
    session.
- **Pairs well with:** [`narrate`](#narrate) (the TTS engine it calls),
  [`/wrap`](#wrap) (the endgame sibling — `/catchup` explicitly does *not* end the session).

#### `/handoff`

- **Run config:** inherits the session · `medium` — mostly summarization, but it ends on a
  real run-config judgment for the next session.
- **Reach for it when:**
  - Context is getting long and the remaining work would be cleaner in a fresh session.
  - You want hard-won lessons and rejected options captured so the next session doesn't
    relitigate them.
- **Pairs well with:** [`/begin`](#begin) (what the fresh session runs first),
  [`/launch`](#launch) (opens the fresh session and loads the prompt into it),
  [`/prompt-optimize`](#prompt-optimize) (same model/effort vocabulary, advisory only),
  [`narrate`](#narrate) (`--audio`).
- **Notes:** it **stops the current work** after printing — that's deliberate. The
  run-config note lands outside the paste-able block, never inside it.

#### `/launch`

- **Run config:** inherits the session · `low` — it opens a window and starts a process;
  the judgment already happened in the run-config note it reads.
- **Reach for it when:**
  - You've just run `/handoff` (or `/ship-and-route`, `/prompt-optimize`,
    `/backlog-hygiene`) and want the fresh session open rather than assembled by hand.
  - Pass `--send` when you want it working immediately instead of pausing on your ⌘V.
- **Pairs well with:** [`/handoff`](#handoff) (the usual caller — `/launch` consumes its
  paste-able block and run-config note), [`/begin`](#begin) (what the launched session
  often runs first).
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

#### `/learn`

- **Run config:** Fable 5, or the session you're in · `high` — deciding what generalizes into
  a reusable skill is convention-setting, which is judgment work.
- **Reach for it when:**
  - You just solved something the hard way and the *approach* would pay off again.
  - You've repeated a workaround across sessions and want it encoded rather than remembered.
- **Pairs well with:** [`/wrap`](#wrap) (the same end-of-session moment),
  `superpowers:writing-skills` (how the skill file itself should be shaped),
  [`adversarial-review`](#adversarial-review) (skills edits never take the trivial-diff
  escape hatch).
- **Notes:** hard STOP after presenting candidates — nothing is written before you pick. It
  lands skills in `claude-config` via branch + PR, which may not be the repo you're working
  in, and each new skill ships with its index row *and* its card here in the same commit —
  the sync check blocks the push otherwise.

### Planning & Exploration

#### `/explore-plan`

- **Run config:** Fable 5 · `high`, `xhigh` when the approach is genuinely gnarly — ranked
  tradeoffs before any edit is the definition of judgment-first.
- **Reach for it when:**
  - The task is medium-sized and the *approach* is uncertain or risky enough that guessing
    wrong costs a rewrite.
  - You want reconnaissance across unfamiliar code before committing to a shape.
- **Pairs well with:** [`/tdd`](#tdd) (executes the approach you pick),
  [`/autonomous-milestone`](#autonomous-milestone) (hand it a settled plan),
  [`reweave`](#reweave) (fold a follow-up decision back into the plan it belongs in).
- **Notes:** writes and edits nothing until you approve a plan — it presents approaches and
  stops.

#### `/brainstorm`

- **Run config:** Fable 5 · `ultracode` — blind parallel divergence lenses plus a two-sided
  critic gate is exactly the fan-out + adversarial-verify shape ultracode exists for.
- **Reach for it when:**
  - The backlog feels safe or stale and you want ideas outside the usual grooves.
  - You're starting a phase and want the option space mapped before committing — pick the
    mode that matches the axis (Moonshot, QuickWin, Subtract, Harden, Premortem, Friction,
    Delight, Positioning, Reach).
- **Pairs well with:** [`replenish`](#replenish) (runs brainstorm modes as lanes),
  [`backlog-hygiene`](#backlog-hygiene) (sequences the survivors),
  [`kickoff`](#kickoff) (when an idea outgrows the current project).
- **Notes:** the mode is resolved *before* steering, because the mode decides which lenses
  and which critic gate load. HARD STOP at Synthesize — nothing is captured to
  `docs/ideas/` or the backlog without an explicit go-ahead.

#### `/autonomous-milestone`

- **Run config:** Opus 5 · `ultracode` — a build-heavy autonomous run, and the command is
  itself your explicit opt-in to multi-agent orchestration.
- **Reach for it when:**
  - You have a well-specified target and want it planned, built, tested, verified, and
    reported without check-ins.
  - You have *no* target and want the backlog triaged into ranked candidates (with heuristic
    blast radius) so you can just pick.
- **Pairs well with:** [`backlog-hygiene`](#backlog-hygiene) (hands off the picked arc to
  it), [`ship-and-route`](#ship-and-route) (lands what it produced),
  [`adversarial-review`](#adversarial-review) (the gate before its PR merges).
- **Notes:** giving a target **is** the go-ahead — it won't stop for plan approval. It never
  merges to `main` or writes to production without an explicit say-so. Its triage phase runs
  deliberately cheap; `ultracode` is for the build.

#### `/prompt-optimize`

- **Run config:** Fable 5 · `medium` — small output, but the diagnosis and archetype routing
  are real judgment calls.
- **Reach for it when:**
  - You have a rough draft prompt for a big run and want the workflow archetype, model, and
    effort settled before you spend the tokens.
  - You're unsure whether something wants a linear session, a subagent fan-out, or a full
    ultracode Workflow.
- **Pairs well with:** [`/handoff`](#handoff) (the same model/effort vocabulary),
  [`kickoff`](#kickoff) (shape the idea first, then the prompt),
  [`/explore-plan`](#explore-plan) (one of the archetypes it recommends).
- **Notes:** advisory only — it never executes the task. It gates on your accept/override
  before synthesizing, and the cost estimate stays in chat, never inside the prompt block.

#### `/reframe-orchestrator`

- **Run config:** Opus 5 · `high` — careful docs restructuring against live references, with
  a fixed target shape; well-specified but unforgiving.
- **Reach for it when:**
  - A repo's `.claude/orchestrator.md` still mandates human pauses and now deadlocks against
    autonomous runs.
  - You want invariants and gates separated from the dispatch persona without invalidating
    the diagrams, session-start prompts, and agent files that reference it.
- **Pairs well with:** [`/claudify-repo`](#claudify-repo) (the flow that put repo tooling
  there), [`adversarial-review`](#adversarial-review) (before the docs PR merges).
- **Notes:** docs only — it won't touch source, SQL, migrations, or config, and it reframes
  the pipeline rather than deleting it. It opens a PR and leaves the merge to you.

### Development Workflows

#### `/tdd`

- **Run config:** Opus 5 · `high` — ordinary build work with a discipline attached.
- **Reach for it when:**
  - The behavior is specified well enough to write the failing test first.
  - You want a regression net around a module you're about to change.
- **Pairs well with:** [`/explore-plan`](#explore-plan) (upstream: pick the approach),
  `superpowers:test-driven-development` (the general discipline),
  [`spec-miner`](#spec-miner) (mined specs become the tests),
  [`adversarial-review`](#adversarial-review) (before the merge).
- **Notes:** the tests get committed before implementation, and the implementation-only rule
  is the point — failures are fixed in the code, never by editing the test.

#### `/screenshot-iterate`

- **Run config:** Opus 5 · `medium` — the loop does the correcting, so per-pass reasoning
  depth matters less than actually looking at each screenshot.
- **Reach for it when:**
  - You have a visual target (mock, screenshot, reference page) and want the UI driven
    toward it rather than described.
  - A layout is "almost right" and the remaining diffs are only visible on screen.
- **Pairs well with:** [`match-the-mock`](#match-the-mock) (the auto-triggering sibling —
  same loop), [`/boot_server`](#boot_server) (gets the app reachable first),
  `frontend-design` plugin skill (styling judgment).
- **Notes:** needs a working browser tool (Playwright/Kapture) to navigate and capture —
  confirm that before starting, or the loop has no eyes.

#### `/smoke-test`

- **Run config:** Sonnet 5 · `medium` — deriving what to verify from the diff and assembling
  a checklist is checklist-shaped work.
- **Reach for it when:**
  - You're about to ship and want a precise do-this / see-that list instead of clicking
    around hoping.
  - A change spans surfaces and you want every page you'll need already open in Chrome.
- **Pairs well with:** [`/boot_server`](#boot_server) (it auto-boots local apps),
  [`ship-and-route`](#ship-and-route) (manual-smoke evidence for the landing gate),
  [`/verify`](#verify) (DogHood's automated-check twin).
- **Notes:** the TL;DR of main objectives comes **last**, on purpose, and the checklist is
  saved to `docs/smoke/` so it survives the session.

#### `/trim-context`

- **Run config:** Sonnet 5 · `medium` — a fixed-rubric audit plus mechanical fixes.
- **Reach for it when:**
  - A repo's `CLAUDE.md` is creeping toward the 40k-char limit, or sessions feel expensive
    before you've done anything.
  - You want every repo under a parent directory swept in one pass.
- **Pairs well with:** [`/claudify-repo`](#claudify-repo) (vendoring adds weight),
  `claude-md-management` plugin skills (rewrite the rules it flags).
- **Notes:** bails out and reports rather than doing git surgery in a dirty or mid-rebase
  repo, never switches your branch or resets your work, never deletes a rule (it moves rules
  to on-demand files), and never auto-merges — a human reviews the PR.

### Environment & Setup

#### `/boot_server`

- **Run config:** Sonnet 5 · `low` — detect, start, wait, open. Mechanical.
- **Reach for it when:**
  - You want the dev server up and the app in front of you without remembering this repo's
    start command.
  - Pass `live` to open the deployed page (GitHub Pages and friends) instead of localhost.
- **Pairs well with:** [`/smoke-test`](#smoke-test) (calls it),
  [`/screenshot-iterate`](#screenshot-iterate) (needs the app reachable),
  `run` (Claude Code's built-in launcher skill — project-aware, ships with the harness, so
  it has no file in this repo and no card here).
- **Notes:** prefers the repo's own launcher, reuses an already-running server instead of
  starting a second one, and waits for a real response before opening Chrome — on a timeout
  it shows the last lines of the server log rather than claiming success.

#### `/envsetup`

- **Run config:** Sonnet 5 · `low` — resolve key + URL, stub the line, open two things.
- **Reach for it when:**
  - You need a credential and don't want to hunt for which env file this repo uses or where
    the token gets generated.
  - You're onboarding a fresh clone and want the `.env` scaffolded with source comments.
- **Pairs well with:** [`/boot_server`](#boot_server) (what you run next),
  [`kickoff`](#kickoff) / [`mini`](#mini) (right after a scaffold).
- **Notes:** it appends stubs and never clobbers an existing value — you paste the secret
  yourself.

#### `/claudify-repo`

- **Run config:** two modes, two configs. **PORT:** Sonnet 5 · `medium` — a picker plus a
  copy. **BRAINSTORM:** Opus 5 · `high` — it spawns the automation recommender and designs
  repo-specific tooling.
- **Reach for it when:**
  - A repo needs your global tooling to work in cloud/web sessions or for collaborators
    (vendored copies, not symlinks).
  - You want new repo-specific commands or skills designed around how this project actually
    works.
- **Pairs well with:** [`kickoff`](#kickoff) / [`mini`](#mini) (post-scaffold step),
  `claude-automation-recommender` plugin skill (what BRAINSTORM mode dispatches),
  [`/trim-context`](#trim-context) (vendoring adds always-loaded weight).
- **Notes:** stages only the files it touched — never `git add -A` — and won't push unless
  you say so. Vendored copies don't track upstream.

#### `/wiki-init`

- **Run config:** Sonnet 5 · `medium` — an idempotent scaffold delegated to
  [`project-wiki`](#project-wiki)'s INIT mode.
- **Reach for it when:**
  - A project has no `PROJECT.md` / `HANDOFF.md` and you want the minimum wiki in place.
  - You want every project under `~/Projects/` initialized in one sweep (`--all`).
- **Pairs well with:** [`project-wiki`](#project-wiki) (does the actual work),
  [`/wiki-backfill`](#wiki-backfill) (the history page comes after),
  [`kickoff`](#kickoff) (auto-runs it for new projects).
- **Notes:** never overwrites an existing wiki file, so re-running anywhere is safe. `--all`
  has one up-front confirmation and then runs unattended, report-and-proceed, landing each
  project via branch + PR.

#### `/wiki-backfill`

- **Run config:** Opus 5 · `medium` — mining PRs, tags, wrap logs, and ADRs into a milestone
  narrative is synthesis work with a fixed output shape.
- **Reach for it when:**
  - A project has real history and no `Wiki/History.md` to explain how it got here.
  - You're about to write a project guide or interview yourself on a repo and want the
    evolution recorded first.
- **Pairs well with:** [`project-wiki`](#project-wiki) (BACKFILL mode),
  [`reorient`](#reorient) (a history page makes the catch-up brief much better),
  [`project-guide`](#project-guide) (overlapping mining, different output).
- **Notes:** requires an existing wiki sentinel and **refuses to overwrite** an existing
  `History.md`. Branches from `origin/<default-branch>`, not your checkout, and stages only
  the two wiki files. After backfill the page accretes forward on its own via MAINTAIN mode.

---

## Global Skills

### Project Kickoff & Setup

#### `kickoff`

- **Run config:** Fable 5 · `high` — a deep adaptive interview that pushes back on vagueness
  is judgment-first. Use `ultracode` only if you're running the optional pre-mortem panel.
- **Reach for it when:**
  - You have an idea that's real but half-baked, and building now would bake in the wrong
    assumptions.
  - You want the riskiest assumption named and turned into Milestone 0 before any code.
- **Pairs well with:** [`mini`](#mini) (the lighter sibling for throwaway experiments),
  [`/claudify-repo`](#claudify-repo) and [`/wiki-init`](#wiki-init) (post-scaffold; the wiki
  is automatic), [`/prompt-optimize`](#prompt-optimize) (turn the phased plan into a build
  prompt).
- **Notes:** one question at a time, never a wall. Hard gate before scaffolding — creating a
  public-trail GitHub repo is confirmed via `AskUserQuestion`, never a bare "go". The
  adversarial stress-test panel is opt-in, not default. "Just scaffold it, skip the
  questions" gets a compressed pass with stated assumptions, not a skipped gate.

#### `mini`

- **Run config:** Sonnet 5 · `medium` — a short interview and a scripted scaffold.
- **Reach for it when:**
  - You want to try something this weekend and a full kickoff interview would be more
    ceremony than the idea deserves.
  - You just need the folder, git repo, and private GitHub repo to exist so you can start.
- **Pairs well with:** [`kickoff`](#kickoff) (the upgrade path when the idea turns out to
  matter), [`/envsetup`](#envsetup) (right after the scaffold).
- **Notes:** there's still a one-line spec checkpoint before it scaffolds — "skip the
  questions" compresses it, it doesn't remove it.

#### `project-wiki`

- **Run config:** inherits the session · `medium` — it fires inside whatever session changed
  the project state, and surgical updates don't want a model switch.
- **Reach for it when:**
  - You're working in a project with wiki sentinel files and a decision was just made, work
    is pausing, or a new source needs integrating.
  - You need it explicitly: INIT (create the minimum wiki), MAINTAIN (surgical updates),
    BACKFILL (retroactive history).
- **Pairs well with:** [`/wiki-init`](#wiki-init) and [`/wiki-backfill`](#wiki-backfill)
  (the commands that invoke it), [`ship-and-route`](#ship-and-route) (state changes are what
  trigger MAINTAIN).
- **Notes:** INIT is additive, idempotent, and proceeds without an approval gate; it never
  creates a `Wiki/` holding nothing but an index. Every assertion carries a claim label
  (Fact / Inference / Decision / Proposed / Contradiction) — an unlabeled assertion is a
  bug. Decisions tables and History are append-only. Broad changes (3+ pages) get their
  scope reported first.

#### `grill-me`

- **Run config:** Fable 5 · `high` — a pressure-test interview is judgment-first work; bump
  to `xhigh` when the plan hangs on one genuinely hard design call.
- **Reach for it when:**
  - You have a plan or design that *feels* done and you want its weak branches found before
    you commit to building.
  - You're about to hand work to a builder session and want every silent assumption
    surfaced first.
- **Pairs well with:** [`grilling`](#grilling) (the method this invokes),
  [`kickoff`](#kickoff) (grill the brief a kickoff produced), [`/explore-plan`](#explore-plan)
  (grill the winning approach before approving it), [`/handoff`](#handoff) (turn the
  sharpened plan into a builder handoff).
- **Notes:** deliberately a thin wrapper (`disable-model-invocation: true`) — it only fires
  when you type `/grill-me`; the auto-trigger surface lives on `grilling`. Imported from
  [mattpocock/skills](https://github.com/mattpocock/skills) (MIT).

#### `grilling`

- **Run config:** inherits the session · `high` — it auto-fires mid-session on "grill me"
  phrasing, interrogating whatever plan that session already holds.
- **Reach for it when:**
  - You say "grill me on this" about a plan, decision, or idea mid-session.
  - A decision has branches you haven't consciously visited and you want them enumerated
    rather than assumed.
- **Pairs well with:** [`grill-me`](#grill-me) (the typed entry point),
  [`adversarial-review`](#adversarial-review) (the post-code sibling — grilling
  stress-tests the plan, the review loop stress-tests the diff),
  [`backlog-hygiene`](#backlog-hygiene) (grill the "what's next" pick it produces).
- **Notes:** works in rounds — the whole frontier of askable questions at once, each
  numbered with a recommended answer; questions whose prerequisites are still open wait for
  a later round. Facts are Claude's job (dispatched to subagents, never asked of you);
  decisions are yours. Done only when the frontier is empty *and* you confirm shared
  understanding — it does not act on the plan before that. Unattended runs don't stall: it
  writes round 1's frontier with recommended answers as unconfirmed assumptions and stops.
  Imported from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT), with house
  edits for trigger conditions and unattended runs.

### Session & Context Management

#### `reorient`

- **Run config:** Opus 5 · `medium` — read-and-brief synthesis over a repo you've forgotten;
  it decides nothing on your behalf.
- **Reach for it when:**
  - You've been away days to months and barely remember where the project stands.
  - There's dangling state (dirty tree, a stash, an unpushed branch, an open PR) and you need
    to know what it is before touching it.
- **Pairs well with:** [`/begin`](#begin) (the short-gap sibling),
  [`ship-and-route`](#ship-and-route) (where it routes dangling finishable work),
  [`backlog-hygiene`](#backlog-hygiene) / [`replenish`](#replenish) /
  [`/autonomous-milestone`](#autonomous-milestone) (its other exits).
- **Notes:** **it changes nothing** — no commits, stashes, rebases, pushes, merges, branch
  switches, or backlog edits, even under a blanket go-ahead; that dangling state is your
  main evidence. It runs the project's own cheap checks and reports real output, then stops
  for your pick. A wrap log's recommendation is treated as a candidate decayed by the gap.

#### `onboard`

- **Run config:** Opus 5 · `high` — a long interactive session of grounded synthesis and
  in-character Q&A over the repo; the judgment is in the answers and the suggested questions.
- **Reach for it when:**
  - You want to re-learn one of your own projects the way a new hire would — briefed in team
    voice, then pulled deeper by suggested questions you ask back.
  - You're building interview fluency and want the reviewer-attack questions surfaced before
    a real interviewer finds them.
- **Pairs well with:** [`reorient`](#reorient) (plain after-a-gap catch-up with routing — no
  role-play), [`project-guide`](#project-guide) (the written reference doc; onboard's packet
  records a session instead), [`/wrap`](#wrap) (the quiz direction reversed: wrap tests your
  recall, onboard hands you the questions).
- **Notes:** fixed five-segment agenda with a Q&A stop after each; exactly 3 suggested
  questions open every Q&A and 3 fresh ones close every answer, escalating from factual to
  reviewer-attack. The lineup tour reads `~/Projects/portfolio`'s cards, not the underlying
  repos. Everything said is traceable to the repos — the fiction is only the frame. Leaves
  `docs/onboarding/YYYY-MM-DD-onboarding.md` in the project.

#### `reweave`

- **Run config:** inherits the session · `medium` — the answer is already in context; never
  switch sessions to fold it in.
- **Reach for it when:**
  - You got an explanation, asked a follow-up, and now want one clean standalone version
    instead of splicing the two in your head.
  - A plan or design doc on disk needs a decision threaded through every dependent section,
    not appended as an addendum.
- **Pairs well with:** [`/explore-plan`](#explore-plan) (reweave its plans when an approach
  changes), [`/handoff`](#handoff) (a reweaved plan hands off cleanly).
- **Notes:** output lands where the target lived — a chat answer returns to chat, a file gets
  rewritten in place. It never re-architects functional source code; a behavior change is an
  ordinary edit.

#### `ship-and-route`

- **Run config:** Fable 5 · `high` — landing decisions plus ranked next-move routing is
  triage judgment, and the honest ultracode calls are exactly the tradeoff work Fable is
  for.
- **Reach for it when:**
  - You've finished a chunk of work and want outstanding git work landed *behind a review
    gate*, then a straight answer on what's next.
  - You want 2–3 ranked options with an explicit ultracode-benefit verdict rather than a
    vague "we could…".
- **Pairs well with:** [`adversarial-review`](#adversarial-review) (its §1.3 gate for
  substantial diffs), [`backlog-hygiene`](#backlog-hygiene) (when the routing needs the whole
  corpus groomed), [`/handoff`](#handoff) (Act 3 is a starter prompt for a fresh session).
- **Notes:** invoking it **is** your per-action go-ahead to commit/push/PR/merge what's ready
  — but conditional on the review finding no issues; a blocker it can't safely resolve stops
  the flow. Never direct-pushes `main`. It blocks on the review workflow rather than
  deferring the merge to a background notification.

#### `backlog-hygiene`

- **Run config:** Fable 5 · `high` — pure prioritization and sequencing; producing the
  decision *is* the deliverable.
- **Reach for it when:**
  - The backlog is stocked and the real question is what to do next, in what order.
  - Items are stale, oversized, or duplicated and you want them verified before they get
    ranked.
  - You want the remaining mix checked for an empty axis (all build-new and no solidify, say).
- **Pairs well with:** [`replenish`](#replenish) (when the corpus is dry, not messy),
  [`/autonomous-milestone`](#autonomous-milestone) (builds the picked arc),
  [`/brainstorm`](#brainstorm) (sequences its survivors),
  [`reorient`](#reorient) (routes here after a long gap).
- **Notes:** **builds nothing, ever** — verdicts are proposals until you approve them. Two
  gates always survive: one steering round (appetite can't be inferred) and the decision-brief
  hard stop. Retired items move to a Parked section; nothing is deleted. It closes with a
  starter prompt routed to the right executor.

#### `replenish`

- **Run config:** Fable 5 · `ultracode` — a multi-lane bug-hunt plus brainstorm fan-out with
  a merged review is the canonical fan-out-and-verify shape.
- **Reach for it when:**
  - The planned column is empty and you need bugs *and* new ideas refilled in one run.
  - You'd otherwise run `/brainstorm` and `bug-hunt` back to back and hand-dedupe the
    overlap.
- **Pairs well with:** [`/brainstorm`](#brainstorm) and [`bug-hunt`](#bug-hunt) (the engines
  it runs verbatim as lanes), [`backlog-hygiene`](#backlog-hygiene) (sequences what it
  produced afterward).
- **Notes:** composable, not a fork — the engines' own specs stay binding and this skill owns
  only the combination. One combined steering round (compressible, never deletable) plus one
  merged hard stop. It states the total agent count before launching and hard-caps at 70.
  Cross-lane dedup happens on the *move* axis — Harden ↔ bug-hunt is a known seam.

### Quality & Debugging

#### `bug-hunt`

- **Run config:** Opus 5 · dialable from `medium` to `ultracode` — the skill exists to be
  tiered: a quick single-agent pass, or a full multi-agent fan-out with adversarial verify.
- **Reach for it when:**
  - You want to *find* bugs you don't know about yet — a codebase, a subsystem, or a diff
    with no merge in play.
  - You're about to ship something broad and want an audit wider than one branch's diff.
- **Pairs well with:** `superpowers:systematic-debugging` (fixes the findings you pick),
  [`silent-failure-hunter`](#silent-failure-hunter) (its dedicated silent-failure lens),
  [`adversarial-review`](#adversarial-review) (the pre-merge counterpart),
  [`replenish`](#replenish) (runs it as a lane).
- **Notes:** reasoning depth (`max`) and agent count (`ultracode`) are **independent axes** —
  an ultracode fan-out can also run each finder at max effort. Triage gate: it presents a
  ranked, verified list and **stops**; nothing auto-fixes. It never modifies
  `systematic-debugging`, only offers to invoke it.

#### `adversarial-review`

- **Run config:** Opus 5 · `high` — author triage and dispute judgment on a real diff. Its
  reviewer and judge subagents are already Opus-pinned, so effort here buys *your* side of
  the dialogue.
- **Reach for it when:**
  - Any PR is about to merge — this is the standing pre-merge gate in the global git
    workflow.
  - You want a zero-context second set of eyes that actively tries to refute the change.
- **Pairs well with:** [`adversarial-reviewer`](#adversarial-reviewer) and
  [`review-judge`](#review-judge) (the agents it dispatches),
  [`ship-and-route`](#ship-and-route) (calls it as its landing gate),
  [`bug-hunt`](#bug-hunt) (the no-merge-in-play counterpart).
- **Notes:** hard STOP at triage — you can flip verdicts or waive findings by name, and a
  waiver is recorded verbatim. Hard cap of 3 reviewer dispatches per run. The trivial-diff
  escape hatch exists but a skip is always stated in the merge brief, never silent, and
  never for skills/agents/commands/CLAUDE.md edits. Findings land as a PR comment with a
  CLEAR / NOT-CLEAR verdict.

#### `artifacts-audit`

- **Run config:** Opus 5 · `medium` — a taxonomy audit against a fixed rubric, ending in a
  plan.
- **Reach for it when:**
  - A repo's documentation has grown by accretion and you want to know what's missing versus
    what's merely stale.
  - You want a concrete generation + maintenance plan before writing a single README.
- **Pairs well with:** [`artifacts-generate`](#artifacts-generate) (executes the plan it
  writes), [`project-guide`](#project-guide) (a different lens on the same repo).
- **Notes:** plans only — it writes no artifacts. One STOP at the project profile so the
  audit is scoped to what this repo actually is.

#### `artifacts-generate`

- **Run config:** Opus 5 · `medium` — well-specified doc writing from an approved plan.
- **Reach for it when:**
  - `docs/artifacts-plan.md` exists and you want the next README, ADR, runbook, or diagram
    actually written.
  - You want a week's worth generated in one pass — batch mode picks a scope and writes
    without per-item gates.
- **Pairs well with:** [`artifacts-audit`](#artifacts-audit) (writes the plan it consumes),
  [`adr-new`](#adr-new) (DogHood's numbered-ADR scaffold),
  [`adversarial-review`](#adversarial-review) (before the docs PR merges).
- **Notes:** two modes with very different oversight — one-at-a-time interviews, previews,
  and asks "continue?" per item; batch interviews and writes straight through. Never modifies
  source code, and skipped items are always listed with a reason rather than silently
  dropped.

#### `seed-hunt`

- **Run config:** Fable 5 · `high` — scoring candidate papers against a living selection bar
  is triage judgment, and it builds nothing.
- **Reach for it when:**
  - A reproduce-and-measure project just closed and you want the next paper chosen against
    what you learned, not vibes.
  - You want this project's hard-won lessons folded into the selection bar before they fade.
- **Pairs well with:** [`research-paper`](#research-paper) (the write-up that closes the
  project first), [`kickoff`](#kickoff) (where the pick goes),
  [`/handoff`](#handoff) (how it hands the pick to a fresh session).
- **Notes:** Phase 0 verifies the repo is genuinely closed and STOPs if it isn't — offering
  [`ship-and-route`](#ship-and-route) to land the remainder. The shortlist ends at a
  `PENDING-KYLE` gate; it never picks for you. `--audio` narrates the decision brief.

### NotebookLM

#### `notebook-init`

- **Run config:** Sonnet 5 · `medium` — an interview plus `nlm` CLI orchestration against a
  fixed template.
- **Reach for it when:**
  - You have a topic and a pile of sources and want a notebook with baseline artifacts, not
    an empty shell.
  - You want the local sidecar written so later skills know what's in there.
- **Pairs well with:** [`notebook-assist`](#notebook-assist) (everything after
  initialization), [`audio-series`](#audio-series) / [`video-series`](#video-series)
  (episodic courses from it), [`nlm-skill`](#nlm-skill) (the CLI reference).
- **Notes:** source selection is a preset choice (`Essentials` → `Everything`), and
  customization params are proposed with defaults rather than asked one by one. It only ever
  creates — it never deletes.

#### `notebook-assist`

- **Run config:** Sonnet 5 · `medium` — artifact refinement and source management inside an
  existing notebook.
- **Reach for it when:**
  - You have an artifact idea in mind and want it mapped to the right type with a decent
    focus prompt.
  - You want ideas *derived from what's actually in the notebook*, or sources
    added/refreshed/removed.
- **Pairs well with:** [`notebook-init`](#notebook-init) (what created the notebook),
  [`notebook-merge`](#notebook-merge) (when two notebooks should be one),
  [`nlm-skill`](#nlm-skill) (the CLI reference).
- **Notes:** brainstorm mode reads real notebook state first — it won't propose without
  calling `notebook_describe`.

#### `notebook-merge`

- **Run config:** Opus 5 · `medium` — deciding what survives a cross-notebook integration is
  judgment, and the migration itself is unforgiving.
- **Reach for it when:**
  - Two or more notebooks overlap enough that studying either one alone keeps missing
    context.
  - You want one side folded into another with artifacts regenerated from their recorded
    focus prompts.
- **Pairs well with:** [`notebook-assist`](#notebook-assist) (tidy each side first),
  [`notebook-init`](#notebook-init) (the sidecar format it migrates),
  [`nlm-skill`](#nlm-skill).
- **Notes:** exactly two gates — one creation gate for the merge plan, and a **per-notebook**
  delete gate that lists by name every artifact that dies with the original. Default is
  keep-archived; deletion never happens without that gate. Post-merge, the halves stay
  addressable by filtering the manifest by origin.

#### `audio-series`

- **Run config:** Sonnet 5 · `medium` — quota-aware batched generation against a designed
  curriculum is checklist-shaped.
- **Reach for it when:**
  - A notebook deserves a listening curriculum — a flagship Ep 1→N season where each episode
    assumes the last, plus standalones.
  - You want per-episode Study Guide + Quiz without burning more audio quota.
- **Pairs well with:** [`notebook-init`](#notebook-init) (creates the notebook),
  [`video-series`](#video-series) (the same shape in video),
  [`episode-review`](#episode-review) (home-base quizzes you after listening).
- **Notes:** audio is expensive and outward-facing — it never generates without an explicit
  "go" on the presented plan. Episode titles lead with `Ep N —` so they stay legible on a
  phone. Study aids cost no audio quota.

#### `video-series`

- **Run config:** Sonnet 5 · `medium` — same engine shape as its audio sibling.
- **Reach for it when:**
  - The material is visual enough that video overviews beat audio.
  - You want one deliberate visual identity across a whole season.
- **Pairs well with:** [`audio-series`](#audio-series) (the sibling — pick per material),
  [`notebook-init`](#notebook-init), [`catalog-doctor`](#catalog-doctor) (home-base's drift
  check over what got generated).
- **Notes:** pick ONE explicit `visual_style` per flagship season — never `auto_select` for
  series episodes. Blocked episodes get deferred to the sidecar with prompts intact rather
  than loop-retried against a hard quota.

#### `portfolio-notebook-sync`

- **Run config:** Sonnet 5 · `medium` — a checklist-scoped mechanical sync driven by the
  sidecar manifest; the judgment calls it might face are the ones it's built to escalate
  rather than resolve.
- **Reach for it when:**
  - A portfolio project just got its card and should be covered in the notebook like the
    others (`--add <project>`).
  - You merged a project's `/research-paper` PR and want the paper + presenter pack in the
    notebook (`--add-paper <project>`).
  - You've reworked portfolio docs and suspect the notebook's snapshots have gone stale.
  - Something in the notebook cites a number the repo no longer says.
- **Pairs well with:** [`notebook-assist`](#notebook-assist) (ad-hoc work on the same
  notebook), [`audio-series`](#audio-series) (the season this skill appends episodes to),
  [`research-paper`](#research-paper) (writes the paper `--add-paper` later ingests),
  [`nlm-skill`](#nlm-skill) (the CLI/MCP reference it defers to).
- **Notes:** `MANIFEST.md` is the contract — drift is a hash diff, never a judgment call. A
  bare drift check will *never* onboard a project or a paper it happens to notice — it
  reports `unpapered` and stops — and no mode changes git state or edits a file in
  `~/Projects/portfolio` (read-only git is required — it's how `repo_sha` gets filled); an
  unmerged branch or open PR is escalated to Kyle rather than snapshotted. The drift table
  is always shown before anything is deleted, and URL sources are content-hashed, not just
  liveness-checked. `--add-paper` is gated on **both** deliverables being on the project
  repo's **default branch** — queried as `origin/<default>` after a fetch, since Kyle merges
  the paper PR on GitHub and a local ref would still say "not landed" — and hashes and
  ingests them with `git show` from that same tree, never from the working tree. It matches
  two exact filenames: `docs/papers/` (plural) is `/paper-eli5`'s output about *other
  people's* papers and is never read here. Re-running it is safe — an existing `paper` row
  stops it rather than duplicating the source.

#### `curriculum-sync`

- **Run config:** Opus 5 · `high` — the mechanics are delegated, but the judgment isn't:
  reconstructing a scope you can defend, deciding what a partial hash means, and costing a
  multi-day quota plan are all calls a checklist can't make. Drop to Sonnet 5 · `medium` for a
  bare drift check, which is pure table computation.
- **Reach for it when:**
  - You updated the repos underneath a notebook and its episodes, quizzes, study guides, or
    hub course are now describing an older version of the work.
  - You want to know *which* derived artifacts went stale, not regenerate all of them blindly.
  - You're building a new notebook + course pair and want it to start life with a ledger
    (`--new`), instead of hand-assembling three skills' output.
  - A pair predates the ledger and needs baselining once (`--adopt`).
- **Pairs well with:** [`portfolio-notebook-sync`](#portfolio-notebook-sync) (owns the source
  layer this skill refuses to run on top of when it's dirty),
  [`audio-series`](#audio-series) / [`video-series`](#video-series) (own every generation
  mechanic), [`notebook-init`](#notebook-init) (the `--new` first step),
  [`course-builder`](#course-builder) (owns the course contract and its syllabus gate).
- **Notes:** `DERIVED.md` is the contract — staleness is a hash comparison, never memory of a
  prior run, and an uncomputable basis is marked `unverified` and **treated as stale** rather
  than guessed at. A dirty source layer is a hard stop: regenerating over stale sources bakes
  the staleness into artifacts that then *look* current. Audio re-records at **season** level
  by design (cross-episode consistency), which against the ~15/24h account-wide cap makes a
  two-season refresh a multi-day plan — costed at the plan gate, never discovered mid-wave.
  Deletion is a separate confirm from the plan approval. Cross-link repair is terminal: the
  portfolio study path hard-references artifact ids across 37 steps, and re-recording one
  season invalidates eight at once.

#### `nlm-skill`

- **Run config:** inherits the session · `low` — it's a reference guide, not a workflow.
- **Reach for it when:**
  - You're driving NotebookLM programmatically and need exact `nlm` CLI or MCP invocations.
  - Auth broke and you need the real recovery path.
- **Pairs well with:** every NotebookLM skill — [`notebook-init`](#notebook-init),
  [`notebook-assist`](#notebook-assist), [`notebook-merge`](#notebook-merge),
  [`audio-series`](#audio-series), [`video-series`](#video-series).
- **Notes:** never `nlm chat start` — it opens an interactive REPL no agent can control. Use
  `nlm notebook query` for one-shot Q&A.

### Research & Writing

#### `research-paper`

- **Run config:** Opus 5 · `xhigh` — one hard synthesis: a full paper from a finished repo's
  recorded results. The skill is designed for an unattended max-effort run, so `max` is the
  right call for a cloud/autonomous session.
- **Reach for it when:**
  - A reproduce-and-measure project is genuinely done and its results are recorded.
  - You want the honest version written — nulls reported as nulls, gates as pre-committed.
- **Pairs well with:** [`seed-hunt`](#seed-hunt) (runs after, to pick the next paper),
  [`project-guide`](#project-guide) (the same repo for a different audience),
  [`narrate`](#narrate) (the presenter pack read aloud).
- **Notes:** results only — it never estimates a missing number, invents a citation, or
  rounds a CI-overlapping result up into a win. **It does not merge and does not push to
  `main`**: the PR is an explicit gate for your review, overriding the global
  merge-autonomously workflow.

#### `paper-eli5`

- **Run config:** Opus 5 · `high` — a long, faithful 1:1 rewrite; demanding but fully
  specified.
- **Reach for it when:**
  - Someone else's paper matters and the jargon is the only thing in the way.
  - You want *nothing* summarized or reordered — same headings, same paragraph order, only
    the language changed.
- **Pairs well with:** [`paper-gloss`](#paper-gloss) (makes the remaining jargon clickable),
  [`paper-figures`](#paper-figures) (drops the real figures in),
  [`narrate`](#narrate) (listen to it).
- **Notes:** after the input paper is known there are no stops — it runs end to end and lands
  the output via the repo's git workflow. Equations survive verbatim plus a named form and a
  `where:` legend; a symbol the paper never defines stays a symbol rather than being guessed.

#### `paper-gloss`

- **Run config:** Opus 5 · `medium` — term proposal plus hand-authored HTML from an eli5
  that already exists.
- **Reach for it when:**
  - You've read the eli5 and specific terms are still opaque.
  - You want one self-contained page to send someone, with a glossary panel and real typeset
    math instead of raw LaTeX.
- **Pairs well with:** [`paper-eli5`](#paper-eli5) (its required input),
  [`paper-figures`](#paper-figures) (fills figure placeholders in the glossed HTML too).
- **Notes:** STOP at the proposed term list — whatever you approve or edit flows through
  unchanged. Prose is only wrapped, never rewritten; terms are never wrapped inside math or
  citations. `--retrofit` repairs math in an already-published page and redeploys to the same
  Artifact URL. Highlights and notes persist per browser via localStorage; export to
  Markdown/JSON is the durability guarantee (a fresh publish starts empty — only
  `--retrofit`/`--annotate` redeploys keep stored notes). `--annotate` retrofits
  the layer onto an existing page.

#### `paper-figures`

- **Run config:** Sonnet 5 · `medium` — mechanical figure harvesting and placeholder filling
  against a ledger.
- **Reach for it when:**
  - An eli5 or glossed page is full of `[Figure N]` placeholders and the real images exist
    on the web.
  - A JS-rendered visualization needs a real screenshot rather than a description.
- **Pairs well with:** [`paper-eli5`](#paper-eli5) and [`paper-gloss`](#paper-gloss) (both
  are valid targets — it injects into markdown and HTML).
- **Notes:** web sources only. One contact-sheet HARD STOP before injection; if that gate is
  skipped, the report says so prominently. Self-verification catches the dominant failure
  mode — a visualization that never rendered — and interactive graphics are flagged as static
  snapshots. It reports what was *programmatically* checked, never implying every figure was
  eyeballed.

#### `project-guide`

- **Run config:** Opus 5 · `high` — whole-project synthesis plus a candid recruiter lens;
  substantial writing against a fixed section order.
- **Reach for it when:**
  - You need to discuss a project fluently — what it is now, how it got built, the
    vocabulary, and what reads weak to someone poking at the repo.
  - You're prepping to talk about your own work and want the honest version, not a brochure.
- **Pairs well with:** [`/wiki-backfill`](#wiki-backfill) (history mining that feeds it),
  [`reorient`](#reorient) (the short-form version when you just need to get back to work),
  [`career-coach`](#career-coach) (its interview lens, as an actual conversation),
  [`narrate`](#narrate) (`--audio`).
- **Notes:** honesty rules are non-negotiable — weak spots get honest context, never spin.
  Thorough mode fans out only on large repos *and* only if you've opted into orchestration;
  on a small project spawning agents is slower and worse.

#### `narrate`

- **Run config:** inherits the session · `low` — it's the TTS rendering engine other
  commands call.
- **Reach for it when:**
  - You want an MP3 of something already written and condensed, for a walk or a commute.
  - Usually you don't invoke it directly — `/catchup`, `/wrap --audio`,
    `/handoff --audio`, `seed-hunt --audio`, and `project-guide --audio` all route through
    it.
- **Pairs well with:** [`/catchup`](#catchup), [`/wrap`](#wrap), [`/handoff`](#handoff),
  [`project-guide`](#project-guide) (its callers).
- **Notes:** needs local Kokoro up (from the voicemode plugin); if it's down, callers say so
  and keep the written artifact — nothing ever claims an MP3 that doesn't exist. Paths and
  code blocks get spoken as names, not character by character.

### Personal Coaching

#### `career-coach`

- **Run config:** Fable 5 · `high` — MCC-level coaching is pure judgment with zero build.
- **Reach for it when:**
  - You feel stuck, unfulfilled, or at a crossroads and want clarity rather than advice.
  - You want continuity across sessions — `[SNAPSHOT]` to establish state, `[UPDATE]` to
    log what changed, `[FOCUS]` to work one thing.
- **Pairs well with:** [`seed-hunt`](#seed-hunt) (the same "what next" energy pointed at
  research), [`project-guide`](#project-guide) (evidence about your own work to bring into a
  session).
- **Notes:** one question at a time, then it stops and waits — a list of questions is an
  interrogation. Don't expect it to hand you an answer; it's built to surface yours.

#### `teach`

- **Run config:** Fable 5 · `high` — lesson design is judgment work: choosing what fits the
  zone of proximal development matters more than producing HTML.
- **Reach for it when:**
  - You want to learn a topic over multiple sessions — programming or not (yoga, physics,
    fitness all fit) — with your progress tracked on disk instead of in chat scrollback.
  - You want lessons grounded in *why* you're learning (the mission), not a generic course.
- **Pairs well with:** [`curriculum-sync`](#curriculum-sync) (the NotebookLM/home-base
  learning chain — separate system, same goal), [`/wrap`](#wrap) (active-recall quizzing at
  session end), [`career-coach`](#career-coach) (when the question is *what* to learn, not
  how).
- **Notes:** typed-only (`disable-model-invocation: true`) — fires only on `/teach`. Run it
  from a dedicated learning directory (e.g. `~/Learning/<topic>/`), one mission per
  workspace; it writes `MISSION.md`, `lessons/`, `reference/`, `learning-records/`,
  `RESOURCES.md`, and `NOTES.md` at the root of wherever it runs, so don't start it inside a
  project repo. First session interviews you into a concrete mission before teaching
  anything. Imported from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT),
  with a house-edited description; format docs kept verbatim upstream, body carries two
  house edits from the pre-merge review — a workspace-location guard before the first write,
  and `GLOSSARY.md` wired into the workspace list.

### UI & Frontend

#### `match-the-mock`

- **Run config:** Opus 5 · `medium` — see-and-correct iteration where the loop, not a single
  deep pass, does the converging.
- **Reach for it when:**
  - You've shared a design, screenshot, or reference and want the UI driven to match it.
  - You'd otherwise describe the diff in words and hope — this one actually looks.
- **Pairs well with:** [`/screenshot-iterate`](#screenshot-iterate) (the manual sibling —
  same loop, invoked explicitly), [`/boot_server`](#boot_server) (get the app reachable),
  `frontend-design` plugin skill (styling judgment).
- **Notes:** auto-triggers when you share a visual target, so you rarely type it. Needs a
  browser tool available to navigate and capture.

---

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
  [`/tdd`](#tdd) (the tests step),
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
  [`new-migration`](#new-migration) (schema decisions usually want an ADR),
  [`artifacts-generate`](#artifacts-generate) (the project-agnostic ADR writer).
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
  [`adversarial-review`](#adversarial-review) (the review gate before a merge).
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
  [`youtube-breakdown`](#youtube-breakdown) (its notes are usable course input).
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

#### `youtube-breakdown`

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
  than compete), [`/handoff`](#handoff) (the note is the async channel, this is the live one).
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
- **Pairs well with:** [`/handoff`](#handoff) (whose composition spec it follows — it calls the
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

- **Run config:** inherits the session — it fires *inside* the successor, in the turn where
  that session ingested its predecessor's handoff note. Nothing about it is model-sensitive;
  every judgment it could have made is a check in `handoff/reap.mjs` instead.
- **Reach for it when:**
  - You don't — it reaches for itself, one turn after a handoff lands. R2 is the only v1
    trigger: this session consumed a note, and the session that launched it is still running.
  - You want to see the clutter without proposing anything: `node handoff/cli.mjs
    reaper-status` lists every launch row with a live probe of both ends and kills nothing.
- **Pairs well with:** [`auto-handoff`](#auto-handoff) (whose accepted proposal writes the
  registry row this reads — spawn and teardown are the two halves of one loop),
  [`/launch`](#launch) (whose *Verified-start* identity discipline the kill path inherits, with
  the stakes inverted).
- **Notes:** propose-first, and the ask is the backstop the design leans on — no SIGTERM
  without a yes, one machine-initiated proposal per registry row ever, and a decline is
  permanent against the machine. Registry-only targeting means a session that never handed off
  through the flow is structurally invisible. Close ≠ destroy: it ends a process and frees a
  window, and no path in it deletes a transcript, a note, or a state file. If the target
  survives SIGTERM it says so and stops — no SIGKILL, no retry. R1 (Kyle's "close it") is
  slice H and is not built.

#### `ghost`

- **Run config:** inherits the session; the answer itself is produced by a subagent, so no
  API call and no separate model pin.
- **Reach for it when:**
  - A handoff briefing left a gap — "what did they already try?", "where were they when
    they stopped?" — and the session that knows is gone.
  - You want testimony from the predecessor's transcript rather than your own reconstruction
    of what it probably did.
- **Pairs well with:** [`party-line`](#party-line) (use that instead if the predecessor is
  still running), [`/handoff`](#handoff) (the note names the transcript this reads).
- **Notes:** expect it to be strong on *what happened* and weak on *why* — measured on CLI
  2.1.220, thinking blocks persist with no text, so reasoning that never reached a reply is
  not recoverable. The rendering says so at the top when it applies; absence of a recorded
  rationale is not evidence there wasn't one.

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
  [`adversarial-review`](#adversarial-review) (the gate before merging).
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

## Custom Subagents

These are **explicit-dispatch only** — a skill that names them, or you asking directly.
Their config is **pinned in the agent file's frontmatter**, so there's nothing for you to
choose: the cards state what's pinned and who dispatches them.

### `adversarial-reviewer`

- **Pinned config:** `model: opus`, no effort override — it inherits the dispatching
  session's effort.
- **Dispatched by:** [`adversarial-review`](#adversarial-review), Phases 1 and 5, with
  `REPO_PATH`, `DEFAULT_BRANCH`, `MAILBOX_PATH`, and `ROUND`.
- **Reach for it when:** you're running the review loop. Don't launch it ad hoc for a general
  review — it expects a mailbox and a round number, and the loop is what makes its findings
  actionable.
- **Pairs well with:** [`review-judge`](#review-judge) (rules on what you dispute),
  [`adversarial-review`](#adversarial-review) (the loop that owns it).
- **Notes:** zero-context by design — the author's context is exactly what hides the bug. The
  diff is its subject, the whole repo its evidence. The mailbox is the **only** file it may
  write; it never touches the repo or runs a mutating git command. On round ≥ 2 it verifies
  each `FIXED-IN` fix as VERIFIED or REOPENED.

### `review-judge`

- **Pinned config:** `model: opus`, no effort override.
- **Dispatched by:** [`adversarial-review`](#adversarial-review), Phase 3 — and only if
  disputes exist.
- **Reach for it when:** you disputed a finding with evidence and want a neutral read rather
  than a standoff.
- **Pairs well with:** [`adversarial-reviewer`](#adversarial-reviewer) (whose claims it
  rules on), [`adversarial-review`](#adversarial-review).
- **Notes:** owes deference to neither side, and rules only on disputes — it raises no new
  findings. "Valid but unimportant" is **DOWNGRADED**, not overruled: true findings don't get
  erased to unblock a merge. Mailbox-only writes.

### `silent-failure-hunter`

- **Pinned config:** `model: sonnet`, `effort: high`.
- **Dispatched by:** [`bug-hunt`](#bug-hunt) as its silent-failure lens — or directly, when
  you ask for that audit specifically.
- **Reach for it when:**
  - You suspect failures are vanishing — swallowed errors, empty catches, fallbacks that
    hide a real problem, broken propagation, missing boundary handling.
  - You want one lens run hard over a scope (a path, a module, a diff range).
- **Pairs well with:** [`bug-hunt`](#bug-hunt) (grades findings on its rubric),
  `superpowers:systematic-debugging` (fixes what it finds).
- **Notes:** read-only — fix recommendations are advisory and it never applies them. Zero
  findings is a valid result; it won't inflate one to have something to report. Not the
  pre-merge gate — that's [`adversarial-review`](#adversarial-review).

### `spec-miner`

- **Pinned config:** `model: opus`, `effort: high`.
- **Dispatched by:** you, explicitly — in two modes. **No capability input** → it maps the
  repo and returns the capability list. **With one** → it mines that capability into
  `openspec/specs/<capability>/spec.md`.
- **Reach for it when:**
  - You're onboarding a brownfield project to spec-driven development and need the behavior
    that already exists written down.
  - You want flat Requirement/Invariant blocks with stable ids that future deltas can match
    on.
- **Pairs well with:** [`kickoff`](#kickoff) (brownfield onboarding),
  [`/tdd`](#tdd) (mined specs become the tests),
  [`add-source`](#add-source) (pipeline contracts worth pinning down).
- **Notes:** **never overwrites** an existing spec unless dispatched with `OVERWRITE=yes` —
  otherwise it reports what a re-mine would change and writes nothing. It never invents
  behavior (unclear contracts become `uncertainty` comments), never guesses cross-module or
  async links, and flags code inconsistencies rather than fixing them. Repo-read-only except
  the single spec file.
