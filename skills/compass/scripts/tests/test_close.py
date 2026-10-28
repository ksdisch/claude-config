"""A topic through close and reopen: `check` on each file the procedure leaves, and `list` on it.

CLOSED is what *Close a topic* writes: nothing open, the parked question kept with its reason,
Kyle's why-answer as the Close-out, `status: closed`. REOPENED is what *Reopen* then writes from
it: `status: open`, the Close-out section gone but its text carried into the session log as an
indented continuation of the reopen entry, every question kept, and a new question logged.

Run from `skills/compass/scripts`:  python3 -m unittest discover
"""
import json
import subprocess
import sys
import unittest

from tests.test_check import SCRIPT, CheckCase

CLOSED = """\
---
topic: Git rebase
why: I keep a clean branch history on shared repos and need to rebase without losing work.
status: closed
workspace:
created: 2026-10-19
updated: 2026-10-21
---

# Git rebase

## Questions

### Q1: What does `git rebase main` actually do to my commits?
- status: answered
- answered by: claude
- last recalled: 2026-10-21

#### Answer
It replays each of my commits onto main's tip as new commits with new hashes.

#### Sources
- git-rebase docs — https://git-scm.com/docs/git-rebase

### Q2: How do rebase internals store the todo list?
- status: parked
- park reason: Internals don't change how I rebase safely; my why is not losing work.
- last recalled:

## Close-out
Rebase rewrites my commits as new ones on top of main, so it's safe on my own branch and
unsafe on a shared one; the reflog is how I get lost work back.

## Session log
- 2026-10-19 — Started; logged Q1, Q2; answered Q1.
- 2026-10-21 — Parked Q2; closed.
"""

REOPENED = """\
---
topic: Git rebase
why: I keep a clean branch history on shared repos and need to rebase without losing work.
status: open
workspace:
created: 2026-10-19
updated: 2026-10-30
---

# Git rebase

## Questions

### Q1: What does `git rebase main` actually do to my commits?
- status: answered
- answered by: claude
- last recalled: 2026-10-21

#### Answer
It replays each of my commits onto main's tip as new commits with new hashes.

#### Sources
- git-rebase docs — https://git-scm.com/docs/git-rebase

### Q2: How do rebase internals store the todo list?
- status: parked
- park reason: Internals don't change how I rebase safely; my why is not losing work.
- last recalled:

### Q3: What does `--update-refs` change for stacked branches?
- status: open
- last recalled:

## Session log
- 2026-10-19 — Started; logged Q1, Q2; answered Q1.
- 2026-10-21 — Parked Q2; closed.
- 2026-10-30 — Reopened; logged Q3. Earlier close-out:
  Rebase rewrites my commits as new ones on top of main, so it's safe on my own branch and
  unsafe on a shared one; the reflog is how I get lost work back.
"""


class CloseAndReopenCheckTests(CheckCase):
    def test_a_closed_topic_keeping_its_parked_question_passes(self):
        rc, report = self.check(CLOSED)
        self.assertEqual(rc, 0, report)

    def test_a_reopened_topic_carrying_its_close_out_in_the_log_passes(self):
        rc, report = self.check(REOPENED)
        self.assertEqual(rc, 0, report)

    def test_reopening_without_removing_the_close_out_section_is_caught(self):
        kept = CLOSED.replace("status: closed", "status: open")
        self.assertViolation(kept, "close-out-on-open")


class CloseAndReopenListTests(CheckCase):
    def list_one(self, text):
        (self.root / "git-rebase.md").write_text(text)
        proc = subprocess.run([sys.executable, str(SCRIPT), "list", "--dir", str(self.root)],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        [row] = json.loads(proc.stdout)["topics"]
        return row

    def test_a_closed_topic_lists_as_closed_with_its_parked_question_counted(self):
        row = self.list_one(CLOSED)
        self.assertEqual(row["status"], "closed")
        self.assertEqual(row["counts"], {"open": 0, "answered": 1, "parked": 1, "prereq": 0})

    def test_a_reopened_topic_lists_as_open_with_nothing_removed(self):
        row = self.list_one(REOPENED)
        self.assertEqual(row["status"], "open")
        self.assertEqual(row["counts"], {"open": 1, "answered": 1, "parked": 1, "prereq": 0})


if __name__ == "__main__":
    unittest.main()
