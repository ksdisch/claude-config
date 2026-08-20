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

---

## Backend A — GitHub Issues (preferred)

All operations go through the `gh` CLI, which infers the repo from the clone it runs inside.

### Create the map

Create one issue carrying the map body, labelled `wayfinder:map`. Create the label first if the repo doesn't have it. The issue's title is the **name** of the map and is how it is referred to from then on.

### Create a child ticket

1. Create the issue with the question as its body and a `wayfinder:<type>` label — one of `research`, `prototype`, `grilling`, `task`.
2. Attach it to the map as a **sub-issue**. The REST surface is a POST to `repos/{owner}/{repo}/issues/{map-number}/sub_issues`, whose body field is the child's numeric **database id** — not its `#number`, not its `node_id`. Read that id off the child issue's `id` field.
3. **Fallback `no-sub-issues`:** if that call is rejected because sub-issues aren't available on this repo or plan, add the child to a task list in the map body and put a `Part of #<map>` line at the top of the child's body. Say once, in the session, that the fallback is in force — a map whose parentage is a text convention needs closer reading than one whose isn't.

### Record a blocking edge

1. Prefer GitHub's **native issue dependencies**: a POST to `repos/{owner}/{repo}/issues/{blocked-number}/dependencies/blocked_by`, whose body field is again the blocker's numeric **database id**. Native is strongly preferred because it is what renders the frontier in GitHub's own UI — Kyle can see what's takeable without opening the map, which is most of why the tracker is worth the ceremony.
2. Read the edges back from the `issue_dependencies_summary.blocked_by` count on an issue, which counts **open** blockers only and is therefore the live gate.
3. **Fallback `no-dependencies`:** if the endpoint isn't available, put a `Blocked by: #<n>, #<n>` line at the top of the blocked issue's body, and say once in the session that blocking is text-inferred and needs manual review.

**Invariant `wire-second`:** create every ticket in a first pass, then wire blocking edges in a second. Issues need ids before they can reference each other.

### Query the frontier

Take the map's open children, then drop any that has an open blocker and any that has an assignee. What survives, in map order, is the frontier; the first is the default pick.

### Claim

Assign the ticket to Kyle's account (`--add-assignee @me` where the session runs as him). **Invariant `claim-first`:** the claim is the session's first write to the tracker, before any work on the question. An open, unassigned ticket is unclaimed, so a session that works first and claims later can be duplicated by a concurrent session.

### Resolve

In order: post the answer as a comment on the ticket, close the ticket, then append one line to the map's **Decisions so far**. See `resolve-order` in SKILL.md.

---

## Backend B — Local markdown (fallback)

The map is a directory of files under `docs/wayfinder/<effort-slug>/`, tracked in git alongside everything else Kyle keeps in `docs/`.

- **Map:** `docs/wayfinder/<effort-slug>/map.md`, holding the same Destination / Notes / Decisions-so-far / Not-yet-specified / Out-of-scope body.
- **Ticket:** `docs/wayfinder/<effort-slug>/tickets/NN-<slug>.md`, numbered from `01`, the question in the body. Near the top it carries three lines: `Type:` (`research` / `prototype` / `grilling` / `task`), `Status:` (`open` / `claimed` / `resolved` / `out-of-scope`), and `Blocked by:` listing ticket numbers.
- **Blocking:** the `Blocked by:` line. A ticket is unblocked when every ticket it lists is `resolved`.
- **Frontier:** the tickets whose `Status:` is `open` and whose blockers are all `resolved`; lowest number first.
- **Claim:** set `Status: claimed` and save the file before any work — same `claim-first` invariant as GitHub.
- **Resolve:** append the answer under an `## Answer` heading, set `Status: resolved`, then append the one-line gist and a relative link to the map's Decisions-so-far.
- **Out of scope:** set `Status: out-of-scope` rather than deleting the file, so the record of the scoping call survives.

**Invariant `local-visible`:** the map directory is committed, not gitignored. A local map that isn't in git is invisible to every other session and to Kyle on another machine, which defeats the "shared map" the skill is named for.

**What this backend costs you:** no visual frontier. Blocking is a text convention, so the dependency graph is only as right as the last session that edited it — review it yourself before working two tickets in parallel.
