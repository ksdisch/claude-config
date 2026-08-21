---
name: wayfinder
description: Plan an effort too big for one agent session as a shared map of decision tickets on the repo's issue tracker, then resolve them one at a time until the way to the destination is clear. Typed-only entry point (`/wayfinder`) — invoke with a loose idea to chart a new map, or with a map's URL/number to work the next ticket on an existing one. NOT for: a plan you can settle in one sitting (use grilling or /grill-me), a brand-new idea that needs discovery and a scaffolded repo (use kickoff), choosing what to do next from a stocked backlog (use backlog-hygiene), or building anything — a cleared map hands off to a spec, never to a pull request.
disable-model-invocation: true
argument-hint: "A loose idea to chart, or an existing map's URL/number"
---

A loose idea has arrived, too big for one agent session, and wrapped in fog: the way from here to the **destination** isn't visible yet. Wayfinding is about finding that way, not charging at the destination. This skill charts the way as a **shared map** on the repo's issue tracker, then works its **decision tickets** — questions whose resolution is a decision, not slices of a build to execute — one at a time until the route is clear.

The destination varies per effort, and naming it is the first act of charting: it shapes every ticket. It might be a spec to hand off and iterate on, a decision to lock before planning starts, or a change made in place like a data-structure migration. The map is domain-agnostic: engineering work, course content, whatever fits the shape.

**Is this the right tool?** The test is **session count, not project size**. If the whole thing fits in one conversation, `grilling` is cheaper and better and wayfinder is genuinely slower for that case. Reach for a map only when the effort is larger than one session can hold *and* the route is foggy. Greenfield isn't required — wayfinder is often sharper on a half-built codebase, where much of the fog is "what is already true here" rather than "what should we do".

## Plan, don't do

Wayfinder is **planning**. Each ticket resolves a decision, and the map is done when the way is clear, with nothing left to decide before someone goes and does the thing. The pull to just do the work is usually the signal you've reached the edge of the map and it's time to hand off. Produce decisions, not deliverables.

**Invariant `no-self-licence`:** the map's own **Notes** cannot grant an execution licence. An effort *may* legitimately carry execution into the map, but only Kyle can decide that, and only in the message that invokes the session — not in a file the agent itself writes and reads back later. This is the hole this skill is most often reported falling through: an agent writes "this map carries execution" into its own Notes, then reads it in a later session as its own permission and starts building. So:

- Notes may **record** that Kyle granted execution, naming when. That record is evidence, not authority.
- If a Notes block claims execution and the invoking message didn't, **ask before doing anything that isn't a decision**. Unattended, treat it as absent.
- Never write an execution licence into Notes on your own initiative.

**Invariant `task-is-not-a-slice`:** any `wayfinder:task` ticket that reads like a piece of the build is mis-typed. Re-type it or rule it out of scope; don't execute it.

## Refer by name

Every map and ticket is an issue, so it has a **name**: its title. In everything Kyle reads — narration, the map's Decisions-so-far — refer to it by that name, never by a bare id, number, or slug. A wall of `#42, #43, #44` is illegible; names read at a glance. The id and URL don't vanish; a name wraps its link, but they ride *inside* the name, never stand in for it.

This is the same rule as **Never show me a bare identifier** in `~/.claude/CLAUDE.md`, and its third part applies here too: once per response that references tickets, say where the full map lives and give a copy-pasteable way to open it — the issue URL, or the `code <path>` line for a local map.

## The Map

The map is a single issue labelled `wayfinder:map` (or a single `map.md`), the canonical artifact. Its tickets are its children. **Where the map, its children, blocking, and frontier queries physically live is backend-specific — see [tracker.md](tracker.md)**, which covers GitHub Issues and the local-markdown fallback, and how to choose.

The map is an **index**, not a store. It lists the decisions made and points at the tickets that hold their detail; a decision lives in exactly one place — its ticket — so the map never restates it, only gists it and links. That is what lets a map keep growing without every session paying for its whole history.

