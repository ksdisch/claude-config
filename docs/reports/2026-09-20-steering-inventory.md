# Steering inventory — 2026-09-20

Window: last 90 days (since 2026-06-22). History rows: 5,474. Transcripts scanned: 6157 (6151 from cache). Surfaces: skill, command, agent, output-style, plugin, mcp, hook, memory, claude-md.

Usage evidence is this machine's local corpus only — every count is a floor, never a ceiling.

Read-only; an Instrument, never a Gate. An em dash is unmeasured, never zero.

## Totals

| Surface | Items | Always-loaded chars |
|---|---|---|
| skill | 80 | 38,198 |
| command | 21 | 5,858 |
| agent | 7 | 4,106 |
| output-style | 1 | 236 |
| plugin | 19 | 11,065 |
| mcp | 33 | 0 |
| hook | 11 | 0 |
| memory | 33 | 520 |
| claude-md | 19 | 23,877 |
| ALL | 224 | 83,860 |

## Proposals

47 rows need a ruling. Grouped by surface with `claude-md` last; `retire` first inside a surface, then `ask`, then `relocate`. Everything else is omitted and summarised below.

| # | Surface | Item | Proposed | Evidence | Flags | Temp |
|---|---|---|---|---|---|---|
| 1 | skill | 36 loose skill copies of plugin mattpocock-skills | retire | 36 items · 5,303 chars · `ask-matt`, `claude-handoff`, `code-review` +33 more | collapsed | — |
| 2 | skill | `adversarial-review` | ask | typed 0/90d · 0 all · auto 161/161 · trig 44/46 · last 2026-09-19 · added 2026-07-26 · edited 2026-08-27 · refs 12 · mentions 14 · 1,528 chars | auto_only, oversized | new |
| 3 | skill | `paper-gloss` | ask | typed 4/90d · 4 all · auto 3/3 · trig 0/0 · last 2026-08-24 · added 2026-07-23 · edited 2026-07-29 · refs 3 · mentions 6 · 1,426 chars · vendored in blind-cite | oversized | new |
| 4 | skill | `paper-eli5` | ask | typed 1/90d · 1 all · auto 3/3 · trig 0/0 · last 2026-08-04 · added 2026-07-19 · edited 2026-07-28 · refs 5 · mentions 3 · 1,351 chars | oversized | new |
| 5 | skill | `architecture-viewer` | ask | typed 0/90d · 0 all · auto 1/1 · trig 1/1 · last 2026-08-23 · added 2026-08-20 · edited 2026-08-20 · refs 1 · mentions 5 · 1,195 chars | oversized | new |
| 6 | skill | `bug-hunt` | ask | typed 0/90d · 0 all · auto 7/7 · trig 0/0 · last 2026-08-13 · added 2026-06-26 · edited 2026-07-27 · refs 8 · mentions 6 · 1,192 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | auto_only, oversized | new |
| 7 | skill | `curriculum-sync` | ask | typed 0/90d · 0 all · auto 0/0 · trig 0/0 · last — · added 2026-08-07 · edited 2026-08-07 · refs 0 · mentions 1 · 1,134 chars | oversized | new |
| 8 | skill | `career-coach` | ask | typed 0/90d · 0 all · auto 2/2 · trig 1/1 · last 2026-08-20 · added 2026-07-23 · edited 2026-07-23 · refs 0 · mentions 0 · 1,133 chars | oversized | new |
| 9 | skill | `reweave` | ask | typed 4/90d · 4 all · auto 2/2 · trig 3/3 · last 2026-09-14 · added 2026-07-21 · edited 2026-07-21 · refs 0 · mentions 2 · 1,069 chars | oversized | new |
| 10 | skill | `artifacts-generate` | ask | typed 0/90d · 0 all · auto 0/3 · trig 0/0 · last 2026-06-03 · added 2026-06-08 · edited 2026-06-08 · refs 0 · mentions 0 · 738 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool |
| 11 | skill | `backlog-hygiene` | ask | typed 1/90d · 1 all · auto 19/19 · trig 19/20 · last 2026-09-19 · added 2026-07-19 · edited 2026-08-21 · refs 8 · mentions 3 · 697 chars · routes→ autonomous-milestone | dangling | new |
| 12 | skill | `reorient` | ask | typed 1/90d · 1 all · auto 1/1 · trig 1/1 · last 2026-08-03 · added 2026-07-19 · edited 2026-07-19 · refs 2 · mentions 2 · 625 chars · routes→ autonomous-milestone | dangling | new |
| 13 | skill | `nlm-skill` | ask | typed 0/90d · 0 all · auto 0/1 · trig 0/0 · last 2026-05-28 · added 2026-06-08 · edited 2026-06-08 · refs 8 · mentions 3 · 611 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool |
| 14 | skill | `artifacts-audit` | ask | typed 0/90d · 1 all · auto 0/0 · trig —/— · last 2026-05-31 · added 2026-06-08 · edited 2026-06-08 · refs 1 · mentions 0 · 593 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool |
| 15 | skill | `portfolio-notebook-sync` | ask | typed 0/90d · 0 all · auto 5/5 · trig 0/0 · last 2026-08-06 · added 2026-08-02 · edited 2026-08-03 · refs 3 · mentions 1 · 582 chars · routes→ learn | auto_only, dangling | new |
| 16 | skill | `match-the-mock` | ask | typed 0/90d · 0 all · auto 0/0 · trig 0/0 · last — · added 2026-06-08 · edited 2026-06-08 · refs 1 · mentions 0 · 396 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool |
| 17 | skill | `notebook-assist` | ask | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-06-08 · edited 2026-07-13 · refs 4 · mentions 3 · 366 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool |
| 18 | skill | `mini` | ask | typed 0/90d · 2 all · auto 0/0 · trig —/— · last 2026-05-20 · added 2026-06-08 · edited 2026-06-08 · refs 5 · mentions 1 · 352 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool |
| 19 | command | `launch` | ask | typed 8/90d · 8 all · auto 48/48 · trig 0/0 · last 2026-09-20 · added 2026-08-10 · edited 2026-08-21 · refs 27 · mentions 9 · 638 chars | oversized | new |
| 20 | command | `reframe-orchestrator` | ask | typed 0/90d · 4 all · auto 0/0 · trig —/— · last 2026-06-05 · added 2026-06-08 · edited 2026-06-23 · refs 0 · mentions 1 · 260 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool |
| 21 | command | `screenshot-iterate` | ask | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-06-08 · edited 2026-06-23 · refs 2 · mentions 0 · 199 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool |
| 22 | command | `brainstorm` | relocate | typed 0/90d · 1 all · auto 5/5 · trig —/— · last 2026-09-16 · added 2026-06-08 · edited 2026-07-27 · refs 11 · mentions 16 · 551 chars · vendored in DogHood, blind-cite, buoy-legal +14 more · routes→ autonomous-milestone | auto_only, dangling, oversized | hot |
| 23 | output-style | `adhd` | ask | typed —/90d · — all · auto —/— · trig —/— · last — · added 2026-08-13 · edited 2026-08-13 · refs 2 · mentions 2 · 236 chars | unlinked | new |
| 24 | plugin | `swift-lsp@claude-plugins-official` | retire | typed —/90d · — all · auto 0/0 · trig —/— · last — · added 2026-05-15 · edited — · refs 0 · mentions 1 · 0 chars | — | cold |
| 25 | plugin | `mattpocock-skills@mattpocock` | ask | typed —/90d · — all · auto 220/258 · trig —/— · last 2026-09-20 · added 2026-08-21 · edited — · refs 0 · mentions 2 · 5,303 chars | oversized | new |
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
| 45 | claude-md | `Local-Markdown Issue Tracker: Tickets Index (added 2026-08-22)` | ask | typed —/90d · — all · auto —/— · trig 31/31 · last 2026-09-20 · added 2026-08-22 · edited — · refs 0 · mentions 0 · 4,086 chars | oversized | new |
| 46 | claude-md | `New Feature Mode` | ask | typed —/90d · — all · auto —/— · trig 0/0 · last — · added 2026-06-08 · edited — · refs 2 · mentions 1 · 767 chars | — | cool |
| 47 | claude-md | `Improvement Mode` | ask | typed —/90d · — all · auto —/— · trig 0/0 · last — · added 2026-06-08 · edited — · refs 1 · mentions 2 · 717 chars | — | cool |

