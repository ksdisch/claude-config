"""The visual map: `check` on the Overview's `Links:` list and the `map:` key, and `render`.

Each test writes small topic files into a fresh temp folder, drives the script through its
command line, and asserts on what comes out: the JSON, the exit code, and the HTML written
beside the topic file. Nothing here imports the script or reads the live ~/Learning folder.

Run from `skills/compass/scripts`:  python3 -m unittest discover
"""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "compass.py"

OVERVIEW = """\
## Overview
1. **Module** — any unit of code with an interface and an implementation.
2. **Interface** — everything a caller must know to use the module.
3. **Implementation** — the code that does the work behind the interface.
4. **Deep module** — a small interface hiding a lot of functionality.
5. **Shallow module** — an interface nearly as complicated as what it does.

How they connect: a module's value is what it does divided by what you must learn.

Links:
- Deep module → Interface: keeps it small
- Deep module → Implementation: hides a lot of it
- Shallow module → Interface: exposes nearly everything
- Interface → Implementation: is the cost of reaching

Sources:
- Gergely Orosz, "A Philosophy of Software Design: My Take" — https://blog.pragmaticengineer.com/a-philosophy-of-software-design-review/

"""

TOPIC = """\
---
topic: Deep modules
why: Matt Pocock talks about deep modules and I want to understand what he means.
status: open
workspace:
created: 2026-10-25
updated: 2026-10-25
---

# Deep modules

{overview}## Questions

### Q1: What makes an interface "small"?
- status: answered
- answered by: claude
- last recalled:

#### Answer
Few concepts to learn, not few methods.

#### Sources
- A Philosophy of Software Design, ch. 4 — https://web.stanford.edu/~ouster/cgi-bin/book.php

### Q1.1: Is a <script> tag in a question escaped?
- status: open
- last recalled:

### Q2: Does this matter for frontend components?
- status: parked
- park reason: My why is agents navigating code, not UI.
- last recalled:

### Q3: What is information hiding?
- status: prereq
- last recalled:

## Session log
- 2026-10-25 — Started; wrote overview.
"""


def topic(overview=OVERVIEW):
    return TOPIC.format(overview=overview)


class MapCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def run_script(self, *args):
        proc = subprocess.run([sys.executable, str(SCRIPT), *args],
                              capture_output=True, text=True)
        return proc.returncode, json.loads(proc.stdout) if proc.stdout.strip() else None

    def write(self, text: str, name: str = "deep-modules.md") -> Path:
        path = self.root / name
        path.write_text(text)
        return path

    def check(self, text: str):
        return self.run_script("check", str(self.write(text)))

    def rules(self, text: str) -> list:
        rc, report = self.check(text)
        self.assertEqual(rc, 1, report)
        return [v["rule"] for v in report["violations"]]

    def render(self, text: str):
        path = self.write(text)
        rc, out = self.run_script("render", str(path))
        html_path = path.with_suffix(".html")
        html = html_path.read_text() if html_path.exists() else None
        return rc, out, html


class LinksCheckTests(MapCase):
    def test_an_overview_with_links_passes(self):
        rc, report = self.check(topic())
        self.assertEqual(rc, 0, report)

    def test_an_overview_without_links_still_passes(self):
        no_links = re.sub(r"Links:\n(- .*\n)+\n", "", OVERVIEW)
        self.assertNotIn("Links:", no_links)
        rc, report = self.check(topic(overview=no_links))
        self.assertEqual(rc, 0, report)

    def test_a_link_end_that_is_not_a_bolded_term_is_reported(self):
        bad = OVERVIEW.replace("- Deep module → Interface", "- Deep module → Abstraction")
        rc, report = self.check(topic(overview=bad))
        self.assertEqual(rc, 1)
        link = [v for v in report["violations"] if v["rule"] == "overview-link"]
        self.assertEqual(len(link), 1, report)
        self.assertIn("Abstraction", link[0]["message"])
        self.assertIsInstance(link[0]["line"], int)

    def test_link_ends_match_terms_case_insensitively(self):
        rc, report = self.check(topic(overview=OVERVIEW.replace(
            "- Deep module → Interface", "- deep MODULE → interface")))
        self.assertEqual(rc, 0, report)

    def test_a_malformed_link_line_is_reported(self):
        for line in ("- Deep module -> Interface: keeps it small",
                     "- Deep module → Interface",
                     "Deep module → Interface: no bullet",
                     "- → Interface: no source"):
            with self.subTest(line=line):
                bad = OVERVIEW.replace("- Deep module → Interface: keeps it small", line)
                self.assertIn("overview-link", self.rules(topic(overview=bad)))

    def test_a_link_from_a_term_to_itself_is_reported(self):
        bad = OVERVIEW.replace("- Deep module → Interface", "- Interface → Interface")
        self.assertIn("overview-link", self.rules(topic(overview=bad)))


