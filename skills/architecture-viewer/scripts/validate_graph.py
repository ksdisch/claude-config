#!/usr/bin/env python3
"""Validate an `arch-graph/v1` document before anything renders or enforces it.

The graph is extracted by an agent reading code, and an agent reading code fails
in two characteristic ways: it cites a file:line that does not exist, and it
never notices a directory. Both produce a document that looks perfect. This
script is what makes those two failures loud — it opens every referenced file and
checks the line is in range, and it counts how much of the scanned source the
modules actually account for.

    python3 validate_graph.py architecture.json
    python3 validate_graph.py architecture.json --min-coverage 0.8 -o summary.json

Exit 0 = the document is safe to render (a one-line summary always prints, so a
silent run is never mistaken for a pass). Exit 1 = problems, each one named.

Cycles are **reported, not failed**. A dependency cycle is the finding the map
exists to surface; refusing to render it would hide exactly what a reader needs
to see.

The schema this checks is `../references/graph-schema.md`. That file is the
contract; this file is its enforcement.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from pathlib import Path, PurePosixPath

SCHEMA = "arch-graph/v1"
MAX_DEPTH = 2  # v1 maps top-level modules and their submodules — see the schema doc.
KNOWN_KINDS = ("import", "type-only", "runtime")

# Directories that are never source for coverage purposes. A repo that really
# does keep source in one of these names can say so by listing it in `roots`,
# which is consulted first.
IGNORED_DIRS = frozenset(
    {
        "node_modules", "dist", "build", "out", "coverage", "target", "vendor",
        "__pycache__", "venv", "site-packages", "bower_components",
    }
)


class Problems:
    """Errors and warnings, kept apart because only one of them fails the run."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def matches_glob(rel: str, pattern: str) -> bool:
    """`**`-aware glob match against a repo-relative POSIX path.

    `PurePath.full_match` (3.13+) has the recursive semantics `excluded`
    patterns are written with. The fallback keeps this usable on older
    interpreters: fnmatch's `*` crosses `/`, so the only case it gets wrong is a
    leading `**/` that must also match zero directories, which the second
    attempt covers.
    """
    path = PurePosixPath(rel)
    full_match = getattr(path, "full_match", None)
    if full_match is not None:
        return full_match(pattern)
    if fnmatch.fnmatchcase(rel, pattern):
        return True
    if pattern.startswith("**/"):
        return fnmatch.fnmatchcase(rel, pattern[3:])
    return False


def line_count(path: Path, cache: dict[Path, int]) -> int:
    """Lines in a file, counting a final line with no trailing newline. An
    unreadable or empty file counts as 0, which makes every 1-based reference
    into it out of range — the correct outcome, not a crash."""
    if path in cache:
        return cache[path]
    try:
        data = path.read_bytes()
    except OSError:
        count = 0
    else:
        count = data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)
    cache[path] = count
    return count


def check_id(module_id: str) -> str | None:
    """Why this id is unusable as a repo-relative POSIX path, or None."""
    if not isinstance(module_id, str) or not module_id:
        return "must be a non-empty string"
    if module_id.startswith("/"):
        return "must be repo-relative (no leading '/')"
    if module_id.endswith("/"):
        return "must not end with '/'"
    if "\\" in module_id:
        return "must use POSIX separators ('/' not '\\')"
    parts = module_id.split("/")
    if "" in parts:
        return "must not contain an empty path segment"
    if "." in parts or ".." in parts:
        return "must not contain '.' or '..' segments"
    return None


def check_locations(
    kind: str,
    where: str,
    locations: object,
    root: Path,
    cache: dict[Path, int],
    problems: Problems,
) -> int:
    """Validate a list of anchor/evidence locations. Returns how many resolved.

    This is the anti-hallucination gate: a location that names a file which is
    not there, or a line past the end of it, is a citation the extraction pass
    invented.
    """
    if not isinstance(locations, list):
        problems.error(f"{where}: `{kind}` must be a list")
        return 0

    resolved = 0
    for index, location in enumerate(locations):
        label = f"{where}: {kind}[{index}]"
        if not isinstance(location, dict):
            problems.error(f"{label} must be an object")
            continue

        file_ref = location.get("file")
        line_ref = location.get("line")
        if not isinstance(file_ref, str) or not file_ref:
            problems.error(f"{label} is missing `file`")
            continue
        reason = check_id(file_ref)
        if reason:
            problems.error(f"{label} `file` {reason}: {file_ref!r}")
            continue
        if not isinstance(line_ref, int) or isinstance(line_ref, bool) or line_ref < 1:
            problems.error(f"{label} `line` must be a 1-based integer, got {line_ref!r}")
            continue

        target = root / file_ref
        if not target.is_file():
            problems.error(f"{label} points at a file that does not exist: {file_ref}")
            continue
        lines = line_count(target, cache)
        if line_ref > lines:
            problems.error(
                f"{label} points at {file_ref}:{line_ref}, but that file has "
                f"{lines} line{'' if lines == 1 else 's'}"
            )
            continue
        resolved += 1

    return resolved