## Ratification table (rendered, not yet ruled)

The same 47 rows as the Proposals table above, each **titled**, and every `ask` carrying the
specific question a ruling needs. Nothing here is applied — `--report` stops after this table;
`/retire` re-renders it live for the ruling. Usage evidence is this machine's local corpus only,
so every count is a **floor**: a zero means "not seen on this Mac", never "never used".

Grouped by surface with `claude-md` last; `retire` first inside a surface, then `ask`, then
`relocate`. Evidence is condensed — the Proposals table above has the full line per row.
MCP names are withheld (this repo is public); the run's local JSON carries them and a sweep
session resolves them from the same script.

Verdict vocabulary: `retire` · `keep` (optional clause) · `pause` · `merge-into <id>` ·
`relocate` · `ask`. Answer by row: `1 retire, 2 keep — still earns it, 7 pause, rest as proposed`.
`rest as proposed` never applies to an `ask` row — `ask` has no verdict to fall back on.

### skill

| # | Item | Surface | Evidence | Proposed | Question / why |
|---|---|---|---|---|---|
| 1 | **36 loose skill copies of plugin `mattpocock-skills`** — untracked `skills/` duplicates of what the enabled plugin already ships (`ask-matt`, `tdd`, `to-tickets`, `wayfinder`, +32 more) | skill | 36 items · 5,303 chars · duplicate of `mattpocock-skills@mattpocock` | retire | design decision D7: the plugin is the survivor, namespaced and self-updating. Verify bare `/tdd` still resolves before applying; the `.gitignore` block goes with them. |
| 2 | **`adversarial-review`** — the pre-merge author↔reviewer↔judge loop; the standing merge gate | skill | typed 0/90d · auto 161/161 · trig 44/46 · last 2026-09-19 · refs 12 · 1,528 chars | ask | never typed, chosen by sessions 161 times — auto-only and plainly earning its place. The only flag is size: 1.5k chars of description in every prompt. Keep as-is, or keep and trim the description? |
| 3 | **`paper-gloss`** — turns a `paper-eli5` rewrite into a clickable-jargon HTML page | skill | typed 4/90d · auto 3/3 · last 2026-08-24 · refs 3 · 1,426 chars · vendored in blind-cite | ask | used this window; the flag is an oversized description. Keep as-is, or keep and trim? |
| 4 | **`paper-eli5`** — 1:1 plain-English rewrite of someone else's paper | skill | typed 1/90d · auto 3/3 · last 2026-08-04 · refs 5 · 1,351 chars | ask | same question as row 3. |
| 5 | **`architecture-viewer`** — repo → clickable HTML architecture map | skill | typed 0/90d · auto 1/1 · trig 1/1 · last 2026-08-23 · added 2026-08-20 · refs 1 · 1,195 chars | ask | one use in the month since it was added; oversized. Keep for the season it serves (and trim?), or retire? |
| 6 | **`bug-hunt`** — proactive multi-agent defect hunt with adversarial verification | skill | typed 0/90d · auto 7/7 · last 2026-08-13 · refs 8 · 1,192 chars · vendored in 17 repos | ask | auto-only (7 picks) and oversized. Keep as-is, or keep and trim? |
| 7 | **`curriculum-sync`** — keeps a NotebookLM notebook's derived audio/quiz content in step with its source repos | skill | typed 0/90d · auto 0/0 · trig 0/0 · last — · added 2026-08-07 · refs 0 · 1,134 chars | ask | never fired in the six weeks since it was added, nothing routes to it, oversized. Retire, or is its season still ahead? |
| 8 | **`career-coach`** — ICF-style career and life coaching interview | skill | typed 0/90d · auto 2/2 · trig 1/1 · last 2026-08-20 · refs 0 · 1,133 chars | ask | two auto picks, the last a month ago, nothing routes to it, oversized. Keep for the job-search season, or retire? |
| 9 | **`reweave`** — regenerate an earlier response with a follow-up folded in at the source | skill | typed 4/90d · trig 3/3 · last 2026-09-14 · refs 0 · 1,069 chars | ask | in use this month; the only flag is size. Keep as-is, or keep and trim? |
| 10 | **`artifacts-generate`** — generate READMEs/ADRs/runbooks from a written `docs/artifacts-plan.md` | skill | typed 0/90d · auto 0/3 · last 2026-06-03 · refs 0 · 738 chars · vendored in 17 repos | ask | three picks ever, none in 109 days, nothing routes to it. Retire (with row 14, its pair)? |
| 11 | **`backlog-hygiene`** — groom and sequence the existing backlog; pick the next arc | skill | typed 1/90d · auto 19/19 · trig 19/20 · last 2026-09-19 · refs 8 · routes→ `autonomous-milestone` (paused) | ask | hot. The only flag is the dangling hand-off to the paused `autonomous-milestone`. Keep and leave the route (a-m may return), or keep and re-point the hand-off? |
| 12 | **`reorient`** — catch-up after a real gap away from a project | skill | typed 1/90d · auto 1/1 · trig 1/1 · last 2026-08-03 · refs 2 · routes→ `autonomous-milestone` (paused) | ask | the same dangling route as row 11, and cooler (one use, early August). Keep with row 11's ruling, or retire? |
| 13 | **`nlm-skill`** — expert guide to the `nlm` CLI and NotebookLM MCP | skill | typed 0/90d · auto 0/1 · last 2026-05-28 · refs 8 · mentions 3 · 611 chars · vendored in 17 repos | ask | silent since May, but all 8 notebook skills route to it as their reference. Keep as that reference, or retire and excise the 8 referrers? |
| 14 | **`artifacts-audit`** — audit which engineering artifacts a codebase should have | skill | typed 0/90d · 1 all · last 2026-05-31 · refs 1 (its pair, row 10) · 593 chars · vendored in 17 repos | ask | one use ever, 112 days ago. Retire with row 10? |
| 15 | **`portfolio-notebook-sync`** — keep the research-portfolio NotebookLM notebook in step with `~/Projects/portfolio` | skill | typed 0/90d · auto 5/5 · last 2026-08-06 · refs 3 · routes→ `learn` (paused) | ask | five auto picks in early August, nothing since; routes to the paused `learn`. Keep, or pause alongside `learn`? |
| 16 | **`match-the-mock`** — implement a UI against a mock and iterate via screenshots | skill | typed 0/90d · auto 0/0 · trig 0/0 · last — · refs 1 · 396 chars · vendored in 17 repos | ask | never used; the same job as `screenshot-iterate` (row 21). Retire both, or keep one? |
| 17 | **`notebook-assist`** — refine or brainstorm artifacts for an existing NotebookLM notebook | skill | typed 0/90d · auto 0/0 · last — · refs 4 · mentions 3 · 366 chars · vendored in 17 repos | ask | never used, but four notebook skills route to it. Retire and excise the referrers, or keep? |
| 18 | **`mini`** — kick off a throwaway mini project under `~/Projects/mini/` | skill | typed 0/90d · 2 all · last 2026-05-20 · refs 5 (incl. the global `CLAUDE.md` Kickoff pointer) · 352 chars · vendored in 17 repos | ask | two uses ever, none since May; `CLAUDE.md` still says "for light throwaway experiments, use /mini". Retire (and drop the pointer), or keep as kickoff's light sibling? |

