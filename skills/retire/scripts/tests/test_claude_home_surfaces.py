"""The surfaces that live in the claude home rather than in the config repo.

Ticket 04. Plugins (install dating, the enable map, duplicate loose copies), MCP servers (the
union of the user-scope config and what transcripts actually called), hook entries, auto-memory
directories, and agent dispatches counted as session-chosen. Same contract as the sibling
suites: build a throwaway tree, drive the script's command line, assert only on what comes out.

Run from `skills/retire/scripts`:  python3 -m unittest discover -s tests -t .
"""
import json
import unittest
from pathlib import Path

from tests.test_steering_inventory import (BASE_COMMIT_DAYS_AGO, FixtureCase, add_history,
                                           commit_all, day, iso, si, tool_use, write)

PLUGIN_TDD_DESC = "Plugin tdd skill."


class HomeCase(FixtureCase):
    """Fixture case with the small edits the claude-home surfaces need."""

    @property
    def settings_path(self) -> Path:
        return self.cfg.claude_home / "settings.json"

    def settings(self) -> dict:
        return json.loads(self.settings_path.read_text())

    def patch_settings(self, **changes) -> None:
        self.settings_path.write_text(json.dumps({**self.settings(), **changes}))

    def install_record(self) -> dict:
        return json.loads(
            (self.cfg.claude_home / "plugins/installed_plugins.json").read_text())

    def patch_plugin(self, key: str, **changes) -> None:
        record = self.install_record()
        record["plugins"][key][0].update(changes)
        (self.cfg.claude_home / "plugins/installed_plugins.json").write_text(json.dumps(record))

    def add_plugin_skill(self, name: str, description: str) -> None:
        """Ship another skill from the fixture's enabled plugin."""
        write(self.cfg.claude_home / f"plugins/cache/mp/mp/1.0.0/skills/{name}/SKILL.md",
              f"---\nname: {name}\ndescription: {description}\n---\n")

    def add_untracked_skill(self, name: str, description: str = "Loose copy.") -> None:
        """A skill directory the fixture repo never commits — what `npx skills` leaves behind."""
        write(self.cfg.config_repo / f"skills/{name}/SKILL.md",
              f"---\nname: {name}\ndescription: {description}\n---\n")

    def add_transcript(self, name: str, *lines: str) -> None:
        write(self.cfg.claude_home / f"projects/-p1/{name}.jsonl", "\n".join(lines) + "\n")


