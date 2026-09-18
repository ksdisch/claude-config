# 07: Ledger seeded, reference pointer, first live redacted report

**What to build:** The retirement ledger exists with both tables, the reference doc's intro points at it, and a real read-only run on the live setup is committed as the first dated steering-inventory report, with the design's hand counts confirmed. The plan's ninth task and the live-run half of its eighth are the starting point.

**Blocked by:** 06

**Status:** done

- [x] The ledger has a header describing the manual restore procedure, an empty retirements table with the spec's columns, and an empty kept-on-purpose table
- [x] The reference doc's intro gains one sentence pointing at the ledger; the doc-sync check passes
- [x] A live run writes the redacted markdown to a dated file in the reports directory and the full JSON under the cache directory, exit 0
- [x] Sanity checks hold: adversarial-review at least 158 session-chosen all-time; Improvement Mode and New Feature Mode 0 trigger hits; 36 loose copies flagged duplicate and collapsed to one row; five files route to the paused autonomous-milestone command; kapture at least 2,635; the output style flagged unlinked; 32 empty memory dirs collapsed
- [x] Searching the committed report for the home directory path returns nothing

## Comments

- 2026-09-18 — merged as `a8aff0b`. Ledger seeded with both tables and the manual restore procedure; read-back verified against the live parser. Reference-doc intro points at it. First live redacted report committed (329 lines). All eight sanity checks hold, two exactly at their floor (adversarial-review 158, kapture 2,635). Committed report searched for the home directory path: zero hits.

