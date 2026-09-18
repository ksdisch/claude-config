# 06: The full precedence table, collapsed rows, oversized, redaction proven

**What to build:** The script computes `proposed` for every surface from the adopted precedence table, collapses the mechanical classes and the duplicate copies into one row each, flags oversized items, summarizes what was omitted and why, prints the per-surface totals table, and proves in tests that the markdown never carries private detail. The plan's seventh task is the starting point; the table itself is in the spec.

**Blocked by:** 05

**Status:** ready-for-agent

- [ ] `proposed` implements the spec's precedence table top-wins, with a test per row including `warm` silent keep, `new` alone omitted, `new` with a flag → ask, paused under a window omitted, paused a window or more → ask, `hot`/`warm` + `oversized` → relocate
- [ ] `oversized` marks the top decile of bytes within a surface only when that surface has at least ten sized items
- [ ] Duplicates collapse to one row per canonical plugin; empty memory dirs and comment-only hooks collapse to one row per class; each collapsed row carries its member count and, in JSON, member ids
- [ ] Omitted classes (kept, new alone, hot/warm, paused under a window) are summarized after the table with counts and names; `auto_only` names are listed
- [ ] The totals table shows always-loaded bytes per surface, and before/after with delta when two JSON files are given
- [ ] Tests assert the markdown contains no absolute paths, no hook command text, no memory slugs, no MCP config values, and only repo names for vendored copies
- [ ] The markdown header carries the local-corpus caveat line

## Comments

