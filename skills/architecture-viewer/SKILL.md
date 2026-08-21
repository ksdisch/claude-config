---
name: architecture-viewer
description: Turn a repo into a clickable architecture map — one self-contained HTML page where modules are nodes, arrows point from dependent to dependency, and a module with submodules opens one level down. An agent pass reads the tree and emits an `arch-graph/v1` JSON graph (modules, edges, and a real file:line behind every edge), a validator refuses to render a graph whose citations don't resolve or whose modules leave source unaccounted for, and the page ends with what the structure actually says — cycles, hubs, and edges running against the repo's stated layering. "Open the code" is a click-to-copy `file:line`, never embedded source. Polyglot: nothing parses imports per language. Use when Kyle types /architecture-viewer, or says "map this repo's architecture", "show me the module structure", "where do the dependencies run", "draw the dependency graph", "I want to review the architecture, not the code", "are there any dependency cycles here" — even if he doesn't name the skill. NOT for prose about a project (project-guide), catching up after a gap (reorient), or enforcing dependency rules (that's the module-dependency-rules-checker's job, which reads the same graph this skill writes).
---

# Architecture Viewer — read the structure instead of the code

Uncle Bob's version of this: *"a nice little UML diagram that shows me the modular
structure of the system and where the dependencies run — I can click on a module
and see inside it to the submodules… I can drill down as much as I want and view
the system architecture at any level."* That's what let him stop reading code and
start reading structure, get scared by what he saw, and redesign.

This skill produces the v0 of that: **one repo in, one self-contained HTML file
out.** Modules as nodes, directed dependency arrows, one level of click-to-expand,
and a findings banner that says what the shape means.

Two halves, deliberately split:

| Half | Who does it | Why there |
|---|---|---|
| **Extraction** — what the modules are, what depends on what | an agent reading the tree | Judgment. A module boundary is a claim about responsibility, and it is polyglot on day one because nothing parses a language. |
| **Layout, rendering, validation** | the scripts in `scripts/` | Mechanical and deterministic. The same graph renders identically every run, and the checks that catch a hallucinated citation are code, not good intentions. |

The graph is a durable artifact in its own right —
[`references/graph-schema.md`](references/graph-schema.md) is the contract, and it
is written so the future
[module-dependency-rules-checker](../../docs/ideas/module-dependency-rules-checker.md)
can enforce the same document this skill draws. **Do not build the checker here.**

---

## Parse `$ARGUMENTS`

- **A path** → that repo is the target.
- **No argument** → the current working repo is the target. Say which one you
  picked before doing anything else.
- **`--out <dir>`** → write both output files there instead of the default
  location (below).
- **`--publish`** → also publish the page as a claude.ai Artifact. **Off by
  default**: a repo's internal structure is Kyle's to share, and publishing is
  outward-facing even though artifacts start private.
- **`--min-coverage <fraction>`** → passed through to the validator. Raising it
  is fine; see the *Coverage floor* invariant before lowering it.

---

## Invariants

Named, so later phases can cite them instead of restating them. Every one of
them is either enforced by `validate_graph.py` or is a rule for the extraction
pass that nothing mechanical can check.

- **Path-backed modules.** Every module is a directory (or single file) that
  exists on disk, and its `id` is that repo-relative POSIX path. There are no
  synthetic grouping nodes in v1 — a module you cannot `cd` into is a module
  nobody can open.
- **One level down.** Top-level modules and their submodules. Not grandchildren.
  Bob's third level is out of scope for v0, and the schema already carries the
  parent pointer that will allow it later.
- **Direction is dependent → dependency.** `from` depends on `to`; the arrow
  points at the thing being depended on. Reversing one edge inverts every
  conclusion drawn from the map, and nothing downstream can detect it.
- **Containment is not dependency.** A module and its own submodule never get an
  edge. Nesting is carried by `parent`.
- **Evidence or no edge.** Every edge carries at least one `file:line` that
  really resolves. An edge you believe in but cannot point at does not go in the
  graph — it goes in `notes`.