class PluginTests(HomeCase):
    def test_rows_come_from_the_install_record_and_the_enable_map(self):
        rc, payload, _ = self.run_json("--surface", "plugin")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        self.assertEqual(sorted(by), ["plugin:mp@mp", "plugin:off@x"])
        self.assertTrue(by["plugin:mp@mp"]["extra"]["enabled"])
        self.assertFalse(by["plugin:off@x"]["extra"]["enabled"])
        self.assertEqual(by["plugin:mp@mp"]["extra"]["version"], "1.0.0")
        self.assertEqual([s["name"] for s in by["plugin:mp@mp"]["extra"]["skills"]], ["tdd"])

    def test_a_disabled_plugin_is_flagged_and_costs_a_session_nothing(self):
        # It ships a skill, and that skill still sits in the cache: what makes its weight 0 is
        # the enable map, not an empty install directory.
        write(self.cfg.claude_home / "plugins/cache/x/off/1.0.0/skills/ghost/SKILL.md",
              "---\nname: ghost\ndescription: Off-plugin skill.\n---\n")
        rc, payload, _ = self.run_json("--surface", "plugin")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        # Enabled: every request pays for the descriptions it ships.
        self.assertEqual(by["plugin:mp@mp"]["bytes_always_loaded"], len(PLUGIN_TDD_DESC))
        self.assertEqual(by["plugin:mp@mp"]["flags"], [])
        # Disabled: still installed, still an item, but weightless until it is switched back on.
        self.assertIn("disabled", by["plugin:off@x"]["flags"])
        self.assertEqual([s["name"] for s in by["plugin:off@x"]["extra"]["skills"]], ["ghost"])
        self.assertEqual(by["plugin:off@x"]["bytes_always_loaded"], 0)

    def test_an_enabled_plugins_bytes_are_the_sum_of_every_skill_it_ships(self):
        self.add_plugin_skill("grilling", "Plugin grilling skill.")
        rc, payload, _ = self.run_json("--surface", "plugin")
        self.assertEqual(rc, si.EXIT_OK)
        mp = self.items_by_id(payload)["plugin:mp@mp"]
        self.assertEqual(mp["bytes_always_loaded"],
                         len(PLUGIN_TDD_DESC) + len("Plugin grilling skill."))

    def test_installed_at_is_the_added_date_and_drives_new(self):
        rc, payload, _ = self.run_json("--surface", "plugin")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        # The fixture installs both 120 days ago: dated, and outside the window.
        self.assertEqual(by["plugin:mp@mp"]["added"], day(120))
        self.assertNotEqual(by["plugin:mp@mp"]["temperature"], "new")
        self.patch_plugin("mp@mp", installedAt=iso(3))
        rc, payload, _ = self.run_json("--surface", "plugin")
        self.assertEqual(rc, si.EXIT_OK)
        fresh = self.items_by_id(payload)["plugin:mp@mp"]
        # A plugin installed this week has had no chance to be used: never proposed for removal.
        self.assertEqual((fresh["added"], fresh["temperature"]), (day(3), "new"))
        self.assertIsNone(fresh["proposed"])

    def test_an_epoch_millisecond_install_stamp_is_dated_too(self):
        stamp = int(si.datetime.fromisoformat(iso(30).replace("Z", "+00:00")).timestamp() * 1000)
        self.patch_plugin("mp@mp", installedAt=stamp)
        rc, payload, _ = self.run_json("--surface", "plugin")
        self.assertEqual(rc, si.EXIT_OK)
        self.assertEqual(self.items_by_id(payload)["plugin:mp@mp"]["added"], day(30))

    def test_an_unusable_install_stamp_reports_no_date_rather_than_a_wrong_one(self):
        self.patch_plugin("mp@mp", installedAt="whenever")
        rc, payload, _ = self.run_json("--surface", "plugin")
        self.assertEqual(rc, si.EXIT_OK)
        self.assertIsNone(self.items_by_id(payload)["plugin:mp@mp"]["added"])

    def test_a_plugin_is_used_when_a_session_calls_a_skill_it_ships(self):
        rc, payload, _ = self.run_json("--surface", "plugin")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        # The fixture transcript holds one `mp:tdd` call, at day 6. A plugin is never invoked by
        # name, so its skills' calls are its whole usage record.
        mp = by["plugin:mp@mp"]
        self.assertEqual((mp["tool_all"], mp["tool_90d"], mp["last_used"]), (1, 1, day(6)))
        self.assertEqual(mp["temperature"], "warm")
        # Read, and genuinely zero — not unmeasured.
        self.assertEqual((by["plugin:off@x"]["tool_all"], by["plugin:off@x"]["tool_90d"]), (0, 0))

    def test_a_plugins_own_mcp_server_counts_for_it(self):
        self.add_transcript("t2", tool_use(8, "mcp__plugin_mp_widget__do", {"x": 1}))
        rc, payload, _ = self.run_json("--surface", "plugin")
        self.assertEqual(rc, si.EXIT_OK)
        mp = self.items_by_id(payload)["plugin:mp@mp"]
        # One `mp:tdd` skill call plus one call to the server the plugin registers.
        self.assertEqual((mp["tool_all"], mp["tool_90d"]), (2, 2))

    def test_a_plugins_namespaced_agent_counts_for_it(self):
        self.add_transcript("t2", tool_use(9, "Agent", {"subagent_type": "mp:reviewer"}))
        rc, payload, _ = self.run_json("--surface", "plugin")
        self.assertEqual(rc, si.EXIT_OK)
        mp = self.items_by_id(payload)["plugin:mp@mp"]
        # A plugin that ships agents rather than skills is reached through them; the dispatch is
        # namespaced with the plugin's short name, which is what ties it back to this row.
        self.assertEqual((mp["tool_all"], mp["tool_90d"]), (2, 2))

    def test_a_house_agent_of_the_same_name_does_not_count_for_a_plugin(self):
        self.add_transcript("t2", tool_use(9, "Agent", {"subagent_type": "judge"}))
        rc, payload, _ = self.run_json("--surface", "plugin")
        self.assertEqual(rc, si.EXIT_OK)
        self.assertEqual(self.items_by_id(payload)["plugin:mp@mp"]["tool_all"], 1)

    def test_a_missing_settings_file_is_a_missing_source_not_an_empty_plugin_list(self):
        self.settings_path.unlink()
        rc, _, err = self.run_cli("--surface", "plugin")
        self.assertEqual(rc, si.EXIT_SOURCE_MISSING)
        self.assertIn("settings.json", err)


