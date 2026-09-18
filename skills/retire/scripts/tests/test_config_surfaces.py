"""Fixture-driven tests for the config-repo surfaces beyond skills.

CLAUDE.md sections, the operating-constraints paragraphs, commands (paused ones included),
agents, output styles, gitignored skill copies, and the trigger sidecar that scores the
CLAUDE.md lane. Same contract as `test_steering_inventory.py`: build a throwaway tree, drive
the script through its command line, assert only on what comes out.

Run from `skills/retire/scripts`:  python3 -m unittest discover -s tests -t .
"""
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import steering_inventory as si  # noqa: E402

from tests.test_steering_inventory import (  # noqa: E402
    BASE_COMMIT_DAYS_AGO, FixtureCase, add_history, commit_all, day, write,
)


class ClaudeMdSectionTests(FixtureCase):
    def test_one_record_per_heading_outside_fenced_code(self):
        rc, payload, _ = self.run_json("--surface", "claude-md")
        self.assertEqual(rc, si.EXIT_OK)
        ids = [i["id"] for i in payload["items"]]
        # The constraints paragraph leads (CLAUDE.md imports that file at the top), then every
        # ##/### heading in document order. `# Top` is level 1 and the fenced `# Not a heading`
        # is inside a code block: neither is a rule, so neither is an item.
        self.assertEqual(ids, ["claude-md:Scope discipline", "claude-md:Improvement Mode",
                               "claude-md:Git Workflow", "claude-md:Sub rule"])
        self.assertTrue(all(i["surface"] == "claude-md" for i in payload["items"]))

    def test_section_bytes_are_the_section_length(self):
        rc, payload, _ = self.run_json("--surface", "claude-md")
        self.assertEqual(rc, si.EXIT_OK)
        imp = self.items_by_id(payload)["claude-md:Improvement Mode"]
        cm = (self.cfg.config_repo / "CLAUDE.md").read_text()
        body = cm[cm.index("## Improvement Mode"):cm.index("## Git Workflow")]
        self.assertEqual(imp["bytes_always_loaded"], len(body))
        self.assertEqual(imp["extra"]["line"], 5)
        self.assertEqual(imp["extra"]["file"], "CLAUDE.md")
        self.assertNotIn("body", imp["extra"])          # the full text never reaches the JSON

    def test_surface_total_is_the_files_not_the_sum_of_nested_sections(self):
        rc, payload, _ = self.run_json("--surface", "claude-md")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        # `### Sub rule` is its own record AND lives inside `## Git Workflow`'s body, so summing
        # the records would charge its bytes twice and still miss the preamble.
        self.assertGreater(by["claude-md:Sub rule"]["bytes_always_loaded"], 0)
        self.assertIn("### Sub rule", (self.cfg.config_repo / "CLAUDE.md").read_text())
        files = sum(len((self.cfg.config_repo / f).read_text())
                    for f in ("CLAUDE.md", "operating-constraints.md"))
        self.assertEqual(payload["totals"]["claude-md"]["always_loaded_chars"], files)
        self.assertLess(files, sum(i["bytes_always_loaded"] for i in payload["items"]))

    def test_missing_claude_md_exits_two_naming_the_source(self):
        (self.cfg.config_repo / "CLAUDE.md").unlink()
        rc, _, err = self.run_cli("--surface", "claude-md")
        self.assertEqual(rc, si.EXIT_SOURCE_MISSING)
        self.assertIn("CLAUDE.md missing", err)


class ConstraintsParagraphTests(FixtureCase):
    def test_bold_led_paragraphs_are_the_unit_and_prose_is_not(self):
        write(self.cfg.config_repo / "operating-constraints.md",
              "# CONSTRAINTS\n\n"
              "These govern every session; a skill's own gate still wins.\n\n"
              "**Scope discipline.** Do exactly what's asked.\n\n"
              "**Act vs. assess.** Report findings and stop.\n\n"
              "**Unattended runs only** — never in an interactive session.\n")
        commit_all(self.cfg.config_repo, "rewrite constraints")
        rc, payload, _ = self.run_json("--surface", "claude-md")
        self.assertEqual(rc, si.EXIT_OK)
        names = [i["name"] for i in payload["items"] if i["extra"]["file"].startswith("operating")]
        # The heading and the un-bolded preamble describe the rules; they are not rules.
        self.assertEqual(names, ["Scope discipline", "Act vs. assess", "Unattended runs only"])
        by = self.items_by_id(payload)
        scope = by["claude-md:Scope discipline"]
        self.assertEqual(scope["bytes_always_loaded"],
                         len("**Scope discipline.** Do exactly what's asked.\n"))
        self.assertEqual(scope["extra"]["line"], 5)
        self.assertTrue(scope["tracked"])


