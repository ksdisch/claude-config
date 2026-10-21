"""Regression tests for the code-review findings on compass.py, each reproducing its failure
scenario through the command line.

Run from `skills/compass/scripts`:  python3 -m unittest discover
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.test_check import VALID

SCRIPT = Path(__file__).resolve().parent.parent / "compass.py"


def run(*args):
    proc = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
    return proc.returncode, json.loads(proc.stdout)


def topic_file(topic):
    return (f"---\ntopic: {topic}\nwhy: Because.\nstatus: open\nworkspace:\n"
            f"created: 2026-10-18\nupdated: 2026-10-20\n---\n\n# {topic}\n\n## Questions\n\n"
            f"## Session log\n- 2026-10-18 — Started.\n")


class Case(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def check(self, text, encoding="utf-8"):
        path = self.root / "topic.md"
        path.write_text(text, encoding=encoding)
        return run("check", str(path))

    def rules(self, text):
        rc, report = self.check(text)
        return rc, [v["rule"] for v in report["violations"]]

    def match(self, query):
        rc, out = run("match", query, "--dir", str(self.root))
        return rc, out


class UnicodeMatchTests(Case):
    def setUp(self):
        super().setUp()
        (self.root / "c.md").write_text(topic_file("C++"))
        (self.root / "berkeley.md").write_text(topic_file("Berkeley sockets"))

    def test_c_sharp_does_not_resolve_to_c_plus_plus(self):
        rc, out = self.match("C#")
        self.assertEqual((rc, out["result"]), (0, "none"), out)

    def test_non_ascii_letters_are_kept(self):
        rc, out = self.match("über")
        self.assertEqual((rc, out["result"]), (0, "none"), out)

    def test_non_latin_query_is_accepted(self):
        (self.root / "nihongo.md").write_text(topic_file("日本語 grammar"))
        rc, out = self.match("日本語")
        self.assertEqual((rc, out["result"], [m["slug"] for m in out["matches"]]),
                         (0, "single", ["nihongo"]), out)

    def test_word_prefix_still_matches(self):
        rc, out = self.match("berk")
        self.assertEqual(out["result"], "single")


class FenceTests(Case):
    def test_quoted_backtick_fence_inside_tilde_fence_does_not_swallow_the_file(self):
        text = VALID.replace(
            "It constrains how long a reference may be used, not how long the value lives.\n",
            "Example:\n~~~markdown\n```rust\nfn x() {}\n~~~\n").replace(
            "- status: parked", "- status: bogus")
        rc, rules = self.rules(text)
        self.assertIn("question-status", rules)
        self.assertNotIn("section-missing", rules)
        self.assertNotIn("answered-needs-sources", rules)


class RepeatedSubsectionTests(Case):
    def test_repeated_sources_is_reported(self):
        text = VALID.replace("### Q1.1:", "#### Sources\n\n### Q1.1:")
        rc, rules = self.rules(text)
        self.assertIn("question-subsection", rules)
        self.assertNotIn("answered-needs-sources", rules)


class QuestionFormatTests(Case):
    def test_empty_question_text(self):
        rc, rules = self.rules(VALID.replace("### Q2: Do I need to understand variance first?",
                                             "### Q2:"))
        self.assertIn("question-heading", rules)

    def test_missing_last_recalled(self):
        rc, rules = self.rules(VALID.replace(
            "- status: open\n- last recalled:\n", "- status: open\n"))
        self.assertIn("question-field", rules)

    def test_answered_by_on_open_question(self):
        rc, rules = self.rules(VALID.replace(
            "- status: open\n", "- status: open\n- answered by: claude\n"))
        self.assertIn("question-field", rules)

    def test_park_reason_on_open_question(self):
        rc, rules = self.rules(VALID.replace(
            "- status: open\n", "- status: open\n- park reason: x\n"))
        self.assertIn("question-field", rules)

    def test_subsection_on_open_question(self):
        rc, rules = self.rules(VALID.replace(
            "### Q2:", "#### Answer\nStale.\n\n### Q2:"))
        self.assertIn("question-subsection", rules)


class StrayLineTests(Case):
    def test_prose_before_first_question(self):
        rc, rules = self.rules(VALID.replace("## Questions\n", "## Questions\nstray prose here\n"))
        self.assertIn("question-field", rules)

    def test_lines_under_malformed_heading(self):
        rc, rules = self.rules(VALID.replace("### Q2: Do", "### Question two: Do"))
        self.assertGreaterEqual(rules.count("question-field"), 1)


class DotfileTests(Case):
    def test_appledouble_files_are_not_topics(self):
        (self.root / "c.md").write_text(topic_file("C"))
        (self.root / "._c.md").write_text(topic_file("ghost"))
        rc, out = run("list", "--dir", str(self.root))
        self.assertEqual([t["slug"] for t in out["topics"]], ["c"])


class DateTests(Case):
    def test_impossible_dates_are_reported(self):
        for old, new, rule in (
                ("updated: 2026-10-20", "updated: 2026-13-45", "frontmatter-date"),
                ("- last recalled:\n\n#### Answer", "- last recalled: 2026-99-01\n\n#### Answer",
                 "last-recalled-date"),
                ("- 2026-10-20 — Parked", "- 2026-13-45 — Parked", "session-log-entry")):
            with self.subTest(rule=rule):
                rc, rules = self.rules(VALID.replace(old, new))
                self.assertIn(rule, rules)


class FrontmatterKeyTests(Case):
    def test_unknown_key(self):
        rc, rules = self.rules(VALID.replace("workspace:", "workspce: ~/Learning/rust"))
        self.assertIn("frontmatter-field", rules)

    def test_repeated_key(self):
        rc, rules = self.rules(VALID.replace("status: open\n", "status: open\nstatus: closed\n", 1))
        self.assertIn("frontmatter-field", rules)


class BomTests(Case):
    def test_bom_file_is_valid(self):
        rc, report = self.check(VALID, encoding="utf-8-sig")
        self.assertEqual(rc, 0, report)


if __name__ == "__main__":
    unittest.main()
