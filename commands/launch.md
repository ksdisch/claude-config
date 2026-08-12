---
description: Open a new terminal window in a project directory and start a fresh Claude Code session there, with a prompt already on the clipboard (or auto-submitted via --send). Reads the target directory, model, and effort from the run-config note the current session just produced, and names the session descriptively via `claude --name` so it's findable in the resume picker instead of carrying an auto-generated title. Pass --remote to start it as a Remote Control session so the name also shows in the claude.ai/mobile session lists. macOS + Warp gets a real auto-start; other terminals get the window plus an honest "run this yourself" message.
argument-hint: "[dir] [--model <id>] [--effort <level>] [--name <session-name>] [--remote] [--send]"
allowed-tools: Bash, Read, Write
---

Launch a fresh Claude Code session in a new terminal window.

This is the last mile of `/handoff`, `/ship-and-route`, `/prompt-optimize`, and
`/backlog-hygiene` — each ends with a paste-able prompt plus a recommended model
and effort. This command turns that into an open window with the session running
and the prompt one ⌘V away.

It launches a session; it never does the work itself. After reporting, **stop** —
don't continue the current session's task.

## Parse `$ARGUMENTS`

- *(none)* → infer everything from this conversation (see Resolve inputs).
- A path → the target directory, overriding what was inferred.
- `--model <id>` / `--effort <level>` → override the inferred run config.
- `--name <session-name>` → override the derived session name.
- `--remote` → start the session in Remote Control mode, so the session (under its
  descriptive name) also appears in the claude.ai and mobile-app session lists and
  can be steered from the phone. Without it, the name shows only in
  `claude --resume` and the desktop app.
- `--send` → auto-submit the prompt instead of leaving it for Kyle to paste.
  **Incompatible with `--remote`** — a Remote Control invocation takes no initial
  prompt, so under `--remote` the prompt always arrives by ⌘V. When both are
  given, `--remote` wins; say in the report that `--send` was ignored and why.

## Resolve inputs

Six values are needed. Take each from `$ARGUMENTS` when given, otherwise infer:

1. **Directory** — the repo the next session works in. Infer from the most recent
   run-config note or handoff in this conversation; that is often *not* the
   current session's cwd. Fall back to cwd only if nothing names a directory.
   Must be absolute and must exist.
2. **Model** — the model ID from the most recent run-config note. Some producers
   name the model rather than its ID (`/prompt-optimize` emits
   `RUN WITH: [Model] · [effort] effort`); resolve those against the
   Planner/Builder Protocol in `CLAUDE.md` — Fable 5 → `claude-fable-5`, Opus 5 →
   `claude-opus-5`, Opus 5 1M → `claude-opus-5[1m]`, Sonnet 5 → `claude-sonnet-5`.
3. **Effort** — the effort level from the same note, one of `low`, `medium`,
   `high`, `xhigh`, `max`, or `ultracode`.
4. **Prompt** — the paste-able block this session most recently printed, with the
   fence markers stripped. Never include the "For Kyle" briefing or run-config
   note; those are notes to Kyle, not part of the prompt.
5. **Session name** — a short descriptive title for the new session, so the resume
   picker and session lists show what it's for instead of an auto-generated name.
   Derive it from the task the prompt describes: kebab-case, 2–5 words, leading
   with the project when the directory isn't obvious from the task
   (`doghood-stripe-webhooks`, `wiki-backfill-all-projects`). This is never a stop
   rule — a name is always derivable, worst case `<repo-basename>-handoff`. The
   same string becomes the Warp tab title in step 5 — and, under `--remote`, the
   Remote Control session title — so the paste target and every session list agree
   on what to call this session.
6. **Mode** — paste (default), auto-submit (`--send`), or Remote Control
   (`--remote`); the `--send`/`--remote` conflict resolves per the parse rules.

**Stop rules apply to all three of prompt, model, and effort.** If any of them
cannot be resolved and was not supplied, stop, say which one, and ask. Never fall
back to saved defaults: a window opened with no prompt, or a session running on a
different model than the note recommended, is worse than no window, because both
look like they worked.

