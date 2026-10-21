"""`check` over the files the loop defenses write: an overview, a park, an unpark, a prereq.

Each fixture is the topic file as it stands right after one defense's write, so a passing test
means that write leaves a file the loop can continue on.

Run from `skills/compass/scripts`:  python3 -m unittest discover
"""
import unittest

from tests.test_check import CheckCase

FRONT = """\
---
topic: Kubernetes networking
why: I'm moving our staging app onto k8s and need to debug why pods can't reach each other.
status: open
workspace:
created: 2026-10-19
updated: 2026-10-20
---

# Kubernetes networking

"""

OVERVIEW = """\
## Overview
1. **Pod IP** — every pod gets its own cluster-routable IP; containers in a pod share it.
2. **CNI plugin** — the component that actually wires pod IPs onto the network.
3. **Service** — a stable virtual IP and DNS name in front of a changing set of pods.
4. **kube-proxy** — programs each node so traffic to a Service IP reaches a backing pod.
5. **Cluster DNS** — resolves `<service>.<namespace>.svc` names to Service IPs.
6. **NetworkPolicy** — rules that restrict which pods may talk; default is allow-all.

How they connect: a pod reaches another by DNS name, DNS gives a Service IP, kube-proxy turns
that into a pod IP, and the CNI plugin carries the packet, unless a NetworkPolicy drops it.

Sources:
- Kubernetes docs, Cluster Networking — https://kubernetes.io/docs/concepts/cluster-administration/networking/
- Kubernetes docs, Service — https://kubernetes.io/docs/concepts/services-networking/service/

"""

QUESTIONS = """\
## Questions

### Q1: Why does my pod resolve the service name but time out connecting?
- status: open
- last recalled:

"""

LOG = """\
## Session log
- 2026-10-20 — Started; wrote the overview; logged Q1.
"""


class OverviewTests(CheckCase):
    def test_an_overview_written_before_any_question_passes(self):
        text = FRONT + OVERVIEW + "## Questions\n\n" + LOG
        rc, report = self.check(text)
        self.assertEqual(rc, 0, report)

    def test_an_overview_and_the_first_question_it_led_to_pass(self):
        rc, report = self.check(FRONT + OVERVIEW + QUESTIONS + LOG)
        self.assertEqual(rc, 0, report)

    def test_an_overview_added_below_existing_questions_is_reported(self):
        self.assertViolation(FRONT + QUESTIONS + OVERVIEW + LOG, "section-order")

    def test_a_second_overview_instead_of_revising_the_first_is_reported(self):
        self.assertViolation(FRONT + OVERVIEW + OVERVIEW + QUESTIONS + LOG, "section-duplicate")


PARKED = FRONT + """\
## Questions

### Q1: Why does my pod resolve the service name but time out connecting?
- status: open
- last recalled:

### Q2: How does the CNI plugin choose between VXLAN and BGP?
- status: parked
- park reason: Overlay internals matter for running clusters; my why is debugging one app.
- last recalled:

### Q2.1: What's the MTU cost of VXLAN encapsulation?
- status: parked
- park reason: Parked with Q2; same overlay internals.
- last recalled:

## Session log
- 2026-10-20 — Logged Q1, Q2, Q2.1; parked Q2 and Q2.1.
"""

UNPARKED = PARKED.replace(
    "- status: parked\n"
    "- park reason: Overlay internals matter for running clusters; my why is debugging one app.\n",
    "- status: open\n",
).replace(
    "- 2026-10-20 — Logged Q1, Q2, Q2.1; parked Q2 and Q2.1.",
    "- 2026-10-20 — Logged Q1, Q2, Q2.1; parked Q2 and Q2.1.\n"
    "- 2026-10-21 — Unparked Q2: staging runs a VXLAN overlay after all.",
)


class ParkTests(CheckCase):
    def test_a_confirmed_park_with_its_follow_up_keeps_both_reasons_and_passes(self):
        rc, report = self.check(PARKED)
        self.assertEqual(rc, 0, report)

    def test_a_park_that_drops_a_follow_ups_reason_is_reported(self):
        text = PARKED.replace("- park reason: Parked with Q2; same overlay internals.\n", "")
        self.assertViolation(text, "parked-needs-reason")

    def test_an_unparked_question_is_open_again_without_its_reason_and_passes(self):
        self.assertIn("### Q2: How does the CNI plugin choose between VXLAN and BGP?\n"
                      "- status: open\n- last recalled:\n", UNPARKED)
        rc, report = self.check(UNPARKED)
        self.assertEqual(rc, 0, report)


PREREQ = FRONT + """\
## Questions

### Q1: Why does my pod resolve the service name but time out connecting?
- status: open
- last recalled:

### Q1.1: What is a NetworkPolicy, and what does a pod allow by default?
- status: prereq
- last recalled:

### Q2: Should staging use one namespace or several?
- status: open
- last recalled:

## Session log
- 2026-10-20 — Logged Q1, Q2; Q1 blocked on a prerequisite, logged Q1.1 (prereq).
"""

PREREQ_ANSWERED = PREREQ.replace(
    "### Q1.1: What is a NetworkPolicy, and what does a pod allow by default?\n"
    "- status: prereq\n- last recalled:\n",
    "### Q1.1: What is a NetworkPolicy, and what does a pod allow by default?\n"
    "- status: answered\n- answered by: claude\n- last recalled:\n\n"
    "#### Answer\nA NetworkPolicy selects pods and lists the traffic they accept; a pod no "
    "policy selects accepts everything.\n\n"
    "#### Sources\n- Kubernetes docs, Network Policies — "
    "https://kubernetes.io/docs/concepts/services-networking/network-policies/\n",
)


class PrereqTests(CheckCase):
    def test_a_prereq_logged_under_the_question_it_blocks_passes(self):
        rc, report = self.check(PREREQ)
        self.assertEqual(rc, 0, report)

    def test_a_prereq_for_a_question_that_does_not_exist_is_reported(self):
        self.assertViolation(PREREQ.replace("### Q1.1:", "### Q3.1:"), "tree-orphan")

    def test_an_answered_prereq_passes_once_it_carries_sources(self):
        rc, report = self.check(PREREQ_ANSWERED)
        self.assertEqual(rc, 0, report)

    def test_an_answered_prereq_without_sources_is_reported(self):
        text = PREREQ_ANSWERED.replace(
            "#### Sources\n- Kubernetes docs, Network Policies — "
            "https://kubernetes.io/docs/concepts/services-networking/network-policies/\n", "")
        self.assertViolation(text, "answered-needs-sources")


if __name__ == "__main__":
    unittest.main()
