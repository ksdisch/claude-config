# OPUS 5 BUILDER NOTES

Rules for any prompt that an **Opus 5** session will consume. Consumed by
the prompt generators when their model recommendation is Opus 5 —
`commands/handoff.md`, `commands/prompt-optimize.md`, and the starter
prompts of `skills/ship-and-route` and `skills/backlog-hygiene` — not loaded
into sessions directly. `/claudify-repo` vendors this file into repos as
`.claude/opus5-builder-notes.md`; consumers prefer that repo-local copy over
`~/.claude/opus5-builder-notes.md` so cloud sessions resolve it too.
Distilled from Anthropic's [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)
guide; the rationale for adopting only this slice is recorded in
[PR #69](https://github.com/ksdisch/claude-config/pull/69).

1. **Complete spec up front, then hands off.** Opus 5 performs best given the
   full task specification and left to run — it finishes tasks rather than
   leaving stubs. Front-load acceptance criteria, scope boundaries, and
   done-bars in one place; don't structure the prompt around mid-task
   check-ins it doesn't need.
2. **No verification boilerplate.** Opus 5 verifies and self-corrects without
   being told to; blanket instructions compound with that behavior and burn
   tokens with no quality gain. Never emit "double-check your work,"
   "re-verify before responding," "add a final verification step," or "use a
   subagent to verify." Targeted gates tied to a named artifact remain fine
   ("run the test suite and paste the output before claiming done"), and
   verification votes inside an explicit multi-agent orchestration sketch
   are the design, not boilerplate.
3. **Cap delegation** — only for surfaces that have subagents (Claude
   Code); skip the line entirely for claude.ai chat, Cowork, or any other
   surface without delegation. Opus 5 spawns subagents more readily than
   prior models. Include one line like: *"Delegate to a subagent only for
   large, genuinely independent, parallelizable tracks. Don't delegate work
   you can finish yourself in a handful of tool calls, and don't use ad-hoc
   subagents to verify your own work — a pre-merge review loop the project
   requires is exempt and still runs."* Exception: when the prompt's own
   shape delegates — a multi-agent/ultracode orchestration sketch, a batch
   of per-unit subagents, a single orchestrator dispatching subagents, or a
   fan-out research/verification design — omit the cap line entirely; the
   prompt's delegation design governs, verification votes included.
4. **Calibrate written deliverables.** Files Opus 5 writes to disk run long.
   If the session will author documents, include: *"Match document length to
   what the task needs — cover the substance; no filler sections, redundant
   summaries, or boilerplate."*
5. **Review prompts must not suppress findings.** Opus 5 follows "only
   report high-severity issues" / "be conservative" literally and
   under-reports. If the prompt asks for review or bug-finding, ask for
   everything found and filter by severity in a separate pass.