### command

| # | Item | Surface | Evidence | Proposed | Question / why |
|---|---|---|---|---|---|
| 19 | **`launch`** — open a new terminal and a fresh Claude session with the prompt on the clipboard | command | typed 8/90d · auto 48/48 · last 2026-09-20 · refs 27 · 638 chars | ask | hot and the most-referenced command; the only flag is size (top decile for commands). Keep as-is, or keep and trim? |
| 20 | **`reframe-orchestrator`** — rewrite a repo's `.claude/orchestrator.md` into an invariants-and-gates doc | command | typed 0/90d · 4 all · last 2026-06-05 · refs 0 · 260 chars · vendored in 17 repos | ask | a one-off migration run four times in June, nothing since, nothing routes to it. Retire? |
| 21 | **`screenshot-iterate`** — visual loop: implement against a mock, screenshot, compare, iterate | command | typed 0/90d · auto 0/0 · last — · refs 2 · 199 chars · vendored in 17 repos | ask | never used; the same job as row 16. Retire? |
| 22 | **`brainstorm`** — multi-mode structured brainstorm with blind agent teams and a critic gate | command | typed 0/90d · auto 5/5 · last 2026-09-16 · refs 11 · mentions 16 · 551 chars · routes→ `autonomous-milestone` (paused) | relocate | hot (5 auto picks) but oversized — earning its place, heavy enough to load on demand. Hand to `/trim-context`; no edit here. Its dangling route rides with row 11's ruling. |

### output-style

| # | Item | Surface | Evidence | Proposed | Question / why |
|---|---|---|---|---|---|
| 23 | **`adhd`** — terse, action-first output style for an ADHD reader | output-style | added 2026-08-13 · refs 2 (`skills/adhd`, `kickoff`) · 236 chars · unlinked | ask | the file is in the repo but `~/.claude/output-styles/` does not exist, so no session can load it. Link it (keep), or retire? |

### plugin

| # | Item | Surface | Evidence | Proposed | Question / why |
|---|---|---|---|---|---|
| 24 | **`swift-lsp@claude-plugins-official`** — Swift language-server plugin | plugin | auto 0/0 · last — · added 2026-05-15 · refs 0 · mentions 1 · 0 chars | retire | cold: no Swift tool call in any transcript on this machine, nothing routes to it. |
| 25 | **`mattpocock-skills@mattpocock`** — the vendored mattpocock engineering skills (`tdd`, `to-tickets`, `wayfinder`, …) | plugin | auto 220/258 · last 2026-09-20 · added 2026-08-21 · 5,303 chars | ask | hot — 220 picks this window, and it is row 1's survivor. The flag is weight: 5.3k always-loaded chars, the heaviest plugin. A plugin enables whole. Keep whole and accept the weight, or pause it between mattpocock-workflow seasons? |
| 26 | **`focus-coach@ksdisch`** — Kyle's own accountability-session plugin (`/lockin`) | plugin | auto 0/2 · last 2026-06-08 · added 2026-06-08 · refs 0 · 371 chars | ask | two picks on the day it was added, none in 104 days. Pause (disable), or keep? |
| 27 | **`claude-code-setup@claude-plugins-official`** — the automation-recommender plugin | plugin | auto 0/6 · last 2026-06-06 · added 2026-05-11 · refs 0 · 354 chars | ask | six picks in setup season (May–June), none since. Pause, or keep for the next repo you claudify? |
| 28 | **`safety-net@cc-marketplace`** — hook-based guard that blocks destructive shell commands | plugin | auto 0/0 · last — · added 2026-05-17 · refs 1 (`orchestrate`) · 71 chars | ask | it works through hooks, which tool-call counts cannot see — the zero is not evidence of disuse. Keep as a guard rail? |
| 29 | **`code-review@claude-plugins-official`** — the one-shot `/code-review:code-review` PR reviewer | plugin | auto 0/0 · last — · added 2026-05-11 · refs 7 · mentions 2 · 0 chars | ask | never invoked, but named as the one-shot alternative by `adversarial-review`, `prompt-optimize`, and five of row 1's loose copies (refs drop to 2 once row 1 lands). Keep as the named fallback, or retire and excise the references? |

