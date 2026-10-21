"""`compass.py check` over throwaway topic files.

Each test writes one small topic file into a fresh temp folder, drives the script through its
command line, and asserts only on what comes out: the JSON report and the exit code. Nothing
here imports the script or reads the live ~/Learning folder.

Run from `skills/compass/scripts`:  python3 -m unittest discover
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "compass.py"

VALID = """\
---
topic: Rust lifetimes
why: I review Rust PRs at work and need to read borrow-checker errors without guessing.
status: open
workspace:
created: 2026-10-18
updated: 2026-10-20
---

# Rust lifetimes

## Questions

### Q1: What does `'a` actually constrain?
- status: answered
- answered by: claude
- last recalled:

#### Answer
It constrains how long a reference may be used, not how long the value lives.

#### Sources
- The Rust Book, ch. 10.3 — https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html

### Q1.1: Why can't the compiler infer it in a function signature?
- status: open
- last recalled:

### Q2: Do I need to understand variance first?
- status: parked
- park reason: Variance matters for library authors; my why is reading errors.
- last recalled:

## Session log
- 2026-10-18 — Started; logged Q1, Q2; answered Q1.
- 2026-10-20 — Parked Q2; logged Q1.1.
"""


class CheckCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def check(self, text: str):
        path = self.root / "topic.md"
        path.write_text(text)
        proc = subprocess.run([sys.executable, str(SCRIPT), "check", str(path)],
                              capture_output=True, text=True)
        return proc.returncode, json.loads(proc.stdout) if proc.stdout.strip() else None

    def rules(self, text: str) -> list:
        rc, report = self.check(text)
        self.assertNotEqual(rc, 0, "an invalid file must exit non-zero")
        self.assertFalse(report["valid"])
        return [v["rule"] for v in report["violations"]]

    def assertViolation(self, text: str, rule: str):
        found = self.rules(text)
        self.assertIn(rule, found)


class ValidFileTests(CheckCase):
    def test_a_valid_file_passes_with_exit_zero(self):
        rc, report = self.check(VALID)
        self.assertEqual(rc, 0, report)
        self.assertEqual(report, {"valid": True, "violations": []})


class FrontmatterTests(CheckCase):
    def test_each_missing_required_field_is_reported(self):
        for field in ("topic", "why", "status", "created", "updated"):
            with self.subTest(field=field):
                text = "\n".join(l for l in VALID.splitlines() if not l.startswith(f"{field}:"))
                rc, report = self.check(text + "\n")
                self.assertEqual(rc, 1)
                messages = [v["message"] for v in report["violations"]
                            if v["rule"] == "frontmatter-field"]
                self.assertTrue(any(field in m for m in messages), report)

    def test_workspace_is_optional(self):
        rc, report = self.check(VALID.replace("workspace:\n", ""))
        self.assertEqual(rc, 0, report)

    def test_a_topic_seeded_from_a_teach_workspace_passes(self):
        # What `--from ~/Learning/rust/MISSION.md` writes once Kyle accepts the proposal: the
        # workspace link, the accepted why, open starter questions, a one-line log entry.
        seeded = """\
---
topic: Rust lifetimes
why: Read borrow-checker errors in work PRs without guessing.
status: open
workspace: ~/Learning/rust lifetimes
created: 2026-10-20
updated: 2026-10-20
---

# Rust lifetimes

## Questions

### Q1: What does a lifetime annotation constrain?
- status: open
- last recalled:

### Q2: When does the compiler need one written out?
- status: open
- last recalled:

