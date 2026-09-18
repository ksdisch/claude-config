"""Referrers, mentions, dangling routes, vendored copies, the ledger read-back, last-edited.

Ticket 05. The shared fixture tree and its helpers live in `tests.test_steering_inventory`.
Same contract as the sibling suites: build a throwaway tree, drive the script's command line,
assert only on what comes out — the JSON records, the redacted markdown, the exit code.

Run from `skills/retire/scripts`:  python3 -m unittest discover -s tests -t .
"""
import unittest
from pathlib import Path

from tests.test_steering_inventory import (BASE_COMMIT_DAYS_AGO, FixtureCase, add_history,
                                           add_skill, commit_all, day, si, write)

# The fixture ledger already records one retirement, `skill:zeta`, and no keeps.
RETIRED_ID = "skill:zeta"


class XrefCase(FixtureCase):
    """Fixture case with the small edits the cross-reference pass needs."""

    def steering_file(self, rel: str, text: str, *, commit: bool = True) -> Path:
        """A file inside the referrer corpus: a skill, a command, an agent, or the prose."""
        path = self.cfg.config_repo / rel
        write(path, text)
        if commit:
            commit_all(self.cfg.config_repo, f"add {rel}")
        return path

    def doc(self, rel: str, text: str, *, commit: bool = True) -> Path:
        """A tracked markdown file outside the referrer corpus: the mention corpus."""
        return self.steering_file(rel, text, commit=commit)

    def refs(self, item_id: str, *extra):
        rc, payload, _ = self.run_json(*extra)
        self.assertEqual(rc, si.EXIT_OK)
        return self.items_by_id(payload)[item_id]


class CorpusTests(XrefCase):
    def test_the_referrer_corpus_is_steering_files_and_prompt_hooks(self):
        self.steering_file("skills/alpha/references/deep.md", "A reference file routes too.\n")
        corpus = si.build_corpus(self.cfg.config_repo, self.cfg.claude_home)
        repo = self.cfg.config_repo
        for rel in ("skills/alpha/SKILL.md", "skills/alpha/references/deep.md",
                    "skills/beta/SKILL.md", "commands/gamma.md", "commands/old.md.disabled",
                    "agents/judge.md", "CLAUDE.md", "operating-constraints.md"):
            self.assertIn(str(repo / rel), corpus, rel)
        # A prompt hook is a steering file that happens to live in JSON; its key is the hook's
        # own id, so a referrer found in it names the row that has to be patched.
        self.assertIn("settings.json:Stop[0][0]", corpus)
        self.assertIn("Improvement Mode", corpus["settings.json:Stop[0][0]"])
        # A command-type hook is a shell line, not steering prose: not part of the corpus.
        self.assertNotIn("settings.json:Stop[0][1]", corpus)
        self.assertNotIn("settings.json:PreToolUse[0][0]", corpus)
        # Output styles and docs are not steering files: nothing in them routes a session.
        self.assertNotIn(str(repo / "output-styles/plain.md"), corpus)
        self.assertNotIn(str(repo / "docs/retired.md"), corpus)

    def test_the_mention_corpus_is_the_other_tracked_markdown(self):
        self.doc("README.md", "Tracked prose about alpha.\n")
        self.doc("notes/scratch.md", "Untracked prose about alpha.\n", commit=False)
        corpus = si.build_corpus(self.cfg.config_repo, self.cfg.claude_home)
        tracked = si.git_tracked(self.cfg.config_repo)
        mentions = si.build_mention_corpus(self.cfg.config_repo, tracked, corpus)
        repo = self.cfg.config_repo
        self.assertIn(str(repo / "README.md"), mentions)
        # Untracked prose is not something a PR can edit, so it is not a repair anyone owes.
        self.assertNotIn(str(repo / "notes/scratch.md"), mentions)
        # No file is ever in both corpora.
        self.assertEqual(set(mentions) & set(corpus), set())
        self.assertNotIn(str(repo / "skills/alpha/SKILL.md"), mentions)

    def test_the_index_the_playbook_and_the_ledger_are_in_neither_corpus(self):
        for rel in si.BOOKKEEPING_DOCS:
            self.doc(rel, "# doc\n\nThis one names beta and coldskill.\n")
        add_skill(self.cfg.config_repo, "coldskill", "Never used.")
        rc, payload, _ = self.run_json("--surface", "skill")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        # Each of the three has its own step in the apply order. Counting them would report the
        # skill's own bookkeeping back as a reason not to retire.
        self.assertEqual(by["skill:coldskill"]["referrers"], [])
        self.assertEqual(by["skill:coldskill"]["mentions"], [])
        self.assertEqual(by["skill:coldskill"]["temperature"], "cold")
        self.assertEqual(by["skill:beta"]["mentions"], [])


