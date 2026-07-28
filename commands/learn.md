---
description: Mine the current session for reusable patterns and save each as a proper skill — house layout, reference-doc row, landed via branch + PR. Confirmation-gated; nothing is written until I approve the drafts.
argument-hint: "[optional: what to focus the extraction on]"
allowed-tools: Bash, Read, Write, Glob, Grep
---

# /learn — extract reusable patterns from this session

Mine THIS session for patterns worth keeping, draft each as a skill, and — only after I approve — land them the house way.

## What to extract

1. **Error-resolution patterns** — what error, what root cause, what fixed it, whether the path generalizes.
2. **Debugging techniques** — non-obvious diagnostic steps or tool combinations that worked.
3. **Workarounds** — library quirks, API limitations, version-specific fixes.
4. **Conventions discovered the hard way** — workflow or codebase patterns a future session would otherwise rediscover.

Skip: trivial fixes (typos, syntax errors), one-time events (an outage, a transient flake), and anything already recorded in CLAUDE.md, an existing skill, or memory — check before drafting. One pattern per skill. If a candidate is a standalone fact rather than a repeatable procedure, it belongs in auto-memory instead — say so rather than forcing a skill out of it.

## Process

1. Review the session (focused by `$ARGUMENTS` if given); list candidate patterns, each with a one-line pitch. If several, mark a "(Recommended)" pick.
2. **STOP — present the candidates and wait for my pick.** No files before approval.
3. For each approved pattern, create `skills/<pattern-name>/SKILL.md` in `~/Projects/claude-config` (kebab-case slug; note this repo may not be the project you're working in — the skill library is global):
   - Frontmatter: `name:` (the slug) and `description:` (what it does + explicit "Use when …" trigger conditions — this is what makes the skill fire).
   - Body: Problem → Solution → Example (if code) → When to use.
   - Write it project-agnostic; if the pattern came from one project, name that origin in the description.
4. Add a row for each new skill to `docs/command-skill-reference.md` in the same commit (house rule).
5. Land via the standard git workflow: feature branch + PR + the adversarial-review gate (skills edits never use the trivial-diff escape hatch).
