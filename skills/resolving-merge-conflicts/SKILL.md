---
name: resolving-merge-conflicts
description: "Use when you need to resolve an in-progress git merge/rebase conflict."
---

# Resolving merge conflicts

1. **See the current state** of the merge/rebase. Check git history, and the conflicting files. Confirm which operation is in flight (`git status` says merging or rebasing) — during a **rebase** the sides are swapped relative to a merge: `HEAD`/"ours" is the branch being replayed *onto*, and the incoming side is your own commit being replayed. Attribute intent to each side accordingly.

2. **Find the primary sources** for each conflict. Understand deeply why each change was made, and what the original intent was. Read the commit messages, check the PRs, check original issues/tickets.

3. **Resolve each hunk.** Preserve both intents where possible. Where incompatible, pick the one matching the merge's stated goal and note the trade-off. Do **not** invent new behaviour. Always resolve; never `--abort`.

4. Discover the project's **automated checks** and run them, typically typecheck, then tests, then format. Fix anything the merge broke.

5. **Finish the merge/rebase.** Stage everything and commit. If rebasing, continue the rebase process until all commits are rebased.

---

Vendored from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT, Copyright (c) 2026 Matt Pocock). Full notice: `THIRD-PARTY.md` in the claude-config repo.