### mcp

One question carries all 13 rows: each connector or server below has been silent on this machine
for 90+ days. **Remove it, or keep it?** Removal is `claude mcp remove` for a local server and the
connector deny list for a claude.ai connector. Names are withheld here; the sweep shows them.

| # | Item | Surface | Evidence | Proposed | Question / why |
|---|---|---|---|---|---|
| 30 | **`mcp #10`** — claude.ai connector; the longest silence in the set | mcp | auto 0/4 · last 2026-04-29 | ask | batch question. 144 days quiet, 4 calls ever. |
| 31 | **`mcp #11`** — local stdio server in `~/.claude.json` (the one row `claude mcp remove` applies to) | mcp | auto 0/11 · last 2026-06-05 · mentions 2 | ask | batch question. 11 calls ever. |
| 32 | **`mcp #13`** — claude.ai connector | mcp | auto 0/11 · last 2026-05-27 | ask | batch question. |
| 33 | **`mcp #19`** — claude.ai connector, already on the deny list | mcp | auto 0/1 · last 2026-06-05 · denied | ask | already denied, so it steers nothing today; "retire" here means dropping the connector itself. |
| 34 | **`mcp #1`** — claude.ai connector; 150 calls before June, none since | mcp | auto 0/150 · last 2026-06-04 | ask | batch question. |
| 35 | **`mcp #23`** — claude.ai connector | mcp | auto 0/24 · last 2026-06-02 | ask | batch question. |
| 36 | **`mcp #32`** — claude.ai connector | mcp | auto 0/12 · last 2026-06-05 | ask | batch question. |
| 37 | **`mcp #3`** — claude.ai connector; the busiest of the quiet set (660 calls all-time) | mcp | auto 0/660 · last 2026-05-02 | ask | batch question. 141 days quiet. |
| 38 | **`mcp #4`** — claude.ai connector | mcp | auto 0/4 · last 2026-05-27 | ask | batch question. |
| 39 | **`mcp #5`** — claude.ai connector | mcp | auto 0/34 · last 2026-06-05 | ask | batch question. |
| 40 | **`mcp #7`** — claude.ai connector | mcp | auto 0/3 · last 2026-05-17 | ask | batch question. |
| 41 | **`mcp #8`** — claude.ai connector | mcp | auto 0/16 · last 2026-06-02 | ask | batch question. |
| 42 | **`mcp #9`** — claude.ai connector | mcp | auto 0/1 · last 2026-06-01 | ask | batch question. |

### hook

| # | Item | Surface | Evidence | Proposed | Question / why |
|---|---|---|---|---|---|
| 43 | **4 hook entries commented out** — two `Notification` and two `Stop` entries left as comments in `~/.claude/settings.json` | hook | 4 items · 0 chars · untracked file | retire | mechanical: comment-only entries steer nothing. An untracked-settings edit — one per-file confirmation showing the exact edit list, with a dated backup first. |

### memory

| # | Item | Surface | Evidence | Proposed | Question / why |
|---|---|---|---|---|---|
| 44 | **32 empty auto-memory directories** — per-project `memory/` folders under `~/.claude/projects/`, all left by throwaway temp-dir sessions | memory | 32 items · 0 chars · all 32 from `/var/folders/…` working dirs | retire | mechanical: empty directories. Backed up to a dated folder, then `mv` — never `rm -rf`. |

### claude-md