class ReferrerTests(XrefCase):
    def test_a_steering_file_that_names_an_item_is_its_referrer(self):
        beta = self.refs("skill:beta", "--surface", "skill")
        # alpha's description says "Hands off to beta and /old."
        self.assertEqual(beta["referrers"],
                         [str(self.cfg.config_repo / "skills/alpha/SKILL.md")])

    def test_an_items_own_files_are_never_its_referrers(self):
        self.steering_file("skills/alpha/references/deep.md", "alpha, alpha, alpha.\n")
        alpha = self.refs("skill:alpha", "--surface", "skill")
        # Its SKILL.md and every reference file beside it name it constantly; none of that is
        # somebody routing to it.
        self.assertEqual(alpha["referrers"], [])

    def test_a_claude_md_section_is_referred_to_by_the_stop_prompt_hook(self):
        imp = self.refs("claude-md:Improvement Mode", "--surface", "claude-md")
        self.assertEqual(imp["referrers"], ["settings.json:Stop[0][0]"])
        # CLAUDE.md names its own headings; the file the section lives in is its own file.
        self.assertNotIn(str(self.cfg.config_repo / "CLAUDE.md"), imp["referrers"])

    def test_matching_is_word_boundary_on_the_name(self):
        add_skill(self.cfg.config_repo, "hand", "Short name.")
        self.steering_file("agents/router.md",
                           "---\nname: router\ndescription: Router.\n---\n"
                           "Route to handoff, or to hands, or to hand-rolled work.\n")
        hand = self.refs("skill:hand", "--surface", "skill")
        # `handoff`, `hands` and `hand-rolled` all extend the name: none of them route to `hand`.
        self.assertEqual(hand["referrers"], [])
        self.steering_file("agents/router.md",
                           "---\nname: router\ndescription: Router.\n---\n"
                           "Route to `hand` when the work is small.\n")
        hand = self.refs("skill:hand", "--surface", "skill")
        self.assertEqual(hand["referrers"], [str(self.cfg.config_repo / "agents/router.md")])

    def test_a_plugin_is_matched_on_its_short_name(self):
        self.steering_file("agents/router.md",
                           "---\nname: router\ndescription: Router.\n---\n"
                           "Hand the grind to mp when it ships the skill.\n")
        rc, payload, _ = self.run_json("--surface", "plugin")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        # The row's id is `plugin:mp@mp`, but a steering file writes the namespace: `mp`.
        self.assertEqual(by["plugin:mp@mp"]["referrers"],
                         [str(self.cfg.config_repo / "agents/router.md")])

    def test_a_hook_and_a_memory_directory_get_no_cross_references(self):
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        for item in payload["items"]:
            if item["surface"] in si.UNNAMEABLE_SURFACES:
                # `Stop[0][1]` is a position and `-p2` is a private path slug. Neither is a name
                # a file could route to, and matching them as words would leak the slug trying.
                self.assertEqual(item["referrers"], [], item["id"])
                self.assertEqual(item["mentions"], [], item["id"])