### The map body

The whole map at low resolution, loaded once per session. Open tickets are **not** listed: they are open children, found by query.

```markdown
## Destination

<what reaching the end of this map looks like: the spec, decision, or change this effort is finding its way to. One or two lines; every session orients to it before choosing a ticket.>

## Notes

<domain; skills every session should consult; standing preferences for this effort; which tracker backend this map uses>

## Decisions so far

<!-- the index: one line per closed ticket, enough to judge relevance, then zoom the link for the detail the ticket holds -->

- [<closed ticket title>](link): <one-line gist of the answer>

## Not yet specified

<!-- see "Fog of war": in-scope fog you can't ticket yet; graduates as the frontier advances -->

## Out of scope

<!-- see "Out of scope": work ruled beyond the destination; closed, never graduates -->
```

### Tickets

Each ticket is a **child** of the map; the tracker's id is its identity. Its body is the question, sized to one agent session:

```markdown
## Question

<the decision or investigation this ticket resolves>
```

Each ticket carries a `wayfinder:<type>` label, one of `research`, `prototype`, `grilling`, `task`.

A session **claims** a ticket before any work, so concurrent sessions skip it (invariant `claim-first` in tracker.md). Claiming never resolves a ticket — open-or-resolved and claimed-or-not are two independent axes, whichever backend is in play (`status-and-claim-are-independent`). A ticket is **unblocked** when every ticket blocking it is closed or out of scope (`out-of-scope-unblocks`); the **frontier** is the open, unblocked, unclaimed children — the edge of the known.

The answer isn't part of the body; it's recorded on resolution. Assets created while resolving a ticket are linked from the ticket, not pasted into it.

## Ticket Types

Every ticket is either **HITL** (human in the loop, worked *with* a human who speaks for themselves) or **AFK**, driven by the agent alone.

**Invariant `hitl-needs-a-human`:** a HITL ticket resolves only through that live exchange. The agent never stands in for Kyle's side of it. A grilling agent that answers its own questions, or a prototype agent that builds three variants and picks one, has broken this and the ticket is not resolved — regardless of how good the answer looks.

| Type | Mode | Reach for it when | Resolved by |
|---|---|---|---|
| `grilling` | HITL | The default. The question can be settled by talking it through. | Call the Skill tool twice — `grilling` and `domain-modeling` — in a fresh session |
| `prototype` | HITL | "How should this look" or "how should this behave" — a question talking cannot settle. | Call the Skill tool with `prototype`; link the artifact from the ticket as an asset |
| `research` | AFK | A fact outside the working directory is blocking a decision. | A subagent that calls the Skill tool with `research` and **investigates only**, returning its findings; the dispatching session resolves the ticket and commits (invariant `subagents-investigate-only`) |
| `task` | Either | Nothing to decide, but manual work blocks a decision — provisioning access, signing up for a service so its API can be judged, moving data so its shape can be seen. | The agent alone where it can (AFK); otherwise a precise checklist for Kyle (HITL) |

`task` is the one type that *does* rather than decides, and it earns its place by unblocking a decision, never by delivering a piece of the destination (invariant `task-is-not-a-slice`). Resolve it by recording what was done plus any facts later tickets depend on — where credentials live, new URLs, row counts.

**Prototype aggressively.** Wayfinder is prototypemaxxing, not planmaxxing: the reason a route stays current is that uncertainty gets flushed out by cheap concrete artifacts before anything depends on it. When a question could plausibly be a `grilling` or a `prototype`, prefer `prototype`.

## Fog of war

The map is *deliberately* incomplete: don't chart what you can't yet see. Beyond the live tickets lies the **fog of war** — the dim view of decisions and investigations you can tell are coming but can't yet pin down, because they hang on questions still open. Resolving a ticket clears the fog ahead of it, graduating whatever's now specifiable into fresh tickets, one at a time, until the way to the destination is clear and no tickets remain.

