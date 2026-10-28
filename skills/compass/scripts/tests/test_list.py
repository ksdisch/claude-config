"""`compass.py list` over a throwaway compass folder.

Each test builds a fresh temp folder of small topic files, drives the script through its command
line with `--dir`, and asserts only on the JSON it prints and its exit code.

Run from `skills/compass/scripts`:  python3 -m unittest discover
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "compass.py"


def topic_file(topic="Rust lifetimes", why="Read borrow-checker errors.", status="open",
               updated="2026-10-20", questions=""):
    close_out = "## Close-out\nI can read them now.\n\n" if status == "closed" else ""
    return (f"---\ntopic: {topic}\nwhy: {why}\nstatus: {status}\nworkspace:\n"
            f"created: 2026-10-18\nupdated: {updated}\n---\n\n# {topic}\n\n"
            f"## Questions\n\n{questions}\n{close_out}## Session log\n- 2026-10-18 — Started.\n")


def question(number, status, extra=""):
    body = f"### Q{number}: Question {number}?\n- status: {status}\n- last recalled:\n"
    if status == "answered":
        body += "- answered by: claude\n\n#### Answer\nYes.\n\n#### Sources\n- https://example.com\n"
    if status == "parked":
        body += "- park reason: Off the why.\n"
    return body + extra + "\n"


class ListCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, slug, text):
        (self.root / f"{slug}.md").write_text(text)

    def run_list(self, folder=None):
        proc = subprocess.run([sys.executable, str(SCRIPT), "list", "--dir",
                               str(folder or self.root)], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        return json.loads(proc.stdout)["topics"]

    def test_counts_questions_per_status(self):
        qs = "".join([question("1", "answered"), question("1.1", "open"), question("2", "open"),
                      question("3", "parked"), question("4", "prereq")])
        self.write("rust-lifetimes", topic_file(questions=qs))
        [row] = self.run_list()
        self.assertEqual(row["counts"], {"open": 2, "answered": 1, "parked": 1, "prereq": 1})

    def test_topic_with_no_questions_has_zero_counts(self):
        self.write("rust-lifetimes", topic_file())
        [row] = self.run_list()
        self.assertEqual(row["counts"], {"open": 0, "answered": 0, "parked": 0, "prereq": 0})

    def test_reports_slug_display_name_status_and_last_touched(self):
        self.write("rust-lifetimes", topic_file(topic="Rust lifetimes", updated="2026-10-19"))
        [row] = self.run_list()
        self.assertEqual(row["slug"], "rust-lifetimes")
        self.assertEqual(row["topic"], "Rust lifetimes")
        self.assertEqual(row["status"], "open")
        self.assertEqual(row["last_touched"], "2026-10-19")

    def test_short_why_is_kept_whole(self):
        self.write("a", topic_file(why="Read borrow-checker errors."))
        [row] = self.run_list()
        self.assertEqual(row["why"], "Read borrow-checker errors.")

    def test_long_why_is_cut_at_a_word_with_an_ellipsis(self):
        why = ("I review Rust PRs at work and need to read borrow-checker errors without "
               "guessing at what the compiler wants.")
        self.write("a", topic_file(why=why))
        [row] = self.run_list()
        self.assertEqual(row["why"], "I review Rust PRs at work and need to read borrow-checker…")

    def test_open_topics_come_before_closed_ones_newest_first(self):
        self.write("old-open", topic_file(topic="Old open", updated="2026-10-01"))
        self.write("new-closed", topic_file(topic="New closed", status="closed",
                                            updated="2026-10-20"))
        self.write("new-open", topic_file(topic="New open", updated="2026-10-15"))
        rows = self.run_list()
        self.assertEqual([r["slug"] for r in rows], ["new-open", "old-open", "new-closed"])
        self.assertEqual([r["status"] for r in rows], ["open", "open", "closed"])

    def test_empty_folder_lists_nothing(self):
        self.assertEqual(self.run_list(), [])

    def test_missing_folder_lists_nothing(self):
        self.assertEqual(self.run_list(self.root / "not-yet-created"), [])

    def test_only_markdown_files_count_as_topics(self):
        self.write("rust-lifetimes", topic_file())
        (self.root / "notes.txt").write_text("not a topic")
        self.assertEqual([r["slug"] for r in self.run_list()], ["rust-lifetimes"])

    def test_a_file_that_is_not_utf8_is_skipped_and_reported(self):
        self.write("rust-lifetimes", topic_file())
        (self.root / "latin1.md").write_bytes(
            topic_file(topic="Cafe").encode().replace(b"Cafe", b"Caf\xe9"))  # Latin-1 bytes
        proc = subprocess.run([sys.executable, str(SCRIPT), "list", "--dir", str(self.root)],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        out = json.loads(proc.stdout)
        self.assertEqual([r["slug"] for r in out["topics"]], ["rust-lifetimes"])
        [skipped] = out["skipped"]
        self.assertEqual(skipped["file"], "latin1.md")
        self.assertIn("UTF-8", skipped["error"])

    def test_nothing_skipped_when_every_file_reads(self):
        self.write("rust-lifetimes", topic_file())
        proc = subprocess.run([sys.executable, str(SCRIPT), "list", "--dir", str(self.root)],
                              capture_output=True, text=True)
        self.assertEqual(json.loads(proc.stdout)["skipped"], [])


if __name__ == "__main__":
    unittest.main()