class MentionTests(XrefCase):
    def test_referrers_and_mentions_are_reported_separately(self):
        add_skill(self.cfg.config_repo, "solo", "Nothing uses it.")
        self.doc("docs/design.md", "The solo skill is described here.\n")
        solo = self.refs("skill:solo", "--surface", "skill")
        self.assertEqual(solo["referrers"], [])
        self.assertEqual(solo["mentions"], [str(self.cfg.config_repo / "docs/design.md")])
        self.steering_file("agents/router.md",
                           "---\nname: router\ndescription: Router.\n---\nHand it to solo.\n")
        solo = self.refs("skill:solo", "--surface", "skill")
        self.assertEqual(solo["referrers"], [str(self.cfg.config_repo / "agents/router.md")])
        self.assertEqual(solo["mentions"], [str(self.cfg.config_repo / "docs/design.md")])

    def test_only_referrers_feed_temperature(self):
        add_skill(self.cfg.config_repo, "described", "Only ever a paragraph in a doc.")
        add_skill(self.cfg.config_repo, "routed", "Only ever the target of a steering file.")
        self.doc("docs/design.md", "A paragraph about the described skill.\n")
        self.steering_file("agents/router.md",
                           "---\nname: router\ndescription: Router.\n---\nHand it to routed.\n")
        rc, payload, _ = self.run_json("--surface", "skill")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        # A doc describing an item is prose to repair on the way out, never evidence of use.
        self.assertEqual(len(by["skill:described"]["mentions"]), 1)
        self.assertEqual(by["skill:described"]["temperature"], "cold")
        self.assertEqual(by["skill:described"]["proposed"], "retire")
        # A steering file routing to it is something that breaks if it goes.
        self.assertEqual(len(by["skill:routed"]["referrers"]), 1)
        self.assertEqual(by["skill:routed"]["temperature"], "cool")
        self.assertEqual(by["skill:routed"]["proposed"], "ask")

    def test_cool_requires_a_referrer_or_an_all_time_use(self):
        for name in ("byreferrer", "byuse", "byneither"):
            add_skill(self.cfg.config_repo, name, f"{name} description.")
        self.steering_file("agents/router.md",
                           "---\nname: router\ndescription: Router.\n---\nGo to byreferrer.\n")
        add_history(self.cfg.claude_home, [("/byuse long ago", 200)])
        rc, payload, _ = self.run_json("--surface", "skill")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        self.assertEqual(by["skill:byreferrer"]["temperature"], "cool")
        self.assertEqual(by["skill:byuse"]["temperature"], "cool")
        self.assertEqual((by["skill:byuse"]["slash_90d"], by["skill:byuse"]["slash_all"]), (0, 1))
        # Nothing in the window, nothing ever, nobody routing to it: the only `cold` of the three.
        self.assertEqual(by["skill:byneither"]["temperature"], "cold")


class DanglingRouteTests(XrefCase):
    def test_a_route_to_a_paused_command_dangles(self):
        alpha = self.refs("skill:alpha", "--surface", "skill")
        # alpha's description routes to `/old`, and `commands/old.md.disabled` is paused: the
        # file is still there, and nothing a session can run is behind it.
        self.assertEqual(alpha["routes_to_missing"], ["old"])
        self.assertIn("dangling", alpha["flags"])

    def test_a_route_to_a_ledger_retired_id_dangles_with_the_prefix_stripped(self):
        self.steering_file("agents/router.md",
                           "---\nname: router\ndescription: Router.\n---\n"
                           "When in doubt hand it to `zeta`.\n")
        router = self.refs("agent:router", "--surface", "agent")
        # The ledger records the retirement as `skill:zeta`; a route is written `zeta`.
        self.assertEqual(si.strip_surface_prefix(RETIRED_ID), "zeta")
        self.assertEqual(router["routes_to_missing"], ["zeta"])
        self.assertIn("dangling", router["flags"])

    def test_every_surface_prefix_is_stripped_and_a_bare_name_is_left_alone(self):
        for surface in si.SURFACE_ORDER:
            self.assertEqual(si.strip_surface_prefix(f"{surface}:thing"), "thing", surface)
        self.assertEqual(si.strip_surface_prefix("thing"), "thing")
        # Only the leading prefix goes; a name that itself holds a colon survives whole.
        self.assertEqual(si.strip_surface_prefix("claude-md:Kickoff Mode → run `/kickoff`"),
                         "Kickoff Mode → run `/kickoff`")

    def test_a_bare_prose_word_is_not_a_route(self):
        self.steering_file("agents/router.md",
                           "---\nname: router\ndescription: Router.\n---\n"
                           "The old way was fine and zeta was a reasonable name.\n")
        router = self.refs("agent:router", "--surface", "agent")
        # Half these names are ordinary English. A route is `/name` or `` `name` `` and nothing
        # else, or every sentence using the word would bury the routes that need patching.
        self.assertEqual(router["routes_to_missing"], [])
        self.assertNotIn("dangling", router["flags"])

    def test_an_item_never_dangles_on_its_own_name(self):
        write(self.cfg.config_repo / "commands/old.md.disabled",
              "---\ndescription: Old command.\n---\nRun `/old` to use this.\n")
        commit_all(self.cfg.config_repo, "old routes to itself")
        old = self.refs("command:old", "--surface", "command")
        self.assertEqual(old["routes_to_missing"], [])
        self.assertNotIn("dangling", old["flags"])

    def test_a_route_in_a_claude_md_section_dangles_on_that_sections_row(self):
        cm = self.cfg.config_repo / "CLAUDE.md"
        cm.write_text(cm.read_text() + "\n## Routing Rule\n\nAlways reach for `/old` first.\n")
        commit_all(self.cfg.config_repo, "add routing rule")
        rule = self.refs("claude-md:Routing Rule", "--surface", "claude-md")
        self.assertEqual(rule["routes_to_missing"], ["old"])
        self.assertIn("dangling", rule["flags"])

    def test_a_surface_filtered_run_still_resolves_a_route_to_an_unlisted_command(self):
        rc, payload, _ = self.run_json("--surface", "skill")
        self.assertEqual(rc, si.EXIT_OK)
        # No command row was enumerated at all, and `/old` still resolves to a paused file: a
        # dangling route is a fact about the referrer, not about the lane being swept.
        self.assertEqual({i["surface"] for i in payload["items"]}, {"skill"})
        self.assertEqual(self.items_by_id(payload)["skill:alpha"]["routes_to_missing"], ["old"])