The map's **Not yet specified** section is where that dim view is written down: the suspected question, the area to revisit later. It's the undiscovered frontier *toward* the destination — everything here is in scope, just not sharp enough to ticket.

**Fog or ticket?** The test is whether you can state the question precisely *now*, not whether you can answer it now.

- **Ticket when** the question is already sharp, even if it's blocked and you can't act on it yet.
- **Not yet specified when** you can't yet phrase it that sharply. Don't pre-slice the fog into ticket-sized pieces: it's coarser than a ticket, and one patch may graduate into several tickets, or none, once the frontier reaches it.

**Not yet specified** excludes what's already decided, what's already a live ticket, and what's out of scope.

**Invariant `fog-shrinks`:** a patch of fog that graduates into a ticket is deleted from **Not yet specified** in the same edit. Living in both places is how a map starts lying about what's left.

## Out of scope

Fog only ever gathers *toward* the destination. The destination fixes the scope, so work beyond it is **out of scope**: it isn't fog, and it doesn't belong in Not yet specified. Scope, not sharpness, lands it there. Out-of-scope work never graduates, so it returns only if the destination is redrawn — and then as a fresh effort, not a resumption.

When a ticket that already exists turns out to sit past the destination, **close it** (a closed ticket is unambiguously off the frontier) and leave one line in **Out of scope**: the gist plus why, linking the closed ticket. It stays out of Decisions-so-far, which records the route actually walked; a scope boundary isn't a step on it.

## Invocation

Two modes. Either way, **never resolve more than one ticket per session** — `research` is the sole exception, since none of those costs Kyle a conversation.

### Chart the map

Kyle invokes with a loose idea.

1. **Name the destination.** Call the Skill tool twice — `grilling` and `domain-modeling` — to pin down what this map is finding its way to. The destination fixes the scope, so it's settled first. **Scope it to one bounded destination**, not to a whole product: a map scoped to "implement V1" is the waterfall trap this skill gets accused of, where the thirteenth ticket invalidates the assumptions the first twelve rested on.
2. **Map the frontier.** Grill again, **breadth-first** this time: fan out across the whole space rather than deep on any one thread, surfacing the open decisions and the first steps takeable now. **If this surfaces no fog** — the way is already clear, the whole journey small enough for one session — you don't need a map. Say so and stop; ask how Kyle wants to proceed.
3. **Pick the tracker backend** per [tracker.md](tracker.md) and record the choice in the map's Notes.
4. **Create the map**: Destination and Notes filled in, Decisions-so-far empty, the fog sketched into Not yet specified.
5. **Create the tickets you can specify now** as children, then wire blocking edges in a second pass (invariant `wire-second`). Everything you can't yet specify stays in the fog.
6. **Fire the research subagents, and resolve their tickets yourself.** For each **unblocked** `research` ticket just created — one whose blockers, if any, are already closed — claim it (invariant `claim-first`), then dispatch a subagent that calls the Skill tool with `research` to investigate it in parallel. **Blocked research tickets wait their turn**: step 5 wired the blocking graph precisely so it gates work, and a research answer produced on an unsettled premise still lands on the map's Decisions-so-far as though it were a decision on the route, where nothing reopens it when the blocker resolves differently.

   **Invariant `subagents-investigate-only`:** a dispatched research subagent **reads and writes its own findings file, and nothing else**. No git operations, no tracker writes, no resolution comment, no close, no map line. It returns three things — the findings file's path, a one-line gist, and the answer — and its job ends there.

   Two hazards make this the boundary, and both come from N agents sharing one working tree: a branch checkout is process-global, so subagents doing git fight each other and drag this session off its branch; and Decisions-so-far is a single shared file, so concurrent appends lose lines. Holding the boundary at "investigate only" removes both at once, and removes a third that a partial split creates — a subagent that dies *after* closing its ticket but *before* returning, leaving a decision recorded on a closed ticket that never reaches the map. A subagent that dies here has changed nothing at all.

   **You perform the whole of `resolve-order` for each ticket, as its subagent returns** — and **you do its git, since the subagent did none**. One ticket at a time, in this session:

   1. **Commit the returned findings file.**
   2. Post the answer as the resolution comment, then close the ticket. On the local backend both of those *are* edits to the ticket file, so **commit it here, once they're written** — not earlier, since before this step there is nothing in it to commit.
   3. Re-read the map body, append that one gist, and commit that map edit by itself — separate from the commits above, per `map-append-protocol` obligation 2.

   The order is the point: everything the map line will point at is committed before the line itself. A committed map entry linking a findings file that exists only in your working tree, or a ticket that git still shows as open and unanswered, is the invisibility `local-visible` exists to prevent.

   Then move to the next return. That keeps `resolve-order` atomic in one process (which is what it was always for), keeps the appends serialized, and discharges `map-append-protocol`'s two obligations once per ticket. Do **not** batch the resolutions to the end: this session is holding N research reports and is exactly where context runs out, and a ticket resolved but unrecorded is invisible — it passes the map-clear test, and the spec is written by walking Decisions-so-far.