class CommandAgentAndStyleTests(FixtureCase):
    def test_commands_include_paused_ones_at_zero_bytes(self):
        rc, payload, _ = self.run_json("--surface", "command")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        self.assertEqual(sorted(by), ["command:gamma", "command:old"])
        self.assertFalse(by["command:gamma"]["paused"])
        self.assertEqual(by["command:gamma"]["bytes_always_loaded"], len("Gamma command."))
        # `old.md.disabled` is a ruling Kyle already made: still on the surface, costing nothing.
        self.assertTrue(by["command:old"]["paused"])
        self.assertIn("paused", by["command:old"]["flags"])
        self.assertEqual(by["command:old"]["bytes_always_loaded"], 0)
        self.assertEqual(by["command:old"]["description"], "Old command.")

    def test_agents_are_enumerated(self):
        rc, payload, _ = self.run_json("--surface", "agent")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        self.assertEqual(sorted(by), ["agent:judge"])
        self.assertEqual(by["agent:judge"]["bytes_always_loaded"], len("Judge agent."))
        self.assertTrue(by["agent:judge"]["tracked"])

    def test_output_style_is_unlinked_when_the_home_has_no_output_styles_dir(self):
        rc, payload, _ = self.run_json("--surface", "output-style")
        self.assertEqual(rc, si.EXIT_OK)
        plain = self.items_by_id(payload)["output-style:plain"]
        self.assertIn("unlinked", plain["flags"])

    def test_output_style_is_not_unlinked_once_the_home_carries_it(self):
        write(self.cfg.claude_home / "output-styles/plain.md", "---\nname: plain\n---\n")
        rc, payload, _ = self.run_json("--surface", "output-style")
        self.assertEqual(rc, si.EXIT_OK)
        self.assertEqual(self.items_by_id(payload)["output-style:plain"]["flags"], [])

    def test_a_style_the_home_does_not_carry_stays_unlinked(self):
        write(self.cfg.claude_home / "output-styles/somethingelse.md", "---\n---\n")
        write(self.cfg.config_repo / "output-styles/second.md",
              "---\nname: second\ndescription: Second style.\n---\n")
        commit_all(self.cfg.config_repo, "add second style")
        rc, payload, _ = self.run_json("--surface", "output-style")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        self.assertIn("unlinked", by["output-style:plain"]["flags"])
        self.assertIn("unlinked", by["output-style:second"]["flags"])


class UntrackedSkillTests(FixtureCase):
    def test_gitignored_skill_is_listed_once_with_tracked_false(self):
        write(self.cfg.config_repo / "skills/ghost/SKILL.md",
              "---\nname: ghost\ndescription: Ghost skill.\n---\n")      # never committed
        rc, payload, _ = self.run_json("--surface", "skill")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        self.assertEqual(sorted(by),
                         ["skill:alpha", "skill:beta", "skill:ghost", "skill:tdd"])
        ghost = by["skill:ghost"]
        self.assertFalse(ghost["tracked"])
        # It is ignored by git but not by the harness: it still costs its description's bytes.
        self.assertEqual(ghost["bytes_always_loaded"], len("Ghost skill."))
        self.assertTrue(all(by[k]["tracked"] for k in by if k != "skill:ghost"))

    def test_untracked_skill_is_dated_by_directory_mtime(self):
        write(self.cfg.config_repo / "skills/ghost/SKILL.md", "---\nname: ghost\n---\n")
        rc, payload, _ = self.run_json("--surface", "skill")
        self.assertEqual(rc, si.EXIT_OK)
        ghost = self.items_by_id(payload)["skill:ghost"]
        self.assertEqual(ghost["added"], day(0))
        self.assertEqual(ghost["temperature"], "new")   # git cannot date it; mtime can


