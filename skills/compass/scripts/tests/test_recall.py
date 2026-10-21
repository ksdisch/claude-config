"""`compass.py recall <file> [n]` over a throwaway topic file.

Each test writes one small topic file to a temp folder, drives the script through its command
line, and asserts only on the JSON it prints and its exit code.

Run from `skills/compass/scripts`:  python3 -m unittest discover
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.test_list import topic_file

SCRIPT = Path(__file__).resolve().parent.parent / "compass.py"


def question(number, status="answered", recalled=""):
    body = f"### Q{number}: Question {number}?\n- status: {status}\n- last recalled: {recalled}\n"
    if status == "answered":
        body += "- answered by: claude\n\n#### Answer\nYes.\n\n#### Sources\n- https://example.com\n"
    if status == "parked":
        body += "- park reason: Off the why.\n"
    return body + "\n"


class RecallCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.file = Path(self._tmp.name) / "rust-lifetimes.md"

    def tearDown(self):
        self._tmp.cleanup()

    def run_recall(self, *questions, n=None):
        self.file.write_text(topic_file(questions="".join(questions)))
        args = [sys.executable, str(SCRIPT), "recall", str(self.file)]
        if n is not None:
            args.append(str(n))
        proc = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        return json.loads(proc.stdout)["questions"]

    def numbers(self, *questions, n=None):
        return [q["number"] for q in self.run_recall(*questions, n=n)]

    def test_never_recalled_come_before_recalled(self):
        picked = self.numbers(question("1", recalled="2026-10-01"), question("2"),
                              question("3", recalled="2026-09-15"), question("4"))
        self.assertEqual(picked, ["2", "4", "3"])

    def test_never_recalled_ties_break_by_tree_number(self):
        # Q10 is logged first and Q1.2 sits below Q2 in the file; tree order still wins.
        picked = self.numbers(question("10"), question("1"), question("2"), question("1.2"),
                              n=4)
        self.assertEqual(picked, ["1", "1.2", "2", "10"])

    def test_recalled_questions_come_oldest_date_first(self):
        picked = self.numbers(question("1", recalled="2026-10-19"),
                              question("2", recalled="2026-08-30"),
                              question("3", recalled="2026-10-02"))
        self.assertEqual(picked, ["2", "3", "1"])

    def test_same_recall_date_ties_break_by_tree_number(self):
        picked = self.numbers(question("3", recalled="2026-10-02"),
                              question("1.1", recalled="2026-10-02"),
                              question("2", recalled="2026-10-02"))
        self.assertEqual(picked, ["1.1", "2", "3"])

    def test_default_cap_is_three(self):
        picked = self.numbers(*(question(str(i)) for i in range(1, 6)))
        self.assertEqual(picked, ["1", "2", "3"])

    def test_n_caps_the_result(self):
        picked = self.numbers(*(question(str(i)) for i in range(1, 6)), n=2)
        self.assertEqual(picked, ["1", "2"])

    def test_n_above_the_answered_count_returns_them_all(self):
        self.assertEqual(self.numbers(question("1"), question("2"), n=3), ["1", "2"])

    def test_only_answered_questions_are_eligible(self):
        picked = self.numbers(question("1", status="open"), question("2", status="parked"),
                              question("3", status="prereq"), question("4"), n=5)
        self.assertEqual(picked, ["4"])

    def test_nothing_answered_gives_an_empty_result(self):
        self.assertEqual(self.run_recall(question("1", status="open"),
                                         question("2", status="parked")), [])

    def test_topic_with_no_questions_gives_an_empty_result(self):
        self.assertEqual(self.run_recall(), [])

    def test_each_pick_carries_its_text_and_last_recalled_date(self):
        [pick] = self.run_recall(question("1.2", recalled="2026-10-02"))
        self.assertEqual(pick, {"number": "1.2", "text": "Question 1.2?",
                                "last_recalled": "2026-10-02"})

    def test_n_must_be_a_positive_integer(self):
        self.file.write_text(topic_file(questions=question("1")))
        for bad in ("0", "-1", "two"):
            proc = subprocess.run([sys.executable, str(SCRIPT), "recall", str(self.file), bad],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2, f"n={bad!r}: {proc.stdout}{proc.stderr}")

    def test_unreadable_file_exits_2_with_an_error(self):
        proc = subprocess.run([sys.executable, str(SCRIPT), "recall",
                               str(self.file.with_name("missing.md"))],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("error", json.loads(proc.stdout))

    def test_a_file_that_is_not_utf8_exits_2_with_an_error(self):
        self.file.write_bytes(topic_file(questions=question("1")).encode()
                              .replace(b"Rust", b"Caf\xe9"))  # Latin-1 bytes
        proc = subprocess.run([sys.executable, str(SCRIPT), "recall", str(self.file)],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertIn("UTF-8", json.loads(proc.stdout)["error"])


if __name__ == "__main__":
    unittest.main()
