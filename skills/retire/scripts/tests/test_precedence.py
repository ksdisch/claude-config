"""The precedence table, the collapsed classes, `oversized`, the omitted summary, redaction.

Ticket 06. One test per row of the spec's precedence table, driven the same way as the sibling
suites: build a throwaway tree, drive the script's command line, assert only on what comes out —
the JSON records, the redacted markdown, the exit code.

Three inherited problems are ruled on here and have their own cases at the bottom: typed counts
on surfaces with no typed spelling, a `cold` resting on a source nobody read, and an evidence
cell that outgrew its table.

Run from `skills/retire/scripts`:  python3 -m unittest discover -s tests -t .
"""
import json
import unittest

from tests.test_claude_home_surfaces import HomeCase
from tests.test_steering_inventory import (add_history, add_skill, commit_all, day, git, si,
                                           tool_use, write)


class PrecedenceCase(HomeCase):
    """Helpers for putting one item into one row of the precedence table."""

    def keep_in_ledger(self, item_id: str, because: str = "load-bearing once a quarter") -> None:
        ledger = self.cfg.config_repo / "docs/retired.md"
        ledger.write_text(ledger.read_text() + f"| {day(30)} | {item_id} | {because} |\n")
        # Only the ledger: `git add -A` here would track whatever loose skill copy the test is
        # about, and a tracked copy is Kyle's own file rather than a duplicate of a plugin's.
        git(self.cfg.config_repo, "add", "docs/retired.md")
        git(self.cfg.config_repo, "commit", "-q", "-m", "record a keep ruling")

    def sized_skills(self, count: int, *, first_size: int = 200, step: int = 50) -> list[str]:
        """`count` committed skills with strictly increasing description lengths."""
        names = []
        for n in range(count):
            name = f"size{n:02d}"
            add_skill(self.cfg.config_repo, name, "x" * (first_size + n * step))
            names.append(name)
        return names

    def rows(self, *extra):
        rc, payload, _ = self.run_json(*extra)
        self.assertEqual(rc, si.EXIT_OK)
        return payload, self.items_by_id(payload)

    def markdown(self, *extra) -> str:
        out_md = self.root / "inv.md"
        rc, _, _ = self.run_cli("--md", str(out_md), *extra)
        self.assertEqual(rc, si.EXIT_OK)
        return out_md.read_text()

    def omitted_class(self, payload, key) -> dict:
        return next(e for e in payload["omitted"] if e["key"] == key)

    def collapsed_row(self, payload, key) -> dict:
        return next(c for c in payload["collapsed"] if c["key"] == key)

    def assert_row(self, item, *, proposed, precedence, shown):
        self.assertEqual((item["proposed"], item["precedence"], item["shown"]),
                         (proposed, precedence, shown), item["id"])


