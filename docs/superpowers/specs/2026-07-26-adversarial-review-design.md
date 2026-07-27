# adversarial-review — design spec

**Date:** 2026-07-26
**Status:** approved design, implemented same day
**Deliverable:** one new skill at `skills/adversarial-review/` (SKILL.md + two `references/` files, auto-invocable as `/adversarial-review` via the `~/.claude/skills` symlink), the repo's first two custom subagents at `agents/adversarial-reviewer.md` and `agents/review-judge.md`, one new bullet in CLAUDE.md's Git Workflow (the pre-merge gate), reference-doc rows, and two one-line routing corrections (`commands/brainstorm.md`, `skills/bug-hunt/SKILL.md`).
**Lineage:** adaptation of a Reddit-described two-model adversarial-review workflow (author writes, a context-free second model reviews the diff read-only, a neutral third model arbitrates, findings graded critical / should-fix / nice-to-have). Reviewer and judge are fresh zero-context Claude subagents rather than a cross-vendor model — the load-bearing property is "hasn't seen the author's context," not "different vendor." Severity discipline and the verify-against-real-code stance are consistent in spirit with `skills/bug-hunt/references/lenses-and-severity.md`.

## Purpose

Once real work is delegated to an agent, Kyle stops being the person who writes the
code and becomes the person answerable for it. The git workflow already grants
autonomous merges; this skill is what *earns* them. An author session always has
blind spots about its own work — the same context that produced the code re-reads
it charitably. The fix is structural, not exhortative: a reviewer whose only power
is ignorance, an author who must answer findings instead of skimming them, and a
judge who breaks the tie when the two disagree.

## Roles and the loop

- **Author** — the main session. Full task context. Triages findings, fixes what
  stands, owns the merge decision inputs.
- **Reviewer** (`adversarial-reviewer`, opus, zero context) — anchors to HEAD,
  reviews the branch diff vs merge-base, writes numbered graded findings to a
  mailbox file. Never edits the repo, never negotiates.
- **Judge** (`review-judge`, opus, zero context) — dispatched only when the author
  disputes findings. Verifies both sides against the actual code; rules upheld /
  overruled / downgraded / upgraded. "Valid but unimportant" is a downgrade, not an
  overrule — true findings don't get erased to unblock a merge.

Loop: preflight → review → author triage (accept / dispute with evidence; STOP for
Kyle in interactive runs) → judge on disputes → fix critical + should-fix → re-review
(max 2 re-rounds, VERIFIED/REOPENED) → PR comment + CLEAR / NOT-CLEAR verdict.

## Grades and the merge gate

- **critical** and **should-fix** block the merge until fixed-and-verified or waived
  *by Kyle, by name*. Waivers never happen on Kyle's behalf — in unattended runs an
  unfixed blocker means NOT CLEAR and no merge.
- **nice-to-have** never blocks and is never auto-fixed (scope discipline); it lands
  in the PR comment as a follow-up list.
- Escape hatch: trivial diffs (docs-only, comment-only, pure formatting, config-typo
  scale) may skip the loop, stated in the merge brief — never silently.

## The mailbox

`~/.claude/reviews/<repo-name>/<YYYY-MM-DD>-<branch-slug>.md` — the file all three
roles co-author as a thread (findings, triage lines, rulings, statuses). It lives
**outside the target repo** (no project pollution, no .gitignore surgery) and must
**never become a tracked top-level dir in claude-config** — install.sh symlinks every
tracked top-level entry, which would wire runtime state into the repo. The mailbox is
the working record; the PR comment is the durable one.

## Why the briefs live in the agent bodies

The primary launch path dispatches the named subagent types (user-level agents in
`~/.claude/agents/` are resolvable subagent types in current Claude Code; the old
note in `/brainstorm` predates this and is corrected in this change). The fallback —
for environments where the types don't resolve — pastes the agent file's body into a
`general-purpose` subagent. One canonical text that works both ways means no
drift between an agent file and a duplicate brief in `references/`.

## Round cap rationale

Reviewers always find *something*; without a cap the loop can oscillate (fix →
new nit → fix). Round 1 + at most 2 re-reviews ≈ worst case 3 reviewer + 3 judge
dispatches (each re-round's new findings get their own triage→judge pass). Anything still standing after the cap goes to Kyle as residue with
explicit options — never a third silent lap.

## Out of scope (v1)

- No changes to `ship-and-route` — it keeps its own release gate and may adopt this
  loop as that gate later.
- No cross-vendor (Codex) reviewer — revisit only if fresh-context Claude reviews
  prove blind to a class of defect a different vendor catches.
- No auto-fixing nice-to-haves, no hooks/settings.json enforcement (the gate is a
  CLAUDE.md git-workflow rule, like every other git rule).

## Definition of done

Skill + agents + references land in one commit with the CLAUDE.md bullet and
reference-doc rows; smoke test on a real branch shows: correct routing, agents
resolve (or fallback engages), mailbox created with anchors, judge rules on a
deliberate dispute, fix → VERIFIED on re-review, PR comment posted, NOT-CLEAR
verdict when a should-fix is left standing.
