---
name: correct
description: "Find the mistakes agents keep repeating in this repo and make each one impossible. Try architecture first, then types, then a lint whose error names the fix, then a test, and write docs last. Prove each check fails on a real past mistake. Repeat this each time the operator corrects you. Use for /correct."
disable-model-invocation: true
---

# Correct

The operator keeps correcting agents in this repo for the same mistakes. Change the repo so the next agent can't make them.

Assume every contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Design the repo so a change that looks right from one file is right for the whole repo.

## Find the mistake classes

First, read recent commits, reverts, PR review comments (`gh pr view <n> --comments`), the repo's agent instruction files (`CLAUDE.md`, `.claude/CLAUDE.md`, `AGENTS.md`, and any skill that lists known false alarms or gotchas), and comments that explain workarounds. Group the mistakes into classes. A class counts once it has happened twice.

## Fix each class at the highest level that works

1. **Eliminate it with architecture.** Give each piece of state one owner and each task one supported way. Hide internals so the wrong import fails. Replace hand-synced lists with one source of truth. Delete old ways and dead code an agent would copy.
2. **Enforce it with types so the bad state can't be written.** If bad code still compiles, add a lint or CI check whose error names the file, type, or function to use instead. If the pattern is already common, fail only when a change adds more.
3. **Test the behavior.** Fix or delete any test that still passes when the behavior it checks breaks, or that fails when only the internals change.
4. **Write docs or agent rules last, only for judgment calls.** Nothing fails when an agent skips them.

## Fix and prove

Then fix the most frequent classes now, one commit each, on a feature branch with a PR, never on `main`. Prove each new check fails on a real past mistake. Run the same command locally and in CI. Exceptions go on the offending line with a reason, an expiry date, and a human's approval.

## Keep the rule table

Last, keep a table in the repo's `CLAUDE.md` that pairs each rule with what enforces it. When the operator corrects you, fix the mistake and add the rule. If the rule was already there and nothing enforces it, that's a repeat, so fix it at the highest level in the same change. Drop a rule once its mistake can't happen.

Editing `CLAUDE.md` is a behavioral change: the PR that carries the table gets a `/code-review` before merge, per the review-gate rule in the global `CLAUDE.md`. If the repo has a `## Wired gates (Preflight)` note, a new enforcer that is a gate gets listed there too.

**Reply:** each class with its evidence, the level you picked, and why a higher level didn't work.

---

Vendored from [cursor/plugins](https://github.com/cursor/plugins) pstack (MIT, Copyright (c) 2026 Lauren Tan), adapted to house conventions. Full notice: `THIRD-PARTY.md` in the claude-config repo.