class MapKeyTests(MapCase):
    def test_the_map_key_is_optional_and_known(self):
        with_map = topic().replace(
            "workspace:\n", "workspace:\nmap: https://claude.ai/artifact/abc123\n")
        rc, report = self.check(with_map)
        self.assertEqual(rc, 0, report)
        rc, report = self.check(topic().replace("workspace:\n", "workspace:\nmap:\n"))
        self.assertEqual(rc, 0, report)


class RenderTests(MapCase):
    def test_render_writes_html_beside_the_topic_file_and_leaves_the_file_alone(self):
        text = topic()
        path = self.write(text)
        rc, out = self.run_script("render", str(path))
        self.assertEqual(rc, 0, out)
        self.assertEqual(out, {"written": str(path.with_suffix(".html"))})
        self.assertTrue(path.with_suffix(".html").is_file())
        self.assertEqual(path.read_text(), text)
        self.assertEqual(sorted(p.name for p in self.root.iterdir()),
                         ["deep-modules.html", "deep-modules.md"])

    def test_render_is_deterministic(self):
        _, _, first = self.render(topic())
        _, _, second = self.render(topic())
        self.assertEqual(first, second)

    def test_render_refuses_a_file_check_rejects_and_writes_nothing(self):
        rc, out, html = self.render(topic().replace("status: prereq", "status: maybe"))
        self.assertEqual(rc, 1)
        self.assertFalse(out["valid"])
        self.assertIn("question-status", [v["rule"] for v in out["violations"]])
        self.assertIsNone(html)

    def test_render_reports_an_unreadable_file(self):
        rc, out = self.run_script("render", str(self.root / "missing.md"))
        self.assertEqual(rc, 2)
        self.assertIn("error", out)

    def test_the_concept_map_draws_every_idea_and_every_link(self):
        _, _, html = self.render(topic())
        self.assertEqual(html.count('class="node"'), 5)
        self.assertEqual(html.count('class="edge"'), 4)
        for term in ("Module", "Interface", "Implementation", "Deep module", "Shallow module"):
            self.assertIn(term, html)
        for label in ("keeps it small", "hides a lot of it", "exposes nearly everything"):
            self.assertIn(label, html)
        self.assertIn("a module&#x27;s value is what it does", html)

    def test_an_overview_without_links_lists_ideas_but_draws_no_edges(self):
        no_links = re.sub(r"Links:\n(- .*\n)+\n", "", OVERVIEW)
        _, _, html = self.render(topic(overview=no_links))
        self.assertEqual(html.count('class="edge"'), 0)
        self.assertIn("Shallow module", html)

    def test_no_overview_means_no_concept_map(self):
        _, _, html = self.render(topic(overview=""))
        self.assertNotIn('class="node"', html)
        self.assertIn("Q1", html)

    def test_the_question_tree_shows_every_question_by_status(self):
        _, _, html = self.render(topic())
        statuses = re.findall(r'<li class="q" data-status="(\w+)"', html)
        self.assertEqual(statuses, ["answered", "open", "parked", "prereq"])
        self.assertIn("My why is agents navigating code, not UI.", html)
        # Q1.1 nests inside Q1's item, so the tree reads as a tree.
        q1 = html.index(">Q1<")
        q11 = html.index(">Q1.1<")
        q2 = html.index(">Q2<")
        self.assertLess(q1, q11)
        self.assertIn("<ul", html[q1:q11])
        self.assertLess(q11, q2)

    def test_counts_and_why_are_on_the_page(self):
        _, _, html = self.render(topic())
        self.assertIn("I want to understand what he means", html)
        for status in ("open", "answered", "parked", "prereq"):
            self.assertRegex(html, rf'data-count="{status}">1<')

    def test_an_empty_question_tree_says_so(self):
        text = re.sub(r"## Questions\n.*?## Session log", "## Questions\n\n## Session log",
                      topic(), flags=re.S)
        _, _, html = self.render(text)
        self.assertIn("No questions yet", html)

    def test_the_page_is_self_contained_and_escapes_file_text(self):
        _, _, html = self.render(topic())
        self.assertNotIn("<script", html)
        self.assertNotIn("<link", html)
        self.assertNotIn(" src=", html)
        self.assertIn("&lt;script&gt;", html)

    def test_only_http_sources_become_links(self):
        hostile = OVERVIEW.replace(
            "Sources:\n", "Sources:\n- Trap — javascript:alert(1)\n")
        _, _, html = self.render(topic(overview=hostile))
        self.assertNotIn('href="javascript', html)
        self.assertIn('href="https://blog.pragmaticengineer.com/', html)

    def test_list_and_match_ignore_the_rendered_page(self):
        self.render(topic())
        rc, out = self.run_script("list", "--dir", str(self.root))
        self.assertEqual(rc, 0)
        self.assertEqual([t["slug"] for t in out["topics"]], ["deep-modules"])
        self.assertEqual(out["skipped"], [])


if __name__ == "__main__":
    unittest.main()
