---
name: cc-yt-idea-mine
description: >-
  Exhaustively mine a video transcript about software engineering / AI / Claude Code /
  AI agents for every segment implementable in Kyle's Claude Code setup — skills, slash
  commands, subagents, hooks, settings, output styles, MCP servers, statusline,
  keybindings, CLAUDE.md conventions. Produces a tiered, dedup-tagged, leverage-ranked
  report saved under ~/Learning, then a gated, verified capture of picked ideas into
  claude-config's backlog. Proposes only — never builds. Trigger on "mine this video for
  Claude Code ideas", "idea-mine this video", "what could I build from this video",
  "any Claude Code ideas in this", or /cc-yt-idea-mine. NOT for general video analysis —
  "analyze / break down / summarize / critique this video" and "study notes" belong to
  youtube-breakdown.
---

# CC YouTube Idea Mine

Turn a talk about software engineering, AI, or Claude Code into a ranked inventory of
things worth building in Kyle's own Claude Code setup. The niche is exactly
**transcript-in → Claude-Code-artifact-proposals-out**: not what the video teaches
(`youtube-breakdown` Mode 1), not what Kyle should do about his work in general (Mode 4),
but what could become a skill, command, agent, hook, or setting in his config.

The skill is a scanner and a proposer. It never builds what it finds — building a skill has
its own gates (adversarial review, doc sync) that must not run as a side effect of watching
a video.

---

## Invariants

These hold on every run. Everything else in this file is guidance.

- **Propose, never build.** The run ends at proposals plus a handoff offer. Building a pick
  — even a one-line hook — happens only after Kyle says yes to that offer, as its own work.
- **No invention.** Every idea traces to a verbatim quote from the transcript. If the
  transcript doesn't support it, it isn't in the report.
- **Full recall, tiered presentation.** Nothing implementable is dropped; the long tail is
  compressed to one line each, never deleted. If a bound is ever applied (a chunked sweep
  that skipped a section, a truncated transcript), say so in the report — never cap
  silently.
- **No numeric scoring.** Ranking is ordinal judgment. No scores, no weights, no
  composites.
- **The report is unverified; picks are verified.** The report ships fast with a staleness
  caveat. Only ideas Kyle selects at the capture gate get their capability claims checked —
  verification cost scales with what he keeps.
- **Capture is gated.** Nothing is written to any repo before Kyle picks at the gate. The
  report file under `~/Learning` is the only thing written without asking.
- **Fixed capture home.** Approved globally-useful picks land in
  `~/Projects/claude-config` regardless of where the skill runs — that is where the
  artifact would be built.
- **Dedup degrades loudly.** If the inventory doc can't be read, the report says dedup was
  skipped and why — it never silently presents un-tagged ideas as new.
- **Stay out of youtube-breakdown's lane.** If the ask is really "analyze / summarize /
  critique this video" or "study notes", hand off to `youtube-breakdown` instead of
  running this skill on a mismatched request.
- **Unattended runs stop at the report.** In a subagent, cron, cloud, or autonomous run,
  produce and save the report, note inside it that capture is pending an interactive
  session, and end. The gate needs Kyle.

---

## Steps

### 1. Get the transcript

| Input | How to handle |
|---|---|
| **YouTube URL** | Invoke the **`youtube-transcript`** skill. The transcript is an intermediate, not a deliverable — have it written to the session scratchpad, never into a repo. While the URL is in hand, also ask yt-dlp to print the video's `upload_date`; it feeds the staleness caveat. |
| **File path** | Read it directly. Upload date: unknown unless Kyle supplies it. |
| **Pasted text** | Use directly. Upload date: unknown unless Kyle supplies it. |

If the input is ambiguous — a non-YouTube URL, or text too short to plausibly be a
transcript — ask one clarifying question rather than guessing.

**Long transcripts (>30k words):** say so up front, then sweep in sections and merge the
idea lists before step 4. The completeness critic then runs over the merged list plus the
section map, so a section that produced suspiciously little gets a second look.

**One video per run.** Given several URLs, do the first and say the others each get their
own run.

### 2. Read the inventory

