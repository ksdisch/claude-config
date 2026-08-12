# Session auto-close: the `/launch` companion that reaps finished sessions

**Status:** Planning handoff — ready to paste. Requested by Kyle on 2026-08-12
as the companion to `/launch` (PRs #75/#76).

## Premise

`/launch` solved starting: it opens a new terminal window, starts a verified
Claude Code session in it, and names the tab to paste into. Nothing solves
stopping. Finished sessions — handed off, wrapped, or simply abandoned — leave
their Warp windows and tabs on the desktop until Kyle sweeps them by hand, and
the more `/launch` gets used, the faster they pile up. Sessions need the
ability, and the insight, to close sessions that are *for sure* done being
used.

The asymmetry that shapes the whole design: on the launch side a mistake costs
one ⌘V into the wrong window. On the close side a mistake **kills a live
session and destroys in-flight work**. False negatives (clutter survives) are
cheap; false positives are the disaster. Every open question below bends
conservative because of this.

## 📋 For Kyle — what the next session will build, and why

**What:** a plan for the `/launch` companion — the thing that notices a Claude
session is truly finished and closes it (or tells you exactly which windows
are safe to close), so your desktop stops collecting dead terminal tabs.

**How:** a Fable planning session that first runs one experiment on your Mac —
can a script actually make Warp close a tab? — then decides what "for sure
done" means, where the reaper lives, and how much it may do without asking.
The output is a plan doc in `docs/plans/`; if the build turns out small, the
same session builds it.

**Why:** `/launch` made opening sessions one command; closing them is still
manual, so the convenience leaks clutter. This closes the loop.

## Run-config note

- **Model:** Fable 5 — four open design questions with real tradeoffs and a
  destructive-op consent model to settle before any code exists; the thinking
  dwarfs the typing. Not a builder model: there is no settled plan yet.
- **Effort:** `xhigh` — one hard, bounded design problem. No fan-out wanted;
  the feasibility experiment and the decisions are sequential.
- **Must run on the Mac**, not in a cloud session — question 1 of the handoff
  is a hands-on Warp experiment.
- Launch command: `claude --model claude-fable-5 --effort xhigh`
- If the settled design is build-light (one command file plus doc rows), finish
  the build in the same session — per the Planner/Builder Protocol's split
  rule, a second handoff would cost more than it saves.

## Handoff prompt (ready to paste)

```
# Context handoff — claude-config: plan the /launch companion that closes finished sessions

## Overview

claude-config is Kyle's global Claude Code config repo (commands/, skills/,
agents/, docs/) — it is what `~/.claude` serves on his Mac. `/launch`
(commands/launch.md, PRs #75/#76) opens a new terminal window and starts a
verified Claude session in it. This session plans its missing companion:
giving sessions the ability and insight to close sessions that are *for sure*
done being used, so finished Warp windows/tabs stop accumulating on the
desktop. Nothing is built or decided yet — greenfield planning. Deliverable: a
plan doc at docs/plans/2026-08-12-session-auto-close-plan.md (precedent:
docs/plans/2026-07-28-usage-playbook-plan.md) settling the questions below and
specifying a phased build, itself ending with a Run-config note for the
builder (CLAUDE.md § Planner/Builder Protocol). If the settled design is
build-light — one command file plus its doc rows — build it in this same
session rather than handing off again.

## What's done

Nothing on this feature. What exists and constrains it:
- commands/launch.md — the sibling. Its Invariants section is the binding
  prior art on identifying one session among many.
- commands/handoff.md and commands/wrap.md — both mark logical end-of-session
  today (handoff explicitly stops the current work; wrap is the end-of-session
  recap), but neither records that fact anywhere a reaper could read.
- Kyle's ask, near-verbatim: sessions need the "ability / insight" to close
  sessions that are for sure done being used, so the desktop doesn't get
  cluttered.

## Hard-won lessons (apply these)

- Probe sessions with exactly `pgrep -x claude`. Any ps-piped-to-grep pattern
  on the command line matches the grep itself and its wrapper shell —
  launch.md step 3 documents this manufacturing phantom PIDs. Session identity
  is PID + cwd (`lsof -a -p <pid> -d cwd`) + command-line head compared as
  fixed strings: model IDs like claude-opus-5[1m] glob in zsh and are char
  classes to grep, so quote them and match with grep -F only.
- No-blind-keystrokes (launch.md invariant): never drive AppleScript System
  Events keystrokes at existing windows — needs Accessibility permission and
  can hit whatever is focused. UI-scripting a window closed hits the same
  wall; off the table unless the plan explicitly gates it.
- Several Claude sessions run routinely — that is why /launch exists — so "the
  finished one" is never identifiable by novelty or argument-matching alone.
- CLAUDE.md's Git Workflow makes destructive/irreversible ops ask-first.
  Killing sessions is destructive; the consent model is a design section, not
  an implementation detail.
- Repo mechanics: a new command lands with its docs/command-skill-reference.md
  row and docs/usage-playbook.md card in the same commit (pre-push hook
  scripts/check-doc-sync.py blocks otherwise), and every PR gets the
  adversarial-review loop before merge — command files never qualify for the
  trivial-diff skip.

## Where the plan stands

Open design questions, in order:

1. Feasibility linchpin first — what can actually close a Warp tab/window on
   macOS? Experiment on this Mac: does Warp close a tab when the root shell
   process under it exits (does killing the shell tree suffice)? Any
   AppleScript or URL-scheme surface? The answer decides whether this feature
   is "close windows" or "kill processes and print which tabs are now safe to
   close by hand." Do not design past this unknown.
2. What does "for sure done" mean? Candidate signals, strongest first:
   (a) self-declaration — /wrap and /handoff already mark logical done and
   could write a tombstone (PID, tty, cwd, timestamp) a reaper trusts;
   (b) the claude process already exited but the window remains;
   (c) inference — PR merged, idle time. Decide whether anything below (a)/(b)
   ever qualifies, given the false-positive asymmetry.
3. Where the reaper lives: a command (/reap?), a step appended to /wrap and
   /handoff, a /launch pre-step (close done sessions before opening new), or a
   hook — and where the insight lives: a registry/tombstone file the commands
   maintain vs. pure runtime probing.
4. Consent model: auto-close only self-declared/exited sessions vs. propose a
   list and confirm. Surface this to Kyle as labeled options with a
   recommended pick (CLAUDE.md clarifying-questions preference) before
   finalizing the plan.

Next concrete action: read commands/launch.md, commands/handoff.md, and
commands/wrap.md, then run the question-1 Warp experiment.

Blocked: nothing. Pending Kyle: the question-4 pick.
Open first: commands/launch.md · commands/handoff.md · commands/wrap.md ·
CLAUDE.md (Git Workflow + Planner/Builder Protocol).
```