## Invariants

Referenced by name below. Each holds on every path.

- **Clipboard-always** — the prompt reaches the clipboard before any window opens,
  on every path including `--send` and every failure branch. A misfired launch then
  costs one ⌘V, not a regenerated handoff.
- **Verified-start** — never report a session as started without having seen *a
  process that was not there before*. Multiple Claude sessions run on this machine
  routinely, and `/launch` exists to add more, so matching `ps` output against the
  launch command finds someone else's session and reports a failed launch as a
  success. Identity comes from a PID that is new, never from matching arguments —
  and the probe that produces those PIDs must match on executable name, or it
  counts itself and manufactures a new PID on every call. A new PID is necessary
  but not sufficient: confirm it is *the launched session* by checking its working
  directory equals the target directory and its command line carries the model and
  effort that were launched. A new PID at the wrong directory is someone else's
  session that happened to start during the wait.
- **Named-target** — with a dozen sessions running, "the new window" is not an
  identification. The report must name the destination — the Warp tab title, or on
  the fallback path the terminal application and directory — and when the "before"
  probe found other sessions already running, it must say so and warn that a stray
  ⌘V into one of them runs the handoff on the wrong model in the wrong directory
  while looking exactly like success. That failure mode has happened; the window
  this command opens is not necessarily the window Kyle is looking at.
- **Bracket-quoting** — 1M-context model IDs contain `[` and `]`, which are a glob
  to zsh and a character class to `grep`. Single-quote every model ID for the shell
  (`--model 'claude-opus-5[1m]'`) **and** match it only with `grep -F`, never as a
  pattern: `grep 'claude-opus-5[1m]'` does not match the literal string.
- **No-blind-keystrokes** — never drive the keyboard through AppleScript System
  Events to type into an already-open window. It needs Accessibility permission and
  can type into whatever happens to be focused. A new window is always correct;
  typing into an existing one is not.
- **Config-is-disposable** — the Warp launch config is a scratch file rewritten on
  every invocation, never an artifact Kyle is expected to keep.
- **Exec-rooted** — the Warp launch runs the session under the shell builtin `exec`,
  so the session process *replaces* the tab's shell instead of running under it.
  This is what lets a session end its own window: a session that exits (pi's
  `PI_HANDOFF_RETIRE=auto` retirement, or a plain `/quit`) leaves no shell behind
  for the tab to fall back to. Verified on this Mac 2026-08-12: Warp runs
  launch-config commands through a shell, so the builtin is available, and the
  exec'd process is a *direct child of Warp* (`ps -p <pid> -o ppid=` → the Warp
  binary) — it is the tab's root process, not a grandchild. The price: a launch
  command that fails to start takes the window down with it, so a failed launch
  leaves nothing to read the error in (see Report).

## Steps

1. **Copy the prompt to the clipboard** with `pbcopy`, before anything else
   (*Clipboard-always*).
2. **Detect the terminal** from `$TERM_PROGRAM` and map it to an application name —
   these are different strings, and the raw `$TERM_PROGRAM` value is not something
   `open -a` can resolve (`WarpTerminal` and `Apple_Terminal` both fail; `Warp` and
   `Terminal` both work):

   | `$TERM_PROGRAM` | Application |
   |---|---|
   | `WarpTerminal` | Warp — takes the Warp path in step 4, not the fallback |
   | `Apple_Terminal` | `Terminal` |
   | `iTerm.app` | `iTerm` |
   | `ghostty` | `Ghostty` |
   | `vscode` | `Visual Studio Code` |
   | anything else, or unset | `Terminal` — the named default; `$TERM_PROGRAM` is unset over ssh and in bare shells |

