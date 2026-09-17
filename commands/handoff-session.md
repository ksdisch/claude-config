---
description: Generate a self-contained handoff prompt I can paste into a fresh Claude Code session to continue this work without losing context. Captures hard-won lessons, what's done, and where the plan stands. Also prints a short plain-English 'what's next & why' briefing for me, so I stay oriented across the handoff. With --orchestrator, writes a coordinator brief instead — a session that dispatches an arc to worker sessions rather than building it itself. Stops the current work after generating. Project-agnostic.
argument-hint: "[--audio [short|long]] [--orchestrator]"
allowed-tools: Bash, Read, Write, Glob, Grep, Task, Skill, ToolSearch, SendUserFile, mcp__plugin_voicemode_voicemode__service
---

Context handoff.

## Parse `$ARGUMENTS`
- `--audio` → after printing the handoff, also generate a spoken-audio version
  of the brief (see "Audio narration" at the end). Optional level: `short`
  (default) or `long`. Without `--audio`, ignore all audio steps entirely —
  the command behaves exactly as before.
- `--orchestrator` → the fresh session **coordinates** an arc across worker
  sessions instead of building it. Replaces the block's section structure and
  lifts the word cap; see "Orchestrator mode". What is genuinely unchanged: the
  **slot ordering**, the rule that notes stay outside the block, **redaction**,
  and the **honesty rules**. What is *not*: the notes' content. The "For Kyle"
  briefing, the run-config note, the party-line `--kickoff` line, the `--audio`
  script and the Opus-5 builder notes each draw on a section this mode replaces,
  and "What the replaced sections fed" says where each reads from instead.
  Composable with `--audio` through that map.

I'm stopping here to switch to a fresh Claude Code session. Generate a
self-contained prompt I can paste into a new session so it picks up exactly
where we left off — no rediscovery, no repeated mistakes, no preamble.

Write for a fresh AI session, not a human reader. The fresh session has zero
memory of this conversation but has the same file/git access. Include only
what the fresh session cannot derive from `git status`, `git log`,
`gh pr list`, or reading the repo cold. Skip anything obvious from those.

## Before writing — orient silently

- `git status --branch` and `git log --oneline -10` to confirm the current
  branch/tree state and recent commits this session produced
- `gh pr list --state open --limit 10` if `gh` is available
- Re-skim any plan / source-of-truth file the session has been working from
  (e.g. `docs/<topic>-plan.md`, `BACKLOG.md`, an open PR body) — the fresh
  session will need its path
- Mine THIS conversation for landmines: hooks that blocked, commands that
  failed and then worked, decisions made, things the user explicitly said
  "do/don't do." These are the hard-won lessons. They are not in git.

## Output format

Print the handoff as a single fenced code block so I can copy it verbatim —
and print it **LAST**, so it's the final thing in the response, right above my
prompt box. Before the block, in this order: (1) the "For Kyle" briefing (see
"'For Kyle' briefing" below), then (2) the short run-config recommendation
described in "Run-config recommendation" below (3–5 lines), then (3) the
one-line note-written line **only in a party-line project** (see "Party-line
handoff note"), then (4) the audio note **only if `--audio` was passed** (see
"Audio narration") — all OUTSIDE the block, notes to me, not part of the
paste-able prompt; none of these pollute the block. Then the fenced block, with
nothing after it. Once it's printed, **STOP** — do not continue the current
work and do not ask "what's next." I'll start a fresh session.

Match my CLAUDE.md preferences: structured, concise but thorough, no filler,
name tradeoffs, quote exact paths/branches/PRs/commands rather than
paraphrasing.

## Handoff structure (sections, in order, inside the code block)

**With `--orchestrator`, this structure is replaced** — skip to "Orchestrator
mode" and use its sections instead. Everything else in this file still applies.

1. **Title** — `# Context handoff — <project>: <one-line topic>`

2. **Overview (2–4 sentences)** — what the project is in plain language,
   what's being continued, and the source-of-truth doc/file the fresh
   session should read first. Name the plan file and say what role it plays
   (e.g. "tracks status in a `## Changelog` section at the top").

3. **What's done** — terse bullets of work completed this session. Quote
   exact PR numbers, commit refs, file paths, branch names. Group by PR or
   branch if multiple are in play. Artifacts only, no subjective spin.

