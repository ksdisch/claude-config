---
name: wayfinder-map
description: Draw a Wayfinder effort's map as one self-contained HTML page — the blocking graph laid out left to right toward the destination, the takeable tickets as cards, the decisions so far, and the fog — generated from `map.md` and the issue files by a deterministic script, written as `map.html` beside `map.md`, and published to one stable Artifact link per effort. Use when Kyle types /wayfinder-map, or says "draw the map", "show me the map", "render the route", "what's on the frontier", "what's takeable on the map" — even if he doesn't name the skill. NOT for what a session or branch did (visual-summary), a repo's module structure (architecture-viewer), or working a ticket on the map (wayfinder itself).
---

# wayfinder-map — see the route instead of scanning Blocked-by lines

On the local-markdown tracker a Wayfinder map is a `map.md` plus one issue file per
ticket, and the frontier is a scan of `Blocked by:` lines. `render_map.py` does that
scan and draws it. The page is generated output: **never hand-edit `map.html`, and
never treat it as the source of truth** — the issue files are.

Low effort; there is no judgment in this skill. The script decides everything the page says.

## 1. Parse `$ARGUMENTS`

- An effort directory (the one holding `map.md` and `issues/`), or nothing.
- With nothing: the one `.scratch/*/map.md` under the repo root. With several, take the
  most recently modified `map.md` and **name it first** ("Rendering `.scratch/06-…`; two
  other maps exist: …") before doing anything else.
- `--no-publish`: render only; skip step 3.

## 2. Render

```bash
python3 ~/.claude/skills/wayfinder-map/scripts/render_map.py <effort-dir>
```

It writes `<effort-dir>/map.html` and prints the path. Warnings on stderr (a ticket
with no `Type:`, a blocker that names no ticket file) go to Kyle verbatim — they are
defects in the map files, not in the page. Exit 1 means a missing `map.md` or a cycle in
the blocking lines; report the reason and stop.

## 3. Publish (unless `--no-publish`)

One stable Artifact link per effort, recorded in the map itself.

- Look in `map.md`'s `## Notes` for a line `- **Rendered map**: <url>`.
- **Present:** read that artifact first with the Artifact tool's `read` action (a
  publish to an artifact this conversation hasn't read is refused), then publish
  `map.html` with `url` set to it.
- **Absent:** publish `map.html` fresh (icon `map`; the page's `<title>` is already the
  map's title), then append `- **Rendered map**: <url>` to `## Notes`. That one-line
  edit to `map.md` is the only change this skill makes to the map files.

## 4. Deliver

Three lines, nothing more:

1. The local path to `map.html`.
2. The Artifact link (or "not published").
3. The frontier in one sentence — the takeable tickets by number and title, glossed.

## Keeping it fresh

Wayfinder sessions run the renderer after every claim, resolve, new ticket, or change
to blocking (the global `CLAUDE.md`'s *Route render* paragraph). A Stop hook is the
backstop: at the end of every turn it re-renders any `map.html` under
`<cwd>/.scratch/*/` older than its inputs, and does nothing otherwise.

**Install the hook once per machine** (a section, not a step: this skill never runs the
installer on its own):

```bash
python3 ~/.claude/skills/wayfinder-map/scripts/install_hook.py --dry-run   # look first
python3 ~/.claude/skills/wayfinder-map/scripts/install_hook.py
```

It backs up `~/.claude/settings.json`, appends one command-type Stop hook, and changes
nothing if the hook is already there. The hook never publishes; publishing stays here.
