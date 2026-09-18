# Implementer notes — retire-skill arc

Read this before touching code. It is the accumulated set of things that have already
bitten someone on this arc. It does not restate the spec; it lists the traps.

## Pointers (read in this order)

1. Your ticket: `.scratch/retire-skill/issues/<NN>-*.md`
2. The spec: `.scratch/retire-skill/spec.md` — **the spec wins wherever the plan's code disagrees**
3. The plan task your ticket names: `docs/plans/2026-09-17-retire-skill.md` (its "Read before
   starting" section holds the verified data shapes; its code is a *starting point to amend*,
   not final — see the amendment banner at the top of the plan)
4. Design record with all 23 grill rulings: `docs/superpowers/specs/2026-09-17-retire-skill-design.md` §14

## Branch and PR

- `feat/retire-skill` is the PR branch; **PR #132 is PR A**. Do not create a new branch or PR.
- Implementer worktrees branch off `feat/retire-skill` and merge back onto it.
- The PR body is updated with `gh pr edit 132`, never `gh pr create`.

## The skills directory is live

`~/.claude/skills` is a symlink to this repo's `skills/`, resolved on **whatever branch the main
checkout has**. Anything under `skills/retire/` in the main checkout is loaded by every new
session immediately. Consequences:

- The skill's `description` must be honest from its very first commit.
- The main checkout stays on `feat/retire-skill` for the whole arc.
- Worktrees are *not* live — work there freely.

## Hooks and shell traps

- `block-rm-rf.sh` rejects `rm -rf` outside `/tmp/`. Use `git rm` for tracked files, `mv` into a
  dated backup folder for untracked ones, or Python.
- The safety-net plugin blocks `xargs … sh -c`, `git checkout --`, and `git reset --hard`.
  Use a `for` loop, `git restore`, or `mv`.
- zsh: quote `'claude-opus-5[1m]'`; brace `${ref}:path`; `builtins` is a read-only variable name.
- `.claude/worktrees/` is gitignored via `.claude/*` with a `!.claude/CLAUDE.md` negation. A
  trailing ` # comment` on a gitignore line is **part of the pattern** — keep comments on their
  own line.

## Your worktree may not start where you expect

A dispatched worktree can be created from an older `main` commit rather than from
`feat/retire-skill`. **Before doing anything else**, run:

```
git merge --ff-only feat/retire-skill
```

If that is not a fast-forward, stop and report — do not try to force it. `git reset --hard` is
blocked by the safety net.

## State of the script (update this as tickets land)

Landed on `feat/retire-skill`: tickets 01, 02, 03, 04, 05, 06. Suite is **202 tests**, green.

- `# ---- tunables` at the top owns every threshold. Add new ones there.
- `ENUMERATED_SURFACES` gates `--surface` so an unbuilt lane errors instead of reporting
  empty. Extend it as you land a surface. Currently: **every** surface — skill, command,
  agent, output-style, plugin, mcp, hook, memory, claude-md.
- **Unmeasured is `None`, never 0.** This is the invariant the whole Instrument rests on
  (spec story 15). `trigger_*` is `None` for an item with no trigger source; `tool_*` is
  `None` only if transcripts could not be read. Never collapse an unread source to 0.
- The transcript reader already collects **all three** call kinds in one pass —
  skill, agent (`input.subagent_type`), and `mcp__<server>__`. Ticket 04 consumed the
  agent and MCP tallies; no later ticket needs to re-read transcripts either.
  `Transcripts.keys(kind)` lists every key of one kind seen anywhere — that is what makes
  the MCP surface a union rather than a copy of the config file.
- `UNMEASURABLE_SURFACES` (hook, memory) get temperature `unknown`, not `cold`: no source
  names a hook entry or a memory dir, and `cold` is a *measured* claim of disuse. Their
  `proposed` therefore comes from their flags, which is ticket 06's table.
- `COUNT_ONLY_SURFACES` (memory) render in markdown as one summary line, never a row per
  item — a memory dir's name is a project path slug and this repo is public.
- Plugins are dated by `installedAt`, which is **ISO-8601** in every live record (the plan
  and the original fixture assumed epoch ms; both spellings are now accepted). Their usage
  is the sum over what they ship: skills (bare + namespaced), `<short>:<agent>` dispatches,
  and `mcp__plugin_<short>_<server>__` calls. Slash commands are deliberately not counted.