3. **Snapshot the running sessions** (*Verified-start*) — record the PID set from exactly
   `pgrep -x claude`. This is the "before" set that step 7 diffs against, and the same
   invocation is used at both ends of the diff. Call it **the session probe**.

   The probe matches on the executable name being exactly `claude`. Do not substitute a
   `ps | grep` for it: any pattern matching the *command line* also matches the `grep`
   itself and the shell wrapper the command runs in, both of which get a fresh PID every
   invocation. Two such snapshots taken seconds apart, with no launch in between, differ by
   three PIDs — so the diff finds a "new session" every time and can never report failure.
4. **Build the launch command** as one line:
   `claude --model <id> --effort <level> --name '<session name>'`, with the model
   ID single-quoted (*Bracket-quoting*) and the session name single-quoted too — it
   may contain spaces or shell-significant characters. The flags appear in exactly
   that order, because step 7 compares against this line as a literal prefix.
   `--name` sets the session's title at launch, so `claude --resume` and the
   session lists show the descriptive name instead of an auto-generated one.

   First check the flag is supported: `claude --help 2>&1 | grep -F -- '--name'`.
   On an older CLI where it isn't, build the command without `--name` and note in
   the report that the session launched unnamed and Kyle can run
   `/rename <session name>` inside it — never pass a flag the binary would reject,
   because a rejected flag means no session at all.

   **Under `--remote`**, the command is instead
   `claude --remote-control '<session name>' --model <id> --effort <level>` — the
   session name rides as the positional argument to `--remote-control` (that *is*
   the Remote Control naming syntax; no separate `--name`), and the session is
   still a normal interactive terminal session locally, with the phone as an extra
   control surface. Probe `claude --help 2>&1 | grep -F -- '--remote-control'`
   the same way; if unsupported, fall back to the plain named launch above and say
   in the report that the name won't reach the mobile list. No prompt argument is
   ever appended on this path — Remote Control takes no initial prompt.

   Under `--send` (non-remote only), write the prompt to a file under `$TMPDIR`
   and append `"$(cat '<file>')"` so the prompt arrives as a single argument
   regardless of what it contains.
5. **Warp path** — write `~/.warp/launch_configurations/claude-launch.yaml`
   (*Config-is-disposable*), creating the directory if absent, then open
   `warp://launch/claude-launch`. The schema, which is the one exact literal here:

   ```yaml
   ---
   name: claude-launch
   windows:
     - tabs:
         - title: <session name>
           layout:
             cwd: <absolute directory>
             commands:
               - exec: exec <launch command from step 4>
   ```

   The doubled word is not a typo and must not be "cleaned up". The outer `exec:`
   is Warp's YAML key for "the command this tab runs"; the second `exec` is the
   shell builtin, and it is what makes the session the tab's root process
   (*Exec-rooted*). Without it the session runs *under* a shell, and a session that
   exits — a retiring pi session, or any `/quit` — drops back to a shell prompt in
   a window that then sits on the desktop forever.

   `exec` does not appear in the resulting process's argv, so step 7's literal-prefix
   comparison against the step-4 command is unaffected.

   **Open, one-time:** whether Warp *closes* the tab (and with it a single-tab window)
   once that root process exits was not verifiable from a shell — Warp's windows do not
   answer an AX window count, so it needs one human look. To check: write a scratch launch
   config with this same schema whose command is `exec zsh -c 'sleep 10'`, open it with
   `open warp://launch/<name>`, and watch whether the tab closes itself when the sleep
   ends. Record the answer here, with the Warp setting it depends on if it needs one.

   Until it is recorded, `exec` is a bet, not a free option. If Warp does close the tab,
   this is the whole feature. If it does not, the trade is a dead "process exited" tab
   where there used to be a live shell prompt — worse for a window Kyle wanted to reuse,
   and worse for reading a failed launch's error (see Report). It is still the
   precondition for any close-on-exit behavior, which is why it lands before the answer.

   If the answer comes back "no", the revert is five sites, not one line — and half a
   revert is worse than none, because it leaves this file telling the agent to report "the
   window is probably gone" while a live shell prompt sits in that tab. All of these go
   together: the inner `exec` in the schema above, the paragraph below defending it against
   exactly this cleanup, the argv note, step 7's Warp branch, and the Report bullet — plus
   the *Exec-rooted* invariant they all cite.

