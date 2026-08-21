#!/usr/bin/env python3
"""Render an `arch-graph/v1` document as one self-contained, clickable HTML map.

    python3 render_map.py architecture.json -o constellation-map.html

Modules are nodes, dependencies are arrows pointing from dependent to
dependency, and a module with submodules can be drilled into — one level, which
is v0's scope. "Open the code" is a `file:line` reference you click to copy, not
embedded source, so the map can never disagree with the tree about what a
function says.

**Geometry is computed here, drawing happens in the page.** Layout is a layered
DAG pass (longest-path ranks, then barycenter ordering) run once per view in
Python, where it is deterministic and testable; the embedded script only turns
those coordinates into SVG and swaps views. Nothing in the page recomputes a
position, so what a test asserts is what a reader sees.

The output obeys the house self-contained-artifact rules: one file, no external
resource of any kind, themed for light and dark through CSS variables, and every
piece of text from the graph inserted with `textContent` rather than markup.

Validate before rendering — `validate_graph.py` is what guarantees the file:line
references in this map resolve.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCHEMA = "arch-graph/v1"

# Edge kinds the stylesheet draws differently. Anything else keeps the default
# stroke, which is what the schema promises for a kind outside the recommended
# vocabulary. Decided here rather than in the page so a test can assert the class
# an edge actually gets, instead of asserting that a constant is spelled a
# certain way in the emitted JavaScript.
STYLED_KINDS = ("type-only", "runtime")

# Layout constants. Node height is fixed so ranks read as clean bands; width
# grows with the label because a truncated module name is a module you cannot
# identify.
NODE_H = 62
MIN_W = 168
MAX_W = 320
CHAR_W = 8.2
LABEL_PAD = 46
COL_GAP = 44
RANK_GAP = 118
MARGIN = 40
BARYCENTER_PASSES = 4


def die(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def node_width(*labels: str) -> float:
    widest = max((len(label) for label in labels if label), default=0)
    return max(MIN_W, min(MAX_W, widest * CHAR_W + LABEL_PAD))


def back_edges(ids: list[str], pairs: list[tuple[str, str]]) -> set[tuple[str, str]]:
    """Edges that close a cycle, found by iterative DFS in sorted order.

    Removing these leaves a DAG to rank. They are not dropped from the drawing —
    they are the most interesting arrows on the page — only from the layering,
    which has no meaning on a cyclic graph.
    """
    successors: dict[str, list[str]] = {node: [] for node in ids}
    for source, target in pairs:
        if source in successors and target in successors and target not in successors[source]:
            successors[source].append(target)
    for node in successors:
        successors[node].sort()

    WHITE, GRAY, BLACK = 0, 1, 2
    colour = {node: WHITE for node in ids}
    found: set[tuple[str, str]] = set()

    for start in ids:
        if colour[start] != WHITE:
            continue
        colour[start] = GRAY
        stack: list[tuple[str, int]] = [(start, 0)]
        while stack:
            node, position = stack[-1]
            if position < len(successors[node]):
                stack[-1] = (node, position + 1)
                nxt = successors[node][position]
                if colour[nxt] == GRAY:
                    found.add((node, nxt))
                elif colour[nxt] == WHITE:
                    colour[nxt] = GRAY
                    stack.append((nxt, 0))
                continue
            colour[node] = BLACK
            stack.pop()
    return found


def rank_nodes(ids: list[str], pairs: list[tuple[str, str]]) -> dict[str, int]:
    """Longest-path rank per node: a dependency always sits below its dependents.

    `pairs` must already have back edges removed, so this is a DAG and Kahn's
    algorithm terminates. Any node the queue never reaches would mean a cycle
    survived; it is ranked 0 rather than dropped, because a node missing from
    the drawing is worse than one drawn in the wrong band.
    """
    rank = {node: 0 for node in ids}
    indegree = {node: 0 for node in ids}
    successors: dict[str, list[str]] = {node: [] for node in ids}
    for source, target in sorted(set(pairs)):
        if source in successors and target in indegree:
            successors[source].append(target)
            indegree[target] += 1

    queue = sorted(node for node in ids if indegree[node] == 0)
    while queue:
        node = queue.pop(0)
        for target in successors[node]:
            rank[target] = max(rank[target], rank[node] + 1)
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
                queue.sort()
    return rank


def order_layers(
    layers: dict[int, list[str]], pairs: list[tuple[str, str]]
) -> dict[int, list[str]]:
    """Reduce edge crossings by barycentre ordering, alternating down and up.

    A fixed pass count with name-based tie-breaking keeps the result
    deterministic — the same graph must render identically every run, or a diff
    of two maps is unreadable.
    """
    preds: dict[str, list[str]] = {}
    succs: dict[str, list[str]] = {}
    for source, target in pairs:
        preds.setdefault(target, []).append(source)
        succs.setdefault(source, []).append(target)

    ordered = {rank: list(nodes) for rank, nodes in layers.items()}
    ranks = sorted(ordered)

    def position_map() -> dict[str, int]:
        return {node: index for nodes in ordered.values() for index, node in enumerate(nodes)}

    for iteration in range(BARYCENTER_PASSES):
        sweep = ranks[1:] if iteration % 2 == 0 else list(reversed(ranks[:-1]))
        neighbours = preds if iteration % 2 == 0 else succs
        for rank in sweep:
            # Recomputed per layer, not per pass: a sweep reorders layers one at a
            # time, and a barycentre taken from the previous layer's stale
            # positions is a barycentre of where the nodes used to be.
            positions = position_map()
            current = list(ordered[rank])
            index_of = {node: index for index, node in enumerate(current)}

            barycentre: dict[str, float] = {}
            for node in current:
                related = [positions[n] for n in neighbours.get(node, []) if n in positions]
                if related:
                    barycentre[node] = sum(related) / len(related)

            # Only nodes with neighbours in the adjacent layer move, and they move
            # only among the slots they already occupy. A node with no neighbours
            # has no barycentre — substituting its index would mix two different
            # scales and let an unconnected node drift past connected ones for no
            # reason a reader could see.
            movable = sorted(barycentre, key=lambda n: (barycentre[n], index_of[n], n))
            slots = [index for index, node in enumerate(current) if node in barycentre]
            for slot, node in zip(slots, movable):
                current[slot] = node
            ordered[rank] = current
    return ordered


def layout(nodes: list[dict], edges: list[dict]) -> dict:
    """Place a view's nodes and route its edges.

    `nodes` are `{id, label, sublabel, …}`; `edges` are `{from, to, …}`. Returns
    the same lists enriched with geometry, plus the canvas size.
    """
    ids = [node["id"] for node in nodes]
    known = set(ids)
    pairs = [(e["from"], e["to"]) for e in edges if e["from"] in known and e["to"] in known]

    reversed_edges = back_edges(ids, pairs)
    forward = [pair for pair in pairs if pair not in reversed_edges]
    rank = rank_nodes(ids, forward)

    layers: dict[int, list[str]] = {}
    for node in sorted(ids):
        layers.setdefault(rank[node], []).append(node)
    layers = order_layers(layers, forward)

    by_id = {node["id"]: node for node in nodes}
    widths = {
        node["id"]: node_width(node["label"], node.get("sublabel", "")) for node in nodes
    }

    # Lay each rank out left to right, then centre the ranks on each other so
    # the shape reads as a stack rather than a left-aligned ragged column.
    rows: dict[int, list[tuple[str, float, float]]] = {}
    widest = 0.0
    for rank_index in sorted(layers):
        x = 0.0
        row = []
        for node_id in layers[rank_index]:
            row.append((node_id, x, widths[node_id]))
            x += widths[node_id] + COL_GAP
        row_width = max(0.0, x - COL_GAP)
        widest = max(widest, row_width)
        rows[rank_index] = row

    for rank_index, row in rows.items():
        row_width = sum(w for _, _, w in row) + COL_GAP * max(0, len(row) - 1)
        offset = MARGIN + (widest - row_width) / 2
        y = MARGIN + rank_index * (NODE_H + RANK_GAP)
        for node_id, x, width in row:
            node = by_id[node_id]
            node["x"] = round(offset + x, 1)
            node["y"] = round(y, 1)
            node["w"] = round(width, 1)
            node["h"] = NODE_H
            node["rank"] = rank_index

    # Fan out parallel edges between the same pair so a second `kind` between two
    # modules is visible rather than hidden under the first.
    seen: dict[tuple[str, str], int] = {}
    routed: list[tuple[dict, dict, dict, int, bool, float, int]] = []
    centre = MARGIN + widest / 2
    for edge in edges:
        source, target = by_id.get(edge["from"]), by_id.get(edge["to"])
        if source is None or target is None:
            continue
        index = seen.get((edge["from"], edge["to"]), 0)
        seen[(edge["from"], edge["to"])] = index + 1
        cyclic = (edge["from"], edge["to"]) in reversed_edges

        # An edge that skips a rank would otherwise be drawn straight through
        # whatever sits on the rank between — which reads as a dependency on that
        # module rather than past it. Bow it sideways instead, away from the
        # middle of the drawing so it leaves by the outside.
        span = target.get("rank", 0) - source.get("rank", 0)
        if cyclic:
            bow = 90.0 + index * 20
        elif span > 1:
            bow = 40.0 + 26 * (span - 2) + index * 16
        else:
            bow = 0.0
        if cyclic:
            side = 1 if target["x"] >= source["x"] else -1
        else:
            side = 1 if source["x"] + source["w"] / 2 >= centre else -1
        routed.append((edge, source, target, index, cyclic, bow, side))

    # Reserve the space those bows need before drawing them, or the outermost
    # curve is simply clipped by the canvas edge.
    pad_left = max([bow for *_, bow, side in routed if side < 0], default=0.0)
    pad_right = max([bow for *_, bow, side in routed if side > 0], default=0.0)
    for node in nodes:
        if "x" in node:
            node["x"] = round(node["x"] + pad_left, 1)

    width = round(widest + 2 * MARGIN + pad_left + pad_right, 1)
    height = (
        round(MARGIN * 2 + (max(rows) + 1) * NODE_H + max(rows) * RANK_GAP, 1)
        if rows
        else 2 * MARGIN
    )

    placed = [
        {
            **edge,
            "cycle": cyclic,
            "cls": edge_classes(edge.get("kind"), cyclic),
            "d": edge_path(source, target, index, cyclic, bow, side),
        }
        for edge, source, target, index, cyclic, bow, side in routed
    ]

    return {"nodes": nodes, "edges": placed, "width": width, "height": height}


def edge_classes(kind: object, cyclic: bool) -> str:
    """The `class` attribute an edge is drawn with.

    `cycle` is listed last and its CSS rule comes last at equal specificity, so a
    runtime edge that also closes a cycle draws as a cycle edge. That is the
    intended precedence: the cycle is the more urgent thing to see.
    """
    classes = ["edge"]
    if isinstance(kind, str) and kind in STYLED_KINDS:
        classes.append(kind)
    if cyclic:
        classes.append("cycle")
    return " ".join(classes)


def edge_path(
    source: dict, target: dict, index: int, cyclic: bool, bow: float, side: int
) -> str:
    """A cubic bezier from the dependent to the dependency.

    A forward edge leaves the bottom of its source and enters the top of its
    target, bowed sideways by `bow` when it has a rank to clear. A back edge runs
    the other way — up the page — and is bowed as well as dashed, so a cycle is
    recognisable from shape alone and not only from colour.
    """
    nudge = index * 16
    sx = round(source["x"] + source["w"] / 2 + nudge, 1)
    tx = round(target["x"] + target["w"] / 2 + nudge, 1)

    if not cyclic:
        sy = round(source["y"] + source["h"], 1)
        ty = round(target["y"], 1)
        lift = max(30.0, (ty - sy) / 2)
        return (
            f"M {sx},{sy} C {round(sx + side * bow, 1)},{round(sy + lift, 1)} "
            f"{round(tx + side * bow, 1)},{round(ty - lift, 1)} {tx},{ty}"
        )

    sy = round(source["y"], 1)
    ty = round(target["y"] + target["h"], 1)
    return (
        f"M {sx},{sy} C {round(sx + side * bow, 1)},{round(sy - 60, 1)} "
        f"{round(tx + side * bow, 1)},{round(ty + 60, 1)} {tx},{ty}"
    )


def descendants(module_id: str, children: dict[str, list[str]]) -> set[str]:
    """A module and everything nested inside it."""
    found = {module_id}
    stack = [module_id]
    while stack:
        for child in children.get(stack.pop(), []):
            if child not in found:
                found.add(child)
                stack.append(child)
    return found


def ancestor_in(module_id: str, members: set[str], parents: dict[str, str | None]) -> str | None:
    """The member of `members` that contains `module_id`, or None."""
    seen, current = set(), module_id
    while current is not None and current not in seen:
        if current in members:
            return current
        seen.add(current)
        current = parents.get(current)
    return None


def roll_up(edges: list[dict], members: set[str], parents: dict[str, str | None]) -> list[dict]:
    """Collapse the document's edges onto one view's node set.

    Two submodules of the same parent produce no edge in the parent's view —
    that dependency is internal to it, and drawing it at this level would claim
    the parent depends on itself.
    """
    merged: dict[tuple[str, str, str], dict] = {}
    for edge in edges:
        source = ancestor_in(edge["from"], members, parents)
        target = ancestor_in(edge["to"], members, parents)
        if source is None or target is None or source == target:
            continue
        kind = edge.get("kind") or "import"
        key = (source, target, kind)
        entry = merged.setdefault(
            key, {"from": source, "to": target, "kind": kind, "count": 0, "via": []}
        )
        entry["count"] += edge.get("count") or len(edge.get("evidence") or []) or 1
        if edge["from"] != source or edge["to"] != target:
            entry["via"].append({"from": edge["from"], "to": edge["to"]})
    ordered = sorted(merged.values(), key=lambda e: (e["from"], e["to"], e["kind"]))
    for edge in ordered:
        edge["via"] = edge["via"][:6]
    return ordered


def build_views(doc: dict) -> tuple[dict, dict]:
    """Every drillable view, plus the per-module panel data.

    View `""` is the root — the top-level modules. A module with submodules also
    gets a view keyed by its id, holding those submodules and the dependencies
    among them. v0 draws no arrows leaving a drilled-in view; where they go is in
    the panel instead, named submodule by submodule.
    """
    modules = doc["modules"]
    by_id = {module["id"]: module for module in modules}
    parents = {module["id"]: module.get("parent") for module in modules}
    children: dict[str, list[str]] = {}
    for module in modules:
        parent = module.get("parent")
        if parent is not None:
            children.setdefault(parent, []).append(module["id"])
    for kids in children.values():
        kids.sort()

    edges = doc.get("edges") or []

    def node_for(module_id: str) -> dict:
        module = by_id[module_id]
        bits = []
        if module.get("layer"):
            bits.append(str(module["layer"]))
        if module.get("file_count"):
            count = module["file_count"]
            bits.append(f"{count} file" + ("" if count == 1 else "s"))
        return {
            "id": module_id,
            "label": module.get("name") or module_id,
            "sublabel": " · ".join(bits),
            "has_children": bool(children.get(module_id)),
            "layer": module.get("layer") or "",
        }

    views: dict[str, dict] = {}
    tops = sorted(m["id"] for m in modules if m.get("parent") is None)
    members = set(tops)
    views[""] = {
        "title": doc["repo"].get("name") or "repository",
        "parent_of": None,
        **layout([node_for(m) for m in tops], roll_up(edges, members, parents)),
    }

    for module_id in sorted(children):
        kids = children[module_id]
        member_set = set(kids)
        views[module_id] = {
            "title": by_id[module_id].get("name") or module_id,
            "parent_of": module_id,
            **layout([node_for(k) for k in kids], roll_up(edges, member_set, parents)),
        }

    panels: dict[str, dict] = {}
    for module in modules:
        module_id = module["id"]
        inside = descendants(module_id, children)
        outbound, inbound = [], []
        for edge in edges:
            source_in, target_in = edge["from"] in inside, edge["to"] in inside
            if source_in and not target_in:
                outbound.append(
                    {
                        "other": edge["to"],
                        "via": edge["from"] if edge["from"] != module_id else "",
                        "kind": edge.get("kind") or "import",
                        "count": edge.get("count") or len(edge.get("evidence") or []) or 1,
                        "evidence": (edge.get("evidence") or [])[:3],
                    }
                )
            elif target_in and not source_in:
                inbound.append(
                    {
                        "other": edge["from"],
                        "via": edge["to"] if edge["to"] != module_id else "",
                        "kind": edge.get("kind") or "import",
                        "count": edge.get("count") or len(edge.get("evidence") or []) or 1,
                        "evidence": (edge.get("evidence") or [])[:3],
                    }
                )
        panels[module_id] = {
            "id": module_id,
            "name": module.get("name") or module_id,
            "path": module.get("path") or module_id,
            "layer": module.get("layer") or "",
            "summary": module.get("summary") or "",
            "file_count": module.get("file_count"),
            "parent": module.get("parent"),
            "children": children.get(module_id, []),
            "anchors": module.get("anchors") or [],
            "outbound": sorted(outbound, key=lambda e: (e["other"], e["kind"])),
            "inbound": sorted(inbound, key=lambda e: (e["other"], e["kind"])),
        }

    return views, panels


CSS = """
:root {
  color-scheme: light dark;
  --bg: #f7f7f5; --surface: #ffffff; --surface-2: #f0efec; --border: #d9d7d1;
  --text: #23211d; --muted: #6d6a63; --accent: #2f6f5e; --accent-soft: #dbeae4;
  --edge: #8d8a82; --edge-strong: #2f6f5e; --cycle: #b4462f; --cycle-soft: #f6e2dc;
  --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  --sans: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #16181a; --surface: #1e2124; --surface-2: #272b2f; --border: #383d42;
    --text: #e6e3dd; --muted: #9aa0a6; --accent: #6fd0ad; --accent-soft: #24413a;
    --edge: #6d747b; --edge-strong: #6fd0ad; --cycle: #f08a70; --cycle-soft: #452a24;
  }
}
:root[data-theme="light"] {
  --bg: #f7f7f5; --surface: #ffffff; --surface-2: #f0efec; --border: #d9d7d1;
  --text: #23211d; --muted: #6d6a63; --accent: #2f6f5e; --accent-soft: #dbeae4;
  --edge: #8d8a82; --edge-strong: #2f6f5e; --cycle: #b4462f; --cycle-soft: #f6e2dc;
}
:root[data-theme="dark"] {
  --bg: #16181a; --surface: #1e2124; --surface-2: #272b2f; --border: #383d42;
  --text: #e6e3dd; --muted: #9aa0a6; --accent: #6fd0ad; --accent-soft: #24413a;
  --edge: #6d747b; --edge-strong: #6fd0ad; --cycle: #f08a70; --cycle-soft: #452a24;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--text);
  font-family: var(--sans); font-size: 15px; line-height: 1.5;
}
header.bar {
  display: flex; flex-wrap: wrap; gap: .75rem 1rem; align-items: baseline;
  padding: .85rem 1.1rem; border-bottom: 1px solid var(--border);
  background: var(--surface); position: sticky; top: 0; z-index: 5;
}
header.bar h1 { font-size: 1.05rem; margin: 0; font-weight: 650; }
header.bar .meta { color: var(--muted); font-size: .82rem; font-family: var(--mono); }
header.bar .spacer { flex: 1 1 auto; }
button {
  font: inherit; color: inherit; background: var(--surface-2);
  border: 1px solid var(--border); border-radius: 7px;
  padding: .28rem .62rem; cursor: pointer;
}
button:hover { border-color: var(--accent); }
button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
nav.crumbs { display: flex; align-items: center; gap: .4rem; font-size: .88rem; }
nav.crumbs .sep { color: var(--muted); }
nav.crumbs .here { font-weight: 620; }
main { display: flex; align-items: stretch; min-height: calc(100vh - 56px); }
/* `min-width: 0` is load-bearing: a flex item defaults to `min-width: auto`, so
   the canvas refuses to shrink below the SVG's intrinsic width, pushes `main`
   wider than the viewport, and takes the whole page sideways with it — clipping
   the panel and the header buttons. The scrollbar belongs to the canvas, never
   to the body. */
