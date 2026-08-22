# Mailbox format

The mailbox is one Markdown file that all three roles co-author, so a finished review reads as a thread: the reviewer files findings, the author answers each one, the judge rules on the disputed ones, and statuses track the whole life of every finding. The orchestrator (author session) creates it in Phase 0; the reviewer and judge only ever append to it.

## Path

```
~/.claude/reviews/<repo-name>/<YYYY-MM-DD>-<branch-slug>.md
```

- `branch-slug`: the branch name with `/` replaced by `-` (`feat/foo` → `feat-foo`).
- `mkdir -p ~/.claude/reviews/<repo-name>/` before creating the file.
- Re-runs on the same branch and day **never recreate the file** — Phase 0 appends a `## Run <n> — <date>` separator instead, and finding numbers continue from the existing highest across runs. Round numbers continue too: a continuation run's first dispatch is a re-review — it verifies carried `FIXED-IN` findings, reviews the diff since the last reviewed sha, and picks up any file-groups earlier rounds recorded as uncovered — never a fresh `ROUND=1`. Waivers and rulings are part of the record; overwriting them is destruction, not tidiness.
- The mailbox lives **outside the target repo** — no project pollution, no .gitignore surgery, and the reviewer's write access never points at the repository.
- `reviews/` must **never become a tracked directory in claude-config**: install.sh symlinks every tracked top-level entry not on its DENY list into `~/.claude`, which would wire runtime state into the config repo. (Belt-and-suspenders: `reviews/` is in this repo's `.gitignore`.)
- The mailbox is the working record. The PR comment (template below) is the durable one.

## Header block (orchestrator, Phase 0)

```
# Adversarial review — <repo-name> · <branch>

- Repo: <absolute path>
- Branch: <branch> → <default-branch>
- Merge-base: <sha>
- PR: <url, or "not yet open">
```

## Round sections (reviewer)

Each review pass appends `## Round <N> — reviewed at <HEAD sha> (<date>)` with the reviewer's recorded anchors (`HEAD`, `git status` summary, merge-base) and a **`Coverage:` line** (`Coverage: complete` or `Coverage: unclosed — <groups>`) stating what the round actually read, then its findings. Round ≥ 2 sections contain the verification lines for previously fixed findings plus any findings newly raised from the diff since the last reviewed sha — including from file-groups earlier rounds left uncovered.

## Finding entries (reviewer)

Numbered `F1, F2, …`, continuing from the file's existing highest number across rounds:

```
### F<n> · [<grade>] <one-line title>
- Where: <file>:<line>
- Claim: <what is wrong and when it bites>
- Evidence: <quoted code or traced path>
- Suggested fix (advisory only): <optional>

Status: OPEN
```

Grades: `critical` / `should-fix` / `nice-to-have` (definitions and gate meaning: `severity-and-scope.md`).

## Thread lines (appended per finding, in order)

```
Triage (author): ACCEPT — <one-line note>
Triage (author): DISPUTE — <evidence-based rebuttal, citing code or tests>
Ruling (judge): <UPHELD | OVERRULED | DOWNGRADED to <grade> | UPGRADED to <grade>> — <one paragraph>
Verification (reviewer): <VERIFIED | REOPENED — <why>>
Status: <current status>
```

The `Status:` line is kept current by whoever last acted. Nobody rewrites or deletes anyone else's words — the thread is append-only.

## Status state machine

```
OPEN ─▶ ACCEPTED ──────────────────────────┐   (accepted nice-to-have → FOLLOW-UP directly, no fix)
  └──▶ DISPUTED ─▶ UPHELD ─────────────────┤
                 ├▶ DOWNGRADED to <grade> ─┤   (blocking grades continue; nice-to-have → FOLLOW-UP)
                 ├▶ UPGRADED to <grade> ───┤
                 └▶ CLOSED (overruled)     │
                                           ▼
                          FIXED-IN <sha> ─▶ VERIFIED | REOPENED
```

Terminal states: `VERIFIED`, `CLOSED (overruled)`, `WAIVED-BY-KYLE (<his words>)`, `FOLLOW-UP` (nice-to-have, listed in the PR comment), and — under a SINGLE ROUND scope only, when the round produced no critical — `FIXED-IN <sha> (self-verified)` (the author's own verification stands in for the reviewer's; PR-comment disposition reads "Fixed in <sha>, self-verified (single round)"). Plain `FIXED-IN <sha>` without the marker remains non-terminal and awaits `VERIFIED | REOPENED`. `REOPENED` goes back onto the author's plate within the round cap. An unclosed **coverage bound** has its own disposition, separate from findings: closed by a later round's review, or `COVERAGE-WAIVED-BY-KYLE (<his words>)` at the cap-residue prompt or Phase 6's pre-verdict coverage check.

## PR comment template (orchestrator, Phase 6)

```
## Adversarial review — <CLEAR TO MERGE | NOT CLEAR> (rounds: <N>)

| # | Severity (final) | Finding | Disposition |
|---|---|---|---|
| F1 | critical | <title> | Fixed in <sha>, verified |
| F2 | should-fix → nice-to-have | <title> | Downgraded by judge → follow-up |
| F3 | should-fix | <title> | Disputed → overruled, closed |

**Waived by Kyle:** <F<n> — reason, verbatim>            (omit if none)
**Follow-ups (nice-to-have):** <F<n> <title>; …>          (omit if none)
**Coverage:** <complete | unclosed: <groups> | waived by Kyle>   (an unclosed, unwaived bound alone forces NOT CLEAR)
**Still standing:** <F<n> <title> — why>                  (only on NOT CLEAR; omit when empty — a coverage-only NOT CLEAR is named by the Coverage line)

Zero-context reviewer + neutral judge on disputes; anchored at <final HEAD sha>.
```
