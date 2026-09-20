# `retire` skill — design

**Status:** Approved design, 2026-09-17. Kyle approved every recommended default in the
brainstorm (nine decisions, recorded in §4). Implementation plan:
[`docs/plans/2026-09-17-retire-skill.md`](../../plans/2026-09-17-retire-skill.md).
**Amended 2026-09-18** by a `/grill-with-docs` pass (23 rulings, §14). The implementation-facing spec is
[`.scratch/retire-skill/spec.md`](../../../.scratch/retire-skill/spec.md); where §5–§7 below disagree with it or with §14, the spec wins.
**Ancestor:** [`docs/ideas/coliseum-commands-earn-their-keep.md`](../../ideas/coliseum-commands-earn-their-keep.md)
(2026-06-18) — this skill is that idea built; it also absorbs
[`docs/ideas/minimal-initial-prompt.md`](../../ideas/minimal-initial-prompt.md) as its CLAUDE.md lane.

## 1. Problem

The config has no subtract verb. Every item in `~/.claude` was added for a reason, but nothing
has a removal path, so the library only grows and old intent keeps steering new sessions. Every
past removal was a manual one-off: the memory prune (2026-08-23), the mattpocock fork retirement
(08-21), the `/learn` and `/autonomous-milestone` disables (08-21, 08-27), the connector prune
(08-22). `/trim-context` explicitly never deletes a rule; it relocates.

"Steering" is two problems in one coat:

- **Behavioral steering** — an item changes how sessions interpret asks, route to skills, plan,
  or build. A 300-char skill description whose trigger phrases hijack routing is a steering
  problem at trivial token cost.
- **Token weight** — always-loaded bytes paid on every request. A never-triggered CLAUDE.md
  section is weight with no steering.

A third goal hides in "I know this is broad": Kyle can no longer see the whole steering surface.
An inventory that names every item with evidence is valuable before anything is deleted.

## 2. Goals and non-goals

**Goals (v1)**

1. Inventory every global steering surface with evidence attached (usage, weight, referrers).
2. Propose retire/keep verdicts that Kyle ratifies; nothing is removed before ratification.
3. Apply ratified retirements with complete bookkeeping so nothing dangles: files, index row,
   playbook card, referrers, `.gitignore` blocks, settings entries, ledger.
4. Make every removal reversible: a ledger line with a restore pointer, and a backup tarball for
   anything untracked.
5. Measure before → after always-loaded weight.

**Secondary benefits** (not separately built, but the design serves them): routing precision
(fewer mis-fires like `/learn` vs `/teach`), contradiction removal (dangling routes, stale hook
prompts), a ruling record so retired items aren't re-proposed, and a downstream blast-radius
report for the public vendored copies.

**Non-goals (v1)** — see §12 for the v2 lanes:

- Editing any project repo: per-project `CLAUDE.md`, vendored `.claude/` copies. Report only.
- Re-litigating the harness disable ruling (`docs/ideas/harness-disable-ruling.md`, keep-all-eight)
  or the connector prune (already applied).
- `basic-memory` MCP notes (11 invocations ever; not a steering surface).
- Relocating content that should stay but load on demand — that is `/trim-context`'s job;
  `retire` hands those verdicts to it.
- Any daemon, hook, or scheduled run. On-demand only.

## 3. Evidence snapshot (2026-09-17)

What is always loaded today, measured on the live setup. The inventory script (§7) reproduces
every number; the recipe column is what it automates.