6. **Fallback path** — `open -a "<application from step 2>" <directory>` opens the
   window at the right directory but cannot start the session (*No-blind-keystrokes*).
   Check `open`'s exit status: a non-zero status means no window appeared, and the
   report must say that rather than claiming one opened. Then give Kyle the literal
   launch command to run in it.
7. **Verify** (*Verified-start*) — wait 3 seconds, run the session probe from step 3
   again, and diff it against the "before" set. Every PID present now and absent then
   is a candidate — more than one session can start during the wait, and novelty alone
   cannot tell the launched one from a stranger's. Retry the diff twice more, 3 seconds
   apart, before concluding no session started — the CLI takes a moment to exec. Never
   treat a PID from the "before" set as the new session, however well its arguments
   match.

   Then run both identity checks against **each** candidate; the launched session is
   whichever candidate passes both:
   - **Directory** — `lsof -a -p <pid> -d cwd` names its working directory; it must
     equal the target directory from step 1 of Resolve inputs.
   - **Command** — `ps -p <pid> -o command=` shows its command line; the line must
     *begin with* the launch command from step 4, quoting stripped — the shell removes
     the quotes before exec, so the head of the line reads `claude --model <id>
     --effort <level> --name <session name>` unquoted (without `--name` when the
     flag-support check in step 4 dropped it), or under `--remote`
     `claude --remote-control <session name> --model <id> --effort <level>`. Compare the head of the line against that literal
     prefix as fixed strings, never as a pattern (*Bracket-quoting*), and never search
     the whole line: under `--send` the entire prompt rides in the command line, and a
     model ID or effort word occurring in the prompt's prose satisfies a whole-line
     search while the actual flags are wrong.

   Three outcomes, each reported honestly: a candidate passes both checks → the
   session is verified; report that PID. Candidates appeared but none passes both →
   say a session started somewhere but it is not the launched one, and treat the
   launch as unverified. No new PID → the session did not start; give the literal
   command and do not retry the launch itself. On the Warp path do **not** say the
   window is waiting for it: the session is the tab's root process (*Exec-rooted*),
   so a command that failed to exec took the tab down with it. Say the window is
   probably gone and the command needs one Kyle opens himself. Only on the fallback
   path, where `open -a` opened a plain shell window, is "the window is open, run
   this in it" true.

## Report

Four or five lines, outside any code block:

- Where the window opened — or that it did not, when `open` returned non-zero.
- Whether the session is verified running (new PID + both identity checks), or
  needs the command run manually.
- **The exact command that was launched**, so a wrong inferred model, effort, or
  session name is visible rather than silently in force.
- **Where to paste** (*Named-target*) — the Warp tab title from step 5, or the
  application and directory on the fallback path; then ⌘V, or that the prompt was
  already submitted. The session name doubles as the identity to look for in
  `claude --resume` and the session lists later. When the "before" probe found
  other sessions running, add the warning *Named-target* requires.
- On the Warp path, when no session started: say the window is probably gone rather
  than waiting (*Exec-rooted* — a command that failed to exec took the tab with it),
  so the literal command needs a window Kyle opens himself. Never re-fire the launch
  to "see what happens".
- Any honest caveat: fallback terminal, unverified start or failed identity check,
  an inferred directory that differed from cwd, a CLI too old for `--name`
  (session launched unnamed — run `/rename <session name>` inside it), or `--send`
  ignored because `--remote` was also given. On the `--remote` path, when the
  window opened but no session started, say that Remote Control has its own
  preconditions the probe can't see — it needs a claude.ai login (not an API key)
  on a paid plan, is disabled under a custom `ANTHROPIC_BASE_URL` or
  telemetry-off env vars, and the docs don't guarantee `--model`/`--effort`
  compose with it — and give the literal command so Kyle can run it and read the
  actual error.

Then stop.