Read `~/Projects/claude-config/docs/command-skill-reference.md` — the index of everything
Kyle already has. It powers the dedup tag every idea carries:

- **New** — nothing in the inventory does this.
- **Overlaps `<item>`** — an existing item covers part of it; the idea may really be an
  improvement to that item. Overlaps stay in the report for exactly that reason.
- **Already covered by `<item>`** — the inventory already does this; the idea is listed in
  the long tail so Kyle knows the video pitched it, tagged so he doesn't re-read it as new.

If the file is missing or unreadable (different machine, moved repo), continue without
dedup and state that prominently in the report — see the invariant.

### 3. Extraction pass

Read the whole transcript and extract **every segment containing something implementable**
in the Claude Code setup. In scope as target artifact types:

skills · slash commands · subagents · hooks · `settings.json` · output styles · MCP
servers · statusline · keybindings · CLAUDE.md rules / workflow conventions.

An "implementable segment" is any technique, feature, workflow habit, configuration, or
tool usage that could become one of those artifact types for Kyle. Bias toward
globally-useful ideas; a project-specific idea is admissible where it clearly earns it, and
carries the project's name. When one segment suggests several distinct artifacts, that is
several ideas.

Each idea records:

- **Title** — short, imperative where natural.
- **Artifact type** — one of the ten above.
- **What it is** — one or two sentences.
- **Why it's leverage** — what improves in Kyle's actual workflows.
- **Effort band** — S / M / L to build.
- **Reach** — Global, or Project(`<name>`).
- **Dedup tag** — from step 2.
- **Quote anchor** — a short verbatim quote from the transcript. The transcript text
  carries no timestamps (the converter strips them), so the quote is the searchable
  pointer — findable in the transcript file or YouTube's own transcript panel.
- **Staleness flags** — the specific Claude Code capability claims the idea depends on
  (a flag name, a hook event, an API), listed so step 7 knows what to verify.

### 4. Completeness critic

Before rendering anything, run a second sweep over your own output — the recall backstop:

1. **Silent sections** — which stretches of the transcript produced zero ideas? Re-read
   them; talks bury implementable asides in demos and Q&A.
2. **Empty categories** — which in-scope artifact types have zero finds? For a video about
   agent workflows, zero hook ideas is suspicious; zero keybinding ideas is normal. Chase
   the suspicious ones.
3. **Fused ideas** — is any extracted idea really two artifacts sharing a sentence? Split
   them.

Add what this pass finds, then move on. One critic pass, not a loop.

### 5. Rank and tier

- **Tier** — the top tier is the set Kyle would plausibly consider building, typically
  5–12 ideas; everything else is the long tail. When in doubt, tail it — the tail is still
  in the report.
- **Rank** — top-tier ideas are grouped by artifact type, leverage-ranked within each
  group, and also ranked overall across categories. The overall rank rides in parens after
  the title: `1. Block force-push via a PreToolUse hook (4)` reads "#1 among hooks, #4
  overall."

### 6. Write and show the report

Write the report to `~/Learning/youtube-notes/` (create the directory if it doesn't
exist), then display it inline in full. **No save prompt** — the location was fixed by
design, so there is no per-run choice to ask about. Tell Kyle the path.

Filename: `YYYY-MM-DD-<kebab-case-video-title>-idea-mine.md`. Frontmatter:

```yaml
---
title: "[video title]"
source: "[URL, or: file path / pasted transcript]"
speaker: "[if identifiable, else: unknown]"
published: [YYYY-MM-DD, or: unknown]
date_processed: [today, YYYY-MM-DD]
skill: cc-yt-idea-mine
tags: [youtube, idea-mine, claude-code]
---
```

The three free-text fields are quoted — talk titles are full of colons, and a bare
`title:` with a colon in the value is a YAML parse error that silently voids the whole
block. Escape any `"` inside a value as `\"`.

Report body:

