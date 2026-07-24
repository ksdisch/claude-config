---
description: Initialize a project wiki — creates PROJECT.md, HANDOFF.md, and the minimum wiki structure for one project or all projects under ~/Projects/. For ongoing wiki maintenance, the project-wiki skill is invoked automatically in any project that has wiki sentinel files.
argument-hint: "[--all | <project-path>]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Skill, Agent
---

# /wiki-init

Initialize a project wiki using the `project-wiki` skill.

## Parse `$ARGUMENTS`

- **No args** → initialize the wiki in the **current working directory**
- **`--all`** → initialize the wiki in every git repo under `~/Projects/` that does not already have a wiki (i.e., no `PROJECT.md` at the repo root)
- **`<path>`** → initialize the wiki at that specific path

## Single-project mode (no args or explicit path)

Invoke the `project-wiki` skill in INIT mode for the target directory. The skill handles everything: inventory, file creation, CLAUDE.md update, and the summary report.

## `--all` mode

When `--all` is passed, use an Agent to scan and initialize all projects in parallel. Follow these steps:

### Step 1: Discover projects

Run:
```sh
ls ~/Projects/
```

Filter to directories that:
1. Contain a `.git` directory (it's a git repo)
2. Do NOT already have a `PROJECT.md` at the root (wiki doesn't exist yet)
3. Are not `_kickoffs`, `mini`, or any directory starting with `_` (these are meta folders, not projects)

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

Proceed? (yes to continue, or name specific ones to skip)
```

Use `AskUserQuestion` to confirm before writing anything. Let Kyle exclude specific projects if he wants.

### Step 3: Initialize each project

After confirmation, use an `Agent` for each project that needs initialization. Spawn them in parallel (one per project). Each agent should:

1. `cd` into the project directory
2. Read the project's `README.md`, `CLAUDE.md`, and any existing source docs to understand what the project is
3. Invoke the `project-wiki` skill in INIT mode
4. Report back: project name, files created, whether CLAUDE.md was updated

### Step 4: Summary report

After all agents complete, print a summary:

```
Wiki initialization complete

Initialized (N projects):
  ✓ bridge-work — PROJECT.md, HANDOFF.md, CLAUDE.md updated
  ✓ clinical-data-etl — PROJECT.md, HANDOFF.md, Sources.md, CLAUDE.md updated
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
