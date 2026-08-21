# Where the map lives

`wayfinder` needs six operations from a tracker: **create the map**, **create a child ticket**, **record a blocking edge**, **query the frontier**, **claim**, **resolve**. This file says how each is expressed on the two backends, and how to pick between them.

Everything below is a procedure, not a script. Read the steps and write your own commands; the invariants are what must hold, and each is named so it can be cited.

## Picking a backend

Decide **once, at charting time**, and record the choice in the map's Notes so later sessions don't re-derive it.

1. If the repo has no git remote, or `gh auth status` reports no authenticated account → **local markdown**.
2. Otherwise ask GitHub whether the repo has Issues enabled (the `has_issues` field on the repo object). Disabled → **local markdown**.
3. Otherwise, if the repo is **public**, say so and ask before proceeding: a public tracker fills with agent-generated planning tickets that everyone watching the repo receives. Kyle may still choose GitHub; the point is that he chooses knowingly. Unattended, with no answer available → **local markdown**.
4. Otherwise → **GitHub Issues**.

**Invariant `one-backend`:** a map lives entirely on one backend. Never create the map on GitHub and its tickets locally, or migrate a live map mid-effort; a half-migrated map has two frontiers and neither is right.

## Cross-backend rules

These hold whichever backend is in play, so they live above the split rather than inside either section.

**Invariant `status-and-claim-are-independent`:** whether a ticket's question is still live, and whether someone is currently on it, are **two axes** and never collapse into one. A ticket is **open** until it is resolved or ruled out of scope — claiming does not change that, so a claimed ticket is still an open ticket, and SKILL.md's "open ticket" always means exactly this, including in the map-clear test. Each backend expresses the two axes with its own primitives (GitHub: issue state + assignee; local markdown: a `Status:` line + a `Claimed by:` line), and neither field name is the rule. Collapsing them would let an abandoned ticket read as not-open, and a map holding one of those would pass "no open tickets and no fog" and get collapsed into a spec with a decision missing.

---

## Backend A — GitHub Issues (preferred)

All operations go through the `gh` CLI, which infers the repo from the clone it runs inside.

### Create the map

Create one issue carrying the map body, labelled `wayfinder:map`. Create the label first if the repo doesn't have it. The issue's title is the **name** of the map and is how it is referred to from then on.

### Create a child ticket

1. Create the issue with the question as its body and a `wayfinder:<type>` label — one of `research`, `prototype`, `grilling`, `task`.
2. Attach it to the map as a **sub-issue**. The REST surface is a POST to `repos/{owner}/{repo}/issues/{map-number}/sub_issues`, whose body field is the child's numeric **database id** — not its `#number`, not its `node_id`. Get that id from **`gh api repos/{owner}/{repo}/issues/{number}`**, whose `.id` is the numeric database id.

   **Trap `node-id-not-database-id`:** `gh issue view <n> --json id` looks like the right source and is not — its `id` is the GraphQL **node id** (`I_kwDO…`, or `PR_kwDO…` when the number is a PR). It is the only id-shaped field `gh issue view` offers, so the wrong value is also the convenient one. Posting it fails the call. Use the `gh api` REST path above; this trap applies everywhere on this page that asks for a database id.
3. **Fallback `no-sub-issues`:** if that call is rejected because sub-issues aren't available on this repo or plan, add the child to a task list in the map body and put a `Part of #<map>` line at the top of the child's body. Say once, in the session, that the fallback is in force — a map whose parentage is a text convention needs closer reading than one whose isn't.

### Record a blocking edge

1. Prefer GitHub's **native issue dependencies**: a POST to `repos/{owner}/{repo}/issues/{blocked-number}/dependencies/blocked_by`, whose body field is again the blocker's numeric **database id** — read the same way, and subject to the same trap `node-id-not-database-id`. Native is strongly preferred because it is what renders the frontier in GitHub's own UI — Kyle can see what's takeable without opening the map, which is most of why the tracker is worth the ceremony.
2. Read the edges back from the `issue_dependencies_summary.blocked_by` count on an issue, which counts **open** blockers only and is therefore the live gate.
3. **Fallback `no-dependencies`:** if the endpoint isn't available, put a `Blocked by: #<n>, #<n>` line at the top of the blocked issue's body, and say once in the session that blocking is text-inferred and needs manual review.

**Invariant `wire-second`:** create every ticket in a first pass, then wire blocking edges in a second. Issues need ids before they can reference each other.

### Query the frontier

Take the map's open children, then drop any that has an open blocker and any that has an assignee. What survives, in map order, is the frontier; the first is the default pick.

### Claim

Assign the ticket to Kyle's account (`--add-assignee @me` where the session runs as him). **Invariant `claim-first`:** the claim is the session's first write to the tracker, before any work on the question. An open, unassigned ticket is unclaimed, so a session that works first and claims later can be duplicated by a concurrent session.

