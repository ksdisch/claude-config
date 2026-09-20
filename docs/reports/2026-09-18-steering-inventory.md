# Steering inventory — 2026-09-18

Window: last 90 days (since 2026-06-20). History rows: 5,449. Transcripts scanned: 6138 (6119 from cache). Surfaces: skill, command, agent, output-style, plugin, mcp, hook, memory, claude-md.

Usage evidence is this machine's local corpus only — every count is a floor, never a ceiling.

Read-only; an Instrument, never a Gate. An em dash is unmeasured, never zero.

## Totals

| Surface | Items | Always-loaded chars |
|---|---|---|
| skill | 78 | 36,538 |
| command | 21 | 5,858 |
| agent | 7 | 4,106 |
| output-style | 1 | 236 |
| plugin | 19 | 11,065 |
| mcp | 33 | 0 |
| hook | 11 | 0 |
| memory | 33 | 520 |
| claude-md | 19 | 23,877 |
| ALL | 222 | 82,200 |

## Proposals

47 rows need a ruling. Grouped by surface with `claude-md` last; `retire` first inside a surface, then `ask`, then `relocate`. Everything else is omitted and summarised below.

| # | Surface | Item | Proposed | Evidence | Flags | Temp |
|---|---|---|---|---|---|---|
| 1 | skill | 36 loose skill copies of plugin mattpocock-skills | retire | 36 items · 5,303 chars · `ask-matt`, `claude-handoff`, `code-review` +33 more | collapsed | — |
| 2 | skill | `adversarial-review` | ask | typed 0/90d · 0 all · auto 159/159 · trig 44/46 · last 2026-09-18 · added 2026-07-26 · edited 2026-08-27 · refs 11 · mentions 14 · 1,528 chars | auto_only, oversized | new |
| 3 | skill | `paper-gloss` | ask | typed 4/90d · 4 all · auto 3/3 · trig 0/0 · last 2026-08-24 · added 2026-07-23 · edited 2026-07-29 · refs 3 · mentions 6 · 1,426 chars · vendored in blind-cite | oversized | new |
| 4 | skill | `paper-eli5` | ask | typed 1/90d · 1 all · auto 3/3 · trig 0/0 · last 2026-08-04 · added 2026-07-19 · edited 2026-07-28 · refs 5 · mentions 3 · 1,351 chars | oversized | new |
| 5 | skill | `architecture-viewer` | ask | typed 0/90d · 0 all · auto 1/1 · trig 1/1 · last 2026-08-23 · added 2026-08-20 · edited 2026-08-20 · refs 0 · mentions 5 · 1,195 chars | oversized | new |
| 6 | skill | `bug-hunt` | ask | typed 0/90d · 0 all · auto 7/7 · trig 0/0 · last 2026-08-13 · added 2026-06-26 · edited 2026-07-27 · refs 8 · mentions 6 · 1,192 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | auto_only, oversized | new |
| 7 | skill | `curriculum-sync` | ask | typed 0/90d · 0 all · auto 0/0 · trig 0/0 · last — · added 2026-08-07 · edited 2026-08-07 · refs 0 · mentions 1 · 1,134 chars | oversized | new |
| 8 | skill | `career-coach` | ask | typed 0/90d · 0 all · auto 2/2 · trig 1/1 · last 2026-08-20 · added 2026-07-23 · edited 2026-07-23 · refs 0 · mentions 0 · 1,133 chars | oversized | new |
| 9 | skill | `reweave` | ask | typed 4/90d · 4 all · auto 2/2 · trig 3/3 · last 2026-09-14 · added 2026-07-21 · edited 2026-07-21 · refs 0 · mentions 2 · 1,069 chars | oversized | new |
| 10 | skill | `artifacts-generate` | ask | typed 0/90d · 0 all · auto 0/3 · trig 0/0 · last 2026-06-03 · added 2026-06-08 · edited 2026-06-08 · refs 0 · mentions 0 · 738 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool |
| 11 | skill | `backlog-hygiene` | ask | typed 1/90d · 1 all · auto 19/19 · trig 17/18 · last 2026-09-09 · added 2026-07-19 · edited 2026-08-21 · refs 7 · mentions 2 · 697 chars · routes→ autonomous-milestone | dangling | new |
| 12 | skill | `reorient` | ask | typed 1/90d · 1 all · auto 1/1 · trig 1/1 · last 2026-08-03 · added 2026-07-19 · edited 2026-07-19 · refs 2 · mentions 2 · 625 chars · routes→ autonomous-milestone | dangling | new |
| 13 | skill | `nlm-skill` | ask | typed 0/90d · 0 all · auto 0/1 · trig 0/0 · last 2026-05-28 · added 2026-06-08 · edited 2026-06-08 · refs 8 · mentions 3 · 611 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool |
| 14 | skill | `artifacts-audit` | ask | typed 0/90d · 1 all · auto 0/0 · trig —/— · last 2026-05-31 · added 2026-06-08 · edited 2026-06-08 · refs 1 · mentions 0 · 593 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool |
| 15 | skill | `portfolio-notebook-sync` | ask | typed 0/90d · 0 all · auto 5/5 · trig 0/0 · last 2026-08-06 · added 2026-08-02 · edited 2026-08-03 · refs 3 · mentions 1 · 582 chars · routes→ learn | auto_only, dangling | new |
| 16 | skill | `match-the-mock` | ask | typed 0/90d · 0 all · auto 0/0 · trig 0/0 · last — · added 2026-06-08 · edited 2026-06-08 · refs 1 · mentions 0 · 396 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool |
| 17 | skill | `notebook-assist` | ask | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-06-08 · edited 2026-07-13 · refs 4 · mentions 3 · 366 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool |
| 18 | skill | `mini` | ask | typed 0/90d · 2 all · auto 0/0 · trig —/— · last 2026-05-20 · added 2026-06-08 · edited 2026-06-08 · refs 5 · mentions 1 · 352 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool |
| 19 | command | `launch` | ask | typed 7/90d · 7 all · auto 48/48 · trig 0/0 · last 2026-09-17 · added 2026-08-10 · edited 2026-08-21 · refs 27 · mentions 8 · 638 chars | oversized | new |
| 20 | command | `reframe-orchestrator` | ask | typed 0/90d · 4 all · auto 0/0 · trig —/— · last 2026-06-05 · added 2026-06-08 · edited 2026-06-23 · refs 0 · mentions 1 · 260 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool |
| 21 | command | `screenshot-iterate` | ask | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-06-08 · edited 2026-06-23 · refs 2 · mentions 0 · 199 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool |
| 22 | command | `brainstorm` | relocate | typed 0/90d · 1 all · auto 5/5 · trig —/— · last 2026-09-16 · added 2026-06-08 · edited 2026-07-27 · refs 10 · mentions 15 · 551 chars · vendored in DogHood, blind-cite, buoy-legal +14 more · routes→ autonomous-milestone | auto_only, dangling, oversized | hot |
| 23 | output-style | `adhd` | ask | typed —/90d · — all · auto —/— · trig —/— · last — · added 2026-08-13 · edited 2026-08-13 · refs 2 · mentions 2 · 236 chars | unlinked | new |
| 24 | plugin | `swift-lsp@claude-plugins-official` | retire | typed —/90d · — all · auto 0/0 · trig —/— · last — · added 2026-05-15 · edited — · refs 0 · mentions 1 · 0 chars | — | cold |
| 25 | plugin | `mattpocock-skills@mattpocock` | ask | typed —/90d · — all · auto 216/254 · trig —/— · last 2026-09-18 · added 2026-08-21 · edited — · refs 0 · mentions 1 · 5,303 chars | oversized | new |
| 26 | plugin | `focus-coach@ksdisch` | ask | typed —/90d · — all · auto 0/2 · trig —/— · last 2026-06-08 · added 2026-06-08 · edited — · refs 0 · mentions 0 · 371 chars | — | cool |
| 27 | plugin | `claude-code-setup@claude-plugins-official` | ask | typed —/90d · — all · auto 0/6 · trig —/— · last 2026-06-06 · added 2026-05-11 · edited — · refs 0 · mentions 0 · 354 chars | — | cool |
| 28 | plugin | `safety-net@cc-marketplace` | ask | typed —/90d · — all · auto 0/0 · trig —/— · last — · added 2026-05-17 · edited — · refs 1 · mentions 2 · 71 chars | — | cool |
| 29 | plugin | `code-review@claude-plugins-official` | ask | typed —/90d · — all · auto 0/0 · trig —/— · last — · added 2026-05-11 · edited — · refs 7 · mentions 2 · 0 chars | — | cool |
| 30 | mcp | `mcp #10` | ask | typed —/90d · — all · auto 0/4 · trig —/— · last 2026-04-29 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | cool |
| 31 | mcp | `mcp #11` | ask | typed —/90d · — all · auto 0/11 · trig —/— · last 2026-06-05 · added — · edited — · refs 0 · mentions 2 · 0 chars | — | cool |
| 32 | mcp | `mcp #13` | ask | typed —/90d · — all · auto 0/11 · trig —/— · last 2026-05-27 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | cool |
| 33 | mcp | `mcp #19` | ask | typed —/90d · — all · auto 0/1 · trig —/— · last 2026-06-05 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only, denied | cool |
| 34 | mcp | `mcp #1` | ask | typed —/90d · — all · auto 0/150 · trig —/— · last 2026-06-04 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | cool |
| 35 | mcp | `mcp #23` | ask | typed —/90d · — all · auto 0/24 · trig —/— · last 2026-06-02 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | cool |
| 36 | mcp | `mcp #32` | ask | typed —/90d · — all · auto 0/12 · trig —/— · last 2026-06-05 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | cool |
| 37 | mcp | `mcp #3` | ask | typed —/90d · — all · auto 0/660 · trig —/— · last 2026-05-02 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | cool |
| 38 | mcp | `mcp #4` | ask | typed —/90d · — all · auto 0/4 · trig —/— · last 2026-05-27 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | cool |
| 39 | mcp | `mcp #5` | ask | typed —/90d · — all · auto 0/34 · trig —/— · last 2026-06-05 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | cool |
| 40 | mcp | `mcp #7` | ask | typed —/90d · — all · auto 0/3 · trig —/— · last 2026-05-17 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | cool |
| 41 | mcp | `mcp #8` | ask | typed —/90d · — all · auto 0/16 · trig —/— · last 2026-06-02 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | cool |
| 42 | mcp | `mcp #9` | ask | typed —/90d · — all · auto 0/1 · trig —/— · last 2026-06-01 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | cool |
| 43 | hook | 4 hook entries commented out | retire | 4 items · 0 chars · `Notification[0][0]`, `Notification[0][1]`, `Stop[1][0]` +1 more | collapsed | — |
| 44 | memory | 32 empty auto-memory directories | retire | 32 items · 0 chars | collapsed | — |
| 45 | claude-md | `Local-Markdown Issue Tracker: Tickets Index (added 2026-08-22)` | ask | typed —/90d · — all · auto —/— · trig 29/29 · last 2026-09-18 · added 2026-08-22 · edited — · refs 0 · mentions 0 · 4,086 chars | oversized | new |
| 46 | claude-md | `New Feature Mode` | ask | typed —/90d · — all · auto —/— · trig 0/0 · last — · added 2026-06-08 · edited — · refs 2 · mentions 1 · 767 chars | — | cool |
| 47 | claude-md | `Improvement Mode` | ask | typed —/90d · — all · auto —/— · trig 0/0 · last — · added 2026-06-08 · edited — · refs 1 · mentions 1 · 717 chars | — | cool |

