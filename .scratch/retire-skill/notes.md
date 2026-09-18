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

Landed on `feat/retire-skill`: tickets 01, 02, 03. Suite is **77 tests**, green.

- `# ---- tunables` at the top owns every threshold. Add new ones there.
- `ENUMERATED_SURFACES` gates `--surface` so an unbuilt lane errors instead of reporting
  empty. Extend it as you land a surface. Currently: skill, command, agent, output-style,
  claude-md.
- **Unmeasured is `None`, never 0.** This is the invariant the whole Instrument rests on
  (spec story 15). `trigger_*` is `None` for an item with no trigger source; `tool_*` is
  `None` only if transcripts could not be read. Never collapse an unread source to 0.
- The transcript reader already collects **all three** call kinds in one pass —
  skill, agent (`input.subagent_type`), and `mcp__<server>__`. Ticket 04 consumes the
  agent and MCP tallies; it does not need to re-read transcripts.
- `compute_totals` takes `config_repo` because CLAUDE.md byte totals are measured from the
  files, not summed across records (a `###` body is already inside its `##` parent's).
- `_name_cell()` in `# ---- output` renders item names safely — some headings contain
  backticks or pipes that would otherwise break the table you rule from. Use it.
- The trigger sidecar carries a `"_comment"` key documenting the null convention. Any code
  iterating sidecar keys must skip keys beginning with `_`.

**Expect to amend ticket 01's tests.** Each surface that lands makes some earlier
assertion about a not-yet-measured state false by construction. Amend those in place and
say so in your report — do not work around them, and do not weaken an assertion to pass.
Put your *new* tests in your own file so parallel tickets don't collide.

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
