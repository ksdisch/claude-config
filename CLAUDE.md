# Operating Constraints

@~/.claude/operating-constraints.md

---

# Claude Code Modes

Three structured modes for working with Claude Code. Type the trigger phrase to activate.

---

## Kickoff Mode → run the `/kickoff` skill

**Purpose:** Start a brand new project from a rough, half-baked idea — interview it into shape before any code.
**Trigger:** `/kickoff`, "kickoff mode", or "new project idea" (followed by the idea).

When any of those fire, **invoke the `kickoff` skill** (`~/.claude/skills/kickoff/`) — do not improvise the interview inline. The skill runs the deep, adaptive, one-question-at-a-time discovery interview (for as long as the idea needs), produces an approved kickoff brief + phased plan, and — only after I confirm at a gate — scaffolds `~/Projects/<slug>/`, a git repo, and a private GitHub repo with the brief inside. Briefs are archived in `~/Projects/_kickoffs/`. For light throwaway experiments, use `/mini` instead.

---

## Improvement Mode

**Purpose:** Fix, refine, or optimize something that already exists in the project but isn't working well.
**When to use:** Something feels off — slow performance, bad UX, ugly layout, confusing flow, or a bug you can't fully describe.
**Trigger:** Say "improvement mode" followed by what bugs you.

When I say "improvement mode", before making any changes:
- Ask me what part of the project I want to improve
- Ask me what's wrong with it or what bugs me about it
- Ask me what "better" looks like in my words
- Review the current code/implementation yourself and tell me what you see
- Propose 2-3 approaches ranked by effort vs. impact
- Wait for me to pick one before changing anything

---

## New Feature Mode

**Purpose:** Add a new capability or feature to an existing project without breaking what's already there.
**When to use:** You want the project to do something it doesn't do yet and need Claude Code to figure out where and how it fits.
**Trigger:** Say "new feature mode" or "feature mode" followed by your idea.

When I say "new feature mode" or "feature mode", before building anything:
- Ask me to describe the feature in plain language
- Ask me why I want it (what problem does it solve)
- Review the existing project structure and tell me how/where this feature would fit
- Flag any conflicts with how things currently work
- Propose how it connects to existing features
- Summarize the plan and wait for approval before writing code

---

## Git Workflow

