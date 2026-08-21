---
description: Generate a self-contained handoff prompt I can paste into a fresh Claude Code session to continue this work without losing context. Captures hard-won lessons, what's done, and where the plan stands. Also prints a short plain-English 'what's next & why' briefing for me, so I stay oriented across the handoff. Stops the current work after generating. Project-agnostic.
argument-hint: "[--audio [short|long]]"
allowed-tools: Bash, Read, Write, Glob, Grep, Task, Skill, ToolSearch, SendUserFile, mcp__plugin_voicemode_voicemode__service
---

Context handoff.

## Parse `$ARGUMENTS`
- `--audio` → after printing the handoff, also generate a spoken-audio version
  of the brief (see "Audio narration" at the end). Optional level: `short`
  (default) or `long`. Without `--audio`, ignore all audio steps entirely —
  the command behaves exactly as before.

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

## Honesty rules

If something is half-done or wrong, say so. If a decision was made under
uncertainty, flag the assumption so the fresh session can revisit. Don't
paper over gaps to make the handoff look tidy — gaps are exactly what the
fresh session needs to know about.

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
     apostrophes so the single-quoting stays simple.
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

Cover, in 4–6 lines / ~120 words max:
- **What** it's about to build — the next chunk of work, in plain language.
- **How** — the approach in one sentence (the shape of it, not step-by-step).
- **Why** — the reasoning/motive: why this, why now, what it unblocks or proves.

Voice: explain it like I'm sharp but new to the jargon — plain English, define any term the
first time, clearer not longer. It's the plain-English distillation of "Where the plan stands"
(the next concrete action) — the forward-looking "what's coming + why," not a recap of what's
done. If the next step is genuinely uncertain or pending my decision, say that plainly instead
of inventing a plan.

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
  spec.
- Add the delegation-cap line — and the deliverable-length line when the
  next session will author documents — as the final bullets of "Where the
  plan stands." The cap line always applies here, whatever the recommended
  effort: a handoff block carries no delegation design of its own, so the
  notes' shape-test exception never fires — and an ultracode recommendation
  can silently degrade to a single-agent session, which is exactly the
  session the cap was written for.
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
