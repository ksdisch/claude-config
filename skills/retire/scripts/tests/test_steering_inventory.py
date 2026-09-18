"""Fixture-driven tests for steering_inventory.py.

Every test builds a throwaway fixture tree (a real git repo, so first-commit dates are real),
drives the script through its command line, and asserts only on what comes out: the JSON
records, the redacted markdown, or the exit code. Nothing here reaches into the script's
intermediate state, and nothing here reads the live machine.

Run from `skills/retire/scripts`:  python3 -m unittest discover -s tests -t .
"""
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import steering_inventory as si  # noqa: E402

NOW = datetime.now(timezone.utc)

# The fixture repo's base commit. Far enough back that nothing in it is `new`.
BASE_COMMIT_DAYS_AGO = 200


def ms(days_ago: int) -> str:
    """history.jsonl timestamps are epoch milliseconds as a string."""
    return str(int((NOW - timedelta(days=days_ago)).timestamp() * 1000))


def iso(days_ago: int) -> str:
    return (NOW - timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def day(days_ago: int) -> str:
    return (NOW - timedelta(days=days_ago)).date().isoformat()


def write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def tool_use(days_ago: int, name: str, inp: dict) -> str:
    """One compact transcript line, exactly as the harness writes them."""
    return json.dumps({"type": "assistant", "timestamp": iso(days_ago),
                       "message": {"content": [{"type": "tool_use", "name": name, "input": inp}]}},
                      separators=(",", ":"))


def git_env(days_ago: int) -> dict:
    """Git isolated from the machine's config, with a fixed author and committer date."""
    stamp = (NOW - timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    return {**os.environ,
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp,
            "GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
            "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid"}


def git(repo: Path, *args: str, days_ago: int = BASE_COMMIT_DAYS_AGO) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True,
                   env=git_env(days_ago))


def commit_all(repo: Path, message: str, days_ago: int = BASE_COMMIT_DAYS_AGO) -> None:
    git(repo, "add", "-A", days_ago=days_ago)
    git(repo, "commit", "-q", "-m", message, days_ago=days_ago)


def add_skill(repo: Path, name: str, description: str, *,
              days_ago: int = BASE_COMMIT_DAYS_AGO) -> None:
    write(repo / f"skills/{name}/SKILL.md",
          f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n")
    commit_all(repo, f"add {name}", days_ago=days_ago)


def add_history(home: Path, rows: list) -> None:
    """Append (display, days_ago) prompts to the fixture history."""
    with open(home / "history.jsonl", "a") as fh:
        for display, days_ago in rows:
            fh.write(json.dumps({"display": display, "timestamp": ms(days_ago),
                                 "project": "/p", "sessionId": "s"}) + "\n")


ALPHA_DESC = ('Alpha does things. Use when Kyle says "alpha please" or "run alpha now". '
              "Hands off to beta and /old.")
BETA_DESC = "Beta does other things across lines."
TDD_DESC = "Loose copy of tdd."


def make_fixture(root: Path) -> "si.Config":
    """A whole miniature setup: a config repo under git and a claude home beside it.

    Built to the shape every later ticket needs — skills, commands, agents, output styles,
    plugins, hooks, history, transcripts, memory dirs, MCP config, vendored copies, a ledger —
    even though this ticket only asserts on the skills surface.
    """
    repo, home, projects = root / "claude-config", root / "home", root / "Projects"

    write(repo / "CLAUDE.md",
          "# Top\n\n@~/.claude/operating-constraints.md\n\n"
          "## Improvement Mode\n\nWhen I say improvement mode, ask first.\n\n"
          "## Git Workflow\n\nAlways branch.\n\n### Sub rule\n\nNested.\n\n"
          "```markdown\n# Not a heading\n```\n")
    write(repo / "operating-constraints.md", "**Scope discipline.** Do exactly what's asked.\n")
    write(repo / "skills/alpha/SKILL.md",
          f"---\nname: alpha\ndescription: {ALPHA_DESC}\n---\n\n# Alpha\n")
    write(repo / "skills/beta/SKILL.md",
          "---\nname: beta\ndescription: >-\n  Beta does other\n  things across lines.\n---\n\n# Beta\n")
    write(repo / "skills/tdd/SKILL.md", f"---\nname: tdd\ndescription: {TDD_DESC}\n---\n")
    write(repo / "commands/gamma.md", "---\ndescription: Gamma command.\n---\nRun gamma.\n")
    write(repo / "commands/old.md.disabled", "---\ndescription: Old command.\n---\n")
    write(repo / "agents/judge.md", "---\nname: judge\ndescription: Judge agent.\n---\n")
    write(repo / "output-styles/plain.md", "---\nname: plain\ndescription: Plain style.\n---\n")
    write(repo / "docs/retired.md",
          "# Retired items\n\n| Date | Item | Surface | Why | Evidence at retirement | Restore | "
          "Downstream copies |\n|---|---|---|---|---|---|---|\n"
          "| 2026-01-01 | skill:zeta | skill | gone | 0 | git revert abc123 | — |\n\n"
          "## Kept on purpose\n\n| Date | Item | Keep because |\n|---|---|---|\n")
    git(repo, "init", "-q", "-b", "main")
    commit_all(repo, "fixture base")

    plugin_dir = home / "plugins/cache/mp/mp/1.0.0"
    write(plugin_dir / "skills/tdd/SKILL.md",
          "---\nname: tdd\ndescription: Plugin tdd skill.\n---\n")
    # `installedAt` is ISO-8601 in every live install record; the epoch-millisecond spelling
    # older records use is covered in tests/test_claude_home_surfaces.py.
    write(home / "plugins/installed_plugins.json", json.dumps({"version": 2, "plugins": {
        "mp@mp": [{"scope": "user", "installPath": str(plugin_dir), "version": "1.0.0",
                   "installedAt": iso(120)}],
        "off@x": [{"scope": "user", "installPath": str(home / "plugins/cache/x/off/1.0.0"),
                   "version": "1.0.0", "installedAt": iso(120)}]}}))
    write(home / "settings.json", json.dumps({
        "enabledPlugins": {"mp@mp": True, "off@x": False},
        "hooks": {
            "Stop": [{"hooks": [
                {"type": "prompt",
                 "prompt": "Kyle's CLAUDE.md defines Improvement Mode; pausing there is fine."},
                {"type": "command", "command": "# DISABLED 2026-08-13: afplay ding.aiff"}]}],
            "PreToolUse": [{"matcher": "Bash",
                            "hooks": [{"type": "command", "command": "bash guard.sh"}]}]}}))
    write(home / "history.jsonl", "\n".join(json.dumps(r) for r in [
        {"display": "/alpha do the thing", "timestamp": ms(3), "project": "/p", "sessionId": "s1"},
        {"display": "alpha please, now", "timestamp": ms(5), "project": "/p", "sessionId": "s1"},
        {"display": "/gamma", "timestamp": ms(200), "project": "/p", "sessionId": "s2"},
        {"display": "/mp:tdd", "timestamp": ms(10), "project": "/p", "sessionId": "s3"},
        {"display": "let's talk about alphabet soup", "timestamp": ms(1), "project": "/p",
         "sessionId": "s3"},
    ]) + "\n")
    write(home / "projects/-p1/t1.jsonl", "\n".join([
        tool_use(2, "Skill", {"skill": "alpha"}),
        tool_use(150, "Agent", {"subagent_type": "judge", "prompt": "x"}),
        tool_use(4, "mcp__todoist__todoist_create_task", {"content": "x"}),
        tool_use(6, "Skill", {"skill": "mp:tdd"}),
        json.dumps({"type": "user", "timestamp": iso(2), "message": {"content": "hello"}}),
    ]) + "\n")
    (home / "projects/-p2/memory").mkdir(parents=True)
    write(home / "projects/-p3/memory/MEMORY.md", "# mem\n")
    write(root / "claude.json",
          json.dumps({"mcpServers": {"todoist": {"command": "npx"},
                                     "docker": {"command": "docker"}}}))
    # The fleet: two repos carrying a vendored copy. A skill copy is a directory with a
    # SKILL.md in it — a bare directory steers nothing, so it is not a copy (ticket 05).
    write(projects / "repoA/.claude/skills/alpha/SKILL.md",
          f"---\nname: alpha\ndescription: {ALPHA_DESC}\n---\n")
    write(projects / "repoB/.claude/commands/gamma.md", "vendored\n")
    write(root / "triggers.json",
          json.dumps({"Improvement Mode": ["improvement mode"], "Git Workflow": None}))

    return si.Config(claude_home=home, config_repo=repo, projects_root=projects,
                     claude_json=root / "claude.json", since_days=si.WINDOW_DEFAULT_DAYS,
                     triggers={"Improvement Mode": ["improvement mode"]}, cache_path=None)


class FixtureCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        # Resolve: on macOS /var is a symlink to /private/var and path comparisons fail without it.
        self.root = Path(self._tmp.name).resolve()
        self.cfg = make_fixture(self.root)

    def tearDown(self):
        self._tmp.cleanup()

    def base_args(self):
        return ["--claude-home", str(self.cfg.claude_home),
                "--config-repo", str(self.cfg.config_repo),
                "--projects-root", str(self.cfg.projects_root),
                "--claude-json", str(self.cfg.claude_json),
                "--triggers", str(self.root / "triggers.json"),
                "--no-cache"]

    def run_cli(self, *extra, with_base=True):
        """Drive the command line; return (exit code, stdout, stderr)."""
        argv = (self.base_args() if with_base else []) + list(extra)
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = si.main(argv)
        return rc, out.getvalue(), err.getvalue()

    def run_json(self, *extra):
        """Drive the command line with --json; return (exit code, parsed JSON, stdout)."""
        out_json = self.root / "inv.json"
        rc, stdout, _ = self.run_cli("--json", str(out_json), *extra)
        payload = json.loads(out_json.read_text()) if out_json.exists() else None
        return rc, payload, stdout

    def items_by_id(self, payload):
        return {i["id"]: i for i in payload["items"]}


class RecordTests(FixtureCase):
    def test_three_skills_one_folded_description(self):
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        self.assertEqual(sorted(i for i in by if i.startswith("skill:")),
                         ["skill:alpha", "skill:beta", "skill:tdd"])
        # The `>-` block scalar is joined with single spaces before it is measured.
        self.assertEqual(by["skill:beta"]["description"], BETA_DESC)
        self.assertEqual(by["skill:beta"]["bytes_always_loaded"], len(BETA_DESC))
        self.assertEqual(by["skill:alpha"]["bytes_always_loaded"], len(ALPHA_DESC))
        self.assertEqual(by["skill:tdd"]["bytes_always_loaded"], len(TDD_DESC))
        self.assertEqual(payload["totals"]["skill"]["items"], 3)
        self.assertEqual(payload["totals"]["skill"]["always_loaded_chars"],
                         len(ALPHA_DESC) + len(BETA_DESC) + len(TDD_DESC))

    def test_typed_counts_window_all_time_and_last_used(self):
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        alpha = self.items_by_id(payload)["skill:alpha"]
        self.assertEqual((alpha["slash_90d"], alpha["slash_all"]), (1, 1))
        # Typed at day 3, but a session chose it at day 2 — last used is the later of the two.
        self.assertEqual(alpha["last_used"], day(2))
        self.assertEqual(alpha["added"], day(BASE_COMMIT_DAYS_AGO))
        self.assertTrue(alpha["tracked"])

    def test_unread_sources_are_unmeasured_not_zero(self):
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        alpha = self.items_by_id(payload)["skill:alpha"]
        beta = self.items_by_id(payload)["skill:beta"]
        # beta's description quotes no phrase, so it has no trigger source at all: the counts
        # stay unmeasured rather than collapsing to a 0 that would read as evidence of disuse.
        self.assertIsNone(beta["trigger_90d"])
        self.assertIsNone(beta["trigger_all"])
        # alpha's description does quote phrases, and the transcripts were read — so both of
        # its count families are real ints. A source that was read never reports None.
        self.assertIsNotNone(alpha["trigger_90d"])
        self.assertEqual(payload["meta"]["transcripts_scanned"], 1)
        self.assertIsNotNone(alpha["tool_90d"])
        self.assertIsNotNone(alpha["tool_all"])


class TypedCountBoundaryTests(FixtureCase):
    def test_slash_form_must_be_followed_by_a_non_name_character(self):
        repo, home = self.cfg.config_repo, self.cfg.claude_home
        add_skill(repo, "hand", "Short name.")
        add_skill(repo, "handoff", "Longer name.")
        add_history(home, [("/handoff please", 2), ("/handoff", 3), ("/handoff-session go", 4),
                           ("/handoffs", 5), ("run /hand later", 6)])
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        # /handoff, /handoff-session and /handoffs all extend "hand" — none of them count for it.
        self.assertEqual(by["skill:hand"]["slash_all"], 0)
        # "/handoff" counts twice; "-session" and the trailing "s" extend the name, and a slash
        # form that does not open the prompt is not a typed invocation.
        self.assertEqual(by["skill:handoff"]["slash_all"], 2)

    def test_namespaced_slash_form_does_not_count_for_the_bare_name(self):
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        # The history holds "/mp:tdd" only.
        self.assertEqual(self.items_by_id(payload)["skill:tdd"]["slash_all"], 0)


class TemperatureTests(FixtureCase):
    def ladder(self):
        repo, home = self.cfg.config_repo, self.cfg.claude_home
        for name in ("hotskill", "warmskill", "coolskill", "coldskill"):
            add_skill(repo, name, f"{name} description.")
        add_skill(repo, "newskill", "Added this week.", days_ago=0)
        add_skill(repo, "newhotskill", "Added this week, used hard.", days_ago=0)
        add_history(home, [(f"/hotskill run {n}", n + 1) for n in range(si.HOT_MIN_USES + 1)])
        add_history(home, [("/warmskill a", 3), ("/warmskill b", 4)])
        add_history(home, [("/coolskill once", 200)])
        add_history(home, [(f"/newhotskill {n}", n + 1) for n in range(si.HOT_MIN_USES + 1)])

    def test_thresholds(self):
        self.ladder()
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        temp = {k: v["temperature"] for k, v in self.items_by_id(payload).items()}
        self.assertEqual(temp["skill:hotskill"], "hot")      # 6 typed in the window
        self.assertEqual(temp["skill:warmskill"], "warm")    # 2 typed in the window
        self.assertEqual(temp["skill:coolskill"], "cool")    # 0 in the window, 1 ever
        self.assertEqual(temp["skill:coldskill"], "cold")    # never typed, no referrers
        self.assertEqual(temp["skill:newskill"], "new")      # first commit inside the window

    def test_new_wins_over_every_count(self):
        self.ladder()
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        newhot = self.items_by_id(payload)["skill:newhotskill"]
        self.assertEqual(newhot["slash_90d"], si.HOT_MIN_USES + 1)
        self.assertEqual(newhot["temperature"], "new")
        self.assertEqual(newhot["added"], day(0))

    def test_proposed_is_retire_for_cold_and_omitted_for_hot_warm_new(self):
        self.ladder()
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        self.assertEqual(by["skill:coldskill"]["proposed"], "retire")
        self.assertEqual(by["skill:coolskill"]["proposed"], "ask")
        for name in ("hotskill", "warmskill", "newskill", "newhotskill"):
            self.assertIsNone(by[f"skill:{name}"]["proposed"], name)


class OutputTests(FixtureCase):
    def test_json_and_md_are_written_and_stdout_stays_quiet(self):
        out_json, out_md = self.root / "inv.json", self.root / "inv.md"
        rc, stdout, _ = self.run_cli("--json", str(out_json), "--md", str(out_md))
        self.assertEqual(rc, si.EXIT_OK)
        self.assertEqual(stdout, "")
        payload = json.loads(out_json.read_text())
        self.assertEqual(payload["meta"]["since_days"], si.WINDOW_DEFAULT_DAYS)
        self.assertEqual(sum(1 for i in payload["items"] if i["surface"] == "skill"), 3)
        md = out_md.read_text()
        self.assertIn("## Totals", md)
        self.assertIn("## skill", md)
        for name in ("alpha", "beta", "tdd"):
            self.assertIn(f"| `{name}` |", md)

    def test_json_alone_writes_no_markdown_to_stdout(self):
        rc, stdout, _ = self.run_cli("--json", str(self.root / "inv.json"))
        self.assertEqual(rc, si.EXIT_OK)
        self.assertEqual(stdout, "")

    def test_markdown_carries_no_paths_and_marks_unmeasured_counts(self):
        out_md = self.root / "inv.md"
        rc, _, _ = self.run_cli("--md", str(out_md))
        self.assertEqual(rc, si.EXIT_OK)
        md = out_md.read_text()
        self.assertNotIn(str(self.root), md)
        self.assertNotIn(str(self.cfg.claude_home), md)
        self.assertIn(si.LOCAL_CORPUS_CAVEAT, md)
        self.assertIn("trig —/—", md)          # trigger hits are unmeasured, never 0

    def test_markdown_goes_to_stdout_when_no_output_file_is_named(self):
        rc, stdout, _ = self.run_cli()
        self.assertEqual(rc, si.EXIT_OK)
        self.assertIn("# Steering inventory", stdout)


class CliTests(FixtureCase):
    def test_every_documented_flag_is_accepted(self):
        out_json, out_md = self.root / "inv.json", self.root / "inv.md"
        rc, _, _ = self.run_cli("--since", "30", "--json", str(out_json), "--md", str(out_md),
                                "--surface", "skill")
        self.assertEqual(rc, si.EXIT_OK)
        meta = json.loads(out_json.read_text())["meta"]
        self.assertEqual(meta["since_days"], 30)
        self.assertEqual(meta["surfaces"], ["skill"])

    def test_meta_reports_the_named_thresholds(self):
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        self.assertEqual(payload["meta"]["thresholds"],
                         {"window_default_days": 90, "hot_min_uses": 5, "warm_min_uses": 1,
                          "auto_only_min_auto": 5})
        self.assertEqual(payload["meta"]["since_days"], 90)

    def test_surface_filter_restricts_output(self):
        rc, payload, _ = self.run_json("--surface", "skill")
        self.assertEqual(rc, si.EXIT_OK)
        self.assertEqual({i["surface"] for i in payload["items"]}, {"skill"})
        self.assertEqual(sorted(payload["totals"]), ["ALL", "skill"])

    def test_unknown_surface_exits_non_zero_and_lists_the_valid_names(self):
        rc, _, err = self.run_cli("--surface", "nonsense")
        self.assertNotEqual(rc, si.EXIT_OK)
        self.assertIn("nonsense", err)
        for name in si.ENUMERATED_SURFACES:
            self.assertIn(name, err)

    def test_config_repo_defaults_to_the_skills_symlink_target(self):
        (self.cfg.claude_home / "skills").symlink_to(self.cfg.config_repo / "skills")
        out_json = self.root / "inv.json"
        argv = ["--claude-home", str(self.cfg.claude_home),
                "--projects-root", str(self.cfg.projects_root),
                "--claude-json", str(self.cfg.claude_json),
                "--triggers", str(self.root / "triggers.json"),
                "--no-cache", "--json", str(out_json)]
        rc, _, _ = self.run_cli(*argv, with_base=False)
        self.assertEqual(rc, si.EXIT_OK)
        payload = json.loads(out_json.read_text())
        self.assertEqual(payload["meta"]["config_repo"], str(self.cfg.config_repo))
        self.assertEqual(sum(1 for i in payload["items"] if i["surface"] == "skill"), 3)


class ExitCodeTests(FixtureCase):
    def test_happy_path_exits_zero(self):
        rc, _, err = self.run_cli("--surface", "skill", "--md", str(self.root / "inv.md"))
        self.assertEqual(rc, 0)
        self.assertIn("OK 3 items", err)

    def test_missing_history_exits_two_naming_the_source(self):
        (self.cfg.claude_home / "history.jsonl").unlink()
        rc, _, err = self.run_cli("--json", str(self.root / "inv.json"))
        self.assertEqual(rc, 2)
        self.assertIn("history.jsonl", err)
        self.assertFalse((self.root / "inv.json").exists())

    def test_empty_history_exits_two_naming_the_source(self):
        (self.cfg.claude_home / "history.jsonl").write_text("")
        rc, _, err = self.run_cli()
        self.assertEqual(rc, 2)
        self.assertIn("history.jsonl", err)

    def test_skills_directory_without_skill_files_exits_three(self):
        for name in ("alpha", "beta", "tdd"):
            (self.cfg.config_repo / f"skills/{name}/SKILL.md").unlink()
        rc, _, err = self.run_cli()
        self.assertEqual(rc, 3)
        self.assertIn("skill", err)

    def test_missing_skills_directory_exits_two(self):
        for name in ("alpha", "beta", "tdd"):
            (self.cfg.config_repo / f"skills/{name}/SKILL.md").unlink()
            (self.cfg.config_repo / f"skills/{name}").rmdir()
        (self.cfg.config_repo / "skills").rmdir()
        rc, _, err = self.run_cli()
        self.assertEqual(rc, 2)
        self.assertIn("skills directory missing", err)


if __name__ == "__main__":
    unittest.main()
