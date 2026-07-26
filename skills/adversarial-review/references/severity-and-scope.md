# Severity grades and the escape hatch

Orchestrator-side calibration: how findings gate the merge, and which diffs may skip the loop. (What the reviewer *hunts for* lives in the reviewer's own brief, `~/.claude/agents/adversarial-reviewer.md`, so the brief stays self-contained for the fallback launch path. Consistent in spirit with `bug-hunt`'s severity reference, but this file is the authority for merge-gate decisions.)

## The three grades

| Grade | Meaning | Merge gate |
|---|---|---|
| **critical** | Data loss, security exposure, crash or wrong results on a realistic path. | Blocks. Fixed-and-verified, or waived by Kyle by name — no other exit. |
| **should-fix** | A real defect or contract violation a user or maintainer will plausibly hit; bounded blast radius. | Blocks until fixed or Kyle-waived. |
| **nice-to-have** | Valid but unimportant: style, naming, micro-perf, a latent edge with no live path. | Never blocks. Never auto-fixed. Listed as follow-ups in the PR comment. |

**Anti-inflation.** Grade blast radius, not confidence — a finding you're unsure of gets its uncertainty stated in the claim, not a lower grade. Reviewers always come back with *something*; the nice-to-have grade exists precisely so real-but-unimportant findings have somewhere honest to go. A calibrated-low list beats an alarmist one — inflated grades train the author to dispute everything and the judge to discount the reviewer.

## Escape hatch — what "trivial" means

A diff qualifies for skipping the loop only if **all** of its changes are:

- docs-only (README, comments, prose files), or
- pure formatting with no semantic change, or
- config-typo scale (fixing a label, a string, a version bump with no code path implications).

**Disqualifiers — always run the loop** if the diff touches: executable code paths, dependencies or lockfiles, CI/workflow files, auth or permissions, data handling (schemas, migrations, serialization), or install-class scripts (anything that runs on someone's machine at setup).

A skip taken under the pre-merge gate must be **stated in the merge brief** ("skipped adversarial review: docs-only") — never silent. When in doubt, it isn't trivial.
