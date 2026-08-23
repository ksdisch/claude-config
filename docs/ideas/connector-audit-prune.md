# Connector audit: prune unused claude.ai connectors from CLI sessions

**Status:** Executed 2026-08-22 — verdicts recorded below and applied to
`~/.claude/settings.json` (untracked; the repo is public, so the ruling record lives
here and the edit lives only in the live file). Mined from "Claude Code's system tools
are SO BLOATED" (https://www.youtube.com/watch?v=oLx4yCbeklQ) by `cc-yt-idea-mine` on
2026-08-22.

## Verdicts (2026-08-22)

Evidence: full sweep of `~/.claude/projects` (2.6 GB, ~1 year) counting actual
`mcp__claude_ai_*` tool invocations. Mechanism question resolved: `deniedMcpServers`
is a valid **user-scope** settings key (documented as enterprise but merges from all
sources, so users can deny for themselves) — the prune is one edit in
`~/.claude/settings.json`, no per-project toggles needed. Entries are
`{ "serverName": "claude.ai <Name>" }`; note `claude.ai O’Reilly` uses a Unicode
apostrophe (U+2019).

**Cut (13):** Asana, Figma, Supabase, IFTTT, Elicit, AWS Marketplace, Canva, O’Reilly,
Spotify, ZipRecruiter (all zero CLI invocations ever) · Todoist (~47 tools duplicating
the self-hosted `todoist` MCP: ×68 vs ×125, self-hosted kept) · Context7 (duplicates
the context7 plugin's identical 2 tools) · Notion (×1 ever, 2026-06-05).

**Keep (5):** Gmail (×116, last 2026-08-22) · Slack (×7, 2026-08-19) · Google Drive
(×25, 2026-07-21) · Google Calendar (×28, stale since 2026-06-08 — Kyle explicitly
kept) · Wispr Flow (zero CLI use, but Kyle explicitly spared it).

Corrections to the original premise: Supabase and Wispr Flow were assumed CLI-used but
show zero CLI invocations — their use was claude.ai web, which these settings don't
touch. Two connectors not in the original list exist on the account (Zapier, Clinical
Trials — zero use, didn't attach recently); not ruled on, not denied. `claude.ai
Claude Code Remote` is the remote-control bridge and must never be denied.

## Premise

Matt Pocock: "Disabled Claude AI connectors, which were burning a ton of tokens I didn't
even realize." This setup carries roughly fifteen connectors' worth of tool surface into
every CLI session — Asana, Canva, Figma, Gmail, Calendar, Drive, IFTTT, Notion,
O'Reilly, Slack, Spotify, Supabase, Todoist, Wispr Flow, ZipRecruiter, AWS Marketplace —
and several have no plausible CLI use. Deferred-tool loading shrinks the cost, but the
roster itself still ships with every request.

## The bet

An hour of audit — which connectors have ever been used from Claude Code — followed by
per-connector pruning recovers tokens on every future request of every session, for a
one-time S-sized effort. The cleanest kind of win: no new artifact to maintain.

## Decisions / open questions

- The blunt global switch is wrong here: `disableClaudeAiConnectors` uses
  any-source-true semantics — one `true` turns connectors off everywhere, and some
  (Todoist, Gmail, Slack, Supabase, Wispr Flow) ARE used from the CLI. The per-connector
  mechanisms are the fit.
- Which mechanism per verdict: `/mcp` panel toggles write `disabledMcpServers`
  **per-project** in `~/.claude.json`; `deniedMcpServers` (e.g. `"claude.ai
  ZipRecruiter"`) blocks by name. Is there a user-scope (all-projects) form of the
  per-connector toggle? Determines whether pruning is one edit or per-project.
- Evidence bar for "unused": transcript sweep vs. Kyle's say-so. A wrong prune is
  trivially reversible, so say-so is probably enough.

## Credible first step

List every `mcp__claude_ai_*` prefix visible in a fresh session, grep recent transcripts
for actual invocations, and present the used/unused split with the recommended
per-connector action for each.

## Dependencies

- **Verified 2026-08-22** (claude-code-guide agent, current docs): connectors attach to
  CLI sessions as auto-loaded MCP servers; **per-surface (CLI-only) disable does not
  exist** for the global setting, but per-connector control does — `/mcp` panel toggles
  (`disabledMcpServers`, per-project), `deniedMcpServers` blocklist, or
  `ENABLE_CLAUDEAI_MCP_SERVERS=false` env var
  (https://code.claude.com/docs/en/mcp.md#disable-claude-ai-connectors). Claude Code
  web/cloud sessions ignore these settings (connectors provisioned remotely).

## Explicitly out of scope

- Disconnecting connectors at the claude.ai account level — that changes web behavior
  too and is Kyle's call outside this repo.
- The self-hosted MCP servers in `~/.claude.json` (`kapture`, `MCP_DOCKER`,
  `notebooklm-mcp`, `todoist`, `basic-memory`) — different mechanism, and mostly in
  active use; audit separately if ever.

## Source segment

> "Disabled Claude AI connectors, which were burning a ton of tokens I didn't even
> realize."
