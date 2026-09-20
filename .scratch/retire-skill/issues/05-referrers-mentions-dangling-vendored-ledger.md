# 05: Referrers, mentions, dangling routes, vendored copies, ledger read-back

**What to build:** Each row shows who routes to it (referrers: steering files including prompt hooks) separately from who merely mentions it (every other tracked markdown file, with the index doc, playbook, and ledger excluded), which of its own routes point at something missing, which project repos carry a vendored copy, whether the ledger already records a keep ruling for it, and when it was last edited. Only referrers feed temperature, so `cool` becomes real. The plan's sixth task is the starting point.

**Blocked by:** 03, 04

**Status:** done

- [x] The referrer corpus is skills, commands, agents markdown plus CLAUDE.md, the constraints file, and prompt hooks; the mention corpus is all other tracked markdown minus the index doc, the playbook, and the ledger
- [x] Matching is word-boundary on the item name, excludes the item's own files, and uses the short name for plugins
- [x] `routes_to_missing` lists strict `/name` or backticked names that resolve to a paused command or a ledger-retired id, and sets `dangling`
- [x] `vendored_copies` lists repo directory names under the projects root that carry the skill or command; CLAUDE.md sections match by heading in project CLAUDE.md files
- [x] `kept` is set from the ledger's kept table by surface-qualified id; retirement ids feed the missing-name check with the surface prefix stripped
- [x] `last_edited` comes from git for tracked items and mtime otherwise
- [x] `cool` requires at least one referrer or any all-time use; tests cover every criterion above

## Comments

- 2026-09-18 — merged to `feat/retire-skill` as `71a5609`. 155 tests green. Live: 109 of 221 items gained a referrer; **exactly 5 files route to the paused `autonomous-milestone`** (independently confirmed by grep), plus a sixth dangling route to the paused `learn`. `cool` became real: 20 cool / 17 cold → **33 cool / 4 cold**, rescuing five constraints paragraphs and three CLAUDE.md sections that referrers show are live. Vendored: 35 items across 23 repos. Redaction re-verified over the 43,889-char markdown: 0 hits.
- Caught a real false claim: config-repo **worktrees** were counting as downstream vendored copies of the repo itself (a worktree's `.git` is a file pointing back into the repo), so the global `CLAUDE.md` reported itself vendored four times. Would have been written into the ledger for a later fleet prune to hunt. Vendored population fell 46 → 35.