4. **Hard-won lessons (apply these)** — the most important section after the
   plan-stands one. Capture gotchas, workarounds, and conventions discovered
   THIS session that a fresh session would otherwise re-hit. Each bullet:
   - Quotes the exact command, file path, hook name, or error message
   - Frames as "X is the case; do Y" or "Z breaks; the path that works is …"
   - Examples worth capturing: pre-commit/push hooks that block direct push,
     repo-specific merge workflow (squash vs merge, branch naming, base
     branch), tools/CLIs the repo expects, env vars that must be set, files
     whose contents look authoritative but aren't, decisions already made
     under uncertainty (so the fresh session doesn't relitigate them),
     things I explicitly told you to do or not do
   - Skip generic advice — only session-specific landmines

5. **Where the plan stands** — the load-bearing section. Be specific:
   - What's in progress right now (file, branch, PR, line of work)
   - The next concrete action, as one imperative sentence
   - What's blocked and on what
   - Any decisions pending me — mark these clearly so the fresh session
     asks before acting, doesn't assume
   - The 1–3 files/branches/PRs the fresh session should open first

6. **Suggested skills** — name which of the fresh session's available skills
   apply to the next concrete action, one bullet each: skill name + why it
   fits (e.g. "adversarial-review — this PR is ready to merge and hasn't
   been reviewed yet", "gauntlet — next backlog item is a fresh story, not a
   bugfix"). The fresh session already has the full skill catalog in its own
   system reminder; the value here is narrowing it, not listing it — skip
   any skill that's a generic fit for "writing code" and name only the ones
   this specific next step calls for. Omit the section entirely if nothing
   beyond ordinary coding applies — don't force a pick.

## Redaction

Before printing anything — the "For Kyle" briefing, the run-config note, and
the fenced block alike — scan for secrets and personally identifiable
information: API keys, tokens, passwords, connection strings with embedded
credentials, private keys, and anything else that shouldn't sit in a
paste-able prompt. Redact with a placeholder that preserves the shape of what
was there (e.g. `sk-...REDACTED`, `<DB_PASSWORD>`) rather than silently
dropping the line — the fresh session still needs to know a credential goes
there, just not its value. If in doubt whether something is sensitive, redact
it; a fresh session can always ask me for the real value.

## Length

A few hundred words is normal. If the handoff is creeping past ~600 words,
you're including things derivable from git — cut those. If it's under ~150
words, you're probably missing the hard-won lessons — mine the conversation
harder.

**`--orchestrator` lifts the ~600-word cap** — a coordinator brief carries an
arc decomposition, worker mechanics and a boundary list that a continuation
handoff doesn't, and a real one runs ~800–1,400 words. The cap lifts; the
*discipline* behind it does not. Every line must be one of two things: a fact
the orchestrator cannot derive by reading the repo, or a verified fact that
saves it a lookup it would otherwise have to do (a symbol's file:line, a
baseline test count). Anything else is filler and costs the orchestrator
attention it needs for the gates.

## Honesty rules

If something is half-done or wrong, say so. If a decision was made under
uncertainty, flag the assumption so the fresh session can revisit. Don't
paper over gaps to make the handoff look tidy — gaps are exactly what the
fresh session needs to know about.

## Orchestrator mode (only if `--orchestrator` was passed)

The fresh session **coordinates an arc**: it decomposes nothing that this
session already decomposed, writes no feature code, and dispatches each unit of
work to a separate worker session in its own worktree — then reviews, merges,
and records. Without the flag, ignore this whole section.

An arc is worth orchestrating when the work splits into units a separate session
can hold in its head, and the coordination (gates, merges, tracker updates) is
real work in its own right. A single well-specified change is not an arc — write
an ordinary handoff for it.

### 1. First check whether `/orchestrate` already covers it

`/orchestrate` (`~/.claude/skills/orchestrate/SKILL.md`) is the existing runtime
for exactly this. **It fits when all four hold:**

- the tracker is a local-markdown one — `.scratch/<slug>/tickets.md` plus
  `issues/`;
- the specs live in those ticket files, not in the brief you are about to write;
- the frontier is genuinely wider than one, so seats buy wall-clock;
- every step in the arc is agent-shaped — nothing waits on Kyle's credentials,
  hardware, or physical presence.

**All four → write a thin brief.** Name the slug, the branch, anything
repo-specific `/orchestrate` cannot infer, and tell the session to run
`/orchestrate <feature-slug> [--seats N]`. Do not restate its mechanics; it owns
them and a copy will drift. Say in the "For Kyle" briefing that you did this and
why.

**Any one fails → write the full brief below**, and say in the "For Kyle"
briefing which of the four failed. That is the honest reason a hand-written
orchestrator exists for this arc, and it is also the bug report: a fit test that
keeps failing the same way is an argument for extending `/orchestrate`.

### 2. Verify the mechanics — never recall them

The worker-dispatch mechanics are the most fakeable content in the brief and the
most expensive to get wrong: a wrong flag or a missed invocation rule doesn't
error, it produces a worker that silently does the wrong thing, or no worker at
all. **Run the checks; quote what came back.**

- **A skill the worker must run in its first prompt.** Skills marked
  `disable-model-invocation: true` cannot be invoked on a worker's behalf — the
  worker's first prompt must *literally begin* with `/<skill-name>`, and the
  spec follows on the lines after it. Check before asserting it either way —
  `grep -m1 '^disable-model-invocation:' ~/.claude/skills/<name>/SKILL.md` — and
  grep rather than eyeballing a line range, since frontmatter length varies. As
  of 2026-09-09, 22 of the installed skills carry the flag (`implement`,
  `to-tickets`, `wayfinder`, `handoff`, …), so it is the common case, not an
  exotic one; recount rather than trusting that number. If the flag is absent,
  say so — a brief that demands the literal-first-line ritual where it isn't
  needed wastes a turn.
- **Cross-session tools.** `ListAgents` and `SendMessage` are usually deferred:
  the brief must tell the orchestrator to load them first with
  `ToolSearch` — query `select:ListAgents,SendMessage` — and to learn its **own**
  name from the first line of `ListAgents` output, because that is the address
  workers reply to. If Kyle renames the session mid-arc, the addressable name may
  not change; the brief should say to re-check rather than assume.
- **Worktrees.** One per worker, branched off the integration branch, e.g.
  `git worktree add -b <branch> .claude/worktrees/<name> <base>`. Confirm
  `.claude/worktrees/` is ignored (`.gitignore` or `.git/info/exclude`) and say
  so; an unignored worktree shows up as untracked noise in every worker's
  `git status` and in the orchestrator's own untouched checks.
- **Opening sessions — and the prompt, which is not an argument.** `/launch`
  takes **no prompt parameter**. It resolves the prompt as "the paste-able block
  this session most recently printed, with the fence markers stripped"
  (`commands/launch.md:52`). So the brief must tell the orchestrator to **print
  the worker's spec as a fenced block immediately before invoking `/launch`** —
  that block *is* the first prompt. Omit that and the best case is `/launch`'s
  stop rule halting for a turn; the worst is that the most recent block in a
  fresh orchestrator session is *the coordinator brief Kyle pasted in*, so worker
  one is auto-submitted the entire arc decomposition while Verified-start reports
  a perfectly healthy launch. `/orchestrate` states it outright
  (`orchestrate/SKILL.md:79-81`) and this path must too.
  **This is also what makes the first-prompt rule above satisfiable**: where the
  worker must fire a `disable-model-invocation` skill, the printed block's first
  line has to be `/<skill-name>`, with the spec on the lines after it. The two
  rules only compose that way — state them together, never three bullets apart.
  The invocation itself: `/launch <absolute-worktree-path> --model <id> --effort
  <level> --name <worker-name> --send`. Every flag there is real, and `/launch`
  verifies a new PID plus working directory plus command line, so a session that
  didn't start is reported, not assumed.
- **Waiting.** `SendMessage` with `notify_when_idle: true`. Never poll.

### 3. Sections, in order, inside the code block

Replaces "Handoff structure". Drop any section the arc genuinely has nothing
for; never pad one.

1. **Role** — who the session is and what it does not do, in two sentences.
   "You coordinate; you do not write feature code yourself" needs a companion
   clause or it fails open: say what to do when the worker machinery won't start
   (ask Kyle, or fall back to the Agent tool) and say explicitly **not** to
   quietly start building instead. A blocked orchestrator that starts coding is
   the failure mode this line exists to prevent.

2. **Orient first** — the read list, in order, and **the tracker, named
   explicitly**: GitHub Issues via `gh`, or `.scratch/<slug>/`, or something
   else. Say which it is *and* which it is not. An orchestrator that guesses the
   tracker wrong burns its first several tool calls and may write state into a
   directory nothing reads.

3. **Current state** — verified, with the receipts: the base SHA, the baseline
   test/lint counts, what closed recently, what is open and out of scope. This
   is what the orchestrator would otherwise spend twenty minutes rediscovering,
   and it is the section most worth being exact in.

4. **The arc** — each unit in order, with its full spec, plus the **topology,
   stated with its reason**: how wide the frontier is and why. Both errors are
   real and they fail differently. Manufactured parallelism puts two workers in
   the same file and surfaces as merge conflicts at the end, when the work is
   done and expensive to redo; missed parallelism just costs wall-clock, quietly.
   So state the width, give the reason (shared module, shared command, a
   sequential data dependency), and close with the anti-manufacture clause in
   both directions: *if you see a genuine independent split I missed, take it; do
   not manufacture one.*

   **Name any human-only step as a first-class member of the arc**, with what
   makes it human — real credentials, real spend, hardware, a physical check —
   and what the orchestrator does when it arrives: stop, hand Kyle a checklist,
   and go no further. This is the part no runtime can infer, and an arc that
   hides it produces an orchestrator that either stalls or improvises past a
   gate that exists for a reason.

5. **How to run workers** — only what section 2 verified. Include what each
   worker reports back and to whom, and the instruction that a worker which
   finds the spec contradicting the code should **stop and ask** rather than
   decide — that contradiction is the single most valuable thing a worker
   surfaces, and it is lost if the worker quietly picks one.

6. **Review gates** — how much review each unit gets, per CLAUDE.md's
   propose-first rule. **The delegation is Kyle's to give, and you may not
   invent it.** If he delegated the gate decisions in this session, quote him
   verbatim and say the orchestrator decides and records. If he did not, say so
   plainly and write the interactive default: propose the scope and **stop for
   his call**. Either way, state what still blocks a merge (critical and
   should-fix findings — fixed and verified, closed or downgraded by the judge,
   or waived by name) and that nice-to-haves become follow-ups. Never write a
   brief that reads as if Kyle delegated when he didn't.

7. **Tracker and git conventions** — the house pattern, read out of `git log`
   rather than assumed: PR title shape, branch-per-unit, squash or merge,
   whether the branch is deleted, what gets commented where, which items may be
   closed and which need Kyle's ruling, and the commit trailers CLAUDE.md
   requires.

8. **Ask Kyle when** — a short, specific list of the things that must not be
   guessed. The generic version ("ask if unsure") is worthless; the useful
   version names this arc's real forks. The reliable four: a spec contradicts
   the code; the worker machinery won't start; a review finding suggests a unit
   boundary is wrong; a decision would change what the feature *means* rather
   than how it's built. Close with "routine judgment calls are yours," or the
   brief produces a session that asks about everything.

9. **Boundaries** — what not to touch, each with its reason: out-of-scope
   issues by number, PRs awaiting Kyle's separate call, anything that would
   spend real money or hit a live account, and "do not refactor beyond what a
   unit needs."

10. **When the arc is done** — the reporting contract: what merged with SHAs,
    what each gate ruled and why, any checklist Kyle owes himself, and what the
    state of the backlog implies about what comes next. An orchestrator that
    isn't told what to report ends on "done."

**State lives in files, never only in messages.** Say this in the brief and give
it a test the orchestrator can apply: *you must be able to recover by re-reading
`<the tracker item>`.* Worker reports and cross-session messages evaporate on a
restart or a compaction; the issue, its comments, and the PR do not.

### 4. What the replaced sections fed

Replacing the block's structure is not a local change. **Five things outside the
block read the default sections** — the "For Kyle" briefing, the run-config note,
the party-line `--kickoff` value, the `--audio` script and the Opus-5 builder
notes — and every one needs an orchestrator source or it has no defined input.
This table is authoritative: when a future section is added to this file that
consumes the default structure, add its row here rather than discovering the gap
in a generated brief.

| Consumer | Reads by default | Reads under `--orchestrator` |
|---|---|---|
| "For Kyle" briefing | "Where the plan stands" (the next concrete action) | **"The arc"** — the next unit to be dispatched and what it unblocks |
| Run-config note | the model-pick guidance | **§5 below**, which overrides it |
| Party-line `--kickoff` | the next concrete action from "Where the plan stands" | **the first unit to dispatch**, as one imperative line under the same constraints (no newlines, no leading `--`, ~160 chars, no apostrophes) |
| `--audio` `short` | the Overview | **Role + "The arc"** — what this arc is and how it is split, 2–4 spoken sentences |
| `--audio` `long` | the Overview plus "Where the plan stands" | **those plus "Ask Kyle when"** — so the listener knows what will stop for them |
| Opus-5 notes, "complete spec up front" | plan file in the Overview; done-bar in "Where the plan stands" | **source-of-truth file in "Orient first"; done-bar in "When the arc is done"** |
| Opus-5 notes, delegation cap | final bullets of "Where the plan stands" | **omitted** — see the carve-out in "Opus 5 builder handoffs" |
| Opus-5 notes, deliverable length | final bullets of "Where the plan stands" | **"When the arc is done"** |

The "For Kyle" briefing also gains one obligation under this flag — §1's fit-test
result, in a clause — so its budget goes to **5–7 lines / ~150 words**. Nothing
else about it changes.

### 5. Run-config for an orchestrator session

Overrides the model-pick guidance in "Run-config recommendation" below; the
note's shape, placement and launch-command rule are unchanged.

Orchestrator sessions read far more than they write — worker reports, review
mailboxes, diffs, tracker threads — while the judgment stays bounded (gate
scope, triage, spec-vs-code calls) because this session already did the design.
That is **Opus 5 (1M context)** at **`high`**: `claude --model
'claude-opus-5[1m]' --effort high`. Go to `xhigh` only when the gates are
genuinely hard — a live account, money, or a security surface.

**If the pick wants to be Fable 5, the arc isn't ready to orchestrate.** Needing
a planner in the coordinator's seat means the decomposition is still open, and
dispatching workers against an unsettled decomposition wastes their work. Say
that in the run-config note and recommend finishing the design first.

## Party-line handoff note (only where the project has one)

Some projects run the **party-line** handoff suite: a `SessionStart` hook briefs every new
session with the newest note left on disk, and a `SessionEnd` hook writes a mechanical
digest for any session that didn't leave a better one. In those projects this command is
the *rich* writer, and the note it leaves disarms this session's digest.

Everywhere else **this section does not apply**: no probe result, no note, no extra line in
the output. The command behaves exactly as it does without this section.

**What the note is, and what it is not.** It is **not** how the successor I am launching
right now gets its context — the paste-able block still is. party-line's reader deliberately
holds back any pending note whose author process is still alive, and `/handoff` stops this
session without exiting it, so a window opened while this one is still up is handed nothing.
What the note guarantees is narrower and worth stating exactly: it disarms **this session's**
mechanical digest, and it is the newest note on disk *as of the write*. The next session
started here after this one exits is briefed with it **unless a later session leaves
something newer** — in a repo with concurrent sessions, a sibling that exits after this
write leaves a digest that is newer and immediately eligible, and this note drops to the
briefing memo's "Also pending" line instead. Still better crash insurance than the digest,
and still a better briefing on any return where I don't have the block in hand — but report
it in exactly those terms. Never tell me a session starting now will be briefed with it, and
never promise the *next* session will be, unconditionally.

### 1. Detect it — one command, before printing anything

```bash
gitroot="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
tmp="${TMPDIR:-/tmp}"; tmp="${tmp%/}"
for stateroot in "$PWD" "$gitroot"; do
  if [ -f "$gitroot/handoff/cli.mjs" ] && grep -q '"session_pid"' "$stateroot/.claude/party-line/handoffs/state/$CLAUDE_CODE_SESSION_ID.json" 2>/dev/null; then
    echo "PARTY_LINE_ACTIVE gitroot=$gitroot stateroot=$stateroot body=$tmp/party-line-handoff-$CLAUDE_CODE_SESSION_ID.md"
    break
  fi
done
```

No `PARTY_LINE_ACTIVE` on stdout → skip the rest of this section. Don't improvise a
different signal and don't run the writer on a hunch: `node handoff/cli.mjs` in some
unrelated project that merely happens to have that path would be executing a stranger's
script.

Both halves are required, and they prove different things:

- **`handoff/cli.mjs`** is the writer, and it lives at the git toplevel. Without it there
  is nothing to call.
- **the `"session_pid"` field in the per-session state file** is the *reader's* receipt.
  Only party-line's `SessionStart` hook stamps that field — its `UserPromptSubmit` hook can
  create the same file *without* it — so grep-for-the-field, not mere file existence, is
  what proves the hooks ran for THIS session in THIS project. It is also the writer's own
  precondition (`cli.mjs` refuses to write unless `session_pid` is an integer), so the
  probe checks the same thing the writer enforces.

The state file is probed at **both `$PWD` and the git toplevel** because the hooks root it
at the *session's* working directory (`input.cwd`), which in a session started in a
subdirectory of the repo is not the toplevel. `stateroot` is wherever it was found; the
writer call below needs both values.

**This detection is a judgment call, not a settled contract.** It is the simplest signal
that is reliable today, and it is worth revisiting when party-line promotes its hooks out
of a project's `.claude/settings.json` into user-level settings. If it ever stops firing
the failure is a silent no-op — `/handoff` just behaves as it does everywhere else — which
is the safe direction to fail in.

### 2. Write the note, before printing the response

1. **Write the composed block to `body`** (the path the probe printed) with the Write tool:
   the *contents* of the fenced block, byte for byte, without the fence markers. One
   composition, two destinations — the fresh session pastes the block, and the next session
   in this project is handed the same text by the `SessionStart` hook. Compose it here
   first and quote that same text when you print the block, so the two can never drift.

2. **Hand it to the writer** (`gitroot`, `stateroot`, and `body` are the probe's values —
   the script runs from the toplevel, the note lands where the hooks will look):

   ```bash
   node "<gitroot>/handoff/cli.mjs" write --source human --cwd "<stateroot>" --kickoff '<one line>' < "<body>"
   ```

   - `--source human` is what records that this session left a real note, which is what
     stops the `SessionEnd` digest from writing a second, worse one over the top of it.
     Never pass any other value from this command.
   - `--kickoff` is the **next concrete action** from "Where the plan stands", as one
     imperative line: no newlines, no leading `--`, under ~160 characters, and no
     apostrophes so the single-quoting stays simple. Under `--orchestrator` that
     section does not exist — take the first unit to dispatch instead, per "What
     the replaced sections fed".
   - It prints the note's path on success, and exits non-zero with a reason on failure.

3. **Delete `body`** — `rm -f "<body>"` — once the writer has returned, whatever it
   returned.

**If the writer fails, print its reason and carry on.** The paste-able block is the
deliverable and it is unaffected; a failed write just leaves the `SessionEnd` digest armed,
which is the fallback doing its job. Never retry with a different `--source`, and never
claim a note was written when the command exited non-zero.

### 3. Report it — one line, outside the block

In slot 3 of "Output format" (after the run-config note), one line addressed to me:

> **Party-line note:** written to `<the path the writer printed>` — it disarms this
> session's mechanical SessionEnd digest and is the newest note on disk as of now: the
> next session started here **after this one exits** is briefed with it unless a later
> session leaves something newer. The block below is still how the successor I launch now
> gets its context.

On failure, one line saying that instead, naming the reason the writer gave.

## "For Kyle" briefing (printed FIRST, at the top of the response)

Open the response with a short plain-English briefing addressed to me — before
the fenced block, never part of the paste. It's the human-facing twin of the machine handoff: its job
is to keep me oriented and engaged across the session boundary, the way a project's
`LEARNING.md` does. Label it clearly so I know it's for me, not for the paste:

> **📋 For Kyle — what the next session will build, and why**

Cover, in 4–6 lines / ~120 words max (5–7 / ~150 under `--orchestrator`, which
adds a clause):
- **What** it's about to build — the next chunk of work, in plain language.
- **How** — the approach in one sentence (the shape of it, not step-by-step).
- **Why** — the reasoning/motive: why this, why now, what it unblocks or proves.

Voice: explain it like I'm sharp but new to the jargon — plain English, define any term the
first time, clearer not longer. It's the plain-English distillation of "Where the plan stands"
(the next concrete action) — the forward-looking "what's coming + why," not a recap of what's
done. Under `--orchestrator` it distils **"The arc"** instead and adds the fit-test clause —
see "What the replaced sections fed". If the next step is genuinely uncertain or pending my
decision, say that plainly instead of inventing a plan.

**If the briefing cites any identifier** (`D31`, `F2`, `T3`, "slice C"), the global "Never show
me a bare identifier" rule applies here too: gloss each one on first mention, and put its
path + `code <path>` line **inside this briefing**. It belongs to slot (1), not to a new slot
appended to the note list — so the run-config note still closes the substance and the fenced
block is still the last thing in the response.

## Run-config recommendation (the second note, still before the code block)

After the "For Kyle" briefing, print a 3–5 line note — OUTSIDE the block, addressed to
me — telling me how to RUN the fresh session. It is never part of the
paste-able prompt (the fresh session can't set its own model/effort). Base the
pick on the *nature of the next concrete action* from "Where the plan stands,"
not on this session's work. Use this shape:

- **Model:** pick by the nature of the next session's work, per the
  "Planner/Builder Protocol" in CLAUDE.md —
  - **Fable 5** (`claude-fable-5`): judgment-first work — planning, design
    calls with real tradeoffs, adoption/triage decisions, convention-setting.
    The thinking dwarfs the typing.
  - **Opus 5** (`claude-opus-5`): a well-specified build — a plan already says
    what to do; the session mostly implements, tests, and lands it. Add
    "(1M context)" whenever the fresh session must read a lot of source /
    long docs / a big plan to orient.
  - **Sonnet 5** (`claude-sonnet-5`): mechanical, checklist-scoped work a
    careful junior could follow — template-driven file generation, rename
    sweeps, doc-formatting passes.
  - Split rule: if this handoff carries a settled plan, recommend a builder
    (Opus/Sonnet); if the next session must still decide or design, recommend
    Fable. And split only when build ≫ plan — for plan-heavy/build-light work,
    say so and recommend finishing in one Fable session instead.
- **Effort:** independent of the model pick, and drawn from the **effort ladder in
  CLAUDE.md's "Planner/Builder Protocol"** — that's the ladder's owner; the rungs
  below are its expansion, not a second ladder. Name exactly ONE, using only the
  CLI's real values (`--effort low|medium|high|xhigh|max`) or ultracode —
  - **ultracode** (multi-agent fan-out + adversarial verify; highest token cost):
    the next task is broad, parallelizable, or wants exhaustive coverage with
    independent verification — a multi-file audit/migration, a "find every X"
    sweep, a batch where each item is verified against HEAD, a comprehensive
    review. Pick when completeness across many surfaces beats speed. Launch
    form: `--effort ultracode` — a real, accepted flag (runs on an xhigh base).
    It needs **dynamic workflows enabled in `/config`**, and the flag path fails
    *silently*: with the setting off, `claude --effort ultracode` parses clean,
    prints no warning, and runs a plain xhigh single-agent session. So whenever
    you recommend ultracode, **spell that out in the note** — tell me to confirm
    dynamic workflows are on, or I won't get the fan-out the handoff promises.
    In-session alternative: `/effort ultracode` from an interactive terminal
    (that path refuses loudly instead of degrading).
  - **`max` / `xhigh`** (deep single-agent reasoning, no fan-out): the next
    task is ONE hard problem — subtle root-cause debugging, tricky
    merge/algorithm logic, untangling a confusing module, a design call with
    real tradeoffs. `max` removes the cap and burns fast; `xhigh` when it's
    hard but bounded.
  - **`high`**: ordinary build work with some judgment in it — a normal
    feature implemented inside a settled plan.
  - **`medium` / `low`**: mechanical or checklist-scoped work — a known small
    edit, a doc update, wiring a module per a fixed checklist, a
    straightforward test add (`low` for purely templated/repetitive). Don't
    pay for reasoning the task doesn't need.
- **Launch command (required):** close the note with the literal command, e.g.
  `claude --model claude-opus-5 --effort high`. For the 1M-context variant the
  model ID contains brackets, which zsh globs — always quote it:
  `claude --model 'claude-opus-5[1m]' --effort high`. Both flags are
  per-invocation only — my saved defaults stay untouched. Always print both
  flags explicitly, even if you suspect they match my current defaults: the
  explicit command is correct whatever the defaults are, and I may paste it
  into a machine or profile whose defaults differ.
- **Why (one clause):** tie the pick to the specific next action you named, so I
  can sanity-check it — e.g. "Opus 5 at max: 3 findings in 2 files, each just
  needs verify-against-HEAD + a minimal fix; too narrow to want fan-out."

Keep it terse, like the rest of the handoff. If the next action is genuinely
ambiguous between two modes, name both and say what tips it.

## Opus 5 builder handoffs

When the run-config model pick is **Opus 5**, read the builder notes —
`~/.claude/opus5-builder-notes.md` if present, else the vendored repo copy
`.claude/opus5-builder-notes.md` — before writing the fenced block and
apply their rules **within the handoff's existing contract** — the six-section
structure, the derivability rule, and the ~600-word cap all still govern:

- The notes' "complete spec up front" rule is satisfied by pointing, not
  inlining: name the plan / source-of-truth file in the Overview and state
  the next done-bar in "Where the plan stands" — the plan file carries the
  spec. Under `--orchestrator` both of those sections are gone: the
  source-of-truth file goes in "Orient first" and the done-bar in "When the
  arc is done". This section fires on **every** orchestrator run, since §5
  mandates Opus 5 — so the routing is the common path, not an edge case.
- Add the delegation-cap line — and the deliverable-length line when the
  next session will author documents — as the final bullets of "Where the
  plan stands." The cap line always applies here, whatever the recommended
  effort: a handoff block carries no delegation design of its own, so the
  notes' shape-test exception never fires — and an ultracode recommendation
  can silently degrade to a single-agent session, which is exactly the
  session the cap was written for.
- **Except under `--orchestrator`, where the cap line is omitted.** That
  block *is* a delegation design — the notes' own shape-test exception ("a
  single orchestrator dispatching subagents") fires on it, and a cap telling
  an orchestrator not to delegate contradicts the role the brief just gave
  it. The deliverable-length line still applies (an orchestrator authors PR
  comments, tracker comments and a final report), and lands in "When the arc
  is done" — orchestrator mode has no "Where the plan stands" section.
- Emit no verification boilerplate anywhere in the block.

The notes shape the paste-able prompt only — the "For Kyle" briefing and
run-config note are unaffected. If neither notes copy exists, say so in the
run-config note and write the block normally.

## Audio narration (only if `--audio` was passed)

Generate a spoken version of the brief so I can listen to it on a walk instead
of reading the block. Render the MP3 BEFORE printing the code block; its chat
note (path + play command) goes after the run-config note, so the paste-able
block stays the last thing in the output. It never changes the other sections'
content.

1. **Write a speakable script** — NOT the paste-able block (that's written for a
   fresh AI; reading its scaffolding aloud is useless). Condense for the ear:
   - `short` (default): just the **Overview** — what this work is and what's
     being continued, in 2–4 spoken sentences (~90s).
   - `long`: the Overview **plus Where the plan stands** — the next concrete
     action, anything blocked, and any decision pending me (~3–4 min).
   - Under `--orchestrator` neither section exists; "What the replaced sections
     fed" gives the substitute source for each level.
   - Follow the narrate skill's "Writing for the ear" rules: no Markdown, expand
     paths/branches/PR numbers into speech, drop commit SHAs and command blocks,
     open with "Here's where things stand…" and close on the one next thing.
2. **Hand it to the `narrate` skill** (`~/.claude/skills/narrate/`) with
   `voice=am_adam` and `out` = next to wherever this project saves session
   artifacts if there's a convention, else
   `~/Projects/_audio/<ISO-date>-<project>-handoff.mp3`. The skill ensures Kokoro
   is up, renders the MP3, and `SendUserFile`s it to me.
3. **One line in chat** with the saved path, then — on its own line, in a fenced
   code block — a ready-to-run play command: `afplay "<full-path>"` (the real
   absolute path). That way I can copy-paste it to listen if I want to, or ignore
   it. If Kokoro is unavailable, say so plainly — the text handoff still stands;
   don't claim an MP3 exists if it doesn't (and print no play command).