## Omitted from the proposals

Each line is one row of the precedence table doing its job. Names are listed except for the silent keeps, which are counted, and for surfaces whose names are private.

- **kept** — ruled keep on purpose, recorded in the ledger — 0
- **paused-recent** — paused less than a window ago — 2: `autonomous-milestone`, `learn`
- **new** — added inside the window, nothing else against it — 51: `Format rules`, `Never show me a bare identifier (added 2026-08-13)`, `Planner/Builder Protocol (added 2026-07-27)`, `Project Wiki`, `Reference Doc Maintenance`, `When to update`, `adhd`, `adversarial-reviewer`, `catchup`, `cc-yt-idea-mine`, `claude-md-management@claude-plugins-official`, `code-simplifier@claude-plugins-official`, `context7@claude-plugins-official`, `crap-check`, `feature-dev@claude-plugins-official`, `find-skills`, `frontend-design@claude-plugins-official`, `gauntlet`, `gauntlet-coder`, `github@claude-plugins-official`, `handoff-session`, `interview-prep`, `mock-call`, `mutation-hardener`, `narrate`, `notebook-merge`, `onboard`, `orchestrate`, `paper-figures`, `playwright@claude-plugins-official`, `project-guide`, `project-wiki`, `ralph-loop@claude-plugins-official`, `replenish`, `research-paper`, `retire`, `review-judge`, `seed-hunt`, `silent-failure-hunter`, `skill-creator@claude-plugins-official`, `spec-miner`, `specifier`, `superpowers@claude-plugins-official`, `tdd-loop`, `teach-research`, `video-series`, `warp@claude-code-warp`, `wiki-backfill`, `wiki-init`, `youtube-breakdown`, `youtube-transcript`
- **hot-warm** — used inside the window — 36
- **unmeasured** — no source could score it; nothing here is evidence of disuse — 17: `Act vs. assess`, `Clarifying questions and option formatting`, `Decisiveness`, `Finish the turn`, `Git Workflow`, `No false progress`, `PreToolUse[0][0]`, `PreToolUse[0][1]`, `PreToolUse[1][0]`, `Scope discipline`, `SessionEnd[0][0]`, `Stop[0][0]`, `Track multi-step work`, `Unattended runs only`, `UserPromptSubmit[0][0]`, `UserPromptSubmit[1][0]` (+1 on a surface whose names are private)
- **auto_only** — never typed, but sessions keep choosing it (evidence, not a verdict) — 18: `adversarial-review`, `audio-series`, `autonomous-milestone`, `brainstorm`, `bug-hunt`, `code-review`, `codebase-design`, `domain-modeling`, `explore-plan`, `grilling`, `handoff-session`, `kickoff`, `narrate`, `notebook-init`, `portfolio-notebook-sync`, `project-wiki`, `tdd`, `youtube-transcript`

