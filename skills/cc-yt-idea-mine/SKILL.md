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
- **The report path is derived, never composed.** The filename slug follows step 6's
  character rule — the video title is third-party text — and the resolved path must sit
  inside `~/Learning/youtube-notes/`. Anything else stops the run.
- **Fixed capture home.** Approved globally-useful picks land in
  `~/Projects/claude-config` regardless of where the skill runs — that is where the
  artifact would be built.
- **Dedup degrades loudly.** If any category's inventory source is missing, unreadable,
  or readable but empty of entries for that category, the report names the category and
  the reason in its blind-spots line — it never silently presents un-tagged ideas as new.
  Exceptions are stated where the source is listed: a file whose absence *means* "none
  configured" (keybindings, a project `.mcp.json`) is an answer, not a blind spot.
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
| **YouTube URL** | Invoke the **`youtube-transcript`** skill, running the whole fetch from the session scratchpad — the transcript and its intermediates (`title.txt`, the `.vtt`) are not deliverables and never touch a repo; the producer's own "Where the file goes" section names this contract. Add `%(upload_date)s` and `%(uploader)s` to the producer's step-2 `%(duration)s|%(id)s` print — never to the print redirected into `title.txt`, which must stay title-only because the converter reads that whole file as the filename stem. Reformat `upload_date`'s `YYYYMMDD` to `YYYY-MM-DD` for the frontmatter (it feeds the staleness caveat); `uploader` feeds `speaker:` per step 6's sourcing order. When the conversion finishes, note the transcript's **absolute** path — the converter prints a relative name and the shell cwd resets between calls, so carry the path explicitly rather than as implicit state. |
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

Dedup needs an inventory per artifact category, and no single file covers all ten.
`docs/command-skill-reference.md` indexes only skills, commands, and agents — the first
real run was structurally blind for rule-shaped ideas until it hand-checked the other
sources. Read what actually records each category:

- **Enabled plugins (feeds several categories)** — the `enabledPlugins` map in
  `~/.claude/settings.json`. It maps plugin name to a boolean, so only `true` entries
  count as installed capability. Plugins ship skills, commands, agents, and MCP servers
  alike — when an idea might already be plugin-provided, check the `true` plugins' own
  directories under `~/.claude/plugins/`.
- **Skills, slash commands, subagents** —
  `~/Projects/claude-config/docs/command-skill-reference.md` for custom items, plus the
  enabled plugins' `skills/` directories: the reference doc indexes only what lives in
  the config repo — plugin-shipped skills come with their plugin and are invisible to
  it by its own charter.
- **CLAUDE.md rules / workflow conventions** — `~/.claude/CLAUDE.md` and
  `~/.claude/operating-constraints.md`.
- **Hooks and settings.json** — the `hooks` block of `~/.claude/settings.json` and
  `~/.claude/hooks/`.
- **Output styles / statusline** — `~/Projects/claude-config/output-styles/`; for the
  statusline, read `settings.json`'s `statusLine` block — whatever command it names is the
  live statusline, and the repo's `statusline-command.sh` is authoritative only when
  `statusLine` actually points at it. The command's *name* is not an inventory: when it
  names `ccstatusline`, the widget list is `~/.config/ccstatusline/settings.json`; when
  it names a script, read the script. If what it names can't be read, that is a blind
  spot.
- **Keybindings** — `~/.claude/keybindings.json`. This file may legitimately not exist:
  absence means no custom keybindings are configured, so keybinding ideas are genuinely
  New — count it as a blind spot only if it exists and can't be read.
- **MCP servers** — the `mcpServers` block of `~/.claude.json` (not `settings.json`,
  which has no such key), the enabled-plugins read above (plugins ship servers), and
  the project's `.mcp.json` when one exists (its absence is per-project normal, not a
  blind spot).
