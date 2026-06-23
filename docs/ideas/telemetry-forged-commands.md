# Telemetry-Forged Commands: the config writes itself from how you actually work

**Status:** Idea — not committed. Added by `/brainstorm` (`moonshot` mode) on 2026-06-18.
**Lens:** contrarian-inverter · **Fit:** identity-shift · **Boldness:** audacious

## Premise

claude-config's deepest asset is compounding leverage: every codified workflow makes
every future session faster. But the codification step is a manual bottleneck gated on
one human's memory — a workflow only becomes a command if Kyle notices the pattern AND
sits down to write prose for it (A4 + A3). The richest record of what's worth codifying —
what he actually does repeatedly, by hand, across sessions — already exists as transcript
JSONL and is never read. `/forge` closes that loop: the config stops being purely a library
of **declared** intentions and becomes partly a **mirror of revealed behavior**. Kyle shifts
from sole author to editor/ratifier of his own tooling; the source of truth for "what commands
should exist" moves from memory to evidence.

## The bet

The one thing that must be true: **your transcripts contain enough repeated, recognizable
multi-step sequences that a draft synthesized from them is a better starting point than a blank
file** — that revealed behavior out-predicts declared intent for what tooling you need next.
(Targets **A3** — commands are hand-authored prose; correctness only surfaces at runtime.)

Verified feasible: the JSONL yields ordered, labeled `tool_use` records (Bash descriptions, file
paths, commands) per session, and the house style is a hard copyable template (frontmatter:
`description`/`argument-hint`/`allowed-tools`, then numbered Steps).

Veteran reaction: *"So it'll lovingly automate my bad habits — mine the workaround I did four
times, ship it as a sanctioned `/command`, and now my cruft is canon."* That objection **is** the
design center, not a footnote: forge proposes, never lands; the human edit-at-the-PR is where a
repeated hack gets promoted to a real workflow **or** thrown out. The bet fails if the clusters are
all noise (every session bespoke) or all already-covered — which is exactly what the read-only
wedge measures before a single line is generated.

**Why now:** The corpus is large enough to mine (claude-config alone has 6+ transcripts, newest
~662 records / 1.7 MB; ~90 project history dirs under `~/.claude/projects`) and the house style has
stabilized across 18 commands + 11 skills. `claudify-repo` already established that
Claude-proposes-tooling-as-a-PR is acceptable here — but its recommender proposes from **static**
repo analysis, blind to what you actually did by hand. `/forge` is the missing evidence-driven half.

## Credible first step

Write `commands/forge-scan.md` — a read-only prose spec (frontmatter `allowed-tools: Bash, Read,
Glob, Grep`, exactly like `smoke-test.md`/`boot_server.md`) that greps the current project's
`~/.claude/projects/<slug>/*.jsonl` for assistant `tool_use` blocks, reconstructs ordered sequences,
clusters repeated multi-step patterns (e.g. Bash-boot → screenshot → Read-diff → Edit, seen N times),
and **prints** the top 3 "you keep doing this by hand" clusters with frequency + a one-line "candidate
command?" verdict and whether an existing command already covers it. No generation, no PR — just the
mirror. Proving the signal exists (and isn't already-covered noise) is the entire first sitting and the
gate on everything downstream.

## Decisions / open questions

- **Cluster identity:** what counts as "the same sequence" — exact tool+arg match, tool-name n-grams,
  or fuzzy/semantic grouping? Start crude (tool-name n-grams with a frequency floor); get smarter only
  if the wedge shows too much noise.
- **Cross-project vs in-project:** the wedge starts in the current project's transcripts; does `/forge`
  eventually mine all of `~/.claude/projects` to find sequences repeated across *different* projects (the
  strongest "this is a general workflow" signal)? Likely yes for forge; wedge stays in-project to stay cheap.
- **Already-covered detection:** forge must diff candidate clusters against the existing ~29 commands/skills
  so it proposes new tooling, not a worse clone of `/smoke-test`.
- **Anti-cruft guard:** should forge weight recent/repeated-but-not-yet-automated sequences and down-weight
  one-off workarounds, so it doesn't canonize bad habits? The veteran's objection lives here.
- **Bloat ceiling:** more auto-proposed commands worsens A4. Does forge owe a paired **subtract** — propose
  merges/deprecations of commands the transcripts show you never invoke — so the library curates as well as grows?

## Dependencies

- Read access to `~/.claude/projects/<slug>/*.jsonl` — confirmed present and parseable (`tool_use` blocks
  carry name + input).
- The JSONL transcript schema staying stable enough to parse (`type=assistant`,
  `message.content[].type=tool_use`); the spec should degrade gracefully on a format change, not hard-fail.
- The house-style template staying consistent (frontmatter + numbered Steps) — true today across `commands/`.
- The `claudify-repo` / `claude-automation-recommender` PR-proposal pattern as the precedent + mechanism for
  landing Claude-authored tooling as a reviewable branch.
- git branch+PR flow (the global workflow already mandates branch-per-change).

## Explicitly out of scope (revisit later)

- Auto-merging forged commands — forge proposes branches+PRs only; the human edit/approve at the PR is the
  whole point and is never automated away.
- A runtime hook/daemon that watches sessions live — forge is an explicit on-demand pass over **past**
  transcripts; no background process, no `settings.json` hooks in v1.
- Committing or syncing transcript JSONL anywhere — it stays gitignored and local.
- Solving A1/A2 (symlink fragility, vendor drift) — forge is squarely an A3 move.
- Generic "analyze any repo for automations" — that's already `claude-automation-recommender` (static
  analysis); forge is specifically your-behavior-driven and must not duplicate it.
- Auto-validating that a forged command actually works (no tests/CI exists — A3); forge improves the draft,
  not the verification gap.

## Identity/positioning note

Shifts what claude-config IS: from a hand-curated library of **declared** intentions (Kyle is sole author;
a command exists because he wrote it) to a self-observing system where part of the corpus is **synthesized**
from **revealed** behavior (Kyle becomes editor/ratifier; the source of truth for "what should exist" moves
from memory to transcript evidence). The read-only `forge-scan` wedge is tethered and safe to ship, but it is
explicitly the proof-of-signal that **earns** the authorship flip — not a way to avoid making it. The
human-approval gate is what keeps the shift honest (it's where judgment promotes a habit to a workflow), not
what cancels the boldness.