class DuplicateSkillTests(HomeCase):
    def test_an_untracked_copy_of_a_plugin_skill_is_flagged_with_its_canonical_name(self):
        self.add_plugin_skill("grilling", "Plugin grilling skill.")
        self.add_untracked_skill("grilling")
        rc, payload, _ = self.run_json("--surface", "skill")
        self.assertEqual(rc, si.EXIT_OK)
        loose = self.items_by_id(payload)["skill:grilling"]
        self.assertIn("duplicate", loose["flags"])
        # The canonical spelling is what survives the copy's removal, so it is what the row names.
        self.assertEqual(loose["duplicate_of"], "mp:grilling")
        self.assertFalse(loose["tracked"])

    def test_a_tracked_skill_of_the_same_name_is_left_alone(self):
        rc, payload, _ = self.run_json("--surface", "skill")
        self.assertEqual(rc, si.EXIT_OK)
        # `skills/tdd` is committed: Kyle's own, whatever the plugin happens to ship.
        tdd = self.items_by_id(payload)["skill:tdd"]
        self.assertTrue(tdd["tracked"])
        self.assertNotIn("duplicate", tdd["flags"])
        self.assertIsNone(tdd["duplicate_of"])

    def test_a_disabled_plugins_skills_make_no_duplicates(self):
        write(self.cfg.claude_home / "plugins/cache/x/off/1.0.0/skills/ghost/SKILL.md",
              "---\nname: ghost\ndescription: Off-plugin skill.\n---\n")
        self.add_untracked_skill("ghost")
        rc, payload, _ = self.run_json("--surface", "skill")
        self.assertEqual(rc, si.EXIT_OK)
        ghost = self.items_by_id(payload)["skill:ghost"]
        # `off@x` ships nothing into a session, so the loose copy is the only copy there is.
        self.assertNotIn("duplicate", ghost["flags"])
        self.assertIsNone(ghost["duplicate_of"])

    def test_a_loose_copy_of_nothing_is_not_a_duplicate(self):
        self.add_untracked_skill("unique")
        rc, payload, _ = self.run_json("--surface", "skill")
        self.assertEqual(rc, si.EXIT_OK)
        self.assertNotIn("duplicate", self.items_by_id(payload)["skill:unique"]["flags"])

    def test_the_flag_survives_a_run_that_asks_only_for_the_skill_surface(self):
        self.add_plugin_skill("grilling", "Plugin grilling skill.")
        self.add_untracked_skill("grilling")
        rc, payload, _ = self.run_json("--surface", "skill")
        self.assertEqual(rc, si.EXIT_OK)
        # The plugin cache is read for the duplicate check even when no plugin row is asked for.
        self.assertEqual({i["surface"] for i in payload["items"]}, {"skill"})
        loose = self.items_by_id(payload)["skill:grilling"]
        self.assertEqual(loose["duplicate_of"], "mp:grilling")

    def test_the_markdown_names_the_canonical_plugin_skill(self):
        self.add_plugin_skill("grilling", "Plugin grilling skill.")
        self.add_untracked_skill("grilling")
        out_md = self.root / "inv.md"
        rc, _, _ = self.run_cli("--surface", "skill", "--md", str(out_md))
        self.assertEqual(rc, si.EXIT_OK)
        row = next(ln for ln in out_md.read_text().splitlines() if "| `grilling` |" in ln)
        self.assertIn("dup of `mp:grilling`", row)
        self.assertIn("duplicate", row)


