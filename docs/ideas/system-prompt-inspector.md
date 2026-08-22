# System-prompt inspector: measure what actually ships over the wire

**Status:** Idea — not committed. Mined from "Claude Code's system tools are SO BLOATED" (https://www.youtube.com/watch?v=oLx4yCbeklQ) by `cc-yt-idea-mine` on 2026-08-22.

## Premise

Matt Pocock: "you can use a proxy to see what you're actually shipping, which is really,
really useful." Every trimming decision — feature disables, connector prunes, repo-side
`/trim-context` fixes — is guesswork without a wire-level measurement, and the built-in
`/context` grid is a visual summary, not the actual request payload.

## The bet

A documented, repeatable measure-before/measure-after workflow (Matt's zero-dependency
`agent-proxy`, or `/context` where it suffices) turns token trimming from folklore into
a number: "25K → 8K" is both the motivation and the acceptance test for every other
trimming idea in this lineage.

## Decisions / open questions

- Form: a short doc in `docs/` vs. a tiny skill ("measure session overhead") that runs
  the proxy, captures one request, and reports the ranked tool table. Doc first; skill
  only if the doc gets followed more than twice.
- When `/context`'s per-item grid is enough vs. when the proxy is warranted (the proxy
  shows the *actual payload*, ranked per tool — `/context` may not itemize tool
  definitions).
- Trust boundary: the proxy sits between Claude Code and the Anthropic API — vendor
  Matt's gist into the repo (pinned, read before running) rather than curl-piping it.

## Credible first step

Run `/context` in a fresh session and save the breakdown; then run one session behind
Matt's `agent-proxy` gist and diff what each reveals. The comparison decides whether the
doc says "use /context" or "use the proxy".

## Dependencies

- **Verified 2026-08-22** (claude-code-guide agent, current docs): `/context` shows a
  colored grid with a per-item breakdown (https://code.claude.com/docs/en/commands.md),
  but the proxy remains the way to see the actual request payload. Matt's tooling is
  real and current: the `agent-proxy` gist
  (https://gist.github.com/mattpocock/5b3d76ea21f5f698aefded47a9cea3b1) and the article
  (https://www.aihero.dev/how-to-kill-the-bloat-in-claude-codes-system-prompt).

## Explicitly out of scope

- Acting on the measurements — that's [`trim-context-harness-lane.md`](trim-context-harness-lane.md)
  and [`harness-disable-ruling.md`](harness-disable-ruling.md).
- Any always-on proxy: this is a diagnostic you run deliberately, not infrastructure.

## Source segment

> "I put this in an article so that you can use a proxy to see what you're actually
> shipping, which is really, really useful. Then, you can tune the settings to choose
> just the bits of the system prompt that you need."