- **Measured, not aspirational.** The graph records the dependencies that exist,
  not the ones the README says exist. Where they differ, that difference is the
  most valuable thing on the page (Phase 6).
- **Coverage floor.** Every source file under a declared root belongs to some
  module, or is matched by an `excluded` glob whose reason is stated in `notes`.
  **Never lower `--min-coverage` to make a run pass** — the number exists to
  catch the directory the extraction never noticed, and lowering it is how that
  directory stays invisible.
- **No render before validate.** `render_map.py` is never run on a graph that
  `validate_graph.py` has not just passed. The validator is the only thing
  standing between an invented citation and a reader who tries to open it.

---

## Phase 1 — Survey the tree

1. **Fix the target and its identity.** Resolve the repo root to an absolute
   path. Read `HEAD`'s commit; if the working tree is dirty, omit `repo.commit`
   rather than recording a revision the map doesn't match — the page says
   "uncommitted tree" and that is the honest label.
2. **Read what the repo says about itself first**, before looking at any source:
   `README`, `CLAUDE.md`, `PROJECT.md`, `Wiki/_index.md`, and whatever declares
   the build shape (`package.json` workspaces, `tsconfig.json` path aliases,
   `pyproject.toml`, `go.mod`, `Cargo.toml`). This is not for the module list —
   it is so Phase 6 can compare the structure you measure against the structure
   the repo claims. Keep a note of any stated layering rule.
3. **Declare the source roots.** The top-level directories holding first-party
   source. Vendored, generated, and build output are not roots. Everything
   outside the roots is out of the graph by construction, so a root you forget is
   a whole tree that silently doesn't count against coverage. **A repo whose
   source sits at the top level uses `"."`** — the whole repo — rather than
   listing files. `"."` is never used alone: it counts README, manifests, `docs/`
   and this skill's own output under `docs/architecture/` as source, so it always
   ships with an `excluded` list, and `*.md` there matches **only the top level**
   (`**/*.md` is what covers every depth). The schema's *Accepted `roots` shapes*
   section has a starting list.
4. **Propose the top-level modules.** A module is a directory that owns one
   coherent responsibility. Start from the repo's own top-level source
   directories, then adjust: split a directory that plainly holds two unrelated
   responsibilities, and keep a directory whole when its parts only make sense
   together. Honour *Path-backed modules*.
5. **Propose submodules**, one level, for each top-level module whose internals
   have a real seam. A module whose children would just be "the files, grouped
   arbitrarily" gets no submodules — an empty drill-in is worse than none.
6. **Write the summaries.** One sentence per module: what it is responsible for,
   in the repo's own vocabulary. This is the field a reader actually reads, and
   it is required.
7. **Assign `layer` only where the repo has a real layering vocabulary** (`ui`,
   `domain`, `contract`, `infra`, or whatever the project uses). Leave it absent
   otherwise. An invented layer name reads exactly like a discovered one.
8. **Pick anchors** — one to three `file:line` locations per top-level module
   that a reader should open first, each with a short label saying why.

**There is no approval gate on the module list, on purpose.** A boundary
proposed before anything is drawn is a boundary Kyle has to evaluate in the
abstract; the map is cheap to regenerate, so the cheaper loop is to render, look,
and re-run Phase 1 with his correction. Say so when delivering — *"if the
grouping is wrong, tell me and I'll re-map"* — so the option is visible.

---

## Phase 2 — Map the dependencies

1. **Fan out by owner.** Dispatch one Explore-style agent per top-level module.
   Each agent is responsible for **its module's outbound edges only** — what this
   module depends on, never what depends on it. That assignment is what keeps two
   agents from producing two halves of the same edge with different evidence and
   different counts.
2. **Give each agent the whole module list**, so it names targets by their real
   `id` instead of inventing one, and tell it which submodules exist so it can
   attribute an edge to the submodule that actually holds it.