## Full inventory

Every item the run read, proposals and omissions alike, with the evidence behind its row.

## skill

| Item | Evidence | Flags | Temp | Proposed |
|---|---|---|---|---|
| `artifacts-generate` | typed 0/90d · 0 all · auto 0/3 · trig 0/0 · last 2026-06-03 · added 2026-06-08 · edited 2026-06-08 · refs 0 · mentions 0 · 738 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool | ask |
| `nlm-skill` | typed 0/90d · 0 all · auto 0/1 · trig 0/0 · last 2026-05-28 · added 2026-06-08 · edited 2026-06-08 · refs 8 · mentions 3 · 611 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool | ask |
| `artifacts-audit` | typed 0/90d · 1 all · auto 0/0 · trig —/— · last 2026-05-31 · added 2026-06-08 · edited 2026-06-08 · refs 1 · mentions 0 · 593 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool | ask |
| `match-the-mock` | typed 0/90d · 0 all · auto 0/0 · trig 0/0 · last — · added 2026-06-08 · edited 2026-06-08 · refs 1 · mentions 0 · 396 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool | ask |
| `notebook-assist` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-06-08 · edited 2026-07-13 · refs 4 · mentions 3 · 366 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool | ask |
| `mini` | typed 0/90d · 2 all · auto 0/0 · trig —/— · last 2026-05-20 · added 2026-06-08 · edited 2026-06-08 · refs 5 · mentions 1 · 352 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool | ask |
| `adversarial-review` | typed 0/90d · 0 all · auto 159/159 · trig 44/46 · last 2026-09-18 · added 2026-07-26 · edited 2026-08-27 · refs 11 · mentions 14 · 1,528 chars | auto_only, oversized | new | ask |
| `paper-gloss` | typed 4/90d · 4 all · auto 3/3 · trig 0/0 · last 2026-08-24 · added 2026-07-23 · edited 2026-07-29 · refs 3 · mentions 6 · 1,426 chars · vendored in blind-cite | oversized | new | ask |
| `paper-eli5` | typed 1/90d · 1 all · auto 3/3 · trig 0/0 · last 2026-08-04 · added 2026-07-19 · edited 2026-07-28 · refs 5 · mentions 3 · 1,351 chars | oversized | new | ask |
| `architecture-viewer` | typed 0/90d · 0 all · auto 1/1 · trig 1/1 · last 2026-08-23 · added 2026-08-20 · edited 2026-08-20 · refs 0 · mentions 5 · 1,195 chars | oversized | new | ask |
| `bug-hunt` | typed 0/90d · 0 all · auto 7/7 · trig 0/0 · last 2026-08-13 · added 2026-06-26 · edited 2026-07-27 · refs 8 · mentions 6 · 1,192 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | auto_only, oversized | new | ask |
| `curriculum-sync` | typed 0/90d · 0 all · auto 0/0 · trig 0/0 · last — · added 2026-08-07 · edited 2026-08-07 · refs 0 · mentions 1 · 1,134 chars | oversized | new | ask |
| `career-coach` | typed 0/90d · 0 all · auto 2/2 · trig 1/1 · last 2026-08-20 · added 2026-07-23 · edited 2026-07-23 · refs 0 · mentions 0 · 1,133 chars | oversized | new | ask |
| `reweave` | typed 4/90d · 4 all · auto 2/2 · trig 3/3 · last 2026-09-14 · added 2026-07-21 · edited 2026-07-21 · refs 0 · mentions 2 · 1,069 chars | oversized | new | ask |
| `research-paper` | typed 1/90d · 1 all · auto 4/4 · trig 0/0 · last 2026-08-05 · added 2026-07-17 · edited 2026-08-03 · refs 2 · mentions 1 · 919 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | new | — |
| `youtube-breakdown` | typed 0/90d · 1 all · auto 0/0 · trig 0/1 · last 2026-06-09 · added 2026-08-20 · edited 2026-08-20 · refs 2 · mentions 1 · 840 chars · vendored in home-base | — | new | — |
| `paper-figures` | typed 0/90d · 0 all · auto 0/0 · trig 0/0 · last — · added 2026-07-27 · edited 2026-07-29 · refs 3 · mentions 3 · 812 chars | — | new | — |
| `gauntlet` | typed 0/90d · 0 all · auto 1/1 · trig 0/0 · last 2026-08-21 · added 2026-08-20 · edited 2026-08-20 · refs 4 · mentions 11 · 789 chars | — | new | — |
| `orchestrate` | typed 0/90d · 0 all · auto 3/3 · trig 0/0 · last 2026-09-17 · added 2026-09-07 · edited 2026-09-08 · refs 4 · mentions 2 · 785 chars | — | new | — |
| `onboard` | typed 0/90d · 0 all · auto 3/3 · trig 0/1 · last 2026-09-18 · added 2026-08-03 · edited 2026-08-22 · refs 2 · mentions 2 · 784 chars | — | new | — |
| `cc-yt-idea-mine` | typed 1/90d · 1 all · auto 4/4 · trig 0/0 · last 2026-08-22 · added 2026-08-20 · edited 2026-08-21 · refs 2 · mentions 36 · 776 chars | — | new | — |
| `project-guide` | typed 3/90d · 3 all · auto 1/1 · trig 5/5 · last 2026-07-06 · added 2026-06-28 · edited 2026-07-06 · refs 5 · mentions 6 · 737 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | new | — |
| `seed-hunt` | typed 1/90d · 1 all · auto 3/3 · trig 1/1 · last 2026-08-21 · added 2026-07-06 · edited 2026-08-21 · refs 2 · mentions 1 · 704 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | new | — |
| `backlog-hygiene` | typed 1/90d · 1 all · auto 19/19 · trig 17/18 · last 2026-09-09 · added 2026-07-19 · edited 2026-08-21 · refs 7 · mentions 2 · 697 chars · routes→ autonomous-milestone | dangling | new | ask |
| `notebook-merge` | typed 3/90d · 3 all · auto 0/0 · trig 3/3 · last 2026-07-14 · added 2026-07-13 · edited 2026-07-13 · refs 1 · mentions 1 · 692 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | new | — |
| `video-series` | typed 1/90d · 1 all · auto 0/0 · trig 71/80 · last 2026-09-17 · added 2026-07-11 · edited 2026-07-13 · refs 3 · mentions 3 · 687 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | new | — |
| `adhd` | typed 0/90d · 0 all · auto 0/0 · trig 16/40 · last 2026-09-12 · added 2026-08-01 · edited 2026-08-01 · refs 1 · mentions 3 · 668 chars | — | new | — |
| `replenish` | typed 1/90d · 1 all · auto 0/0 · trig 10/10 · last 2026-09-12 · added 2026-07-19 · edited 2026-07-19 · refs 2 · mentions 2 · 657 chars | — | new | — |
| `mock-call` | typed 0/90d · 0 all · auto 0/0 · trig 1/1 · last 2026-09-17 · added 2026-09-17 · edited 2026-09-17 · refs 0 · mentions 1 · 651 chars | — | new | — |
| `reorient` | typed 1/90d · 1 all · auto 1/1 · trig 1/1 · last 2026-08-03 · added 2026-07-19 · edited 2026-07-19 · refs 2 · mentions 2 · 625 chars · routes→ autonomous-milestone | dangling | new | ask |
| `teach-research` | typed 1/90d · 1 all · auto 0/0 · trig —/— · last 2026-08-17 · added 2026-08-17 · edited 2026-08-17 · refs 2 · mentions 1 · 620 chars | — | new | — |
| `retire` | typed 0/90d · 0 all · auto 0/0 · trig 0/0 · last — · added 2026-09-18 · edited 2026-09-18 · refs 2 · mentions 5 · 599 chars | — | new | — |
| `portfolio-notebook-sync` | typed 0/90d · 0 all · auto 5/5 · trig 0/0 · last 2026-08-06 · added 2026-08-02 · edited 2026-08-03 · refs 3 · mentions 1 · 582 chars · routes→ learn | auto_only, dangling | new | ask |
| `narrate` | typed 0/90d · 0 all · auto 16/16 · trig 2/6 · last 2026-09-18 · added 2026-06-28 · edited 2026-08-21 · refs 9 · mentions 2 · 555 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | auto_only | new | — |
| `youtube-transcript` | typed 0/90d · 0 all · auto 5/5 · trig 2/3 · last 2026-08-22 · added 2026-08-20 · edited 2026-08-20 · refs 2 · mentions 1 · 514 chars | auto_only | new | — |
| `interview-prep` | typed 0/90d · 6 all · auto 3/3 · trig 0/0 · last 2026-08-30 · added 2026-07-28 · edited 2026-07-28 · refs 6 · mentions 4 · 435 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | new | — |
| `code-review` | typed 0/90d · 0 all · auto 32/44 · trig 0/0 · last 2026-09-17 · added 2026-08-21 · edited 2026-08-21 · refs 6 · mentions 2 · 419 chars · dup of `mattpocock-skills:code-review` | duplicate, auto_only | new | retire |
| `project-wiki` | typed 0/90d · 0 all · auto 60/60 · trig —/— · last 2026-08-22 · added 2026-07-24 · edited 2026-07-26 · refs 4 · mentions 1 · 347 chars | auto_only | new | — |
| `wizard` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-08-21 · edited 2026-08-21 · refs 1 · mentions 0 · 313 chars · dup of `mattpocock-skills:wizard` | duplicate | new | retire |
| `find-skills` | typed 0/90d · 0 all · auto 1/1 · trig 0/0 · last 2026-08-29 · added 2026-08-21 · edited 2026-08-21 · refs 0 · mentions 0 · 303 chars | — | new | — |
| `codebase-design` | typed 0/90d · 0 all · auto 5/5 · trig —/— · last 2026-09-10 · added 2026-08-21 · edited 2026-08-21 · refs 5 · mentions 2 · 265 chars · dup of `mattpocock-skills:codebase-design` | duplicate, auto_only | new | retire |
| `to-tickets` | typed 1/90d · 1 all · auto 2/2 · trig —/— · last 2026-09-18 · added 2026-08-21 · edited 2026-08-21 · refs 5 · mentions 1 · 247 chars · dup of `mattpocock-skills:to-tickets` | duplicate | new | retire |
| `git-guardrails-claude-code` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-08-21 · edited 2026-08-21 · refs 0 · mentions 0 · 243 chars · dup of `mattpocock-skills:git-guardrails-claude-code` | duplicate | new | retire |
| `research` | typed 0/90d · 0 all · auto 2/2 · trig —/— · last 2026-09-18 · added 2026-08-21 · edited 2026-08-21 · refs 27 · mentions 6 · 238 chars · dup of `mattpocock-skills:research` | duplicate | new | retire |
| `setup-pre-commit` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-08-21 · edited 2026-08-21 · refs 0 · mentions 0 · 238 chars · dup of `mattpocock-skills:setup-pre-commit` | duplicate | new | retire |
| `scaffold-exercises` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-08-21 · edited 2026-08-21 · refs 0 · mentions 0 · 204 chars · dup of `mattpocock-skills:scaffold-exercises` | duplicate | new | retire |
| `wayfinder` | typed 1/90d · 1 all · auto 1/1 · trig —/— · last 2026-09-18 · added 2026-08-21 · edited 2026-08-21 · refs 6 · mentions 3 · 197 chars · dup of `mattpocock-skills:wayfinder` | duplicate | new | retire |
| `setup-ts-deep-modules` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-08-21 · edited 2026-08-21 · refs 0 · mentions 0 · 185 chars · dup of `mattpocock-skills:setup-ts-deep-modules` | duplicate | new | retire |
| `setup-matt-pocock-skills` | typed 7/90d · 7 all · auto 1/1 · trig —/— · last 2026-09-18 · added 2026-08-21 · edited 2026-08-21 · refs 7 · mentions 0 · 180 chars · dup of `mattpocock-skills:setup-matt-pocock-skills` | duplicate | new | retire |
| `prototype` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-08-21 · edited 2026-08-21 · refs 11 · mentions 2 · 179 chars · dup of `mattpocock-skills:prototype` | duplicate | new | retire |
| `migrate-to-shoehorn` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-08-21 · edited 2026-08-21 · refs 0 · mentions 0 · 168 chars · dup of `mattpocock-skills:migrate-to-shoehorn` | duplicate | new | retire |
| `diagnosing-bugs` | typed 0/90d · 0 all · auto 0/0 · trig 5/11 · last 2026-08-22 · added 2026-08-21 · edited 2026-08-21 · refs 1 · mentions 0 · 156 chars · dup of `mattpocock-skills:diagnosing-bugs` | duplicate | new | retire |
| `grilling` | typed 0/90d · 0 all · auto 21/21 · trig —/— · last 2026-09-18 · added 2026-08-21 · edited 2026-08-21 · refs 14 · mentions 4 · 152 chars · dup of `mattpocock-skills:grilling` | duplicate, auto_only | new | retire |
| `domain-modeling` | typed 0/90d · 0 all · auto 22/22 · trig —/— · last 2026-09-18 · added 2026-08-21 · edited 2026-08-21 · refs 6 · mentions 4 · 150 chars · dup of `mattpocock-skills:domain-modeling` | duplicate, auto_only | new | retire |
| `tdd` | typed 0/90d · 0 all · auto 21/21 · trig 0/0 · last 2026-09-17 · added 2026-08-21 · edited 2026-08-21 · refs 4 · mentions 6 · 149 chars · dup of `mattpocock-skills:tdd` | duplicate, auto_only | new | retire |
| `to-spec` | typed 3/90d · 3 all · auto 5/5 · trig —/— · last 2026-09-18 · added 2026-08-21 · edited 2026-08-21 · refs 2 · mentions 3 · 149 chars · dup of `mattpocock-skills:to-spec` | duplicate | new | retire |
| `triage` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-08-21 · edited 2026-08-21 · refs 19 · mentions 4 · 136 chars · dup of `mattpocock-skills:triage` | duplicate | new | retire |
| `improve-codebase-architecture` | typed 4/90d · 4 all · auto 0/0 · trig —/— · last 2026-08-22 · added 2026-08-21 · edited 2026-08-21 · refs 2 · mentions 1 · 125 chars · dup of `mattpocock-skills:improve-codebase-architecture` | duplicate | new | retire |
| `writing-beats` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-08-21 · edited 2026-08-21 · refs 0 · mentions 0 · 111 chars · dup of `mattpocock-skills:writing-beats` | duplicate | new | retire |
| `grill-with-docs` | typed 9/90d · 9 all · auto 3/3 · trig —/— · last 2026-09-18 · added 2026-08-21 · edited 2026-08-21 · refs 2 · mentions 3 · 106 chars · dup of `mattpocock-skills:grill-with-docs` | duplicate | new | retire |
| `writing-for-agents` | typed 0/90d · 0 all · auto 4/4 · trig —/— · last 2026-09-18 · added 2026-08-21 · edited 2026-08-21 · refs 1 · mentions 0 · 103 chars · dup of `mattpocock-skills:writing-for-agents` | duplicate | new | retire |
| `claude-handoff` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-08-21 · edited 2026-08-21 · refs 0 · mentions 0 · 97 chars · dup of `mattpocock-skills:claude-handoff` | duplicate | new | retire |
| `to-questionnaire` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-08-21 · edited 2026-08-21 · refs 1 · mentions 0 · 88 chars · dup of `mattpocock-skills:to-questionnaire` | duplicate | new | retire |
| `handoff` | typed 68/90d · 79 all · auto 97/123 · trig —/— · last 2026-08-23 · added 2026-08-21 · edited 2026-08-21 · refs 22 · mentions 11 · 86 chars · dup of `mattpocock-skills:handoff` | duplicate | new | retire |
| `ask-matt` | typed 6/90d · 6 all · auto 0/0 · trig —/— · last 2026-08-24 · added 2026-08-21 · edited 2026-08-21 · refs 0 · mentions 0 · 83 chars · dup of `mattpocock-skills:ask-matt` | duplicate | new | retire |
| `loop-me` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-08-21 · edited 2026-08-21 · refs 0 · mentions 0 · 78 chars · dup of `mattpocock-skills:loop-me` | duplicate | new | retire |
| `writing-shape` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-08-21 · edited 2026-08-21 · refs 0 · mentions 0 · 77 chars · dup of `mattpocock-skills:writing-shape` | duplicate | new | retire |
| `resolving-merge-conflicts` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-08-21 · edited 2026-08-21 · refs 1 · mentions 0 · 70 chars · dup of `mattpocock-skills:resolving-merge-conflicts` | duplicate | new | retire |
| `teach` | typed 7/90d · 7 all · auto 0/0 · trig —/— · last 2026-09-18 · added 2026-08-21 · edited 2026-08-21 · refs 7 · mentions 2 · 61 chars · dup of `mattpocock-skills:teach` | duplicate | new | retire |
| `implement` | typed 24/90d · 24 all · auto 0/0 · trig —/— · last 2026-09-17 · added 2026-08-21 · edited 2026-08-21 · refs 14 · mentions 4 · 60 chars · dup of `mattpocock-skills:implement` | duplicate | new | retire |
| `writing-fragments` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-08-21 · edited 2026-08-21 · refs 0 · mentions 0 · 55 chars · dup of `mattpocock-skills:writing-fragments` | duplicate | new | retire |
| `grill-me` | typed 3/90d · 3 all · auto 0/0 · trig —/— · last 2026-08-13 · added 2026-08-21 · edited 2026-08-21 · refs 1 · mentions 0 · 51 chars · dup of `mattpocock-skills:grill-me` | duplicate | new | retire |
| `wait-what` | typed 12/90d · 12 all · auto 0/0 · trig —/— · last 2026-08-25 · added 2026-08-21 · edited 2026-08-21 · refs 1 · mentions 3 · 50 chars · dup of `mattpocock-skills:wait-what` | duplicate | new | retire |
| `implement-spec` | typed 1/90d · 1 all · auto 0/0 · trig —/— · last 2026-09-18 · added 2026-08-21 · edited 2026-08-21 · refs 1 · mentions 2 · 34 chars · dup of `mattpocock-skills:implement-spec` | duplicate | new | retire |
| `ship-and-route` | typed 1/90d · 2 all · auto 1/7 · trig 0/1 · last 2026-07-20 · added 2026-06-09 · edited 2026-08-22 · refs 7 · mentions 7 · 793 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | warm | — |
| `kickoff` | typed 0/90d · 1 all · auto 12/12 · trig 1/2 · last 2026-08-21 · added 2026-06-08 · edited 2026-07-24 · refs 9 · mentions 6 · 760 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | auto_only | hot | — |
| `audio-series` | typed 0/90d · 2 all · auto 5/6 · trig 71/86 · last 2026-09-17 · added 2026-06-08 · edited 2026-08-01 · refs 6 · mentions 4 · 615 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | auto_only | hot | — |
| `notebook-init` | typed 0/90d · 2 all · auto 5/6 · trig —/— · last 2026-08-01 · added 2026-06-08 · edited 2026-06-08 · refs 6 · mentions 4 · 205 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | auto_only | hot | — |