class PrecedenceRowTests(PrecedenceCase):
    """One test per row of the spec's table, in the table's own order."""

    def test_kept_is_omitted_counted_and_named(self):
        add_skill(self.cfg.config_repo, "coldskill", "Nobody uses this.")
        self.keep_in_ledger("skill:coldskill")
        payload, by = self.rows()
        # Without the ledger row this is `cold` and proposes `retire`; the recorded ruling wins,
        # and Kyle is never asked to re-litigate it.
        self.assertEqual(by["skill:coldskill"]["temperature"], "cold")
        self.assert_row(by["skill:coldskill"], proposed=None, precedence="kept", shown=False)
        kept = self.omitted_class(payload, "kept")
        self.assertEqual((kept["count"], kept["names"]), (1, ["coldskill"]))

    def test_a_duplicate_copy_proposes_retire_and_collapses_per_canonical_plugin(self):
        self.add_plugin_skill("grilling", "Plugin grilling skill.")
        self.add_untracked_skill("grilling")
        payload, by = self.rows("--surface", "skill")
        self.assert_row(by["skill:grilling"], proposed="retire", precedence="duplicate",
                        shown=False)
        self.assertEqual(by["skill:grilling"]["collapsed_into"], "duplicate:mp")
        self.assertEqual(by["skill:grilling"]["duplicate_of"], "mp:grilling")

    def test_a_comment_only_hook_and_an_empty_memory_dir_propose_retire_per_class(self):
        payload, by = self.rows()
        self.assert_row(by["hook:Stop[0][1]"], proposed="retire", precedence="mechanical",
                        shown=False)
        self.assert_row(by["memory:-p2"], proposed="retire", precedence="mechanical", shown=False)
        self.assertEqual(by["hook:Stop[0][1]"]["collapsed_into"], "hook:disabled_comment")
        self.assertEqual(by["memory:-p2"]["collapsed_into"], "memory:empty")

    def test_paused_under_a_window_is_omitted_counted_and_named(self):
        # A command paused today: the pause is honoured, and nothing is asked about it yet.
        write(self.cfg.config_repo / "commands/fresh.md.disabled", "---\ndescription: Paused.\n---\n")
        commit_all(self.cfg.config_repo, "pause fresh", days_ago=0)
        payload, by = self.rows("--surface", "command")
        self.assert_row(by["command:fresh"], proposed=None, precedence="paused-recent",
                        shown=False)
        recent = self.omitted_class(payload, "paused-recent")
        self.assertEqual((recent["count"], recent["names"]), (1, ["fresh"]))

    def test_paused_a_full_window_or_more_asks(self):
        # The fixture's `old` command was paused at the base commit, 200 days ago.
        _, by = self.rows("--surface", "command")
        self.assertIn("paused", by["command:old"]["flags"])
        self.assert_row(by["command:old"], proposed="ask", precedence="paused-long", shown=True)

    def test_an_unlinked_file_asks_on_the_same_row(self):
        # In the repo, never loaded by the harness: the same "is this still wanted?" question.
        _, by = self.rows("--surface", "output-style")
        self.assertIn("unlinked", by["output-style:plain"]["flags"])
        self.assert_row(by["output-style:plain"], proposed="ask", precedence="paused-long",
                        shown=True)

    def test_new_carrying_a_flag_asks(self):
        write(self.cfg.config_repo / "skills/rookie/SKILL.md",
              "---\nname: rookie\ndescription: Fresh, and it routes to /old.\n---\n\nSee /old.\n")
        commit_all(self.cfg.config_repo, "add rookie", days_ago=0)
        _, by = self.rows("--surface", "skill")
        rookie = by["skill:rookie"]
        self.assertEqual((rookie["temperature"], rookie["routes_to_missing"]), ("new", ["old"]))
        self.assert_row(rookie, proposed="ask", precedence="new-flagged", shown=True)

    def test_new_alone_is_omitted_counted_and_named(self):
        add_skill(self.cfg.config_repo, "newskill", "Added this week.", days_ago=0)
        payload, by = self.rows("--surface", "skill")
        self.assertEqual(by["skill:newskill"]["temperature"], "new")
        self.assert_row(by["skill:newskill"], proposed=None, precedence="new", shown=False)
        fresh = self.omitted_class(payload, "new")
        self.assertEqual((fresh["count"], fresh["names"]), (1, ["newskill"]))

    def test_a_used_but_oversized_item_proposes_relocate(self):
        names = self.sized_skills(10)
        biggest = names[-1]
        add_history(self.cfg.claude_home, [(f"/{biggest} go", 3)])
        _, by = self.rows("--surface", "skill")
        heavy = by[f"skill:{biggest}"]
        self.assertIn("oversized", heavy["flags"])
        self.assertEqual(heavy["temperature"], "warm")
        # It is earning its place, so it is not retired — it is handed to /trim-context.
        self.assert_row(heavy, proposed="relocate", precedence="heavy", shown=True)

    def test_hot_and_warm_are_silent_keeps_counted_and_not_named(self):
        add_skill(self.cfg.config_repo, "hotskill", "Used hard.")
        add_history(self.cfg.claude_home,
                    [(f"/hotskill {n}", n + 1) for n in range(si.HOT_MIN_USES + 1)])
        payload, by = self.rows()
        self.assert_row(by["skill:hotskill"], proposed=None, precedence="hot-warm", shown=False)
        self.assert_row(by["skill:alpha"], proposed=None, precedence="hot-warm", shown=False)
        silent = self.omitted_class(payload, "hot-warm")
        # Counted, never named: the spec keeps these off the table entirely.
        self.assertGreaterEqual(silent["count"], 2)
        self.assertEqual(silent["names"], [])

    def test_cool_asks(self):
        # `gamma` was typed once, 200 days ago: outside the window, real all-time.
        _, by = self.rows("--surface", "command")
        self.assertEqual(by["command:gamma"]["temperature"], "cool")
        self.assert_row(by["command:gamma"], proposed="ask", precedence="cool", shown=True)

    def test_cold_proposes_retire(self):
        add_skill(self.cfg.config_repo, "coldskill", "Nobody uses this.")
        _, by = self.rows("--surface", "skill")
        self.assertEqual(by["skill:coldskill"]["temperature"], "cold")
        self.assert_row(by["skill:coldskill"], proposed="retire", precedence="cold", shown=True)

    def test_an_item_no_source_could_score_falls_to_the_unmeasured_floor(self):
        payload, by = self.rows("--surface", "claude-md")
        # "Git Workflow" is `null` in the sidecar: no phrase is a fair proxy for it, so nothing
        # measured it. It is counted and named, and proposed on by nothing.
        self.assert_row(by["claude-md:Git Workflow"], proposed=None, precedence="unmeasured",
                        shown=False)
        floor = self.omitted_class(payload, "unmeasured")
        self.assertIn("Git Workflow", floor["names"])

    def test_the_table_is_top_wins(self):
        """A row that matches two signals takes the higher one, every time."""
        self.add_plugin_skill("grilling", "Plugin grilling skill.")
        self.add_untracked_skill("grilling")
        self.keep_in_ledger("skill:grilling")
        _, by = self.rows("--surface", "skill")
        # `kept` sits above `duplicate`, so a recorded keep survives the duplicate check.
        self.assertEqual(sorted(by["skill:grilling"]["flags"]), ["duplicate", "kept"])
        self.assert_row(by["skill:grilling"], proposed=None, precedence="kept", shown=False)

    def test_every_precedence_key_is_reachable_and_unique(self):
        keys = [row.key for row in si.PRECEDENCE_TABLE]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(sorted(si.PRECEDENCE_BY_KEY), sorted(keys))
        # The last row is the floor: it holds for anything, so no item can fall off the table.
        self.assertTrue(si.PRECEDENCE_TABLE[-1].test(None, ""))


