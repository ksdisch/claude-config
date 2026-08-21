# cc-yt-idea-mine — design

**Date:** 2026-08-20 · **Status:** approved by Kyle (interview + design sign-off in session)

A standalone global skill: transcript in → Claude Code artifact proposals out. It
exhaustively scans a video transcript about software engineering / AI / agents and surfaces
every segment that could become something in Kyle's Claude Code setup. It proposes, never
builds.

## Decisions (from the design interview)

| Question | Decision |
|---|---|
| Boundary vs `youtube-breakdown` Mode 4 | Standalone skill. Mode 4 keeps the general "what should I do" lane; this skill only fires on distinctly-shaped asks ("mine this video for Claude Code ideas", `/cc-yt-idea-mine`) and never claims "analyze / break down this video". |
| Implement? | Propose only. Ends with a handoff offer (build in-session, or builder-session prompt per the planner/builder protocol). Never acts on it without a yes. |
| Output | Tiered exhaustive report + `/brainstorm`-style capture gate (vision doc + backlog stub, write-gated). |
| Recall | Everything implementable is captured; top tier gets full treatment, long tail gets one line each in an appendix. |
| Ranking | Grouped by artifact type; leverage-ranked within each group; overall cross-category rank in parens — `1. <idea> (4)` = #1 among its type, #4 overall. Qualitative only, no numeric scoring. |
| Traceability | Short verbatim quote anchor per idea (the transcript .txt carries no timestamps — the converter strips them). |
| Staleness | Report ships unverified with the video's upload date + a caveat; only the ideas Kyle picks at the gate get their capability claims verified (claude-code-guide agent / docs) before landing. |
| Dedup | Full pass against `docs/command-skill-reference.md`; every idea tagged New / Overlaps `<item>` / Already covered by `<item>`. Overlaps stay in the report. |
| Report home | Auto-saved to `~/Learning/youtube-notes/YYYY-MM-DD-<title-slug>-idea-mine.md`, no prompt. |
| Capture home | Fixed: `~/Projects/claude-config` (`BACKLOG.md` stub + `docs/ideas/` vision doc) regardless of cwd. Project-specific picks offered to that project's own backlog if it has one. |
| Artifact scope | Everything: skills, slash commands, subagents, hooks, settings.json, output styles, MCP servers, statusline, keybindings, CLAUDE.md rules / workflow conventions. |
| Name | `cc-yt-idea-mine` (Kyle's pick). |
| Trigger | Auto + typed, narrow trigger phrases; description explicitly leaves youtube-breakdown's phrases alone. |
| Batch | Single video per run. |
| Report save | Automatic — the location was fixed by design, so there is no per-run choice to ask about. |
| Landing | Captured picks land via docs-only branch → PR → merge in claude-config, adversarial-review skip stated (docs-only diff), PR link + SHA reported. |
| Sweep architecture | Pass + completeness critic: one full extraction pass, then an inline second sweep ("what segment did I skip; which in-scope category has zero finds that shouldn't?") before the report renders. No subagent fan-out. |

## Flow

1. **Input** — URL (via `youtube-transcript`; transcript is a scratchpad intermediate; also
   record the upload date), file path, or pasted text. One clarifying question on ambiguous
   input. Transcripts over ~30k words are chunk-swept with a heads-up.
2. **Inventory read** — `~/Projects/claude-config/docs/command-skill-reference.md` for the
   dedup tags. If unreadable, dedup is skipped loudly, never silently.
3. **Extraction pass** — every implementable segment becomes an idea with: title, artifact
   type, what/why, effort band (S/M/L), Global vs Project tag, dedup tag, quote anchor,
   staleness flags (the Claude Code capability claims it depends on).
4. **Completeness critic** — inline second sweep before rendering.
5. **Report** — auto-saved and shown inline (format above).
6. **Capture gate** — pick one / several / all / none; none ends cleanly.
7. **Verify picks** — claims checked; failed claims come back as keep / amend / drop.
8. **Land** — vision doc + backlog stub in claude-config on a fresh branch cut from
   up-to-date main; PR; merge; brief. Project picks offered to their own repo's backlog.
9. **Handoff offer** — build a pick now, or generate a builder-session prompt. Offer only.

## Guardrails

No invention (every idea traces to a quote). Never steal youtube-breakdown's triggers. No
copy-pasteable shell in the skill body — numbered steps + named invariants. Unattended runs
stop after the report; capture is interactive-only. Nothing is written to claude-config
before the gate.

## Meta

Reference-doc row + playbook card under Research & Writing, same commit as the skill.
Playbook run config: inherits the session · `high`. Ships via branch → PR → full
adversarial-review loop (mandatory for `skills/`) → merge.