**Release** by removing the assignee (`--remove-assignee`). Claiming never changes open/closed state — an assigned issue is still an open issue. See `claims-are-released` in SKILL.md.

### Resolve

In order: post the answer as a comment on the ticket, close the ticket, then append one line to the map's **Decisions so far**, obeying `map-append-protocol` below. All three are one session's work — see `resolve-order` in SKILL.md.

**The resolver is always a session, never a dispatched research subagent.** Those investigate and return; their parent runs this procedure on what comes back (`subagents-investigate-only` in SKILL.md).

---

## Backend B — Local markdown (fallback)

The map is a directory of files under `docs/wayfinder/<effort-slug>/`, tracked in git alongside everything else Kyle keeps in `docs/`.

- **Map:** `docs/wayfinder/<effort-slug>/map.md`, holding the same Destination / Notes / Decisions-so-far / Not-yet-specified / Out-of-scope body.
- **Ticket:** `docs/wayfinder/<effort-slug>/tickets/NN-<slug>.md`, numbered from `01`, the question in the body. Near the top it carries four lines: `Type:` (`research` / `prototype` / `grilling` / `task`), `Status:` (`open` / `resolved` / `out-of-scope`), `Claimed by:` (a name, or `—` for unclaimed), and `Blocked by:` listing ticket numbers.
- **Blocking:** the `Blocked by:` line. A ticket is unblocked when every ticket it lists is `resolved` **or** `out-of-scope` — see `out-of-scope-unblocks` below.
- **Frontier:** the tickets that are `open`, unblocked, and whose `Claimed by:` is `—`; lowest number first.
- **Claim:** set `Claimed by:` to the driving dev and save the file before any work — same `claim-first` invariant as GitHub. **Leave `Status: open`.** Claiming is not closing; a claimed ticket is still an open ticket.
- **Resolve:** append the answer under an `## Answer` heading, set `Status: resolved`, then append the one-line gist and a relative link to the map's Decisions-so-far, obeying `map-append-protocol` below. As on Backend A, the resolver is always a session — a dispatched research subagent never edits a ticket file or `map.md` (`subagents-investigate-only` in SKILL.md).
- **Release:** set `Claimed by:` back to `—`. See `claims-are-released` in SKILL.md.
- **Out of scope:** set `Status: out-of-scope` rather than deleting the file, so the record of the scoping call survives.

These two lines are this backend's expression of `status-and-claim-are-independent` above: `Status:` is the open/resolved axis, `Claimed by:` is the who's-on-it axis, and neither is ever folded into the other.

**Invariant `out-of-scope-unblocks`:** a blocker that leaves scope stops blocking, exactly as a closed issue does on GitHub. Ruling a ticket out of scope is therefore never a way to strand its dependents. Revisit each dependent in the same edit: with its premise gone, it is usually itself out of scope, or its question has changed and the ticket needs rewriting.

**Invariant `map-append-protocol`:** appending to Decisions-so-far is read-modify-write on a resource other sessions also write. Two obligations, and they are separate:

1. **Re-read, then append, with nothing in between** *(both backends, every append)* — re-read the map body immediately before appending, not the copy loaded at the start of the session, and if it changed since load, re-apply your line on top of the current text. No unrelated work between the re-read and the write: every step you take in that gap is time for another session to land a line you are about to overwrite.
2. **Commit each map edit on its own** *(local backend, every append)* — never folded in with ticket files or anything else, so a clobber is visible in `git log` instead of silent. This is the half that actually *detects* a lost line, and a session appending N times satisfies it N times, one commit each.

**Neither obligation says the append must be a session's last write**, and no session in this skill could honour that if it did: charting appends once per returning research subagent with step 7 still to come, and a work-through session appends at step 5 and then edits the same map body again at step 6 whenever fog graduates (`fog-shrinks`) or something is ruled out of scope. Shortening the window is obligation 1's job and detecting a loss is obligation 2's; do not defer or batch appends chasing an ordering guarantee this protocol never claimed, because batching separates a resolution's third step from its first two, which is what `resolve-order` forbids.

This is a backstop against *other sessions*, which the tracker can't serialize. It is not what protects a single session's own parallelism: `subagents-investigate-only` keeps dispatched research subagents off the map and off git entirely, so every writer that has to obey this invariant is a session that can also commit. Losing the line is not cosmetic — the ticket keeps the decision, but the map is the only index anyone loads.

**Invariant `local-visible`:** the map directory is committed, not gitignored. A local map that isn't in git is invisible to every other session and to Kyle on another machine, which defeats the "shared map" the skill is named for.

**What this backend costs you:** no visual frontier. Blocking is a text convention, so the dependency graph is only as right as the last session that edited it — review it yourself before working two tickets in parallel.
