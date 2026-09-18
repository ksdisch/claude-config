"""Session-chosen usage from the transcripts, and the per-file cache behind it.

Ticket 02. The shared fixture tree and its helpers live in `tests.test_steering_inventory`;
everything here either drives the script's command line over that tree or exercises the
transcript reader directly over transcript files this module writes into the fixture home.

Run from `skills/retire/scripts`:  python3 -m unittest discover -s tests -t .
"""
import json
import os
import unittest
from datetime import timedelta
from pathlib import Path

from tests.test_steering_inventory import (NOW, FixtureCase, add_history, add_skill, day, iso,
                                           si, tool_use, write)

SINCE = NOW - timedelta(days=si.WINDOW_DEFAULT_DAYS)


def transcript(home: Path) -> Path:
    """The fixture's one pre-built transcript."""
    return home / "projects/-p1/t1.jsonl"


class TranscriptCase(FixtureCase):
    """Fixture case whose CLI args leave the cache switched on."""

    def cached_args(self, *extra):
        return [a for a in self.base_args() if a != "--no-cache"] + list(extra)

    def run_cached_json(self, *extra):
        out = self.root / "cached.json"
        rc, _, err = self.run_cli(*self.cached_args("--json", str(out)), with_base=False)
        payload = json.loads(out.read_text()) if out.exists() else None
        return rc, payload, err

    @property
    def cache_file(self) -> Path:
        return self.cfg.claude_home / "cache" / "retire" / "transcripts.json"

    def transcripts(self, cache_path=None):
        return si.Transcripts(self.cfg.claude_home / "projects", cache_path)


class ExtractionTests(TranscriptCase):
    def test_every_kind_of_call_is_collected_in_one_pass(self):
        # One read collects skill, agent and MCP calls together: the agent and MCP surfaces
        # consume these tallies later without re-reading gigabytes.
        events = si.extract_events(transcript(self.cfg.claude_home))
        self.assertEqual([(kind, key) for _, kind, key in events],
                         [("skill", "alpha"), ("agent", "judge"), ("mcp", "todoist"),
                          ("skill", "mp:tdd")])

    def test_skill_calls_count_as_session_chosen_for_the_named_skill(self):
        t = self.transcripts()
        self.assertEqual(t.count("skill", "alpha", SINCE), (1, 1, day(2)))
        self.assertEqual(t.count("skill", "beta", SINCE), (0, 0, None))

    def test_agent_and_mcp_tallies_are_available_from_the_same_pass(self):
        t = self.transcripts()
        self.assertEqual(t.count("agent", "judge", SINCE), (1, 0, day(150)))
        self.assertEqual(t.count("mcp", "todoist", SINCE), (1, 1, day(4)))
        self.assertEqual(t.count("mcp", "docker", SINCE), (0, 0, None))

    def test_a_plugin_skill_counts_under_both_its_bare_and_namespaced_spelling(self):
        # The plugin ships `tdd`; a session may call it either way. The fixture holds the
        # namespaced spelling, and this adds the bare one.
        write(self.cfg.claude_home / "projects/-p1/t2.jsonl",
              tool_use(7, "Skill", {"skill": "tdd"}) + "\n")
        t = self.transcripts()
        self.assertEqual(si.skill_spellings("tdd", "mp"), ["tdd", "mp:tdd"])
        self.assertEqual(si.skill_spellings("tdd"), ["tdd"])
        self.assertEqual(t.count("skill", "tdd", SINCE)[:2], (1, 1))
        self.assertEqual(t.count("skill", "mp:tdd", SINCE)[:2], (1, 1))
        # Asked for both spellings, the plugin's skill counts both calls as one item.
        self.assertEqual(t.count("skill", si.skill_spellings("tdd", "mp"), SINCE), (2, 2, day(6)))

    def test_a_namespaced_call_never_counts_for_the_house_copy(self):
        # `skills/tdd/` is a loose copy of the plugin's skill. `mp:tdd` went to the plugin, so
        # the house row must not inherit it — that is what makes retiring the copy safe.
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        tdd = self.items_by_id(payload)["skill:tdd"]
        self.assertEqual((tdd["tool_all"], tdd["tool_90d"]), (0, 0))


