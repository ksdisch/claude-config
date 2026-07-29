# Build Plan: Usage Playbook (per-item config advice)

**Status:** Approved plan, ready to build. Planned by a Fable 5 session on 2026-07-28; this
document is the sole input the builder session needs (do not go hunting for the planning
session's transcript — it doesn't add anything).

## Goal

Create `docs/usage-playbook.md` — a companion doc to `docs/command-skill-reference.md` that
gives every custom slash command, skill, and subagent a **detail card**: suggested model +
effort level, concrete use cases, and what it pairs well with. The reference doc stays the
lean, sync-enforced index; the playbook holds the judgment content. Then cross-link the two
and land the change through the standard git workflow with the adversarial-review gate.

Decisions already made by Kyle (do not re-litigate):

1. **Placement:** new companion doc `docs/usage-playbook.md`; reference-doc rows link to
   their cards. Not inline in the reference doc, not extra table columns.
2. **Scope:** everything — all global commands, all global skills, all project-specific
   items (A2C, clinical-data-etl, Constellation, DogHood, home-base, stopwatch, forge-gap),
   and the 4 custom subagents.
3. **Process:** fully autonomous — draft, adversarial-review loop, merge. No preview gate.

## Deliverables

1. `docs/usage-playbook.md` — one card per item, structure mirroring the reference doc's
   section order exactly (Global Commands by category → Global Skills by category →
   Project-Specific Items by project → Custom Subagents).
2. Edits to `docs/command-skill-reference.md` — per-row links to the cards + a pointer
   paragraph in the intro + a keep-in-sync note.
3. A README navigation entry for the new doc.
4. Branch → PR → adversarial-review loop → autonomous merge → end on pulled `main`.

## Card template