3. **Each agent returns, per dependency:** the target module `id`, the `kind`
   (`import`, `type-only`, `runtime` — see the schema for what each means),
   roughly how many dependency sites it saw, and one to three `file:line`
   locations with the line's text. An agent that finds no outbound dependency
   says so explicitly; silence is indistinguishable from a crashed pass.
4. **Attribute at the finest level you mapped.** If `src/game/net` is the
   submodule that imports the shared protocol, the edge is `from: src/game/net`,
   not `from: src/game`. The renderer rolls submodule edges up to the parent for
   the top view, so recording the coarse version throws away the drill-in for
   nothing.
5. **Honour *Evidence or no edge*.** A dependency you are confident about but
   cannot locate is a `notes` entry, not an edge.
6. **Runtime and cross-process dependencies count.** An HTTP call, a message on a
   socket, a job queued for another module — these are real dependencies with
   `kind: "runtime"`, and they are the ones an import parser would miss entirely.
   Finding them is most of why extraction is an agent pass.

---

## Phase 3 — Emit the graph

Write `arch-graph/v1` exactly as
[`references/graph-schema.md`](references/graph-schema.md) specifies. Assemble it
yourself from the Phase 1 and Phase 2 results:

1. Merge duplicate edges: one edge per `(from, to, kind)`, `count` summed,
   evidence concatenated and trimmed to the clearest three.
2. Fill `roots` and `excluded` from Phase 1 step 3, and put the *reason* for each
   exclusion in `notes` — the coverage number is only auditable if the
   subtractions are stated.
3. Put every judgment call you are unsure about in `notes`. It renders in the
   findings banner, where a reader can weigh it, rather than being lost.
4. `file_count` per module is the count including its descendants. It is a size
   cue, so an approximate count is fine and no count is better than a wrong one.

---

## Phase 4 — Validate (hard gate)

```
python3 skills/architecture-viewer/scripts/validate_graph.py <graph.json>
```

Add `--min-coverage` only to *raise* the floor, and `-o <summary.json>` when you
want the machine summary (cycles, uncovered files, orphans) for Phase 6.

**It must exit clean before anything is rendered** (*No render before validate*).
When it fails:

- **A citation that doesn't resolve** means the extraction invented a location.
  Re-read the file and correct it. Never delete the evidence to make the edge
  pass — an edge without evidence is not allowed either, and dropping it would
  hide a dependency that probably exists.
- **Coverage below the floor** means a directory nobody mapped. Map it, or
  exclude it *and say why in `notes`*. Honour *Coverage floor*: the threshold is
  not the thing to adjust.
- **A `roots` entry that doesn't exist**, or a scan that found zero files, is an
  error rather than a clean run. Both are the coverage half of this gate
  reporting on nothing — fix the root or the `excluded` pattern that swallowed
  everything. `excluded` globs match segment-by-segment (`*` never crosses `/`,
  a whole segment of `**` matches any depth); see the schema doc.
- **A containment edge** means Phase 2 recorded nesting as dependency. Delete the
  edge; `parent` already says it.

Warnings are not gates, but read them. "Modules with no dependencies in either
direction" is usually a missed edge rather than a genuinely standalone module.

---

## Phase 5 — Render

```
python3 skills/architecture-viewer/scripts/render_map.py <graph.json> -o <map.html>
```

The page is produced whole by the script — there is nothing to hand-author, and
nothing in it should be hand-edited afterwards. It already satisfies the house
self-contained-artifact rules that `paper-gloss` sets out: one file, no external
resource of any kind, CSS variables themed for light and dark with
`data-theme` overriding the media query, and every string from the graph inserted
as text rather than markup.

**Default output location**, when `--out` is not given:

- `docs/architecture/` in the target repo if it has a `docs/` directory,
  otherwise `.claude/architecture/`.
- Filenames: `<repo-name>-graph.json` and `<repo-name>-map.html`.
- Both scripts create the output's parent directory, so a repo being mapped for
  the first time needs no setup step.

---

## Phase 6 — Read the map

