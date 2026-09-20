# Spec: `retire` — evidence-ranked subtraction for the steering surface

Status: ready-for-agent
Date: 2026-09-18
Branch: `feat/retire-skill` (PR #132)
Design record: `docs/superpowers/specs/2026-09-17-retire-skill-design.md` (§14 carries the grill amendments this spec encodes)
Code-level reference: `docs/plans/2026-09-17-retire-skill.md` (where its code conflicts with this spec, this spec wins)

## Problem Statement

Kyle's Claude Code configuration only ever grows. Every skill, command, agent, plugin, MCP server, hook, and `CLAUDE.md` section was added for a reason, but nothing has a removal path, so old intent keeps steering new sessions: it changes how a session interprets an ask, which skill it routes to, how it plans, and how it builds. Every request also pays for the always-loaded bytes of things Kyle no longer uses.

Kyle can no longer see the whole steering surface. He cannot answer "what is shaping my sessions right now, and which of it have I actually used?" without a manual sweep. Every past removal was a one-off (a memory prune, a fork retirement, two commands renamed to `.disabled`, a connector prune), and each left something behind: routes that still point at a disabled command, a third-party doc describing files that are gone, disabled hook entries lingering as comment-only commands, and no record of why anything was removed or how to get it back.

The existing `/trim-context` command relocates content so it loads on demand; it never deletes. The config has no subtract verb.

## Solution

A `retire` skill that gives the config its subtract verb, backed by an inventory Instrument.

Running `/retire` inventories every global steering surface with evidence attached (always-loaded bytes, how often Kyle typed it, how often a session chose it, when it was last used, who routes to it, whether it duplicates a plugin, whether it routes to something missing, how old it is), assigns each item a temperature, and proposes a verdict from a fixed precedence table. Kyle rules on one titled table, by row. Only after that ruling does the skill apply anything, and it applies with complete bookkeeping: the file, the index row, the playbook card, the referrers, the mentions in other docs, the ignore rules, the settings entries, and a ledger line saying why and how to restore. Before-and-after weight is measured by re-running the inventory, never asserted from prose.

Three modes: a full sweep, a read-only report, and a targeted removal of named items. A surface filter narrows the sweep to one lane. The script is an Instrument in the glossary's sense: it informs Kyle's judgment and never blocks or decides.

## User Stories

**Seeing the surface**

1. As Kyle, I want one inventory of every global steering surface (`CLAUDE.md` sections, the operating-constraints paragraphs, house skills, untracked skills, commands, agents, plugins, MCP servers, hooks, output styles, auto-memory dirs), so that I can see everything shaping my sessions in one place.
2. As Kyle, I want each item to show its always-loaded bytes, so that I know what each one costs on every request.
3. As Kyle, I want each item to show how many times I typed it and how many times a session chose it on its own, shown separately, so that I can tell a routing hijack from a skill I actually reach for.
4. As Kyle, I want each item's last-used date and its all-time count next to its 90-day count, so that a rare-but-load-bearing item is not mistaken for a dead one.
5. As Kyle, I want to see which steering files route to an item (its referrers), so that I know what breaks if it goes.
6. As Kyle, I want to see which other tracked docs merely mention an item, so that retiring it does not leave prose describing something that no longer exists.
7. As Kyle, I want to see when an item was added, so that a skill I built last week is never proposed for retirement for lack of use.
8. As Kyle, I want to see how many of my project repos carry a vendored copy of an item, so that I know the downstream blast radius before I retire it.
9. As Kyle, I want items that duplicate a plugin skill flagged, so that the same skill is not listed twice in every session.
10. As Kyle, I want items that route to something missing flagged, so that dangling routes left by past removals finally get patched.
11. As Kyle, I want a section of `CLAUDE.md` that has never been triggered to show zero hits against its trigger phrases, so that I can retire modes I never use.
12. As Kyle, I want `CLAUDE.md` sections with no known trigger phrases reported as unmeasured rather than as zero, so that a missing sidecar entry never reads as evidence of disuse.
13. As Kyle, I want a file that exists in the repo but is never loaded (an unlinked output style) flagged, so that dead weight in the repo is visible even when it costs sessions nothing.
14. As Kyle, I want MCP servers that only exist as claude.ai connectors to still get usage rows, so that the MCP surface is not limited to what a local config file lists.
15. As Kyle, I want every count that could not be measured to be reported as unmeasured and to fail the run loudly, so that a broken read never produces a false clean.

**Proposing**

16. As Kyle, I want each item to carry a temperature (`new`, `cold`, `cool`, `warm`, `hot`) with the rule for each stated once, so that I can read the evidence class at a glance.
17. As Kyle, I want a fixed precedence table to turn temperature and flags into a proposed verdict, so that proposals are consistent from sweep to sweep and testable.
18. As Kyle, I want `hot` and `warm` items kept silently with only a count shown, so that the table is not padded with things that are obviously earning their place.
19. As Kyle, I want items I already ruled "keep" with a clause omitted from future sweeps, so that I am never asked to re-litigate a recorded ruling.
20. As Kyle, I want paused items left alone until they have been paused for a full window, then asked "retire, or stay paused?", so that a pause is honored without becoming permanent by neglect.
21. As Kyle, I want mechanical classes (empty memory dirs, comment-only hook entries, the loose copies of one plugin) collapsed to one row each, so that trivia does not bury the judgment calls.
22. As Kyle, I want the ratification table grouped by surface with the `CLAUDE.md` sections last, so that the highest-judgment rows come when I have the rest settled.
23. As Kyle, I want every row to carry a title, not just an id, so that I can rule from the table without opening files.
24. As Kyle, I want `ask` rows to carry their specific question in the table, so that the table is the interview and I answer once.
25. As Kyle, I want to be able to say "ask me about row N" and get a fuller evidence card, so that depth is available without being forced on me.
26. As Kyle, I want the sweep to say plainly that usage evidence is local to this machine, so that I remember the counts are a floor.

**Ruling**

27. As Kyle, I want to answer by row number with a verdict and an optional clause, and "rest as proposed" for everything else, so that ruling on a hundred items takes one reply.
28. As Kyle, I want unanswered rows to stay unapplied, so that silence is never consent.
29. As Kyle, I want a `pause` verdict for commands, skills, and plugins, so that "not sure yet" has a spelling that is neither retire nor keep-forever.
30. As Kyle, I want a `keep` with a clause recorded in the ledger, so that my reason survives and the item is not re-proposed.
31. As Kyle, I want a `relocate` verdict handed to `/trim-context` by name with no edit made, so that content that should stay but load on demand goes through the tool built for that.
32. As Kyle, I want a `merge-into` verdict to record the intent as a backlog stub and make no removal, so that nothing is missing from the surface until the merge PR lands both halves.
33. As Kyle, I want to mark a kept `CLAUDE.md` rule as hook-convertible in the same reply, so that a backlog stub is written to convert it later.

**Applying**

34. As Kyle, I want ratified tracked items removed with `git rm`, their index row and playbook card deleted, and the doc-sync Gate run and passing, so that the reference docs never describe a file that is gone.
35. As Kyle, I want untracked items backed up to a dated backup folder and moved out, never deleted with `rm -rf`, so that every removal is reversible and the rm-rf hook never fires.
36. As Kyle, I want the ignore-file block for a retired untracked item removed along with any comment that now describes nothing, so that the ignore file stays honest.
37. As Kyle, I want every steering file that routes to a retired item edited by surgical excision with a refuse-if-unsure guard, so that a shared line never loses a neighbor by accident.
38. As Kyle, I want mentions in non-steering docs edited by the skill in the same PR and listed under their own PR heading, so that the README and third-party doc stop describing what is gone and I can review each edit in the diff.
39. As Kyle, I want edits to my untracked settings files to wait for one confirmation per file per pass that shows the exact edit list, so that I approve what changes without a stop per entry.
40. As Kyle, I want plugins and MCP servers changed through the CLI verbs that exist for them rather than by hand-editing JSON, so that the supported path is the one taken.
41. As Kyle, I want every settings file backed up with a dated suffix before it is edited, so that an untracked edit has an undo.
42. As Kyle, I want a retired plugin uninstalled and a paused plugin disabled, so that the retire/pause distinction means the same thing on every surface.
43. As Kyle, I want a paused command or skill to keep its index row and card, marked "paused" with the date and the restore instruction, so that the docs say what the ruling means.
44. As Kyle, I want a step that cannot complete cleanly to stop that item and report it rather than leave a partial removal, so that the surface is never half-edited.
45. As Kyle, I want each retired item's downstream vendored copies listed in the ledger and the PR body with no edits made, so that a later fleet prune knows what to hunt.
46. As Kyle, I want empty auto-memory directories removed without a per-item stop, so that mechanical cleanup does not cost me attention.

**Recording and measuring**

47. As Kyle, I want a ledger with one line per retirement (date, surface-qualified id, surface, why, evidence at the time, restore pointer, downstream copies), so that "why is X gone" and "how do I get it back" have one answer.
48. As Kyle, I want the ledger to use surface-qualified ids, so that a skill and a `CLAUDE.md` section with the same name never collide and a ledger row pastes straight into targeted mode.
49. As Kyle, I want a "kept on purpose" table in the same ledger, so that keep rulings live next to retirements.
50. As Kyle, I want the reference doc's intro to point at the ledger, so that a reader of the index knows where removed things went.
51. As Kyle, I want the inventory re-run after apply and every retired item asserted absent from every surface it was on, so that verification is a measurement, not a claim.
52. As Kyle, I want a before-and-after table of always-loaded bytes per surface in the PR body, so that the token-weight goal is measured, not described.
53. As Kyle, I want to paste `/context` output from fresh sessions before and after and have it included as the wire-level check, so that the script's byte counts are cross-checked against what the harness actually loads.

**Reports, modes, and safety**

54. As Kyle, I want `/retire --report` to produce the inventory and proposal table as a dated report and stop with no edits, so that I can audit without committing to a sweep.
55. As Kyle, I want the committed report redacted (counts and generic labels for memory dirs and hooks, repo names only for vendored copies, no private paths), so that a public repo never carries private project names.
56. As Kyle, I want the full-detail inventory kept in a local cache file the skill reads, so that redaction costs the sweep nothing.
57. As Kyle, I want `--report` to follow the standing git workflow (branch from `main`, commit, push, docs-only PR; or commit on the current feature branch), so that even a read-only run leaves a durable record.
58. As Kyle, I want `/retire --surface <name>` to run the sweep on one surface, so that "audit my CLAUDE.md" is a one-liner.
59. As Kyle, I want `/retire <item>…` to skip the sweep, show each named item's evidence card, confirm, and apply with the same full bookkeeping, so that future one-off removals are cheap and complete.
60. As Kyle, I want ambiguous item names in targeted mode to stop and ask, so that the wrong thing is never removed on a name collision.
61. As Kyle, I want every change to land on a branch with a PR and never on `main`, so that the PR is the durable record and the review gate can run.
62. As Kyle, I want the skill to propose a review scope before any merge and stop for my call in an interactive session, with a single round as the floor when unattended, so that behavioral diffs get the review the global gate requires.
63. As Kyle, I want an unattended run to write the table to the report and stop, so that retire never applies an unratified row.
64. As Kyle, I want re-runs to be cheap by caching per-transcript results keyed by size and modification time, so that a 3 GB corpus is read once.
65. As Kyle, I want the inventory script to be stdlib-only, read-only, and deterministic, so that it runs anywhere and can be trusted as an Instrument.
66. As a future reader, I want the ledger's restore pointer to be a command I can run, so that undoing a retirement needs no archaeology.
67. As a reviewer, I want the PR body to carry the script's before-and-after table and the list of relocate and doc-mention edits, so that I review measurements and named edits rather than a narrative.
68. As a builder, I want the precedence table and temperature rules to be named constants in one place, so that a threshold change is one edit.

## Implementation Decisions

**Vocabulary.** The spec uses the repo glossary: steering surface, retire, pause, relocate, temperature, verdict, ledger, Instrument, Gate. The inventory script is an Instrument and never a Gate; per ADR 0001 nothing here gains a merge veto. The existing doc-sync check remains the only Gate involved and is reused unchanged.

**Modules.**
- An inventory script inside the skill's scripts directory: stdlib-only Python, read-only, deterministic. It enumerates every surface, attaches evidence, assigns temperature and flags, computes the proposed verdict from the precedence table, and renders JSON (full) and markdown (redacted).
- A trigger-phrase sidecar keyed by exact `CLAUDE.md` headings, shipped next to the script. A heading with no entry is reported as unmeasured.
- A unit-test suite next to the script, built on a tiny generated fixture tree.
- The skill's procedure document and a per-surface bookkeeping reference.
- A ledger document in the repo's docs tree, with a retirements table and a kept-on-purpose table; the reference doc's intro gains one sentence pointing at it.
- A dated, redacted report in the repo's reports directory per `--report` run.
- The skill's own index row and playbook card, landing in the same commit as the skill.

**Surfaces and their units.** `CLAUDE.md` sections (one per `##`/`###` heading outside fenced blocks); operating-constraints paragraphs (one per bold-led paragraph, since the file has no headings); tracked skills (directory); untracked skills (directory, gitignored); commands including `.disabled` files; agents; plugins (the plugin, not its skills); MCP servers (union of the user-scope config and server names observed in transcripts, so claude.ai connectors appear); hook entries; output styles; auto-memory directories; the fleet's vendored copies (report only).

**Item ids.** Surface-qualified: `skill:<name>`, `command:<name>`, `agent:<name>`, `plugin:<key>`, `mcp:<server>`, `claude-md:<heading>`, `hook:<event>[group][index]`, `output-style:<name>`, `memory:<slug>`. Targeted mode resolves bare names across surfaces and stops on ambiguity.

**Evidence fields per item.** Always-loaded bytes (description length for skills, commands, plugin skills; section length for `CLAUDE.md`; zero for paused items); typed count and session-chosen count, each for the window and all-time; last-used date; trigger hits for the window and all-time, or unmeasured; referrers; mentions; routes-to-missing; vendored-copy repo names; duplicate-of; last-edited; added date; number of projects it was used in (a count, never names).

**Usage sources.** Typed invocations come from the prompt history (a `display` beginning with the slash form). Session-chosen invocations come from transcripts: Skill tool calls, Agent tool dispatches, and MCP tool names. Plugin skills match both bare and namespaced spellings. Transcripts are streamed line by line with a substring pre-filter before JSON parsing, and per-file results are cached keyed by path, size, and mtime.

**Referrers versus mentions.** Referrers are steering files: skills, commands, agents, `CLAUDE.md`, the constraints file, and prompt-type hooks in settings. Mentions are every other tracked markdown file. The index doc, the playbook, and the ledger are excluded from both, since each has its own bookkeeping step. Only referrers feed temperature. Matching is word-boundary on the item's name, excluding the item's own files; plugins match on their short name.

**Added date per surface.** Tracked files: the first commit that added them. `CLAUDE.md` sections: the first commit containing the heading. Untracked directories: mtime. Plugins: the install record's `installedAt`. MCP servers, hooks, and memory dirs: none, so never `new`.

**Temperature.** Constants in one place. Window defaults to 90 days. `new`: added inside the window. `hot`: 5 or more uses in the window. `warm`: 1 to 4. `cool`: 0 in the window but used or referenced ever. `cold`: 0 in the window, 0 referrers, nothing all-time. Uses = typed + session-chosen + trigger hits.

**Flags.** `duplicate` (a loose copy of a skill an enabled plugin ships), `dangling` (routes to a missing name, including paused commands and ledger-retired items), `oversized` (top decile of bytes within its surface, only when the surface has 10 or more sized items), `paused`, `disabled_comment` (hook whose command is comment-only), `empty` (memory dir), `unlinked` (a repo file the harness never loads), `kept` (present in the ledger's kept table), `auto_only` (skills and commands only: 0 typed and 5 or more session-chosen in the window; informational, changes no proposal).

**Precedence table, top wins** (computed by the script as `proposed`; the skill renders, Kyle rules):

| Signal | Row shown | Proposed |
|---|---|---|
| `kept` | omitted, counted and named | — |
| `duplicate` non-canonical copy | yes, collapsed per canonical plugin | `retire` |
| `disabled_comment` hook, `empty` memory dir | yes, collapsed per class | `retire` |
| `paused` less than a window | omitted, counted and named | — |
| `paused` a window or more, `unlinked` | yes | `ask` |
| `new` with another flag | yes | `ask` |
| `new` alone | omitted, counted and named | — |
| `hot` or `warm` and `oversized` | yes | `relocate` |
| `hot` or `warm` | omitted, counted | — |
| `cool` | yes | `ask` |
| `cold` | yes | `retire` |

`dangling` is never a verdict on the item; it is an apply step on the referrer.

**Verdicts.** `retire`, `keep` (optional clause), `pause`, `merge-into <id>`, `relocate`, `ask`. Reply grammar: `<row> <verdict>[ — clause]`, comma-separated; `rest as proposed`; `keep (hook)` marks hook-convertible and writes a backlog stub; "ask me about row N" returns a fuller card. Unanswered rows are not applied.

**Ratification table.** One table, every row titled, grouped by surface with `CLAUDE.md` last, `retire` rows first within a group, then `ask`, then `relocate`. Omitted classes are summarized by count and name after the table. The table header carries the local-corpus caveat.

**Pause mechanics.** Commands and skills: rename the file to `.disabled` (a skill directory without its skill file is not listed; verified in the pilot before the first skill pause). Plugins: the CLI disable verb. No pause for `CLAUDE.md` sections, MCP servers, or hooks. No ledger line. Index row and card stay, prefixed "(paused <date>)" with a bold "Paused" note and the restore instruction. Pause date is the last commit touching the paused file, or mtime when untracked.

**Apply order per retired item.** Backup (untracked only) → remove (`git rm` for tracked; move to the dated backup folder for untracked; never `rm -rf`) → index row and playbook card, then the doc-sync Gate must pass → ignore-file block (untracked only) → referrers by surgical excision with a refuse-if-unsure guard, rewriting routes to a merge target if one was ruled → mentions edited with judgment and listed under their own PR heading → ledger line → downstream copies appended to the ledger line and PR body → re-inventory asserting absence. A step that cannot complete cleanly stops that item and reports.

**Untracked settings edits.** One confirmation per file per pass showing the exact edit list, after the row is ratified. Back the file up with a dated suffix first. Use `claude plugin uninstall` / `claude plugin disable` and `claude mcp remove` where they apply; edit JSON only for hook entries and the claude.ai deny list. A retired MCP server's restore pointer is the backup file, never the config block (it may hold secrets).

**merge-into.** Writes a backlog stub naming source and target; makes no removal; the merge PR removes the item and writes the ledger line "merged into <id>".

**Relocate.** Listed in the PR body under a "hand to /trim-context" heading; no edit.

**Ledger schema.** Retirements: date, surface-qualified id, surface, why, evidence at retirement, restore pointer (a runnable command or a backup path), downstream copies (repo names only). Kept on purpose: date, id, keep-because. The script reads the kept table back to set the `kept` flag and reads the retirements table to feed the dangling-route check.

**Report redaction.** The markdown renderer is always redacted: memory dirs and hook entries as counts with generic labels, vendored copies as repo names, no absolute paths, no hook command text, no MCP config detail. The JSON renderer is full and is written only under the local cache directory.

**Modes.** Sweep; `--report` (inventory plus proposal table, committed under the standing git workflow, then stop); `--surface <name>` (filter, valid on sweep and report); targeted `<item>…` (evidence card, confirm, apply). Unattended: write the table, stop.

**Measurement.** Before and after apply, the script prints always-loaded bytes per surface; the PR body carries that table. Pasted `/context` output is included as the wire-level check when Kyle supplies it.

**Script contract.** Flags for window days, JSON output path, markdown output path, claude home, config repo, projects root, claude config file, triggers file, cache toggle, surface filter. Exit 0 complete; 2 a source missing or unreadable; 3 a surface enumerated to zero where files exist. A zero is only reported when the source was read.

**Convention changes.** Retire means delete plus ledger; `.disabled` means paused; pause rows say "Paused", and the two existing "Disabled" rows are reworded whichever way the pilot rules on them. The skill's description stays short and honest from the first commit, because the skills directory is live through the symlink on whatever branch is checked out.

**Review gate.** Diffs under skills, commands, agents, `CLAUDE.md`, hooks, or settings are behavioral: propose at least a single round; Kyle rules interactively; single round is the unattended floor.

## Testing Decisions

**What makes a good test here.** A test drives the inventory script through its command line over a throwaway fixture tree and asserts on what comes out: the JSON records, the redacted markdown, and the exit code. It never imports internals to poke at intermediate state, and it never depends on the live machine. Fixtures are small and built per test so the assertion reads next to the tree that produced it. The live numbers from the design's evidence snapshot are sanity checks in the pilot, not test expectations.

**Seam A (new, automated): the script's command line over a fixture home.** Everything deterministic is observable here and every rule gets a test: surface enumeration including the operating-constraints paragraphs and the union-derived MCP list; typed versus session-chosen counts and last-used; trigger hits and the unmeasured dash; referrers versus mentions with the index, playbook, and ledger excluded; each flag (`duplicate`, `dangling`, `oversized`, `paused`, `disabled_comment`, `empty`, `unlinked`, `kept`, `auto_only`); added-date per surface and the `new` temperature; the temperature thresholds; the precedence table row by row; the collapsed rows; report redaction (no absolute paths, no hook text, memory dirs as a count); cache hits on a second run; the surface filter; the two non-zero exits and the rule that a zero is only reported when the source was read.

**Seam B (existing, reused): the doc-sync check.** It verifies the index row and playbook card bookkeeping and already runs at push. Every apply step runs it; no new tests.

**Seam C (manual acceptance): the live `--report` run and the pilot sweep.** The skill procedure is prose executed by the model. Its acceptance is the re-inventory (every retired item absent from every surface it was on), the doc-sync Gate green, the before-and-after byte table in the PR, and Kyle's `/context` paste as the wire-level check.

**Prior art.** The stdlib `unittest` suites under the architecture-viewer, paper-gloss, and paper-figures skills: each test builds a resolved temporary tree, drives the script, and asserts on outputs; run with `python3 -m unittest discover` from the scripts directory, no pytest.

## Out of Scope

- Editing any project repo: per-project `CLAUDE.md`, vendored `.claude/` copies, project-scoped MCP entries. The fleet is report-only (v2 lane).
- Re-litigating the harness disable ruling (keep all eight) or the already-applied connector prune.
- The basic-memory note store.
- Relocating content that stays: that is `/trim-context`'s job; `retire` hands it over by name.
- Any daemon, hook, or scheduled run; a periodic `--report` cadence is a v2 stub.
- A restore verb; restore is the documented manual procedure in the ledger header.
- Performing the merge edits for `merge-into` verdicts, or converting hook-convertible rules to hooks; both are recorded as backlog stubs.
- Co-occurrence and correction-detection evidence.
- Building a `/context` proxy; pasted output is accepted, not produced.
- Usage from sessions on other machines or cloud sessions; the corpus is local by design, with a caveat.

## Further Notes

- **Pilot first targets** (proposals, the table decides): the 36 loose mattpocock copies and their ignore block (verify bare `/tdd` still resolves to the plugin first); Improvement Mode and New Feature Mode (0 hits ever; the Stop-hook prompt sentence is a referrer to patch); Kickoff Mode (2 hits; likely relocate or shrink); the two `.disabled` commands (retire to ledger or stay paused; the five dangling routes get patched either way); four comment-only hook entries; 32 empty memory dirs; the failing MCP_DOCKER server; the three coexisting browser automators; every `cold` item the sweep finds. The unlinked output style is a new candidate from the grill.
- **Landmines.** The rm-rf hook and the safety-net plugin (no `xargs sh -c`, no `git checkout --`, no `git reset --hard`); zsh mangling of `$ref:path`; false cleans from a failing grep or API; single-line command lists in downstream repos (report-only for that reason); the live symlink; the public repo (repo names only in the ledger and report).
- **Two pull requests.** PR A: script, tests, sidecar, ledger, skill, bookkeeping reference, index row, playbook card, first redacted report. PR B: the pilot sweep's retirements, measured. The tooling review and the cleanse review stay separate on purpose.
- **Ancestry.** Builds the coliseum-commands-earn-their-keep idea (without its Stop-hook tracer; transcripts already carry the signal) and absorbs the minimal-initial-prompt idea as the `CLAUDE.md` lane. Three v2 stubs go to the backlog: fleet prune lane, per-project `CLAUDE.md` lane, periodic report cadence.

**Run-config note.** Tickets for the script and its tests are mechanical once specified: a Sonnet 5 implementer at `medium` per ticket, fresh from the ticket, is the right shape. The skill text, the first live run, and the pilot ratification are judgment work and stay in the Fable 5.1 session that holds the design. If a fresh planning session is ever needed: `claude --model claude-fable-5-1 --effort xhigh`.
