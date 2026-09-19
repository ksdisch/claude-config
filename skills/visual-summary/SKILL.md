---
name: visual-summary
description: Use when Kyle wants to SEE what happened instead of reading about it — one self-contained HTML page summarizing a conversation, a branch, or an uncommitted worktree as charts, diagrams, and short labels instead of prose. Saves the page beside the session logs and publishes it as a claude.ai Artifact every run. Triggers: "/visual-summary", "visual summary", "summarize this visually", "make me a picture of what we did", "chart what changed on this branch", "show me the shape of this work", "one-page summary of the diff". NOT for: a written recap with vocabulary and recall quiz (/wrap), a prose walkthrough of a project (project-guide), a module dependency map (architecture-viewer), a paste-able prompt for a fresh session (/handoff-session), or judging whether a diff is safe to merge (adversarial-review).
---

# Visual Summary — one page, read at a glance

Kyle's brief, verbatim: *"Create a single page HTML summary of the [conversation |
branch | work tree]. Make it visual and digestible without additional cognitive
fatigue. Minimal text, clear flow of information. Opt for charts and diagrams over
long explanations."*

So the deliverable is a **picture of the work**, not an illustrated essay. The page
answers *what happened, how much, and in what order* from across the room. Anyone
who has to read a paragraph to get the answer has been failed by the page.

**Run this at low effort.** The judgment here is which three or four visuals earn
the page — not deep analysis. Gather, pick, render, deliver.

---

## Parse `$ARGUMENTS`

- **Mode** — `conversation` (default) | `branch` | `worktree`. Say which mode you
  picked before gathering anything.
- **`--out <dir>`** → write the HTML there instead of the default location.
- **`--no-publish`** → save the local file only. Publishing is on by default,
  every run; this is the escape hatch for a page Kyle doesn't want a link to.

---

## The three modes

Each mode sees a different thing, and one of them can be empty. Check the
availability line **before** gathering, and stop with the stated redirect rather
than rendering a page about nothing.

| Mode | What it summarizes | Gather | Empty when |
|---|---|---|---|
| `conversation` | **This session's transcript only** | What you did this session: the arc of decisions, the files touched, what was tried and abandoned, what's unresolved | You were launched fresh into this session. There is no transcript to read and no way to recover one — say so and offer `branch` or `worktree` |
| `branch` | The diff against the merge-base with `main` | `git merge-base main HEAD`, then `git diff --stat <base>...HEAD`, `git log --oneline <base>..HEAD`, and the diff itself for what actually changed | The branch has no commits past the merge-base — offer `worktree` |
| `worktree` | The uncommitted working tree | `git status --short`, `git diff HEAD --stat`, and the diff itself | The tree is clean — offer `branch` |

In `branch` and `worktree` mode, read enough of the diff to say what the change
*does*, not just which files moved. A page that charts line counts and names no
mechanism is a page of arithmetic.

---

## The visual contract

Checkable bounds, because "minimal text" loses to the drift toward explaining.

- **Every claim on the page is measured.** Line counts, commit counts, file names,
  decisions actually made. No estimated percentages, no invented severity scores,
  no round-number filler. A thing you cannot measure is a thing you leave off.
- **Three to five visuals, and a headline.** Below three, a list would have done.
  Above five, the page needs scrolling and scanning, and the glance is gone.
- **One prose block, the headline claim** — at most two sentences, at the top,
  saying what this work *is*. Everything else is a chart, a diagram, or a label.
- **Ten words per label.** A caption longer than that is an explanation wearing a
  caption's clothes; cut it or move the content into the visual.
- **One flow, top to bottom.** The page reads in a single column in one direction:
  headline → what changed → how much → what's open. A reader should never have to
  choose where to look next.
- **Honest emptiness.** A section with nothing in it is omitted, never padded. No
  "no blockers identified" tiles.

---

## Build it

1. **Gather** per the mode table. Keep the raw numbers; the page cites them.
2. **Pick the visuals.** Match the shape to the content rather than reaching for
   the same four every run:
   - A **timeline or flow** for the arc — commits in order, or the sequence of
     decisions that got here. Almost always earns its place.
   - A **bar or treemap** for magnitude — churn by area, files by size of change.
     One magnitude chart, not three.
   - A **before → after diagram** for the mechanism that actually changed. This is
     the visual that makes the page worth more than `git diff --stat`, and it is
     the one most often skipped. Draw it when a mechanism changed.
   - **Chips or cards** for discrete facts — decisions made, files touched, open
     questions. Not a table pretending to be a card.
3. **Load the design skills before writing any HTML.** They own these rules; this
   skill does not restate them:
   - `artifact-design` — required before writing the page, every run.
   - `dataviz` — before writing any chart: palette, form heuristic, mark specs.
   - `artifact-diagramming` — before drawing any diagram, including the
     before → after.

   The `Artifact` tool's own description is the authority on page constraints —
   title, theme tokens, the CDN allowlist, favicon. Follow it rather than
   guessing.
4. **Write one self-contained HTML file.** No external resource of any kind, so
   the file opens from disk years from now. Default path, when `--out` is absent:
   `docs/session-logs/YYYY-MM-DD-<project>-<slug>-visual.html`, beside the
   Markdown recaps `/wrap` writes — same `<project>` tag and slug conventions.

---

## Deliver

1. **`SendUserFile`** the HTML. It is meant to be opened, not described.
2. **Publish**, unless `--no-publish`: `Artifact` with a short distinctive title
   (the branch or session's subject, not "Visual Summary"), favicon `"📊"`, and a
   one-sentence `description`. Hand Kyle the link.
3. **Report in chat in three lines**: mode and what it covered, the local path,
   the Artifact link. The page is the summary — don't also summarize it in chat.
4. **Git.** When the summarized repo is the one this session is working in, follow
   the normal workflow. The page is an artifact *about* the work, so it does not
   belong in the branch it describes unless Kyle asks — save it and say where it
   landed.

---

## What it deliberately does not do

- **No judgment on the work.** It shows what happened; it does not grade the diff,
  flag risk, or recommend a next move. Review is `adversarial-review`'s job and
  routing is `ship-and-route`'s.
- **No cross-session history.** One conversation, one branch, or one tree. It
  never reads past session logs to assemble a longer story.
- **No live page.** Static HTML. It does not refresh, poll, or track state.

---

## Definition of done

The mode was named before gathering; every number on the page traces to something
measured this run; the page carries three to five visuals, one headline, and no
second prose block; `artifact-design` was loaded before the HTML was written, with
`dataviz` and `artifact-diagramming` loaded for whatever the page actually
contains; the file is self-contained at its reported path; it was sent with
`SendUserFile` and published (or `--no-publish` was passed); and chat got the three
lines rather than a retelling.
