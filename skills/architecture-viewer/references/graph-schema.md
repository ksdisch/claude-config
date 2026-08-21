# `arch-graph/v1` — the extracted architecture graph

One JSON document describing a repo's modules and the dependencies between them.
`/architecture-viewer` writes it; `scripts/validate_graph.py` checks it;
`scripts/render_map.py` renders it. It is deliberately renderer-agnostic: the
viewer is the first consumer, not the only intended one.

**This file is the contract, not a description of one implementation.** The
sibling idea [`module-dependency-rules-checker`](../../../docs/ideas/module-dependency-rules-checker.md)
is designed to read the same document — see *Contract with the checker* at the
bottom for the four guarantees it depends on. Changing any of them is a `v2`.

---

## Top level

```json
{
  "schema": "arch-graph/v1",
  "repo": { … },
  "roots": ["src", "server"],
  "excluded": ["**/*.test.ts"],
  "modules": [ … ],
  "edges": [ … ],
  "notes": ["…"]
}
```

| Field | Required | Meaning |
|---|---|---|
| `schema` | yes | Exactly `"arch-graph/v1"`. A consumer that sees anything else must refuse rather than guess. |
| `repo` | yes | Provenance — see below. |
| `roots` | yes | Repo-relative directories that were scanned for source. Everything outside them is out of the graph by construction, and the coverage check only counts files inside them. Accepted shapes are below — looser than a module `id`. |
| `excluded` | no | Glob patterns *inside* `roots` deliberately left unmapped (tests, generated code, vendored trees). Coverage subtracts these. An empty/absent list means nothing was excluded. |
| `modules` | yes | The nodes. At least one. |
| `edges` | yes | The directed dependencies. May be empty (a repo of independent modules is a legitimate finding, not an error). |
| `notes` | no | Free-text observations from the extraction pass — ambiguities, judgment calls, things a reader should distrust. Rendered in the map's findings banner, under *Extraction notes*. |

### `repo`

| Field | Required | Meaning |
|---|---|---|
| `name` | yes | Display name; the map's title falls back to it. |
| `root` | yes | Absolute path the graph was extracted from. Every relative path in the document resolves against it. |
| `commit` | no | The commit the graph describes. Absent means a dirty or non-git tree; the renderer says so rather than implying freshness. |
| `generated` | no | `YYYY-MM-DD`. |
| `extractor` | no | What produced it (`"architecture-viewer agent pass"`). Present so a future parser-based extractor is distinguishable from an agent-mapped one without diffing the data. |

---

## `modules` — the nodes

```json
{
  "id": "src/shared",
  "name": "shared",
  "parent": null,
  "path": "src/shared",
  "layer": "contract",
  "summary": "Wire protocol and shared types both clients speak.",
  "file_count": 7,
  "anchors": [
    { "file": "src/shared/protocol.ts", "line": 12, "label": "the message union" }
  ]
}
```

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | **Repo-relative POSIX path** of the module's directory (or of the file, for a single-file module). Unique across the document. No leading `/`, no `.` or `..` segments, no trailing slash. This is the name every other part of the document — and the future checker's rules file — refers to. |
| `name` | yes | Short display label. Need not be unique; `id` disambiguates. |
| `parent` | yes | `id` of the containing module, or `null` for a top-level module. |
| `path` | yes | Repo-relative path that must exist on disk. Normally equal to `id`; they differ only for a synthetic grouping node, which is not supported in v1 (`path` and `id` are required to match — the field exists so v2 can relax it without moving anything). |
| `layer` | no | Free-text grouping hint (`"ui"`, `"domain"`, `"contract"`, `"infra"`). The viewer shows it on the node and as a pill in the panel; the checker will phrase rules over it. Absent means ungrouped. |
| `summary` | yes | One sentence: what this module is responsible for. The single most valuable field for the "read the structure instead of the code" purpose, so it is required even though nothing mechanical depends on it. |
| `file_count` | no | Source files attributed to this module *including* its descendants. Displayed as a size cue. |
| `anchors` | no | Where to look first — see *Anchors and evidence*. |

**Nesting.** `parent` chains must be acyclic. v1 maps two levels — top-level
modules and their submodules — so a validated v1 document has depth ≤ 2; the
field is a general parent pointer so deeper trees need no schema change.

**Containment is not dependency.** A parent and its descendant must never
appear as the two endpoints of an edge. "`src/game` depends on `src/game/net`"
is a statement about nesting, which `parent` already carries.

---

## `edges` — the dependencies

```json
{
  "from": "src/game",
  "to": "src/shared",
  "kind": "import",
  "count": 12,
  "evidence": [
    {
      "file": "src/game/net/socket.ts",
      "line": 3,
      "text": "import type { Msg } from '../../shared/protocol'"
    }
  ]
}
```