| Surface | Measured | Recipe |
|---|---|---|
| Global `CLAUDE.md` + `@operating-constraints.md` | 24,033 chars | `wc -c` |
| Skill descriptions in `skills/` (79 dirs) | 34,108 chars | frontmatter `description:` per `SKILL.md` |
| Plugin skill descriptions (67 skills, 19 plugins) | 11,154 chars | same, over `~/.claude/plugins/cache` |
| Mattpocock skills listed twice per session | 36 | `skills/<x>` untracked copies ∩ plugin skill names |
| Commands / agents | 20 live + 2 `.disabled` / 7 | `ls` |
| Largest per-project `CLAUDE.md` | stopwatch 38,651; hush-gauge 31,223 | `wc -c` |
| Project repos carrying vendored global kit | 16 | `ls ~/Projects/*/.claude/{skills,commands}` |
| Usage corpus | 5,398 prompts in `history.jsonl`; 6,110 transcripts (3.1 GB) | `~/.claude/history.jsonl`, `~/.claude/projects/**/*.jsonl` |

Findings the sweep surfaced by hand — the kind of verdict the skill must produce:

- **Improvement Mode and New Feature Mode have never been triggered.** 0 hits in all prompt
  history. Kickoff Mode: 2 hits, last 2026-08-01. All three sit at the top of every session's
  CLAUDE.md and the Stop-hook prompt names them.
- **The mattpocock skills load twice.** Untracked `npx skills` copies in `skills/` and the
  enabled `mattpocock-skills` plugin both appear, so every session sees `tdd` and
  `mattpocock-skills:tdd`.
- **Dangling routes survive retirement.** Five files still route to the disabled
  `/autonomous-milestone`: `backlog-hygiene`, `reorient`, `replenish`, `/brainstorm`,
  `/prompt-optimize`.
- **Four disabled sound hooks remain in `settings.json`** as comment-only commands (Stop ×2,
  Notification ×2).
- **Memory is already mostly clean.** `autoMemoryEnabled: false`; one 2-line file survived the
  August prune; ~30 empty `memory/` dirs remain under temp-project slugs.
- **Usage evidence is cheap and rich.** Skill invocations all-time: adversarial-review 158,
  handoff 122, project-wiki 60, launch 47, code-review 44. Slash commands typed: `/handoff` 79,
  `/begin` 24, `/implement` 24, `/wrap` 13, `/trim-context` 6.
- **Zero referrers ≠ unused.** 19 skills are named by no other file, but `reweave` is one and
  has 11 history hits. Verdicts need several signals; no single count decides.
- **MCP usage (all-time tool calls):** kapture 2,635; todoist 1,375; notebooklm-mcp 1,307;
  claude-in-chrome 712; MCP_DOCKER 512 (currently failing to connect); basic-memory 11. Three
  browser automators coexist (kapture, claude-in-chrome, playwright plugin).

## 4. Decisions

Each is the brainstorm question, the option chosen, and why. IDs are for cross-reference from
the plan; the title is the gloss.