class LedgerReadBackTests(XrefCase):
    def kept_table(self, *rows: str) -> None:
        ledger = self.cfg.config_repo / "docs/retired.md"
        ledger.write_text(ledger.read_text() + "".join(f"{r}\n" for r in rows))
        commit_all(self.cfg.config_repo, "record keeps")

    def test_kept_is_set_from_the_kept_table_by_surface_qualified_id(self):
        self.kept_table("| 2026-02-02 | `skill:beta` | Load-bearing twice a year. |")
        rc, payload, _ = self.run_json("--surface", "skill")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        self.assertEqual(si.kept_ids(self.cfg.config_repo), {"skill:beta"})
        self.assertIn("kept", by["skill:beta"]["flags"])
        self.assertNotIn("kept", by["skill:alpha"]["flags"])

    def test_the_id_is_surface_qualified_so_two_surfaces_never_collide(self):
        write(self.cfg.config_repo / "commands/beta.md", "---\ndescription: Beta command.\n---\n")
        self.kept_table("| 2026-02-02 | `command:beta` | The command earns its place. |")
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        # A skill and a command of the same name are different rows and different rulings.
        self.assertIn("kept", by["command:beta"]["flags"])
        self.assertNotIn("kept", by["skill:beta"]["flags"])

    def test_a_retirement_row_is_not_a_keep_and_a_keep_is_not_a_retirement(self):
        self.kept_table("| 2026-02-02 | `skill:beta` | Load-bearing. |")
        retired, kept = si.ledger_ids(self.cfg.config_repo)
        # The two tables live in one file and must not bleed into one another.
        self.assertEqual(retired, {RETIRED_ID})
        self.assertEqual(kept, {"skill:beta"})
        self.assertEqual(si.missing_names(self.cfg.config_repo), {"old", "zeta"})

    def test_an_absent_ledger_reads_as_two_empty_tables_not_a_missing_source(self):
        (self.cfg.config_repo / "docs/retired.md").unlink()
        commit_all(self.cfg.config_repo, "remove the ledger")
        self.assertEqual(si.ledger_ids(self.cfg.config_repo), (set(), set()))
        # Before the first retirement there is nothing to read; only the paused command is left.
        self.assertEqual(si.missing_names(self.cfg.config_repo), {"old"})
        rc, payload, _ = self.run_json("--surface", "skill")
        self.assertEqual(rc, si.EXIT_OK)
        self.assertEqual(self.items_by_id(payload)["skill:alpha"]["routes_to_missing"], ["old"])