class OversizedTests(PrecedenceCase):
    def test_a_surface_under_ten_sized_items_flags_nothing(self):
        self.sized_skills(si.OVERSIZED_MIN_SIZED_ITEMS - 4)   # + alpha, beta, tdd = 9
        payload, _ = self.rows()
        sized = [i for i in payload["items"]
                 if i["surface"] == "skill" and i["bytes_always_loaded"] > 0]
        self.assertEqual(len(sized), si.OVERSIZED_MIN_SIZED_ITEMS - 1)
        self.assertFalse([i["id"] for i in payload["items"] if "oversized" in i["flags"]])

    def test_exactly_ten_sized_items_flags_only_the_largest(self):
        names = self.sized_skills(si.OVERSIZED_MIN_SIZED_ITEMS - 3)   # + alpha, beta, tdd = 10
        payload, _ = self.rows()
        flagged = sorted(i["name"] for i in payload["items"] if "oversized" in i["flags"])
        self.assertEqual(flagged, [names[-1]])

    def test_twenty_sized_items_flag_the_top_decile(self):
        names = self.sized_skills(17)   # + alpha, beta, tdd = 20
        payload, _ = self.rows()
        flagged = sorted(i["name"] for i in payload["items"] if "oversized" in i["flags"])
        self.assertEqual(flagged, sorted(names[-2:]))

    def test_weightless_items_do_not_rank(self):
        """A paused command costs a session nothing, so it is not the heavy end of anything."""
        for n in range(12):
            write(self.cfg.config_repo / f"commands/dead{n:02d}.md.disabled",
                  "---\ndescription: " + "y" * (100 + n) + "\n---\n")
        commit_all(self.cfg.config_repo, "twelve paused commands")
        payload, _ = self.rows("--surface", "command")
        paused = [i for i in payload["items"] if "paused" in i["flags"]]
        self.assertEqual(len(paused), 13)                       # twelve, plus the fixture's `old`
        self.assertFalse([i for i in paused if "oversized" in i["flags"]])

    def test_the_flag_is_measured_per_surface_not_across_the_inventory(self):
        self.sized_skills(si.OVERSIZED_MIN_SIZED_ITEMS - 3)
        payload, _ = self.rows()
        surfaces = {i["surface"] for i in payload["items"] if "oversized" in i["flags"]}
        # Only the skill surface has ten sized items; claude-md's four sections do not rank,
        # however heavy one of them is next to a skill description.
        self.assertEqual(surfaces, {"skill"})


