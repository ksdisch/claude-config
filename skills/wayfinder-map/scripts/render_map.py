#!/usr/bin/env python3
"""Render a Wayfinder effort (`map.md` + `issues/`) as one self-contained `map.html`.

    python3 render_map.py <effort-dir>              write <effort-dir>/map.html
    python3 render_map.py <effort-dir> -o <file>    write elsewhere
    python3 render_map.py --all [--root <dir>]      every <dir>/.scratch/*/map.md
    python3 render_map.py --all --stale-only        skip maps already newer than their inputs
    python3 render_map.py --hook                    Stop-hook mode: JSON on stdin, never fails

The page is the blocking graph laid out left to right toward the destination,
the takeable tickets as cards, the decisions so far, and the fog. Every count on
it is a scan of the issue files' `Status:` and `Blocked by:` lines; `map.html`
is generated output and never the source of truth.

**Geometry is computed here, the page only draws.** Ranks are longest paths from
the unblocked tickets, order within a column is by barycenter, and the SVG is
emitted with fixed coordinates, so the same files render to the same bytes. The
only date on the page is the newest input file's modification date.

The output obeys the house self-contained-artifact rules: one file, no
`<script>`, no `<link>`, no external URL, system font fallbacks, themed for
light and dark through CSS variables, and every string from the files escaped.

The Stop hook runs this in every repo on the machine, so `--hook` does one glob
and a few stat calls before any parsing, and it always exits 0.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from html import escape
from pathlib import Path

STATES = ("resolved", "claimed", "frontier", "blocked")
TYPES = ("grilling", "prototype", "research", "task")

# Layout constants. Width grows with the label between MIN_W and MAX_W; a label
# longer than three lines at MAX_W is ellipsised, and the full label rides in
# the node's <title> for hover.
CHAR_W = 6.9
PAD_X = 14
HEX_INSET = 12
LINE_H = 16
PAD_Y = 11
MIN_W = 136
MAX_W = 212
MAX_LINES = 3
COL_GAP = 70
ROW_GAP = 16
BOX_PAD = 14
BOX_LABEL_H = 22
MARGIN = 24

BOX_LABEL = "Edge of the map · nothing waits on these"


def warn(message: str) -> None:
    print(f"wayfinder-map: {message}", file=sys.stderr)


class MapError(Exception):
    """A map that cannot be rendered: missing map.md, a cycle."""


# ---------------------------------------------------------------- parsing


def _header_lines(text: str) -> list[str]:
    """Lines before the first `##` heading."""
    out = []
    for line in text.splitlines():
        if line.startswith("## "):
            break
        out.append(line)
    return out


def _field(lines: list[str], name: str) -> str | None:
    prefix = name.lower() + ":"
    for line in lines:
        if line.lower().startswith(prefix):
            return line[len(prefix):].strip()
    return None


def parse_ticket(path: Path) -> dict | None:
    m = re.match(r"(\d+)", path.name)
    if not m:
        warn(f"{path.name}: no leading ticket number, skipped")
        return None
    label = m.group(1)
    text = path.read_text(encoding="utf-8")
    title = path.stem
    for line in text.splitlines():
        if line.startswith("# "):
            title = re.sub(r"^\s*\d+\s*(?::|·|-)\s*", "", line[2:].strip())
            break
    header = _header_lines(text)

    ttype = (_field(header, "Type") or "").lower()
    if not ttype:
        warn(f"{path.name}: no Type line, drawn as grilling")
        ttype = "grilling"
    elif ttype not in TYPES:
        warn(f"{path.name}: unknown Type {ttype!r}, drawn as grilling")
        ttype = "grilling"

    status = (_field(header, "Status") or "open").lower()
    if status not in ("open", "claimed", "resolved"):
        warn(f"{path.name}: unknown Status {status!r}, treated as open")
        status = "open"

    raw = _field(header, "Blocked by") or ""
    blockers = [] if raw.lower() in ("", "none") else [int(n) for n in re.findall(r"\d+", raw)]

    return {"num": int(label), "label": label, "title": title, "type": ttype,
            "status": status, "blocked_by": blockers, "file": path.name}


def _sections(text: str) -> dict[str, str]:
    out: dict[str, list[str]] = {}
    current = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip().lower()
            out[current] = []
        elif current is not None:
            out[current].append(line)
    return {k: "\n".join(v) for k, v in out.items()}


def _bullets(body: str) -> list[str]:
    """Top-level `- ` bullets, continuation lines joined with a space."""
    items: list[list[str]] = []
    in_bullet = False
    for line in body.splitlines():
        if line.startswith("- "):
            items.append([line[2:].strip()])
            in_bullet = True
        elif in_bullet and line.strip() and line[:1].isspace():
            items[-1].append(line.strip())
        elif line.strip():
            in_bullet = False  # an unindented non-bullet line ends the bullet
    return [" ".join(parts) for parts in items]


def parse_map(path: Path) -> dict:
    text = re.sub(r"<!--.*?-->", "", path.read_text(encoding="utf-8"), flags=re.S)
    title = path.parent.name
    for line in text.splitlines():
        if line.startswith("# "):
            title = re.sub(r"^Map:\s*", "", line[2:].strip())
            break
    charted = None
    m = re.search(r"^Charted:\s*(\d{4}-\d{2}-\d{2})", text, flags=re.M)
    if m:
        charted = m.group(1)
    secs = _sections(text)

    destination = ""
    for para in re.split(r"\n\s*\n", secs.get("destination", "").strip()):
        destination = " ".join(l.strip() for l in para.splitlines())
        break

    decisions = []
    for b in _bullets(secs.get("decisions so far", "")):
        dm = re.match(r"\[(.+?)\]\(([^)]*)\):\s*(.*)$", b, flags=re.S)
        if dm:
            decisions.append({"title": dm.group(1), "link": dm.group(2), "gist": dm.group(3)})
        else:
            decisions.append({"title": None, "link": None, "gist": b})

    fog = []
    for b in _bullets(secs.get("not yet specified", "")):
        fm = re.match(r"\*\*(.+?)\*\*\s*(.*)$", b, flags=re.S)
        if fm:
            fog.append({"lead": fm.group(1).rstrip(". "), "rest": fm.group(2), "text": b})
        else:
            fog.append({"lead": b, "rest": "", "text": b})

    return {"title": title, "charted": charted, "destination": destination,
            "decisions": decisions, "fog": fog}


def load_effort(effort: Path) -> tuple[dict, list[dict]]:
    map_md = effort / "map.md"
    if not map_md.is_file():
        raise MapError(f"{effort}: no map.md")
    m = parse_map(map_md)
    tickets = []
    issues = effort / "issues"
    if issues.is_dir():
        for p in sorted(issues.glob("*.md")):
            t = parse_ticket(p)
            if t:
                tickets.append(t)
    known = {t["num"] for t in tickets}
    for t in tickets:
        kept = []
        for b in t["blocked_by"]:
            if b in known:
                kept.append(b)
            else:
                warn(f"{t['file']}: blocker {b:02d} names no ticket file, dropped")
        t["blocked_by"] = sorted(set(kept))
    tickets.sort(key=lambda t: t["num"])
    return m, tickets


# ------------------------------------------------------------- derivation


def derive(m: dict, tickets: list[dict]) -> dict:
    by = {t["num"]: t for t in tickets}
    dependents: dict[int, list[int]] = {n: [] for n in by}
    for t in tickets:
        for b in t["blocked_by"]:
            dependents[b].append(t["num"])

    for t in tickets:
        if t["status"] in ("resolved", "claimed"):
            t["state"] = t["status"]
        elif all(by[b]["status"] == "resolved" for b in t["blocked_by"]):
            t["state"] = "frontier"
        else:
            t["state"] = "blocked"

    rank: dict[int, int] = {}
    visiting: list[int] = []

    def visit(n: int) -> int:
        if n in rank:
            return rank[n]
        if n in visiting:
            # visiting walks blocked → blocker; reverse it so → reads "must resolve before", as on the page
            cycle = (visiting[visiting.index(n):] + [n])[::-1]
            raise MapError("cycle in Blocked by: " + " → ".join(by[c]["label"] for c in cycle))
        visiting.append(n)
        r = 0 if not by[n]["blocked_by"] else 1 + max(visit(b) for b in by[n]["blocked_by"])
        visiting.pop()
        rank[n] = r
        return r

    for n in sorted(by):
        visit(n)

    sinks = {n for n in by if not dependents[n]}
    last = max(rank.values(), default=0)
    for n in sinks:
        rank[n] = last

    columns: list[list[int]] = [[] for _ in range(last + 1)] if by else []
    for n in sorted(by):
        columns[rank[n]].append(n)
    pos: dict[int, float] = {}
    for c, col in enumerate(columns):
        if c == 0:
            col.sort()
        else:
            def bary(n: int, c: int = c) -> tuple[float, int]:
                prev = [b for b in by[n]["blocked_by"] if rank[b] == c - 1]
                nbrs = prev or by[n]["blocked_by"]
                return (sum(pos[b] for b in nbrs) / len(nbrs) if nbrs else float("inf"), n)
            col.sort(key=bary)
        for i, n in enumerate(col):
            pos[n] = float(i)

    fog_links = []
    for f in m["fog"]:
        linked = set()
        for wm in re.finditer(r"waits on\s+((?:\d+(?:\s*(?:,|&|and)\s*)?)+)", f["text"], flags=re.I):
            linked.update(int(x) for x in re.findall(r"\d+", wm.group(1)) if int(x) in by)
        low = f["text"].lower()
        linked.update(n for n, t in by.items() if t["title"].lower() in low)
        fog_links.append(sorted(linked))
    fog_order = sorted(
        range(len(m["fog"])),
        key=lambda i: (sum(pos[n] for n in fog_links[i]) / len(fog_links[i]) if fog_links[i] else float("inf"), i),
    )

    counts = {"tickets": len(tickets)}
    for s in STATES:
        counts[s] = sum(1 for t in tickets if t["state"] == s)
    counts["fog"] = len(m["fog"])

    takeable = [
        {**t, "unblocks": [by[d]["title"] for d in sorted(dependents[t["num"]])]}
        for t in tickets if t["state"] == "frontier"
    ]
    return {"by": by, "dependents": dependents, "rank": rank, "columns": columns,
            "sinks": sinks, "fog_links": fog_links, "fog_order": fog_order,
            "counts": counts, "takeable": takeable}


# ---------------------------------------------------------------- layout


def wrap(label: str, width: float) -> list[str]:
    cpl = max(4, int((width - 2 * PAD_X) / CHAR_W))
    words = label.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        while len(w) > cpl:
            if cur:
                lines.append(cur)
                cur = ""
            lines.append(w[:cpl])
            w = w[cpl:]
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= cpl:
            cur += " " + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) > MAX_LINES:
        last = lines[MAX_LINES - 1]
        lines = lines[:MAX_LINES]
        lines[-1] = (last[: cpl - 1].rstrip() if len(last) >= cpl else last) + "…"
    return lines or [""]


def _box(label: str, kind: str) -> dict:
    pad = PAD_X + (HEX_INSET if kind == "research" else 0)
    w = min(MAX_W, max(MIN_W, len(label) * CHAR_W + 2 * pad))
    lines = wrap(label, w - (2 * HEX_INSET if kind == "research" else 0))
    return {"w": round(w), "h": len(lines) * LINE_H + 2 * PAD_Y, "lines": lines}


def layout(m: dict, d: dict) -> dict:
    nodes: dict = {}
    cols: list[list] = []
    for col in d["columns"]:
        cols.append([])
        for n in col:
            t = d["by"][n]
            label = f"{t['label']} · {t['title']}"
            nodes[("t", n)] = {**_box(label, t["type"]), "label": label}
            cols[-1].append(("t", n))
    if m["fog"]:
        cols.append([])
        for i in d["fog_order"]:
            nodes[("f", i)] = {**_box(m["fog"][i]["lead"], "fog"), "label": m["fog"][i]["lead"]}
            cols[-1].append(("f", i))

    has_box = bool(d["columns"])
    box_col = len(d["columns"]) - 1
    heights = [sum(nodes[k]["h"] for k in col) + ROW_GAP * max(0, len(col) - 1) for col in cols]
    tallest = max(heights, default=0)
    top = MARGIN + BOX_LABEL_H + BOX_PAD

    x = MARGIN
    for c, col in enumerate(cols):
        colw = max((nodes[k]["w"] for k in col), default=0)
        if c == box_col and has_box:
            x += BOX_PAD
        y = top + (tallest - heights[c]) / 2
        for k in col:
            nd = nodes[k]
            nd["x"] = round(x + (colw - nd["w"]) / 2)
            nd["y"] = round(y)
            y += nd["h"] + ROW_GAP
        x += colw + COL_GAP + (BOX_PAD if c == box_col and has_box else 0)

    box = None
    if has_box:
        members = [nodes[k] for k in cols[box_col]]
        bx = min(nd["x"] for nd in members) - BOX_PAD
        by_ = min(nd["y"] for nd in members) - BOX_PAD
        bw = max(nd["x"] + nd["w"] for nd in members) + BOX_PAD - bx
        bh = max(nd["y"] + nd["h"] for nd in members) + BOX_PAD - by_
        box = {"x": bx, "y": by_, "w": bw, "h": bh}

    width = round(max([nd["x"] + nd["w"] for nd in nodes.values()] + [(box["x"] + box["w"]) if box else 0]) + MARGIN) if nodes else 2 * MARGIN
    height = round(top + tallest + BOX_PAD + MARGIN)
    return {"nodes": nodes, "box": box, "width": width, "height": height}


# ---------------------------------------------------------------- drawing


def _inline(text: str) -> str:
    """Escape, then render the three bits of markdown the map files lean on."""
    s = escape(text)
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    return s


def _shape(kind: str, x: int, y: int, w: int, h: int) -> str:
    if kind == "research":
        i = HEX_INSET
        pts = [(x + i, y), (x + w - i, y), (x + w, y + h / 2), (x + w - i, y + h), (x + i, y + h), (x, y + h / 2)]
        return '<polygon class="shape" points="' + " ".join(f"{px:g},{py:g}" for px, py in pts) + '"/>'
    rx = {"prototype": h / 2, "task": 0}.get(kind, 8)
    return f'<rect class="shape" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx:g}"/>'


def _text(nd: dict) -> str:
    cx = nd["x"] + nd["w"] / 2
    first = nd["y"] + nd["h"] / 2 - (len(nd["lines"]) - 1) * LINE_H / 2
    spans = "".join(
        f'<tspan x="{cx:g}" y="{first + i * LINE_H:g}">{escape(line)}</tspan>'
        for i, line in enumerate(nd["lines"])
    )
    return f'<text text-anchor="middle" dominant-baseline="central">{spans}</text>'


def _edge(a: dict, b: dict, cls: str) -> str:
    x1, y1 = a["x"] + a["w"], a["y"] + a["h"] / 2
    x2, y2 = b["x"] - 3, b["y"] + b["h"] / 2
    dx = max(24, (x2 - x1) / 2)
    return (f'<path class="{cls}" d="M{x1:g},{y1:g} C{x1 + dx:g},{y1:g} {x2 - dx:g},{y2:g} {x2:g},{y2:g}" '
            f'marker-end="url(#arrow)"/>')


def render_svg(m: dict, d: dict, lay: dict) -> str:
    nodes = lay["nodes"]
    c = d["counts"]
    aria = (f"Blocking graph: {c['tickets']} tickets — {c['frontier']} takeable, {c['resolved']} resolved, "
            f"{c['claimed']} claimed, {c['blocked']} blocked — and {c['fog']} fog patches")
    out = [f'<svg role="img" aria-label="{escape(aria)}" '
           f'viewBox="0 0 {lay["width"]} {lay["height"]}" width="{lay["width"]}" height="{lay["height"]}">',
           '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
           'orient="auto-start-reverse"><path class="arrowhead" d="M0,0 L10,5 L0,10 z"/></marker></defs>']
    if lay["box"]:
        b = lay["box"]
        out.append(f'<rect class="edge-box" x="{b["x"]}" y="{b["y"]}" width="{b["w"]}" height="{b["h"]}" rx="10"/>')
        out.append(f'<text class="edge-box-label" x="{b["x"] + 2}" y="{b["y"] - 8}">{escape(BOX_LABEL)}</text>')
    for t in sorted(d["by"].values(), key=lambda t: t["num"]):
        for bnum in t["blocked_by"]:
            out.append(_edge(nodes[("t", bnum)], nodes[("t", t["num"])], "edge"))
    for i, links in enumerate(d["fog_links"]):
        for n in links:
            out.append(_edge(nodes[("t", n)], nodes[("f", i)], "edge fog-edge"))
    for t in sorted(d["by"].values(), key=lambda t: t["num"]):
        nd = nodes[("t", t["num"])]
        out.append(f'<g class="node st-{t["state"]} ty-{t["type"]}" data-ticket="{escape(t["label"])}">'
                   f'<title>{escape(nd["label"])}</title>{_shape(t["type"], nd["x"], nd["y"], nd["w"], nd["h"])}'
                   f'{_text(nd)}</g>')
    for i in range(len(m["fog"])):
        nd = nodes[("f", i)]
        out.append(f'<g class="node fog" data-fog="{i + 1}"><title>{escape(nd["label"])}</title>'
                   f'<rect class="shape" x="{nd["x"]}" y="{nd["y"]}" width="{nd["w"]}" height="{nd["h"]}" rx="8"/>'
                   f'{_text(nd)}</g>')
    out.append("</svg>")
    return "\n".join(out)


def _plural(n: int, one: str, many: str) -> str:
    return f"{n} {one if n == 1 else many}"


def headline(c: dict) -> str:
    n = c["tickets"]
    lead = (f"<strong>{_plural(n, 'decision ticket stands', 'decision tickets stand')} "
            f"between here and the destination.</strong>")
    if c["frontier"]:
        clauses = [f"{c['frontier']} takeable now"]
        clauses += [f"{c[s]} {s}" for s in ("resolved", "claimed") if c[s]]
        return f"{lead} {', '.join(clauses)}."
    clauses = [f"{c[s]} {s}" for s in ("blocked", "claimed") if c[s]]
    if not clauses:
        return f"{lead} Nothing is takeable: every ticket is resolved."
    return f"{lead} Nothing is takeable: {', '.join(clauses)}."


def _repo_relative(effort: Path) -> str:
    effort = effort.resolve()
    for parent in [effort, *effort.parents]:
        if (parent / ".git").exists():
            return effort.relative_to(parent).as_posix() or "."
    return effort.name


def _last_changed(effort: Path) -> str:
    files = [effort / "map.md", *sorted((effort / "issues").glob("*.md"))]
    newest = max(f.stat().st_mtime for f in files if f.exists())
    return _dt.date.fromtimestamp(newest).isoformat()


CSS = """
:root {
  --ground: #F3F5F4; --surface: #FFFFFF; --ink: #1C2426; --ink-soft: #4F5B60; --ink-faint: #8A97A0;
  --rule: #D6DDDF; --trail: #1B7F79; --trail-ink: #FFFFFF; --trail-tint: #DDEFEC;
  --resolved: #5C8A3C; --resolved-tint: #DCE9CF; --claimed: #C98A1B; --claimed-tint: #F6E3B5;
  --blocked: #8A97A0; --blocked-tint: #E6EAEC; --blocked-ink: #3B464C;
  --display: Fraunces, Georgia, "Times New Roman", serif;
  --body: "IBM Plex Sans", -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
  --data: "IBM Plex Mono", "SF Mono", Menlo, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --ground: #151A1C; --surface: #1E2528; --ink: #E4E9E8; --ink-soft: #AEB8BC; --ink-faint: #7C8990;
    --rule: #2E383C; --trail: #3FB3AB; --trail-ink: #0F1A19; --trail-tint: #1D3634;
    --resolved: #8DBB6A; --resolved-tint: #2A3A22; --claimed: #E0A43A; --claimed-tint: #3E3220;
    --blocked: #7C8990; --blocked-tint: #262F33; --blocked-ink: #C4CDD1;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --ground: #151A1C; --surface: #1E2528; --ink: #E4E9E8; --ink-soft: #AEB8BC; --ink-faint: #7C8990;
  --rule: #2E383C; --trail: #3FB3AB; --trail-ink: #0F1A19; --trail-tint: #1D3634;
  --resolved: #8DBB6A; --resolved-tint: #2A3A22; --claimed: #E0A43A; --claimed-tint: #3E3220;
  --blocked: #7C8990; --blocked-tint: #262F33; --blocked-ink: #C4CDD1;
}
body { background: var(--ground); color: var(--ink); font-family: var(--body); font-size: 15px; line-height: 1.5; margin: 0; }
main { max-width: 1040px; margin: 0 auto; padding: 40px 24px 56px; display: flex; flex-direction: column; gap: 36px; }
code { font-family: var(--data); font-size: 0.88em; }
.eyebrow { font-family: var(--data); font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink-faint); margin: 0 0 10px; }
h1 { font-family: var(--display); font-weight: 600; font-size: 40px; line-height: 1.1; letter-spacing: -0.01em; margin: 0 0 14px; text-wrap: balance; }
.headline { font-size: 18px; max-width: 62ch; margin: 0; color: var(--ink-soft); text-wrap: pretty; }
.headline strong { color: var(--ink); font-weight: 600; }
.destination { margin: 14px 0 0; max-width: 70ch; font-size: 14px; color: var(--ink-faint); text-wrap: pretty; }
.strip { display: flex; flex-wrap: wrap; gap: 10px; margin: 0; padding: 0; list-style: none; }
.strip li { display: inline-flex; align-items: baseline; gap: 8px; padding: 8px 14px; border-radius: 999px; border: 1px solid var(--rule); background: var(--surface); font-size: 14px; }
.strip .n { font-family: var(--data); font-size: 18px; font-weight: 500; font-variant-numeric: tabular-nums; }
.strip .dot { width: 10px; height: 10px; border-radius: 50%; align-self: center; background: var(--c); }
.strip .fog-dot { background: none; border: 1.5px dashed var(--ink-faint); }
section > h2 { font-family: var(--data); font-size: 12px; font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink-faint); margin: 0 0 12px; display: flex; align-items: center; gap: 12px; }
section > h2::after { content: ""; flex: 1; height: 1px; background: var(--rule); }
figure { margin: 0; background: var(--surface); border: 1px solid var(--rule); border-radius: 6px; padding: 18px 18px 10px; }
.graph-scroll { overflow-x: auto; }
.graph-scroll svg { display: block; max-width: none; font-family: var(--body); font-size: 12.5px; }
figcaption { font-size: 13px; color: var(--ink-soft); margin: 12px 0 0; text-wrap: pretty; }
.legend { display: flex; flex-wrap: wrap; gap: 6px 22px; margin: 10px 0 0; padding: 12px 0 0; border-top: 1px solid var(--rule); font-size: 13px; color: var(--ink-soft); list-style: none; }
.legend li { display: inline-flex; align-items: center; gap: 7px; }
.sw { width: 14px; height: 14px; border-radius: 3px; background: var(--c); }
.sw.fog { background: none; border: 1.5px dashed var(--ink-faint); }
.sh { width: 22px; height: 14px; border: 1.5px solid var(--ink-faint); box-sizing: border-box; }
.sh.grilling { border-radius: 5px; }
.sh.prototype { border-radius: 999px; }
.sh.task { border-radius: 0; }
.sh.research { border: none; background: var(--ink-faint); clip-path: polygon(20% 0, 80% 0, 100% 50%, 80% 100%, 20% 100%, 0 50%); }
.node text { fill: var(--ink); }
.node .shape { stroke-width: 1.5px; }
.st-frontier .shape { fill: var(--trail); stroke: var(--trail); stroke-width: 2px; }
.st-frontier text { fill: var(--trail-ink); font-weight: 600; }
.st-resolved .shape { fill: var(--resolved-tint); stroke: var(--resolved); }
.st-claimed .shape { fill: var(--claimed-tint); stroke: var(--claimed); }
.st-blocked .shape { fill: var(--blocked-tint); stroke: var(--blocked); stroke-width: 1px; }
.st-blocked text { fill: var(--blocked-ink); }
.node.fog .shape { fill: none; stroke: var(--ink-faint); stroke-dasharray: 5 4; }
.node.fog text { fill: var(--ink-faint); }
.edge { fill: none; stroke: var(--ink-faint); stroke-width: 1.3px; }
.fog-edge { stroke-dasharray: 5 4; }
.arrowhead { fill: var(--ink-faint); }
.edge-box { fill: none; stroke: var(--trail); stroke-width: 1.2px; stroke-dasharray: 2 3; }
.edge-box-label { fill: var(--trail); font-family: var(--data); font-size: 11px; letter-spacing: 0.04em; }
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 14px; margin: 0; padding: 0; list-style: none; }
.card { background: var(--surface); border: 1px solid var(--rule); border-top: 3px solid var(--trail); border-radius: 6px; padding: 14px 14px 12px; display: flex; flex-direction: column; gap: 8px; }
.card .num { font-family: var(--data); font-size: 12px; color: var(--ink-faint); display: flex; justify-content: space-between; align-items: center; }
.card .type { font-size: 11px; letter-spacing: 0.06em; text-transform: uppercase; padding: 2px 7px; border-radius: 3px; background: var(--trail-tint); color: var(--trail); font-weight: 600; }
.card .title { font-weight: 600; font-size: 15px; line-height: 1.3; margin: 0; text-wrap: balance; }
.card .meta { font-size: 13px; color: var(--ink-soft); margin: 0; }
.card .meta span { color: var(--ink-faint); margin-right: 6px; }
.none { margin: 0; color: var(--ink-soft); }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; align-items: start; }
.stack { display: flex; flex-direction: column; gap: 10px; margin: 0; padding: 0; list-style: none; }
.decision { background: var(--surface); border: 1px solid var(--rule); border-left: 3px solid var(--resolved); border-radius: 6px; padding: 14px 16px; }
.decision .num { font-family: var(--data); font-size: 12px; color: var(--ink-faint); }
.decision .title { font-weight: 600; margin: 2px 0 6px; }
.decision p { margin: 0; font-size: 14px; color: var(--ink-soft); overflow-wrap: anywhere; }
.fog-item { border: 1.5px dashed var(--ink-faint); border-radius: 6px; padding: 10px 14px; font-size: 14px; color: var(--ink-soft); }
.fog-item .head { display: flex; justify-content: space-between; gap: 12px; }
.fog-item b { color: var(--ink); font-weight: 600; }
.fog-item .waits { color: var(--ink-faint); font-size: 13px; white-space: nowrap; }
.fog-item p { margin: 4px 0 0; font-size: 13px; overflow-wrap: anywhere; }
footer { font-family: var(--data); font-size: 12px; color: var(--ink-faint); border-top: 1px solid var(--rule); padding-top: 14px; overflow-wrap: anywhere; }
@media (max-width: 860px) { .two { grid-template-columns: 1fr; } h1 { font-size: 32px; } }
"""

LEGEND = (
    '<ul class="legend" aria-label="Legend">'
    '<li><span class="sw" style="--c: var(--trail)"></span>frontier · takeable now</li>'
    '<li><span class="sw" style="--c: var(--resolved)"></span>resolved</li>'
    '<li><span class="sw" style="--c: var(--claimed)"></span>claimed</li>'
    '<li><span class="sw" style="--c: var(--blocked)"></span>blocked</li>'
    '<li><span class="sw fog"></span>fog · not yet specified</li>'
    '<li><span class="sh grilling"></span>grilling</li>'
    '<li><span class="sh prototype"></span>prototype</li>'
    '<li><span class="sh research"></span>research</li>'
    '<li><span class="sh task"></span>task</li>'
    "</ul>"
)


def render_html(effort: Path) -> str:
    m, tickets = load_effort(effort)
    d = derive(m, tickets)
    lay = layout(m, d)
    c = d["counts"]

    eyebrow = ["wayfinder:map"]
    if m["charted"]:
        eyebrow.append(f"charted {m['charted']}")
    eyebrow.append(f"tickets last changed {_last_changed(effort)}")

    parts = [
        "<!doctype html>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{escape(m['title'])}</title>",
        f"<style>{CSS}</style>",
        "<main>",
        "<header>",
        f'<p class="eyebrow">{escape(" · ".join(eyebrow))}</p>',
        f"<h1>{escape(m['title'])}</h1>",
        f'<p class="headline">{headline(c)}</p>',
    ]
    if m["destination"]:
        parts.append(f'<p class="destination">{_inline(m["destination"])}</p>')
    parts.append("</header>")

    chips = [f'<li><span class="n">{c["tickets"]}</span> tickets</li>']
    for s, var, word in (("resolved", "resolved", "resolved"), ("claimed", "claimed", "claimed"),
                         ("frontier", "trail", "on the frontier"), ("blocked", "blocked", "blocked")):
        chips.append(f'<li data-count="{s}"><span class="dot" style="--c: var(--{var})"></span>'
                     f'<span class="n">{c[s]}</span> {word}</li>')
    chips.append(f'<li data-count="fog"><span class="dot fog-dot"></span><span class="n">{c["fog"]}</span> in the fog</li>')
    parts.append(f'<ul class="strip" aria-label="Ticket status counts">{"".join(chips)}</ul>')

    parts += [
        "<section>", "<h2>The route</h2>", "<figure>",
        f'<div class="graph-scroll">{render_svg(m, d, lay)}</div>',
        LEGEND,
        '<figcaption>An arrow means "must resolve before". A dashed arrow means the fog patch waits on that '
        "ticket to become a ticket of its own. Out-of-scope items are not drawn; they never graduate.</figcaption>",
        "</figure>", "</section>",
    ]

    parts.append("<section><h2>Takeable now · one per session</h2>")
    if d["takeable"]:
        cards = []
        for t in d["takeable"]:
            meta = (f'<p class="meta"><span>Unblocks</span>{escape(" · ".join(t["unblocks"]))}</p>'
                    if t["unblocks"] else "")
            cards.append(f'<li class="card"><div class="num">{escape(t["label"])} '
                         f'<span class="type">{escape(t["type"])}</span></div>'
                         f'<p class="title">{escape(t["title"])}</p>{meta}</li>')
        parts.append(f'<ul class="cards">{"".join(cards)}</ul>')
    else:
        parts.append(f'<p class="none">Nothing is takeable right now: '
                     f'{c["blocked"]} blocked, {c["claimed"]} claimed.</p>')
    parts.append("</section>")

    side = []
    if m["decisions"]:
        items = []
        for dec in m["decisions"]:
            num = ""
            if dec["link"]:
                lm = re.search(r"(?:^|/)(\d+)[^/]*$", dec["link"])
                if lm and int(lm.group(1)) in d["by"]:
                    t = d["by"][int(lm.group(1))]
                    num = f'<div class="num">{escape(t["label"])} · {escape(t["type"])}</div>'
            title = f'<p class="title">{_inline(dec["title"])}</p>' if dec["title"] else ""
            items.append(f'<li class="decision">{num}{title}<p>{_inline(dec["gist"])}</p></li>')
        side.append(f'<section><h2>Decisions so far</h2><ul class="stack">{"".join(items)}</ul></section>')
    if m["fog"]:
        items = []
        for i, f in enumerate(m["fog"]):
            links = d["fog_links"][i]
            waits = (f'<span class="waits">waits on {escape(", ".join(d["by"][n]["label"] for n in links))}</span>'
                     if links else "")
            rest = f"<p>{_inline(f['rest'])}</p>" if f["rest"] else ""
            items.append(f'<li class="fog-item"><div class="head"><b>{_inline(f["lead"])}</b>{waits}</div>{rest}</li>')
        side.append(f'<section><h2>Not yet specified</h2><ul class="stack">{"".join(items)}</ul></section>')
    if side:
        parts.append(f'<div class="two">{"".join(side)}</div>')

    parts.append(f"<footer>Generated from {escape(_repo_relative(effort))}/map.md and "
                 f"{_plural(len(tickets), 'file', 'files')} under issues/ · every count above is a scan of the "
                 "Status and Blocked-by lines</footer>")
    parts.append("</main>")
    return "\n".join(parts) + "\n"


# -------------------------------------------------------------------- CLI


def is_stale(effort: Path) -> bool:
    out = effort / "map.html"
    if not out.exists():
        return True
    built = out.stat().st_mtime
    inputs = [effort / "map.md", *(effort / "issues").glob("*.md")]
    return any(p.stat().st_mtime >= built for p in inputs if p.exists())


def render_one(effort: Path, out: Path | None = None) -> Path:
    html = render_html(effort)
    target = out or effort / "map.html"
    target.write_text(html, encoding="utf-8")
    return target


def render_all(root: Path, stale_only: bool) -> tuple[list[Path], int]:
    written, failures = [], 0
    for map_md in sorted(root.glob(".scratch/*/map.md")):
        effort = map_md.parent
        if stale_only and not is_stale(effort):
            continue
        try:
            written.append(render_one(effort))
        except MapError as e:
            warn(str(e))
            failures += 1
    return written, failures


def run_hook(stdin_text: str) -> int:
    try:
        payload = json.loads(stdin_text)
        root = Path(payload.get("cwd") or ".")
    except (ValueError, AttributeError) as e:
        warn(f"--hook: unreadable stdin ({e}); nothing rendered")
        return 0
    try:
        written, _ = render_all(root, stale_only=True)
    except Exception as e:  # a hook must never block a stop
        warn(f"--hook: {e}")
        return 0
    for p in written:
        print(p)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Render a Wayfinder map as a self-contained map.html.")
    ap.add_argument("effort", nargs="?", type=Path, help="effort directory holding map.md and issues/")
    ap.add_argument("-o", "--output", type=Path, help="write here instead of <effort>/map.html")
    ap.add_argument("--all", action="store_true", help="every <root>/.scratch/*/map.md")
    ap.add_argument("--root", type=Path, default=Path("."), help="repo root for --all (default: cwd)")
    ap.add_argument("--stale-only", action="store_true", help="with --all: skip maps newer than their inputs")
    ap.add_argument("--hook", action="store_true", help="Stop-hook mode: JSON on stdin, always exits 0")
    args = ap.parse_args(argv)

    if args.hook:
        return run_hook(sys.stdin.read())
    if args.all:
        if args.effort or args.output:
            warn("--all takes no effort directory and no -o")
            return 1
        written, failures = render_all(args.root, args.stale_only)
        for p in written:
            print(p)
        return 1 if failures else 0
    if not args.effort:
        warn("give an effort directory, or --all")
        return 1
    try:
        print(render_one(args.effort, args.output))
    except MapError as e:
        warn(str(e))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