class McpTests(HomeCase):
    def test_rows_are_the_union_of_the_config_and_the_transcripts(self):
        self.add_transcript("t2", tool_use(5, "mcp__claude_ai_Gmail__search_threads", {"q": "x"}))
        rc, payload, _ = self.run_json("--surface", "mcp")
        self.assertEqual(rc, si.EXIT_OK)
        # `docker` and `todoist` are configured; the Gmail connector exists in no local file and
        # would be invisible if the config were the whole source.
        self.assertEqual(sorted(self.items_by_id(payload)),
                         ["mcp:claude_ai_Gmail", "mcp:docker", "mcp:todoist"])

    def test_session_chosen_counts_and_last_used_come_from_the_transcripts(self):
        rc, payload, _ = self.run_json("--surface", "mcp")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        todoist = by["mcp:todoist"]
        self.assertEqual((todoist["tool_all"], todoist["tool_90d"], todoist["last_used"]),
                         (1, 1, day(4)))
        # Configured, never called, and the corpus was read: a measured zero, not unmeasured.
        self.assertEqual((by["mcp:docker"]["tool_all"], by["mcp:docker"]["tool_90d"]), (0, 0))
        self.assertEqual(by["mcp:docker"]["temperature"], "cold")

    def test_a_connector_only_server_is_labelled_as_such(self):
        self.add_transcript("t2", tool_use(5, "mcp__claude_ai_Gmail__search_threads", {"q": "x"}))
        rc, payload, _ = self.run_json("--surface", "mcp")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        gmail = by["mcp:claude_ai_Gmail"]
        self.assertIn("connector_only", gmail["flags"])
        self.assertEqual(gmail["extra"]["origin"], "connector")
        self.assertEqual((gmail["tool_all"], gmail["tool_90d"]), (1, 1))
        # A configured server is not a connector.
        self.assertNotIn("connector_only", by["mcp:todoist"]["flags"])
        self.assertEqual(by["mcp:todoist"]["extra"]["origin"], "config")

    def test_a_denied_connector_is_flagged(self):
        self.patch_settings(deniedMcpServers=[{"serverName": "claude.ai Gmail"}])
        self.add_transcript("t2", tool_use(5, "mcp__claude_ai_Gmail__search_threads", {"q": "x"}))
        rc, payload, _ = self.run_json("--surface", "mcp")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        # The deny list spells the name as the website does; a transcript flattens it. Joining
        # the two is the only way a denied connector's own usage row finds its ruling.
        self.assertEqual(si.mcp_key("claude.ai Gmail"), "claude_ai_Gmail")
        self.assertIn("denied", by["mcp:claude_ai_Gmail"]["flags"])
        self.assertNotIn("denied", by["mcp:todoist"]["flags"])

    def test_a_hyphenated_server_is_one_row_not_two(self):
        self.cfg.claude_json.write_text(json.dumps({"mcpServers": {"basic-memory": {}}}))
        self.add_transcript("t2", tool_use(5, "mcp__basic-memory__search", {"q": "x"}))
        rc, payload, _ = self.run_json("--surface", "mcp")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        # A hyphen survives into the tool name untouched. Flattening it would split the server
        # into a configured row with no calls and a "connector" row holding all of them.
        self.assertEqual(si.mcp_key("basic-memory"), "basic-memory")
        self.assertEqual([i for i in by if "basic" in i], ["mcp:basic-memory"])
        row = by["mcp:basic-memory"]
        self.assertEqual(row["extra"]["origin"], "config")
        self.assertEqual((row["tool_all"], row["tool_90d"]), (1, 1))

    def test_a_plugins_own_server_is_not_called_a_connector(self):
        self.add_transcript("t2", tool_use(8, "mcp__plugin_mp_widget__do", {"x": 1}))
        rc, payload, _ = self.run_json("--surface", "mcp")
        self.assertEqual(rc, si.EXIT_OK)
        widget = self.items_by_id(payload)["mcp:plugin_mp_widget"]
        self.assertEqual(widget["extra"]["origin"], "plugin")
        self.assertEqual(widget["flags"], [])

    def test_the_markdown_carries_no_mcp_config_values(self):
        (self.cfg.claude_json).write_text(json.dumps({"mcpServers": {
            "todoist": {"command": "/private/bin/secret-launcher", "type": "stdio",
                        "env": {"TOKEN": "hunter2"}}}}))
        out_md = self.root / "inv.md"
        rc, _, _ = self.run_cli("--surface", "mcp", "--md", str(out_md))
        self.assertEqual(rc, si.EXIT_OK)
        md = out_md.read_text()
        self.assertIn("| `todoist` |", md)
        for secret in ("secret-launcher", "hunter2", "/private/bin", str(self.cfg.claude_json)):
            self.assertNotIn(secret, md)