class CollapseTests(PrecedenceCase):
    def test_one_row_per_canonical_plugin(self):
        self.add_plugin_skill("grilling", "Plugin grilling skill.")
        self.add_plugin_skill("wizard", "Plugin wizard skill.")
        self.add_untracked_skill("grilling")
        self.add_untracked_skill("wizard")
        # A second enabled plugin shipping a third skill: its copies collapse separately.
        write(self.cfg.claude_home / "plugins/cache/x/off/1.0.0/skills/ghost/SKILL.md",
              "---\nname: ghost\ndescription: Off-plugin skill.\n---\n")
        self.patch_settings(enabledPlugins={"mp@mp": True, "off@x": True})
        self.add_untracked_skill("ghost")
        payload, by = self.rows("--surface", "skill")
        keys = sorted(c["key"] for c in payload["collapsed"])
        self.assertEqual(keys, ["duplicate:mp", "duplicate:off"])
        mp = self.collapsed_row(payload, "duplicate:mp")
        self.assertEqual((mp["count"], mp["proposed"], mp["surface"]), (2, "retire", "skill"))
        self.assertEqual(sorted(mp["members"]), ["skill:grilling", "skill:wizard"])
        self.assertEqual(self.collapsed_row(payload, "duplicate:off")["members"], ["skill:ghost"])

    def test_one_row_per_mechanical_class(self):
        self.patch_settings(hooks={"Stop": [{"hooks": [
            {"type": "command", "command": "# off one"},
            {"type": "command", "command": "  # off two"},
            {"type": "command", "command": "live.sh"}]}]})
        (self.cfg.claude_home / "projects/-p4/memory").mkdir(parents=True)
        payload, _ = self.rows()
        hooks = self.collapsed_row(payload, "hook:disabled_comment")
        self.assertEqual((hooks["count"], hooks["proposed"]), (2, "retire"))
        self.assertEqual(sorted(hooks["members"]), ["hook:Stop[0][0]", "hook:Stop[0][1]"])
        mem = self.collapsed_row(payload, "memory:empty")
        self.assertEqual((mem["count"], mem["proposed"]), (2, "retire"))
        self.assertEqual(sorted(mem["members"]), ["memory:-p2", "memory:-p4"])

    def test_a_collapsed_row_carries_its_member_count_into_the_markdown(self):
        self.add_plugin_skill("grilling", "Plugin grilling skill.")
        self.add_plugin_skill("wizard", "Plugin wizard skill.")
        self.add_untracked_skill("grilling")
        self.add_untracked_skill("wizard")
        md = self.markdown()
        row = next(ln for ln in md.splitlines() if "loose skill copies" in ln)
        self.assertIn("2 loose skill copies of plugin mp", row)
        self.assertIn("| retire |", row)
        self.assertIn("`grilling`, `wizard`", row)
        # The members are not in the proposals table under their own names.
        proposals = md.split("## Omitted")[0]
        self.assertNotIn("| skill | `grilling` |", proposals)

    def test_members_keep_every_field_and_only_lose_their_row(self):
        self.add_plugin_skill("grilling", "Plugin grilling skill.")
        self.add_untracked_skill("grilling", "Loose copy of grilling.")
        _, by = self.rows("--surface", "skill")
        loose = by["skill:grilling"]
        self.assertEqual(loose["bytes_always_loaded"], len("Loose copy of grilling."))
        self.assertEqual(loose["proposed"], "retire")
        self.assertFalse(loose["shown"])
        self.assertEqual(loose["collapsed_into"], "duplicate:mp")

    def test_a_collapsed_class_is_not_counted_as_omitted(self):
        payload, _ = self.rows()
        mechanical = [e for e in payload["omitted"] if e["key"] == "mechanical"]
        # `mechanical` is a shown row, so it never appears in the omitted summary at all: its
        # members are in the table, standing behind one collapsed row.
        self.assertEqual(mechanical, [])