- **Standing lessons** — the memory index at
  `~/.claude/projects/-Users-kyledisch-Projects-claude-config/memory/MEMORY.md`, which
  records adopted conventions that live nowhere else (hooks-over-prompts, the
  bare-identifier rule's ancestors). Memory is per-project, so the ambiently-loaded
  session memory belongs to whatever project the skill runs from — a supplement, never
  the source.

Every idea carries one of **four** tags:

- **New** — nothing in the inventory does this.
- **Overlaps `<item>`** — an existing item covers part of it; the idea may really be an
  improvement to that item. Overlaps stay in the report for exactly that reason.
- **Already covered by `<item>`** — the inventory already does this; the idea is listed in
  the long tail so Kyle knows the video pitched it, tagged so he doesn't re-read it as new.
- **Contradicts `<item>`** — the idea conflicts with an existing item or convention rather
  than duplicating it: adopting it means changing or retiring what exists. Often the most
  valuable tag in a report, because it forces a decision. Never soften a genuine conflict
  into Overlaps with a parenthetical.

A category is a blind spot when its source is missing, unreadable, **or readable but
carrying no entries for that category** — a config file that parses fine while holding no
relevant block dedups nothing, and that silent success is exactly what the invariant
forbids. (Exceptions: a source whose absence *means* "none configured" — keybindings
above, a project `.mcp.json` — is an answer, not a blind spot.) Continue without dedup
for a blind-spotted category and name it, with the reason, in the Snapshot's dedup
blind-spots line.

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
- **Decision-forcing counts as leverage.** An idea tagged Contradicts, whose payoff is
  forcing a call on an existing convention rather than building something, may earn top
  tier on that basis — its Why line says so plainly instead of dressing it up as
  buildability.

### 6. Write and show the report

Write the report to `~/Learning/youtube-notes/` (create the directory if it doesn't
exist), then display it inline in full. **No save prompt** — the location was fixed by
design, so there is no per-run choice to ask about. Tell Kyle the path.

Filename: `YYYY-MM-DD-<title-slug>-idea-mine.md`. The slug comes from the video title by
an explicit rule: lowercase; every run of characters outside `a–z 0–9` collapsed to a
single `-`; leading and trailing `-` stripped; truncated to 60 characters. The title is
third-party text — the sibling skill's warning about stranger-controlled titles applies
on this side too — so never paste it raw into a path, and confirm the resolved path sits
inside `~/Learning/youtube-notes/` before writing; if it doesn't, stop and say so.

Frontmatter:

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

`speaker:` is sourced, in order of trust: the transcript's own self-identification (an
intro, a "my name is…"), then the video title, then the `uploader` from step 1's metadata
print. The uploader is the *channel*, not necessarily who's talking — an interview posted
on the interviewer's channel mis-attributes by default. When the sources conflict or none
is clear, write the literal quoted value — `speaker: "unknown"` or
`speaker: "uploader: <name>"` — rather than guessing; it's a value, not a new frontmatter
key, and the quoting matters for exactly the colon reason above.

Report body:

```markdown
## Snapshot
- **Video:** [title] — [speaker]
- **Published:** [date or unknown] · **Processed:** [date]
- **Staleness caveat:** [e.g. "Published 7 months ago. Claude Code moves fast —
  every capability claim below is unverified until the capture gate checks the
  ones you pick."]
- **Dedup blind spots:** [category — reason; semicolon-separated, or "none"]

## Overall top picks
[Ordered list of the strongest ideas across all categories — title + artifact
type, one line each. This is the scan-first view.]

## <Artifact type with finds>   (one section per non-empty type)
1. **<Title>** (<overall rank>)
   - **What:** …
   - **Why:** …
   - **Effort:** S|M|L · **Reach:** Global | Project(<name>) · **Dedup:** New |
     Overlaps <item> | Already covered by <item> | Contradicts <item>
   - **Anchor:** "<short verbatim quote>"
   - **Depends on:** [staleness flags, or "nothing version-sensitive"]

## Long tail
[One real Markdown list item per idea, with the anchor forced onto its own
rendered line by a hard line break (trailing backslash):

- <title> — <artifact type> · <effort> · <reach> · <dedup tag> ·
  deps: <staleness flags, or "nothing version-sensitive">\
  "<short quote anchor>"

List items keep twenty tail ideas as twenty separate bullets when the saved
report renders; plain indented lines would soft-wrap back into the one wall
of text this format exists to avoid. The deps sentinel is the top tier's
own wording — it asserts the extractor looked and found nothing, which a
bare dash doesn't. Full recall lives here; nothing found is omitted, and a
tail pick at the capture gate carries the same anchor, effort band, and
staleness flags a top-tier pick does — so step 8 can verify it from the
saved report alone.]
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

1. Never switch the primary checkout. `~/Projects/claude-config`'s working tree **is**
   the machine's live global config — `~/.claude` symlinks into it — so changing its
   branch changes every running session's skills mid-flight. Instead: fetch, then add a
   **temporary git worktree** (under the session scratchpad) on a fresh `docs/`-prefixed
   branch cut from `origin/main`, and do all capture writes there. Concurrent sessions'
   state in the primary checkout is never touched.
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
   artifact is `[Feature]`; an uncertain bet is `[Exploration]`. A Contradicts-tagged pick
   is `[Exploration]` whose vision doc names the conflicting item under **Decisions / open
   questions** — the capture's job is to force that decision, not to pre-decide it.
4. Stage the specific files (never `git add -A` — concurrent sessions leave untracked
   state), commit, push, open the PR, and merge — this is Kyle's standing git workflow.
   The diff is docs-only and non-behavioral, so the adversarial-review skip applies:
   **state the skip and the reason in the merge brief**, never silently. Report the PR
   link and merge SHA.
5. End state: remove the temporary worktree and delete the merged branch. If the primary
   checkout sits on `main`, pull it so the machine runs the just-merged config live; if
   it sits on any other branch (a concurrent session's work), leave it exactly where it
   is and say so in the brief.

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