class AddedDateTests(FixtureCase):
    def test_tracked_files_are_dated_by_their_first_commit(self):
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        for item_id in ("command:gamma", "command:old", "agent:judge", "output-style:plain"):
            self.assertEqual(by[item_id]["added"], day(BASE_COMMIT_DAYS_AGO), item_id)

    def test_a_section_is_dated_by_the_commit_that_introduced_its_heading(self):
        cm = self.cfg.config_repo / "CLAUDE.md"
        cm.write_text(cm.read_text() + "\n## Late Rule\n\nAdded well after the file was.\n")
        commit_all(self.cfg.config_repo, "add Late Rule", days_ago=10)
        rc, payload, _ = self.run_json("--surface", "claude-md")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        # The file is 200 days old; this rule is 10 days old and must not be judged on the file's
        # age — a rule written last week has had no chance to be triggered.
        self.assertEqual(by["claude-md:Improvement Mode"]["added"], day(BASE_COMMIT_DAYS_AGO))
        self.assertEqual(by["claude-md:Late Rule"]["added"], day(10))
        self.assertEqual(by["claude-md:Late Rule"]["temperature"], "new")


class TriggerSidecarTests(FixtureCase):
    def sidecar(self, mapping):
        (self.root / "triggers.json").write_text(json.dumps(mapping))

    def test_a_matched_section_counts_history_hits_for_the_window_and_all_time(self):
        add_history(self.cfg.claude_home,
                    [("improvement mode: the layout is off", 5),
                     ("Improvement Mode again please", 20),
                     ("improvement mode, long ago", 200)])
        rc, payload, _ = self.run_json("--surface", "claude-md")
        self.assertEqual(rc, si.EXIT_OK)
        imp = self.items_by_id(payload)["claude-md:Improvement Mode"]
        self.assertEqual((imp["trigger_90d"], imp["trigger_all"]), (2, 3))
        self.assertEqual(imp["last_used"], day(5))
        self.assertEqual(imp["temperature"], "warm")

    def test_a_matched_section_with_no_hits_reports_a_real_zero(self):
        rc, payload, _ = self.run_json("--surface", "claude-md")
        self.assertEqual(rc, si.EXIT_OK)
        imp = self.items_by_id(payload)["claude-md:Improvement Mode"]
        # The sidecar named a phrase and the history was read: 0 here is evidence, not absence.
        self.assertEqual((imp["trigger_90d"], imp["trigger_all"]), (0, 0))
        self.assertEqual(imp["temperature"], "cold")

    def test_null_and_absent_sidecar_entries_stay_unmeasured(self):
        rc, payload, _ = self.run_json("--surface", "claude-md")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        # "Git Workflow" is null in the sidecar; "Sub rule" is not in it at all. Neither has a
        # fair proxy phrase, so neither may be reported as never-triggered.
        for item_id in ("claude-md:Git Workflow", "claude-md:Sub rule"):
            self.assertIsNone(by[item_id]["trigger_90d"], item_id)
            self.assertIsNone(by[item_id]["trigger_all"], item_id)

    def test_the_unmeasured_dash_reaches_the_markdown(self):
        out_md = self.root / "inv.md"
        rc, _, _ = self.run_cli("--surface", "claude-md", "--md", str(out_md))
        self.assertEqual(rc, si.EXIT_OK)
        md = out_md.read_text()
        self.assertIn("| `Git Workflow` |", md)
        self.assertIn("trig —/—", md)           # null entry: unmeasured
        self.assertIn("trig 0/0", md)           # matched entry, no hits: a measured zero
        self.assertNotIn(str(self.root), md)

    def test_a_heading_carrying_backticks_survives_the_table_cell(self):
        cm = self.cfg.config_repo / "CLAUDE.md"
        cm.write_text(cm.read_text() + "\n## Kickoff Mode → run the `/kickoff` skill\n\nGo.\n")
        commit_all(self.cfg.config_repo, "add kickoff heading")
        out_md = self.root / "inv.md"
        rc, _, _ = self.run_cli("--surface", "claude-md", "--md", str(out_md))
        self.assertEqual(rc, si.EXIT_OK)
        row = next(ln for ln in out_md.read_text().splitlines() if "Kickoff Mode" in ln)
        # The name is the key Kyle rules by and the key the sidecar is keyed on: it has to come
        # back verbatim, and the row has to stay a five-column row.
        self.assertIn("Kickoff Mode → run the `/kickoff` skill", row)
        self.assertEqual(row.count("|"), 6)


