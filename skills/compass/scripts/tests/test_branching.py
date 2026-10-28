"""`check` over a topic file after a session that branched both ways.

The file below is what the loop leaves behind when Kyle said "let me try" on Q1 (his answer as
checked, with Claude's correction and its source) and the answers spawned follow-ups two levels
deep, one of them logged later than Q2 so it sits below Q2 in the file.

Run from `skills/compass/scripts`:  python3 -m unittest discover
"""
import unittest

from tests.test_check import CheckCase

BRANCHED = """\
---
topic: Git rebase
why: I keep a clean branch history on shared repos and need to rebase without losing work.
status: open
workspace:
created: 2026-10-19
updated: 2026-10-20
---

# Git rebase

## Questions

### Q1: What does `git rebase main` actually do to my commits?
- status: answered
- answered by: kyle
- last recalled:

#### Answer
Held up: it replays each of my branch's commits on top of main's tip, one at a time.
Correction: the replayed commits are new commits with new hashes, not the originals moved; the
originals stay reachable through the reflog until they expire.

#### Sources
- git-rebase documentation — https://git-scm.com/docs/git-rebase

### Q1.1: Why does a rebased branch need a force push?
- status: answered
- answered by: claude
- last recalled:

#### Answer
The remote branch still points at the old commits, which the new ones don't descend from, so a
plain push is rejected as non-fast-forward.

#### Sources
- git-push documentation, --force-with-lease — https://git-scm.com/docs/git-push

### Q1.1.1: What does --force-with-lease protect against that --force doesn't?
- status: open
- last recalled:

### Q1.1.2: Can a teammate's pull break after I force-push?
- status: open
- last recalled:

### Q2: When should I merge instead of rebase?
- status: prereq
- last recalled:

### Q1.2: How do I get the originals back from the reflog?
- status: open
- last recalled:

## Session log
- 2026-10-19 — Started; logged Q1, Q2; Kyle answered Q1 (corrected); logged Q1.1, Q1.2.
- 2026-10-20 — Answered Q1.1; logged Q1.1.1, Q1.1.2.
"""

KYLE_SOURCES = "#### Sources\n- git-rebase documentation — https://git-scm.com/docs/git-rebase\n"
KYLE_ANSWER_BODY = BRANCHED.split("#### Answer\n", 1)[1].split("\n#### Sources", 1)[0]


class BranchedSessionTests(CheckCase):
    def test_a_session_with_let_me_try_and_nested_follow_ups_passes(self):
        rc, report = self.check(BRANCHED)
        self.assertEqual(rc, 0, report)
        self.assertEqual(report, {"valid": True, "violations": []})

    def test_a_checked_attempt_still_needs_the_sources_behind_its_corrections(self):
        self.assertViolation(BRANCHED.replace(KYLE_SOURCES, ""), "answered-needs-sources")

    def test_a_checked_attempt_still_needs_its_answer_written_down(self):
        self.assertViolation(BRANCHED.replace(KYLE_ANSWER_BODY, ""), "answered-needs-answer")

    def test_a_follow_up_under_a_missing_middle_question_is_reported(self):
        text = BRANCHED.replace("### Q1.1: Why does", "### Q1.3: Why does")
        found = self.rules(text)
        self.assertEqual(found.count("tree-orphan"), 2, found)


if __name__ == "__main__":
    unittest.main()
