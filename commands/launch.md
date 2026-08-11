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
2. **Model** — the model ID from the most recent run-config note.
3. **Effort** — the effort level from the same note.
4. **Prompt** — the paste-able block this session most recently printed, with the
   fence markers stripped. Never include the "For Kyle" briefing or run-config
   note; those are notes to Kyle, not part of the prompt.
5. **Send mode** — paste (default) or auto-submit (`--send`).

If no prompt can be resolved and none was supplied, **stop and say so** — a window
with no prompt is worse than no window, because it looks like it worked.

## Invariants

Referenced by name below. Each holds on every path.

- **Clipboard-always** — the prompt reaches the clipboard before any window opens,
  on every path including `--send` and every failure branch. A misfired launch then
  costs one ⌘V, not a regenerated handoff.
- **Verified-start** — never report a session as started without having seen its
  process. "I opened a window" and "Claude is running" are different claims.
- **Bracket-quoting** — 1M-context model IDs contain `[` and `]`, which zsh expands
  as a glob. Single-quote every model ID: `--model 'claude-opus-5[1m]'`.
- **No-blind-keystrokes** — never drive the keyboard through AppleScript System
  Events to type into an already-open window. It needs Accessibility permission and
  can type into whatever happens to be focused. A new window is always correct;
  typing into an existing one is not.
- **Config-is-disposable** — the Warp launch config is a scratch file rewritten on
  every invocation, never an artifact Kyle is expected to keep.

## Steps

1. **Copy the prompt to the clipboard** with `pbcopy`, before anything else
   (*Clipboard-always*).
2. **Detect the terminal** from `$TERM_PROGRAM`. `WarpTerminal` takes the Warp path;
   anything else takes the fallback path.
3. **Build the launch command** as one line: `claude --model <id> --effort <level>`,
   with the model ID single-quoted (*Bracket-quoting*). Under `--send`, write the
   prompt to a file under `$TMPDIR` and append `"$(cat '<file>')"` so the prompt
   arrives as a single argument regardless of what it contains.
4. **Warp path** — write `~/.warp/launch_configurations/claude-launch.yaml`
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
               - exec: <launch command from step 3>
   ```

5. **Fallback path** — `open -a "<terminal app>" <directory>` opens the window at the
   right directory but cannot start the session (*No-blind-keystrokes*). Say that
   plainly and give Kyle the literal launch command to run in it.
6. **Verify** (*Verified-start*) — after a short pause, look for the process with
   `ps -Ao pid,args` filtered to the launch command. Report the PID when found. When
   not found, say the window opened but the session did not start, and give the
   literal command — do not retry the launch a second time.

## Report

Three or four lines, outside any code block:

- Where the window opened, and whether the session is running (with PID) or needs
  the command run manually.
- Whether to paste (⌘V) or that the prompt was already submitted.
- Any honest caveat: fallback terminal, unverified start, an inferred directory that
  differed from cwd.

Then stop.
