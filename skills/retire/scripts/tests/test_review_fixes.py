"""Regression tests for the adversarial-review round-1 findings.

Each test pins the behaviour a finding said was wrong, so the defect cannot come back quietly.
Named by what the code must now do, not by finding number — a finding id means nothing to
someone reading this file in six months.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import steering_inventory as si  # noqa: E402

from tests.test_steering_inventory import (  # noqa: E402
    BASE_COMMIT_DAYS_AGO, FixtureCase, commit_all, write,
)


class UnmeasuredBeatsReferrers(FixtureCase):
    """F2 — a referrer is not a measurement, so it can never manufacture a disuse claim."""

    def test_an_item_nothing_measured_is_unknown_even_with_a_referrer(self):
        repo = self.cfg.config_repo
        # A constraints paragraph: no slash form, no tool call, and deliberately no sidecar
        # entry — every count is unmeasurable. Another steering file names it, so it has a
        # referrer and nothing else.
        write(repo / "operating-constraints.md",
              "**Scope discipline.** Do exactly what's asked.\n\n"
              "**Orphan rule.** Nothing measures this one.\n")
        write(repo / "skills/alpha/SKILL.md",
              "---\nname: alpha\ndescription: Mentions the Orphan rule by name.\n---\n")
        commit_all(repo, "add an unmeasurable paragraph with a referrer")

        rc, payload, _ = self.run_json("--surface", "claude-md")
        self.assertEqual(rc, si.EXIT_OK)
        it = self.items_by_id(payload)["claude-md:Orphan rule"]

        self.assertIsNone(it["trigger_all"], "precondition: nothing measured this paragraph")
        self.assertEqual(
            it["temperature"], "unknown",
            "a referrer says another file names it, never that it went unused")
        self.assertIsNone(
            it["proposed"],
            "an unmeasured row must not be put in front of Kyle as a disuse question")

    def test_a_referrer_still_lifts_a_measured_zero_from_cold_to_cool(self):
        """The fix must not go too far: where a source WAS read, a referrer still counts."""
        repo = self.cfg.config_repo
        write(repo / "skills/lonely/SKILL.md",
              "---\nname: lonely\ndescription: Never used, but routed to.\n---\n")
        commit_all(repo, "add lonely", days_ago=BASE_COMMIT_DAYS_AGO)
        rc, payload, _ = self.run_json("--surface", "skill")
        self.assertEqual(rc, si.EXIT_OK)
        it = self.items_by_id(payload)["skill:lonely"]
        self.assertEqual(it["slash_all"], 0, "precondition: the history WAS read and is empty")
        self.assertEqual(it["temperature"], "cold", "no referrer yet")

        write(repo / "skills/alpha/SKILL.md",
              "---\nname: alpha\ndescription: Routes onward.\n---\n\nHand to `lonely` when done.\n")
        commit_all(repo, "route to lonely")
        rc, payload, _ = self.run_json("--surface", "skill")
        it = self.items_by_id(payload)["skill:lonely"]
        self.assertTrue(it["referrers"])
        self.assertEqual(it["temperature"], "cool", "a measured zero plus a referrer is cool")


class PausedSkillsStayVisible(FixtureCase):
    """F3 — three documents promise a skill can be paused; the instrument must see it."""

    def paused(self):
        repo = self.cfg.config_repo
        src = repo / "skills/beta/SKILL.md"
        body = src.read_text()
        src.unlink()
        write(repo / "skills/beta/SKILL.md.disabled", body)
        commit_all(repo, "pause beta")

    def test_a_paused_skill_is_still_enumerated_flagged_and_weightless(self):
        self.paused()
        rc, payload, _ = self.run_json("--surface", "skill")
        self.assertEqual(rc, si.EXIT_OK)
        it = self.items_by_id(payload).get("skill:beta")
        self.assertIsNotNone(it, "a paused skill that vanishes is recorded nowhere at all")
        self.assertIn("paused", it["flags"])
        self.assertEqual(it["bytes_always_loaded"], 0, "a paused skill loads nothing")

    def test_a_route_to_a_paused_skill_dangles(self):
        repo = self.cfg.config_repo
        self.paused()
        write(repo / "commands/gamma.md",
              "---\ndescription: Gamma command.\n---\nWhen finished, hand to `beta`.\n")
        commit_all(repo, "route at the paused skill")
        rc, payload, _ = self.run_json("--surface", "command")
        self.assertEqual(rc, si.EXIT_OK)
        gamma = self.items_by_id(payload)["command:gamma"]
        self.assertIn("beta", gamma["routes_to_missing"])
        self.assertIn("dangling", gamma["flags"])


class ArchivalRecordsAreNotMentions(FixtureCase):
    """F6 — the apply step edits mentions, so history must never become one."""

    def test_reports_plans_and_scratch_never_count_as_mentions(self):
        repo = self.cfg.config_repo
        for rel in ("docs/reports/2026-01-01-steering-inventory.md",
                    "docs/plans/2026-01-01-some-plan.md",
                    ".scratch/some-feature/spec.md"):
            write(repo / rel, "A dated record naming alpha, which must not become a repair.\n")
        write(repo / "docs/guide.md", "Ordinary prose naming alpha, which does owe a repair.\n")
        commit_all(repo, "archival records plus one real mention")

        rc, payload, _ = self.run_json("--surface", "skill")
        self.assertEqual(rc, si.EXIT_OK)
        mentions = self.items_by_id(payload)["skill:alpha"]["mentions"]
        joined = " ".join(mentions)
        self.assertIn("docs/guide.md", joined, "ordinary prose is still a mention")
        for archival in ("docs/reports/", "docs/plans/", ".scratch/"):
            self.assertNotIn(archival, joined,
                             f"{archival} is a historical record, not a stale reference")
