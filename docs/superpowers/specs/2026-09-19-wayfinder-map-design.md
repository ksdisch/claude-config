# wayfinder-map — a generated picture of a Wayfinder map

Date: 2026-09-19
Branch: `feat/wayfinder-map`
Visual reference: [`2026-09-19-wayfinder-map-reference.html`](2026-09-19-wayfinder-map-reference.html), the hand-built page Kyle approved. The generator reproduces its structure and styling; where this document and the reference page disagree, this document wins.

## Problem

A Wayfinder map on the local-markdown tracker is a `map.md` plus one issue file per ticket. The tracker doc says native blocking exists so "the human sees what's takeable without opening the map", and local-markdown is the fallback that loses exactly that: the frontier is a scan of `Blocked by:` lines. A hand-drawn diagram restores it but goes stale the moment the next session resolves a ticket.

## Solution

A skill, `wayfinder-map`, whose core is a deterministic Python script that reads an effort directory and writes one self-contained `map.html` beside `map.md`: the blocking graph laid out left to right toward the destination, the takeable tickets as cards, the decisions so far, and the fog. Regeneration is wired into the workflow twice: as a step in the Wayfinding operations every session reads, and as a Stop hook that re-renders any stale map at the end of every turn. Publishing stays a skill step, on request, to one stable Artifact link per effort.

## Decisions (grilled 2026-09-19)

| Question | Decision |
|---|---|
| Trigger | Instruction in the Wayfinding operations **and** a command-type Stop hook running the script in stale-only mode. The hook catches Bash-driven edits a per-tool hook would miss; the instruction covers machines and cloud sessions without the hook. |
| Output | A self-contained `map.html` beside `map.md`, graph laid out in Python as inline SVG. No mermaid, no external resource. |
| Publishing | On request only, from the skill, not the script. The Artifact URL is recorded in the map's Notes as a `Rendered map:` line so later sessions republish to the same link. |

## Components

```
skills/wayfinder-map/
├── SKILL.md
└── scripts/
    ├── render_map.py         # effort dir in, map.html out; --all, --stale-only, --hook
    ├── install_hook.py       # one-shot, idempotent Stop-hook install into ~/.claude/settings.json
    └── tests/
        ├── __init__.py
        ├── test_render_map.py
        └── test_install_hook.py
```

Plus three wiring edits (see *Wiring*) and the index row and playbook card in the same commit as the skill.

### `render_map.py`

Pure Python 3, standard library only, no third-party imports. Same conventions as `skills/architecture-viewer/scripts/render_map.py`: geometry computed in Python, the page only draws; every string from the files inserted escaped; unittest under `scripts/tests/`.

**Inputs.** An effort directory holding `map.md` and `issues/`.

From each `issues/NN-<slug>.md`:

- **Number**: the leading digits of the filename.
- **Title**: the first H1, with a leading `NN:`, `NN ·`, or `NN -` prefix stripped.
- **Type**: the `Type:` line before the first `##` heading. Missing → drawn with the grilling shape and a warning on stderr.
- **Status**: the `Status:` line before the first `##`. Missing → `open`. A value other than `open`, `claimed`, `resolved` → treated as `open` with a warning.
- **Blocked by**: the `Blocked by:` line before the first `##`. `None`, empty, or absent → no blockers. Otherwise the numbers in the list, comma or space separated. A number that names no ticket file → dropped with a warning.

From `map.md`:

- **Title**: the H1, with a leading `Map:` stripped.
- **Charted**: a `Charted: YYYY-MM-DD` line, if present.
- **Destination**: the first paragraph under `## Destination` (up to the first blank line). Later paragraphs, such as an italic caveat, are not rendered.
- **Decisions so far**: each bullet under `## Decisions so far`. A bullet of the form `- [Title](link): gist` yields title and gist; any other bullet is shown verbatim as its gist with no title.
- **Not yet specified**: each bullet under `## Not yet specified`. A bullet opening with `**Lead.**` yields lead and rest; otherwise the whole bullet is the lead.
- **Out of scope** is read and ignored. It is never drawn: out-of-scope items never graduate.
- **Notes** is ignored by the script. The `Rendered map:` line there belongs to the skill.

HTML comments in `map.md` are stripped before parsing.

**Derivation.**

- A ticket's **state** is `resolved` or `claimed` when its Status says so. Otherwise it is `frontier` when every blocker is resolved (trivially, when it has none) and `blocked` when any blocker is not. Claimed wins over blocked: a claimed ticket is being worked, whatever its blockers say.
- **Edges** run from blocker to blocked ticket.
- **Rank** is the longest path from the unblocked tickets, which sit at rank 0. That puts every takeable ticket in the left column without any pinning. A cycle is an error (exit 1, cycle named); a Wayfinder map is a DAG by construction.
- **Edge of the map**: tickets that no other ticket lists as a blocker. They are moved to the last ticket column and boxed with the label "Edge of the map · nothing waits on these". Because a ticket at the last rank can have no dependents, that column then holds exactly the sinks. A frontier ticket that is also a sink lands in the box, coloured frontier; accepted.
- **Fog**: each Not-yet-specified bullet is a dashed node in one final column right of the edge box. It gets a dashed edge from a ticket when the bullet contains `waits on` followed by ticket numbers, or contains a ticket's full title (case-insensitive). No match → drawn unattached. Multiple matches → multiple edges.
- **Order within a column**: sources by ticket number; every later column by the barycenter of its neighbours in the previous column, ties by number. Deterministic.
- **Takeable now**: the frontier tickets by number, each with the titles of the tickets it directly unblocks.
- **Counts**: total tickets, resolved, claimed, frontier, blocked, fog.

