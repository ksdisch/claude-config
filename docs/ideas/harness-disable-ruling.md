# Harness disable ruling: keep/cut pass over Matt Pocock's disable list

**Status:** Idea — not committed. Mined from "Claude Code's system tools are SO BLOATED" (https://www.youtube.com/watch?v=oLx4yCbeklQ) by `cc-yt-idea-mine` on 2026-08-22.

## Premise

Matt disabled: plan-mode tools, AskUserQuestion, cron tools, the bundled code-review
skill, dynamic workflows, remote control, claude.ai connectors, and artifacts. Copied
blindly into this setup, five of those eight break live workflows. The idea worth
capturing is not his list — it's the one-time decision pass: rule keep/cut on each
built-in against *this* setup's actual usage, and pocket the savings on the genuine
cuts.

## The bet

Two or three of the eight are genuinely unused here and each is a one-line settings
change worth tokens on every request. The rest get an explicit, recorded "keep because
X" so the question never has to be re-litigated.

## Decisions / open questions

This capture's job is to force these calls, not pre-decide them. The known conflicts:

- **Dynamic workflows** — `disableWorkflows` conflicts with ultracode orchestration:
  `/autonomous-milestone`, `/brainstorm`, `/replenish` all dispatch via the Workflow tool.
- **Remote control** — `disableRemoteControl` conflicts with `remoteControlAtStartup:
  true` in settings.json and `/launch --remote`.
- **Artifacts** — `disableArtifact` conflicts with `paper-gloss` (publishes claude.ai
  Artifacts) and artifact-based deliverables generally.
- **AskUserQuestion** — a bare-name deny conflicts with the CLAUDE.md
  clarifying-questions/option-formatting convention.
- **Cron tools** — a bare-name deny conflicts with `/schedule` and DogHood's
  `/scheduled-reconcile` (a live scheduled trigger).
- **Bundled skills** — `disableBundledSkills` is all-or-nothing and conflicts with
  active `/code-review` usage (incl. `/code-review ultra`).
- **Plan-mode tools** — plausible cut: `/explore-plan` covers the plan-shaped flow as a
  command; how often plan *mode* itself gets used is the open question.
- **Connectors** — per-connector, not global; ruled separately in
  [`connector-audit-prune.md`](connector-audit-prune.md).

## Credible first step

A one-sitting review with Kyle: the eight features in a table — mechanism, observed
usage, conflict if cut, recommendation — ending in recorded keep/cut verdicts and a
single settings.json PR for the cuts.

## Dependencies

- **Verified 2026-08-22** (claude-code-guide agent, current docs): the mechanisms exist —
  `disableBundledSkills` / `disableWorkflows` / `disableRemoteControl` /
  `disableClaudeAiConnectors` / `disableArtifact` as settings keys
  (https://code.claude.com/docs/en/settings-reference.md); plan-mode tools,
  AskUserQuestion, and cron tools have **no dedicated disable keys** and are cut via
  bare tool names in `permissions.deny`, which removes the definition from the payload
  (https://www.aihero.dev/how-to-kill-the-bloat-in-claude-codes-system-prompt).
- Before/after measurement: [`system-prompt-inspector.md`](system-prompt-inspector.md).

## Explicitly out of scope

- Automating the audit — that's [`trim-context-harness-lane.md`](trim-context-harness-lane.md);
  this is the manual pass that teaches the lane what to look for.
- Any disable Kyle hasn't explicitly ruled on.

## Source segment

> "So, I didn't want it to control when I entered and exited plan mode. So, I just
> disabled those tools, and the tool definitions get removed from the system prompt. I
> personally really hate the ask user question tool… Equally, I don't want it to
> schedule crons for me, so I just deleted those as well."
