---
description: Open a new terminal window in a project directory and start a fresh Claude Code session there, with a prompt already on the clipboard (or auto-submitted via --send). Reads the target directory, model, and effort from the run-config note the current session just produced. macOS + Warp gets a real auto-start; other terminals get the window plus an honest "run this yourself" message.
argument-hint: "[dir] [--model <id>] [--effort <level>] [--send]"
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
- `--send` → auto-submit the prompt instead of leaving it for Kyle to paste.

## Resolve inputs

Five values are needed. Take each from `$ARGUMENTS` when given, otherwise infer:

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
5. **Send mode** — paste (default) or auto-submit (`--send`).

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
  success. Identity comes from a PID that is new, never from matching arguments.
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

3. **Snapshot the running sessions** (*Verified-start*) — record the set of PIDs whose
   args contain `claude --model`, matched with `grep -F`. This is the "before" set that
   step 7 diffs against.
4. **Build the launch command** as one line: `claude --model <id> --effort <level>`,
   with the model ID single-quoted (*Bracket-quoting*). Under `--send`, write the
   prompt to a file under `$TMPDIR` and append `"$(cat '<file>')"` so the prompt
   arrives as a single argument regardless of what it contains.
5. **Warp path** — write `~/.warp/launch_configurations/claude-launch.yaml`
   (*Config-is-disposable*), creating the directory if absent, then open
   `warp://launch/claude-launch`. The schema, which is the one exact literal here:

   ```yaml
   ---
   name: claude-launch
   windows:
     - tabs:
         - title: <short title>
           layout:
             cwd: <absolute directory>
             commands:
               - exec: <launch command from step 4>
   ```

6. **Fallback path** — `open -a "<application from step 2>" <directory>` opens the
   window at the right directory but cannot start the session (*No-blind-keystrokes*).
   Check `open`'s exit status: a non-zero status means no window appeared, and the
   report must say that rather than claiming one opened. Then give Kyle the literal
   launch command to run in it.
7. **Verify** (*Verified-start*) — wait 3 seconds, then take the PID set again the same
   way as step 3 and diff it against the "before" set. A PID present now and absent
   then is the new session; report it. Retry the diff twice more, 3 seconds apart,
   before concluding it did not start — the CLI takes a moment to exec. Never treat a
   PID from the "before" set as the new session, however well its arguments match.
   When no new PID appears, say the window opened but the session did not start, and
   give the literal command — do not retry the launch itself.

## Report

Three or four lines, outside any code block:

- Where the window opened — or that it did not, when `open` returned non-zero.
- Whether the session is running, with the new PID, or needs the command run manually.
- **The exact command that was launched**, so a wrong inferred model or effort is
  visible rather than silently in force.
- Whether to paste (⌘V) or that the prompt was already submitted.
- Any honest caveat: fallback terminal, unverified start, an inferred directory that
  differed from cwd.

Then stop.