- `mcp_key()` flattens only what cannot appear in a tool name (dots, spaces, apostrophes).
  **Hyphens survive** — `mcp__basic-memory__search`. Flattening them split every hyphenated
  server into two rows; do not "simplify" that regex.
- `compute_totals` takes `config_repo` because CLAUDE.md byte totals are measured from the
  files, not summed across records (a `###` body is already inside its `##` parent's).
- `_name_cell()` in `# ---- output` renders item names safely — some headings contain
  backticks or pipes that would otherwise break the table you rule from. Use it.
- The trigger sidecar carries a `"_comment"` key documenting the null convention. Any code
  iterating sidecar keys must skip keys beginning with `_`.
- **Referrers vs. mentions (ticket 05).** Two corpora, built once per run in `build_inventory`
  from the *repo*, not from the enumerated rows — so a `--surface skill` run still resolves a
  route to a command it never listed. `build_corpus` is the steering corpus (skills incl. their
  reference files, commands incl. `.disabled`, agents, `CLAUDE.md`, the constraints file, and
  one entry per **prompt**-type hook keyed `settings.json:<Event>[g][i]`); `build_mention_corpus`
  is every other *tracked* `.md`. `BOOKKEEPING_DOCS` (index, playbook, ledger) are in neither.
  **Only `referrers` feeds temperature.** Both render as counts — the paths stay in the JSON.
- Word-boundary matching is blunt on purpose and it shows: a plugin short name like `off` hits
  the phrase "hands off". Expect a few false referrers on short, English-word names; the pilot
  reads the row, not the count alone.
- `missing_names()` = paused command filenames + ledger retirement ids with the surface prefix
  stripped (`skill:zeta` → `zeta`). A route is strict `/name` or `` `name` `` — bare prose words
  are not routes. Live: **five** files route to the paused `autonomous-milestone`, one to `learn`.
- `vendored_copies()` skips the config repo **and its git worktrees** (`.git` as a file pointing
  into `<config repo>/.git`). Several live worktrees sit under `~/Projects`; without that skip
  every global `CLAUDE.md` section reported itself as vendored four times over.
- `last_edited` covers the four config-repo file surfaces only (skill/command/agent/output-style):
  git for tracked, mtime otherwise, and a skill is dated by its **directory**. A plugin, an MCP
  server, a hook and a `claude-md` section have no edit date of their own and report `None`.
- `kept` is a flag read back from the ledger's `## Kept on purpose` table by **surface-qualified**
  id, so `skill:beta` and `command:beta` never collide. `docs/retired.md` does not exist yet
  (ticket 07 creates it); an absent ledger reads as two empty tables, never a missing source.
- **`PRECEDENCE_TABLE` is the only thing that decides a proposal (ticket 06).** An ordered tuple
  of `PrecedenceRow`s just under the model; the first row whose `test` holds sets `proposed`,
  `shown` and `precedence` on the item, so *the order of that tuple is the rule*. Its last row
  holds for anything — nothing can fall off the table. `PROPOSED_BY_TEMPERATURE` is gone.
- `PROPOSAL_FLAGS` is the flag set the table reads. `auto_only` is deliberately outside it (the
  spec calls it informational), and so are the three flags later tickets added beyond the spec's
  list — `disabled`, `connector_only`, `denied`. Adding a flag to that tuple moves live rows.
- **Collapse and omission are computed, not rendered.** `collapse_rows` folds the duplicate
  copies (one row per canonical *plugin*) and the mechanical classes (one row per class) and
  stamps `collapsed_into` on each member; `omitted_summary` groups everything suppressed by the
  precedence row that suppressed it. Both ride on `Inventory.collapsed` / `.omitted` and into
  the JSON. A collapsed member is not "omitted" — its row is in the table, behind the collapse.
- The markdown is three sections now: `## Proposals` (numbered, grouped by surface, `retire` →
  `ask` → `relocate`), `## Omitted from the proposals`, then the per-surface `## <surface>`
  tables as a full-inventory appendix. The appendix is why story 1 still holds — the report
  shows everything, the proposals table shows only what needs a ruling.
- `--compare BEFORE.json AFTER.json` renders the before/after always-loaded table with deltas
  and reads nothing else. That is what story 52's PR-body table comes from.
- A count-only surface can never render an individual row in the proposals table; the guard is
  structural, not incidental. Memory rulings reach Kyle only through the collapsed row.

**Expect to amend ticket 01's tests.** Each surface that lands makes some earlier
assertion about a not-yet-measured state false by construction. Amend those in place and
say so in your report — do not work around them, and do not weaken an assertion to pass.
Put your *new* tests in your own file so parallel tickets don't collide.

## The three wrinkles ticket 06 owned — all ruled, do not reopen

1. **Typed counts on surfaces with no typed spelling.** `slash_all` / `slash_90d` are now
   `int | None` and are set only for `TYPED_SURFACES` (`skill`, `command`). Everything else
   renders `typed —/90d · — all`. Live that is 123 of 221 items. The invariant is the whole
   script's: a zero is only printed after the source behind it could have shown something.
2. **A `cold` resting on a source nobody read.** `temperature()` no longer folds anything
   through `or 0`; `_measured()` drops the unmeasured counts, and an item where *nothing* was
   measured is `unknown`, not `cold`. A measured zero still earns `cold` (story 11's CLAUDE.md
   section with a sidecar entry and no hits). Live this moved exactly three rows off `retire`:
   `claude-md:Track multi-step work`, `claude-md:Unattended runs only`,
   `claude-md:Clarifying questions and option formatting`. One `cold` row survives:
   `plugin:swift-lsp@claude-plugins-official`.
3. **An evidence cell that outgrew its table.** `_name_list()` prints the first
   `EVIDENCE_NAMES_MAX` names and counts the rest; the full list stays in the JSON the ledger
   and the fleet prune read. `claude-md:Project Wiki`'s row went from >300 chars to 213.

Consequence worth knowing for ticket 08: an item whose only flag is `dangling` and whose
sources were never measured (`claude-md:Unattended runs only`) reaches the unmeasured floor
and gets no proposal. That is correct — `dangling` is an apply step on the *referrer*, never a
verdict on the item — but it means the five dangling routes to `autonomous-milestone` are
visible in the full inventory and in the JSON, not in the proposals table.

## Gates

- **doc-sync is a pre-push Gate.** `scripts/check-doc-sync.py` checks *the commits being pushed*,
  not the working tree. Only ticket 08 touches the index doc and the playbook; its row and card
  must land in the **same commit**. Baseline: 102 index rows, 102 cards, 64 item files.
  Run it yourself before pushing: `python3 scripts/check-doc-sync.py`.
- **Tests:** stdlib `unittest` only. Run as `python3 -m unittest discover -s tests -t .` from the
  script's directory. Prior art: `skills/architecture-viewer/scripts/tests/`.
  Resolve fixture temp paths on macOS (`/var` → `/private/var`) or path comparisons fail.

## Verified data shapes (do not re-derive)

- `history.jsonl` rows carry `display`, `timestamp` (epoch **milliseconds as a string**),
  `project`, `sessionId`.
- Transcripts are **compact** JSON (no spaces after colons), so the substring needles
  `"name":"Skill"` and `"name":"Agent"` are exact. Agent dispatch carries `input.subagent_type`.
  MCP calls appear as `"name":"mcp__<server>__<tool>"`. Timestamps are ISO-8601.
- Three `SKILL.md` files use `description: >-` folded block scalars; the frontmatter parser must
  join the continuation lines.
- `operating-constraints.md` has **no headings** — its unit is the bold-led paragraph.
- Plugin cache lives at `plugins/cache/<marketplace>/<plugin>/<version>/skills/**/SKILL.md` under
  the claude home; `SKILL.md` files sit at varying depths, so `rglob`.
- `installed_plugins.json` is `{version, plugins: {key: [{installedAt, …}]}}`.
- 33 memory dirs, 32 of them empty. `output-styles/adhd.md` is unlinked.

## Public repo

This repo is public. Nothing committed — report, ledger, notes — may carry absolute paths, hook
command text, memory slugs, or MCP config values. Repo **basenames** only for vendored copies.

## Settled — do not relitigate

The nine brainstorm decisions (design §4) and the 23 grill rulings (§14) are closed. If you find
the spec contradicting the plan's code, **the spec wins**. If you find the spec contradicting
*itself*, stop and report rather than picking.

## Git rules in force

Never push to `main`. Never `gh pr merge --admin`. Before any merge, a review scope is proposed
and the session stops for Kyle's call — this diff is behavioral (skills), so a single round is the
floor. Silence is not consent.