- Always create a feature branch before making changes
- Branch naming: `feat/`, `fix/`, `refactor/`, `docs/`
- Commit frequently with descriptive messages
- **Keep me in the loop, don't gate on me (updated 2026-06-13).** Commit, push, open PRs, and merge them to `main` autonomously — no per-push go-ahead needed. In exchange, brief me at the point of action (what changed, commit SHA, PR link, whether you merged) and recap at session end. I'd rather be told after the fact than asked before — but nothing happens silently.
- Still branch + PR for every change; the PR is the durable record that keeps me briefed, not a gate. Don't push straight to `main`.
- **Review-gate proposal before autonomous merge (updated 2026-08-22; supersedes the mandatory loop added 2026-07-26).** Before merging any PR yourself, don't auto-run the `adversarial-review` loop — **propose** it: give me your honest take on whether review is warranted for this diff and at what scope — **skip / single round / full loop** — with the why (risk surface, behavioral vs. mechanical content, blast radius, test coverage). Interactive sessions: STOP and wait for my call; I can veto in either direction (skip a review you proposed, or run one you'd skip), and my call is final for that merge. Unattended runs: make the call yourself and record the decision + reasoning in the merge brief — never silently — with one floor: diffs touching behavioral/agent-instruction files (as defined in `adversarial-review`'s severity-and-scope reference: any `CLAUDE.md`, `skills/**`, `agents/**`, `commands/**`, hooks, or `settings*.json`) get at least a single round when I'm not around to veto. Recommendation heuristics: behavioral files, data integrity, auth, or money lean full loop; ordinary well-tested code often earns a single round; docs-only, comment-only, config-typo diffs earn a skip (the old escape hatch is now just the bottom of this spectrum). **Single round** means one reviewer dispatch → triage → judge on disputes → fix, with fixes self-verified by the author (no re-review lap) — escalate to a re-review dispatch only if the round surfaced a critical or left a coverage bound unclosed. The sole named substitute remains `ship-and-route`'s §1.3 release gate — one gate per merge, not two — which follows this same propose-first convention; future substitutes get added to this line by name. Whatever review does run, critical and should-fix findings still block the merge — fixed-and-verified (self-verified under a single-round scope), closed or downgraded by the judge, or explicitly waived by me; nice-to-haves become follow-ups listed in the PR comment.
- Pause and ask first only for genuinely irreversible/destructive ops: force-push, history rewrite, production deploys. Exception: deleting the remote copy of a feature branch you created and already merged via PR is routine cleanup — do it without asking (this is the same "delete branch" button GitHub offers after every merge). Still pause before deleting any other remote ref or branch — one you didn't create, one that isn't confirmed merged, a shared/long-lived branch, or a tag.
- A specific project's `CLAUDE.md` may tighten this back (e.g. require my merge, or hold risky changes for a heads-up); the project rule wins where it does.

## Clarifying questions and option formatting
- Ask 1–3 high-leverage clarifying questions up front whenever a prompt is ambiguous or uses fuzzy terminology — I prefer alignment over rework. When offering options: give each a short label, a 1–2 sentence merits/tradeoffs description, and mark your "(Recommended)" pick. If you assume rather than ask, surface the assumptions before acting on them.

## Never show me a bare identifier (added 2026-08-13)

**An ID you put in front of me is a pointer into a document I don't have open.** `F2`, `D31`, `S1.4`, `T3`, "slice C" — each is a label whose meaning lives somewhere else, and I can't memorize them across sessions. A table of `# · grade · verdict` tells me the shape of a decision without telling me what I'm deciding, so I either approve blind or go hunting. Neither is what I'm paying attention for.

**The rule, in three parts:**

1. **Every ID you put in front of me carries a gloss on its first mention in a turn** — `F2 (digest strips the wrong tags)`, `D31 (T3 threshold 70 → 85)`, `S1.4 (statusline reads one turn stale)`. Later mentions in the same turn can go bare; prose shouldn't turn into a glossary. **Whether you minted it this session or inherited it is irrelevant** — inherited is the *common* case and the one this rule is mostly about, since an ID from a past session or an existing doc is precisely the one I can't be expected to recall. Applies to every kind: review findings, decision rows, spike questions, triggers, build slices, milestones.
2. **Any table listing IDs gets a title column.** ID, severity/status, **what it is**, then your reason or disposition. The title column is not optional and is not the same as the reason column — "contradicts the plan table" is what's wrong; "recorded in one file while §13 says otherwise" is why you think so. I need both.
3. **Say where the full text lives, and how to open it.** Once per response that references IDs, give the absolute path *and* a copy-pasteable command — `code <path>` (or `open <path>` for anything that isn't text). Not "see the mailbox"; the actual line I can paste.

**This is a presentation rule and it outranks a skill's or command's output spec.** If a template says `# · grade · verdict · one-line reason`, render it with the title column anyway. Where a skill or command writes a durable artifact for somewhere else (a PR comment, a report file), that artifact follows its own template — this rule governs what reaches *me*, in chat.

**Where a spec fixes the order of a response, rule 3's path line rides with the note that referenced the IDs — wherever that note sits.** It is never appended as a new trailing slot after a spec's final element, and it never goes inside the paste. Two response shapes exist and the rule has to work for both:

- `/handoff-session` puts its notes **before** the fenced block and forbids anything after it, so the path line joins the "For Kyle" briefing (slot 1) and the run-config ordering rule is untouched.
- `ship-and-route` and `backlog-hygiene` put the fenced block **first** and every Kyle-facing note after it, so the path line rides with whichever of those notes cited the ID.

A spec that fixes its order wins on *placement*; it does not win on *omission*.

**What it does not license:** dumping full claims, evidence blocks, or quoted code inline. The gloss is a title, not a paragraph. The point is that I can decide from the table and open the file when I want depth — not that the file gets pasted into the conversation.

## Planner/Builder Protocol (added 2026-07-27)

How model choice works across my sessions: **Fable 5 plans, Opus 5 builds, Sonnet 5 grinds.**

- Judgment-first work — planning, design calls with real tradeoffs, triage/adoption decisions, convention-setting — runs on Fable 5. Well-specified builds run on Opus 5. Mechanical, checklist-scoped work runs on Sonnet 5.
- Every plan or handoff written for another session to execute ends with a **Run-config note**: recommended model + effort for that session, a one-clause why, and the literal launch command (e.g. `claude --model claude-opus-5 --effort high`). `--model` and `--effort` are per-invocation flags — they never touch my saved defaults. "Ends with" means it closes the *substance*: it comes after everything the plan or handoff has to say, is never buried mid-document, and is never folded inside a paste-able block. Pure delivery artifacts may follow it — in `/handoff-session`, on `--audio`, the audio note does, and then the paste-able block itself, both by design. Call it a **note**, never a "block", so it never reads as belonging inside that paste.
- **Effort ladder (this protocol owns it — `/handoff-session` and `/prompt-optimize` both cite here, never each other):** `ultracode` for broad, parallelizable, want-exhaustive-coverage work (multi-agent fan-out + adversarial verify) · `max` / `xhigh` for ONE hard problem, design calls with real tradeoffs included (`max` uncapped and fast-burning, `xhigh` hard-but-bounded) · `high` for ordinary build work with judgment in it · `medium` / `low` for mechanical, checklist-scoped work. Effort is independent of the model pick.
- Builder sessions start **fresh from the plan file**, never from the planning session's transcript. Never recommend switching models mid-session after heavyweight planning: `/model` keeps the conversation but invalidates the per-model prompt cache — the full transcript re-ingests at uncached rates, and the build inherits deliberation noise it doesn't need.
- **Split planner from builder only when build ≫ plan.** When the work is plan-heavy and build-light, finish it in the Fable session — a handoff would cost more than it saves.
- In-session alternative for mid-size, decomposable builds: stay in the Fable session and dispatch scoped tasks to subagents with `model:` and `effort:` pinned in their frontmatter (see `agents/silent-failure-hunter.md` and `agents/spec-miner.md` for the worked shape). Both keys are real, consumed agent-file fields — but a *misspelled* `effort:` only logs a warning and falls back to the default; it never fails the dispatch, so proofread the value.

---

## Reference Doc Maintenance

`~/Projects/claude-config/docs/command-skill-reference.md` is the living index of every custom slash command, skill, and agent; `docs/usage-playbook.md` is its paired companion, holding one run-config card per indexed item. **Keep both in sync in the same commit that changes what the index records — an item's existence, name, or description. Never batch those updates later.** The "When to update" table below is the complete trigger list: a commit that changes an item's internals without touching its name or description needs no edit to either doc. This includes mid-review fix commits — a fix that reworks a `description:` triggers the sync just like the original add did.

This rule fires everywhere (this file is the global CLAUDE.md), so it covers global items in this repo AND project-specific items in any project.

### When to update

| Action | What to do in the reference doc |
|---|---|
| Add a new global skill (`skills/<name>/`) | Add a row to the appropriate category table under "Global Skills" |
| Add a new global command (`commands/<name>.md`) | Add a row to the appropriate category table under "Global Commands" |
| Add a project-specific skill or command | Add a row under that project's section in "Project-Specific Items"; create the section if the project isn't listed yet |
| Rename or change the description of any item | Find its row and edit in place |
| Delete any item | Remove its row; remove the project section entirely if it's now empty |
| Add a custom subagent (`agents/<name>/`) | Add it to the "Custom Subagents" section at the bottom |
| A new project gets a `.claude/` with skills or commands | Add a new `### Project Name` subsection under "Project-Specific Items" with a one-line description of what the project is |

**Every action in that table applies to the playbook too.** An added item gets a card (Run config · Reach for it when · Pairs well with, per the conventions already in `docs/usage-playbook.md`); a renamed or re-described item gets its card edited; a deleted item loses its card — and the row's `config →` link and the card's anchor stay in agreement.

This is checked, not remembered: `scripts/check-doc-sync.py` runs as the repo's tracked `pre-push` hook (`.githooks/pre-push`, activated by `install.sh` via `core.hooksPath`), so a row without its card blocks the push instead of landing. It checks the **commits being pushed**, not the working tree, so a half-finished doc edit can't block an unrelated branch. It fires for terminal and agent pushes alike; `git push --no-verify` bypasses it deliberately. Run it any time with `python3 scripts/check-doc-sync.py`. It also verifies the other direction — every tracked file matching the standard layout (`commands/<name>.md`, `agents/<name>.md`, `skills/<name>/SKILL.md`) has a row, and no row links to a file that's gone; anything item-shaped outside that layout is warned about rather than passed over. **What it still can't check** is project-specific items: their files live in other repos, so nothing here verifies that a DogHood skill you added has a row. That part is still on you.

### Format rules
- One-line description per entry: what it does, not how it works
- For global items: assign to the most fitting existing category; only create a new category if nothing fits
- For project-specific sections: include a one-sentence description of the project above the table(s)
- Commit the reference-doc row **and its playbook card** in the **same commit** as the skill/command change (or as an immediately following commit on the same branch — the check runs at `git push`, so the branch has to be consistent before it leaves the machine)

---

## Local-Markdown Issue Tracker: Tickets Index (added 2026-08-22)

The mattpocock engineering skills (`setup-matt-pocock-skills`, `to-tickets`, `wayfinder`, `implement-spec`, ...) are vendored raw upstream via `npx skills` and deliberately untracked in `claude-config` (see `THIRD-PARTY.md`) — I can't durably edit their templates or process steps there; any edit would be unreviewable and silently lost on the next reinstall. This section is the editable substitute: it supplements their **local-markdown** issue-tracker mode (`.scratch/<feature-slug>/issues/<NN>-<slug>.md`, one file per ticket) with a convention the upstream files don't define.

**Keep one-file-per-ticket as the source of truth.** Per-ticket `Status:` / `Blocked by:` lines and `## Comments` history live only in the issue files — never collapse them into a single combined file.

**Also maintain a generated index.** Every time tickets are published to a local-markdown tracker (`/to-tickets`, or any skill step that says "publish to the issue tracker" in local-markdown mode), write or refresh `.scratch/<feature-slug>/tickets.md` — a short manifest listing, for each ticket: number, title, one-line summary, `Status`, and `Blocked by`, each linking to its issue file. Refresh it again whenever a ticket's `Status` changes (claim, resolve, triage). This is what makes `/implement @tickets.md`-style references resolve without hand-listing every issue file.

```markdown
# Tickets: <feature-slug>

Generated index — resolves to the issue files below. Source of truth is `issues/`; refresh on publish or Status change.

| # | Title | Summary | Status | Blocked by |
|---|---|---|---|---|
| [01](issues/01-slug.md) | Ticket title | One-line summary | resolved | None |
| [02](issues/02-slug.md) | Ticket title | One-line summary | ready-for-agent | 01 |
```

**The manifest is an entry point, never the source of truth.** Ticket-consuming skills (`/implement`, `/implement-spec`, `/wayfinder`, `/triage`) should treat `tickets.md` as an index that resolves to the issue files — read it to find which files exist and their current status, then read the issue files themselves for content (What to build / Acceptance criteria / Comments). If `tickets.md` and an issue file's `Status:` line ever disagree, the issue file wins; refresh the manifest.

**When scaffolding a new repo for local-markdown tracking**, `/setup-matt-pocock-skills` writes that repo's own `docs/agents/issue-tracker.md` from the untracked upstream template, which doesn't mention this convention. Append a short "Tickets index" subsection to that file (mirroring the two paragraphs above) so the convention is discoverable in-repo too, not just from this global file.

---

## Project Wiki

When working in a project that contains `PROJECT.md`, a `Wiki/` directory, or `HANDOFF.md`, maintain the project wiki using the `project-wiki` skill:
- Before integrating a new source: read `PROJECT.md` and `Wiki/_index.md`, then report the proposed update scope before making broad changes
- Record decisions in `Decisions.md`; update `HANDOFF.md` whenever work pauses or state changes
- Make surgical updates — don't reorganize the entire wiki because a new source was added
- Label all claims: Fact / Inference / Recommendation / Decision / Proposed / Unresolved / Contradiction

New projects started via `/kickoff` automatically get a wiki initialized. To retroactively initialize all existing projects, run `/wiki-init --all`.