class HookTests(HomeCase):
    def test_ids_carry_the_event_group_and_index(self):
        rc, payload, _ = self.run_json("--surface", "hook")
        self.assertEqual(rc, si.EXIT_OK)
        self.assertEqual(sorted(self.items_by_id(payload)),
                         ["hook:PreToolUse[0][0]", "hook:Stop[0][0]", "hook:Stop[0][1]"])
        pre = self.items_by_id(payload)["hook:PreToolUse[0][0]"]
        self.assertEqual((pre["extra"]["event"], pre["extra"]["group"], pre["extra"]["index"]),
                         ("PreToolUse", 0, 0))
        self.assertEqual(pre["extra"]["matcher"], "Bash")

    def test_a_comment_only_command_is_flagged(self):
        rc, payload, _ = self.run_json("--surface", "hook")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        # `# DISABLED 2026-08-13: afplay ding.aiff` is a hook switched off by commenting it out.
        self.assertIn("disabled_comment", by["hook:Stop[0][1]"]["flags"])
        self.assertNotIn("disabled_comment", by["hook:PreToolUse[0][0]"]["flags"])

    def test_a_prompt_hook_keeps_its_text_for_the_referrer_corpus(self):
        rc, payload, _ = self.run_json("--surface", "hook")
        self.assertEqual(rc, si.EXIT_OK)
        prompt = self.items_by_id(payload)["hook:Stop[0][0]"]
        self.assertEqual(prompt["extra"]["type"], "prompt")
        # The Stop prompt routes to CLAUDE.md sections by title: retiring one has to patch it,
        # so the text has to survive into the JSON the referrer pass reads.
        self.assertIn("Improvement Mode", prompt["extra"]["command"])

    def test_hook_text_never_reaches_the_markdown(self):
        out_md = self.root / "inv.md"
        rc, _, _ = self.run_cli("--surface", "hook", "--md", str(out_md))
        self.assertEqual(rc, si.EXIT_OK)
        md = out_md.read_text()
        self.assertIn("| `Stop[0][1]` |", md)          # the row is there, by position
        for text in ("bash guard.sh", "afplay", "DISABLED 2026-08-13",
                     "pausing there is fine", str(self.cfg.claude_home)):
            self.assertNotIn(text, md)

    def test_a_hook_is_unmeasured_rather_than_cold(self):
        rc, payload, _ = self.run_json("--surface", "hook")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        for item in payload["items"]:
            # No source names a hook entry, so calling one `cold` would claim a disuse nothing
            # measured. It is unmeasured, and an unmeasured hook proposes nothing.
            self.assertEqual(item["temperature"], "unknown", item["id"])
            self.assertIsNone(item["tool_all"], item["id"])
        for live in ("hook:Stop[0][0]", "hook:PreToolUse[0][0]"):
            self.assertIsNone(by[live]["proposed"], live)
            self.assertEqual(by[live]["precedence"], "unmeasured", live)
        # Amended by ticket 06: a hook commented out is still unmeasured, but `disabled_comment`
        # outranks temperature in the precedence table — it is a ruling Kyle already made in the
        # file, and the proposal is to finish it. Its row is collapsed with the rest of its class.
        off = by["hook:Stop[0][1]"]
        self.assertEqual((off["temperature"], off["proposed"], off["precedence"]),
                         ("unknown", "retire", "mechanical"))
        self.assertEqual(off["collapsed_into"], "hook:disabled_comment")


