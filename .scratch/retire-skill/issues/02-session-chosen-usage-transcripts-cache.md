# 02: Session-chosen usage from transcripts, with the per-file cache

**What to build:** Skill rows gain session-chosen counts and last-used from Skill tool calls in the transcripts, shown separately from typed counts, with the `auto_only` flag and a per-file cache so a re-run over the 3 GB corpus only reads what changed. The plan's fifth task is the starting point.

**Blocked by:** 01

**Status:** done

- [x] Skill tool calls in fixture transcripts count as session-chosen for the named skill; a plugin skill counts under both its bare and namespaced spelling
- [x] The evidence column reads `typed N · auto M`; invocations are the sum; last-used is the latest across both sources
- [x] `auto_only` is set for skills and commands when window typed is 0 and window auto is at least 5, and it never changes `proposed`
- [x] Transcript lines are substring-filtered before JSON parsing; malformed lines are skipped without aborting the run
- [x] Per-file results are cached under the claude home's cache directory keyed by path, size, and mtime; a second run reports cache hits equal to the file count; a touched file is re-read; `--no-cache` bypasses
- [x] Zero transcripts parsed (directory missing or every file unreadable) exits 2 naming the source
- [x] Tests cover every criterion above

## Comments

- 2026-09-18 — merged to `feat/retire-skill` in `5b3050c`. Live corpus: 6,127 transcripts / 3.1 GB, cold run 8.2s, warm run 0.25s with 6,125 cache hits. `adversarial-review` shows 158 session-chosen all-time, matching the sanity check, flagged `auto_only`.