## Session log
- 2026-10-20 — Started from ~/Learning/rust lifetimes/MISSION.md; logged Q1, Q2.
"""
        rc, report = self.check(seeded)
        self.assertEqual(rc, 0, report)
        self.assertEqual(report, {"valid": True, "violations": []})

    def test_an_empty_why_counts_as_missing(self):
        self.assertViolation(VALID.replace("why: I review", "why:\nx: I review"),
                             "frontmatter-field")

    def test_a_file_without_frontmatter_is_reported(self):
        self.assertViolation(VALID.split("---\n", 2)[2], "frontmatter-missing")

    def test_a_topic_status_outside_open_or_closed_is_reported(self):
        self.assertViolation(VALID.replace("status: open\nworkspace", "status: done\nworkspace"),
                             "topic-status")

    def test_a_malformed_date_is_reported(self):
        self.assertViolation(VALID.replace("updated: 2026-10-20", "updated: Oct 20"),
                             "frontmatter-date")


Q1_ANSWER = ("#### Answer\nIt constrains how long a reference may be used, "
             "not how long the value lives.\n\n")
Q1_SOURCES = ("#### Sources\n- The Rust Book, ch. 10.3 — "
              "https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html\n\n")


class QuestionTests(CheckCase):
    def test_a_question_status_outside_the_four_is_reported(self):
        text = VALID.replace("- status: open\n- last recalled:\n\n### Q2",
                             "- status: todo\n- last recalled:\n\n### Q2")
        self.assertViolation(text, "question-status")

    def test_a_question_without_a_status_is_reported(self):
        text = VALID.replace("- status: open\n- last recalled:\n\n### Q2",
                             "- last recalled:\n\n### Q2")
        self.assertViolation(text, "question-status")

    def test_prereq_is_a_valid_status(self):
        text = VALID.replace("- status: open\n- last recalled:\n\n### Q2",
                             "- status: prereq\n- last recalled:\n\n### Q2")
        rc, report = self.check(text)
        self.assertEqual(rc, 0, report)

    def test_an_answered_question_without_an_answer_is_reported(self):
        self.assertViolation(VALID.replace(Q1_ANSWER, ""), "answered-needs-answer")

    def test_an_answered_question_with_an_empty_answer_is_reported(self):
        self.assertViolation(VALID.replace(Q1_ANSWER, "#### Answer\n\n"), "answered-needs-answer")

    def test_an_answered_question_without_sources_is_reported(self):
        self.assertViolation(VALID.replace(Q1_SOURCES, ""), "answered-needs-sources")

    def test_an_answered_question_with_an_empty_sources_list_is_reported(self):
        self.assertViolation(VALID.replace(Q1_SOURCES, "#### Sources\n\n"),
                             "answered-needs-sources")

    def test_an_answered_question_must_say_who_answered(self):
        self.assertViolation(VALID.replace("- answered by: claude\n", ""), "answered-by")
        self.assertViolation(VALID.replace("answered by: claude", "answered by: bob"),
                             "answered-by")

    def test_kyle_is_a_valid_answerer(self):
        rc, report = self.check(VALID.replace("answered by: claude", "answered by: kyle"))
        self.assertEqual(rc, 0, report)

    def test_a_parked_question_without_a_reason_is_reported(self):
        text = "\n".join(l for l in VALID.splitlines() if not l.startswith("- park reason:"))
        self.assertViolation(text + "\n", "parked-needs-reason")

    def test_a_malformed_last_recalled_date_is_reported(self):
        text = VALID.replace("- answered by: claude\n- last recalled:",
                             "- answered by: claude\n- last recalled: last week")
        self.assertViolation(text, "last-recalled-date")

    def test_a_dated_last_recalled_passes(self):
        text = VALID.replace("- answered by: claude\n- last recalled:",
                             "- answered by: claude\n- last recalled: 2026-10-19")
        rc, report = self.check(text)
        self.assertEqual(rc, 0, report)

    def test_an_unknown_field_is_reported_so_typos_surface(self):
        self.assertViolation(VALID.replace("- status: answered", "- statsu: answered"),
                             "question-field")

    def test_stray_text_among_the_fields_is_reported(self):
        self.assertViolation(VALID.replace("- answered by: claude\n",
                                           "- answered by: claude\nsome note\n"),
                             "question-field")

    def test_a_malformed_question_heading_is_reported(self):
        self.assertViolation(VALID.replace("### Q2: Do I", "### Do I"), "question-heading")

    def test_an_unknown_question_subsection_is_reported(self):
        self.assertViolation(VALID.replace("#### Sources", "#### Links"), "question-subsection")

    def test_broken_tree_numbers_are_reported(self):
        for bad in ("Q0", "Q1.0", "Q01", "Q1..1", "Q1.", "Q.1"):
            with self.subTest(number=bad):
                self.assertViolation(VALID.replace("### Q1.1:", f"### {bad}:"), "tree-number")

    def test_a_duplicate_tree_number_is_reported(self):
        self.assertViolation(VALID.replace("### Q2:", "### Q1:"), "tree-duplicate")

    def test_a_child_without_its_parent_is_reported(self):
        self.assertViolation(VALID.replace("### Q1.1:", "### Q3.1:"), "tree-orphan")

    def test_a_grandchild_needs_its_direct_parent_not_just_the_root(self):
        self.assertViolation(VALID.replace("### Q1.1:", "### Q1.2.1:"), "tree-orphan")

    def test_gaps_in_numbering_are_allowed_because_numbers_are_stable(self):
        rc, report = self.check(VALID.replace("### Q2:", "### Q5:"))
        self.assertEqual(rc, 0, report)

    def test_headings_inside_a_fenced_code_block_are_answer_text(self):
        text = VALID.replace(Q1_ANSWER, "#### Answer\nLike this:\n\n```\n### Q9: not a question\n"
                                        "## Not a section\n```\n\n")
        rc, report = self.check(text)
        self.assertEqual(rc, 0, report)


OVERVIEW = """\
## Overview
- Key idea: a lifetime names a region of code where a borrow is valid.

