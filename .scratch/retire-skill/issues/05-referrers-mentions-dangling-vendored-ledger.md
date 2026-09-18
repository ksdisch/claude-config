# 05: Referrers, mentions, dangling routes, vendored copies, ledger read-back

**What to build:** Each row shows who routes to it (referrers: steering files including prompt hooks) separately from who merely mentions it (every other tracked markdown file, with the index doc, playbook, and ledger excluded), which of its own routes point at something missing, which project repos carry a vendored copy, whether the ledger already records a keep ruling for it, and when it was last edited. Only referrers feed temperature, so `cool` becomes real. The plan's sixth task is the starting point.

**Blocked by:** 03, 04

**Status:** ready-for-agent

- [ ] The referrer corpus is skills, commands, agents markdown plus CLAUDE.md, the constraints file, and prompt hooks; the mention corpus is all other tracked markdown minus the index doc, the playbook, and the ledger
- [ ] Matching is word-boundary on the item name, excludes the item's own files, and uses the short name for plugins
- [ ] `routes_to_missing` lists strict `/name` or backticked names that resolve to a paused command or a ledger-retired id, and sets `dangling`
- [ ] `vendored_copies` lists repo directory names under the projects root that carry the skill or command; CLAUDE.md sections match by heading in project CLAUDE.md files
- [ ] `kept` is set from the ledger's kept table by surface-qualified id; retirement ids feed the missing-name check with the surface prefix stripped
- [ ] `last_edited` comes from git for tracked items and mtime otherwise
- [ ] `cool` requires at least one referrer or any all-time use; tests cover every criterion above

## Comments