| ID | Decision | Choice | Why |
|---|---|---|---|
| D1 | What "memories" means | `CLAUDE.md` files + Claude Code auto-memory dirs. `basic-memory` out of scope. | Auto-memory is off and nearly empty; CLAUDE.md is what Claude Code itself calls memory; basic-memory is a note store, not steering. |
| D2 | Surfaces in scope for v1 | Global only: claude-config files, `settings.json`, plugins, MCP servers, hooks, output styles, memory dirs. Fleet is report-only. | Bookkeeping, git workflow, and undo all live in claude-config. Project repos carry landmines (DogHood's single-line command list; 13 public repos). |
| D3 | Evidence standard | Hybrid: the script ranks a shortlist by evidence; the interview covers only the ambiguous middle. 90-day window, all-time last-used shown alongside. | Evidence beats recall (Coliseum bet), but one-user counts are small, so rare-but-load-bearing items need a human. |
| D4 | Act or propose | Apply on branch + PR for claude-config-owned files under the standing git workflow. `settings.json`, `~/.claude.json`, plugin toggles wait for Kyle's word per item. Nothing touches a project repo. | Tracked files are reversible via git and gated by review; untracked settings are not, and the repo is public. |
| D5 | Retire, disable, or delete | Delete outright; git history is the archive; one ledger line per item in `docs/retired.md`. `.md.disabled` is reserved for "paused, likely coming back". | A pile of disabled files and banner cards is its own cruft. Changes the convention for the two existing `.disabled` commands — they become pilot candidates, ruled by Kyle. |
| D6 | Audit rules inside CLAUDE.md | Yes, as a separate propose-only lane; Kyle rules per section. Evidence: trigger-phrase hits in history, referrers, hook-convertibility. | Highest-judgment lane; folds in the minimal-initial-prompt backlog item. |
| D7 | Which mattpocock copy to keep | The plugin. Retire the 36 untracked `skills/` copies and their `.gitignore` block. Verify bare `/tdd` still resolves before applying. | Plugin self-updates and is namespaced. This is the pilot's first live target. |
| D8 | Name and shape | Skill `retire`, two modes: **sweep** (`/retire`) audits everything; **targeted** (`/retire <item>…`) does full bookkeeping for named items. `--report` runs sweep read-only. | A verb, pairs with `replenish`/`reorient`; targeted mode makes future one-off removals cheap and complete. |
| D9 | One-off or repeatable | Repeatable. A Python script owns inventory and counting; prose owns judgment. The script is an **Instrument** (CONTEXT.md vocabulary), never a Gate. | Hand-counting produced two false cleans in the July fleet sweep; a script that fails loudly can't fail into a passing result. |

## 5. Skill design

### 5.1 Invocation and modes

| Form | Behavior |
|---|---|
| `/retire` | **Sweep.** Inventory → evidence → verdict table → ratification → apply → measure → PR. |
| `/retire --report` | Sweep through the verdict table, then stop. Writes `docs/reports/<date>-steering-inventory.md`. No edits. |
| `/retire <item> [<item>…]` | **Targeted.** Skip the sweep. Show each named item's evidence card, confirm, apply with full bookkeeping. Item names resolve across all surfaces (`mock-call`, `commands/learn`, `plugin:swift-lsp`, `mcp:MCP_DOCKER`, `claude-md:Improvement Mode`). Ambiguous names stop and ask. |

Trigger phrases in the description: "retire", "cleanse my config", "declutter claude code",
"what can I get rid of", "prune my skills", "what's steering my sessions". NOT for: relocating
content that stays (`/trim-context`), repo-side bloat in a project (`/trim-context` at that repo),
fleet drift (`fleet-manifest-reconcile`, unbuilt).

### 5.2 Surfaces inventoried

| Surface | Where | Unit | "Retire" means |
|---|---|---|---|
| Global CLAUDE.md sections | `CLAUDE.md` (symlinked), `@operating-constraints.md` | one `##`/`###` section | delete the section; if part must survive, verdict is *relocate* → `/trim-context` |
| House skills | `skills/<name>/` (tracked) | directory | `git rm -r`; row + card; referrers; ledger |
| Untracked skills | `skills/<name>/` in `.gitignore` (mattpocock set, `adhd`, `interview-prep`, `mock-panel`) | directory | tar → `~/.claude/backups/retired-<date>/`, then `mv` out of `skills/`; drop the `.gitignore` block; ledger |
| Commands | `commands/<name>.md`, incl. `.md.disabled` | file | `git rm`; row + card; referrers; ledger |
| Agents | `agents/<name>.md` | file | `git rm`; row under Custom Subagents; card; referrers (skills that dispatch it by name); ledger |
| Plugins | `settings.json` → `enabledPlugins`; `~/.claude/plugins/installed_plugins.json` | plugin | propose `false` or `claude plugin uninstall`; applied on Kyle's word; ledger |
| MCP servers | `~/.claude.json` → `mcpServers`; claude.ai connectors via `deniedMcpServers` | server | propose removal / deny; applied on word; ledger |
| Hooks | `settings.json` → `hooks` | hook entry | propose deletion; applied on word; backup file first |
| Output styles | `output-styles/<name>.md` | file | `git rm`; ledger |
| Auto-memory | `~/.claude/projects/*/memory/` | dir / file | delete empty dirs outright; tar + delete files on word |
| Fleet (report only) | `~/Projects/*/.claude/{skills,commands}/`, `~/Projects/*/CLAUDE.md` | copy | list every downstream copy of each retired item in the ledger line and the PR; no edits |

### 5.3 Evidence fields per item

| Field | Source | Notes |
|---|---|---|
| `bytes_always_loaded` | frontmatter `description:` length (skills, commands, plugin skills); section length (CLAUDE.md); tool-name count (MCP, deferred) | the per-request cost |
| `invocations_90d`, `invocations_all`, `last_used` | transcripts: `tool_use` with `name=Skill` → `input.skill`; `name=Agent` → `input.subagent_type`; `mcp__<server>__*`; `history.jsonl` `display` starting with `/<name>` | plugin skills match `plugin:name`; bare and namespaced both count |
| `trigger_hits_90d`, `trigger_hits_all` | `history.jsonl` user prompts matched against the item's trigger phrases (parsed from its description, or a hand list for CLAUDE.md sections) | CLAUDE.md lane's primary signal |
| `referrers` | grep of the item's name across `skills/`, `commands/`, `agents/`, `CLAUDE.md`, and the Stop-hook prompt in `settings.json` | who routes to it |
| `routes_to_missing` | names this item routes to that no longer exist | dangling-route detector |
| `vendored_copies` | count + repo list under `~/Projects/*/.claude/` | downstream blast radius |
| `duplicate_of` | name collision with a plugin skill or a built-in | the mattpocock case |
| `last_edited` | `git log -1 --format=%as` for tracked; mtime for untracked | staleness |
| `hook_convertible` | judgment flag, CLAUDE.md sections only; set during ratification, not by the script | from minimal-initial-prompt |

### 5.4 Verdicts

The script assigns a **temperature**, never a verdict:

| Temperature | Rule |
|---|---|
| `cold` | 0 invocations and 0 trigger hits in 90d, 0 referrers |
| `cool` | 0 in 90d, but referenced or used all-time |
| `warm` | 1–4 in 90d |
| `hot` | ≥5 in 90d |

Plus flags: `duplicate`, `dangling` (routes to something missing), `oversized` (top decile of
bytes for its surface), `paused` (`.disabled`). The skill proposes a **verdict** from
temperature + flags + the item's own description, and Kyle rules:

| Verdict | Meaning | Apply step |
|---|---|---|
| `retire` | remove with full bookkeeping | §5.6 |
| `keep` | recorded so it isn't re-proposed; optional "keep because" clause | ledger *keep* section (dated) |
| `merge-into <x>` | fold into another item | retire this item; note the merge; the merge edit itself is a follow-up PR |
| `relocate` | stays, but should load on demand | hand to `/trim-context` with the item named; no edit here |
| `ask` | evidence is mixed | interview question in the ratification pass |

Heuristics the skill applies before showing the table: `cold` + not `paused` → propose `retire`;
`duplicate` → propose `retire` for the non-canonical copy; `dangling` → propose patching the
referrer (an apply step, not a verdict on the referrer); `hot` → `keep` silently unless
`oversized`, then `relocate`; everything else → `ask`. A rare-but-load-bearing item (`envsetup`,
`claudify-repo`) is the reason `cold` proposes and never decides.

### 5.5 Ratification table

Per the global bare-identifier rule, every row carries a title, not just an ID:

```
| # | Item | Surface | Evidence | Proposed | Why |
|---|---|---|---|---|---|
| 1 | Improvement Mode (CLAUDE.md §22–36) | claude-md | 0 hits ever · 1 referrer (Stop hook) · 1.1k chars | retire | never triggered in 5,398 prompts |
| 2 | mock-call (skill) | skill | 0/90d · 3 all-time · last 2026-07-02 · 0 referrers · 651 chars | ask | cold but recent; interview |
```

Kyle answers by row number: `1 retire, 2 keep, 5 relocate, rest as proposed`. `keep` may carry a
clause: `2 keep — interview season`. Unanswered rows are **not** applied ("silence is not
consent", same rule as `reorient`).

### 5.6 Apply: bookkeeping checklist

Run per retired item, in order. Every step is verified before the next; a step that can't be
completed cleanly stops the item and reports it — never a partial removal.

1. **Backup (untracked only).** `tar czf ~/.claude/backups/retired-<date>/<item>.tar.gz <path>`;
   record the path. Tracked items skip this — git is the archive.
2. **Remove the item.** Tracked: `git rm -r <path>`. Untracked: `mv <path> ~/.claude/backups/retired-<date>/<item>/`
   (never `rm -rf`; the `block-rm-rf.sh` hook rejects it outside `/tmp/`). Settings / `~/.claude.json`
   entries: back the file up as `<file>.pre-retire-<ts>` (matches existing backup naming), edit, and
   only on Kyle's per-item word.
3. **Index row and playbook card.** Delete the row in `docs/command-skill-reference.md` and the
   card in `docs/usage-playbook.md`. Run `python3 scripts/check-doc-sync.py`; it must pass.
4. **`.gitignore` block** (untracked only). Remove the item's line(s) and any comment block that
   now describes nothing.
5. **Referrers.** For each file naming the item: **surgical excision with a refuse-if-unsure
   guard** — parse the other item tokens on the same line, excise only the target fragment,
   assert every other token survived, else leave the line and report it. Routes that pointed
   at the item are rewritten to its `merge-into` target if one was ruled, otherwise removed.
   The Stop-hook prompt in `settings.json` counts as a referrer (it names the CLAUDE.md modes).
6. **Ledger line** in `docs/retired.md` (§5.7).
7. **Downstream report.** Append the item's vendored-copy list to the ledger line and to the PR
   body. No edits.
8. **Re-inventory.** Re-run the script; assert the item is absent from every surface it was
   listed on.

### 5.7 Ledger: `docs/retired.md`

```markdown
# Retired items

One line per removal. Source of truth for "why is X gone" and "how do I get it back".
Restore a tracked item with `git show <sha>^:<path> > <path>` (the SHA is the retirement
commit); an untracked one from the backup path. Downstream copies are listed so a later
fleet prune knows what to hunt.

| Date | Item | Surface | Why | Evidence at retirement | Restore | Downstream copies |
|---|---|---|---|---|---|---|
| 2026-09-XX | Improvement Mode | claude-md | never triggered | 0 hits / 5,398 prompts | `git show abc123^:CLAUDE.md` §22–36 | — |
| 2026-09-XX | tdd (loose copy) | skill (untracked) | duplicate of plugin `mattpocock-skills:tdd` | 36-skill collision | `~/.claude/backups/retired-2026-09-XX/tdd/` | 16 repos |

## Kept on purpose

Items ruled `keep` with a clause, so they aren't re-proposed. Re-open only if usage changes.

| Date | Item | Keep because |
|---|---|---|
```

`docs/command-skill-reference.md` gains one sentence in its intro pointing at the ledger. The
doc-sync check does not read the ledger.

### 5.8 Safety rules

- **Branch + PR always.** Never on `main`. Diffs under `skills/**`, `commands/**`, `agents/**`,
  or `CLAUDE.md` are behavioral; propose at least a single review round per the global gate.
  Interactive: Kyle rules on scope. Unattended: single round is the floor.
- **Ratify before remove.** No apply step runs for an unratified row.
- **Never `rm -rf`.** `git rm` for tracked, `mv` to backups for untracked.
- **Untracked settings edits only on Kyle's word**, one item at a time, file backed up first.
- **Never touch a project repo.** Fleet is report-only.
- **No false cleans.** The script exits non-zero if `history.jsonl` is unreadable, zero
  transcripts parse, or any surface enumerates to zero items where files exist. A count of 0 is
  only reported when the source was read.
- **Refuse-if-unsure on referrer edits** (§5.6 step 5).
- **Doc-sync must pass** before push.
- **Verification is the re-inventory**, not a claim. The PR body carries the before → after
  table from the script, not from prose.

### 5.9 Measurement and report

Before and after the apply pass, the script prints always-loaded chars per surface:

```
Surface                          Before    After    Δ
Global CLAUDE.md + constraints   24,033   19,450  -4,583
Skill descriptions (skills/)     34,108   21,200 -12,908
Plugin skill descriptions        11,154   11,154       0
...
```

If Kyle pastes `/context` output from a fresh session before and after, the report includes
it as the wire-level check; the skill does not try to run `/context` itself.

### 5.10 Handoffs

| Situation | Hand to |
|---|---|
| Verdict `relocate` | `/trim-context` (named item, "move to on-demand") |
| Retired item has vendored copies | ledger + PR body; a future `fleet-manifest-reconcile` build |
| Verdict `merge-into` | follow-up PR; `retire` records the intent only |
| A CLAUDE.md rule is `hook_convertible` | backlog stub; converting is its own change |

## 6. Convention changes

1. **Retire = delete + ledger.** `.md.disabled` now means "paused, likely coming back", nothing
   else. The two existing `.disabled` commands (`/learn`, `/autonomous-milestone`) are pilot
   candidates; Kyle rules whether they convert to ledger entries or stay paused.
2. **`docs/retired.md` exists** and the reference doc's intro points at it.
3. **Reference Doc Maintenance** in the global CLAUDE.md already covers deletion ("remove its
   row"). No edit needed there. The skill's own row and card land in the same commit as
   `skills/retire/SKILL.md`, per that rule.

## 7. Inventory script

`skills/retire/scripts/steering_inventory.py` — Python 3 stdlib only, read-only, deterministic.

```
usage: steering_inventory.py [--since DAYS] [--json PATH] [--md PATH] [--claude-home DIR] [--config-repo DIR] [--projects-root DIR]
```

- Enumerates every surface in §5.2 and emits one record per item with the fields in §5.3 and a
  temperature from §5.4. Flags, not verdicts.
- `--since` defaults to 90. `--claude-home` defaults to `~/.claude`, `--config-repo` to the
  resolved target of `~/.claude/skills`, `--projects-root` to `~/Projects`. The overrides exist
  so tests run against fixtures.
- Exit codes: 0 = inventory complete; 2 = a source was missing or unreadable (never silently 0);
  3 = a surface enumerated to zero items where files exist.
- Output: `--json` for the skill to reason over; `--md` for the report file and the PR body. With
  neither, prints the markdown to stdout.
- Tests: `skills/retire/scripts/tests/` with tiny fixtures (a fake `history.jsonl`, two fake
  transcripts, a fake `skills/` tree). Asserts: counts, `last_used`, referrer detection, the
  duplicate flag, the dangling flag, and the non-zero exits. `python3 -m unittest discover`.
- Performance: the transcript corpus is 3.1 GB. Stream line-by-line, match on the
  `"name":"Skill"` / `"name":"Agent"` / `"name":"mcp__` substrings before JSON-parsing a line,
  and cache per-file results keyed by `(path, size, mtime)` in `~/.claude/cache/retire/` so a
  re-run only reads new transcripts.

## 8. Pilot: first targets

The first sweep's candidates, from the 2026-09-17 evidence. These are proposals; the
ratification table decides.

| # | Item | Likely verdict | Note |
|---|---|---|---|
| 1 | 36 untracked mattpocock skill copies + `.gitignore` block | retire | D7. Verify bare `/tdd` resolves to the plugin first; if not, the plugin's namespaced form is the new spelling and the playbook says so. |
| 2 | Improvement Mode, New Feature Mode (CLAUDE.md) | retire | 0 hits ever. The Stop-hook prompt sentence naming them is a referrer to patch. |
| 3 | Kickoff Mode section (CLAUDE.md) | relocate or shrink | 2 hits; `/kickoff` exists — one pointer line may suffice. |
| 4 | `/autonomous-milestone.md.disabled`, `/learn.md.disabled` | retire → ledger, or keep paused | D5 convention change; Kyle rules. The five dangling routes get patched either way. |
| 5 | Four comment-only disabled hook entries | retire | on Kyle's word (settings.json). |
| 6 | ~30 empty `memory/` dirs | retire | mechanical. |
| 7 | `MCP_DOCKER` (failing to connect; 512 uses all-time) | ask | on Kyle's word. |
| 8 | Three browser automators (kapture / claude-in-chrome / playwright plugin) | ask | usage says kapture leads; ask before touching. |
| 9 | Every `cold` skill/command/agent the sweep finds | ask | the actual point of the sweep. |

## 9. Build phases

| Phase | Deliverable | Acceptance |
|---|---|---|
| 0 | This spec + the implementation plan | committed on `feat/retire-skill` |
| 1 | `steering_inventory.py` + tests; a read-only run saved to `docs/reports/<date>-steering-inventory.md` | tests green; report lists every surface item with evidence; numbers match this session's hand checks (adversarial-review 158 all-time; Improvement Mode 0 hits); missing-source exit verified |
| 2 | `skills/retire/SKILL.md` + `references/bookkeeping.md` + reference row (Session & Context Management) + playbook card + `docs/retired.md` seeded empty | `check-doc-sync.py` passes; `/retire --report` runs end-to-end on the live setup |
| 3 | Pilot sweep on the live config; Kyle ratifies; apply; measure | retired items absent from a fresh session's listing (re-inventory + Kyle's `/context`); ledger written; before → after table in the PR; review scope proposed |
| 4 (v2 stubs) | backlog items: fleet prune lane, per-project CLAUDE.md lane, periodic `--report` cadence | stubs only |

## 10. Risks and landmines

- **`block-rm-rf.sh`** rejects `rm -rf` outside `/tmp/`. Use `git rm` / `mv`. Safety-net also
  blocks `xargs sh -c`, `git checkout --`, `git reset --hard`.
- **zsh mangles `$ref:path`.** Brace every expansion or run scripts under `bash`.
- **False cleans.** A grep or API call that fails must not read as 0 (§5.8). The July fleet
  sweep produced two.
- **Single-line lists.** DogHood's `CLAUDE.md` lists every command on one line. The fleet is
  report-only in v1 precisely because of this; the same excision guard protects claude-config's
  own referrer edits.
- **Bare-name resolution after removing loose plugin copies** (D7). Test before apply; if bare
  `/tdd` stops resolving, that is a documented spelling change, not a blocker.
- **Live symlink.** `skills/retire/SKILL.md` is live the moment it exists on disk, on whatever
  branch is checked out. Keep the description honest from the first commit.
- **Transcript volume.** 3.1 GB; the cache in §7 keeps re-runs cheap. First run is minutes.
- **Public repo.** Never write private repo paths into `docs/retired.md`'s downstream column;
  use repo names only.

## 11. Backlog effects

- **Absorbs:** `coliseum-commands-earn-their-keep` (this is it, without the Stop-hook tracer —
  transcripts already carry the signal); `minimal-initial-prompt` (the CLAUDE.md lane).
- **Leaves alone:** `trim-context-harness-lane`, `system-prompt-inspector` (the measure step
  accepts pasted `/context` numbers but does not build the proxy).
- **Adds (v2 stubs):** fleet prune lane; per-project CLAUDE.md lane; a periodic
  `/retire --report` cadence.

## 12. Deferred to v2

- Fleet prune (needs `fleet-manifest-reconcile`'s per-item manifest and its landmine list).
- Per-project `CLAUDE.md` sections and vendored `.claude/` copies as first-class surfaces.
- Co-occurrence evidence ("handoff and wrap fire back-to-back") — cheap, but not needed to
  retire anything.
- Correction detection (was the next human turn a correction?) — noisy; skip until a verdict
  needs it.

## 13. Run-config note

Continue in the current Fable 5.1 session after compaction: phases 1–2 are small and phase 3 is
judgment-heavy (ruling on rows with Kyle), which is the planner's job. If starting fresh instead:

```
claude --model claude-fable-5-1 --effort xhigh
```

Phase 1 (the script and its tests) is mechanical enough to dispatch to a Sonnet 5 subagent at
`medium` from within the session; the plan marks that task.

## 14. Grill amendments (2026-09-18)

Rulings from the grill, each a delta to the sections above. The spec in `.scratch/retire-skill/spec.md`
encodes them in full; this list exists so a reader of this document is not misled.

**Evidence (§5.3)**
- A `new` temperature for items added inside the window; never proposed `retire`; omitted unless it carries another flag. Added date per surface: first commit (tracked), first commit containing the heading (CLAUDE.md sections), mtime (untracked), `installedAt` (plugins); MCP, hooks, memory dirs are never `new`.
- Typed and session-chosen invocations are shown split; temperature uses the sum. `auto_only` flags skills and commands with 0 typed and ≥5 session-chosen in the window; informational only.
- Referrers (steering files) drive temperature; mentions (all other tracked markdown) are reported and edited. The index doc, the playbook, and the ledger are excluded from both.
- MCP servers are the union of the user-scope config and server names observed in transcripts, so claude.ai connectors get rows. Output styles carry an `unlinked` flag (the repo's one style never loads).
- Usage is local-only by design; the report and table carry a one-line caveat. The number of projects an item was used in is shown as a count.

**Proposals (§5.4)**
- Precedence table adopted (spec, Implementation Decisions). Change from §5.4: `warm` is a silent keep, not `ask`. `cool`, `unlinked`, flagged-`new`, and long-paused items are `ask`; `cold` and duplicates are `retire`.
- The precedence table is computed by the script as a `proposed` field so it is under test; the skill renders and Kyle rules.
- Kept-on-purpose rows are read back by the script and omitted with a count. Paused items are omitted until paused a full window, then `ask`.
- Duplicates collapse to one row per canonical plugin; empty memory dirs and comment-only hooks collapse to one row per class.

**Verdicts (§5.4, §5.10)**
- `pause` is a verdict: commands and skills rename to `.disabled`, plugins get `claude plugin disable`; no pause for CLAUDE.md sections, MCP servers, or hooks; no ledger line. Index rows read "(paused <date>)" with a bold "Paused" note.
- `merge-into` writes a backlog stub only; the removal lands with the merge PR, whose ledger line reads "merged into".
- Reply grammar gains `keep (hook)` for hook-convertible sections, and "ask me about row N" for a fuller card. The table is the interview.

**Ratification and apply (§5.5, §5.6)**
- One table, grouped by surface, CLAUDE.md sections last, mechanical classes collapsed.
- Untracked settings: one confirmation per file per pass showing the exact edit list, using the CLI verbs (`claude plugin uninstall|disable`, `claude mcp remove`). Retire = uninstall for plugins.
- Doc mentions are edited by the skill in the same PR, listed under their own PR heading.

**Ledger and report (§5.7, §5.9)**
- Ledger Item ids are surface-qualified (`skill:mock-call`, `claude-md:Improvement Mode`).
- The committed report is redacted (counts and generic labels for memory dirs and hooks, repo names only for vendored copies); the full JSON stays under the local cache dir. `--report` follows the standing git workflow.
- `--surface <name>` filters the sweep and the report.

**Glossary.** CONTEXT.md gained steering surface, retire, pause, relocate, temperature, verdict, ledger (commits `65c56f4`, `83147c2`).
