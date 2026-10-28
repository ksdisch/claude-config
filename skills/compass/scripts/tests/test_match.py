"""`compass.py match <query>` over a throwaway compass folder.

Each test builds a fresh temp folder of minimal topic files, drives the script through its
command line with `--dir`, and asserts only on the JSON it prints and its exit code.

Run from `skills/compass/scripts`:  python3 -m unittest discover
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "compass.py"


def topic_file(topic, status="open"):
    close_out = "## Close-out\nDone.\n\n" if status == "closed" else ""
    return (f"---\ntopic: {topic}\nwhy: Because.\nstatus: {status}\nworkspace:\n"
            f"created: 2026-10-18\nupdated: 2026-10-20\n---\n\n# {topic}\n\n## Questions\n\n"
            f"{close_out}## Session log\n- 2026-10-18 — Started.\n")


class MatchCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def add(self, slug, topic, status="open"):
        (self.root / f"{slug}.md").write_text(topic_file(topic, status))

    def match(self, query, folder=None):
        proc = subprocess.run([sys.executable, str(SCRIPT), "match", query, "--dir",
                               str(folder or self.root)], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        out = json.loads(proc.stdout)
        return out["result"], [m["slug"] for m in out["matches"]]

    def populate(self):
        self.add("rust-lifetimes", "Rust lifetimes")
        self.add("rust-async", "Rust async")
        self.add("k8s-networking", "Kubernetes networking")

    def test_exact_slug_is_a_single_match(self):
        self.populate()
        self.assertEqual(self.match("rust-lifetimes"), ("single", ["rust-lifetimes"]))

    def test_exact_slug_wins_over_topics_that_contain_it(self):
        self.add("rust", "Rust")
        self.add("rust-lifetimes", "Rust lifetimes")
        self.assertEqual(self.match("rust"), ("single", ["rust"]))

    def test_partial_name_is_a_single_match(self):
        self.populate()
        self.assertEqual(self.match("lifetime"), ("single", ["rust-lifetimes"]))

    def test_words_match_in_any_order(self):
        self.populate()
        self.assertEqual(self.match("lifetimes rust"), ("single", ["rust-lifetimes"]))

    def test_match_ignores_case(self):
        self.populate()
        self.assertEqual(self.match("RUST Lifetimes"), ("single", ["rust-lifetimes"]))

    def test_display_name_hit_when_the_slug_differs(self):
        self.populate()
        self.assertEqual(self.match("kubernetes"), ("single", ["k8s-networking"]))

    def test_several_candidates_are_all_reported(self):
        self.populate()
        result, slugs = self.match("rust")
        self.assertEqual(result, "several")
        self.assertEqual(sorted(slugs), ["rust-async", "rust-lifetimes"])

    def test_matches_carry_display_name_and_status(self):
        self.add("rust-lifetimes", "Rust lifetimes", status="closed")
        proc = subprocess.run([sys.executable, str(SCRIPT), "match", "rust", "--dir",
                               str(self.root)], capture_output=True, text=True)
        [m] = json.loads(proc.stdout)["matches"]
        self.assertEqual(m, {"slug": "rust-lifetimes", "topic": "Rust lifetimes",
                             "status": "closed"})

    def test_no_match(self):
        self.populate()
        self.assertEqual(self.match("haskell"), ("none", []))

    def test_empty_folder_is_no_match(self):
        self.assertEqual(self.match("rust"), ("none", []))

    def test_missing_folder_is_no_match(self):
        self.assertEqual(self.match("rust", self.root / "not-yet-created"), ("none", []))

    def test_blank_query_is_a_usage_error(self):
        proc = subprocess.run([sys.executable, str(SCRIPT), "match", "  ", "--dir",
                               str(self.root)], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)

    def test_a_file_that_is_not_utf8_is_skipped_and_reported(self):
        self.add("rust-lifetimes", "Rust lifetimes")
        (self.root / "rust-cafe.md").write_bytes(
            topic_file("Rust cafe").encode().replace(b"cafe", b"caf\xe9"))  # Latin-1 bytes
        proc = subprocess.run([sys.executable, str(SCRIPT), "match", "rust", "--dir",
                               str(self.root)], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        out = json.loads(proc.stdout)
        self.assertEqual((out["result"], [m["slug"] for m in out["matches"]]),
                         ("single", ["rust-lifetimes"]))
        self.assertEqual([s["file"] for s in out["skipped"]], ["rust-cafe.md"])

    # Query words match whole words or word prefixes, never the middle of a word.

    def populate_words(self):
        self.populate()
        self.add("git-rebasing", "Git rebasing")

    def test_a_short_word_does_not_match_inside_other_words(self):
        self.populate_words()
        self.assertEqual(self.match("in"), ("none", []))

    def test_word_prefixes_match(self):
        self.populate_words()
        self.assertEqual(self.match("kube net"), ("single", ["k8s-networking"]))

    def test_the_middle_of_a_word_does_not_match(self):
        self.populate_words()
        self.assertEqual(self.match("time"), ("none", []))


if __name__ == "__main__":
    unittest.main()