## command

| Item | Evidence | Flags | Temp | Proposed |
|---|---|---|---|---|
| `reframe-orchestrator` | typed 0/90d · 4 all · auto 0/0 · trig —/— · last 2026-06-05 · added 2026-06-08 · edited 2026-06-23 · refs 0 · mentions 1 · 260 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool | ask |
| `screenshot-iterate` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-06-08 · edited 2026-06-23 · refs 2 · mentions 0 · 199 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool | ask |
| `launch` | typed 7/90d · 7 all · auto 48/48 · trig 0/0 · last 2026-09-17 · added 2026-08-10 · edited 2026-08-21 · refs 27 · mentions 8 · 638 chars | oversized | new | ask |
| `handoff-session` | typed 0/90d · 0 all · auto 18/18 · trig —/— · last 2026-09-18 · added 2026-09-17 · edited 2026-09-09 · refs 8 · mentions 1 · 509 chars | auto_only | new | — |
| `wiki-backfill` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-07-26 · edited 2026-07-26 · refs 2 · mentions 0 · 332 chars | — | new | — |
| `wiki-init` | typed 0/90d · 0 all · auto 1/1 · trig —/— · last 2026-07-26 · added 2026-07-24 · edited 2026-07-26 · refs 3 · mentions 0 · 315 chars | — | new | — |
| `crap-check` | typed 0/90d · 0 all · auto 0/0 · trig 1/1 · last 2026-09-09 · added 2026-08-27 · edited 2026-08-27 · refs 1 · mentions 4 · 314 chars | — | new | — |
| `tdd-loop` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-08-21 · edited 2026-08-21 · refs 3 · mentions 2 · 218 chars | — | new | — |
| `catchup` | typed 2/90d · 2 all · auto 0/0 · trig —/— · last 2026-07-06 · added 2026-07-06 · edited 2026-07-06 · refs 3 · mentions 1 · 214 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | new | — |
| `autonomous-milestone` | typed 0/90d · 25 all · auto 6/8 · trig —/— · last 2026-08-19 · added 2026-08-27 · edited 2026-08-27 · refs 6 · mentions 5 · 0 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | paused, auto_only | new | — |
| `learn` | typed 0/90d · 0 all · auto 1/1 · trig —/— · last 2026-08-21 · added 2026-08-21 · edited 2026-08-21 · refs 15 · mentions 2 · 0 chars | paused | new | — |
| `smoke-test` | typed 0/90d · 1 all · auto 2/3 · trig —/— · last 2026-07-19 · added 2026-06-12 · edited 2026-06-12 · refs 1 · mentions 7 · 367 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | warm | — |
| `claudify-repo` | typed 0/90d · 6 all · auto 1/1 · trig —/— · last 2026-07-18 · added 2026-06-08 · edited 2026-08-21 · refs 2 · mentions 9 · 313 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | warm | — |
| `trim-context` | typed 0/90d · 6 all · auto 1/2 · trig 0/2 · last 2026-07-20 · added 2026-06-08 · edited 2026-06-23 · refs 3 · mentions 6 · 306 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | warm | — |
| `envsetup` | typed 0/90d · 0 all · auto 1/1 · trig —/— · last 2026-07-06 · added 2026-06-08 · edited 2026-06-08 · refs 0 · mentions 3 · 159 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | warm | — |
| `brainstorm` | typed 0/90d · 1 all · auto 5/5 · trig —/— · last 2026-09-16 · added 2026-06-08 · edited 2026-07-27 · refs 10 · mentions 15 · 551 chars · vendored in DogHood, blind-cite, buoy-legal +14 more · routes→ autonomous-milestone | auto_only, dangling, oversized | hot | relocate |
| `prompt-optimize` | typed 3/90d · 4 all · auto 4/4 · trig —/— · last 2026-09-18 · added 2026-06-08 · edited 2026-08-21 · refs 3 · mentions 5 · 312 chars · vendored in DogHood, blind-cite, buoy-legal +14 more · routes→ autonomous-milestone | dangling | hot | — |
| `begin` | typed 2/90d · 24 all · auto 13/15 · trig —/— · last 2026-09-16 · added 2026-06-08 · edited 2026-06-30 · refs 6 · mentions 6 · 243 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | hot | — |
| `explore-plan` | typed 0/90d · 0 all · auto 12/12 · trig —/— · last 2026-09-08 · added 2026-06-08 · edited 2026-06-23 · refs 3 · mentions 3 · 214 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | auto_only | hot | — |
| `boot_server` | typed 3/90d · 6 all · auto 7/8 · trig —/— · last 2026-09-09 · added 2026-06-08 · edited 2026-06-08 · refs 1 · mentions 3 · 201 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | hot | — |
| `wrap` | typed 5/90d · 13 all · auto 1/27 · trig —/— · last 2026-07-06 · added 2026-06-08 · edited 2026-06-30 · refs 17 · mentions 10 · 193 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | hot | — |