class MalformedLineTests(TranscriptCase):
    def test_malformed_lines_are_skipped_without_aborting_the_file(self):
        write(self.cfg.claude_home / "projects/-p1/t2.jsonl", "\n".join([
            '{"type":"assistant","timestamp":"' + iso(3) + '","message":{"content":[{"type":"too',
            'not json at all "name":"Skill"',
            '{"name":"Skill"}',                                        # no timestamp, no message
            '{"timestamp":"' + iso(3) + '","message":"\\"name\\":\\"Skill\\""}',  # message a string
            '{"timestamp":"nonsense","message":{"content":[{"type":"tool_use","name":"Skill",'
            '"input":{"skill":"beta"}}]}}',                            # unusable timestamp
            tool_use(3, "Skill", {"skill": "beta"}),                   # the one good line
            '{"timestamp":"' + iso(3) + '","message":{"content":[{"type":"tool_use",'
            '"name":"Skill","input":null}]}}',                         # input not a dict
        ]) + "\n")
        t = self.transcripts()
        self.assertEqual(t.files_scanned, 2)
        self.assertEqual(t.files_unreadable, 0)
        self.assertEqual(t.count("skill", "beta", SINCE)[:2], (1, 1))

    def test_a_file_of_nothing_but_garbage_is_read_and_contributes_zero(self):
        # Read-but-empty is a true zero; it must not read as an unreadable source.
        write(self.cfg.claude_home / "projects/-p1/t2.jsonl", 'garbage\n{"name":"Skill"\n')
        t = self.transcripts()
        self.assertEqual((t.files_scanned, t.files_unreadable), (2, 0))

    def test_only_needle_bearing_lines_reach_the_json_parser(self):
        path = self.cfg.claude_home / "projects/-p1/t2.jsonl"
        write(path, "\n".join([tool_use(3, "Skill", {"skill": "beta"})]
                              + ['{"type":"user","message":{"content":"chatter"}}'] * 50) + "\n")
        seen = []
        real = si.json.loads

        def counting(text, *a, **kw):
            seen.append(text)
            return real(text, *a, **kw)

        si.json.loads = counting
        try:
            events = si.extract_events(path)
        finally:
            si.json.loads = real
        self.assertEqual(len(seen), 1)                     # 51 lines in, one line parsed
        self.assertEqual([(k, v) for _, k, v in events], [("skill", "beta")])

    def test_a_tool_call_spelled_without_the_exact_needle_is_not_counted(self):
        # The deliberate cost of the substring pre-filter: transcripts are compact JSON, so a
        # pretty-printed line is not a transcript line and is skipped unparsed.
        spaced = json.dumps({"type": "assistant", "timestamp": iso(3),
                             "message": {"content": [{"type": "tool_use", "name": "Skill",
                                                      "input": {"skill": "beta"}}]}})
        self.assertNotIn('"name":"Skill"', spaced)
        write(self.cfg.claude_home / "projects/-p1/t2.jsonl", spaced + "\n")
        self.assertEqual(self.transcripts().count("skill", "beta", SINCE)[:2], (0, 0))


class RowWiringTests(TranscriptCase):
    def test_invocations_are_the_sum_and_last_used_the_latest_of_both_sources(self):
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        alpha = self.items_by_id(payload)["skill:alpha"]
        self.assertEqual((alpha["slash_90d"], alpha["tool_90d"]), (1, 1))
        self.assertEqual((alpha["slash_all"], alpha["tool_all"]), (1, 1))
        self.assertEqual((alpha["invocations_90d"], alpha["invocations_all"]), (2, 2))
        # Typed at day 3, chosen by a session at day 2 — the later of the two wins.
        self.assertEqual(alpha["last_used"], day(2))

    def test_the_evidence_column_shows_typed_and_auto_separately(self):
        out_md = self.root / "inv.md"
        rc, _, _ = self.run_cli("--md", str(out_md))
        self.assertEqual(rc, si.EXIT_OK)
        md = out_md.read_text()
        self.assertIn("typed 1/90d · 1 all · auto 1/1", md)     # alpha: one of each
        self.assertIn("typed 0/90d · 0 all · auto 0/0", md)     # beta: read, and genuinely zero

    def test_meta_reports_how_many_transcripts_were_scanned(self):
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        self.assertEqual(payload["meta"]["transcripts_scanned"], 1)
        self.assertEqual(payload["meta"]["transcripts_unreadable"], 0)


