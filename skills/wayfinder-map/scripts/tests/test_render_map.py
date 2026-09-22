"""Tests for render_map.py. Fixtures are built in a temp directory per test.

    python3 -m unittest discover -s skills/wayfinder-map/scripts/tests
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import re
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import render_map as rm  # noqa: E402

MAP = """# Map: Six ticket effort

Label: wayfinder:map
Charted: 2026-09-18

## Destination

Three specs, plan-ready.
Second line of the first paragraph.

_A caveat that is not rendered._

## Notes

- **Rendered map**: https://example.invalid/should-not-appear

## Decisions so far

<!-- one line per resolved ticket: [title](issues/NN-slug.md): gist -->

- [Pick the key](issues/01-pick-the-key.md): name slug,
  never the member id.
- A bare decision with no link.

## Not yet specified

- **Records page.** The list waits on 04.
- **Lineups.** Depends on Layout choice somehow.
- **Unattached patch.** Nothing links here.

## Out of scope

- Never drawn out-of-scope item.
"""

TICKETS = {
    "01-pick-the-key.md": ("# 01: Pick the key", "grilling", "resolved", "None"),
    "02-layout-choice.md": ("# 02 · Layout choice", "prototype", None, None),
    "03-research-api.md": ("# 03 - Research the API", "research", "claimed", ""),
    "04-data-shape.md": ("# 04: Data shape", "grilling", "open", "01, 03"),
    "05-write-spec-a.md": ("# 05: Write spec A", "task", "open", "01 02"),
    "06-write-spec-b.md": ("# 06: Write spec B", "task", "open", "04, 05"),
}


def ticket_text(h1: str, ttype: str | None, status: str | None, blocked: str | None) -> str:
    lines = [h1, ""]
    if ttype is not None:
        lines.append(f"Type: {ttype}")
    if status is not None:
        lines.append(f"Status: {status}")
    if blocked is not None:
        lines.append(f"Blocked by: {blocked}")
    lines += ["", "## Question", "", "Status: resolved  <- below the first ## and ignored"]
    return "\n".join(lines) + "\n"


class Fixture(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / ".git").mkdir()
        self.effort = self.root / ".scratch" / "07-six"
        (self.effort / "issues").mkdir(parents=True)
        (self.effort / "map.md").write_text(MAP, encoding="utf-8")
        for name, spec in TICKETS.items():
            self.write_ticket(name, *spec)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def write_ticket(self, name, h1, ttype, status, blocked) -> None:
        (self.effort / "issues" / name).write_text(ticket_text(h1, ttype, status, blocked), encoding="utf-8")

    def load(self):
        with contextlib.redirect_stderr(io.StringIO()) as err:
            m, tickets = rm.load_effort(self.effort)
            d = rm.derive(m, tickets)
        return m, d, err.getvalue()

    def render(self) -> str:
        with contextlib.redirect_stderr(io.StringIO()):
            return rm.render_html(self.effort)


class ParsingTests(Fixture):
    def test_title_prefixes_stripped(self):
        _, d, _ = self.load()
        self.assertEqual(d["by"][1]["title"], "Pick the key")
        self.assertEqual(d["by"][2]["title"], "Layout choice")
        self.assertEqual(d["by"][3]["title"], "Research the API")

    def test_missing_status_is_open(self):
        _, d, _ = self.load()
        self.assertEqual(d["by"][2]["status"], "open")

    def test_status_below_first_heading_ignored(self):
        _, d, _ = self.load()
        self.assertEqual(d["by"][4]["status"], "open")

    def test_blocked_by_none_absent_empty_and_lists(self):
        _, d, _ = self.load()
        self.assertEqual(d["by"][1]["blocked_by"], [])
        self.assertEqual(d["by"][2]["blocked_by"], [])
        self.assertEqual(d["by"][3]["blocked_by"], [])
        self.assertEqual(d["by"][4]["blocked_by"], [1, 3])
        self.assertEqual(d["by"][5]["blocked_by"], [1, 2])

    def test_unknown_blocker_dropped_with_warning(self):
        self.write_ticket("04-data-shape.md", "# 04: Data shape", "grilling", "open", "01, 03, 99")
        _, d, err = self.load()
        self.assertEqual(d["by"][4]["blocked_by"], [1, 3])
        self.assertIn("99", err)

    def test_missing_type_warns_and_draws_grilling(self):
        self.write_ticket("02-layout-choice.md", "# 02 · Layout choice", None, None, None)
        _, d, err = self.load()
        self.assertEqual(d["by"][2]["type"], "grilling")
        self.assertIn("02-layout-choice.md", err)

    def test_map_fields_and_html_comments(self):
        m, _, _ = self.load()
        self.assertEqual(m["title"], "Six ticket effort")
        self.assertEqual(m["charted"], "2026-09-18")
        self.assertEqual(m["destination"], "Three specs, plan-ready. Second line of the first paragraph.")
        self.assertEqual(len(m["decisions"]), 2)
        self.assertEqual(m["decisions"][0]["title"], "Pick the key")
        self.assertEqual(m["decisions"][0]["gist"], "name slug, never the member id.")
        self.assertIsNone(m["decisions"][1]["title"])
        self.assertEqual([f["lead"] for f in m["fog"]], ["Records page", "Lineups", "Unattached patch"])


class DerivationTests(Fixture):
    def test_states(self):
        _, d, _ = self.load()
        states = {n: t["state"] for n, t in d["by"].items()}
        self.assertEqual(states, {1: "resolved", 2: "frontier", 3: "claimed", 4: "blocked",
                                  5: "blocked", 6: "blocked"})

    def test_claimed_blocker_keeps_dependents_blocked(self):
        _, d, _ = self.load()
        self.assertEqual(d["by"][4]["state"], "blocked")  # 03 is claimed, not resolved

    def test_claimed_wins_over_blocked(self):
        self.write_ticket("05-write-spec-a.md", "# 05: Write spec A", "task", "claimed", "01 02")
        _, d, _ = self.load()
        self.assertEqual(d["by"][5]["state"], "claimed")

    def test_sinks_land_in_last_column(self):
        self.write_ticket("07-side-task.md", "# 07: Side task", "task", "open", "None")
        _, d, _ = self.load()
        self.assertEqual(d["columns"][-1], [6, 7])
        self.assertEqual(d["sinks"], {6, 7})

    def test_sources_in_first_column_by_number(self):
        _, d, _ = self.load()
        self.assertEqual(d["columns"][0], [1, 2, 3])

    def test_cycle_exits_1_naming_it(self):
        self.write_ticket("01-pick-the-key.md", "# 01: Pick the key", "grilling", "open", "06")
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            code = rm.main([str(self.effort)])
        self.assertEqual(code, 1)
        self.assertIn("cycle", err.getvalue())
        self.assertRegex(err.getvalue(), r"01 → 04 → 06 → 01|06 → 01 → 04 → 06|04 → 06 → 01 → 04")

    def test_takeable_lists_what_it_unblocks(self):
        _, d, _ = self.load()
        self.assertEqual([(t["num"], t["unblocks"]) for t in d["takeable"]], [(2, ["Write spec A"])])


class FogTests(Fixture):
    def test_links_by_waits_on_by_title_and_unattached(self):
        _, d, _ = self.load()
        self.assertEqual(d["fog_links"], [[4], [2], []])

    def test_two_links_from_one_bullet(self):
        text = MAP.replace("The list waits on 04.", "The list waits on 04, 05.")
        (self.effort / "map.md").write_text(text, encoding="utf-8")
        _, d, _ = self.load()
        self.assertEqual(d["fog_links"][0], [4, 5])


class RenderTests(Fixture):
    def test_each_title_once_in_the_svg(self):
        html = self.render()
        svg = html[html.index("<svg"): html.index("</svg>")]
        _, d, _ = self.load()
        for n, t in d["by"].items():
            self.assertEqual(svg.count(f'data-ticket="{t["label"]}"'), 1)
            group = re.search(rf'data-ticket="{t["label"]}".*?</g>', svg, flags=re.S).group(0)
            spans = " ".join(re.findall(r"<tspan[^>]*>(.*?)</tspan>", group))
            self.assertEqual(spans, f"{t['label']} · {t['title']}")

    def test_strip_counts_match_derivation(self):
        html = self.render()
        _, d, _ = self.load()
        for key in ("resolved", "claimed", "frontier", "blocked", "fog"):
            m = re.search(rf'data-count="{key}">.*?<span class="n">(\d+)</span>', html)
            self.assertEqual(int(m.group(1)), d["counts"][key], key)

    def test_self_contained(self):
        html = self.render()
        self.assertNotIn("http", html)
        self.assertNotIn("<script", html)
        self.assertNotIn("<link", html)

    def test_title_and_out_of_scope(self):
        html = self.render()
        self.assertIn("<title>Six ticket effort</title>", html)
        self.assertNotIn("Never drawn", html)
        self.assertNotIn("caveat", html)

    def test_empty_sections_absent(self):
        text = re.sub(r"## Decisions so far.*?## Not yet specified\n\n.*?\n\n", "## Out of scope\n\n", MAP, flags=re.S)
        (self.effort / "map.md").write_text(text, encoding="utf-8")
        html = self.render()
        self.assertNotIn("Decisions so far", html)
        self.assertNotIn("Not yet specified", html)
        self.assertNotIn('class="two"', html)

    def test_empty_frontier(self):
        self.write_ticket("02-layout-choice.md", "# 02 · Layout choice", "prototype", "claimed", None)
        html = self.render()
        self.assertIn("Nothing is takeable", html)
        self.assertNotIn('class="cards"', html)

    def test_markup_in_files_is_escaped(self):
        self.write_ticket("02-layout-choice.md", "# 02 · Layout <b>choice</b>", "prototype", None, None)
        html = self.render()
        self.assertNotIn("<b>choice</b>", html)
        self.assertIn("&lt;b&gt;choice&lt;/b&gt;", html)

    def test_two_renders_byte_identical(self):
        self.assertEqual(self.render(), self.render())


def _age(path: Path, seconds_ago: float) -> None:
    t = time.time() - seconds_ago
    os.utime(path, (t, t))


class StaleTests(Fixture):
    def inputs(self):
        return [self.effort / "map.md", *(self.effort / "issues").glob("*.md")]

    def test_missing_renders(self):
        self.assertTrue(rm.is_stale(self.effort))

    def test_older_renders(self):
        (self.effort / "map.html").write_text("old")
        _age(self.effort / "map.html", 100)
        self.assertTrue(rm.is_stale(self.effort))

    def test_newer_skipped(self):
        for p in self.inputs():
            _age(p, 100)
        (self.effort / "map.html").write_text("new")
        self.assertFalse(rm.is_stale(self.effort))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(rm.main(["--all", "--stale-only", "--root", str(self.root)]), 0)
        self.assertEqual(out.getvalue(), "")
        self.assertEqual((self.effort / "map.html").read_text(), "new")


class HookTests(Fixture):
    def run_hook(self, stdin: str):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = rm.run_hook(stdin)
        return code, out.getvalue(), err.getvalue()

    def test_valid_stdin_renders(self):
        code, out, _ = self.run_hook(json.dumps({"cwd": str(self.root), "hook_event_name": "Stop"}))
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), str(self.effort / "map.html"))
        self.assertTrue((self.effort / "map.html").exists())

    def test_nothing_stale_prints_nothing(self):
        self.run_hook(json.dumps({"cwd": str(self.root)}))
        for p in [self.effort / "map.md", *(self.effort / "issues").glob("*.md")]:
            _age(p, 100)
        code, out, _ = self.run_hook(json.dumps({"cwd": str(self.root)}))
        self.assertEqual((code, out), (0, ""))

    def test_malformed_stdin_exits_0(self):
        code, out, err = self.run_hook("{not json")
        self.assertEqual((code, out), (0, ""))
        self.assertIn("--hook", err)

    def test_broken_map_still_exits_0(self):
        self.write_ticket("01-pick-the-key.md", "# 01: Pick the key", "grilling", "open", "06")
        code, _, err = self.run_hook(json.dumps({"cwd": str(self.root)}))
        self.assertEqual(code, 0)
        self.assertIn("cycle", err)


if __name__ == "__main__":
    unittest.main()
