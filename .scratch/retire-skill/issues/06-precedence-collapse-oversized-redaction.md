# 06: The full precedence table, collapsed rows, oversized, redaction proven

**What to build:** The script computes `proposed` for every surface from the adopted precedence table, collapses the mechanical classes and the duplicate copies into one row each, flags oversized items, summarizes what was omitted and why, prints the per-surface totals table, and proves in tests that the markdown never carries private detail. The plan's seventh task is the starting point; the table itself is in the spec.

**Blocked by:** 05

**Status:** done

- [x] `proposed` implements the spec's precedence table top-wins, with a test per row including `warm` silent keep, `new` alone omitted, `new` with a flag → ask, paused under a window omitted, paused a window or more → ask, `hot`/`warm` + `oversized` → relocate
- [x] `oversized` marks the top decile of bytes within a surface only when that surface has at least ten sized items
- [x] Duplicates collapse to one row per canonical plugin; empty memory dirs and comment-only hooks collapse to one row per class; each collapsed row carries its member count and, in JSON, member ids
- [x] Omitted classes (kept, new alone, hot/warm, paused under a window) are summarized after the table with counts and names; `auto_only` names are listed
- [x] The totals table shows always-loaded bytes per surface, and before/after with delta when two JSON files are given
- [x] Tests assert the markdown contains no absolute paths, no hook command text, no memory slugs, no MCP config values, and only repo names for vendored copies
- [x] The markdown header carries the local-corpus caveat line

## Comments

- 2026-09-18 — merged to `feat/retire-skill` as `83cf246`. 202 tests green (47 new, a test per precedence row). Live: 53 rows to rule on (4 retire, 48 ask, 1 relocate), 168 items represented without a row; 72 mechanical items collapsed into 3 rows. Distribution independently re-derived from the JSON: cold 1, new 103.
- All three inherited problems ruled. The second one mattered: `temperature()` no longer treats a missing trigger source as a measured zero, which **moved three CLAUDE.md sections off a `retire` proposal** — `Track multi-step work`, `Unattended runs only`, `Clarifying questions and option formatting`. `cold` went 4 → 1.
- **Open for ticket 08:** the implementer's honest answer to "could a human rule on this in one sitting" was *borderline, no*. 48 of 53 rows are `ask`, clustered into about three repeated questions (13 MCP connector rows, 9 claude-md rows, 8 new+oversized skills). Spec story 24 — each `ask` row carrying its specific question — is the fix, and it lives in ticket 08's renderer. Check this first when 08 renders the table.

