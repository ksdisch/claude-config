# Tickets: retire-skill

Generated index — resolves to the issue files below. Source of truth is `issues/`; refresh on publish, on a /triage Status change, or once after each merge in /implement-spec.

| # | Title | Summary | Status | Blocked by |
|---|---|---|---|---|
| [01](issues/01-tracer-inventory-cli-skills.md) | Tracer: the inventory CLI over a fixture, tracked skills only | Script runs end to end on a fixture: tracked skills, typed usage, new/temperature, outputs, exit codes, tests | done | None (can start immediately) |
| [02](issues/02-session-chosen-usage-transcripts-cache.md) | Session-chosen usage from transcripts, with the per-file cache | Skill rows gain auto counts from Skill tool calls, the typed/auto split, auto_only, and a size+mtime cache | done | 01 |
| [03](issues/03-config-repo-surfaces.md) | The rest of the config repo: CLAUDE.md sections, constraints paragraphs, commands, agents, output styles, untracked skills | Every config-repo surface enumerated with bytes, added dates, paused/unlinked flags, and trigger hits from the sidecar | done | 01 |
| [04](issues/04-claude-home-surfaces.md) | The Claude home: plugins, MCP servers, hooks, memory dirs | Plugins with duplicate detection, MCP from config ∪ transcripts, hooks, memory dirs, agent dispatches counted | ready-for-agent | 02, 03 |
| [05](issues/05-referrers-mentions-dangling-vendored-ledger.md) | Referrers, mentions, dangling routes, vendored copies, ledger read-back | Referrers vs mentions with exclusions, dangling flag, vendored repo names, kept flag, last-edited, real cool temperature | ready-for-agent | 03, 04 |
| [06](issues/06-precedence-collapse-oversized-redaction.md) | The full precedence table, collapsed rows, oversized, redaction proven | Script-computed proposed on every surface, collapsed classes, omitted summary, totals table, redaction tests | ready-for-agent | 05 |
| [07](issues/07-ledger-pointer-first-live-report.md) | Ledger seeded, reference pointer, first live redacted report | The ledger exists, the index intro points at it, and a real --report run is committed with sanity checks passed | ready-for-agent | 06 |
| [08](issues/08-the-skill-procedure-and-docs.md) | The skill: procedure, bookkeeping reference, index row, playbook card | SKILL.md and the per-surface bookkeeping reference written per the spec, with row and card in the same commit | ready-for-agent | 06 |
| [09](issues/09-pilot-sweep.md) | Pilot sweep (PR B) | The first live sweep: ratification with Kyle, apply, measure, ledger, review-scope proposal | ready-for-human | 07, 08, and PR A merged |
| [10](issues/10-backlog-and-idea-doc-bookkeeping.md) | Backlog and idea-doc bookkeeping | Three v2 stubs in the backlog; coliseum marked built; minimal-initial-prompt marked absorbed | ready-for-agent | 08 |