```markdown
## Snapshot
- **Video:** [title] — [speaker]
- **Published:** [date or unknown] · **Processed:** [date]
- **Staleness caveat:** [e.g. "Published 7 months ago. Claude Code moves fast —
  every capability claim below is unverified until the capture gate checks the
  ones you pick." If dedup was skipped, say so here too.]

## Overall top picks
[Ordered list of the strongest ideas across all categories — title + artifact
type, one line each. This is the scan-first view.]

## <Artifact type with finds>   (one section per non-empty type)
1. **<Title>** (<overall rank>)
   - **What:** …
   - **Why:** …
   - **Effort:** S|M|L · **Reach:** Global | Project(<name>) · **Dedup:** New |
     Overlaps <item> | Already covered by <item>
   - **Anchor:** "<short verbatim quote>"
   - **Depends on:** [staleness flags, or "nothing version-sensitive"]

## Long tail
[One line per idea: title — artifact type · reach · dedup tag. Full recall
lives here; nothing found is omitted.]
```

### 7. Capture gate

Ask which ideas to capture — **one / several / all / none**. None ends the run cleanly;
the report stands on its own. This is a per-run gate: no prior blanket approval counts.

For picks tagged Project(`<name>`), the capture offer is to **that project's own
backlog** (step 8's project variant), not to claude-config.

### 8. Verify, then land the picks

**Verify first.** For each pick, check its staleness flags — does the claimed feature,
flag, event, or API still exist as described? Use the `claude-code-guide` agent or the
current Claude Code docs. Outcomes:

- **Confirmed** — land it.
- **Changed** — amend the idea to today's reality, tell Kyle what moved, land the amended
  version unless he objects.
- **Gone** — back to Kyle: keep as inspiration (noting the dependency is dead), amend, or
  drop.

**Then land, in `~/Projects/claude-config`** (global picks):

1. Fetch and branch from up-to-date `origin/main` — never from whatever happens to be
   checked out; concurrent sessions leave state there. Branch prefix `docs/`.
2. For each landed idea, write a vision doc `docs/ideas/<kebab-title>.md`. Mirror the
   existing ideas-doc shape: `# <Title>` · **Status:** Idea — not committed. Mined from
   "<video title>" (<source>) by `cc-yt-idea-mine` on <date>. · **Premise** · **The bet**
   · **Decisions / open questions** · **Credible first step** · **Dependencies** (include
   the verification result) · **Explicitly out of scope** · **Source segment** (the quote
   anchor, plus surrounding context worth keeping).
3. Append a stub to `BACKLOG.md` under `## Open` — never edit existing items. Match the
   house stub shape: `### [Type] <Title>` with **Why** (one sentence + link to the vision
   doc), **Acceptance**, **Size** (from the effort band), **Added** (today). Type: an
   Overlaps-tagged idea that improves an existing item is `[Improvement]`; a concrete new
   artifact is `[Feature]`; an uncertain bet is `[Exploration]`.
4. Stage the specific files (never `git add -A` — concurrent sessions leave untracked
   state), commit, push, open the PR, and merge — this is Kyle's standing git workflow.
   The diff is docs-only and non-behavioral, so the adversarial-review skip applies:
   **state the skip and the reason in the merge brief**, never silently. Report the PR
   link and merge SHA.

**Project picks:** confirm the project's path with Kyle if it isn't obvious, then append a
self-contained stub (the full why inline — don't link into `~/Learning`) to that repo's
backlog file via that repo's own git workflow; its `CLAUDE.md` rules win. If the project
has no backlog file, say so and leave the idea in the report.

### 9. Handoff offer

End with an offer, never an action:

> Want me to build one of these now, or set up a builder session for it
> (`/handoff` / `/launch` per the planner/builder protocol)? Building a skill or command
> gets its own branch, review loop, and doc-sync — it doesn't ride on this run.

If Kyle declines, the run is complete — the report and any captured stubs are the
deliverable.

---

## Related

- **`youtube-transcript`** — supplies the text when the input is a URL.
- **`youtube-breakdown`** — the general four-mode sibling. "Analyze / break down /
  summarize this video" is its lane, including Mode 4's life-and-work actionables.
- **`/brainstorm`** — the capture shape (vision doc + backlog stub behind a gate) is
  deliberately the same, so ideas from videos and ideas from brainstorms groom
  identically.
- **`backlog-hygiene`** — grooms and sequences what this skill captures.
- **`claude-code-guide`** agent — the verification instrument at the capture gate.
