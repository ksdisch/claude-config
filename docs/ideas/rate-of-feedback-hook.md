# Rate-of-feedback hook: fast typecheck feedback after edit bursts

**Status:** Idea — not committed. Mined from ""Software Fundamentals Matter More Than Ever" — Matt Pocock" (https://www.youtube.com/watch?v=v4F1gFy-hqg) by `cc-yt-idea-mine` on 2026-08-21.

## Premise

Pocock's diagnosis of the "it built the right thing but it doesn't work" failure mode:
even with feedback loops available, the model "does way too much at once" — a huge burst
of code, then a late typecheck. The Pragmatic Programmer calls it outrunning your
headlights: "the rate of feedback is your speed limit."

## The bet

A PostToolUse hook (matcher: Edit/Write) that runs the cheapest available check —
`tsc --noEmit` scoped to touched files, or the project's fastest linter — and feeds
failures straight back into the transcript shortens the loop without prompt text.
Feedback-only is exactly the right posture here (the hook informs, never gates), and it
honors the standing hooks-over-prompts lesson: "take small steps" as prose is precisely
the must-happen behavior that belongs in a hook.

## Decisions / open questions

- Per-project check detection: how the hook finds the right command (tsconfig presence,
  a `.claude/` config key, or a settings.json env var) and what it does in repos with no
  cheap check (silence, not noise).
- Debounce: per-edit runs could thrash on multi-file bursts; batching by turn or by a
  short window may be needed.
- Global default vs. opt-in per repo.

## Credible first step

A minimal version for one TypeScript repo: PostToolUse → `tsc --noEmit` filtered to the
edited file's project, output truncated to the first N errors.

## Dependencies

PostToolUse hook event — **feedback-only; cannot gate** (verified 2026-08-20 against
code.claude.com/docs/en/hooks.md, reconfirmed as the standing fact for this capture).
That constraint is a feature for this idea, not a limitation.

## Explicitly out of scope

Gating/blocking on failures (PostToolUse can't, and the idea doesn't want to), and
full-suite test runs (this is the fast loop; suites stay with `/tdd`, `gauntlet`, and CI).

## Source segment

> "This in the Pragmatic Programmer they describe as outrunning your headlights. It's
> essentially driving too fast because the rate of feedback is your speed limit. …which
> means that you should be testing as you go, taking small deliberate steps. And the AI
> by default is really not very good at that."
