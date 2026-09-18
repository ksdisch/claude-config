# Retired items

One line per removal from the global steering surface. Source of truth for "why is X gone"
and "how do I get it back". Written by the [`retire`](../skills/retire/SKILL.md) skill; edit
by hand only to correct a line. Restore a tracked item with
`git show <sha>^:<path> > <path>` (the SHA is the retirement commit); an untracked one from
the backup path. Downstream copies are repo **names** only (this repo is public) so a later
fleet prune knows what to hunt.

| Date | Item | Surface | Why | Evidence at retirement | Restore | Downstream copies |
|---|---|---|---|---|---|---|

## Kept on purpose

Items ruled `keep` with a clause, so they aren't re-proposed. Re-open only if usage changes.

| Date | Item | Keep because |
|---|---|---|