| # | Item | Surface | Evidence | Proposed | Question / why |
|---|---|---|---|---|---|
| 45 | **`Local-Markdown Issue Tracker: Tickets Index (added 2026-08-22)`** — the global rule for the generated `tickets.md` manifest beside `.scratch/<slug>/issues/` | claude-md | trig 31/31 · last 2026-09-20 · 4,086 chars | ask | fires constantly (31 hits, the latest today) — it earns its place. The flag is 4.1k chars in every prompt, the heaviest section in the file. Keep as-is, or `relocate` the body (table example, wayfinder and scaffolding caveats) to a doc and leave a pointer? |
| 46 | **`New Feature Mode`** — the "feature mode" interview-before-building convention | claude-md | trig 0/0 · last — · added 2026-06-08 · refs 2 (`kickoff`, the Stop hook) · 767 chars | ask | its trigger phrases never appear in 5,474 prompts. Retire, or keep as a mode you still intend to use? |
| 47 | **`Improvement Mode`** — the "improvement mode" diagnose-before-fixing convention | claude-md | trig 0/0 · last — · added 2026-06-08 · refs 1 (the Stop hook) · 717 chars | ask | 0 hits ever (matches the design spec's hand check). Retire, or keep? |

### Omitted from this table

The next section lists them by precedence row. In short: 0 kept rulings (the ledger is empty),
2 recently paused (`autonomous-milestone`, `learn`), 53 `new` items with nothing else against
them, 36 silent hot/warm keeps, and 17 unmeasured (the operating-constraint sections, the live
hook entries, and one MCP server). The 19 `auto_only` names — reached for by sessions, never
typed — are listed there too; they change no proposal but are worth knowing.

## Omitted from the proposals

Each line is one row of the precedence table doing its job. Names are listed except for the silent keeps, which are counted, and for surfaces whose names are private.

- **kept** — ruled keep on purpose, recorded in the ledger — 0
- **paused-recent** — paused less than a window ago — 2: `autonomous-milestone`, `learn`
- **new** — added inside the window, nothing else against it — 53: `Format rules`, `Never show me a bare identifier (added 2026-08-13)`, `Planner/Builder Protocol (added 2026-07-27)`, `Project Wiki`, `Reference Doc Maintenance`, `When to update`, `adhd`, `adversarial-reviewer`, `catchup`, `cc-yt-idea-mine`, `claude-md-management@claude-plugins-official`, `code-simplifier@claude-plugins-official`, `context7@claude-plugins-official`, `crap-check`, `family-compare`, `feature-dev@claude-plugins-official`, `find-skills`, `frontend-design@claude-plugins-official`, `gauntlet`, `gauntlet-coder`, `github@claude-plugins-official`, `handoff-session`, `interview-prep`, `mock-call`, `mutation-hardener`, `narrate`, `notebook-merge`, `onboard`, `orchestrate`, `paper-figures`, `playwright@claude-plugins-official`, `project-guide`, `project-wiki`, `ralph-loop@claude-plugins-official`, `replenish`, `research-paper`, `retire`, `review-judge`, `seed-hunt`, `silent-failure-hunter`, `skill-creator@claude-plugins-official`, `spec-miner`, `specifier`, `superpowers@claude-plugins-official`, `tdd-loop`, `teach-research`, `video-series`, `visual-summary`, `warp@claude-code-warp`, `wiki-backfill`, `wiki-init`, `youtube-breakdown`, `youtube-transcript`
- **hot-warm** — used inside the window — 36
- **unmeasured** — no source could score it; nothing here is evidence of disuse — 17: `Act vs. assess`, `Clarifying questions and option formatting`, `Decisiveness`, `Finish the turn`, `Git Workflow`, `No false progress`, `PreToolUse[0][0]`, `PreToolUse[0][1]`, `PreToolUse[1][0]`, `Scope discipline`, `SessionEnd[0][0]`, `Stop[0][0]`, `Track multi-step work`, `Unattended runs only`, `UserPromptSubmit[0][0]`, `UserPromptSubmit[1][0]` (+1 on a surface whose names are private)
- **auto_only** — never typed, but sessions keep choosing it (evidence, not a verdict) — 19: `adversarial-review`, `audio-series`, `autonomous-milestone`, `brainstorm`, `bug-hunt`, `code-review`, `codebase-design`, `domain-modeling`, `explore-plan`, `grilling`, `handoff-session`, `kickoff`, `narrate`, `notebook-init`, `portfolio-notebook-sync`, `project-wiki`, `tdd`, `writing-for-agents`, `youtube-transcript`

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
| `adversarial-review` | typed 0/90d · 0 all · auto 161/161 · trig 44/46 · last 2026-09-19 · added 2026-07-26 · edited 2026-08-27 · refs 12 · mentions 14 · 1,528 chars | auto_only, oversized | new | ask |
| `paper-gloss` | typed 4/90d · 4 all · auto 3/3 · trig 0/0 · last 2026-08-24 · added 2026-07-23 · edited 2026-07-29 · refs 3 · mentions 6 · 1,426 chars · vendored in blind-cite | oversized | new | ask |
| `paper-eli5` | typed 1/90d · 1 all · auto 3/3 · trig 0/0 · last 2026-08-04 · added 2026-07-19 · edited 2026-07-28 · refs 5 · mentions 3 · 1,351 chars | oversized | new | ask |
| `architecture-viewer` | typed 0/90d · 0 all · auto 1/1 · trig 1/1 · last 2026-08-23 · added 2026-08-20 · edited 2026-08-20 · refs 1 · mentions 5 · 1,195 chars | oversized | new | ask |
| `bug-hunt` | typed 0/90d · 0 all · auto 7/7 · trig 0/0 · last 2026-08-13 · added 2026-06-26 · edited 2026-07-27 · refs 8 · mentions 6 · 1,192 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | auto_only, oversized | new | ask |
| `curriculum-sync` | typed 0/90d · 0 all · auto 0/0 · trig 0/0 · last — · added 2026-08-07 · edited 2026-08-07 · refs 0 · mentions 1 · 1,134 chars | oversized | new | ask |
| `career-coach` | typed 0/90d · 0 all · auto 2/2 · trig 1/1 · last 2026-08-20 · added 2026-07-23 · edited 2026-07-23 · refs 0 · mentions 0 · 1,133 chars | oversized | new | ask |
| `reweave` | typed 4/90d · 4 all · auto 2/2 · trig 3/3 · last 2026-09-14 · added 2026-07-21 · edited 2026-07-21 · refs 0 · mentions 2 · 1,069 chars | oversized | new | ask |
| `research-paper` | typed 1/90d · 1 all · auto 4/4 · trig 0/0 · last 2026-08-05 · added 2026-07-17 · edited 2026-08-03 · refs 2 · mentions 1 · 919 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | new | — |
| `youtube-breakdown` | typed 0/90d · 1 all · auto 0/0 · trig 0/1 · last 2026-06-09 · added 2026-08-20 · edited 2026-08-20 · refs 2 · mentions 1 · 840 chars · vendored in home-base | — | new | — |
| `family-compare` | typed 0/90d · 0 all · auto 0/0 · trig 2/2 · last 2026-09-19 · added 2026-09-18 · edited 2026-09-19 · refs 0 · mentions 1 · 837 chars | — | new | — |
| `visual-summary` | typed 0/90d · 0 all · auto 0/0 · trig 1/1 · last 2026-09-19 · added 2026-09-18 · edited 2026-09-19 · refs 0 · mentions 0 · 823 chars | — | new | — |
| `paper-figures` | typed 0/90d · 0 all · auto 0/0 · trig 0/0 · last — · added 2026-07-27 · edited 2026-07-29 · refs 3 · mentions 3 · 812 chars | — | new | — |
| `gauntlet` | typed 0/90d · 0 all · auto 1/1 · trig 0/0 · last 2026-08-21 · added 2026-08-20 · edited 2026-08-20 · refs 4 · mentions 11 · 789 chars | — | new | — |
| `orchestrate` | typed 0/90d · 0 all · auto 3/3 · trig 0/0 · last 2026-09-17 · added 2026-09-07 · edited 2026-09-08 · refs 4 · mentions 2 · 785 chars | — | new | — |
| `onboard` | typed 0/90d · 0 all · auto 3/3 · trig 0/1 · last 2026-09-18 · added 2026-08-03 · edited 2026-08-22 · refs 2 · mentions 2 · 784 chars | — | new | — |
| `cc-yt-idea-mine` | typed 1/90d · 1 all · auto 4/4 · trig 0/0 · last 2026-08-22 · added 2026-08-20 · edited 2026-08-21 · refs 2 · mentions 36 · 776 chars | — | new | — |
| `project-guide` | typed 3/90d · 3 all · auto 1/1 · trig 5/5 · last 2026-07-06 · added 2026-06-28 · edited 2026-07-06 · refs 6 · mentions 6 · 737 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | new | — |
| `seed-hunt` | typed 1/90d · 1 all · auto 3/3 · trig 1/1 · last 2026-08-21 · added 2026-07-06 · edited 2026-08-21 · refs 2 · mentions 1 · 704 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | new | — |
| `backlog-hygiene` | typed 1/90d · 1 all · auto 19/19 · trig 19/20 · last 2026-09-19 · added 2026-07-19 · edited 2026-08-21 · refs 8 · mentions 3 · 697 chars · routes→ autonomous-milestone | dangling | new | ask |
| `notebook-merge` | typed 3/90d · 3 all · auto 0/0 · trig 3/3 · last 2026-07-14 · added 2026-07-13 · edited 2026-07-13 · refs 1 · mentions 1 · 692 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | new | — |
| `video-series` | typed 1/90d · 1 all · auto 0/0 · trig 73/82 · last 2026-09-19 · added 2026-07-11 · edited 2026-07-13 · refs 3 · mentions 3 · 687 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | new | — |
| `adhd` | typed 0/90d · 0 all · auto 0/0 · trig 16/40 · last 2026-09-12 · added 2026-08-01 · edited 2026-08-01 · refs 1 · mentions 3 · 668 chars | — | new | — |
| `replenish` | typed 1/90d · 1 all · auto 0/0 · trig 10/10 · last 2026-09-12 · added 2026-07-19 · edited 2026-07-19 · refs 2 · mentions 2 · 657 chars | — | new | — |
| `mock-call` | typed 0/90d · 0 all · auto 0/0 · trig 1/1 · last 2026-09-17 · added 2026-09-17 · edited 2026-09-17 · refs 0 · mentions 2 · 651 chars | — | new | — |
| `reorient` | typed 1/90d · 1 all · auto 1/1 · trig 1/1 · last 2026-08-03 · added 2026-07-19 · edited 2026-07-19 · refs 2 · mentions 2 · 625 chars · routes→ autonomous-milestone | dangling | new | ask |
| `teach-research` | typed 1/90d · 1 all · auto 0/0 · trig —/— · last 2026-08-17 · added 2026-08-17 · edited 2026-08-17 · refs 2 · mentions 1 · 620 chars | — | new | — |
| `retire` | typed 1/90d · 1 all · auto 0/0 · trig 0/0 · last 2026-09-20 · added 2026-09-18 · edited 2026-09-18 · refs 4 · mentions 6 · 599 chars | — | new | — |
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
| `wayfinder` | typed 3/90d · 3 all · auto 1/1 · trig —/— · last 2026-09-20 · added 2026-08-21 · edited 2026-08-21 · refs 7 · mentions 4 · 197 chars · dup of `mattpocock-skills:wayfinder` | duplicate | new | retire |
| `setup-ts-deep-modules` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-08-21 · edited 2026-08-21 · refs 0 · mentions 0 · 185 chars · dup of `mattpocock-skills:setup-ts-deep-modules` | duplicate | new | retire |
| `setup-matt-pocock-skills` | typed 7/90d · 7 all · auto 1/1 · trig —/— · last 2026-09-18 · added 2026-08-21 · edited 2026-08-21 · refs 7 · mentions 0 · 180 chars · dup of `mattpocock-skills:setup-matt-pocock-skills` | duplicate | new | retire |
| `prototype` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-08-21 · edited 2026-08-21 · refs 11 · mentions 2 · 179 chars · dup of `mattpocock-skills:prototype` | duplicate | new | retire |
| `migrate-to-shoehorn` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-08-21 · edited 2026-08-21 · refs 0 · mentions 0 · 168 chars · dup of `mattpocock-skills:migrate-to-shoehorn` | duplicate | new | retire |
| `diagnosing-bugs` | typed 0/90d · 0 all · auto 0/0 · trig 5/11 · last 2026-08-22 · added 2026-08-21 · edited 2026-08-21 · refs 1 · mentions 0 · 156 chars · dup of `mattpocock-skills:diagnosing-bugs` | duplicate | new | retire |
| `grilling` | typed 0/90d · 0 all · auto 22/22 · trig —/— · last 2026-09-20 · added 2026-08-21 · edited 2026-08-21 · refs 15 · mentions 5 · 152 chars · dup of `mattpocock-skills:grilling` | duplicate, auto_only | new | retire |
| `domain-modeling` | typed 0/90d · 0 all · auto 23/23 · trig —/— · last 2026-09-20 · added 2026-08-21 · edited 2026-08-21 · refs 6 · mentions 4 · 150 chars · dup of `mattpocock-skills:domain-modeling` | duplicate, auto_only | new | retire |
| `tdd` | typed 0/90d · 0 all · auto 21/21 · trig 0/0 · last 2026-09-17 · added 2026-08-21 · edited 2026-08-21 · refs 4 · mentions 6 · 149 chars · dup of `mattpocock-skills:tdd` | duplicate, auto_only | new | retire |
| `to-spec` | typed 3/90d · 3 all · auto 5/5 · trig —/— · last 2026-09-18 · added 2026-08-21 · edited 2026-08-21 · refs 2 · mentions 3 · 149 chars · dup of `mattpocock-skills:to-spec` | duplicate | new | retire |
| `triage` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-08-21 · edited 2026-08-21 · refs 19 · mentions 4 · 136 chars · dup of `mattpocock-skills:triage` | duplicate | new | retire |
| `improve-codebase-architecture` | typed 4/90d · 4 all · auto 0/0 · trig —/— · last 2026-08-22 · added 2026-08-21 · edited 2026-08-21 · refs 2 · mentions 1 · 125 chars · dup of `mattpocock-skills:improve-codebase-architecture` | duplicate | new | retire |
| `writing-beats` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-08-21 · edited 2026-08-21 · refs 0 · mentions 0 · 111 chars · dup of `mattpocock-skills:writing-beats` | duplicate | new | retire |
| `grill-with-docs` | typed 9/90d · 9 all · auto 3/3 · trig —/— · last 2026-09-18 · added 2026-08-21 · edited 2026-08-21 · refs 3 · mentions 4 · 106 chars · dup of `mattpocock-skills:grill-with-docs` | duplicate | new | retire |
| `writing-for-agents` | typed 0/90d · 0 all · auto 6/6 · trig —/— · last 2026-09-19 · added 2026-08-21 · edited 2026-08-21 · refs 1 · mentions 0 · 103 chars · dup of `mattpocock-skills:writing-for-agents` | duplicate, auto_only | new | retire |
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
| `grill-me` | typed 3/90d · 3 all · auto 0/0 · trig —/— · last 2026-08-13 · added 2026-08-21 · edited 2026-08-21 · refs 2 · mentions 1 · 51 chars · dup of `mattpocock-skills:grill-me` | duplicate | new | retire |
| `wait-what` | typed 12/90d · 12 all · auto 0/0 · trig —/— · last 2026-08-25 · added 2026-08-21 · edited 2026-08-21 · refs 1 · mentions 3 · 50 chars · dup of `mattpocock-skills:wait-what` | duplicate | new | retire |
| `implement-spec` | typed 1/90d · 1 all · auto 0/0 · trig —/— · last 2026-09-18 · added 2026-08-21 · edited 2026-08-21 · refs 1 · mentions 2 · 34 chars · dup of `mattpocock-skills:implement-spec` | duplicate | new | retire |
| `ship-and-route` | typed 1/90d · 2 all · auto 1/7 · trig 0/1 · last 2026-07-20 · added 2026-06-09 · edited 2026-08-22 · refs 8 · mentions 7 · 793 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | warm | — |
| `kickoff` | typed 0/90d · 1 all · auto 12/12 · trig 1/2 · last 2026-08-21 · added 2026-06-08 · edited 2026-07-24 · refs 9 · mentions 6 · 760 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | auto_only | hot | — |
| `audio-series` | typed 0/90d · 2 all · auto 5/6 · trig 73/88 · last 2026-09-19 · added 2026-06-08 · edited 2026-08-01 · refs 6 · mentions 4 · 615 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | auto_only | hot | — |
| `notebook-init` | typed 0/90d · 2 all · auto 5/6 · trig —/— · last 2026-08-01 · added 2026-06-08 · edited 2026-06-08 · refs 6 · mentions 4 · 205 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | auto_only | hot | — |

## command

| Item | Evidence | Flags | Temp | Proposed |
|---|---|---|---|---|
| `reframe-orchestrator` | typed 0/90d · 4 all · auto 0/0 · trig —/— · last 2026-06-05 · added 2026-06-08 · edited 2026-06-23 · refs 0 · mentions 1 · 260 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool | ask |
| `screenshot-iterate` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-06-08 · edited 2026-06-23 · refs 2 · mentions 0 · 199 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | cool | ask |
| `launch` | typed 8/90d · 8 all · auto 48/48 · trig 0/0 · last 2026-09-20 · added 2026-08-10 · edited 2026-08-21 · refs 27 · mentions 9 · 638 chars | oversized | new | ask |
| `handoff-session` | typed 0/90d · 0 all · auto 19/19 · trig —/— · last 2026-09-19 · added 2026-09-17 · edited 2026-09-09 · refs 9 · mentions 1 · 509 chars | auto_only | new | — |
| `wiki-backfill` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-07-26 · edited 2026-07-26 · refs 2 · mentions 0 · 332 chars | — | new | — |
| `wiki-init` | typed 0/90d · 0 all · auto 1/1 · trig —/— · last 2026-07-26 · added 2026-07-24 · edited 2026-07-26 · refs 3 · mentions 0 · 315 chars | — | new | — |
| `crap-check` | typed 0/90d · 0 all · auto 0/0 · trig 1/1 · last 2026-09-09 · added 2026-08-27 · edited 2026-08-27 · refs 1 · mentions 4 · 314 chars | — | new | — |
| `tdd-loop` | typed 0/90d · 0 all · auto 0/0 · trig —/— · last — · added 2026-08-21 · edited 2026-08-21 · refs 3 · mentions 2 · 218 chars | — | new | — |
| `catchup` | typed 2/90d · 2 all · auto 0/0 · trig —/— · last 2026-07-06 · added 2026-07-06 · edited 2026-07-06 · refs 3 · mentions 1 · 214 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | new | — |
| `autonomous-milestone` | typed 0/90d · 25 all · auto 6/8 · trig —/— · last 2026-08-19 · added 2026-08-27 · edited 2026-08-27 · refs 6 · mentions 5 · 0 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | paused, auto_only | new | — |
| `learn` | typed 0/90d · 0 all · auto 1/1 · trig —/— · last 2026-08-21 · added 2026-08-21 · edited 2026-08-21 · refs 15 · mentions 2 · 0 chars | paused | new | — |
| `smoke-test` | typed 0/90d · 1 all · auto 2/3 · trig —/— · last 2026-07-19 · added 2026-06-12 · edited 2026-06-12 · refs 1 · mentions 7 · 367 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | warm | — |
| `claudify-repo` | typed 0/90d · 6 all · auto 1/1 · trig —/— · last 2026-07-18 · added 2026-06-08 · edited 2026-08-21 · refs 2 · mentions 9 · 313 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | warm | — |
| `trim-context` | typed 0/90d · 6 all · auto 1/2 · trig 0/2 · last 2026-07-20 · added 2026-06-08 · edited 2026-06-23 · refs 4 · mentions 7 · 306 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | warm | — |
| `envsetup` | typed 0/90d · 0 all · auto 1/1 · trig —/— · last 2026-07-06 · added 2026-06-08 · edited 2026-06-08 · refs 0 · mentions 3 · 159 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | warm | — |
| `brainstorm` | typed 0/90d · 1 all · auto 5/5 · trig —/— · last 2026-09-16 · added 2026-06-08 · edited 2026-07-27 · refs 11 · mentions 16 · 551 chars · vendored in DogHood, blind-cite, buoy-legal +14 more · routes→ autonomous-milestone | auto_only, dangling, oversized | hot | relocate |
| `prompt-optimize` | typed 3/90d · 4 all · auto 4/4 · trig —/— · last 2026-09-18 · added 2026-06-08 · edited 2026-08-21 · refs 4 · mentions 6 · 312 chars · vendored in DogHood, blind-cite, buoy-legal +14 more · routes→ autonomous-milestone | dangling | hot | — |
| `begin` | typed 2/90d · 24 all · auto 13/15 · trig —/— · last 2026-09-16 · added 2026-06-08 · edited 2026-06-30 · refs 7 · mentions 6 · 243 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | hot | — |
| `explore-plan` | typed 0/90d · 0 all · auto 12/12 · trig —/— · last 2026-09-08 · added 2026-06-08 · edited 2026-06-23 · refs 3 · mentions 3 · 214 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | auto_only | hot | — |
| `boot_server` | typed 3/90d · 6 all · auto 7/8 · trig —/— · last 2026-09-09 · added 2026-06-08 · edited 2026-06-08 · refs 1 · mentions 3 · 201 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | hot | — |
| `wrap` | typed 5/90d · 13 all · auto 1/27 · trig —/— · last 2026-07-06 · added 2026-06-08 · edited 2026-06-30 · refs 18 · mentions 10 · 193 chars · vendored in DogHood, blind-cite, buoy-legal +14 more | — | hot | — |

## agent

| Item | Evidence | Flags | Temp | Proposed |
|---|---|---|---|---|
| `spec-miner` | typed —/90d · — all · auto 0/0 · trig —/— · last — · added 2026-07-27 · edited 2026-08-21 · refs 1 · mentions 4 · 715 chars | — | new | — |
| `mutation-hardener` | typed —/90d · — all · auto 0/0 · trig —/— · last — · added 2026-08-20 · edited 2026-08-20 · refs 1 · mentions 2 · 675 chars | — | new | — |
| `silent-failure-hunter` | typed —/90d · — all · auto 1/1 · trig —/— · last 2026-07-28 · added 2026-07-27 · edited 2026-07-27 · refs 3 · mentions 4 · 675 chars | — | new | — |
| `specifier` | typed —/90d · — all · auto 1/1 · trig —/— · last 2026-08-21 · added 2026-08-20 · edited 2026-08-20 · refs 2 · mentions 5 · 543 chars | — | new | — |
| `adversarial-reviewer` | typed —/90d · — all · auto 600/600 · trig —/— · last 2026-09-19 · added 2026-07-26 · edited 2026-07-27 · refs 4 · mentions 5 · 520 chars | — | new | — |
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
| `mattpocock-skills@mattpocock` | typed —/90d · — all · auto 220/258 · trig —/— · last 2026-09-20 · added 2026-08-21 · edited — · refs 0 · mentions 2 · 5,303 chars | oversized | new | ask |
| `superpowers@claude-plugins-official` | typed —/90d · — all · auto 125/125 · trig —/— · last 2026-09-19 · added 2026-06-23 · edited — · refs 3 · mentions 10 · 1,965 chars | — | new | — |
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
| `mcp #14` | typed —/90d · — all · auto 754/754 · trig —/— · last 2026-09-19 · added — · edited — · refs 0 · mentions 2 · 0 chars | connector_only | hot | — |
| `mcp #16` | typed —/90d · — all · auto 476/485 · trig —/— · last 2026-09-19 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | hot | — |
| `mcp #17` | typed —/90d · — all · auto 543/571 · trig —/— · last 2026-09-20 · added — · edited — · refs 0 · mentions 0 · 0 chars | connector_only | hot | — |
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
| `mcp #33` | typed —/90d · — all · auto 1421/1468 · trig —/— · last 2026-09-20 · added — · edited — · refs 3 · mentions 2 · 0 chars | — | hot | — |

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
| `Improvement Mode` | typed —/90d · — all · auto —/— · trig 0/0 · last — · added 2026-06-08 · edited — · refs 1 · mentions 2 · 717 chars | — | cool | ask |
| `Local-Markdown Issue Tracker: Tickets Index (added 2026-08-22)` | typed —/90d · — all · auto —/— · trig 31/31 · last 2026-09-20 · added 2026-08-22 · edited — · refs 0 · mentions 0 · 4,086 chars | oversized | new | ask |
| `Reference Doc Maintenance` | typed —/90d · — all · auto —/— · trig 14/15 · last 2026-09-19 · added 2026-07-23 · edited — · refs 0 · mentions 1 · 3,696 chars | — | new | — |
| `Never show me a bare identifier (added 2026-08-13)` | typed —/90d · — all · auto —/— · trig 31/42 · last 2026-09-18 · added 2026-08-13 · edited — · refs 0 · mentions 0 · 3,121 chars | — | new | — |
| `Planner/Builder Protocol (added 2026-07-27)` | typed —/90d · — all · auto —/— · trig 13/14 · last 2026-09-09 · added 2026-07-27 · edited — · refs 0 · mentions 0 · 2,637 chars | — | new | — |
| `When to update` | typed —/90d · — all · auto —/— · trig —/— · last — · added 2026-07-23 · edited — · refs 0 · mentions 0 · 2,277 chars | — | new | — |
| `Project Wiki` | typed —/90d · — all · auto —/— · trig 37/38 · last 2026-08-22 · added 2026-07-24 · edited — · refs 2 · mentions 0 · 749 chars · vendored in DogHood, bandmark, blind-cite +20 more | — | new | — |
| `Format rules` | typed —/90d · — all · auto —/— · trig —/— · last — · added 2026-07-23 · edited — · refs 1 · mentions 0 · 562 chars | — | new | — |
| ``Kickoff Mode → run the `/kickoff` skill`` | typed —/90d · — all · auto —/— · trig 1/3 · last 2026-08-01 · added 2026-06-08 · edited — · refs 0 · mentions 0 · 771 chars | — | warm | — |
| `Git Workflow` | typed —/90d · — all · auto —/— · trig —/— · last — · added 2026-06-08 · edited — · refs 9 · mentions 9 · 4,004 chars | oversized | unknown | — |
| `Track multi-step work` | typed —/90d · — all · auto —/— · trig —/— · last — · added 2026-06-18 · edited — · refs 0 · mentions 0 · 681 chars | — | unknown | — |
| `Clarifying questions and option formatting` | typed —/90d · — all · auto —/— · trig —/— · last — · added 2026-06-08 · edited — · refs 0 · mentions 0 · 399 chars | — | unknown | — |
| `Unattended runs only` | typed —/90d · — all · auto —/— · trig —/— · last — · added 2026-06-18 · edited — · refs 0 · mentions 0 · 362 chars · routes→ autonomous-milestone | dangling | unknown | — |
| `Scope discipline` | typed —/90d · — all · auto —/— · trig —/— · last — · added 2026-06-18 · edited — · refs 2 · mentions 1 · 359 chars | — | unknown | — |
| `Act vs. assess` | typed —/90d · — all · auto —/— · trig —/— · last — · added 2026-06-18 · edited — · refs 1 · mentions 0 · 353 chars | — | unknown | — |
| `Finish the turn` | typed —/90d · — all · auto —/— · trig —/— · last — · added 2026-06-18 · edited — · refs 1 · mentions 0 · 251 chars | — | unknown | — |
| `No false progress` | typed —/90d · — all · auto —/— · trig —/— · last — · added 2026-06-18 · edited — · refs 1 · mentions 0 · 240 chars | — | unknown | — |
| `Decisiveness` | typed —/90d · — all · auto —/— · trig —/— · last — · added 2026-06-18 · edited — · refs 1 · mentions 0 · 239 chars | — | unknown | — |