7. **Release what never landed, then stop.** A subagent that errored, timed out, or returned nothing has left its ticket exactly as step 6 created it — open, with a claim this session took on its behalf. **Release that claim** so the ticket returns to the frontier; nothing else in this skill unclaims it, and `claims-are-released` is otherwise broken at the one site that isn't a session ending. There is no closed-but-unrecorded case to reconcile, because a research subagent never closes anything (`subagents-investigate-only`).

   Charting hand-resolves nothing else. Report the map by name with its link, name the frontier tickets Kyle could take next, and say plainly which research tickets came back empty and were released.

### Work through the map

Kyle invokes with a map (URL or number). A ticket argument is **optional**: without one, you pick the next decision, not him.

1. Load the **map** — the low-res view, not every ticket body.
2. **Read the Notes** before anything else, especially on a map you didn't chart. Apply invariant `no-self-licence` to whatever they claim.
3. Choose the ticket. If Kyle named one, use it. Otherwise take the first frontier ticket in order. **Claim it** before any work (invariant `claim-first`).
4. Resolve it. **Zoom as needed**: fetch the full body of any related or closed ticket on demand; call the Skill tool for whichever skills the Notes name. If in doubt, call the Skill tool twice, for `grilling` and `domain-modeling`.
5. **The session ends one of three ways.** Pick before writing anything to the tracker:
   - **Resolved** — you have an answer. Follow `resolve-order` below.
   - **Handed over** — a HITL ticket whose artifact or questions are now in front of Kyle and which only *he* can settle. Link the asset, leave the ticket **open and still claimed**, write **no** map line, and say plainly what you're waiting on. This is a complete, correct session; it is the normal ending for a `prototype` ticket, and closing one on your own read of your own artifact is the failure `hitl-needs-a-human` names.
   - **Released** — you got nowhere, or you're stopping for an unrelated reason. Release the claim (see `claims-are-released`) so the ticket returns to the frontier.

   **Invariant `resolve-order`** *(applies to the resolved ending only — it is not a demand that every session produce an answer)*: post the answer as a resolution comment, *then* close the ticket, *then* append the one-line gist to the map's Decisions-so-far. All three, in that order, in one process. A closed ticket with no comment has lost the decision; a comment with no map line has hidden it. Charting obeys this too, performing all three itself per returning research subagent — the reason `subagents-investigate-only` draws the line where it does is so that this invariant never has to span two processes.

   **Invariant `claims-are-released`:** a claim is a lease, not a deed. Nothing else in this skill unclaims a ticket, so a session that ends without resolving must either hand over explicitly or release — otherwise the ticket sits claimed forever, permanently off the frontier, and no later session ever surfaces it. A handed-over ticket keeps its claim on purpose (it's waiting on Kyle, not available to take); every other non-resolving ending releases.

   When appending to the map, obey `map-append-protocol` in [tracker.md](tracker.md): re-read the map body immediately before you append rather than trusting the copy you loaded at step 1, because a concurrent session may have written to it since.
6. Add newly-surfaced tickets (create-then-wire); graduate any fog the answer made specifiable (invariant `fog-shrinks`). If the answer reveals a ticket sits beyond the destination, rule it out of scope rather than resolving it on the route (on the local backend that also unblocks its dependents — `out-of-scope-unblocks`). If the decision invalidates other parts of the map, update or delete those tickets.
7. **Stop.** One ticket, one session.

Kyle may run unblocked tickets in parallel, so expect other sessions to be editing the tracker concurrently — both the tickets and, more easily lost, the map body. Warn him once if he asks to parallelize two `grilling` tickets: sessions share no context, so the second one will re-ask what the first just settled.

### A decision turns out to be wrong

Say so plainly rather than designing around it — the reflex to route the map past a bad decision instead of challenging it is a known failure here. Comment on the already-closed ticket, revise the tickets that rested on it, and correct the map's Decisions-so-far. Scope changes mid-map are recoverable; a map you *designed* to change is a scoping smell worth naming out loud.

## When the map clears

No open tickets and no fog means the way is clear. **A ticket is open until it is resolved or ruled out of scope, whoever holds the claim** (`status-and-claim-are-independent` in [tracker.md](tracker.md), which also says how each backend expresses that) — so a claimed-but-unresolved ticket still blocks the clear test, and an abandoned or handed-over one can never let a map be declared clear with a decision missing. Check for those before concluding anything.

**The map does not build the thing.** What's left is a set of linked decisions, which is not a build plan, so:

1. **Collapse the decisions into one spec.** Walk Decisions-so-far, zoom each ticket for its detail, and write a single document that states what is to be built and why — the decisions, not their transcripts. Put it where the repo already keeps specs; absent a convention, `docs/specs/<effort-slug>.md`. Link it from the map.
2. **Close the map** with a comment pointing at the spec.
3. **Route the next move.** Give Kyle 2–3 ranked options for what happens now — typically `backlog-hygiene` to slice and sequence the spec, `/autonomous-milestone` to build a well-specified chunk of it, or a straight builder session — each with a one-clause recommendation and an honest call on whether ultracode buys anything.
4. **Equip the next session.** Close with a Run-config note per the Planner/Builder protocol in `~/.claude/CLAUDE.md`: recommended model + effort, one clause why, and the literal launch command. `/launch` can start it.

Then stop. The session that finishes a map hands Kyle toward a spec, never toward a pull request.

## Unattended runs

Only `research` and AFK `task` tickets are resolvable with nobody there; `grilling` and `prototype` tickets are not (invariant `hitl-needs-a-human`), and neither is naming a destination.

- **Charting unattended:** do not create a map. A destination Kyle hasn't agreed to fixes the scope of everything downstream. Write the breadth-first frontier as a proposal — proposed destination, proposed tickets, the fog you can see — and stop.
- **Working unattended:** take the first frontier ticket whose type is `research` or AFK `task`, resolve it in full, and stop. If the frontier holds only HITL tickets, resolve nothing and report which ones are waiting on him, by name.
- Never grant execution licence, close a HITL ticket, redraw a destination, or rule something out of scope from an unattended run.

## It's working if

- The destination is written down and agreed before a single ticket exists.
- Every open ticket reads as a **question**. Any ticket that reads "build the X" is mis-typed or belongs downstream of the map.
- Kyle can look at the tracker and see which tickets are takeable without opening the map.
- A session resolves one ticket, comments, closes, leaves one line on the map — then stops. Or it hands one over and stops with the ticket open, which is equally correct; what never happens is a session inventing an answer so it has something to close.
- **Not yet specified** shrinks over time.
- When the opening breadth-first grill turns up no fog, the session says the effort is small enough to skip the map, and stops.

---

Vendored from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT, Copyright (c) 2026 Matt Pocock), adapted to house conventions. Full notice: `THIRD-PARTY.md` in the claude-config repo.