class VendoredCopyTests(XrefCase):
    def test_skills_commands_and_agents_are_found_by_file_in_a_projects_dot_claude(self):
        write(self.cfg.projects_root / "repoC/.claude/agents/judge.md", "vendored judge\n")
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        # Repo directory names, never paths: this repo is public and the report is committed.
        self.assertEqual(by["skill:alpha"]["vendored_copies"], ["repoA"])
        self.assertEqual(by["command:gamma"]["vendored_copies"], ["repoB"])
        self.assertEqual(by["agent:judge"]["vendored_copies"], ["repoC"])
        self.assertEqual(by["skill:beta"]["vendored_copies"], [])

    def test_a_copy_in_several_repos_names_every_one_of_them(self):
        for repo in ("repoB", "repoC"):
            write(self.cfg.projects_root / f"{repo}/.claude/skills/alpha/SKILL.md",
                  "---\nname: alpha\n---\n")
        alpha = self.refs("skill:alpha", "--surface", "skill")
        self.assertEqual(alpha["vendored_copies"], ["repoA", "repoB", "repoC"])

    def test_a_skill_directory_without_a_skill_file_is_not_a_copy(self):
        (self.cfg.projects_root / "repoC/.claude/skills/beta").mkdir(parents=True)
        beta = self.refs("skill:beta", "--surface", "skill")
        # An empty directory steers nothing — the harness reads SKILL.md or reads nothing.
        self.assertEqual(beta["vendored_copies"], [])

    def test_a_claude_md_section_is_vendored_by_heading(self):
        write(self.cfg.projects_root / "repoC/CLAUDE.md",
              "# Project\n\n## Improvement Mode\n\nA copy of the global rule.\n")
        write(self.cfg.projects_root / "repoD/.claude/CLAUDE.md",
              "## Something Else\n\n**Scope discipline.** A copy of the constraints paragraph.\n")
        rc, payload, _ = self.run_json("--surface", "claude-md")
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        # A global rule copied into a project is a copy by heading, not by file — and the
        # constraints file's unit is the bold-led paragraph, so that is what is matched there.
        self.assertEqual(by["claude-md:Improvement Mode"]["vendored_copies"], ["repoC"])
        self.assertEqual(by["claude-md:Scope discipline"]["vendored_copies"], ["repoD"])
        self.assertEqual(by["claude-md:Git Workflow"]["vendored_copies"], [])

    def test_the_config_repo_and_its_worktrees_are_not_downstream_copies_of_themselves(self):
        # The live projects root holds the config repo and several git worktrees of it. Both
        # carry every global item by construction: counting them would report the source back
        # as evidence that the source is vendored somewhere.
        (self.cfg.projects_root / "claude-config").symlink_to(self.cfg.config_repo)
        worktree = self.cfg.projects_root / "claude-config-wt-thing"
        write(worktree / "CLAUDE.md", "## Improvement Mode\n\nThe same file, another commit.\n")
        write(worktree / ".claude/skills/alpha/SKILL.md", "---\nname: alpha\n---\n")
        (worktree / ".git").write_text(
            f"gitdir: {self.cfg.config_repo / '.git/worktrees/claude-config-wt-thing'}\n")
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        self.assertEqual(by["skill:alpha"]["vendored_copies"], ["repoA"])
        self.assertEqual(by["claude-md:Improvement Mode"]["vendored_copies"], [])

    def test_a_missing_projects_root_is_no_copies_rather_than_a_crash(self):
        rc, payload, _ = self.run_json("--projects-root", str(self.root / "nowhere"))
        self.assertEqual(rc, si.EXIT_OK)
        self.assertEqual(self.items_by_id(payload)["skill:alpha"]["vendored_copies"], [])