class OmittedSummaryTests(PrecedenceCase):
    def test_every_suppressing_row_is_reported_even_at_zero(self):
        payload, _ = self.rows()
        keys = [e["key"] for e in payload["omitted"]]
        self.assertEqual(keys, [r.key for r in si.PRECEDENCE_TABLE if not r.shown])

    def test_the_markdown_names_the_suppressed_rows(self):
        add_skill(self.cfg.config_repo, "newskill", "Added this week.", days_ago=0)
        md = self.markdown()
        summary = md.split("## Omitted from the proposals")[1].split("## Full inventory")[0]
        self.assertIn("**new**", summary)
        self.assertIn("`newskill`", summary)
        self.assertIn("**hot-warm**", summary)

    def test_auto_only_names_are_listed(self):
        add_skill(self.cfg.config_repo, "autoskill", "Chosen, never typed.")
        self.add_transcript("t2", *[tool_use(3, "Skill", {"skill": "autoskill"})]
                            * si.AUTO_ONLY_MIN_AUTO)
        md = self.markdown()
        line = next(ln for ln in md.splitlines() if ln.startswith("- **auto_only**"))
        self.assertIn(f"— {1}", line)
        self.assertIn("`autoskill`", line)

    def test_a_count_only_surface_is_counted_but_never_named(self):
        payload, _ = self.rows()
        floor = self.omitted_class(payload, "unmeasured")
        # `-p3` holds files, so it is unmeasured rather than empty — counted, never named.
        self.assertIn("memory:-p3", floor["ids"])
        self.assertNotIn("-p3", floor["names"])
        md = self.markdown()
        summary = md.split("## Omitted from the proposals")[1].split("## Full inventory")[0]
        self.assertIn("names are private", summary)
        self.assertNotIn("-p3", summary)


class TotalsTests(PrecedenceCase):
    def test_the_totals_table_carries_always_loaded_bytes_per_surface(self):
        payload, _ = self.rows()
        md = self.markdown()
        totals = md.split("## Totals")[1].split("## Proposals")[0]
        for surface in si.ENUMERATED_SURFACES:
            chars = payload["totals"][surface]["always_loaded_chars"]
            self.assertIn(f"| {surface} | {payload['totals'][surface]['items']} | {chars:,} |",
                          totals)
        self.assertIn(f"| ALL | {payload['totals']['ALL']['items']} |", totals)

    def test_two_json_files_render_a_before_and_after_table_with_deltas(self):
        before, after = self.root / "before.json", self.root / "after.json"
        rc, _, _ = self.run_cli("--json", str(before))
        self.assertEqual(rc, si.EXIT_OK)
        add_skill(self.cfg.config_repo, "extra", "y" * 500)
        rc, _, _ = self.run_cli("--json", str(after))
        self.assertEqual(rc, si.EXIT_OK)
        rc, stdout, _ = self.run_cli("--compare", str(before), str(after), with_base=False)
        self.assertEqual(rc, si.EXIT_OK)
        row = next(ln for ln in stdout.splitlines() if ln.startswith("| skill |"))
        b = json.loads(before.read_text())["totals"]["skill"]
        a = json.loads(after.read_text())["totals"]["skill"]
        self.assertEqual(a["always_loaded_chars"] - b["always_loaded_chars"], 500)
        self.assertIn(f"{b['items']} → {a['items']}", row)
        self.assertIn("+500", row)
        self.assertIn("| ALL |", stdout)

    def test_a_comparison_input_that_cannot_be_read_exits_two(self):
        rc, _, err = self.run_cli("--compare", str(self.root / "nope.json"),
                                  str(self.root / "also-nope.json"), with_base=False)
        self.assertEqual(rc, si.EXIT_SOURCE_MISSING)
        self.assertIn("comparison input", err)