Sources: The Rust Book ch. 10.3.

"""

CLOSE_OUT = """\
## Close-out
Lifetimes are regions the borrow checker proves references stay inside; reading an error
means finding which two regions it says don't nest.

"""


def closed(text: str, close_out: bool = True) -> str:
    text = text.replace("status: open\nworkspace", "status: closed\nworkspace")
    return text.replace("## Session log", CLOSE_OUT + "## Session log") if close_out else text


class SectionTests(CheckCase):
    def test_an_overview_before_questions_is_valid(self):
        rc, report = self.check(VALID.replace("## Questions", OVERVIEW + "## Questions"))
        self.assertEqual(rc, 0, report)

    def test_a_closed_topic_with_a_close_out_is_valid(self):
        rc, report = self.check(closed(VALID))
        self.assertEqual(rc, 0, report)

    def test_a_closed_topic_without_a_close_out_is_reported(self):
        self.assertViolation(closed(VALID, close_out=False), "closed-needs-close-out")

    def test_a_closed_topic_with_an_empty_close_out_is_reported(self):
        text = closed(VALID).replace(CLOSE_OUT, "## Close-out\n\n")
        self.assertViolation(text, "closed-needs-close-out")

    def test_a_close_out_on_an_open_topic_is_reported(self):
        text = VALID.replace("## Session log", CLOSE_OUT + "## Session log")
        self.assertViolation(text, "close-out-on-open")

    def test_missing_required_sections_are_reported(self):
        no_log = VALID.split("## Session log")[0]
        self.assertViolation(no_log, "section-missing")
        no_questions = VALID.replace("## Questions\n", "")
        self.assertViolation(no_questions, "section-missing")

    def test_a_topic_with_no_questions_yet_is_valid(self):
        head, _, _ = VALID.partition("### Q1:")
        rc, report = self.check(head + "## Session log\n")
        self.assertEqual(rc, 0, report)

    def test_an_unknown_section_is_reported(self):
        self.assertViolation(VALID.replace("## Session log", "## Notes\nx\n\n## Session log"),
                             "section-unknown")

    def test_sections_out_of_order_are_reported(self):
        text = VALID.replace("## Questions", "## Session log\n\n## Questions", 1)
        text = text[::-1].replace("gol noisseS ##", "", 1)[::-1]
        self.assertViolation(text, "section-order")

    def test_a_section_appearing_twice_is_reported(self):
        self.assertViolation(VALID + "\n## Questions\n", "section-duplicate")

    def test_an_undated_session_log_entry_is_reported(self):
        self.assertViolation(VALID + "- Did some more.\n", "session-log-entry")

    def test_an_indented_continuation_of_a_log_entry_is_fine(self):
        rc, report = self.check(VALID + "  and wrapped onto a second line.\n")
        self.assertEqual(rc, 0, report)


class ReportTests(CheckCase):
    def test_every_violation_is_reported_not_just_the_first(self):
        text = (VALID.replace("status: open\nworkspace", "status: done\nworkspace")
                .replace(Q1_SOURCES, "")
                .replace("- park reason: Variance matters for library authors; "
                         "my why is reading errors.\n", "")
                .replace("### Q1.1:", "### Q4.1:"))
        found = self.rules(text)
        for rule in ("topic-status", "answered-needs-sources", "parked-needs-reason", "tree-orphan"):
            self.assertIn(rule, found)

    def test_each_violation_names_its_line(self):
        rc, report = self.check(VALID.replace("### Q1.1:", "### Q3.1:"))
        line = VALID.splitlines().index("### Q1.1: Why can't the compiler infer it in a "
                                        "function signature?") + 1
        self.assertEqual([v["line"] for v in report["violations"]], [line])

    def test_an_unreadable_file_exits_two(self):
        proc = subprocess.run([sys.executable, str(SCRIPT), "check", str(self.root / "nope.md")],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("error", json.loads(proc.stdout))


if __name__ == "__main__":
    unittest.main()