## agent

| Item | Evidence | Flags | Temp | Proposed |
|---|---|---|---|---|
| `spec-miner` | typed —/90d · — all · auto 0/0 · trig —/— · last — · added 2026-07-27 · edited 2026-08-21 · refs 1 · mentions 4 · 715 chars | — | new | — |
| `mutation-hardener` | typed —/90d · — all · auto 0/0 · trig —/— · last — · added 2026-08-20 · edited 2026-08-20 · refs 1 · mentions 2 · 675 chars | — | new | — |
| `silent-failure-hunter` | typed —/90d · — all · auto 1/1 · trig —/— · last 2026-07-28 · added 2026-07-27 · edited 2026-07-27 · refs 3 · mentions 4 · 675 chars | — | new | — |
| `specifier` | typed —/90d · — all · auto 1/1 · trig —/— · last 2026-08-21 · added 2026-08-20 · edited 2026-08-20 · refs 2 · mentions 5 · 543 chars | — | new | — |
| `adversarial-reviewer` | typed —/90d · — all · auto 597/597 · trig —/— · last 2026-09-18 · added 2026-07-26 · edited 2026-07-27 · refs 4 · mentions 5 · 520 chars | — | new | — |
| `review-judge` | typed —/90d · — all · auto 18/18 · trig —/— · last 2026-09-18 · added 2026-07-26 · edited 2026-07-27 · refs 2 · mentions 2 · 501 chars | — | new | — |
| `gauntlet-coder` | typed —/90d · — all · auto 0/0 · trig —/— · last — · added 2026-08-20 · edited 2026-08-20 · refs 1 · mentions 1 · 477 chars | — | new | — |