class RedactionTests(PrecedenceCase):
    """The markdown renderer is always redacted. This is the proof, across every surface."""

    def loaded_fixture(self) -> None:
        """Every kind of private detail the live setup carries, in one tree."""
        self.cfg.claude_json.write_text(json.dumps({"mcpServers": {
            "todoist": {"command": "/private/bin/secret-launcher", "type": "stdio",
                        "args": ["--token", "swordfish"], "env": {"TOKEN": "hunter2"}}}}))
        self.patch_settings(hooks={"Stop": [{"hooks": [
            {"type": "command", "command": "/Users/private/bin/afplay ding.aiff"},
            {"type": "command", "command": "# DISABLED: /Users/private/bin/notify.sh"}]}]})
        (self.cfg.claude_home / "projects/-Users-private-Projects-client-work/memory").mkdir(
            parents=True)
        write(self.cfg.projects_root / "clientwork/.claude/skills/alpha/SKILL.md",
              "---\nname: alpha\ndescription: Vendored.\n---\n")

    def test_the_markdown_carries_no_private_detail_on_any_surface(self):
        self.loaded_fixture()
        md = self.markdown()
        private = (
            str(self.root), str(self.cfg.claude_home), str(self.cfg.config_repo),
            str(self.cfg.projects_root), str(self.cfg.claude_json),   # absolute paths
            "afplay", "ding.aiff", "notify.sh", "DISABLED:",          # hook command text
            "-Users-private-Projects-client-work", "client-work",     # memory slugs
            "secret-launcher", "hunter2", "swordfish", "stdio",       # MCP config values
        )
        for needle in private:
            self.assertNotIn(needle, md, needle)

    def test_vendored_copies_are_repo_names_and_nothing_more(self):
        self.loaded_fixture()
        md = self.markdown()
        row = next(ln for ln in md.splitlines() if ln.startswith("| `alpha` |"))
        self.assertIn("vendored in clientwork, repoA", row)
        # The name, never the path that holds it.
        self.assertNotIn(str(self.cfg.projects_root / "clientwork"), md)

    def test_the_proposals_table_never_names_a_memory_directory(self):
        self.loaded_fixture()
        md = self.markdown()
        proposals = md.split("## Proposals")[1].split("## Omitted")[0]
        self.assertIn("empty auto-memory", proposals)
        for slug in ("-p2", "-p3", "-Users-private"):
            self.assertNotIn(slug, proposals)

    def test_the_json_keeps_what_the_markdown_withholds(self):
        self.loaded_fixture()
        payload, by = self.rows()
        # Redaction is a property of the report, not of the measurement: the apply pass needs
        # the hook text, the slug and the full vendored list, and reads them from here.
        self.assertIn("afplay", by["hook:Stop[0][0]"]["extra"]["command"])
        self.assertIn("memory:-Users-private-Projects-client-work", by)
        self.assertEqual(by["skill:alpha"]["vendored_copies"], ["clientwork", "repoA"])

    def test_the_header_carries_the_local_corpus_caveat(self):
        md = self.markdown()
        head = md.split("## Totals")[0]
        self.assertIn(si.LOCAL_CORPUS_CAVEAT, head)
        self.assertIn("An em dash is unmeasured, never zero.", head)


class TypedCountsAreUnmeasuredWithoutASpellingTests(PrecedenceCase):
    """Inherited problem 1: a measured 0 for something that can never be typed."""

    def test_only_skills_and_commands_report_typed_counts(self):
        _, by = self.rows()
        for item_id in ("skill:alpha", "command:gamma"):
            self.assertIsNotNone(by[item_id]["slash_all"], item_id)
            self.assertIsNotNone(by[item_id]["slash_90d"], item_id)
        for item_id in ("agent:judge", "output-style:plain", "plugin:mp@mp", "mcp:todoist",
                        "hook:Stop[0][0]", "memory:-p2", "claude-md:Git Workflow"):
            self.assertIsNone(by[item_id]["slash_all"], item_id)
            self.assertIsNone(by[item_id]["slash_90d"], item_id)

    def test_the_evidence_cell_says_unmeasured_rather_than_zero(self):
        md = self.markdown()
        agent = next(ln for ln in md.splitlines() if ln.startswith("| `judge` |"))
        self.assertIn("typed —/90d · — all", agent)
        skill = next(ln for ln in md.splitlines() if ln.startswith("| `alpha` |"))
        self.assertIn("typed 1/90d · 1 all", skill)

    def test_an_unmeasured_typed_count_still_sums_into_invocations(self):
        _, by = self.rows("--surface", "agent")
        judge = by["agent:judge"]
        # One dispatch, no typed spelling: the sum is what was measured, not None.
        self.assertEqual((judge["tool_all"], judge["invocations_all"]), (1, 1))


