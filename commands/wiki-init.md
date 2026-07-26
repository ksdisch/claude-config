---
description: Initialize a project wiki — creates PROJECT.md, HANDOFF.md, and the minimum wiki structure for one project or all projects under ~/Projects/. Idempotent (never overwrites existing wiki files). For ongoing wiki maintenance, the project-wiki skill is invoked automatically in any project that has wiki sentinel files.
argument-hint: "[--all | <project-path>]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, AskUserQuestion
---

# /wiki-init

Initialize a project wiki using the `project-wiki` skill.

## Parse `$ARGUMENTS`

- **No args** → initialize the wiki in the **current working directory**
- **`--all`** → initialize the wiki in every git repo directly under `~/Projects/` (top level only) that does not already have a wiki (i.e., no `PROJECT.md` at the repo root)
- **`<path>`** → initialize the wiki at that specific path. If the path doesn't exist or isn't a directory, stop and report — don't guess.

## Single-project mode (no args or explicit path)

Invoke the `project-wiki` skill in INIT mode for the target directory. The skill handles everything: inventory, file creation, CLAUDE.md update, git landing (branch + PR, merged autonomously; local merge if no remote), and the summary report. INIT is idempotent — if the wiki partially exists it creates only the missing files, and if it fully exists the skill reports that and switches to MAINTAIN.

## `--all` mode

When `--all` is passed, use an Agent to scan and initialize all projects in parallel. Follow these steps:

### Step 1: Discover projects

Run:
```sh
for d in ~/Projects/*/; do
  name=$(basename "$d")
  case "$name" in _*|mini|claude-config) continue ;; esac
  if [ -d "$d/.git" ] && [ ! -f "$d/PROJECT.md" ]; then echo "$d"; fi
done
```

This yields top-level git repos with no wiki yet, excluding:
- `_*` directories (meta folders like `_kickoffs`)
- `mini` (throwaway experiments — they don't get wikis)
- `claude-config` (the tooling repo, not a project)

Also note which repos were skipped because `PROJECT.md` already exists (for the preview).

### Step 2: Preview before acting

Print a table of what will be initialized:

```
Projects to initialize (N total):
  ~/Projects/bridge-work
  ~/Projects/clinical-data-etl
  ...

Projects already have a wiki (skipped):
  ~/Projects/some-project (PROJECT.md exists)
  ...
```

Then use `AskUserQuestion` to confirm before writing anything. Let Kyle exclude specific projects if he wants.

### Step 3: Initialize each project

After confirmation, spawn one `Agent` per project, in parallel. Each agent's prompt must include all of the following:

1. The target project directory (work inside it; `cd` there first)
2. **"You are running unattended — no questions, no approval gates. Report-and-proceed."**
3. Read the project's `README.md`, `CLAUDE.md`, and any existing source docs to understand what the project is
4. Follow the `project-wiki` skill in INIT mode (invoke it via the Skill tool; if that tool is unavailable, read `~/.claude/skills/project-wiki/SKILL.md` and follow it directly)
5. Never overwrite an existing file; stage **only** the wiki files and the CLAUDE.md edit — leave unrelated dirty files alone
6. Land the changes per the skill's commit step: `docs/wiki-init` branch → commit → push → PR → merge (merge locally if the repo has no remote)
7. Return a structured result: project name, files created, files skipped, CLAUDE.md updated (yes/no/not found), PR URL (or "merged locally"), and any errors

### Step 4: Summary report

After all agents complete, print a summary:

```
Wiki initialization complete

Initialized (N projects):
  ✓ bridge-work — PROJECT.md, HANDOFF.md, CLAUDE.md updated — PR #12 (merged)
  ✓ clinical-data-etl — PROJECT.md, HANDOFF.md, Sources.md, CLAUDE.md updated — PR #3 (merged)
  ...

Skipped (already had wiki):
  - some-project

Errors:
  ✗ problem-project — <reason>
```

## Notes

- The `project-wiki` skill is what does the actual work — this command is the entry point that handles discovery and batching
- After a project's wiki is initialized, Claude will maintain it automatically in future sessions (the CLAUDE.md update is what signals this)
- To maintain the wiki in an already-initialized project, invoke the `project-wiki` skill directly or Claude will invoke it when wiki updates are needed
- Re-running `/wiki-init` anywhere is safe: INIT never overwrites existing wiki files
- For a retroactive milestone-by-milestone history page (`Wiki/History.md`), run `/wiki-backfill` after the wiki exists — it mines merged PRs and git history into an append-only evolution narrative