**The page.** The reference page's structure and CSS, generated:

1. Eyebrow: `wayfinder:map · charted <date> · tickets last changed <date>` (charted omitted if absent; the last-changed date is the newest input file's modification date, so the file carries no wall-clock time and the same files render to the same bytes).
2. H1: the map title. Headline: "`N` decision tickets stand between here and the destination. `F` takeable now, `R` resolved, `C` claimed." Zero-valued clauses are omitted; when the frontier is empty the headline says so instead ("Nothing is takeable: `B` blocked, `C` claimed").
3. The Destination paragraph, quiet, in the map's own words.
4. Status strip: the counts as chips.
5. The route: the SVG graph in a horizontally scrolling container, the legend (state colours, type shapes, fog), and a caption stating the two edge meanings.
6. Takeable now: cards by number with type chip, title, and "Unblocks" line (omitted when nothing depends on it). If the frontier is empty, one line saying so replaces the cards.
7. Decisions so far and Not yet specified, side by side. Either section is omitted when empty; nothing is padded.
8. Footer: the effort directory's path relative to the repo root and the sentence "every count above is a scan of the Status and Blocked-by lines".

**SVG.** Columns left to right; node width from label length within a min and max; labels broken into at most three lines of `<tspan>` on word boundaries, the last line ellipsised if the title is longer; node height from line count. Shapes by type: grilling rounded rectangle, prototype pill, research hexagon, task square-cornered rectangle; fog a dashed rounded rectangle with no fill. Fill and stroke by state through CSS classes on the tokens, so the graph follows the page's light and dark themes. Edges are cubic curves from the source's right edge to the target's left edge with a marker arrowhead; fog edges dashed. `role="img"` and an `aria-label` carrying the counts. The `viewBox` is sized to the content with margin for the outermost labels.

**Self-contained.** No `<link>`, no `<script>`, no external URL of any kind. System font stacks, not Google Fonts: display `Fraunces, Georgia, "Times New Roman", serif`; body `"IBM Plex Sans", -apple-system, "Segoe UI", Helvetica, Arial, sans-serif`; data `"IBM Plex Mono", "SF Mono", Menlo, monospace`. The page must read correctly on the fallbacks alone. Three-state theme tokens exactly as the reference page: full palette on bare `:root`, redefined under `prefers-color-scheme: dark` guarded by `:root:not([data-theme="light"])`, and again under `:root[data-theme="dark"]`; `body` paints its background from a token.

**CLI.**

```
render_map.py <effort-dir>              write <effort-dir>/map.html; print its path
render_map.py <effort-dir> -o <file>    write elsewhere
render_map.py --all [--root <dir>]      every <dir>/.scratch/*/map.md; <dir> defaults to the cwd
render_map.py --all --stale-only        skip an effort whose map.html is newer than map.md and every issues/*.md
render_map.py --hook                    read the Stop-hook JSON on stdin; its cwd is --root; implies --all --stale-only
```

Exit 0 on success, 1 on a usage or parse error (missing `map.md`, a cycle), with the reason on stderr. `--hook` always exits 0 and prints nothing unless it rendered something, in which case it prints one line per file written; malformed stdin is reported on stderr and still exits 0. A hook must never block a stop.

### `install_hook.py`

One-shot, idempotent. Reads `~/.claude/settings.json` (path overridable with `--settings` for tests), copies it to `~/.claude/hooks/backups/settings.json.<YYYYMMDD-HHMMSS>` first, then appends to `hooks.Stop` (creating `hooks` or `Stop` if absent) the entry

```json
{ "hooks": [ { "type": "command",
               "command": "python3 ~/.claude/skills/wayfinder-map/scripts/render_map.py --hook" } ] }
```

unless an entry with that exact command already exists, in which case it changes nothing and says so. Writes atomically (temp file then rename), two-space indent, other keys untouched. `--dry-run` prints the resulting Stop array and writes nothing. Exit 0 both ways; exit 1 if the settings file is not valid JSON, touching nothing.

### `SKILL.md`

Frontmatter `name: wayfinder-map`; description with the triggers (`/wayfinder-map`, "draw the map", "show me the map", "render the route", "what's on the frontier") and a NOT-for line (visual-summary for what a session or branch did; architecture-viewer for module structure; wayfinder itself for working a ticket). Body:

- **Parse `$ARGUMENTS`**: an effort path, or none. With none, the one `.scratch/*/map.md` in the repo; with several, the most recently modified, named before anything else. `--no-publish` renders only.
- **Render**: run `render_map.py <effort-dir>`; the file lands beside `map.md`.
- **Publish** (unless `--no-publish`): look in the map's `## Notes` for a line `- **Rendered map**: <url>`. If present, read that artifact first (the Artifact tool refuses a publish to an artifact this conversation has not read) and republish to its URL. If absent, publish fresh with favicon `🗺️`, a title that is the map's title, and append the line to Notes. The link is per effort and stable.
- **Deliver**: three lines. The local path, the link, and the frontier in one sentence.
- **Install the hook once per machine**: `python3 ~/.claude/skills/wayfinder-map/scripts/install_hook.py`. A section, not a step: the skill never runs the installer on its own.
- Runs at low effort; the judgment is nil.

### Wiring

1. **Global `CLAUDE.md`**, in *Local-Markdown Issue Tracker: Tickets Index*, after the paragraph beginning "`/wayfinder` does not consume this manifest": a **Route render** paragraph. Every claim, resolve, add-ticket, or wire-blocking step in a wayfinder effort is followed by `python3 ~/.claude/skills/wayfinder-map/scripts/render_map.py <effort-dir>`; the Stop hook is the backstop, not the mechanism sessions rely on; `map.html` is generated output, never hand-edited, and never the source of truth; to see or share it, invoke `wayfinder-map`. And one sentence telling `/setup-matt-pocock-skills` to append the same bullet to a new repo's `docs/agents/issue-tracker.md`.
2. **This repo is not a wayfinder host**, so nothing changes in claude-config's own tracker doc.
3. **`ff-2026-league-site/docs/agents/issue-tracker.md`**, under *Wayfinding operations*, one bullet: **Render**: after claim, resolve, or a new ticket, run the renderer; `map.html` beside `map.md` is generated and never edited by hand. Separate PR in that repo, from a worktree so the dirty reconcile branch stays untouched.
4. **Index row and playbook card** for `wayfinder-map`, in the Global Skills table next to `visual-summary` and `architecture-viewer`, in the same commit as the skill.

### Tests

`unittest`, run with `python3 -m unittest discover -s skills/wayfinder-map/scripts/tests`. Fixtures are built in a temp directory by the tests themselves.

- Parsing: prefix stripping in titles; missing Status → open; `Blocked by: None`, absent, and a list; an unknown blocker number dropped with a warning; HTML comments ignored.
- Derivation: unblocked → frontier; a claimed blocker keeps its dependents blocked; a claimed ticket with unresolved blockers reads claimed; sinks land in the last ticket column; a cycle exits 1 naming it.
- Fog: link by `waits on 07`, link by title, unattached, two links from one bullet.
- Render: on a six-ticket fixture the HTML contains each title exactly once inside the SVG, the strip counts equal the derived counts, there is no `http` anywhere in the file, `<title>` is the map title, empty sections are absent, and two renders are byte-identical.
- Stale-only: missing `map.html` renders; an older one renders; a newer one is skipped.
- Hook mode: valid stdin renders and exits 0; malformed stdin exits 0 with a stderr line.
- Installer: installs once into a temp settings file, a second run changes nothing, a backup is written, `--dry-run` writes nothing, invalid JSON exits 1 untouched.

## Out of scope

- A mermaid export.
- A PostToolUse hook, or publishing from the hook.
- Any change to the vendored `wayfinder` skill or its upstream template.
- Any interplay with `tickets.md`; wayfinder efforts stay out of that manifest.
- Cross-effort views. One effort, one page.

## Risks

- **The Stop hook runs in every repo on this machine.** It must be fast when there is nothing to do: one `glob` for `.scratch/*/map.md`, then stat calls. No imports beyond the standard library, no work before the stale check.
- **`~/.claude/settings.json` is machine-local and hand-maintained.** The installer backs up first, writes atomically, and refuses to touch a file it cannot parse.
- **Layout on a wide map.** Twenty-plus tickets across five ranks will scroll horizontally; that is the container's job, and the page body never scrolls sideways.

## Build plan

Plan and prose in this Fable session; the mechanical bulk to one subagent.

1. Subagent (Opus 5, high): `render_map.py`, `install_hook.py`, and both test files in the worktree, from this document. Done when the tests pass and rendering `ff-2026-league-site/.scratch/06-team-manager-pages` produces a page that reads like the reference.
2. This session: `SKILL.md`, the index row, the playbook card, the global `CLAUDE.md` paragraph; then the ff repo's tracker-doc bullet in its own worktree and PR.
3. This session: render the team-and-manager-pages effort, publish to the existing artifact URL, record the `Rendered map:` line in its Notes, install the hook on this machine, and confirm one end-of-turn regeneration.

**Run-config note.** Builder subagent: `claude-opus-5`, effort `high`: a well-specified build with real layout judgment in it. Dispatched from this session with `model` and effort pinned, not a fresh terminal, because the build is mid-size and decomposable and the plan is this file.
