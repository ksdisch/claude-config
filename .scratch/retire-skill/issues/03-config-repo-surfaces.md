# 03: The rest of the config repo: CLAUDE.md sections, constraints paragraphs, commands, agents, output styles, untracked skills

**What to build:** The remaining config-repo surfaces appear as rows with the same evidence shape as skills: CLAUDE.md sections, the operating-constraints paragraphs, commands including paused ones, agents, output styles, and untracked skills. Trigger hits come from a shipped sidecar keyed by the real CLAUDE.md headings and from quoted phrases in descriptions. The plan's second and eighth tasks are the starting point.

**Blocked by:** 01

**Status:** done

- [x] CLAUDE.md yields one record per `##`/`###` heading outside fenced code, bytes equal to the section length, id `claude-md:<heading>`
- [x] The operating-constraints file, which has no headings, yields one record per bold-led paragraph
- [x] Commands including `.md.disabled` (flag `paused`, bytes 0), agents, output styles, and gitignored skills (tracked false) are enumerated
- [x] Output styles carry `unlinked` when the claude home has no output-styles directory or link; on the live setup the one style is flagged
- [x] Added dates: first commit for tracked files, first commit containing the heading for sections, mtime for untracked directories
- [x] The sidecar ships with every current CLAUDE.md heading; sections whose entry is absent or null render `—` and carry no trigger count; matched sections count history hits for the window and all-time
- [x] Double-quoted phrases of 8 to 80 characters in skill and command descriptions count as trigger phrases
- [x] `--surface` accepts each new surface name
- [x] Tests cover each surface, both flags, the unmeasured dash, and a sidecar match

## Comments

- 2026-09-18 — merged to `feat/retire-skill` in `5b3050c`. 125 items / 70,016 always-loaded chars. Improvement Mode and New Feature Mode report a measured `0/0` (not `—`); `output-style:adhd` flagged `unlinked`. Constraints file yields 7 bold-led paragraph records.

