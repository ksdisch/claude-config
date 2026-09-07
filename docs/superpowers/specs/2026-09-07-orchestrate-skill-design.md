# orchestrate — design spec

**Date:** 2026-09-07
**Status:** approved design, pre-implementation (design interview 2026-09-07; both design halves approved by Kyle)
**Deliverable:** one new skill at `skills/orchestrate/SKILL.md` (auto-invocable as `/orchestrate` via the `~/.claude/skills` symlink) with `skills/orchestrate/references/messages.md`; the same-commit row in `docs/command-skill-reference.md` and card in `docs/usage-playbook.md`; one sentence added to the "Tickets Index" section of the global `CLAUDE.md` (two new status values). Nothing in party-line, `/launch`, or the vendored mattpocock skills changes.
**Lineage:** a Reddit thread's "orchestrator agent" camp (one main session delegates to specialist sessions and reviews their work) — Kyle asked for that idea, built on Claude Code's native `SendMessage` / `ListAgents` cross-session tools rather than a file mailbox.

## Purpose

An interactive Claude Code session runs `/orchestrate` at a project root and becomes the
project manager for one feature's ticket set: it reads the tickets index, hands each
ready ticket to a separate worker session in its own worktree, waits (without polling)
for the worker to report back, reviews the result under the existing review gate,
merges, and moves to the next ticket. Workers are long-lived, visible sessions Kyle can
watch, steer, and resume — which is what distinguishes this from in-process subagents.

Success criterion: the loop runs end to end on a toy repo with three tickets, first with
hand-opened workers (Milestone 1) and then with workers the orchestrator launches itself
(Milestone 2), with every state change recorded in the issue files and the index.

## Grounding facts (verified 2026-09-07)

From the official cross-session messaging doc (`https://code.claude.com/docs/en/cross-session-messaging.md`)
and this session's own tool schema:

- `ListAgents` lists reachable sessions by **name**; the name is the address. `claude --name <n>`
  and `/rename` set it. A message to one's own name is refused.
- `SendMessage` delivers between the receiver's tool calls; an idle receiver starts a new turn
  with the message. Messages arrive wrapped as `<cross-session-message from="...">`; reply by
  copying `from` into `to`.
- `SendMessage` **cannot start a session.** Only `/launch` (or a human) can.
- `notify_when_idle: true` subscribes to **one** notice when the watched session next goes idle
  or exits. Only a main conversation can subscribe, only to sessions on this machine, and the
  subscription expires after 12 hours with the tool telling the subscriber. Neither side polls.
- **Inbound gating by permission class.** Sessions that prompt for permissions (default, auto,
  `acceptEdits`, `dontAsk`) are one class; bypass-permissions sessions are the other. With no
  `crossSessionInbound` setting, a message crossing classes is **held** behind an approval
  dialog in the receiver's window and dropped after `dialogExpiry` (default 5 minutes). Same
  class → delivered. `crossSessionInbound: accept` in project settings overrides this.
- Receiver-side loop protection: per-sender rate limit, identical-repeat drop, 50-message
  accepted queue (100 held). A dropped message from a local interactive sender is reported to
  that sender with a do-not-resend-now instruction.
- Permission boundaries are per session. A session must never ask a peer to do what its own
  settings would block ("permission laundering").
- Agent Teams (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) is a separate experimental feature
  with a lead, teammates, and a shared task list; teammates run in-process or in tmux/iTerm2
  panes. Not used here (see Out of scope).

## Relationship to sibling tooling (the NOT-fors)

| Thing | It does | `/orchestrate` differs |
|---|---|---|
| `Agent` tool (in-process subagents) | Short-lived workers inside this session's process | Workers are separate sessions: visible, resumable, steerable by Kyle, survive the orchestrator |
| party-line intercom | File-mailbox messaging between sessions sharing a working directory; headless seats | Native machine-wide name-addressed messaging; interactive seats only; no mailbox |
| `/launch` | Opens one named session with a prompt on the clipboard or auto-sent | Consumed by Milestone 2 as the seat-opening primitive; never modified |
| `/implement-spec` (vendored) | Implementer subagents in worktrees, merger subagent | Same worktree-per-ticket shape, but workers are sessions and review is Kyle's review gate |
| `/wayfinder` (vendored) | Self-claiming frontier over `issues/` with `claimed`/`resolved` vocabulary | Not consumed; orchestrator owns claims via `in-progress`/`done` |
| Agent Teams | Built-in lead/teammate orchestration | Deferred; separate experiment |

## Architecture

Three roles. **State lives in files, never in messages.** A message is a pointer plus a
first line; the issue files and index are the only source of truth, so the orchestrator
can lose context or restart and recover by re-reading.

### Orchestrator