def source_files(root: Path, roots: list[str], excluded: list[str]) -> list[str]:
    """Repo-relative paths of every file the graph claims to account for.

    A dot-directory or a build output is never source; everything else under
    `roots` is, minus the document's own `excluded` globs. Symlinked
    directories are not followed — a self-referential link would otherwise walk
    forever.
    """
    found: list[str] = []
    for entry in roots:
        base = root / entry
        if not base.exists():
            continue
        if base.is_file():
            rel = base.relative_to(root).as_posix()
            if not any(matches_glob(rel, pattern) for pattern in excluded):
                found.append(rel)
            continue
        stack = [base]
        while stack:
            current = stack.pop()
            try:
                children = sorted(current.iterdir())
            except OSError:
                continue
            for child in children:
                name = child.name
                if name.startswith("."):
                    continue
                if child.is_symlink():
                    continue
                if child.is_dir():
                    if name not in IGNORED_DIRS:
                        stack.append(child)
                    continue
                if not child.is_file():
                    continue
                rel = child.relative_to(root).as_posix()
                if any(matches_glob(rel, pattern) for pattern in excluded):
                    continue
                found.append(rel)
    return sorted(set(found))


def covered_by(rel: str, module_paths: list[str]) -> bool:
    """Whether a file sits inside some module's path."""
    for path in module_paths:
        if rel == path or rel.startswith(path + "/"):
            return True
    return False


def strongly_connected(nodes: list[str], edges: list[tuple[str, str]]) -> list[list[str]]:
    """Every strongly connected component of more than one node — i.e. every
    dependency cycle — via iterative Tarjan. Iterative because a deep module
    tree would otherwise be a recursion-limit crash on the one input that most
    needs an answer.
    """
    successors: dict[str, list[str]] = {node: [] for node in nodes}
    for source, target in edges:
        if source in successors and target in successors:
            successors[source].append(target)

    index_of: dict[str, int] = {}
    low: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    counter = 0
    components: list[list[str]] = []

    for start in nodes:
        if start in index_of:
            continue
        # Each frame is (node, iterator position into its successors).
        work: list[tuple[str, int]] = [(start, 0)]
        index_of[start] = low[start] = counter
        counter += 1
        stack.append(start)
        on_stack.add(start)

        while work:
            node, position = work[-1]
            if position < len(successors[node]):
                work[-1] = (node, position + 1)
                nxt = successors[node][position]
                if nxt not in index_of:
                    index_of[nxt] = low[nxt] = counter
                    counter += 1
                    stack.append(nxt)
                    on_stack.add(nxt)
                    work.append((nxt, 0))
                elif nxt in on_stack:
                    low[node] = min(low[node], index_of[nxt])
                continue

            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[node])
            if low[node] == index_of[node]:
                component = []
                while True:
                    member = stack.pop()
                    on_stack.discard(member)
                    component.append(member)
                    if member == node:
                        break
                if len(component) > 1:
                    components.append(sorted(component))

    return sorted(components)


def top_ancestor(module_id: str, parents: dict[str, str | None]) -> str:
    """The top-level module a node rolls up into."""
    seen = {module_id}
    current = module_id
    while True:
        parent = parents.get(current)
        if parent is None or parent in seen:
            return current
        seen.add(parent)
        current = parent