## output-style

| Item | Evidence | Flags | Temp | Proposed |
|---|---|---|---|---|
| `adhd` | typed —/90d · — all · auto —/— · trig —/— · last — · added 2026-08-13 · edited 2026-08-13 · refs 2 · mentions 2 · 236 chars | unlinked | new | ask |

## plugin

| Item | Evidence | Flags | Temp | Proposed |
|---|---|---|---|---|
| `swift-lsp@claude-plugins-official` | typed —/90d · — all · auto 0/0 · trig —/— · last — · added 2026-05-15 · edited — · refs 0 · mentions 1 · 0 chars | — | cold | retire |
| `focus-coach@ksdisch` | typed —/90d · — all · auto 0/2 · trig —/— · last 2026-06-08 · added 2026-06-08 · edited — · refs 0 · mentions 0 · 371 chars | — | cool | ask |
| `claude-code-setup@claude-plugins-official` | typed —/90d · — all · auto 0/6 · trig —/— · last 2026-06-06 · added 2026-05-11 · edited — · refs 0 · mentions 0 · 354 chars | — | cool | ask |
| `safety-net@cc-marketplace` | typed —/90d · — all · auto 0/0 · trig —/— · last — · added 2026-05-17 · edited — · refs 1 · mentions 2 · 71 chars | — | cool | ask |
| `code-review@claude-plugins-official` | typed —/90d · — all · auto 0/0 · trig —/— · last — · added 2026-05-11 · edited — · refs 7 · mentions 2 · 0 chars | — | cool | ask |
| `mattpocock-skills@mattpocock` | typed —/90d · — all · auto 216/254 · trig —/— · last 2026-09-18 · added 2026-08-21 · edited — · refs 0 · mentions 1 · 5,303 chars | oversized | new | ask |
| `superpowers@claude-plugins-official` | typed —/90d · — all · auto 122/122 · trig —/— · last 2026-09-18 · added 2026-06-23 · edited — · refs 3 · mentions 9 · 1,965 chars | — | new | — |
| `claude-md-management@claude-plugins-official` | typed —/90d · — all · auto 0/0 · trig —/— · last — · added 2026-06-23 · edited — · refs 0 · mentions 0 · 338 chars | — | new | — |
| `skill-creator@claude-plugins-official` | typed —/90d · — all · auto 4/4 · trig —/— · last 2026-07-24 · added 2026-06-23 · edited — · refs 0 · mentions 0 · 319 chars | — | new | — |
| `frontend-design@claude-plugins-official` | typed —/90d · — all · auto 1/1 · trig —/— · last 2026-06-29 · added 2026-06-23 · edited — · refs 0 · mentions 0 · 234 chars | — | new | — |
| `code-simplifier@claude-plugins-official` | typed —/90d · — all · auto 0/0 · trig —/— · last — · added 2026-06-23 · edited — · refs 0 · mentions 3 · 0 chars | — | new | — |
| `context7@claude-plugins-official` | typed —/90d · — all · auto 21/21 · trig —/— · last 2026-09-17 · added 2026-06-23 · edited — · refs 0 · mentions 1 · 0 chars | — | new | — |
| `feature-dev@claude-plugins-official` | typed —/90d · — all · auto 5/5 · trig —/— · last 2026-07-27 · added 2026-06-23 · edited — · refs 0 · mentions 2 · 0 chars | — | new | — |
| `github@claude-plugins-official` | typed —/90d · — all · auto 0/0 · trig —/— · last — · added 2026-06-23 · edited — · refs 31 · mentions 8 · 0 chars | disabled | new | — |
| `playwright@claude-plugins-official` | typed —/90d · — all · auto 432/432 · trig —/— · last 2026-09-10 · added 2026-06-23 · edited — · refs 7 · mentions 4 · 0 chars | — | new | — |
| `ralph-loop@claude-plugins-official` | typed —/90d · — all · auto 0/0 · trig —/— · last — · added 2026-06-23 · edited — · refs 0 · mentions 1 · 0 chars | — | new | — |
| `warp@claude-code-warp` | typed —/90d · — all · auto 0/0 · trig —/— · last — · added 2026-06-26 · edited — · refs 1 · mentions 2 · 0 chars | — | new | — |
| `obsidian@obsidian-skills` | typed —/90d · — all · auto 16/17 · trig —/— · last 2026-09-06 · added 2026-05-17 · edited — · refs 1 · mentions 1 · 1,557 chars | — | hot | — |
| `voicemode@voicemode` | typed —/90d · — all · auto 19/34 · trig —/— · last 2026-09-18 · added 2026-05-28 · edited — · refs 2 · mentions 0 · 553 chars | — | hot | — |

