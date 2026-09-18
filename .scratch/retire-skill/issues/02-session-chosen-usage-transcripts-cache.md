# 02: Session-chosen usage from transcripts, with the per-file cache

**What to build:** Skill rows gain session-chosen counts and last-used from Skill tool calls in the transcripts, shown separately from typed counts, with the `auto_only` flag and a per-file cache so a re-run over the 3 GB corpus only reads what changed. The plan's fifth task is the starting point.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] Skill tool calls in fixture transcripts count as session-chosen for the named skill; a plugin skill counts under both its bare and namespaced spelling
- [ ] The evidence column reads `typed N · auto M`; invocations are the sum; last-used is the latest across both sources
- [ ] `auto_only` is set for skills and commands when window typed is 0 and window auto is at least 5, and it never changes `proposed`
- [ ] Transcript lines are substring-filtered before JSON parsing; malformed lines are skipped without aborting the run
- [ ] Per-file results are cached under the claude home's cache directory keyed by path, size, and mtime; a second run reports cache hits equal to the file count; a touched file is re-read; `--no-cache` bypasses
- [ ] Zero transcripts parsed (directory missing or every file unreadable) exits 2 naming the source
- [ ] Tests cover every criterion above

## Comments