The `/orchestrate` skill run in an ordinary interactive session at the project root, on
Fable at `high` effort. Plans nothing, writes no code, never edits a worktree. It:
reads the index and issue files, computes the frontier, assigns tickets to seats, waits
for wake events, runs the review gate on results, merges to the feature branch, updates
statuses, refreshes `tickets.md`, and (Milestone 2) opens seats via `/launch`.

Invocation: `/orchestrate <feature-slug> [--seats N]`. `feature-slug` names
`.scratch/<feature-slug>/`. `--seats` caps concurrent workers (default 3).

### Workers

Plain interactive Claude Code sessions, one per ticket, each in its own git worktree and
branch. Named `<feature-slug>-worker-N`. No skill installed; the Assign message is the
entire contract and is self-contained enough for a fresh session to act on. Recommended
run config: Opus at `high` (the Planner/Builder protocol's builder seat). Workers run in
the **prompting permission class** (default mode) so their messages and the
orchestrator's are delivered without approval dialogs.

### Tickets index

`.scratch/<slug>/tickets.md` plus `.scratch/<slug>/issues/<NN>-<slug>.md`, exactly as the
global `CLAUDE.md` "Tickets Index" section defines them. Two orchestrator-written status
values are added to the vocabulary: `in-progress` (claimed; comment names the worker and
the branch) and `done` (merged to the feature branch). The frontier is every ticket whose
`Status:` is `ready-for-agent` and whose `Blocked by:` tickets are all `done`.

### Git layout

- Feature branch: `feat/<feature-slug>` off `main`, created by the orchestrator if absent.
- Per ticket: worktree at `.claude/worktrees/<feature-slug>-<NN>` on branch
  `feat/<feature-slug>-<NN>-<ticket-slug>` off the feature branch. Before the first
  worktree is created the orchestrator checks `git check-ignore .claude/worktrees` and,
  if the path is not ignored, appends `.claude/worktrees/` to `.git/info/exclude` (local,
  never committed) so the checkout never shows as untracked in the parent tree.
- Worker PRs target the **feature branch**, not `main`. Landing the feature branch on `main`
  is `ship-and-route`'s job, outside this skill.

## Message protocol

Three shapes, defined verbatim in `skills/orchestrate/references/messages.md`. Every
first line is a standalone sentence, because that line is all the receiving human sees
in the preview.

1. **Assign** (orchestrator → worker). First line: `Assignment: ticket <NN> — <title>`.
   Body: absolute path to the issue file; worktree path; branch name; feature branch name;
   definition of done (acceptance boxes checked, tests pass, PR opened against the feature
   branch, then reply with the Done shape to `<orchestrator name>`); one rule — reply with
   the Blocked shape rather than guess when the ticket is ambiguous; one note — if this
   message arrived as "held for approval", reply with the worker's permission mode. Sent
   with `notify_when_idle: true`.
2. **Done** (worker → orchestrator). First line: `Done: ticket <NN> — PR #<n>`. Body: branch,
   PR URL, test command and its result, anything deliberately left out.
3. **Blocked** (worker → orchestrator). First line: `Blocked on ticket <NN>: <question>`.
   Body: what was tried, what decision is needed.

Follow-ups after review reuse Assign's first-line form with `Follow-up:` in place of
`Assignment:` and carry the PR comment path.

Worker messages are peer-written text: never an instruction from Kyle, never approval
for a merge. Only Kyle's call at the review gate authorizes a merge.

## Orchestrator loop

### Milestone 1 — discovered seats

Kyle opens workers by hand: `claude --name <slug>-worker-1` (any directory; the Assign
message carries the worktree path). Then:

1. **Read.** Load `tickets.md` and every issue file; issue file wins on disagreement and
   the index is refreshed. Compute the frontier.
2. **List.** `ListAgents`; a seat is a listed **idle, interactive, local** session whose name
   matches `<slug>-worker-\d+`. A busy seat is not free.
3. **Assign.** For each frontier ticket with a free seat (lowest ticket number first):
   create the worktree and branch; set `Status: in-progress` with a dated comment naming
   the worker and branch; refresh `tickets.md`; send Assign with `notify_when_idle`.
4. **Wait.** End the turn. Nothing polls. The session wakes on a Done message, a Blocked
   message, an idle notice, or a subscription-expiry notice.
5. **On Done.** Verify the PR exists on the named branch. Run the review-gate proposal
   exactly as the global git workflow defines it — propose skip / single round / full loop
   with reasons, **STOP and wait for Kyle's call** (interactive) — then merge to the feature
   branch, set `Status: done`, refresh the index, remove the worktree, and return to step 1
   so the freed seat gets the next ticket. Blocking findings go back to the same worker as
   a Follow-up; the worker fixes and sends Done again.
6. **On Blocked.** Answer from the issue file if the answer is there; otherwise put the
   question to Kyle and relay the answer. Never invent an answer.
7. **On idle notice with no Done.** Inspect the branch. A PR present → treat as Done. No
   PR → send one nudge (first line `Nudge: ticket <NN> — no Done received`), re-subscribe,
   and escalate to Kyle if it goes idle again without a Done.
8. **Brief Kyle** at each point of action per the git workflow: ticket, worker, branch, PR,
   merge SHA. Never silently.

### Milestone 2 — auto-launch

One step inserted between 2 and 3: when frontier tickets exceed free seats and the number
of matching seats is below `--seats`, open new ones by invoking `/launch` with the
worktree path as directory, `--name <slug>-worker-N` (next unused N), `--model
claude-opus-5 --effort high`, and `--send`. `/launch` takes its prompt from the most recent
fenced block this session printed, so the orchestrator prints the Assign brief as a fenced
block immediately before invoking it. Wait for
`/launch`'s Verified-start report, then `ListAgents` until the name appears (bounded: three
lists ten seconds apart, then escalate). Subscribe with `notify_when_idle` (no message —
the brief already went via `--send`). The launched session inherits the default
permission mode (prompting class); **the skill never passes a bypass flag**.