| Field | Required | Meaning |
|---|---|---|
| `from` | yes | `id` of the **depending** module. |
| `to` | yes | `id` of the module **depended on**. |
| `kind` | no | Defaults to `"import"`. Recommended vocabulary: `import` (a static code dependency), `type-only` (erased at build time — worth distinguishing, because it is the cheapest dependency to invert), `runtime` (dynamic import, DI, message passing, HTTP call). Any non-empty string is accepted so a language the vocabulary didn't anticipate isn't forced to lie; unrecognized kinds render in the default style and are listed in the validator's summary. |
| `count` | no | How many dependency sites the extraction pass observed. A thickness cue, and a rough confidence signal. It is **not** required to equal `len(evidence)` — evidence carries exemplars, not an exhaustive list. |
| `evidence` | yes | At least one location proving the edge is real — see below. |

**Direction is fixed: `from` depends on `to`.** Arrows in the rendered map point
from dependent to dependency. Everything downstream — the layering, the cycle
report, the future checker's `may-not-depend-on` rules — reads the pair in that
order, and reversing it silently inverts every conclusion.

**One edge per `(from, to, kind)`.** Multiple import sites collapse into one
edge with a higher `count`, not into repeated edges.

---

## Anchors and evidence

Both are the same shape:

```json
{ "file": "src/game/net/socket.ts", "line": 3, "text": "…", "label": "…" }
```

| Field | Required | Meaning |
|---|---|---|
| `file` | yes | Repo-relative POSIX path. Must exist. |
| `line` | yes | 1-based. Must be ≤ the file's line count. |
| `text` | no | The line's content, for display. Not verified against the file — a source line moves, and a stale quote is far less harmful than a validator that fails whenever the tree changes. |
| `label` | no | Anchors only: why this location is the one to look at first. |

**Why every edge must carry one.** The extraction pass is an agent reading code,
and the characteristic failure of an agent reading code is a confident reference
to a file:line that does not exist. Requiring a resolvable location per edge
turns that failure from an invisible one into a validator error — which is why
`validate_graph.py` opens every referenced file and checks the line is in range,
and why a document that fails that check must never be rendered.

An `anchor` answers "open the code" for a *module*: the two or three places a
reader should look first. That is v1's substitute for embedding source, and it
is deliberately a pointer rather than a copy — copies go stale silently.

---

## Coverage

`roots` minus `excluded` defines the set of source files the graph claims to
account for. A file is *covered* when it sits under some module's `path`.
Uncovered files are the second characteristic extraction failure — a whole
directory the pass never noticed — so the validator reports the fraction and
fails below a floor (default 0.90, `--min-coverage`).

Coverage is a property of the extraction, not of the repo: excluding tests
raises it honestly, and both `roots` and `excluded` are in the document so the
number can be audited rather than trusted.

**Glob semantics for `excluded`** are fixed by this contract, not inherited from
whichever library happens to run it: matching is segment-by-segment, `*` and `?`
match within one path segment and never cross a `/`, and a whole segment of `**`
matches zero or more segments. So `src/generated/*` excludes
`src/generated/api.ts` but not `src/generated/deep/api.ts`, and `**/*.test.ts`
excludes at every depth including the top. Since `excluded` is subtracted from
the coverage denominator, a semantics that varied by interpreter would make the
same graph's coverage — and whether it cleared the floor — depend on where it
ran.

Two things make coverage a real gate rather than a number:

- **A `roots` entry that does not exist on disk is an error**, not a skip. A
  typo'd root scans nothing, and "nothing" would otherwise divide out to a clean
  100%.
- **Scanning zero files is an error.** Coverage of nothing is not coverage.

### Accepted `roots` shapes

A `roots` entry is a place to start walking, not an identity, so it is checked
more loosely than a module `id` — these are normalized rather than rejected:

| Entry | Means |
|---|---|
| `src` | that directory |
| `src/` · `./src` · `src//lib` | the same as `src` / `src/lib` — trailing, leading and doubled separators collapse |
| `.` (or `./`) | **the whole repo is source** — the only way to say it, and what a flat repo needs. Without it, a repo with `main.py` at the top level would have to list its top-level *files*, and every file added afterwards would fall outside the coverage denominator unnoticed |

Rejected, because a root must not escape the repo: a leading `/`, any `..`
segment, a backslash separator, and the empty string.

---

## Contract with the checker

The dependency-rules checker in
[`docs/ideas/module-dependency-rules-checker.md`](../../../docs/ideas/module-dependency-rules-checker.md)
is not built. These are the four guarantees it is designed against, and they are
the reason the fields above look the way they do:

1. **`id` is a stable, human-writable name.** A rules file says
   `src/shared: may-not-depend-on: [src/game, src/phone]` — hand-written by a
   person against paths they already know, and re-resolvable after a re-extract
   because a path is not a generated identifier.
2. **`(from, to)` is the whole dependency relation.** A rule is a predicate over
   that pair; nothing else in the document is needed to decide whether an edge is
   allowed. `kind` and `layer` refine rules but are never required by them.
3. **`evidence` is the violation report.** When a rule fails, the checker has a
   file:line to print without re-scanning the tree — and validation has already
   guaranteed it resolves.
4. **The graph is data, not a rendering.** Nothing in the document encodes
   position, colour, or view state; the renderer derives all of it. A second
   consumer never has to strip presentation out.

The viewer shows this graph. The checker would enforce it. Neither owns it.