## mcp

| Item | Evidence | Flags | Temp | Proposed |
|---|---|---|---|---|
| `mcp #1` | typed —/90d · — all · auto 0/150 · trig —/— · last 2026-06-04 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | cool | ask |
| `mcp #3` | typed —/90d · — all · auto 0/660 · trig —/— · last 2026-05-02 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | cool | ask |
| `mcp #4` | typed —/90d · — all · auto 0/4 · trig —/— · last 2026-05-27 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | cool | ask |
| `mcp #5` | typed —/90d · — all · auto 0/34 · trig —/— · last 2026-06-05 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | cool | ask |
| `mcp #7` | typed —/90d · — all · auto 0/3 · trig —/— · last 2026-05-17 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | cool | ask |
| `mcp #8` | typed —/90d · — all · auto 0/16 · trig —/— · last 2026-06-02 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | cool | ask |
| `mcp #9` | typed —/90d · — all · auto 0/1 · trig —/— · last 2026-06-01 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | cool | ask |
| `mcp #10` | typed —/90d · — all · auto 0/4 · trig —/— · last 2026-04-29 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | cool | ask |
| `mcp #11` | typed —/90d · — all · auto 0/11 · trig —/— · last 2026-06-05 · added — · edited — · refs 0 · mentions 2 · 0 chars | — | cool | ask |
| `mcp #13` | typed —/90d · — all · auto 0/11 · trig —/— · last 2026-05-27 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | cool | ask |
| `mcp #19` | typed —/90d · — all · auto 0/1 · trig —/— · last 2026-06-05 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only, denied | cool | ask |
| `mcp #23` | typed —/90d · — all · auto 0/24 · trig —/— · last 2026-06-02 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | cool | ask |
| `mcp #32` | typed —/90d · — all · auto 0/12 · trig —/— · last 2026-06-05 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | cool | ask |
| `mcp #12` | typed —/90d · — all · auto 3/3 · trig —/— · last 2026-08-12 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | warm | — |
| `mcp #15` | typed —/90d · — all · auto 2/22 · trig —/— · last 2026-07-21 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only, denied | warm | — |
| `mcp #22` | typed —/90d · — all · auto 4/5 · trig —/— · last 2026-07-11 · added — · edited — · refs 2 · mentions 0 · 0 chars | connector_only | warm | — |
| `mcp #2` | typed —/90d · — all · auto 8/8 · trig —/— · last 2026-08-04 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | hot | — |
| `mcp #6` | typed —/90d · — all · auto 57/512 · trig —/— · last 2026-07-21 · added — · edited — · refs 0 · mentions 2 · 0 chars | — | hot | — |
| `mcp #14` | typed —/90d · — all · auto 739/739 · trig —/— · last 2026-09-18 · added — · edited — · refs 0 · mentions 2 · 0 chars | connector_only | hot | — |
| `mcp #16` | typed —/90d · — all · auto 471/480 · trig —/— · last 2026-09-18 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | hot | — |
| `mcp #17` | typed —/90d · — all · auto 509/537 · trig —/— · last 2026-09-18 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | hot | — |
| `mcp #18` | typed —/90d · — all · auto 33/36 · trig —/— · last 2026-09-09 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | hot | — |
| `mcp #20` | typed —/90d · — all · auto 7/7 · trig —/— · last 2026-08-18 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | hot | — |
| `mcp #21` | typed —/90d · — all · auto 68/68 · trig —/— · last 2026-08-12 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only, denied | hot | — |
| `mcp #24` | typed —/90d · — all · auto 12/27 · trig —/— · last 2026-07-20 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | hot | — |
| `mcp #25` | typed —/90d · — all · auto 63/108 · trig —/— · last 2026-08-12 · added — · edited — · refs 31 · mentions 8 · 0 chars | connector_only | hot | — |
| `mcp #26` | typed —/90d · — all · auto 870/2635 · trig —/— · last 2026-07-24 · added — · edited — · refs 2 · mentions 2 · 0 chars | — | hot | — |
| `mcp #27` | typed —/90d · — all · auto 527/1307 · trig —/— · last 2026-09-16 · added — · edited — · refs 0 · mentions 2 · 0 chars | — | hot | — |
| `mcp #28` | typed —/90d · — all · auto 273/511 · trig —/— · last 2026-08-13 · added — · edited — · refs 7 · mentions 4 · 0 chars | connector_only | hot | — |
| `mcp #29` | typed —/90d · — all · auto 21/21 · trig —/— · last 2026-09-17 · added — · edited — · refs 0 · mentions 0 · 0 chars | — | hot | — |
| `mcp #30` | typed —/90d · — all · auto 432/432 · trig —/— · last 2026-09-10 · added — · edited — · refs 0 · mentions 0 · 0 chars | — | hot | — |
| `mcp #31` | typed —/90d · — all · auto 19/34 · trig —/— · last 2026-09-18 · added — · edited — · refs 0 · mentions 0 · 0 chars | — | hot | — |
| `mcp #33` | typed —/90d · — all · auto 1368/1415 · trig —/— · last 2026-09-18 · added — · edited — · refs 3 · mentions 2 · 0 chars | — | hot | — |