class ColdIsAlwaysMeasuredTests(PrecedenceCase):
    """Inherited problem 2: a `cold` resting on a source nobody read."""

    def test_an_item_with_no_measured_source_is_unknown_not_cold(self):
        _, by = self.rows("--surface", "claude-md")
        # A constraints paragraph has no typed spelling, no transcript spelling, and no sidecar
        # entry. Before this ruling it read `cold`, and `cold` proposes `retire`.
        scope = by["claude-md:Scope discipline"]
        self.assertEqual((scope["slash_all"], scope["tool_all"], scope["trigger_all"]),
                         (None, None, None))
        self.assertEqual(scope["temperature"], "unknown")
        self.assertIsNone(scope["proposed"])

    def test_a_measured_zero_still_earns_cold(self):
        add_skill(self.cfg.config_repo, "coldskill", "Nobody uses this.")
        _, by = self.rows("--surface", "skill")
        cold = by["skill:coldskill"]
        # The history and the transcripts were both read and both came back empty: that is
        # evidence of disuse, and `retire` is a fair thing to propose from it.
        self.assertEqual((cold["slash_all"], cold["tool_all"]), (0, 0))
        self.assertEqual((cold["temperature"], cold["proposed"]), ("cold", "retire"))

    def test_a_sidecar_entry_alone_is_enough_to_earn_cold(self):
        (self.root / "triggers.json").write_text(
            json.dumps({"Git Workflow": ["git workflow mode"]}))
        _, by = self.rows("--surface", "claude-md")
        git = by["claude-md:Git Workflow"]
        # Nothing else can score a section, but the phrases were checked against the history.
        self.assertEqual((git["trigger_all"], git["trigger_90d"]), (0, 0))
        self.assertEqual((git["temperature"], git["proposed"]), ("cold", "retire"))

    def test_a_referrer_still_beats_an_unmeasured_source(self):
        _, by = self.rows("--surface", "claude-md")
        # The Stop prompt hook names "Improvement Mode" by title: something breaks if it goes.
        self.assertEqual(by["claude-md:Improvement Mode"]["temperature"], "cool")


class EvidenceCellStaysInItsTableTests(PrecedenceCase):
    """Inherited problem 3: the right content in the wrong place, past a handful."""

    def vendor_widely(self, count: int) -> list[str]:
        names = [f"repo{n:02d}" for n in range(count)]
        for name in names:
            write(self.cfg.projects_root / f"{name}/.claude/skills/alpha/SKILL.md",
                  "---\nname: alpha\ndescription: Vendored.\n---\n")
        return names

    def test_a_widely_vendored_item_lists_a_few_names_and_counts_the_rest(self):
        self.vendor_widely(23)
        md = self.markdown()
        row = next(ln for ln in md.splitlines() if ln.startswith("| `alpha` |"))
        self.assertIn("vendored in repo00, repo01, repo02 +21 more", row)
        self.assertNotIn("repo10", row)
        # 23 repo names in one cell is 200 characters of the right content in the wrong place.
        self.assertLess(len(row), 300)

    def test_the_full_list_survives_in_the_json(self):
        names = self.vendor_widely(23)
        _, by = self.rows("--surface", "skill")
        # The ledger and a later fleet prune need every one of them.
        self.assertEqual(by["skill:alpha"]["vendored_copies"], sorted(names + ["repoA"]))

    def test_a_short_list_is_printed_whole(self):
        md = self.markdown()
        row = next(ln for ln in md.splitlines() if ln.startswith("| `alpha` |"))
        self.assertIn("vendored in repoA", row)
        self.assertNotIn("more", row)


if __name__ == "__main__":
    unittest.main()