The map is worthless if nobody draws a conclusion from it, and this is the phase
the backlog acceptance is written against: *does it change a real review?* Work
the validator's summary and the rendered page, and report:

1. **Cycles.** Every cycle at the top level, and every cycle among submodules
   that the rollup hides. For each one, name the two edges that close it and
   which is the cheaper to invert — a `type-only` edge is usually the one.
2. **Dependency hubs.** The module the most others depend on (a change there is
   the most expensive change in the repo) and the module that depends on the
   most others (usually the least testable one).
3. **Edges against the stated layering.** Compare what you measured against what
   Phase 1 step 2 said the repo intends. An arrow from a contract module up into
   a client, or from a shared module into a specific feature, is the finding
   worth the whole exercise. This is *Measured, not aspirational* paying off.
4. **Orphans**, and whether each is genuinely standalone or a missed edge.
5. **One paragraph of "what I'd change"** — the single structural change with the
   best ratio of review value to effort, stated as a claim Kyle can disagree
   with.

If nothing here is interesting, say that plainly. A repo whose structure is
already clean is a real result, and reporting a manufactured concern to justify
the run is worse than reporting none.

---

## Phase 7 — Deliver

1. **Send the HTML** to Kyle with `SendUserFile` — it is the deliverable, and it
   is meant to be opened, not described.
2. **Report** both output paths, the validator's one-line summary (modules,
   edges, coverage, cycles), and Phase 6's findings.
3. **Offer the re-map**, per the Phase 1 note: if the grouping is wrong, one
   correction and a re-run fixes it.
4. **Git.** When the target repo *is* the repo this session is working in, follow
   the normal workflow — branch, commit, push, PR, merge, brief Kyle — unless
   that project's `CLAUDE.md` tightens it. **When the target is a different
   repo, write the files and stop there**: a session working in one repo does not
   open pull requests in another. Say where the files landed and that they are
   uncommitted.
5. **Publish only on `--publish`.** Then `Artifact` with the repo name as
   `title`, `favicon` `"🗺️"`, and a one-sentence `description` naming the module
   and edge counts. Every run publishes a new artifact unless Kyle gives a URL to
   redeploy to.

---

## What v0 deliberately does not do

State these when delivering, so the map's silence is never mistaken for a finding:

- **One drill level.** A submodule does not open further. Bob's third level —
  click a submodule, get the code on screen — is not here; the anchors and the
  per-edge `file:line` references are the substitute.
- **No source embedding.** "Open the code" copies a `file:line`. A copy of the
  source in the page would go stale silently; a reference cannot.
- **A drilled-in view draws only internal arrows.** Dependencies leaving the
  module you opened are listed in the panel, named submodule by submodule, but
  are not drawn as arrows in that view.
- **No import parser.** Nothing is parsed per language, which is what makes this
  work on any repo on day one — and also what makes the extraction an agent's
  judgment rather than a compiler's fact. `notes` is where that uncertainty goes.
- **No rule enforcement, no watch mode, no IDE integration.** The first is the
  checker's job and reads this same graph; the other two are out of scope.

---

## Maintaining the scripts

`scripts/tests/` covers both scripts with stdlib `unittest` — no pytest:

```
python3 -m unittest discover -s tests -t .    # from skills/architecture-viewer/scripts
```

Layout changes are the ones worth guarding: the suite pins that a dependency
ranks below its dependents, that back edges are found without recursion, and
that two runs of the same graph produce byte-identical geometry. A layout that
shifts between runs makes two maps of the same repo impossible to compare.

---

## Definition of done

The graph JSON and the HTML map both exist at their reported paths;
`validate_graph.py` exited clean on the graph that was rendered (not an earlier
one); the map opens with the top-level modules laid out, arrows pointing from
dependent to dependency, every module with submodules drillable one level, and
every `file:line` copyable; Phase 6's findings were reported with a named
conclusion or an explicit "nothing here is interesting"; the file was sent via
`SendUserFile`; and the git rule in Phase 7 step 4 was followed for whichever
repo the target turned out to be.