#canvas-wrap { flex: 1 1 auto; min-width: 0; overflow: auto; padding: 1rem; }
svg { display: block; }
.node rect {
  fill: var(--surface); stroke: var(--border); stroke-width: 1.4;
  rx: 10; filter: drop-shadow(0 1px 1px rgba(0,0,0,.12));
}
.node.has-children rect { stroke-dasharray: none; stroke-width: 2; }
.node .name { font-size: 14px; font-weight: 640; fill: var(--text); }
.node .sub { font-size: 11px; fill: var(--muted); font-family: var(--mono); }
.node .drill { font-size: 12px; fill: var(--accent); }
.node { cursor: pointer; }
.node:hover rect, .node:focus-visible rect { stroke: var(--accent); }
.node.selected rect { stroke: var(--accent); stroke-width: 2.6; fill: var(--accent-soft); }
.node.dim { opacity: .28; }
.edge { fill: none; stroke: var(--edge); stroke-width: 1.6; }
.edge.type-only { stroke-dasharray: 2 4; }
/* Dash-dot, and heavier: a runtime edge crosses a process boundary, which is
   the one kind an import parser cannot see and the most consequential kind to
   mistake for a plain import. */
.edge.runtime { stroke-dasharray: 10 3 2 3; stroke-width: 2; }
.edge.cycle { stroke: var(--cycle); stroke-width: 2.2; stroke-dasharray: 7 4; }
.edge.lit { stroke: var(--edge-strong); stroke-width: 2.6; }
.edge.cycle.lit { stroke: var(--cycle); }
.edge.dim { opacity: .12; }
aside#panel {
  flex: 0 0 clamp(280px, 32vw, 400px); min-width: 0; border-left: 1px solid var(--border);
  background: var(--surface); overflow-y: auto; max-height: calc(100vh - 56px);
  position: sticky; top: 56px; padding: 1rem 1.1rem 3rem;
}
aside#panel h2 { font-size: 1.02rem; margin: .2rem 0 .1rem; }
aside#panel h3 {
  font-size: .72rem; text-transform: uppercase; letter-spacing: .07em;
  color: var(--muted); margin: 1.2rem 0 .4rem; font-weight: 650;
}
.path { font-family: var(--mono); font-size: .8rem; color: var(--muted); word-break: break-all; }
.summary { margin: .5rem 0 0; }
.pill {
  display: inline-block; font-size: .72rem; padding: .1rem .45rem; border-radius: 999px;
  background: var(--accent-soft); color: var(--text); border: 1px solid var(--border);
  font-family: var(--mono);
}
ul.plain { list-style: none; margin: 0; padding: 0; }
ul.plain li { padding: .3rem 0; border-bottom: 1px solid var(--border); font-size: .88rem; }
ul.plain li:last-child { border-bottom: none; }
.ref {
  font-family: var(--mono); font-size: .78rem; background: var(--surface-2);
  border: 1px solid var(--border); border-radius: 6px; padding: .1rem .35rem;
  cursor: pointer; display: inline-block; margin: .15rem .2rem .15rem 0;
}
.ref:hover { border-color: var(--accent); }
.ref.copied { background: var(--accent-soft); border-color: var(--accent); }
.muted { color: var(--muted); }
.small { font-size: .82rem; }
.findings {
  margin: 0; padding: .75rem 1.1rem; background: var(--cycle-soft);
  border-bottom: 1px solid var(--border); font-size: .88rem;
}
.findings.none { background: var(--surface-2); }
.findings code { font-family: var(--mono); }
.legend {
  display: flex; flex-wrap: wrap; gap: .2rem 1rem; padding: .5rem 1.1rem;
  border-top: 1px solid var(--border); font-size: .78rem; color: var(--muted);
  background: var(--surface);
}
.legend svg { display: inline-block; vertical-align: middle; }
.scroll-note { color: var(--muted); font-size: .78rem; }
@media (max-width: 800px) {
  main { flex-direction: column; }
  aside#panel { position: static; flex: 1 1 auto; max-height: none; border-left: none;
    border-top: 1px solid var(--border); }
}
"""

JS = r"""
(function () {
  const wrap = document.getElementById('canvas-wrap');
  const panel = document.getElementById('panel');
  const crumbs = document.getElementById('crumbs');
  const SVG_NS = 'http://www.w3.org/2000/svg';
  let currentView = '';
  let selected = null;
  let zoom = 1;

  const el = (tag, attrs, text) => {
    const node = document.createElementNS(SVG_NS, tag);
    for (const key in attrs) node.setAttribute(key, attrs[key]);
    if (text !== undefined) node.textContent = text;
    return node;
  };
  const h = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  };

  function defs() {
    const d = el('defs', {});
    [['arrow', 'var(--edge)'], ['arrow-lit', 'var(--edge-strong)'], ['arrow-cycle', 'var(--cycle)']]
      .forEach(([id, fill]) => {
        const marker = el('marker', {
          id, viewBox: '0 0 10 10', refX: '9', refY: '5',
          markerWidth: '7', markerHeight: '7', orient: 'auto-start-reverse'
        });
        marker.appendChild(el('path', { d: 'M 0 0 L 10 5 L 0 10 z', fill }));
        d.appendChild(marker);
      });
    return d;
  }

  function drawView(viewId) {
    const view = VIEWS[viewId];
    if (!view) return;
    currentView = viewId;
    wrap.textContent = '';

    const svg = el('svg', {
      viewBox: `0 0 ${view.width} ${view.height}`,
      width: Math.round(view.width * zoom),
      height: Math.round(view.height * zoom),
      role: 'img',
      'aria-label': `Dependency map of ${view.title}`
    });
    svg.appendChild(defs());

    const edgeLayer = el('g', { class: 'edges' });
    view.edges.forEach((edge, index) => {
      const path = el('path', {
        d: edge.d,
        class: edge.cls,
        'marker-end': edge.cycle ? 'url(#arrow-cycle)' : 'url(#arrow)',
        'data-from': edge.from,
        'data-to': edge.to,
        'data-index': index
      });
      const title = el('title', {});
      title.textContent =
        `${edge.from} → ${edge.to} (${edge.kind}${edge.count ? ', ' + edge.count + ' site' + (edge.count === 1 ? '' : 's') : ''})`
        + (edge.cycle ? ' — part of a cycle' : '');
      path.appendChild(title);
      edgeLayer.appendChild(path);
    });
    svg.appendChild(edgeLayer);

    const nodeLayer = el('g', { class: 'nodes' });
    view.nodes.forEach(node => {
      const classes = ['node'];
      if (node.has_children) classes.push('has-children');
      const group = el('g', {
        class: classes.join(' '),
        transform: `translate(${node.x}, ${node.y})`,
        tabindex: '0',
        role: 'button',
        'data-id': node.id,
        'aria-label': node.label + (node.has_children ? ', has submodules' : '')
      });
      group.appendChild(el('rect', { width: node.w, height: node.h }));
      group.appendChild(el('text', { class: 'name', x: 14, y: 26 }, node.label));
      if (node.sublabel) group.appendChild(el('text', { class: 'sub', x: 14, y: 45 }, node.sublabel));
      if (node.has_children) {
        group.appendChild(el('text', { class: 'drill', x: node.w - 20, y: 26 }, '▸'));
      }
      const title = el('title', {});
      title.textContent = (PANELS[node.id] && PANELS[node.id].summary) || node.id;
      group.appendChild(title);
      nodeLayer.appendChild(group);
    });
    svg.appendChild(nodeLayer);
    wrap.appendChild(svg);

    drawCrumbs();
    if (selected && !view.nodes.some(n => n.id === selected)) selected = null;
    highlight();
    // Only a real selection fills the panel. Falling back to "the first node"
    // put a module's details on screen while nothing on the map was highlighted,
    // which reads as the map having lost track of itself.
    showPanel(selected || view.parent_of || null);
  }

  function drawCrumbs() {
    crumbs.textContent = '';
    const trail = [];
    let cursor = currentView;
    while (cursor) {
      trail.unshift(cursor);
      cursor = (PANELS[cursor] && PANELS[cursor].parent) || '';
    }
    const root = h('button', null, GRAPH.repo.name || 'repository');
    root.addEventListener('click', () => { selected = null; drawView(''); });
    crumbs.appendChild(root);
    trail.forEach((id, index) => {
      crumbs.appendChild(h('span', 'sep', '›'));
      const last = index === trail.length - 1;
      if (last) {
        crumbs.appendChild(h('span', 'here', (PANELS[id] && PANELS[id].name) || id));
      } else {
        const step = h('button', null, (PANELS[id] && PANELS[id].name) || id);
        step.addEventListener('click', () => drawView(id));
        crumbs.appendChild(step);
      }
    });
  }

  function highlight() {
    const nodes = wrap.querySelectorAll('.node');
    const edges = wrap.querySelectorAll('.edge');
    if (!selected) {
      nodes.forEach(n => n.classList.remove('dim', 'selected'));
      edges.forEach(e => {
        e.classList.remove('dim', 'lit');
        e.setAttribute('marker-end',
          e.classList.contains('cycle') ? 'url(#arrow-cycle)' : 'url(#arrow)');
      });
      return;
    }
    const touching = new Set([selected]);
    edges.forEach(edge => {
      const from = edge.getAttribute('data-from');
      const to = edge.getAttribute('data-to');
      const related = from === selected || to === selected;
      edge.classList.toggle('lit', related);
      edge.classList.toggle('dim', !related);
      // The arrowhead is a marker, not a stroke, so a CSS class cannot recolour
      // it — swap the marker itself or a highlighted edge keeps a grey head.
      const cyclic = edge.classList.contains('cycle');
      edge.setAttribute('marker-end',
        cyclic ? 'url(#arrow-cycle)' : (related ? 'url(#arrow-lit)' : 'url(#arrow)'));
      if (related) { touching.add(from); touching.add(to); }
    });
    nodes.forEach(node => {
      const id = node.getAttribute('data-id');
      node.classList.toggle('selected', id === selected);
      node.classList.toggle('dim', !touching.has(id));
    });
  }

  // Deliberately no window.prompt fallback: a modal dialog blocks the page, and
  // this page may be running inside an artifact frame where that is worse than a
  // failed copy. A failure says so on the button instead.
  function legacyCopy(text) {
    const field = document.createElement('textarea');
    field.value = text;
    field.setAttribute('readonly', '');
    field.style.position = 'fixed';
    field.style.top = '-1000px';
    field.style.opacity = '0';
    document.body.appendChild(field);
    field.select();
    let copied = false;
    try { copied = document.execCommand('copy'); } catch (err) { copied = false; }
    document.body.removeChild(field);
    return copied;
  }

  function reference(location) {
    const label = location.file + ':' + location.line;
    const button = h('button', 'ref', label);
    button.title = location.label || location.text || 'Copy this reference';
    button.addEventListener('click', () => {
      const flash = (message, ok) => {
        if (ok) button.classList.add('copied');
        button.textContent = message;
        setTimeout(() => { button.textContent = label; button.classList.remove('copied'); }, 1200);
      };
      const fallback = () => {
        const copied = legacyCopy(label);
        flash(copied ? 'copied ✓' : 'copy failed', copied);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(label).then(() => flash('copied ✓', true), fallback);
      } else {
        fallback();
      }
    });
    return button;
  }

  function relationList(entries, direction) {
    const list = h('ul', 'plain');
    if (!entries.length) {
      list.appendChild(h('li', 'muted small', direction === 'out'
        ? 'Depends on nothing outside itself.'
        : 'Nothing outside depends on it.'));
      return list;
    }
    entries.forEach(entry => {
      const item = h('li');
      const line = h('div');
      const arrow = h('span', null, direction === 'out' ? '→ ' : '← ');
      line.appendChild(arrow);
      const name = h('strong', null, entry.other);
      line.appendChild(name);
      const meta = h('span', 'muted small', '  ' + entry.kind
        + (entry.count ? ' · ' + entry.count + ' site' + (entry.count === 1 ? '' : 's') : ''));
      line.appendChild(meta);
      item.appendChild(line);
      if (entry.via) item.appendChild(h('div', 'muted small', 'via ' + entry.via));
      const refs = h('div');
      (entry.evidence || []).forEach(location => refs.appendChild(reference(location)));
      if (refs.childNodes.length) item.appendChild(refs);
      list.appendChild(item);
    });
    return list;
  }

  function showPanel(moduleId) {
    const info = PANELS[moduleId];
    panel.textContent = '';
    if (!info) {
      panel.appendChild(h('p', 'muted', 'Select a module to see what it is and where its dependencies run.'));
      return;
    }
    panel.appendChild(h('h2', null, info.name));
    panel.appendChild(h('div', 'path', info.path));
    const tags = h('div');
    if (info.layer) tags.appendChild(h('span', 'pill', info.layer));
    if (info.file_count) {
      tags.appendChild(document.createTextNode(' '));
      tags.appendChild(h('span', 'pill', info.file_count + ' file' + (info.file_count === 1 ? '' : 's')));
    }
    if (tags.childNodes.length) panel.appendChild(tags);
    panel.appendChild(h('p', 'summary', info.summary));

    if (info.children.length) {
      const drill = h('button', null, 'Look inside → ' + info.children.length + ' submodules');
      drill.addEventListener('click', () => { selected = null; drawView(info.id); });
      const holder = h('p');
      holder.appendChild(drill);
      panel.appendChild(holder);
    }

    if ((info.anchors || []).length) {
      panel.appendChild(h('h3', null, 'Start reading here'));
      const list = h('ul', 'plain');
      info.anchors.forEach(anchor => {
        const item = h('li');
        item.appendChild(reference(anchor));
        if (anchor.label) item.appendChild(h('div', 'muted small', anchor.label));
        list.appendChild(item);
      });
      panel.appendChild(list);
    }

    panel.appendChild(h('h3', null, 'Depends on'));
    panel.appendChild(relationList(info.outbound, 'out'));
    panel.appendChild(h('h3', null, 'Depended on by'));
    panel.appendChild(relationList(info.inbound, 'in'));
  }

  wrap.addEventListener('click', event => {
    const group = event.target.closest('.node');
    if (!group) { selected = null; highlight(); return; }
    const id = group.getAttribute('data-id');
    if (selected === id && PANELS[id] && PANELS[id].children.length) {
      selected = null;
      drawView(id);
      return;
    }
    selected = id;
    highlight();
    showPanel(id);
  });

  wrap.addEventListener('keydown', event => {
    const group = event.target.closest && event.target.closest('.node');
    if (!group) return;
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      group.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    }
  });

  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    if (selected) { selected = null; highlight(); return; }
    if (currentView) drawView((PANELS[currentView] && PANELS[currentView].parent) || '');
  });

  document.getElementById('zoom-in').addEventListener('click', () => {
    zoom = Math.min(2, zoom + 0.15); drawView(currentView);
  });
  document.getElementById('zoom-out').addEventListener('click', () => {
    zoom = Math.max(0.4, zoom - 0.15); drawView(currentView);
  });
  document.getElementById('zoom-reset').addEventListener('click', () => {
    zoom = 1; drawView(currentView);
  });
  document.getElementById('theme').addEventListener('click', () => {
    const root = document.documentElement;
    const dark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const now = root.getAttribute('data-theme') || (dark ? 'dark' : 'light');
    root.setAttribute('data-theme', now === 'dark' ? 'light' : 'dark');
  });

  drawView('');
})();
"""


def escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def embed(data: object) -> str:
    """JSON safe to sit inside a `<script>` element.

    `</script>` anywhere in a summary or a quoted source line would end the
    block early and spill the rest of the graph into the page as markup, so the
    three characters that can start a tag are escaped at the JSON level, where
    they stay valid JSON and decode back to themselves.
    """
    return (
        json.dumps(data, separators=(",", ":"), sort_keys=True)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )


def findings_html(doc: dict, views: dict) -> str:
    """The banner that makes the map worth opening: what the structure says."""
    root = views[""]
    cyclic_pairs = [(e["from"], e["to"]) for e in root["edges"] if e["cycle"]]
    notes = [n for n in (doc.get("notes") or []) if str(n).strip()]

    parts = []
    if cyclic_pairs:
        listed = ", ".join(
            f"<code>{escape(a)}</code> ⇄ <code>{escape(b)}</code>" for a, b in cyclic_pairs
        )
        parts.append(
            f"<strong>{len(cyclic_pairs)} dependency cycle"
            f"{'' if len(cyclic_pairs) == 1 else 's'} at the top level:</strong> {listed}. "
            f"Dashed red arrows run against the layering."
        )
    else:
        parts.append(
            "<strong>No cycles at the top level.</strong> Every arrow runs downward, so the "
            "modules stack into layers."
        )
    if notes:
        parts.append(
            "<strong>Extraction notes:</strong> "
            + " ".join(escape(note) for note in notes)
        )

    css_class = "findings" if cyclic_pairs else "findings none"
    return f'<p class="{css_class}">' + "<br>".join(parts) + "</p>"


def render(doc: dict, title: str | None = None) -> str:
    views, panels = build_views(doc)
    repo = doc.get("repo") or {}
    name = repo.get("name") or "repository"
    page_title = title or f"{name} — architecture map"

    commit = repo.get("commit")
    generated = repo.get("generated")
    meta_bits = [f"{len(doc['modules'])} modules", f"{len(doc.get('edges') or [])} edges"]
    if commit:
        meta_bits.append(f"@ {commit[:12]}")
    else:
        meta_bits.append("uncommitted tree")
    if generated:
        meta_bits.append(str(generated))

    legend = (
        '<div class="legend">'
        '<span><svg width="34" height="10" aria-hidden="true">'
        '<line x1="0" y1="5" x2="30" y2="5" stroke="var(--edge)" stroke-width="1.6"/></svg>'
        " depends on (arrow points at the dependency)</span>"
        '<span><svg width="34" height="10" aria-hidden="true">'
        '<line x1="0" y1="5" x2="30" y2="5" stroke="var(--edge)" stroke-width="1.6" '
        'stroke-dasharray="2 4"/></svg> type-only</span>'
        '<span><svg width="34" height="10" aria-hidden="true">'
        '<line x1="0" y1="5" x2="30" y2="5" stroke="var(--edge)" stroke-width="2" '
        'stroke-dasharray="10 3 2 3"/></svg> runtime (crosses a process boundary)</span>'
        '<span><svg width="34" height="10" aria-hidden="true">'
        '<line x1="0" y1="5" x2="30" y2="5" stroke="var(--cycle)" stroke-width="2.2" '
        'stroke-dasharray="7 4"/></svg> part of a cycle</span>'
        "<span>▸ has submodules — click it twice, or use <em>Look inside</em></span>"
        '<span class="scroll-note">Esc clears the selection, then steps back up a level.</span>'
        "</div>"
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(page_title)}</title>
<style>{CSS}</style>
</head>
<body>
<header class="bar">
  <h1>{escape(name)} — architecture</h1>
  <nav class="crumbs" id="crumbs" aria-label="Drill-down trail"></nav>
  <span class="spacer"></span>
  <span class="meta">{escape(' · '.join(meta_bits))}</span>
  <button id="zoom-out" aria-label="Zoom out">−</button>
  <button id="zoom-reset">100%</button>
  <button id="zoom-in" aria-label="Zoom in">+</button>
  <button id="theme">Theme</button>
</header>
{findings_html(doc, views)}
<main>
  <div id="canvas-wrap"></div>
  <aside id="panel" aria-live="polite"></aside>
</main>
{legend}
<script>
const GRAPH = {embed({"repo": repo, "roots": doc.get("roots") or [], "excluded": doc.get("excluded") or []})};
const VIEWS = {embed(views)};
const PANELS = {embed(panels)};
</script>
<script>{JS}</script>
</body>
</html>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("graph", help="path to a validated architecture.json")
    parser.add_argument("-o", "--out", required=True, help="path to write the HTML map to")
    parser.add_argument("--title", help="override the page title")
    args = parser.parse_args(argv)

    try:
        doc = json.loads(Path(args.graph).read_text())
    except OSError as exc:
        die(f"cannot read {args.graph}: {exc}")
    except json.JSONDecodeError as exc:
        die(f"{args.graph} is not valid JSON: {exc}")

    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        die(
            f"{args.graph} is not an {SCHEMA} document — run validate_graph.py first; "
            f"rendering an unvalidated graph is how an unresolvable file:line reaches a reader."
        )
    if not isinstance(doc.get("modules"), list) or not doc["modules"]:
        die(f"{args.graph} has no modules to draw.")

    html = render(doc, args.title)
    try:
        out = Path(args.out)
        # The skill's documented default is `docs/architecture/` in the target
        # repo, which does not exist the first time a repo is mapped. Creating it
        # is the difference between the happy path working and a traceback.
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
    except OSError as exc:
        die(f"cannot write the map to {args.out}: {exc}")
    drillable = len({m.get("parent") for m in doc["modules"] if m.get("parent")})
    edge_count = len(doc.get("edges") or [])
    print(
        f"map written to {args.out} — {len(doc['modules'])} modules, "
        f"{edge_count} edge{'' if edge_count == 1 else 's'}, "
        f"{drillable} drill-in view{'' if drillable == 1 else 's'}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