class DescriptionPhraseTests(FixtureCase):
    def test_quoted_phrases_in_a_skill_description_count_as_triggers(self):
        rc, payload, _ = self.run_json("--surface", "skill")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        # alpha's description quotes "alpha please" and "run alpha now"; the history holds
        # "alpha please, now" once, inside the window.
        self.assertEqual((by["skill:alpha"]["trigger_90d"], by["skill:alpha"]["trigger_all"]),
                         (1, 1))
        # beta and tdd quote nothing, so there is no phrase list to measure them against.
        self.assertIsNone(by["skill:beta"]["trigger_all"])
        self.assertIsNone(by["skill:tdd"]["trigger_all"])

    def test_quoted_phrases_in_a_command_description_count_as_triggers(self):
        write(self.cfg.config_repo / "commands/delta.md",
              '---\ndescription: Delta. Use when Kyle says "delta the thing".\n---\n')
        commit_all(self.cfg.config_repo, "add delta")
        add_history(self.cfg.claude_home, [("please delta the thing now", 4)])
        rc, payload, _ = self.run_json("--surface", "command")
        self.assertEqual(rc, si.EXIT_OK)
        delta = self.items_by_id(payload)["command:delta"]
        self.assertEqual((delta["trigger_90d"], delta["trigger_all"]), (1, 1))

    def test_quoted_runs_outside_the_length_bounds_are_not_phrases(self):
        short, long = "x" * (si.TRIGGER_PHRASE_MIN_CHARS - 1), "y" * (
            si.TRIGGER_PHRASE_MAX_CHARS + 1)
        write(self.cfg.config_repo / "commands/edge.md",
              f'---\ndescription: Edge. Say "{short}" or "{long}".\n---\n')
        commit_all(self.cfg.config_repo, "add edge")
        add_history(self.cfg.claude_home, [(f"{short} and {long}", 2)])
        rc, payload, _ = self.run_json("--surface", "command")
        self.assertEqual(rc, si.EXIT_OK)
        # A run below the floor is a word that would match anything; one above the ceiling is a
        # sentence nobody retypes. Neither is a trigger, so `edge` has no phrase list at all.
        self.assertIsNone(self.items_by_id(payload)["command:edge"]["trigger_all"])

    def test_the_phrase_extractor_lowercases_and_escapes(self):
        self.assertEqual(si.phrases_from_description('Say "Red-Team This Diff" now.'),
                         [si.re.escape("red-team this diff")])
        self.assertEqual(si.phrases_from_description('Use "a.b (c+d)" please.'),
                         [si.re.escape("a.b (c+d)")])
        self.assertEqual(si.phrases_from_description("No quotes here at all."), [])


class NewSurfaceFilterTests(FixtureCase):
    def test_every_new_surface_name_is_accepted_and_filters(self):
        for surface in ("command", "agent", "output-style", "claude-md"):
            with self.subTest(surface=surface):
                rc, payload, _ = self.run_json("--surface", surface)
                self.assertEqual(rc, si.EXIT_OK)
                self.assertTrue(payload["items"])
                self.assertEqual({i["surface"] for i in payload["items"]}, {surface})
                self.assertEqual(sorted(payload["totals"]), ["ALL", surface])
                self.assertEqual(payload["meta"]["surfaces"], [surface])

    def test_the_default_run_covers_every_enumerated_surface(self):
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        self.assertEqual({i["surface"] for i in payload["items"]}, set(si.ENUMERATED_SURFACES))
        # Totals name only surfaces that were read: an unbuilt lane is absent, never a zero row.
        self.assertEqual(sorted(payload["totals"]),
                         sorted(si.ENUMERATED_SURFACES + ["ALL"]))


class ShippedSidecarTests(unittest.TestCase):
    """The sidecar that ships beside the script, against the CLAUDE.md that ships beside it."""

    def setUp(self):
        self.scripts = Path(si.__file__).resolve().parent
        self.sidecar = json.loads(
            (self.scripts / "claude_md_triggers.json").read_text())
        self.claude_md = self.scripts.parents[2] / "CLAUDE.md"

    def test_an_entry_ships_for_every_current_claude_md_heading(self):
        headings = [t for t, _, _ in si.split_sections(self.claude_md.read_text())]
        keys = [k for k in self.sidecar if not k.startswith("_")]
        # A heading with no key renders as unmeasured — correct, but it means the lane silently
        # stops measuring the moment a heading is renamed. Keys and headings stay in lockstep.
        self.assertEqual(sorted(keys), sorted(headings))

    def test_the_two_modes_the_pilot_targets_carry_real_phrase_lists(self):
        for heading in ("Improvement Mode", "New Feature Mode"):
            self.assertTrue(self.sidecar[heading], heading)

    def test_every_phrase_compiles_as_a_regex(self):
        for heading, phrases in self.sidecar.items():
            if heading.startswith("_") or phrases is None:
                continue
            for p in phrases:
                with self.subTest(heading=heading, phrase=p):
                    si.re.compile(p)


if __name__ == "__main__":
    unittest.main()