class AutoOnlyFlagTests(TranscriptCase):
    def auto_calls(self, name: str, n: int, days_ago: int) -> None:
        write(self.cfg.claude_home / f"projects/-p1/{name}.jsonl",
              "\n".join(tool_use(days_ago, "Skill", {"skill": name}) for _ in range(n)) + "\n")

    def test_flag_is_set_when_nothing_was_typed_and_the_window_auto_count_clears_the_bar(self):
        for name in ("autoskill", "nearlyauto", "typedtoo"):
            add_skill(self.cfg.config_repo, name, f"{name} description.")
        self.auto_calls("autoskill", si.AUTO_ONLY_MIN_AUTO, 3)
        self.auto_calls("nearlyauto", si.AUTO_ONLY_MIN_AUTO - 1, 3)
        self.auto_calls("typedtoo", si.AUTO_ONLY_MIN_AUTO, 3)
        add_history(self.cfg.claude_home, [("/typedtoo go", 4)])
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        self.assertIn("auto_only", by["skill:autoskill"]["flags"])
        self.assertNotIn("auto_only", by["skill:nearlyauto"]["flags"])   # one call short
        self.assertNotIn("auto_only", by["skill:typedtoo"]["flags"])     # Kyle typed it too
        self.assertNotIn("auto_only", by["skill:beta"]["flags"])         # never used at all

    def test_calls_outside_the_window_do_not_earn_the_flag(self):
        add_skill(self.cfg.config_repo, "staleauto", "Chosen, but long ago.")
        self.auto_calls("staleauto", si.AUTO_ONLY_MIN_AUTO, 200)
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        stale = self.items_by_id(payload)["skill:staleauto"]
        self.assertEqual((stale["tool_all"], stale["tool_90d"]), (si.AUTO_ONLY_MIN_AUTO, 0))
        self.assertNotIn("auto_only", stale["flags"])

    def test_the_flag_never_changes_the_proposed_verdict(self):
        add_skill(self.cfg.config_repo, "autoskill", "Chosen, never typed.")
        self.auto_calls("autoskill", si.AUTO_ONLY_MIN_AUTO, 3)
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        flagged = self.items_by_id(payload)["skill:autoskill"]
        self.assertIn("auto_only", flagged["flags"])
        # Amended by ticket 06: the precedence table replaced the temperature-only mapping, so
        # the claim is now made against that table. `auto_only` is deliberately not one of the
        # flags it reads, so a hot row carrying it is still the silent keep a hot row always was.
        self.assertNotIn("auto_only", si.PROPOSAL_FLAGS)
        self.assertEqual((flagged["temperature"], flagged["proposed"], flagged["precedence"]),
                         ("hot", None, "hot-warm"))
        # And the flag is invisible to the table for every other row too: dropping it changes
        # nothing about what any row proposes.
        for item in payload["items"]:
            stripped = si.Item(id=item["id"], surface=item["surface"], name=item["name"],
                               path="", bytes_always_loaded=0,
                               flags=[f for f in item["flags"] if f != "auto_only"],
                               temperature=item["temperature"], last_edited=item["last_edited"],
                               duplicate_of=item["duplicate_of"])
            si.propose(stripped, payload["meta"]["since"])
            self.assertEqual(stripped.proposed, item["proposed"], item["id"])


