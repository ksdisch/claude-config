---
name: adversarial-review
description: Pre-merge adversarial review loop — a structured author↔reviewer↔judge dialogue over the current branch's diff. Dispatches a zero-context reviewer subagent that writes numbered findings graded critical / should-fix / nice-to-have to a mailbox file; the author (this session) triages each finding (accept, or dispute with evidence); a neutral zero-context judge rules on disputes (uphold / overrule / re-grade); standing blockers get fixed and re-checked (max 2 re-review rounds); the adjudicated summary lands as a PR comment with a CLEAR / NOT-CLEAR merge verdict. This is the standing pre-merge gate in the global git workflow — run it before autonomously merging any PR (escape hatch: trivial docs-only / pure-formatting / config-typo diffs may skip, stated in the merge brief). Also use whenever Kyle types /adversarial-review or says "adversarial review", "adv review", "red-team this diff", "red-team this PR", "second set of eyes before merge", "run the review loop". NOT for: proactive defect hunts over a codebase or subsystem with no merge in play (use bug-hunt), the full end-of-build land-everything-and-chart-next-steps release flow (use ship-and-route), or a one-shot review with no triage/judge dialogue (use the plugin's /code-review or /security-review).
---

# Adversarial Review

**You are the Author.** You have full context on this change — which is exactly why you can't be the only one to check it: the context that produced the code re-reads it charitably. The reviewer's power is its ignorance; the judge exists because reviewers always find *something* and authors always want to merge. Grades let the judge say "valid, but unimportant."

| Role | Who | Power |
|---|---|---|
| Author | this session | triages findings, fixes what stands — decides nothing unilaterally about disputed findings |
| Reviewer | `adversarial-reviewer` (opus, zero context) | files graded findings in the mailbox; edits nothing |
| Judge | `review-judge` (opus, zero context) | rules on disputed findings only; rulings final for the run |

**Launching them.** Dispatch by subagent type (`adversarial-reviewer`, `review-judge`). If the named type doesn't resolve in this environment, fall back: launch a `general-purpose` subagent with the agent's brief (frontmatter stripped) pasted verbatim as the prompt preamble, followed by the same input block. Read the brief from `~/.claude/agents/<name>.md` when installed; when it isn't (the usual case when the type doesn't resolve), read `agents/<name>.md` from the claude-config checkout (`readlink ~/.claude/agents` resolves it when symlinked). **No readable brief → no dispatch** — stop and say so; an improvised reviewer defeats the mechanism. Either path, hand the agent **only the input block** — no task context, no design rationale, no "this is fine because…". Contaminating the reviewer with your context defeats the entire mechanism.

**The untouched check — around every dispatch.** Immediately before dispatching either agent, capture `git rev-parse HEAD`, `git branch --show-current`, and `git stash list | wc -l`. When the agent returns, assert all three unchanged **and** `git status --porcelain` empty. A clean tree alone proves nothing — it's the expected post-state of a stray commit, checkout, stash, push, or hard reset.

## Phase 0 — Preflight

1. `git branch --show-current` — on the default branch, refuse: the loop reviews a branch diff, and nothing merges from `main` to `main`.
2. Resolve the default branch and `git merge-base`. `git status` — uncommitted work gets committed first, or you state explicitly that only committed work is being reviewed.
3. Escape-hatch check against `references/severity-and-scope.md`. Trivial diff → offer the skip; a skip taken under the pre-merge gate is stated in the merge brief, never silent. When in doubt, it isn't trivial.
4. `mkdir -p ~/.claude/reviews/<repo-name>/`. Mailbox absent → create it with the header block from `references/mailbox-format.md`. Mailbox already present (same branch, same day — e.g. re-running after NOT CLEAR or a hit round cap) → **never overwrite it**: append a `## Run <n> — <date>` separator and carry finding numbering forward. A continuation run resumes the loop, it doesn't restart it: prior findings still in blocking states (`OPEN`, `UPHELD`, `REOPENED`, `FIXED-IN`) are this run's first order of business, and its first reviewer dispatch continues the round numbering (`ROUND=<previous highest + 1>` — never `ROUND=1` into an existing mailbox), so carried `FIXED-IN` findings get verified and the diff since the last reviewed sha gets reviewed. Any file-group a prior round recorded as uncovered is part of this run's review scope — uncovered groups are never "already-reviewed diff". Waivers and rulings are part of the record.
5. One-line launch statement: scope (branch → default, files/lines), mailbox path, expected dispatch count.

## Phase 1 — Review (round 1)