## hook

| Item | Evidence | Flags | Temp | Proposed |
|---|---|---|---|---|
| `Notification[0][0]` | typed —/90d · — all · auto —/— · trig —/— · last — · added — · edited — · refs 0 · mentions 0 · 0 chars | disabled_comment | unknown | retire |
| `Notification[0][1]` | typed —/90d · — all · auto —/— · trig —/— · last — · added — · edited — · refs 0 · mentions 0 · 0 chars | disabled_comment | unknown | retire |
| `PreToolUse[0][0]` | typed —/90d · — all · auto —/— · trig —/— · last — · added — · edited — · refs 0 · mentions 0 · 0 chars | — | unknown | — |
| `PreToolUse[0][1]` | typed —/90d · — all · auto —/— · trig —/— · last — · added — · edited — · refs 0 · mentions 0 · 0 chars | — | unknown | — |
| `PreToolUse[1][0]` | typed —/90d · — all · auto —/— · trig —/— · last — · added — · edited — · refs 0 · mentions 0 · 0 chars | — | unknown | — |
| `SessionEnd[0][0]` | typed —/90d · — all · auto —/— · trig —/— · last — · added — · edited — · refs 0 · mentions 0 · 0 chars | — | unknown | — |
| `Stop[0][0]` | typed —/90d · — all · auto —/— · trig —/— · last — · added — · edited — · refs 0 · mentions 0 · 0 chars | — | unknown | — |
| `Stop[1][0]` | typed —/90d · — all · auto —/— · trig —/— · last — · added — · edited — · refs 0 · mentions 0 · 0 chars | disabled_comment | unknown | retire |
| `Stop[1][1]` | typed —/90d · — all · auto —/— · trig —/— · last — · added — · edited — · refs 0 · mentions 0 · 0 chars | disabled_comment | unknown | retire |
| `UserPromptSubmit[0][0]` | typed —/90d · — all · auto —/— · trig —/— · last — · added — · edited — · refs 0 · mentions 0 · 0 chars | — | unknown | — |
| `UserPromptSubmit[1][0]` | typed —/90d · — all · auto —/— · trig —/— · last — · added — · edited — · refs 0 · mentions 0 · 0 chars | — | unknown | — |

## memory

33 memory entries · 32 flagged `empty` · 1 holding files · 520 chars. Names are project path slugs and are not printed; they are in the local JSON.

## claude-md

| Item | Evidence | Flags | Temp | Proposed |
|---|---|---|---|---|
| `New Feature Mode` | typed —/90d · — all · auto —/— · trig 0/0 · last — · added 2026-06-08 · edited — · refs 2 · mentions 1 · 767 chars | — | cool | ask |
| `Improvement Mode` | typed —/90d · — all · auto —/— · trig 0/0 · last — · added 2026-06-08 · edited — · refs 1 · mentions 1 · 717 chars | — | cool | ask |
| `Local-Markdown Issue Tracker: Tickets Index (added 2026-08-22)` | typed —/90d · — all · auto —/— · trig 29/29 · last 2026-09-18 · added 2026-08-22 · edited — · refs 0 · mentions 0 · 4,086 chars | oversized | new | ask |
| `Reference Doc Maintenance` | typed —/90d · — all · auto —/— · trig 12/13 · last 2026-09-18 · added 2026-07-23 · edited — · refs 0 · mentions 1 · 3,696 chars | — | new | — |
| `Never show me a bare identifier (added 2026-08-13)` | typed —/90d · — all · auto —/— · trig 31/42 · last 2026-09-18 · added 2026-08-13 · edited — · refs 0 · mentions 0 · 3,121 chars | — | new | — |
| `Planner/Builder Protocol (added 2026-07-27)` | typed —/90d · — all · auto —/— · trig 13/14 · last 2026-09-09 · added 2026-07-27 · edited — · refs 0 · mentions 0 · 2,637 chars | — | new | — |
| `When to update` | typed —/90d · — all · auto —/— · trig —/— · last — · added 2026-07-23 · edited — · refs 0 · mentions 0 · 2,277 chars | — | new | — |
| `Project Wiki` | typed —/90d · — all · auto —/— · trig 37/38 · last 2026-08-22 · added 2026-07-24 · edited — · refs 2 · mentions 0 · 749 chars · vendored in DogHood, bandmark, blind-cite +20 more | — | new | — |
| `Format rules` | typed —/90d · — all · auto —/— · trig —/— · last — · added 2026-07-23 · edited — · refs 1 · mentions 0 · 562 chars | — | new | — |
| ``Kickoff Mode → run the `/kickoff` skill`` | typed —/90d · — all · auto —/— · trig 1/3 · last 2026-08-01 · added 2026-06-08 · edited — · refs 0 · mentions 0 · 771 chars | — | warm | — |
| `Git Workflow` | typed —/90d · — all · auto —/— · trig —/— · last — · added 2026-06-08 · edited — · refs 8 · mentions 8 · 4,004 chars | oversized | unknown | — |
| `Track multi-step work` | typed —/90d · — all · auto —/— · trig —/— · last — · added 2026-06-18 · edited — · refs 0 · mentions 0 · 681 chars | — | unknown | — |
| `Clarifying questions and option formatting` | typed —/90d · — all · auto —/— · trig —/— · last — · added 2026-06-08 · edited — · refs 0 · mentions 0 · 399 chars | — | unknown | — |
| `Unattended runs only` | typed —/90d · — all · auto —/— · trig —/— · last — · added 2026-06-18 · edited — · refs 0 · mentions 0 · 362 chars · routes→ autonomous-milestone | dangling | unknown | — |
| `Scope discipline` | typed —/90d · — all · auto —/— · trig —/— · last — · added 2026-06-18 · edited — · refs 2 · mentions 1 · 359 chars | — | unknown | — |
| `Act vs. assess` | typed —/90d · — all · auto —/— · trig —/— · last — · added 2026-06-18 · edited — · refs 1 · mentions 0 · 353 chars | — | unknown | — |
| `Finish the turn` | typed —/90d · — all · auto —/— · trig —/— · last — · added 2026-06-18 · edited — · refs 1 · mentions 0 · 251 chars | — | unknown | — |
| `No false progress` | typed —/90d · — all · auto —/— · trig —/— · last — · added 2026-06-18 · edited — · refs 1 · mentions 0 · 240 chars | — | unknown | — |
| `Decisiveness` | typed —/90d · — all · auto —/— · trig —/— · last — · added 2026-06-18 · edited — · refs 1 · mentions 0 · 239 chars | — | unknown | — |