Use exactly this shape for every item (omit **Notes** when there's nothing non-obvious):

```markdown
### `/brainstorm`

- **Run config:** Fable 5 · `ultracode` — blind parallel lenses + two-sided critic gates
  are exactly the fan-out + adversarial-verify shape ultracode exists for.
- **Reach for it when:**
  - The backlog feels stale or safe and you want ideas outside the usual grooves.
  - Starting a new phase and you want the option space mapped before committing.
- **Pairs well with:** `replenish` (runs it as one lane), `backlog-hygiene` (sequences the
  survivors), `kickoff` (when an idea outgrows the current project).
```

Rules:

- **Run config** = model · effort, one clause of *why*, using the effort-ladder vocabulary
  (see rubric). For items that run inside an already-running session (e.g. `/begin`,
  `/catchup`, `reweave`), say "inherits the session — fine on any model" instead of
  prescribing one; only prescribe when the item is worth launching a session *for*.
- **Reach for it when** = 2–3 bullets of concrete situations, written to Kyle. Ground them
  in the item's actual file (triggers, gates, modes), not just the index description.
- **Pairs well with** = 2–4 items, each with a parenthetical saying *how* they connect.
  Every pairing must be real (one dispatches/feeds/follows the other) — no vibes-based
  pairings. Link each named item to its card anchor.
- **Notes** (optional) = gates/interactivity caveats (e.g. "has a hard STOP gate — don't
  run unattended"), autonomy behavior, deprecations.

## Rubric: deriving Run config (the effort ladder)

This is the Planner/Builder protocol from the global `~/.claude/CLAUDE.md` — the playbook's
advice must be consistent with it:

- **Fable 5** for judgment-first work: planning, design calls with real tradeoffs, triage
  and routing decisions, coaching, convention-setting.
- **Opus 5** for well-specified builds and synthesis-heavy writing.
- **Sonnet 5** for mechanical, checklist-scoped grinding (scaffolds, audits with fixed
  rubrics, CLI orchestration).
- **Effort:** `ultracode` = broad parallelizable fan-out with adversarial verify ·
  `max`/`xhigh` = ONE hard problem or a design call with real tradeoffs · `high` =
  ordinary build work with judgment in it · `medium`/`low` = mechanical, checklist-scoped.
- Effort is independent of the model pick. Subagent cards note what their frontmatter
  already pins rather than recommending a session config.

## Pre-assigned run configs (planner's calls — the judgment is done)

The builder's job is to **verify each assignment against the item's source file and write
the prose**, not to re-derive the calls. If reading a file genuinely contradicts an
assignment (e.g. a skill turns out to be far more/less autonomous than assumed), adjust it
and list every deviation in the PR body under "Plan deviations". Read every item's source
file before writing its card — the "Reach for it when" bullets and Notes must come from the
file, not from this table.

### Global Commands

| Item | Model · Effort | Rationale (compress into the card) | Pairs with |
|---|---|---|---|
| `/begin` | inherits session · `low` | Orientation ritual; cheap on any model | `/wrap` (reads its log), `reorient` (long gaps), `/catchup` |
| `/wrap` | inherits session · `medium` | Recap + recall synthesis; no need to switch | `/begin` (next session), `/handoff`, `narrate` (`--audio`) |
| `/catchup` | inherits session · `low` | Narration of existing context | `narrate` (engine), `/wrap` (endgame sibling) |
| `/handoff` | inherits session · `medium` | Summarization + a run-config judgment call at the end | `/begin`, `/prompt-optimize`, `narrate` |
| `/learn` | Fable 5 or session · `high` | Judging what generalizes into a skill is convention-setting | `/wrap`, `superpowers:writing-skills`, `adversarial-review` (skills never skip the gate) |
| `/explore-plan` | Fable 5 · `high` (`xhigh` if gnarly) | Planning with ranked tradeoffs is judgment-first | `/tdd` (executes the pick), `/autonomous-milestone`, `adversarial-review` |
| `/brainstorm` | Fable 5 · `ultracode` | Blind parallel lenses + critic gates = fan-out + adversarial verify | `replenish` (lane), `backlog-hygiene`, `kickoff` |
| `/autonomous-milestone` | Opus 5 · `ultracode` | Build-heavy autonomous run with explicit multi-agent opt-in | `backlog-hygiene` (hands off to it), `ship-and-route`, `adversarial-review` |
| `/prompt-optimize` | Fable 5 · `medium` | Advisory diagnosis + routing; small output, real judgment | `/handoff`, `kickoff`, `/explore-plan` |
| `/reframe-orchestrator` | Opus 5 · `high` | Careful docs restructuring against live references | `/claudify-repo`, `adversarial-review` |
| `/tdd` | Opus 5 · `high` | Ordinary build work with discipline | `/explore-plan` (upstream), `superpowers:test-driven-development`, `adversarial-review` |
| `/screenshot-iterate` | Opus 5 · `medium` | Iterative visual build; loop does the correcting | `match-the-mock` (auto sibling), `/boot_server`, `frontend-design` |
| `/smoke-test` | Sonnet 5 · `medium` | Checklist assembly + page opening | `/boot_server` (it auto-boots), `ship-and-route`, DogHood `/verify` |
| `/trim-context` | Sonnet 5 · `medium` | Fixed-rubric audit + mechanical fixes | `/claudify-repo`, `claude-md-management` plugin skills |
| `/boot_server` | Sonnet 5 · `low` | Detect, start, open — mechanical | `/smoke-test`, `/screenshot-iterate`, `run` |
| `/envsetup` | Sonnet 5 · `low` | Stub + open pages; user pastes the value | `/boot_server`, `kickoff`/`mini` (post-scaffold) |
| `/claudify-repo` | Sonnet 5 · `medium` (Port) / Opus 5 · `high` (Brainstorm) | Port is a picker + copy; Brainstorm spawns the recommender | `kickoff`, `mini`, `claude-automation-recommender` |
| `/wiki-init` | Sonnet 5 · `medium` | Idempotent scaffold via project-wiki INIT | `project-wiki`, `/wiki-backfill`, `kickoff` (auto-runs it) |
| `/wiki-backfill` | Opus 5 · `medium` | History mining + narrative synthesis | `project-wiki` (BACKFILL mode), `reorient`, `project-guide` |

### Global Skills

| Item | Model · Effort | Rationale | Pairs with |
|---|---|---|---|
| `kickoff` | Fable 5 · `high` (`ultracode` if using the pre-mortem panel) | Deep adaptive interview + de-risking = judgment-first | `mini` (lighter sibling), `/claudify-repo`, `/wiki-init`, `/prompt-optimize` |
| `mini` | Sonnet 5 · `medium` | Short interview + scripted scaffold | `kickoff` (upgrade path), `/envsetup` |
| `project-wiki` | inherits session · `medium` | Surgical maintenance inside whatever session triggered it | `/wiki-init`, `/wiki-backfill`, `ship-and-route` (state changes) |
| `reorient` | Opus 5 · `medium` | Read-and-brief synthesis; routes, builds nothing | `/begin` (short-gap sibling), `backlog-hygiene`, `ship-and-route` |
| `reweave` | inherits session · `medium` | Re-integration of an answer already in context — never switch sessions for it | `/explore-plan` (reweave its plans), `/handoff` |
| `ship-and-route` | Fable 5 · `high` | Landing decisions + ranked routing = triage judgment | `adversarial-review` (its gate), `backlog-hygiene`, `/handoff` |
| `backlog-hygiene` | Fable 5 · `high` | Pure prioritization/sequencing decisions | `replenish` (when dry), `/autonomous-milestone` (executes pick), `/brainstorm` |
| `replenish` | Fable 5 · `ultracode` | Multi-lane brainstorm + bug-hunt fan-out | `/brainstorm`, `bug-hunt` (its lanes), `backlog-hygiene` (afterward) |
| `bug-hunt` | Opus 5 · dialable `medium`→`ultracode` | Explicitly dialable: quick single-agent pass → full fan-out + adversarial verify | `superpowers:systematic-debugging` (fixes the picks), `silent-failure-hunter` (its lens), `adversarial-review` (pre-merge counterpart) |
| `adversarial-review` | Opus 5 · `high` | Author triage + dispute judgment; dispatches its own pinned subagents | `adversarial-reviewer` + `review-judge` (its agents), `ship-and-route`, every merge |
| `artifacts-audit` | Opus 5 · `medium` | Taxonomy audit → plan; plans only | `artifacts-generate` (executes), `project-guide` |
| `artifacts-generate` | Opus 5 · `medium` | Well-specified doc writing from an approved plan | `artifacts-audit` (upstream), `adversarial-review` |
| `seed-hunt` | Fable 5 · `high` | Scoring papers against a selection bar = triage judgment | `research-paper` (upstream closer), `kickoff` (downstream), `/handoff` |
| `notebook-init` | Sonnet 5 · `medium` | Interview + nlm CLI orchestration | `notebook-assist`, `audio-series`/`video-series`, `nlm-skill` |
| `notebook-assist` | Sonnet 5 · `medium` | Artifact refinement + source management | `notebook-init`, `notebook-merge`, `nlm-skill` |
| `notebook-merge` | Opus 5 · `medium` | Cross-notebook integration judgment + careful migration | `notebook-assist`, `notebook-init`, `nlm-skill` |
| `audio-series` | Sonnet 5 · `medium` | Quota-aware batched generation — checklist-shaped | `notebook-init`, `video-series` (sibling), home-base `episode-review` |
| `video-series` | Sonnet 5 · `medium` | Same shape as audio-series | `audio-series`, `notebook-init`, home-base catalog |
| `nlm-skill` | inherits session · `low` | Reference guide, not a workflow | every NotebookLM skill |
| `research-paper` | Opus 5 · `xhigh` | One hard synthesis: a full paper from recorded results | `seed-hunt` (runs after), `project-guide`, `narrate` |
| `paper-eli5` | Opus 5 · `high` | Long 1:1 faithful rewrite — demanding, well-specified | `paper-gloss` (next), `paper-figures` (next), `narrate` |
| `paper-gloss` | Opus 5 · `medium` | Term proposal + hand-authored HTML from an existing eli5 | `paper-eli5` (upstream), `paper-figures` |
| `paper-figures` | Sonnet 5 · `medium` | Mechanical figure harvesting + placeholder filling | `paper-eli5`, `paper-gloss` |
| `project-guide` | Opus 5 · `high` | Whole-project synthesis + interview lens | `/wiki-backfill`, `reorient`, `interview-prep` |
| `narrate` | inherits session · `low` | TTS rendering engine invoked by other commands | `/catchup`, `/handoff --audio`, `/wrap --audio` |
| `career-coach` | Fable 5 · `high` | MCC-level coaching = pure judgment, zero build | `interview-prep`, `seed-hunt` |
| `interview-prep` | Sonnet 5 · `medium` | Dossier bundling + notebook orchestration | `career-coach`, `project-guide`, `notebook-init` |
| `match-the-mock` | Opus 5 · `medium` | See-and-correct UI iteration | `/screenshot-iterate` (manual sibling), `/boot_server`, `frontend-design` |

### Project-Specific Items

One card per item, grouped by project exactly as in the reference doc. Source files live in
each project's `.claude/` (paths per the reference doc: `~/Desktop/A2CAuctions/`,
clinical-data-etl, Constellation, DogHood, home-base, stopwatch (Tempo), forge-gap — find
the repos under `~/Projects/` unless the reference doc says otherwise). If a project repo
is unreadable from the build session, write the card from the reference-doc description and
say so in the PR body.

| Item | Model · Effort | Rationale | Pairs with |
|---|---|---|---|
| A2C `replenish-a2c` | Sonnet 5 · `medium` | Parallel audit + prospecting lanes, fixed shape | `stage-a2c` (next), `rebrief-a2c` |
| A2C `stage-a2c` | Sonnet 5 · `medium` | Draft staging + reconciliation; never sends | `replenish-a2c`, `rebrief-a2c` |
| A2C `rebrief-a2c` | Sonnet 5 · `medium` | Gmail/Todoist sweep + reconcile + brief | `stage-a2c`, `replenish-a2c` |
| etl `add-source` | Opus 5 · `high` | End-to-end pipeline wiring across schema/loader/dbt | `new-dbt-model`, `/tdd` |
| etl `new-dbt-model` | Sonnet 5 · `low` | Convention-following scaffold | `add-source` |
| Constellation `new-planet` | Sonnet 5 · `low` | Contract-following scaffold, modeled on an exemplar | `new-power`, `/verify-planet` |
| Constellation `new-power` | Sonnet 5 · `low` | Same scaffold shape | `new-planet`, `/verify-planet` |
| Constellation `/verify-planet` | Sonnet 5 · `medium` | Scripted Playwright verification | `new-planet`, `/smoke-test` |
| Constellation `/moonshot` | — deprecated | Card = one line pointing at `/brainstorm` Moonshot mode | `/brainstorm` |
| DogHood `adr-new` | Sonnet 5 · `low` | Numbered-template scaffold | `/new-scope`, `new-migration` |
| DogHood `new-migration` | Sonnet 5 · `medium` | Boilerplate scaffold, but RLS content deserves care | `adr-new`, `/verify` |
| DogHood `/new-scope` | Sonnet 5 · `low` | Template scaffold | `adr-new`, `/ship` |
| DogHood `/reconcile-backlog` | Sonnet 5 · `medium` | Fixed drift-table reconcile | `/scheduled-reconcile` (unattended twin) |
| DogHood `/scheduled-reconcile` | Sonnet 5 · `medium` | Unattended weekly reconcile | `/reconcile-backlog` |
| DogHood `/ship` | Sonnet 5 · `medium` | Gate-aware commit→push→PR recipe | `/verify` (feeds PR body), `/new-scope` |
| DogHood `/verify` | Sonnet 5 · `medium` | Path→check mapping, deterministic | `/ship`, `/smoke-test` |
| home-base `course-builder` | Opus 5 · `high` | Autonomous multi-material authoring after one approval | `/build-course` (entry), `episode-review`, `review-next` |
| home-base `episode-review` | inherits session · `low` | Interactive quiz + progress logging | `course-builder`, `review-next`, `audio-series` |
| home-base `review-next` | Sonnet 5 · `low` | Read-only ranking from the progress store | `episode-review` |
| home-base `youtube-breakdown` | Sonnet 5 · `medium` | Transcript → one of four fixed formats | `course-builder`, catalog |
| home-base `catalog-doctor` | Sonnet 5 · `low` | Read-only drift report | `api-types-sync`, `review-next` |
| home-base `api-types-sync` | Sonnet 5 · `medium` | Mechanical type reconciliation | `catalog-doctor` |
| home-base `/build-course` | Opus 5 · `high` | Thin entry to course-builder — same config | `course-builder` |
| Tempo `/add-panel` | Sonnet 5 · `low` | Registered-scaffold + cache bump | `/new-engine-module`, `/run-tests` |
| Tempo `/new-engine-module` | Sonnet 5 · `low` | Wiring scaffold | `/add-panel`, `/run-tests` |
| Tempo `/fix-bug` | Opus 5 · `high` | Root-cause debugging against playbooks | `/run-tests`, `superpowers:systematic-debugging`, `/ship-pr` |
| Tempo `/run-tests` | Sonnet 5 · `low` | Diff-driven suite selection | `/fix-bug`, `/ship-pr` |
| Tempo `/ship-pr` | Sonnet 5 · `medium` | DoD pre-flight + house-convention PR | `/run-tests`, `/fix-bug` |
| forge-gap `/document-stage` | Opus 5 · `medium` | Teaching + recall synthesis | `/wrap`, `seed-hunt` |

### Custom Subagents

Cards note the **pinned** config (from each agent file's frontmatter — read it; e.g.
spec-miner is Opus-pinned) plus who dispatches them. Do not recommend a session config.

| Agent | Card focus | Pairs with |
|---|---|---|
| `adversarial-reviewer` | Dispatched by `adversarial-review`; zero-context, repo-read-only; never launch ad hoc for general review | `review-judge`, `adversarial-review` |
| `review-judge` | Rules only on disputed findings; neutral, no deference | `adversarial-reviewer`, `adversarial-review` |
| `silent-failure-hunter` | `bug-hunt`'s silent-failure lens; also standalone on explicit ask; read-only | `bug-hunt`, `superpowers:systematic-debugging` |
| `spec-miner` | Two dispatch modes (map / mine); never overwrites without `OVERWRITE=yes` | `kickoff` (brownfield onboarding), `/tdd` (specs → tests) |

## Playbook front matter (top of the doc)

- Title + 2–3 sentence intro: what the doc is, that the reference doc is the index and
  this is the "how to run it" companion.
- A compact legend restating the effort ladder and model roles (Fable plans / Opus builds /
  Sonnet grinds) in ~6 lines, linking the reader's mental model to the cards. Cite
  `~/.claude/CLAUDE.md`'s Planner/Builder protocol as the source of truth so the ladder is
  never duplicated authoritatively.
- A keep-in-sync note: *when a row is added/renamed/deleted in the reference doc, the
  matching card changes in the same commit.*

## Cross-linking spec

1. In `docs/command-skill-reference.md`: append ` · [config →](usage-playbook.md#<anchor>)`
   to the description cell of **every** row that has a card. Anchor = GitHub's auto-anchor
   for the card heading (e.g. `### \`/boot_server\`` → `#boot_server`). Verify a few
   anchors by eye — backticks are stripped, slashes dropped, underscores kept.
   Project-specific items whose headings could collide with a global name (none known —
   check while writing) get a project-suffixed heading.
2. Reference-doc intro: add one sentence pointing at the playbook.
3. `README.md`: add the playbook to the docs navigation, mirroring how
   `command-skill-reference.md` is linked.
4. Do **not** edit the global `~/.claude/CLAUDE.md` in this build. If the builder believes
   the Reference Doc Maintenance rule should formally extend to playbook cards, propose it
   as a follow-up in the PR comment for Kyle to approve — the in-doc sync notes carry the
   rule for now.

## Landing procedure

1. Work on branch `docs/usage-playbook` (already created and pushed with this plan on it).
2. Commit granularity: plan file is already committed; then (a) playbook doc, (b)
   cross-links + README, or one commit for both — builder's call. Conventional commits,
   `docs:` prefix.
3. Push, open the PR (body: what/why, the plan-deviations list, the follow-up proposal).
   **Known hook quirk:** run `git push` as its own Bash call, separate from any command or
   heredoc containing PR-body text with the word "main" — a guard hook false-positives on
   it (see memory: claude-config deploy wiring).
4. Run the **adversarial-review skill** (this diff is substantial docs — the trivial-diff
   escape hatch does NOT apply). Resolve critical/should-fix findings per the loop; merge
   autonomously on CLEAR.
5. End on pulled `main` (the repo symlinks into `~/.claude/` — live config comes from the
   checked-out branch).
6. Brief Kyle: PR link, merge status, deviations, follow-ups.

## Quality bar

- Every card grounded in its source file, not just the index description — the reviewer
  should find no card that contradicts its item's actual gates, modes, or autonomy level.
- Pairings must be bidirectionally sane: if A's card says "pairs with B", B's card should
  usually name A too (not mandatory when the relationship is one-directional, e.g. an
  engine like `narrate`).
- No duplicated authority: the effort ladder lives in CLAUDE.md; the playbook restates it
  as a legend and defers.
- Keep cards tight — 6–10 lines each. The doc will have ~75 cards; discipline per card is
  what keeps it usable.

---

**Run-config note:** Build this in a fresh session on **Opus 5 · effort `high`** — it's a
well-specified, judgment-adjacent writing build (the config calls are pre-made; the prose
and verification still need care), which is exactly the `high` band; no fan-out needed, so
no ultracode. Launch: `cd ~/Projects/claude-config && claude --model claude-opus-5 --effort high`,
then prompt: *"Check out the `docs/usage-playbook` branch and execute
`docs/plans/2026-07-28-usage-playbook-plan.md` end to end."*