class CacheTests(TranscriptCase):
    def second_transcript(self) -> Path:
        p = self.cfg.claude_home / "projects/-p1/t2.jsonl"
        write(p, tool_use(3, "Skill", {"skill": "beta"}) + "\n")
        return p

    def test_the_cache_lands_under_the_claude_homes_cache_directory(self):
        self.assertFalse(self.cache_file.exists())
        rc, payload, _ = self.run_cached_json()
        self.assertEqual(rc, si.EXIT_OK)
        self.assertTrue(self.cache_file.exists())
        self.assertEqual(payload["meta"]["transcripts_cache_hits"], 0)   # nothing cached yet

    def test_a_second_run_reports_cache_hits_equal_to_the_file_count(self):
        self.second_transcript()
        self.assertEqual(self.run_cached_json()[0], si.EXIT_OK)
        rc, payload, _ = self.run_cached_json()
        self.assertEqual(rc, si.EXIT_OK)
        self.assertEqual(payload["meta"]["transcripts_scanned"], 2)
        self.assertEqual(payload["meta"]["transcripts_cache_hits"], 2)

    def test_the_cache_key_carries_the_path_size_and_mtime(self):
        self.assertEqual(self.run_cached_json()[0], si.EXIT_OK)
        entry = json.loads(self.cache_file.read_text())[str(transcript(self.cfg.claude_home))]
        st = transcript(self.cfg.claude_home).stat()
        self.assertEqual((entry["size"], entry["mtime"]), (st.st_size, st.st_mtime))

    def test_a_touched_file_is_re_read_while_the_rest_stay_cached(self):
        touched = self.second_transcript()
        self.assertEqual(self.run_cached_json()[0], si.EXIT_OK)
        st = touched.stat()
        os.utime(touched, (st.st_atime + 60, st.st_mtime + 60))
        rc, payload, _ = self.run_cached_json()
        self.assertEqual(rc, si.EXIT_OK)
        self.assertEqual(payload["meta"]["transcripts_cache_hits"], 1)   # the untouched one
        self.assertEqual(payload["meta"]["transcripts_scanned"], 2)

    def test_changed_content_is_picked_up_rather_than_served_from_the_cache(self):
        self.assertEqual(self.run_cached_json()[0], si.EXIT_OK)
        with open(transcript(self.cfg.claude_home), "a") as fh:
            fh.write(tool_use(1, "Skill", {"skill": "alpha"}) + "\n")
        rc, payload, _ = self.run_cached_json()
        self.assertEqual(rc, si.EXIT_OK)
        alpha = self.items_by_id(payload)["skill:alpha"]
        self.assertEqual((alpha["tool_all"], alpha["last_used"]), (2, day(1)))

    def test_a_corrupt_cache_is_ignored_rather_than_fatal(self):
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.cache_file.write_text("{not json")
        rc, payload, _ = self.run_cached_json()
        self.assertEqual(rc, si.EXIT_OK)
        self.assertEqual(payload["meta"]["transcripts_cache_hits"], 0)

    def test_the_cache_holds_only_the_files_that_still_exist(self):
        gone = self.second_transcript()
        self.assertEqual(self.run_cached_json()[0], si.EXIT_OK)
        self.assertEqual(len(json.loads(self.cache_file.read_text())), 2)
        gone.unlink()
        self.assertEqual(self.run_cached_json()[0], si.EXIT_OK)
        self.assertEqual(list(json.loads(self.cache_file.read_text())),
                         [str(transcript(self.cfg.claude_home))])

    def test_no_cache_writes_nothing_and_never_reports_a_hit(self):
        for _ in range(2):
            rc, payload, _ = self.run_json()              # base_args carries --no-cache
            self.assertEqual(rc, si.EXIT_OK)
            self.assertEqual(payload["meta"]["transcripts_cache_hits"], 0)
        self.assertFalse(self.cache_file.exists())

    def test_no_cache_ignores_a_cache_that_is_already_on_disk(self):
        self.assertEqual(self.run_cached_json()[0], si.EXIT_OK)
        self.assertTrue(self.cache_file.exists())
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        self.assertEqual(payload["meta"]["transcripts_cache_hits"], 0)


class NoTranscriptsTests(TranscriptCase):
    def remove_transcripts(self) -> None:
        for p in sorted((self.cfg.claude_home / "projects").rglob("*.jsonl")):
            p.unlink()

    def test_a_missing_transcript_directory_exits_two_naming_the_source(self):
        self.remove_transcripts()
        rc, _, err = self.run_cli("--json", str(self.root / "inv.json"))
        self.assertEqual(rc, si.EXIT_SOURCE_MISSING)
        self.assertIn("transcripts", err)
        self.assertIn("projects", err)
        self.assertFalse((self.root / "inv.json").exists())

    def test_every_file_unreadable_exits_two_rather_than_reporting_zeroes(self):
        target = transcript(self.cfg.claude_home)
        target.chmod(0o000)
        if os.access(target, os.R_OK):
            self.skipTest("this user cannot make a file unreadable")
        rc, _, err = self.run_cli()
        self.assertEqual(rc, si.EXIT_SOURCE_MISSING)
        self.assertIn("1 found, 1 unreadable", err)

    def test_one_unreadable_file_among_readable_ones_is_not_fatal(self):
        bad = self.cfg.claude_home / "projects/-p1/t2.jsonl"
        write(bad, tool_use(3, "Skill", {"skill": "beta"}) + "\n")
        bad.chmod(0o000)
        if os.access(bad, os.R_OK):
            self.skipTest("this user cannot make a file unreadable")
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        self.assertEqual(payload["meta"]["transcripts_scanned"], 1)
        self.assertEqual(payload["meta"]["transcripts_unreadable"], 1)
        # The unreadable file's skill is reported as 0, because the file it lived in was not read
        # — the honest reading of a partial corpus, with the shortfall named in the meta.
        self.assertEqual(self.items_by_id(payload)["skill:beta"]["tool_all"], 0)


if __name__ == "__main__":
    unittest.main()
