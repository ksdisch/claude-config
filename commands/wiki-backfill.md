---
description: Backfill a retroactive project history page — mines merged PRs, git log, tags, wrap logs, and ADRs into an append-only Wiki/History.md evolution narrative for one project or all wiki-bearing projects under ~/Projects/. Refuses to overwrite an existing History.md. Ongoing upkeep is handled by the project-wiki skill's MAINTAIN mode.
argument-hint: "[--all | <project-path>]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, AskUserQuestion
---

# /wiki-backfill

Backfill a project's evolution history (`Wiki/History.md`) using the `project-wiki` skill in BACKFILL mode.

## Parse `$ARGUMENTS`

- **No args** → backfill the **current working directory**
- **`--all`** → backfill every git repo directly under `~/Projects/` (top level only) that has a wiki (`PROJECT.md` on the remote default branch) and no `Wiki/History.md` yet
- **`<path>`** → backfill at that specific path. If the path doesn't exist or isn't a directory, stop and report — don't guess.

## Single-project mode (no args or explicit path)

Invoke the `project-wiki` skill in BACKFILL mode for the target directory. The skill handles everything: preconditions (a wiki sentinel is required; an existing `Wiki/History.md` → refuse-and-report), history mining, writing `Wiki/History.md`, updating `Wiki/_index.md`, and landing on a `docs/wiki-history` branch cut from `origin/<default-branch>` (branch + PR, merged autonomously; local merge if no remote).

## `--all` mode

When `--all` is passed, scan and backfill all eligible projects. Follow these steps:

### Step 1: Discover projects

Check the **remote default branch**, not the local worktree — local checkouts may be behind origin or parked on a feature branch. Run:

```sh
for d in ~/Projects/*/; do
  name=$(basename "$d")
  case "$name" in _*|mini|claude-config) continue ;; esac
  [ -d "$d/.git" ] || continue
  if git -C "$d" remote get-url origin >/dev/null 2>&1; then
    git -C "$d" fetch origin --quiet 2>/dev/null
    ref="origin/HEAD"
    git -C "$d" rev-parse --verify -q "$ref" >/dev/null || ref=$(git -C "$d" symbolic-ref --short HEAD)
  else
    ref="HEAD"
  fi
  has_wiki=$(git -C "$d" ls-tree --name-only "$ref" 2>/dev/null | grep -cx 'PROJECT.md')
  has_history=$(git -C "$d" ls-tree --name-only "$ref" Wiki/ 2>/dev/null | grep -cx 'Wiki/History.md')
  if [ "$has_wiki" -ge 1 ] && [ "$has_history" -eq 0 ]; then echo "$d"; fi
done
```

This yields top-level git repos with a wiki but no history page, excluding:
- `_*` directories (meta folders like `_kickoffs`)
- `mini` (throwaway experiments — they don't get wikis)
- `claude-config` (the tooling repo, not a project)

Also note the repos skipped and why (no wiki sentinel → suggest `/wiki-init` first; `Wiki/History.md` already exists) for the preview.

### Step 2: Preview before acting

Print a table of what will be backfilled:

```
Projects to backfill (N total):
  ~/Projects/bridge-work
  ~/Projects/clinical-data-etl
  ...

Skipped:
  ~/Projects/some-project (no wiki — run /wiki-init first)
  ~/Projects/other-project (Wiki/History.md already exists)
```

Then use `AskUserQuestion` to confirm before writing anything. Let Kyle exclude specific projects if he wants.

### Step 3: Backfill each project — in waves

After confirmation, spawn one `Agent` per project, **in waves of ~6, not all at once** — history mining is `gh`-API-heavy (a full merged-PR sweep plus up to 20 `gh pr view` deep-reads per repo), and a full-parallel fleet risks rate limiting. Each agent's prompt must include all of the following:

1. The target project directory (work inside it; `cd` there first)
2. **"You are running unattended — no questions, no approval gates. Report-and-proceed."**
3. Follow the `project-wiki` skill in BACKFILL mode (invoke it via the Skill tool; if that tool is unavailable, read `~/.claude/skills/project-wiki/SKILL.md` and follow it directly)
4. Cut the `docs/wiki-history` branch **from `origin/<default-branch>`** (resolve via `origin/HEAD`) — never from the current checkout, which may be stale or on an unrelated branch
5. Stage **only** `Wiki/History.md` and `Wiki/_index.md` — leave unrelated dirty files alone; **never stage or print `.env` files or credential values**
6. Land per the skill: `docs/wiki-history` branch → commit → push → PR → merge (merge locally if the repo has no remote)
7. Return a structured result: project name, merged-PR sweep total N, deep-read count K, era count, milestone count, `_index.md` created/updated, PR URL (or "merged locally"), and any errors

### Step 4: Summary report

After all waves complete, print a summary:

```
History backfill complete

Backfilled (N projects):
  ✓ bridge-work — 3 eras / 9 milestones (13 PRs swept, 8 deep-read) — PR #15 (merged)
  ✓ home-base — 5 eras / 18 milestones (146 PRs swept, 20 deep-read) — PR #148 (merged)
  ...

Skipped:
  - some-project (no wiki)

Errors:
  ✗ problem-project — <reason>
```

## Notes

- The `project-wiki` skill's BACKFILL mode does the actual work — this command is the entry point that handles discovery and batching, the same relationship `/wiki-init` has to INIT mode
- Re-running `/wiki-backfill` anywhere is safe: BACKFILL refuses when `Wiki/History.md` already exists
- After backfill, the history page accretes forward automatically — the skill's MAINTAIN mode appends a milestone entry whenever a milestone-significant change lands