class MemoryTests(HomeCase):
    def test_an_empty_directory_is_flagged_and_a_populated_one_is_not(self):
        rc, payload, _ = self.run_json("--surface", "memory")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        self.assertEqual(sorted(by), ["memory:-p2", "memory:-p3"])
        self.assertIn("empty", by["memory:-p2"]["flags"])
        self.assertEqual(by["memory:-p2"]["extra"]["files"], 0)
        self.assertNotIn("empty", by["memory:-p3"]["flags"])
        self.assertEqual(by["memory:-p3"]["extra"]["files"], 1)

    def test_bytes_are_the_files_the_directory_holds(self):
        rc, payload, _ = self.run_json("--surface", "memory")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        self.assertEqual(by["memory:-p3"]["bytes_always_loaded"], len("# mem\n"))
        self.assertEqual(by["memory:-p2"]["bytes_always_loaded"], 0)
        self.assertEqual(payload["totals"]["memory"]["items"], 2)

    def test_the_markdown_reports_a_count_and_never_a_slug(self):
        out_md = self.root / "inv.md"
        rc, _, _ = self.run_cli("--surface", "memory", "--md", str(out_md))
        self.assertEqual(rc, si.EXIT_OK)
        md = out_md.read_text()
        self.assertIn("## memory", md)
        self.assertIn("2 memory entries", md)
        self.assertIn("1 flagged `empty`", md)
        # A slug is the project's path with the separators flattened — a private project list.
        for slug in ("-p2", "-p3", str(self.cfg.claude_home)):
            self.assertNotIn(slug, md)

    def test_a_memory_directory_is_unmeasured_rather_than_cold(self):
        rc, payload, _ = self.run_json("--surface", "memory")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        for item in payload["items"]:
            self.assertEqual(item["temperature"], "unknown", item["id"])
        # Amended by ticket 06: a directory holding files is unmeasured and proposes nothing, but
        # an empty one is `empty`, and the precedence table retires the mechanical classes above
        # any temperature — nothing about its emptiness needed measuring.
        self.assertIsNone(by["memory:-p3"]["proposed"])
        self.assertEqual(by["memory:-p3"]["precedence"], "unmeasured")
        self.assertEqual(by["memory:-p2"]["proposed"], "retire")
        self.assertEqual(by["memory:-p2"]["collapsed_into"], "memory:empty")


