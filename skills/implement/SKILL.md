---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

Implement the work described by Kyle in the spec or tickets.

When the work is a ticket set, work the **frontier**: take a ticket whose blockers are all done — for a purely linear chain, top to bottom — never a blocked one. Do not close or modify any parent issue while working.

Call the Skill tool with `tdd` where possible, at pre-agreed seams ("seam" in the codebase-design skill's sense).

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Work on a feature branch and commit as you go, per the global git workflow in `~/.claude/CLAUDE.md`. Once done, open a PR — the `adversarial-review` loop is the standing pre-merge gate before any autonomous merge.

---

Vendored from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT, Copyright (c) 2026 Matt Pocock), adapted to house conventions. Full notice: `THIRD-PARTY.md` in the claude-config repo.