class LastEditedTests(XrefCase):
    def test_a_tracked_item_is_dated_by_the_last_commit_touching_it(self):
        write(self.cfg.config_repo / "skills/alpha/references/deep.md", "A later edit.\n")
        commit_all(self.cfg.config_repo, "edit alpha's reference", days_ago=10)
        alpha = self.refs("skill:alpha", "--surface", "skill")
        # A skill is dated by its whole directory: rewriting its reference file is an edit to
        # the skill. And last-edited is not added — the two dates answer different questions.
        self.assertEqual(alpha["last_edited"], day(10))
        self.assertEqual(alpha["added"], day(BASE_COMMIT_DAYS_AGO))

    def test_commands_agents_and_styles_are_dated_by_their_own_file(self):
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        by = self.items_by_id(payload)
        for item_id in ("command:gamma", "command:old", "agent:judge", "output-style:plain"):
            self.assertEqual(by[item_id]["last_edited"], day(BASE_COMMIT_DAYS_AGO), item_id)

    def test_an_untracked_item_falls_back_to_mtime(self):
        write(self.cfg.config_repo / "skills/ghost/SKILL.md",
              "---\nname: ghost\ndescription: Ghost skill.\n---\n")       # never committed
        ghost = self.refs("skill:ghost", "--surface", "skill")
        self.assertFalse(ghost["tracked"])
        # git has nothing to say about a file it ignores; the directory's mtime is all there is.
        self.assertEqual(ghost["last_edited"], day(0))

    def test_a_surface_with_no_file_of_its_own_reports_no_last_edited(self):
        rc, payload, _ = self.run_json()
        self.assertEqual(rc, si.EXIT_OK)
        for item in payload["items"]:
            if item["surface"] in ("plugin", "mcp", "hook", "memory", "claude-md"):
                # A plugin lives in the cache, a server in a website, a section inside a file
                # somebody else edits: none of them has an edit date of its own to report.
                self.assertIsNone(item["last_edited"], item["id"])


class RedactionTests(XrefCase):
    def test_the_evidence_cell_carries_counts_for_referrers_and_mentions_not_paths(self):
        self.doc("docs/design.md", "A paragraph about beta.\n")
        out_md = self.root / "inv.md"
        rc, _, _ = self.run_cli("--surface", "skill", "--md", str(out_md))
        self.assertEqual(rc, si.EXIT_OK)
        row = next(ln for ln in out_md.read_text().splitlines() if "| `beta` |" in ln)
        self.assertIn("refs 1", row)
        self.assertIn("mentions 1", row)
        # The files behind those counts are in the local JSON; naming them here would print
        # absolute paths into a public repo.
        self.assertNotIn(str(self.cfg.config_repo), row)

    def test_vendored_copies_reach_the_markdown_as_repo_names_only(self):
        out_md = self.root / "inv.md"
        rc, _, _ = self.run_cli("--md", str(out_md))
        self.assertEqual(rc, si.EXIT_OK)
        md = out_md.read_text()
        self.assertIn("vendored in repoA", md)
        # The basename is the one downstream detail the redaction rules allow; the path it sits
        # at is not, and neither is anything else private.
        for private in (str(self.root), str(self.cfg.projects_root), str(self.cfg.claude_home),
                        str(self.cfg.config_repo)):
            self.assertNotIn(private, md)

    def test_a_dangling_route_names_the_target_and_the_last_edit_date_is_shown(self):
        out_md = self.root / "inv.md"
        rc, _, _ = self.run_cli("--surface", "skill", "--md", str(out_md))
        self.assertEqual(rc, si.EXIT_OK)
        row = next(ln for ln in out_md.read_text().splitlines() if "| `alpha` |" in ln)
        self.assertIn("routes→ old", row)
        self.assertIn("dangling", row)
        self.assertIn(f"edited {day(BASE_COMMIT_DAYS_AGO)}", row)

    def test_a_prompt_hooks_text_never_reaches_the_markdown_through_a_referrer(self):
        out_md = self.root / "inv.md"
        rc, _, _ = self.run_cli("--md", str(out_md))
        self.assertEqual(rc, si.EXIT_OK)
        md = out_md.read_text()
        # `Improvement Mode` is `cool` because of the Stop prompt hook, and the prompt that made
        # it so stays in the JSON: the count is the evidence, the text is not. The hook's own
        # row still renders by position — that is its name, and it carries nothing private.
        self.assertIn("| `Improvement Mode` |", md)
        self.assertIn("| `Stop[0][0]` |", md)
        for text in ("pausing there is fine", "Kyle's CLAUDE.md defines",
                     "settings.json:Stop", str(self.cfg.claude_home)):
            self.assertNotIn(text, md)


if __name__ == "__main__":
    unittest.main()
