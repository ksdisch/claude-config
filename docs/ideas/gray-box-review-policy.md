# Gray-box review policy: design the interface, delegate the implementation

**Status:** Idea — not committed. Mined from ""Software Fundamentals Matter More Than Ever" — Matt Pocock" (https://www.youtube.com/watch?v=v4F1gFy-hqg) by `cc-yt-idea-mine` on 2026-08-21.

## Premise

Pocock's answer to the "shipping more than your brain can keep up with" failure mode:
treat non-critical deep modules as gray boxes — "I'm going to just design the interface,
but I'm not going to… review the implementation too much," testing and verifying from
outside the boundary. Explicitly not for critical territory ("can't do this with…
finance or whatever"). "I have found this has really saved my brain."

## The bet

A stated convention for where *Kyle's personal* review attention goes: interfaces and
boundary tests always; implementation line-reading only for critical modules. The agent
gates (`adversarial-review`, `gauntlet`) stay whole-diff — this governs the human layer
on top of them, which today has no stated policy and defaults to whole-diff reading or
nothing.

## Decisions / open questions

- **The tension this capture exists to force:** the global git workflow's review gate is
  whole-diff by design. Does a criticality-tiered human layer complement it, or quietly
  erode the "nothing merges unreviewed" guarantee? Needs an explicit call, not drift.
- What marks a module critical — a CLAUDE.md list per repo, path patterns, or judgment
  per PR?
- Kinship with [`deep-modules-for-agent-legibility`](deep-modules-for-agent-legibility.md):
  gray-boxing is only safe where modules are genuinely deep with testable boundaries —
  that capture's convention is this one's precondition.

## Credible first step

Draft the convention text with the criticality question answered for one real repo, and
trial it on a few merges where the agent review came back clean.

## Dependencies

Nothing version-sensitive. Verification at capture (2026-08-21): no capability claims
to check.

## Explicitly out of scope

Weakening the agent-side gates: `adversarial-review` and `gauntlet` remain whole-diff;
this policy never substitutes for them.

## Source segment

> "You can kind of say, 'Okay, I'm going to just design the interface, but I'm not going
> to worry too much or not review the implementation too much.' … in many many modules
> in your app, you don't need to think about the implementation too much as long as you
> have a testable boundary outside the module. … So, that's tip number five. Design the
> interface, delegate the implementation."
