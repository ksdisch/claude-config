# Trim-context harness lane: audit and disable unused built-in tools

**Status:** Idea — not committed. Mined from "Claude Code's system tools are SO BLOATED" (https://www.youtube.com/watch?v=oLx4yCbeklQ) by `cc-yt-idea-mine` on 2026-08-22.

## Premise

Matt Pocock cut his per-request system-tool payload from ~25K to ~8K tokens by disabling
built-ins he never used — workflows, remote control, artifacts, connectors, bundled
skills, plan-mode tools. `/trim-context` today audits only the repo side of token bloat
(CLAUDE.md, memory files, `.claude/` cruft); the harness side — which every request in
every session pays for — is invisible to it.

## The bet

A harness-side lane in `/trim-context` that inventories what the harness ships (feature
blocks, tool definitions, bundled skills, connectors), cross-checks it against what this
setup actually uses, and proposes specific `settings.json` disables would find the
single biggest per-request token win available — and would do it with a proposal gate,
since several candidate disables would break live workflows here.

## Decisions / open questions

- Proposal-gated, never auto-applied: `disableWorkflows` would break ultracode
  orchestration, `disableRemoteControl` contradicts `remoteControlAtStartup: true`,
  `disableArtifact` breaks `paper-gloss` — the lane's value is the *diff between
  shipped and used*, and only Kyle can rule on the margins (see
  [`harness-disable-ruling.md`](harness-disable-ruling.md), the one-time manual pass
  this lane would later automate).
- Usage evidence source: transcript sweep (like `/fewer-permission-prompts` does for
  permission rules) vs. asking Kyle per feature. Transcript sweep is the differentiator;
  asking is the fallback.
- Whether the lane belongs inside `/trim-context` or as a sibling command sharing the
  report shape. Inside wins unless the diff gets unwieldy.

## Credible first step

Add a read-only "harness report" section to `/trim-context`'s output: the five
documented disable settings with their current values, plus which tools a bare-name
`permissions.deny` could remove, each annotated with observed usage. Propose-only; no
settings edits in v1.

## Dependencies

- **Verified 2026-08-22** (claude-code-guide agent, current docs): `disableBundledSkills`,
  `disableWorkflows`, `disableRemoteControl`, `disableClaudeAiConnectors`, and
  `disableArtifact` are all documented settings
  (https://code.claude.com/docs/en/settings-reference.md). There is **no general
  `disabledTools` key** and no disable settings for plan-mode tools, AskUserQuestion, or
  cron tools — but a **bare tool name in `permissions.deny` removes that tool's
  definition from the payload** (a scoped rule only blocks the call and leaves the
  definition), per Matt's article
  (https://www.aihero.dev/how-to-kill-the-bloat-in-claude-codes-system-prompt).
- Measurement for before/after numbers: [`system-prompt-inspector.md`](system-prompt-inspector.md).

## Explicitly out of scope

- Actually flipping any disable in this setup — that's
  [`harness-disable-ruling.md`](harness-disable-ruling.md)'s decision pass.
- Repo-side trimming — `/trim-context` already owns it.

## Source segment

> "Fortunately, Claude Code allows you to customize this stuff, so you can actually put
> this in your global settings.json file, and you can disable all sorts of useless
> stuff. … All of that means that I dropped my initial starting system prompt, or the
> system tools, from 25K down to around 8K."