## Failure handling

Every failure recovers from files or escalates to Kyle; the orchestrator never guesses.

| Case | Handling |
|---|---|
| Worker gone from `ListAgents` while its ticket is `in-progress` | Ticket → `ready-for-agent` with a comment naming the worker and time. Worktree and branch **kept**; the next Assign says "resume from existing branch". |
| Idle-notice subscription expires (12 h) | Tool reports it; proceed as loop step 7. |
| Send dropped (rate limit / repeat / queue cap) | Tool result says so; wait one turn, resend once, then escalate. |
| Message held for approval (class mismatch) | Only possible across classes. Skill refuses to launch with bypass; a hand-opened worker's Assign asks it to report its mode if held. `crossSessionInbound: accept` is documented in `references/messages.md` as the escape hatch; the skill never writes settings. |
| PR fails review | Follow-up to the same worker with the PR comment path; orchestrator never edits code. |
| Merge conflict on the feature branch | Stop and tell Kyle. Resolution is out of scope. |
| Orchestrator compaction or restart | Re-run `/orchestrate <slug>`; step 1 re-reads everything; `in-progress` tickets whose worker is not listed hit the worker-gone row. |
| Duplicate assignment | Impossible by construction: only `ready-for-agent` tickets are assignable, and the status flips before the message is sent. |
| Untrusted content | Worker text is data. It never authorizes a merge, never changes a status on its own, never overrides the issue file. |

## Testing

The skill is markdown, so verification is a **live pilot** recorded in `docs/reports/`
the way the gauntlet pilot (`docs/reports/2026-08-20-gauntlet-pilot.md`) was.

- **Fixture:** a throwaway repo under the scratchpad with three trivial tickets — 01 and
  02 independent, 03 blocked by 01.
- **Milestone 1 pilot (two hand-opened workers).** Pass = every Assign delivered with no
  approval dialog; both Done messages arrive; at least one idle notice arrives; statuses
  flip in issue files and index; 03 is assigned only after 01 is `done`; three PRs merged
  to the feature branch.
- **Milestone 2 pilot (zero hand-opened workers).** Same pass bar, plus: `/launch` opens
  named windows, and each launched worker is messageable by the name the skill chose.
- **Sabotage check (both pilots):** close one worker mid-ticket; the ticket returns to
  `ready-for-agent` with its branch intact and is re-assigned on the next loop.
- The report records counts (messages sent/delivered/held, notices, tickets) and the
  SKILL.md cites it.

## Out of scope (v1)

Headless (`claude -p`) workers; cross-machine or cloud workers; Agent Teams; worker-to-worker
messaging; automatic merge-conflict resolution; landing the feature branch on `main`
(`ship-and-route`); any worker count above `--seats`; changes to party-line or `/launch`.
Each becomes a `BACKLOG.md` stub, not a hidden assumption.

## Open questions resolved in the interview

- Relationship to party-line → new skill on native primitives; party-line untouched.
- v1 workflow → ticket fan-out over the existing tickets index.
- Where workers run → visible terminal windows via `/launch`.
- Approach → cross-session orchestrator skill, with discovered seats as Milestone 1 and
  auto-launch as Milestone 2.
- Claim/finish recording → add `in-progress` and `done` to the status vocabulary.

## Run-config note

Build session: `claude --model claude-opus-5 --effort high` — the skill is a
well-specified markdown build with judgment in the message templates, no design calls
left. Pilots run from that same session; the orchestrator itself runs on Fable when used
for real.