class AgentDispatchTests(HomeCase):
    def test_a_dispatch_counts_as_session_chosen_for_the_named_agent(self):
        rc, payload, _ = self.run_json("--surface", "agent")
        self.assertEqual(rc, si.EXIT_OK)
        judge = self.items_by_id(payload)["agent:judge"]
        # The fixture dispatches `judge` once, 150 days ago: outside the window, real all-time.
        self.assertEqual((judge["tool_all"], judge["tool_90d"], judge["last_used"]),
                         (1, 0, day(150)))
        self.assertEqual(judge["temperature"], "cool")

    def test_an_agent_nobody_dispatched_reports_a_measured_zero(self):
        write(self.cfg.config_repo / "agents/idle.md",
              "---\nname: idle\ndescription: Never dispatched.\n---\n")
        commit_all(self.cfg.config_repo, "add idle agent")
        rc, payload, _ = self.run_json("--surface", "agent")
        self.assertEqual(rc, si.EXIT_OK)
        idle = self.items_by_id(payload)["agent:idle"]
        self.assertEqual((idle["tool_all"], idle["tool_90d"]), (0, 0))
        self.assertEqual(idle["added"], day(BASE_COMMIT_DAYS_AGO))
        self.assertEqual(idle["temperature"], "cold")

    def test_a_recent_dispatch_warms_the_agent_row(self):
        self.add_transcript("t2", *[tool_use(2, "Agent", {"subagent_type": "judge"})] * 3)
        rc, payload, _ = self.run_json("--surface", "agent")
        self.assertEqual(rc, si.EXIT_OK)
        judge = self.items_by_id(payload)["agent:judge"]
        self.assertEqual((judge["tool_all"], judge["tool_90d"]), (4, 3))
        self.assertEqual(judge["temperature"], "warm")

    def test_a_skill_call_of_the_same_name_does_not_count_for_the_agent(self):
        # `Skill` and `Agent` calls are different kinds in the same pass; a skill named like an
        # agent must not inherit its uses.
        self.add_transcript("t2", tool_use(2, "Skill", {"skill": "judge"}))
        rc, payload, _ = self.run_json("--surface", "agent")
        self.assertEqual(rc, si.EXIT_OK)
        self.assertEqual(self.items_by_id(payload)["agent:judge"]["tool_90d"], 0)

    def test_agents_are_never_flagged_auto_only(self):
        self.add_transcript("t2", *[tool_use(2, "Agent", {"subagent_type": "judge"})]
                            * (si.AUTO_ONLY_MIN_AUTO + 1))
        rc, payload, _ = self.run_json("--surface", "agent")
        self.assertEqual(rc, si.EXIT_OK)
        # An agent has no typed spelling at all, so "never typed" says nothing about it.
        self.assertNotIn("auto_only", self.items_by_id(payload)["agent:judge"]["flags"])


class HomeSurfaceFilterTests(HomeCase):
    def test_every_claude_home_surface_name_is_accepted_and_filters(self):
        for surface in ("plugin", "mcp", "hook", "memory"):
            with self.subTest(surface=surface):
                rc, payload, _ = self.run_json("--surface", surface)
                self.assertEqual(rc, si.EXIT_OK)
                self.assertTrue(payload["items"])
                self.assertEqual({i["surface"] for i in payload["items"]}, {surface})
                self.assertEqual(sorted(payload["totals"]), ["ALL", surface])
                self.assertEqual(payload["meta"]["surfaces"], [surface])

    def test_the_default_run_carries_every_claude_home_surface(self):
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        surfaces = {i["surface"] for i in payload["items"]}
        for surface in ("plugin", "mcp", "hook", "memory"):
            self.assertIn(surface, surfaces)

    def test_the_live_markdown_keeps_its_redactions_across_every_surface(self):
        out_md = self.root / "inv.md"
        rc, _, _ = self.run_cli("--md", str(out_md))
        self.assertEqual(rc, si.EXIT_OK)
        md = out_md.read_text()
        for private in (str(self.root), str(self.cfg.claude_home), str(self.cfg.config_repo),
                        "afplay", "bash guard.sh", "-p2", "-p3"):
            self.assertNotIn(private, md)


if __name__ == "__main__":
    unittest.main()