Dispatch the reviewer with: `REPO_PATH`, `DEFAULT_BRANCH`, `MAILBOX_PATH`, `ROUND=1` (a continuation run dispatches at the next round number instead — Phase 0). It anchors to HEAD, reviews the diff vs merge-base, writes findings to the mailbox, returns one counts line. When it returns: run the untouched check, then read the mailbox. Zero findings → Phase 6 with a clean verdict **when coverage is complete** — a legitimate outcome, not a failed review. A bounded-coverage round with zero findings is not clean: its uncovered groups still gate the verdict.

## Phase 2 — Triage (present, then STOP)

For each finding, append to its mailbox thread `Triage (author): ACCEPT — <note>` or `Triage (author): DISPUTE — <evidence-based rebuttal citing code or tests>`, and update `Status:`. "I meant to do that" is not a rebuttal — intent that isn't visible in the code is itself a finding about the code.

Present the triage table (# · grade · verdict · one-line reason), then **STOP**. Kyle can flip verdicts, waive findings by name (`WAIVED-BY-KYLE`, his words recorded verbatim), or say proceed. **Unattended runs: proceed without pausing — but waivers never happen on Kyle's behalf; an unfixed blocker stays a blocker.**

## Phase 3 — Judge (only if disputes exist)

No disputes → skip to Phase 4. Otherwise dispatch the judge with: `REPO_PATH`, `MAILBOX_PATH`. It verifies both sides against the code and appends one-paragraph rulings. Run the untouched check again, read the rulings: overruled findings close; upheld or re-graded-blocking findings go back on your plate. Rulings are final for this run — you don't re-litigate, you fix or Kyle waives.

## Phase 4 — Fix

Fix every standing **critical** and **should-fix** (accepted, upheld, or upgraded). Nice-to-haves are **not** fixed now — scope discipline; they become `FOLLOW-UP` and land in the PR comment. Commit on the branch, then mark each fixed finding `FIXED-IN <sha>` in the mailbox.

## Phase 5 — Re-review (hard cap: 2 re-review dispatches per run — round numbers continue across runs, the cap does not)

Re-dispatch the reviewer with `ROUND=<N>`. It verifies each `FIXED-IN` finding (`VERIFIED` / `REOPENED`) and may raise new findings only if the fixes introduced them; new findings get one triage→judge pass. Anything still standing after the cap → **STOP and present the residue** to Kyle with options: fix without re-verify (recorded as `WAIVED-BY-KYLE (re-verify waived)` — a verification waiver, which terminates the finding), waive outright, or hold the merge. Never a third silent lap.

## Phase 6 — Publish + verdict

Render the PR comment from the template in `references/mailbox-format.md` (disposition table, waivers verbatim, follow-ups, standing items on NOT CLEAR) and post it — `gh pr comment` if available, else the GitHub MCP tools; if neither works, print the comment in full and say plainly that it wasn't posted. Then declare:

- **CLEAR TO MERGE** — no finding remains in a blocking state (every critical and should-fix ends `VERIFIED`, `CLOSED (overruled)`, downgraded to nice-to-have (`FOLLOW-UP`), or `WAIVED-BY-KYLE`) **and no round's stated coverage bound is left unclosed** — every changed file was covered by some round.
- **NOT CLEAR** — anything blocking still stands, **or any round's coverage bound is left unclosed**; name it. No merge.

The merge itself follows the normal git workflow (brief with commit SHA, PR link, and this verdict).

## Token discipline

Worst case ≤3 reviewer + ≤2 judge dispatches per run, all opus — verdict work is where opus earns its cost. Agents write detail to the mailbox and return one counts line; you read the mailbox instead of re-deriving it. Big diffs (~2k+ lines): the reviewer batches file-groups into the one mailbox and states coverage bounds — bounded coverage is fine, silent truncation is not. If context is tight, `/compact` at the triage→fix seam.

## Autonomy boundary

- ✅ **Without asking:** all git reads, mailbox creation, reviewer/judge dispatches, writing triage, fixing accepted/upheld findings, committing on the branch, posting the PR comment, declaring the verdict.
- ⛔ **Never without an explicit per-run go-ahead:** waiving a critical or should-fix (Kyle-only, by name), skipping the loop on a non-trivial diff, exceeding the round cap.
- ⛔ **Never:** reviewer or judge modifying repo files; merging with a critical/should-fix still in a blocking state — neither fixed-and-verified, closed or downgraded by the judge, nor Kyle-waived; merging while any round's stated coverage bound is unclosed; running the loop without a mailbox record; auto-fixing nice-to-haves.