def validate(doc: object, root: Path, min_coverage: float) -> tuple[Problems, dict]:
    """Check a loaded document. Returns the problems and a machine summary."""
    problems = Problems()
    summary: dict = {"schema_ok": False, "modules": 0, "edges": 0}

    if not isinstance(doc, dict):
        problems.error("the document must be a JSON object")
        return problems, summary
    if doc.get("schema") != SCHEMA:
        problems.error(
            f"`schema` must be {SCHEMA!r}, got {doc.get('schema')!r} — refusing to "
            f"guess at another version's meaning"
        )
        return problems, summary
    summary["schema_ok"] = True

    repo = doc.get("repo")
    if not isinstance(repo, dict):
        problems.error("`repo` must be an object")
        repo = {}
    for field in ("name", "root"):
        if not isinstance(repo.get(field), str) or not repo.get(field):
            problems.error(f"`repo.{field}` must be a non-empty string")
    if not repo.get("commit"):
        problems.warn(
            "`repo.commit` is absent — the map cannot say which revision it describes"
        )

    roots = doc.get("roots")
    if not isinstance(roots, list) or not roots or not all(isinstance(r, str) and r for r in roots):
        problems.error("`roots` must be a non-empty list of repo-relative directories")
        roots = []
    excluded = doc.get("excluded", [])
    if not isinstance(excluded, list) or not all(isinstance(p, str) for p in excluded):
        problems.error("`excluded` must be a list of glob patterns")
        excluded = []
    notes = doc.get("notes", [])
    if not isinstance(notes, list) or not all(isinstance(n, str) for n in notes):
        problems.error("`notes` must be a list of strings")

    modules = doc.get("modules")
    if not isinstance(modules, list) or not modules:
        problems.error("`modules` must be a non-empty list")
        return problems, summary
    edges = doc.get("edges")
    if not isinstance(edges, list):
        problems.error("`edges` must be a list (it may be empty)")
        edges = []

    cache: dict[Path, int] = {}
    by_id: dict[str, dict] = {}
    parents: dict[str, str | None] = {}

    for index, module in enumerate(modules):
        where = f"modules[{index}]"
        if not isinstance(module, dict):
            problems.error(f"{where} must be an object")
            continue
        module_id = module.get("id")
        reason = check_id(module_id) if module_id is not None else "is required"
        if reason:
            problems.error(f"{where}: `id` {reason}" + (f": {module_id!r}" if module_id else ""))
            continue
        if module_id in by_id:
            problems.error(f"{where}: duplicate module id {module_id!r}")
            continue
        by_id[module_id] = module

        where = f"module {module_id!r}"
        for field in ("name", "summary"):
            if not isinstance(module.get(field), str) or not module.get(field).strip():
                problems.error(f"{where}: `{field}` must be a non-empty string")

        path = module.get("path")
        if not isinstance(path, str) or check_id(path):
            problems.error(f"{where}: `path` must be a repo-relative POSIX path")
        else:
            if path != module_id:
                problems.error(
                    f"{where}: `path` is {path!r} — in v1 it must equal `id`, so a "
                    f"module is always the directory it names"
                )
            if not (root / path).exists():
                problems.error(f"{where}: `path` does not exist on disk: {path}")

        if "parent" not in module:
            problems.error(f"{where}: `parent` is required (use null for a top-level module)")
            parents[module_id] = None
        elif module["parent"] is None or (
            isinstance(module["parent"], str) and module["parent"]
        ):
            parents[module_id] = module["parent"]
        else:
            problems.error(f"{where}: `parent` must be a module id or null")
            parents[module_id] = None

        if "layer" in module and module["layer"] is not None:
            if not isinstance(module["layer"], str) or not module["layer"].strip():
                problems.error(f"{where}: `layer` must be a non-empty string when present")
        if "file_count" in module and module["file_count"] is not None:
            count = module["file_count"]
            if not isinstance(count, int) or isinstance(count, bool) or count < 0:
                problems.error(f"{where}: `file_count` must be a non-negative integer")
        if "anchors" in module and module["anchors"] is not None:
            check_locations("anchors", where, module["anchors"], root, cache, problems)

    for module_id, parent in parents.items():
        if parent is None:
            continue
        if parent not in by_id:
            problems.error(f"module {module_id!r}: `parent` {parent!r} is not a module")
            continue
        # Walk to the root, bounded by the number of modules so a parent cycle
        # is reported rather than looped on.
        depth, seen, current = 1, {module_id}, parent
        cyclic = False
        while current is not None:
            if current in seen:
                problems.error(f"module {module_id!r}: `parent` chain is cyclic at {current!r}")
                cyclic = True
                break
            seen.add(current)
            depth += 1
            current = parents.get(current)
        if not cyclic and depth > MAX_DEPTH:
            problems.error(
                f"module {module_id!r}: nested {depth} levels deep — v1 maps at most "
                f"{MAX_DEPTH} (a top-level module and its submodules)"
            )

    def is_ancestor(candidate: str, node: str) -> bool:
        seen, current = {node}, parents.get(node)
        while current is not None and current not in seen:
            if current == candidate:
                return True
            seen.add(current)
            current = parents.get(current)
        return False

    seen_edges: set[tuple[str, str, str]] = set()
    resolved_edges: list[tuple[str, str]] = []
    unknown_kinds: set[str] = set()
    connected: set[str] = set()

    for index, edge in enumerate(edges):
        where = f"edges[{index}]"
        if not isinstance(edge, dict):
            problems.error(f"{where} must be an object")
            continue
        source, target = edge.get("from"), edge.get("to")
        missing = [f for f in ("from", "to") if not isinstance(edge.get(f), str) or not edge.get(f)]
        if missing:
            problems.error(f"{where}: {' and '.join('`' + m + '`' for m in missing)} must be a module id")
            continue

        where = f"edge {source!r} → {target!r}"
        unresolved = [n for n in (source, target) if n not in by_id]
        if unresolved:
            problems.error(
                f"{where}: {' and '.join(repr(n) for n in unresolved)} "
                f"{'is not a module' if len(unresolved) == 1 else 'are not modules'}"
            )
            continue
        if source == target:
            problems.error(f"{where}: a module cannot depend on itself")
            continue
        if is_ancestor(source, target) or is_ancestor(target, source):
            problems.error(
                f"{where}: these are nested in each other — containment is carried by "
                f"`parent`, not by an edge"
            )
            continue

        kind = edge.get("kind", "import")
        if not isinstance(kind, str) or not kind.strip():
            problems.error(f"{where}: `kind` must be a non-empty string when present")
            kind = "import"
        elif kind not in KNOWN_KINDS:
            unknown_kinds.add(kind)

        key = (source, target, kind)
        if key in seen_edges:
            problems.error(
                f"{where}: duplicate {kind} edge — collapse repeated dependency sites "
                f"into one edge with a higher `count`"
            )
            continue
        seen_edges.add(key)

        if "count" in edge and edge["count"] is not None:
            count = edge["count"]
            if not isinstance(count, int) or isinstance(count, bool) or count < 1:
                problems.error(f"{where}: `count` must be a positive integer")

        evidence = edge.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            problems.error(
                f"{where}: needs at least one `evidence` location — an edge nothing "
                f"points at is an edge nothing verified"
            )
        else:
            check_locations("evidence", where, evidence, root, cache, problems)

        resolved_edges.append((source, target))
        connected.add(source)
        connected.add(target)

    for kind in sorted(unknown_kinds):
        problems.warn(
            f"edge kind {kind!r} is outside the recommended vocabulary "
            f"({', '.join(KNOWN_KINDS)}) — it renders in the default style"
        )

    # A module is only unconnected when nothing in its whole subtree is: a parent
    # never carries its submodules' edges (that would be a containment edge), so
    # judging it on its own id alone reports every parent in the graph.
    children_of: dict[str, list[str]] = {}
    for module_id, parent in parents.items():
        if parent is not None:
            children_of.setdefault(parent, []).append(module_id)

    def subtree_connected(module_id: str) -> bool:
        stack, seen = [module_id], {module_id}
        while stack:
            current = stack.pop()
            if current in connected:
                return True
            for child in children_of.get(current, []):
                if child not in seen:
                    seen.add(child)
                    stack.append(child)
        return False

    orphans = sorted(m for m in by_id if not subtree_connected(m))
    if orphans:
        problems.warn(
            "modules with no dependencies in either direction — either genuinely "
            "standalone, or an edge the extraction pass missed:\n    "
            + "\n    ".join(orphans)
        )

    files = source_files(root, roots, excluded) if roots else []
    module_paths = [m.get("path") for m in by_id.values() if isinstance(m.get("path"), str)]
    uncovered = [f for f in files if not covered_by(f, module_paths)]
    coverage = 1.0 if not files else (len(files) - len(uncovered)) / len(files)
    if files and coverage < min_coverage:
        shown = uncovered[:20]
        more = f"\n    …and {len(uncovered) - len(shown)} more" if len(uncovered) > len(shown) else ""
        problems.error(
            f"coverage is {coverage:.0%} of {len(files)} scanned source files, below the "
            f"{min_coverage:.0%} floor — {len(uncovered)} file(s) belong to no module:\n    "
            + "\n    ".join(shown)
            + more
            + "\n    Either map them, or list them in `excluded` and say why in `notes`."
        )
    elif uncovered:
        problems.warn(
            f"{len(uncovered)} of {len(files)} scanned source files belong to no module "
            f"(coverage {coverage:.0%}); first few:\n    " + "\n    ".join(uncovered[:5])
        )

    node_ids = sorted(by_id)
    cycles = strongly_connected(node_ids, resolved_edges)
    rolled: set[tuple[str, str]] = set()
    for source, target in resolved_edges:
        a, b = top_ancestor(source, parents), top_ancestor(target, parents)
        if a != b:
            rolled.add((a, b))
    tops = sorted(m for m in by_id if parents.get(m) is None)
    top_cycles = strongly_connected(tops, sorted(rolled))

    summary.update(
        {
            "modules": len(by_id),
            "top_level_modules": len(tops),
            "edges": len(resolved_edges),
            "coverage": round(coverage, 4),
            "scanned_files": len(files),
            "uncovered_files": uncovered,
            "cycles": cycles,
            "top_level_cycles": top_cycles,
            "orphan_modules": orphans,
            "unknown_edge_kinds": sorted(unknown_kinds),
            "errors": problems.errors,
            "warnings": problems.warnings,
        }
    )
    return problems, summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("graph", help="path to the architecture.json to validate")
    parser.add_argument(
        "--repo-root",
        help="resolve relative paths against this directory instead of the document's "
        "`repo.root` (use when the tree has moved)",
    )
    parser.add_argument(
        "--min-coverage",
        type=float,
        default=0.9,
        help="fraction of scanned source files that must belong to some module (default 0.9)",
    )
    parser.add_argument("-o", "--out", help="write the machine summary here as JSON")
    args = parser.parse_args(argv)

    graph_path = Path(args.graph)
    try:
        doc = json.loads(graph_path.read_text())
    except OSError as exc:
        print(f"cannot read {args.graph}: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"{args.graph} is not valid JSON: {exc}", file=sys.stderr)
        return 1

    root_hint = args.repo_root
    if root_hint is None and isinstance(doc, dict):
        repo = doc.get("repo")
        if isinstance(repo, dict) and isinstance(repo.get("root"), str):
            root_hint = repo["root"]
    root = Path(root_hint).expanduser().resolve() if root_hint else graph_path.resolve().parent

    if not root.is_dir():
        print(
            f"repo root {root} is not a directory — pass --repo-root if the tree has moved.",
            file=sys.stderr,
        )
        return 1

    problems, summary = validate(doc, root, args.min_coverage)
    summary["repo_root"] = str(root)

    if args.out:
        Path(args.out).write_text(json.dumps(summary, indent=2) + "\n")

    for warning in problems.warnings:
        print(f"warning — {warning}\n", file=sys.stderr)

    if problems.errors:
        print(
            f"graph check FAILED — {args.graph} is not safe to render.\n"
            f"({len(problems.errors)} problem(s))\n",
            file=sys.stderr,
        )
        for problem in problems.errors:
            print(f"  {problem}\n", file=sys.stderr)
        print(
            "Fix the extraction, not the checker: a location that does not resolve is a\n"
            "citation nobody can follow, and an uncovered directory is a module nobody drew.",
            file=sys.stderr,
        )
        return 1

    cycles = summary.get("top_level_cycles") or []
    cycle_note = (
        f", {len(cycles)} top-level dependency cycle(s) — see the map"
        if cycles
        else ", no top-level cycles"
    )
    edge_count = summary["edges"]
    print(
        f"graph check: clean — {summary['modules']} modules "
        f"({summary['top_level_modules']} top-level), {edge_count} "
        f"edge{'' if edge_count == 1 else 's'}, {summary['coverage']:.0%} coverage of "
        f"{summary['scanned_files']} files{cycle_note}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
