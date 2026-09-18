#!/usr/bin/env python3
"""steering_inventory.py — enumerate every global Claude Code steering surface with usage evidence.

Read-only. An Instrument, never a Gate (see CONTEXT.md in claude-config): it informs a human
ruling and blocks nothing. Stdlib only. Deterministic.

A count that could not be measured is reported as unmeasured (`None` in JSON, an em dash in
markdown) and never as 0: a zero is only ever printed after the source behind it was read.

Exit codes:
  0  inventory complete
  2  a required source was missing or unreadable, or the command line was invalid
  3  a surface enumerated to zero items where files exist
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ------------------------------------------------------------------ tunables
# Every threshold this script applies lives here, so changing one is a single edit.

WINDOW_DEFAULT_DAYS = 90        # --since default: how far back "recent" reaches
HOT_MIN_USES = 5                # uses inside the window at or above this -> hot
WARM_MIN_USES = 1               # uses inside the window at or above this -> warm
AUTO_ONLY_MIN_AUTO = 5          # 0 typed and at least this many session-chosen -> auto_only
TRIGGER_PHRASE_MIN_CHARS = 8    # a shorter double-quoted run is a word, not a trigger phrase
TRIGGER_PHRASE_MAX_CHARS = 80   # a longer one is a quoted sentence nobody types verbatim
OVERSIZED_MIN_SIZED_ITEMS = 10  # below this a "top decile" is one item picked out of a handful
OVERSIZED_TOP_DECILE = 0.9      # rank at or above this fraction of its surface -> oversized
EVIDENCE_NAMES_MAX = 3          # names listed in one evidence cell before "+N more"

EXIT_OK = 0
EXIT_SOURCE_MISSING = 2
EXIT_USAGE = 2                  # argparse's convention; shares 2 with a missing source
EXIT_EMPTY_SURFACE = 3

# Every surface the inventory will eventually carry, in report order. CLAUDE.md sections sort
# last so the highest-judgment rows come after the mechanical ones.
SURFACE_ORDER = ["skill", "command", "agent", "output-style", "plugin", "mcp", "hook", "memory",
                 "claude-md"]

# The surfaces this build actually enumerates. Later tickets extend this list as their
# enumerators land; --surface validates against it so an unimplemented lane can never be
# mistaken for an empty one.
ENUMERATED_SURFACES = ["skill", "command", "agent", "output-style", "plugin", "mcp", "hook",
                       "memory", "claude-md"]

# Surfaces no usage source can score. Nothing in the prompt history or the transcripts names a
# hook entry or an auto-memory directory, so their counts stay unmeasured and their temperature
# is `unknown` — never `cold`, which would claim a disuse no source could have shown.
UNMEASURABLE_SURFACES = ("hook", "memory")

# Surfaces the markdown reports as one count instead of a row each: an auto-memory directory's
# name is a project path slug, and this report is committed to a public repo.
COUNT_ONLY_SURFACES = ("memory",)

# Coldest first: the rows that need a ruling come before the rows that earned their place.
TEMP_ORDER = {"cold": 0, "cool": 1, "new": 2, "warm": 3, "hot": 4, "unknown": 5}

# Surfaces with a spelling Kyle could type at a prompt. Nothing else can ever appear in the
# prompt history, so its typed counts stay unmeasured: an agent that reads `typed 0/90d · 0 all`
# invites the reading "Kyle never typed it" for something he could not have typed.
TYPED_SURFACES = ("skill", "command")

# The flags the precedence table reads. `auto_only` is deliberately absent: the spec calls it
# informational and says in so many words that it changes no proposal, so a `new` item that
# sessions keep choosing is still `new` alone. The flags later tickets added beyond the spec's
# list (`disabled`, `connector_only`, `denied`) are informational for the same reason — each
# describes how an item is reached, not whether it has earned its place.
PROPOSAL_FLAGS = ("kept", "duplicate", "disabled_comment", "empty", "paused", "unlinked",
                  "dangling", "oversized")

# Verdicts, sorted the way the proposals table shows them: the removals Kyle rules on first.
VERDICT_ORDER = {"retire": 0, "ask": 1, "relocate": 2}

LOCAL_CORPUS_CAVEAT = ("Usage evidence is this machine's local corpus only — every count is a "
                       "floor, never a ceiling.")

UNMEASURED = "—"


class SourceMissing(Exception):
    """A required evidence source is absent or unreadable."""


class EmptySurface(Exception):
    """A surface directory has entries but enumerated to zero items."""


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(errors="ignore"))
    except (OSError, ValueError) as e:
        raise SourceMissing(f"{path}: {e}") from e


# ---------------------------------------------------------------- parsing

FM_KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")
HEADING_RE = re.compile(r"^(#{1,3})\s+(.+?)\s*$")
BOLD_LEAD_RE = re.compile(r"^\*\*(.+?)\*\*")


def parse_frontmatter(text: str) -> dict:
    """Minimal YAML front matter: `key: value` lines between `---` fences.

    Supports `>`, `>-`, `|`, `|-` block scalars (folded joins with spaces, literal with
    newlines) — three live SKILL.md files use `description: >-`.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    out: dict = {}
    i = 1
    while i < len(lines) and lines[i].strip() != "---":
        m = FM_KEY_RE.match(lines[i])
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val in (">", ">-", "|", "|-"):
            block: list[str] = []
            i += 1
            while (i < len(lines) and lines[i].strip() != "---"
                   and (lines[i].startswith(" ") or lines[i].strip() == "")):
                block.append(lines[i].strip())
                i += 1
            joiner = " " if val.startswith(">") else "\n"
            out[key] = joiner.join(b for b in block if b).strip()
            continue
        out[key] = val.strip('"').strip("'")
        i += 1
    return out


def split_sections(text: str):
    """Yield (title, body, line_no) for every ##/### heading outside fenced code.

    A section's body runs to the next heading of the same or higher level.
    """
    lines = text.splitlines(keepends=True)
    heads: list[tuple[int, int, str]] = []
    in_fence = False
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING_RE.match(ln)
        if m and len(m.group(1)) >= 2:
            heads.append((i, len(m.group(1)), m.group(2)))
    for n, (i, level, title) in enumerate(heads):
        end = len(lines)
        for j, lvl, _ in heads[n + 1:]:
            if lvl <= level:
                end = j
                break
        yield title, "".join(lines[i:end]), i + 1


def split_bold_paragraphs(text: str):
    """Yield (name, body, line_no) for every paragraph whose first run is bold.

    `operating-constraints.md` carries no headings at all, so a heading splitter would see it as
    one undifferentiated blob. Its real unit is the bold-led paragraph — `**Scope discipline.**
    Do exactly what's asked…` — and that bold lead is the rule's name. Paragraphs with no bold
    lead (the file's preamble) are prose about the rules, not rules, and are not items.
    """
    para: list[str] = []
    start = 1
    for i, line in enumerate(text.splitlines(keepends=True) + [""], start=1):
        if line.strip():
            if not para:
                start = i
            para.append(line)
            continue
        if para:
            body = "".join(para)
            m = BOLD_LEAD_RE.match(body)
            if m:
                yield m.group(1).strip().rstrip(".:").strip(), body, start
            para = []


def phrases_from_description(desc: str) -> list[str]:
    """A description's double-quoted runs, lowercased and escaped for use as regexes.

    A skill or command description quotes the phrases Kyle would say to summon it ("red-team
    this diff"), so those quotes are the item's trigger phrases. Bounded by the tunables above:
    below the floor a quoted run is a single word that would match everything, above the ceiling
    it is a quoted sentence nobody retypes verbatim.
    """
    rx = rf'"([^"]{{{TRIGGER_PHRASE_MIN_CHARS},{TRIGGER_PHRASE_MAX_CHARS}}})"'
    return [re.escape(p.lower()) for p in re.findall(rx, desc)]


# ---------------------------------------------------------------- model

@dataclass
class Item:
    """One steering-surface item with its evidence.

    Counts Kyle typed himself (`slash_*`) are ints once the history is read. Counts a session
    chose on its own (`tool_*`) and trigger-phrase hits (`trigger_*`) are None until the source
    behind them is read — None renders as an em dash, never as 0.
    """

    id: str                              # "skill:reweave", "claude-md:Git Workflow"
    surface: str                         # one of SURFACE_ORDER
    name: str
    path: str
    bytes_always_loaded: int
    tracked: bool | None = None          # None = repo has no usable git
    paused: bool = False                 # commands/<x>.md.disabled
    description: str = ""
    slash_all: int | None = None         # typed by Kyle, all time (None = no typed spelling)
    slash_90d: int | None = None         # typed by Kyle, inside the window
    tool_all: int | None = None          # session-chosen (Skill / Agent / mcp__), all time
    tool_90d: int | None = None
    last_used: str | None = None         # ISO date
    trigger_all: int | None = None       # None = no trigger list known (reported as —, never 0)
    trigger_90d: int | None = None
    referrers: list[str] = field(default_factory=list)   # steering files that route here
    mentions: list[str] = field(default_factory=list)    # other tracked docs that describe it
    routes_to_missing: list[str] = field(default_factory=list)
    vendored_copies: list[str] = field(default_factory=list)
    duplicate_of: str | None = None
    added: str | None = None             # ISO date the item first appeared
    last_edited: str | None = None
    flags: list[str] = field(default_factory=list)
    temperature: str = "unknown"
    proposed: str | None = None          # None = omitted from the proposals table
    precedence: str | None = None        # key of the precedence row that decided both of those
    shown: bool = False                  # whether the proposals table carries a row of its own
    collapsed_into: str | None = None    # key of the collapsed row standing in for it
    extra: dict = field(default_factory=dict)

    @property
    def invocations_all(self) -> int:
        return (self.slash_all or 0) + (self.tool_all or 0)

    @property
    def invocations_90d(self) -> int:
        return (self.slash_90d or 0) + (self.tool_90d or 0)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["invocations_all"] = self.invocations_all
        d["invocations_90d"] = self.invocations_90d
        d["extra"] = {k: v for k, v in self.extra.items() if k != "body"}
        return d


@dataclass
class Config:
    claude_home: Path
    config_repo: Path
    projects_root: Path
    claude_json: Path
    since_days: int = WINDOW_DEFAULT_DAYS
    triggers: dict | None = None         # claude-md section title -> list[regex] | None
    cache_path: Path | None = None
    surfaces: tuple[str, ...] = tuple(ENUMERATED_SURFACES)


@dataclass
class Inventory:
    items: list
    totals: dict
    meta: dict
    collapsed: list = field(default_factory=list)   # one entry per collapsed class
    omitted: list = field(default_factory=list)     # one entry per suppressed precedence row


# ---------------------------------------------------------------- the precedence table
#
# Spec, Implementation Decisions: "Precedence table, top wins". The first row whose `test`
# holds decides both the proposed verdict and whether the item gets a row of its own, so the
# order of this tuple *is* the rule. Nothing else in the script decides a proposal.


@dataclass(frozen=True)
class PrecedenceRow:
    key: str                # stable label; names the class in the omitted summary and the JSON
    title: str              # what the row means, for a reader of the report
    proposed: str | None    # the verdict, or None for "kept silently"
    shown: bool             # whether the proposals table carries a row per item
    collapse: str | None    # None, "plugin" (one row per canonical plugin) or "class"
    test: object            # (item, window_start) -> bool


def _has_proposal_flag(it: "Item") -> bool:
    return any(f in PROPOSAL_FLAGS for f in it.flags)


def _paused_a_full_window(it: "Item", window_start: str) -> bool:
    """Whether a paused item has been paused for a window or more.

    A pause is dated by the last commit touching the paused file, or its mtime when untracked —
    `last_edited`, the one date the pause leaves behind. With no date at all the claim "this has
    been paused long enough to ask about" is one nothing measured, so it is not made.
    """
    return it.last_edited is not None and it.last_edited < window_start


PRECEDENCE_TABLE = (
    PrecedenceRow("kept", "ruled keep on purpose, recorded in the ledger", None, False, None,
                  lambda it, w: "kept" in it.flags),
    PrecedenceRow("duplicate", "a loose copy of a skill an enabled plugin already ships",
                  "retire", True, "plugin", lambda it, w: "duplicate" in it.flags),
    PrecedenceRow("mechanical", "comment-only hook entries and empty auto-memory directories",
                  "retire", True, "class",
                  lambda it, w: "disabled_comment" in it.flags or "empty" in it.flags),
    PrecedenceRow("paused-recent", "paused less than a window ago", None, False, None,
                  lambda it, w: "paused" in it.flags and not _paused_a_full_window(it, w)),
    PrecedenceRow("paused-long", "paused a full window or more, or in the repo but never loaded",
                  "ask", True, None,
                  lambda it, w: "paused" in it.flags or "unlinked" in it.flags),
    PrecedenceRow("new-flagged", "added inside the window and carrying a flag", "ask", True, None,
                  lambda it, w: it.temperature == "new" and _has_proposal_flag(it)),
    PrecedenceRow("new", "added inside the window, nothing else against it", None, False, None,
                  lambda it, w: it.temperature == "new"),
    PrecedenceRow("heavy", "earning its place but heavy enough to load on demand instead",
                  "relocate", True, None,
                  lambda it, w: it.temperature in ("hot", "warm") and "oversized" in it.flags),
    PrecedenceRow("hot-warm", "used inside the window", None, False, None,
                  lambda it, w: it.temperature in ("hot", "warm")),
    PrecedenceRow("cool", "unused in the window, but used or referenced before", "ask", True,
                  None, lambda it, w: it.temperature == "cool"),
    PrecedenceRow("cold", "no use in the window, nothing all-time, nothing routes to it",
                  "retire", True, None, lambda it, w: it.temperature == "cold"),
    # The floor. An item reaches it only when no source could score it — a live hook entry, a
    # memory directory holding files, a CLAUDE.md section with no trigger phrases in the sidecar.
    # `cold` would be a measured claim of disuse, and nothing here was measured, so the row is
    # counted and named rather than proposed on.
    PrecedenceRow("unmeasured", "no source could score it; nothing here is evidence of disuse",
                  None, False, None, lambda it, w: True),
)

PRECEDENCE_BY_KEY = {row.key: row for row in PRECEDENCE_TABLE}


# ---------------------------------------------------------------- config-repo surfaces

def git_tracked(repo: Path) -> set[str] | None:
    """Set of git-tracked relative paths, or None when the repo has no usable git."""
    try:
        out = subprocess.run(["git", "-C", str(repo), "ls-files"],
                             capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return {ln for ln in out.split("\n") if ln}


def first_added_dates(repo: Path) -> dict[str, str]:
    """Relative path -> ISO date of the first commit that added it.

    One `git log` pass over the whole repo rather than one per file, so a live run over a repo
    with thousands of commits stays a single subprocess.
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "log", "--reverse", "--diff-filter=A",
             "--format=\x01%aI", "--name-only"],
            capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return {}
    dates: dict[str, str] = {}
    current: str | None = None
    for line in out.split("\n"):
        if line.startswith("\x01"):
            current = line[1:11]
        elif line and current:
            dates.setdefault(line, current)
    return dates


def _tracked_flag(tracked: set[str] | None, rel: str) -> bool | None:
    return None if tracked is None else rel in tracked


def _mtime_date(path: Path) -> str | None:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).date().isoformat()
    except OSError:
        return None


def added_date(path: Path, rel: str, added: dict[str, str]) -> str | None:
    """First-commit date for a tracked file; modification date when git cannot say."""
    return added.get(rel) or _mtime_date(path)


def enumerate_skills(config_repo: Path, tracked: set[str] | None,
                     added: dict[str, str] | None = None) -> list[Item]:
    """House skills: one item per `skills/<name>/SKILL.md` that git tracks.

    Untracked (gitignored) skill copies are a separate surface and are skipped here. When the
    repo has no usable git nothing can be classified, so every skill is listed with tracked=None.
    """
    root = config_repo / "skills"
    if not root.is_dir():
        raise SourceMissing(f"skills directory missing: {root}")
    added = added or {}
    items: list[Item] = []
    dirs = [d for d in sorted(root.iterdir()) if d.is_dir()]
    for d in dirs:
        sk = d / "SKILL.md"
        if not sk.is_file():
            continue
        rel = f"skills/{d.name}/SKILL.md"
        is_tracked = _tracked_flag(tracked, rel)
        if is_tracked is False:
            continue
        desc = parse_frontmatter(sk.read_text(errors="ignore")).get("description", "")
        items.append(Item(id=f"skill:{d.name}", surface="skill", name=d.name, path=str(sk),
                          bytes_always_loaded=len(desc), tracked=is_tracked, description=desc,
                          added=added_date(sk, rel, added)))
    if not items and dirs:
        raise EmptySurface(f"skill: {root} has directories but no tracked SKILL.md files")
    return items


def enumerate_untracked_skills(config_repo: Path, tracked: set[str] | None) -> list[Item]:
    """Gitignored skill directories: vendored third-party copies the repo deliberately ignores.

    They are invisible to `git ls-files` but not to a session — the harness loads their
    descriptions like any other skill's, so they cost the same bytes and steer the same routing.
    Their added date is the directory's mtime; git has nothing to say about a file it ignores.
    When the repo has no usable git nothing can be classified as ignored, and `enumerate_skills`
    has already listed every directory with tracked=None, so this returns nothing.
    """
    root = config_repo / "skills"
    if tracked is None or not root.is_dir():
        return []
    items: list[Item] = []
    for d in sorted(root.iterdir()):
        if not d.is_dir():
            continue
        sk = d / "SKILL.md"
        if not sk.is_file() or f"skills/{d.name}/SKILL.md" in tracked:
            continue
        desc = parse_frontmatter(sk.read_text(errors="ignore")).get("description", "")
        items.append(Item(id=f"skill:{d.name}", surface="skill", name=d.name, path=str(sk),
                          bytes_always_loaded=len(desc), tracked=False, description=desc,
                          added=_mtime_date(d)))
    return items


def _md_items(root: Path, surface: str, tracked: set[str] | None, config_repo: Path,
              added: dict[str, str] | None = None,
              suffixes: tuple[str, ...] = (".md",)) -> list[Item]:
    """One item per markdown file directly under `root`, in filename order.

    `suffixes` is tried in order, so `.md.disabled` must precede `.md`; a file matched by a
    `.disabled` suffix is paused, and a paused file costs a session nothing, so its
    always-loaded weight is 0 rather than its description's length.
    """
    if not root.is_dir():
        return []
    added = added or {}
    items: list[Item] = []
    entries = [f for f in sorted(root.iterdir()) if f.is_file()]
    for f in entries:
        name = None
        paused = False
        for suf in suffixes:
            if f.name.endswith(suf):
                name, paused = f.name[: -len(suf)], suf.endswith(".disabled")
                break
        if not name:
            continue
        desc = parse_frontmatter(f.read_text(errors="ignore")).get("description", "")
        rel = str(f.relative_to(config_repo))
        it = Item(id=f"{surface}:{name}", surface=surface, name=name, path=str(f),
                  bytes_always_loaded=0 if paused else len(desc),
                  tracked=_tracked_flag(tracked, rel), paused=paused, description=desc,
                  added=added_date(f, rel, added))
        if paused:
            it.flags.append("paused")
        items.append(it)
    if not items and entries:
        raise EmptySurface(f"{surface}: {root} has files but none of them are items")
    return items


def enumerate_commands(config_repo: Path, tracked: set[str] | None,
                       added: dict[str, str] | None = None) -> list[Item]:
    """Slash commands, paused ones included: a `.md.disabled` is a ruling, not an absence."""
    return _md_items(config_repo / "commands", "command", tracked, config_repo, added,
                     suffixes=(".md.disabled", ".md"))


def enumerate_agents(config_repo: Path, tracked: set[str] | None,
                     added: dict[str, str] | None = None) -> list[Item]:
    return _md_items(config_repo / "agents", "agent", tracked, config_repo, added)


def enumerate_output_styles(config_repo: Path, tracked: set[str] | None,
                            added: dict[str, str] | None = None,
                            claude_home: Path | None = None) -> list[Item]:
    """Output styles, each flagged `unlinked` when the harness has no way to load it.

    A style only reaches a session through `<claude home>/output-styles/<name>.md`. With no such
    directory — or no entry in it for this style — the file is in the repo and nowhere else:
    dead weight that is invisible from inside a session, which is exactly why it needs a flag.
    """
    items = _md_items(config_repo / "output-styles", "output-style", tracked, config_repo, added)
    linked = claude_home / "output-styles" if claude_home else None
    for it in items:
        if linked is None or not (linked / f"{it.name}.md").exists():
            it.flags.append("unlinked")
    return items


def first_commit_containing(repo: Path, rel: str, needle: str) -> str | None:
    """ISO date of the earliest commit whose change to `rel` introduced `needle`.

    A section of a file has no add-date of its own — the file's first commit is the file's, not
    the section's, and would date every rule in CLAUDE.md to the day the file was created. The
    pickaxe finds the commit that actually introduced the heading.
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "log", "--reverse", "--format=%aI", "-S", needle,
             "--", rel],
            capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    for line in out.split("\n"):
        if line.strip():
            return line[:10]
    return None


def enumerate_claude_md(config_repo: Path, tracked: set[str] | None = None,
                        added: dict[str, str] | None = None) -> list[Item]:
    """The always-loaded prose: constraints paragraphs first, then CLAUDE.md's own sections.

    Constraints lead because CLAUDE.md imports that file at the top, so that is the order a
    session reads them in. A section's bytes are its own length, heading line included; a `###`
    nests inside its `##`, so the surface total is taken from the files rather than from this
    sum (see `claude_md_file_bytes`).
    """
    cm = config_repo / "CLAUDE.md"
    if not cm.is_file():
        raise SourceMissing(f"CLAUDE.md missing: {cm}")
    items: list[Item] = []
    for rel, splitter in (("operating-constraints.md", split_bold_paragraphs),
                          ("CLAUDE.md", split_sections)):
        path = config_repo / rel
        if not path.is_file():
            continue
        text = path.read_text(errors="ignore")
        for name, body, line_no in splitter(text):
            when = (first_commit_containing(config_repo, rel, _needle(body))
                    if tracked is not None else None)
            items.append(Item(
                id=f"claude-md:{name}", surface="claude-md", name=name, path=str(path),
                bytes_always_loaded=len(body), tracked=_tracked_flag(tracked, rel),
                added=when or added_date(path, rel, added or {}),
                extra={"body": body, "line": line_no, "file": rel}))
    if not items:
        raise EmptySurface(f"claude-md: {cm} holds no ##/### headings")
    return items


def _needle(body: str) -> str:
    """The shortest run of a section or paragraph that identifies it in a diff.

    For a section that is its heading line; for a bold-led paragraph, the bold lead.
    """
    m = BOLD_LEAD_RE.match(body)
    return m.group(0) if m else body.splitlines()[0].strip()


def claude_md_file_bytes(config_repo: Path) -> int:
    """Always-loaded weight of the claude-md surface, measured from the files themselves.

    Summing the items would double-count: a `###` section's body is also inside its `##`
    parent's, and neither covers the preamble above the first heading. The files are the truth.
    """
    total = 0
    for rel in ("CLAUDE.md", "operating-constraints.md"):
        path = config_repo / rel
        if path.is_file():
            total += len(path.read_text(errors="ignore"))
    return total


# ---------------------------------------------------------------- claude-home surfaces
#
# Plugins, MCP servers, hook entries and auto-memory directories: the steering that reaches a
# session from the claude home rather than from the config repo. None of it is under git, so
# none of it has a first-commit date — only a plugin carries an install date of its own.


def _plugin_short(key: str) -> str:
    """`mattpocock-skills@mattpocock` -> `mattpocock-skills`: the namespace a session sees."""
    return key.split("@", 1)[0]


def _install_date(value) -> str | None:
    """An `installedAt` stamp as an ISO date.

    Live records write ISO-8601 (`2026-08-21T18:46:48.710Z`); older ones write epoch
    milliseconds. Both spellings are in the wild, so both are accepted, and an unusable stamp
    reports no date at all rather than a wrong one.
    """
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)) or (isinstance(value, str) and value.strip().isdigit()):
        try:
            return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc).date().isoformat()
        except (ValueError, OverflowError, OSError):
            return None
    dt = _parse_iso(value)
    return dt.date().isoformat() if dt else None


def plugin_skills(install: Path) -> list[dict]:
    """Every SKILL.md a plugin ships, at whatever depth it sits.

    `mattpocock-skills` nests them as `skills/engineering/<name>/SKILL.md`, so the walk has to be
    recursive; the frontmatter `name` wins over the directory name because that is the spelling a
    session calls the skill by.
    """
    out: list[dict] = []
    if not install.is_dir():
        return out
    for sk in sorted(install.rglob("SKILL.md")):
        fm = parse_frontmatter(sk.read_text(errors="ignore"))
        out.append({"name": fm.get("name") or sk.parent.name,
                    "description": fm.get("description", ""), "path": str(sk)})
    return out


def enumerate_plugins(claude_home: Path) -> list[Item]:
    """One item per installed plugin, enabled or not.

    A disabled plugin still occupies the surface — it is installed, and one CLI verb from being
    live again — but it costs a session nothing, so its always-loaded weight is 0 and it carries
    `disabled`. An enabled plugin's weight is the sum of its shipped skill descriptions, which is
    exactly what every request pays for it.
    """
    settings = load_json(claude_home / "settings.json")
    installed = load_json(claude_home / "plugins" / "installed_plugins.json")
    enabled = settings.get("enabledPlugins") or {}
    items: list[Item] = []
    for key, entries in sorted((installed.get("plugins") or {}).items()):
        entry = (entries[0] if entries else {}) if isinstance(entries, list) else entries
        entry = entry if isinstance(entry, dict) else {}
        skills = plugin_skills(Path(entry.get("installPath") or ""))
        is_enabled = bool(enabled.get(key, False))
        it = Item(id=f"plugin:{key}", surface="plugin", name=key,
                  path=str(entry.get("installPath") or ""),
                  bytes_always_loaded=(sum(len(s["description"]) for s in skills)
                                       if is_enabled else 0),
                  added=_install_date(entry.get("installedAt")),
                  extra={"enabled": is_enabled, "short": _plugin_short(key),
                         "version": entry.get("version"), "skills": skills})
        if not is_enabled:
            it.flags.append("disabled")
        items.append(it)
    return items


def plugin_skill_canonicals(plugins: list[Item]) -> dict[str, str]:
    """Skill name -> the canonical `<plugin short>:<skill>` spelling of the plugin that ships it.

    Enabled plugins only: a disabled plugin ships nothing into a session, so a loose copy of one
    of its skills is the only copy there is and duplicates nothing.
    """
    out: dict[str, str] = {}
    for p in plugins:
        if not p.extra.get("enabled"):
            continue
        short = p.extra.get("short") or _plugin_short(p.name)
        for s in p.extra.get("skills") or []:
            out.setdefault(s["name"], f"{short}:{s['name']}")
    return out


def flag_duplicate_skills(items: list[Item], canonicals: dict[str, str]) -> None:
    """An untracked house skill an enabled plugin already ships is listed twice in every session.

    Tracked skills are Kyle's own and are left alone even on a name collision; the untracked ones
    are what `npx skills` dropped into `skills/` beside a plugin that already carries them, which
    is why `duplicate_of` names the plugin spelling that survives the copy's removal.
    """
    for it in items:
        if it.surface == "skill" and it.tracked is False and it.name in canonicals:
            it.duplicate_of = canonicals[it.name]
            if "duplicate" not in it.flags:
                it.flags.append("duplicate")


MCP_NAME_RE = re.compile(r"[^0-9A-Za-z_-]+")


def mcp_key(name: str) -> str:
    """A server name as a transcript spells it: `claude.ai Gmail` -> `claude_ai_Gmail`.

    Tool names are `mcp__<server>__<tool>`, and the harness flattens what cannot appear in one —
    dots, spaces, apostrophes — to underscores. Hyphens and underscores survive untouched
    (`mcp__basic-memory__search`), so flattening them too would split every hyphenated server
    into two rows: one configured with no calls, one "connector" carrying all of them.
    """
    return MCP_NAME_RE.sub("_", name)


def enumerate_mcp(claude_json: Path, claude_home: Path,
                  observed: list[str] | None = None) -> list[Item]:
    """The union of the user-scope config and every server a transcript actually called.

    A claude.ai connector is configured on the website and appears in no local config file, so
    the config alone would report a surface smaller than the one steering Kyle's sessions.
    Anything seen only in the transcripts is flagged `connector_only` — it reaches sessions from
    outside the user-scope config — except a plugin's own server, whose weight already belongs to
    its plugin's row. A server on the deny list carries `denied`.
    """
    configured = load_json(claude_json).get("mcpServers") or {}
    settings = load_json(claude_home / "settings.json")
    denied = set()
    for entry in settings.get("deniedMcpServers") or []:
        name = entry.get("serverName") if isinstance(entry, dict) else entry
        if isinstance(name, str) and name:
            denied.add(mcp_key(name))

    rows: dict[str, dict] = {}
    for name in sorted(configured):
        cfg = configured[name]
        rows[mcp_key(name)] = {"name": name, "origin": "config",
                               "cfg": cfg if isinstance(cfg, dict) else {}}
    for key in sorted(observed or []):
        rows.setdefault(key, {"name": key, "cfg": {},
                              "origin": "plugin" if key.startswith("plugin_") else "connector"})

    items: list[Item] = []
    for key in sorted(rows):
        row = rows[key]
        cfg = row["cfg"]
        it = Item(id=f"mcp:{row['name']}", surface="mcp", name=row["name"],
                  path=str(claude_json) if row["origin"] == "config" else "",
                  bytes_always_loaded=0,
                  extra={"origin": row["origin"], "key": key, "transport": cfg.get("type"),
                         "command": cfg.get("command")})
        if row["origin"] == "connector":
            it.flags.append("connector_only")
        if key in denied:
            it.flags.append("denied")
        items.append(it)
    return items


def enumerate_hooks(claude_home: Path) -> list[Item]:
    """One item per hook entry, named by its position in the settings file and nothing else.

    A hook command is a shell line carrying absolute paths, and the markdown report is committed
    to a public repo — so the name a row renders under is its position (`Stop[1][0]`) and the
    command text stays in the JSON, which never leaves the local cache. The text is kept there
    because a prompt-type hook is part of the referrer corpus: the Stop hook names three
    CLAUDE.md modes by title, and retiring one of them has to patch that prompt.

    A command that is entirely a comment is a hook Kyle already switched off by commenting it
    out. It still sits in the file, so it is still an item, and it carries `disabled_comment`.
    """
    settings = load_json(claude_home / "settings.json")
    items: list[Item] = []
    for event, groups in sorted((settings.get("hooks") or {}).items()):
        for gi, group in enumerate(groups or []):
            group = group if isinstance(group, dict) else {}
            for hi, hook in enumerate(group.get("hooks") or []):
                hook = hook if isinstance(hook, dict) else {}
                cmd = hook.get("command") or hook.get("prompt") or ""
                cmd = cmd if isinstance(cmd, str) else ""
                it = Item(id=f"hook:{event}[{gi}][{hi}]", surface="hook",
                          name=f"{event}[{gi}][{hi}]",
                          path=str(claude_home / "settings.json"), bytes_always_loaded=0,
                          extra={"event": event, "group": gi, "index": hi,
                                 "matcher": group.get("matcher"), "type": hook.get("type"),
                                 "command": cmd})
                if cmd.lstrip().startswith("#"):
                    it.flags.append("disabled_comment")
                items.append(it)
    return items


def enumerate_memory(claude_home: Path) -> list[Item]:
    """One item per auto-memory directory under the projects tree.

    The directory name is a project path slug, which is why the markdown reports this surface as
    a count and never by name (see `COUNT_ONLY_SURFACES`). A directory holding nothing carries
    `empty`: most of them are leftovers from projects that no longer exist.
    """
    items: list[Item] = []
    for mem in sorted((claude_home / "projects").glob("*/memory")):
        if not mem.is_dir():
            continue
        files = [f for f in sorted(mem.rglob("*")) if f.is_file()]
        size = 0
        for f in files:
            try:
                size += f.stat().st_size
            except OSError:
                continue
        it = Item(id=f"memory:{mem.parent.name}", surface="memory", name=mem.parent.name,
                  path=str(mem), bytes_always_loaded=size, extra={"files": len(files)})
        if not files:
            it.flags.append("empty")
        items.append(it)
    return items


def plugin_usage(it: Item, transcripts: "Transcripts",
                 since: datetime) -> tuple[int, int, str | None]:
    """A plugin's session-chosen uses: its skills, its namespaced agents, and its own MCP servers.

    A plugin is never invoked by name — what a session reaches for is one of the things it ships:
    a skill (bare or namespaced), an agent dispatched as `<plugin>:<agent>`, or one of the MCP
    servers it registers, which the harness names `mcp__plugin_<plugin>_<server>__<tool>`.
    Summing those is a measurement taken from the same transcript pass everything else uses;
    without it a heavily-used plugin would read as unused, which is the one thing this script
    must never say about a source it did read.

    Its slash commands are the one thing not counted here: they are typed, not chosen, and the
    live history holds seven of them across every plugin that has any other evidence at all.
    """
    short = _plugin_short(it.name)
    prefixes = (f"plugin_{short}_", f"plugin_{short.replace('-', '_')}_")
    keys: list[tuple[str, object]] = [("skill", skill_spellings(s["name"], short))
                                      for s in it.extra.get("skills") or []]
    keys += [("agent", k) for k in transcripts.keys("agent") if k.startswith(f"{short}:")]
    keys += [("mcp", k) for k in transcripts.keys("mcp") if k.startswith(prefixes)]
    total = recent = 0
    last: str | None = None
    for kind, key in keys:
        seen_all, seen_recent, seen_last = transcripts.count(kind, key, since)
        total += seen_all
        recent += seen_recent
        if seen_last and (last is None or seen_last > last):
            last = seen_last
    return total, recent, last


# ---------------------------------------------------------------- evidence: history.jsonl

def slash_pattern(name: str) -> str:
    """Regex for a prompt that starts with /<name> and nothing that extends the name.

    `/handoff` must never count for `/hand`, and `/mp:tdd` must never count for `/tdd`.
    """
    return r"^\s*/" + re.escape(name) + r"(?![\w:-])"


class History:
    """The prompt history — what Kyle typed himself."""

    def __init__(self, path: Path):
        if not path.exists():
            raise SourceMissing(f"history file missing: {path}")
        self.path = path
        self.rows: list[tuple[datetime, str]] = []
        try:
            fh = open(path, errors="ignore")
        except OSError as e:
            raise SourceMissing(f"history file unreadable: {path}: {e}") from e
        with fh:
            for line in fh:
                try:
                    d = json.loads(line)
                    dt = datetime.fromtimestamp(int(d.get("timestamp")) / 1000, tz=timezone.utc)
                except (ValueError, TypeError, OverflowError, AttributeError):
                    continue
                self.rows.append((dt, (d.get("display") or "").lower()))
        if not self.rows:
            raise SourceMissing(f"history file parsed to zero rows: {path}")

    def count_any(self, patterns: list[str], since: datetime) -> tuple[int, int, str | None]:
        """(all-time hits, hits inside the window, ISO date of the latest hit)."""
        rx = re.compile("|".join(f"(?:{p})" for p in patterns), re.I)
        total = recent = 0
        last: datetime | None = None
        for dt, text in self.rows:
            if rx.search(text):
                total += 1
                if dt >= since:
                    recent += 1
                if last is None or dt > last:
                    last = dt
        return total, recent, (last.date().isoformat() if last else None)

    def count(self, pattern: str, since: datetime) -> tuple[int, int, str | None]:
        return self.count_any([pattern], since)


# ---------------------------------------------------------------- evidence: transcripts

# Transcript lines are compact JSON (no spaces after colons), so these needles are exact. Every
# line is substring-filtered before the JSON parser ever sees it: the corpus is gigabytes and the
# overwhelming majority of lines carry no tool call at all.
NEEDLES = ('"name":"Skill"', '"name":"Agent"', '"name":"mcp__')


def skill_spellings(name: str, namespace: str | None = None) -> list[str]:
    """Every Skill-call spelling that belongs to one skill.

    A plugin skill is reachable both bare and namespaced (`tdd` and `mp:tdd`) and both spellings
    count for it. A house skill has no namespace and answers to its bare name only — a namespaced
    call went to the plugin, not to the loose copy sitting beside it.
    """
    return [name] if namespace is None else [name, f"{namespace}:{name}"]


def _parse_iso(ts) -> datetime | None:
    """Transcript timestamps are ISO-8601 with a `Z`. None when the stamp is unusable."""
    try:
        dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def extract_events(path: Path) -> list[list] | None:
    """[[iso_ts, kind, key], ...] for every Skill / Agent / mcp__ tool call in one transcript.

    None means the file could not be read at all — distinct from a file that read cleanly and
    held no tool calls, which is an empty list. That distinction is what keeps an unreadable
    corpus from being reported as a corpus of zeroes.

    A line that is malformed, truncated, or shaped unexpectedly is skipped; one bad line never
    costs the rest of the file, and never aborts the run.
    """
    out: list[list] = []
    try:
        fh = open(path, errors="ignore")
    except OSError:
        return None
    try:
        with fh:
            for line in fh:
                if not any(n in line for n in NEEDLES):
                    continue
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(d, dict):
                    continue
                ts, msg = d.get("timestamp"), d.get("message")
                if not ts or not isinstance(msg, dict):
                    continue
                for c in msg.get("content") or []:
                    if not (isinstance(c, dict) and c.get("type") == "tool_use"):
                        continue
                    name = c.get("name")
                    if not isinstance(name, str):
                        continue
                    inp = c.get("input")
                    inp = inp if isinstance(inp, dict) else {}
                    if name == "Skill" and inp.get("skill"):
                        out.append([ts, "skill", str(inp["skill"])])
                    elif name == "Agent" and inp.get("subagent_type"):
                        out.append([ts, "agent", str(inp["subagent_type"])])
                    elif name.startswith("mcp__"):
                        parts = name.split("__")
                        if len(parts) >= 2 and parts[1]:
                            out.append([ts, "mcp", parts[1]])
    except OSError:
        return None
    return out


class Transcripts:
    """Session-chosen usage — what a session reached for without being told to.

    Skill tool calls, Agent dispatches and `mcp__<server>__*` names, read once per file and
    cached by path, size and mtime so a re-run over a multi-gigabyte corpus only reads what
    changed. Agent and MCP tallies are collected in the same pass the skill counts come from;
    the surfaces that consume them land later.

    Zero readable transcripts is a missing source, never a corpus of zeroes.
    """

    def __init__(self, root: Path, cache_path: Path | None = None):
        self.root = root
        files = sorted(root.rglob("*.jsonl")) if root.is_dir() else []
        cache = self._load_cache(cache_path)
        fresh: dict = {}
        self.cache_hits = 0
        self.files_unreadable = 0
        self.events: list[tuple[datetime, str, str]] = []
        self._index: dict[tuple[str, str], list[datetime]] = {}
        for p in files:
            try:
                st = p.stat()
            except OSError:
                self.files_unreadable += 1
                continue
            key = str(p)
            hit = cache.get(key)
            if (isinstance(hit, dict) and hit.get("size") == st.st_size
                    and hit.get("mtime") == st.st_mtime):
                events = hit.get("events") or []
                self.cache_hits += 1
            else:
                events = extract_events(p)
                if events is None:
                    self.files_unreadable += 1
                    continue
            fresh[key] = {"size": st.st_size, "mtime": st.st_mtime, "events": events}
            self._ingest(events)
        self.files_found = len(files)
        self.files_scanned = len(fresh)
        if not self.files_scanned:
            raise SourceMissing(f"no readable transcripts under {root} "
                                f"({self.files_found} found, {self.files_unreadable} unreadable)")
        self._write_cache(cache_path, fresh)

    def _ingest(self, events) -> None:
        for row in events:
            try:
                ts, kind, key = row
            except (TypeError, ValueError):
                continue
            dt = _parse_iso(ts)
            if dt is None:
                continue
            self.events.append((dt, kind, key))
            self._index.setdefault((kind, key), []).append(dt)

    def keys(self, kind: str) -> list[str]:
        """Every key of one kind that appeared anywhere in the corpus.

        This is what makes the MCP surface the union of the config and what sessions actually
        called: a claude.ai connector is in no local file, so the transcripts are the only place
        its name exists.
        """
        return sorted(k for kd, k in self._index if kd == kind)

    def count(self, kind: str, key, since: datetime) -> tuple[int, int, str | None]:
        """(all-time hits, hits inside the window, ISO date of the latest hit).

        `key` may be one spelling or several; several are counted as one item, which is how a
        plugin skill's bare and namespaced calls add up (see `skill_spellings`).
        """
        keys = [key] if isinstance(key, str) else list(key)
        total = recent = 0
        last: datetime | None = None
        for k in keys:
            for dt in self._index.get((kind, k), ()):
                total += 1
                if dt >= since:
                    recent += 1
                if last is None or dt > last:
                    last = dt
        return total, recent, (last.date().isoformat() if last else None)

    @staticmethod
    def _load_cache(cache_path: Path | None) -> dict:
        """An unreadable or corrupt cache is not an error: it just means reading everything."""
        if not cache_path or not cache_path.exists():
            return {}
        try:
            data = json.loads(cache_path.read_text())
        except (OSError, ValueError):
            return {}
        return data if isinstance(data, dict) else {}

    @staticmethod
    def _write_cache(cache_path: Path | None, fresh: dict) -> None:
        """Only the files seen this run are kept, so the cache cannot outgrow the corpus."""
        if not cache_path:
            return
        try:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(json.dumps(fresh))
        except OSError as e:
            print(f"WARN transcript cache not written ({e}); the next run re-reads everything",
                  file=sys.stderr)


# ---------------------------------------------------------------- cross-references
#
# Who routes to an item (referrers), who merely talks about it (mentions), which of its own
# routes point at something that is gone (dangling), which project repos carry a copy of it,
# whether the ledger already records a keep ruling for it, and when it was last edited.
#
# Only referrers feed temperature. A doc that describes an item is prose to repair on the way
# out; a steering file that routes to it is something that breaks, which is the whole reason
# `cool` exists as a class distinct from `cold`.

# The three docs that describe the steering surface rather than steer with it. Each already has
# its own step in the apply order — the index row, the playbook card, the ledger line — so
# counting them here would report the skill's own bookkeeping back as a reason not to retire.
INDEX_DOC_REL = "docs/command-skill-reference.md"
PLAYBOOK_REL = "docs/usage-playbook.md"
LEDGER_REL = "docs/retired.md"
BOOKKEEPING_DOCS = (INDEX_DOC_REL, PLAYBOOK_REL, LEDGER_REL)

# Surfaces whose name is a position (`Stop[0][1]`) or a private path slug rather than something
# a file could route to. Matching those as words would find nothing and leak the slug trying.
UNNAMEABLE_SURFACES = ("hook", "memory")

# Surfaces the fleet can carry a copy of: a project's `.claude/` mirrors skills, commands and
# agents by file, and a project's own CLAUDE.md can carry a copy of a global section.
VENDORABLE_SURFACES = ("skill", "command", "agent", "claude-md")

# An item id is surface-qualified (`skill:reweave`). A route in prose is not — it is written
# `/reweave` — so a ledger id has to shed its prefix before it can be matched against one.
SURFACE_PREFIX_RE = re.compile(
    r"^(?:" + "|".join(re.escape(s) for s in sorted(SURFACE_ORDER, key=len, reverse=True))
    + r"):")

# A ledger row opens with an ISO date in its first cell; every other table line does not.
LEDGER_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}\b")
LEDGER_KEPT_HEADING_RE = re.compile(r"^#{1,6}\s+Kept on purpose\s*$", re.I | re.M)


def steering_files(config_repo: Path) -> list[Path]:
    """Every file in the repo that can route a session somewhere: the steering corpus.

    Skills (their reference files too, not just the SKILL.md — a route lives wherever it is
    written), commands including the paused ones, agents, and the two always-loaded prose files.
    """
    files: list[Path] = []
    skills = config_repo / "skills"
    if skills.is_dir():
        files += sorted(skills.rglob("*.md"))
    for sub, pattern in (("commands", "*.md*"), ("agents", "*.md")):
        d = config_repo / sub
        if d.is_dir():
            files += sorted(d.glob(pattern))
    files += [config_repo / "CLAUDE.md", config_repo / "operating-constraints.md"]
    return [p for p in files if p.is_file()]


def build_corpus(config_repo: Path, claude_home: Path) -> dict[str, str]:
    """Referrer corpus: path -> text, plus one entry per prompt-type hook.

    A prompt hook is a steering file that happens to live in JSON: the Stop hook names CLAUDE.md
    modes by title, and retiring one of them has to patch that prompt. Its key is the hook's own
    id spelling (`settings.json:Stop[0][0]`) so a referrer found here names the row that carries
    it — the prompt text itself never leaves this dict.
    """
    corpus = {str(p): p.read_text(errors="ignore") for p in steering_files(config_repo)}
    settings_path = claude_home / "settings.json"
    if not settings_path.is_file():
        return corpus
    try:
        settings = load_json(settings_path)
    except SourceMissing:
        return corpus
    for event, groups in sorted((settings.get("hooks") or {}).items()):
        for gi, group in enumerate(groups or []):
            group = group if isinstance(group, dict) else {}
            for hi, hook in enumerate(group.get("hooks") or []):
                hook = hook if isinstance(hook, dict) else {}
                if hook.get("type") != "prompt":
                    continue
                prompt = hook.get("prompt")
                corpus[f"settings.json:{event}[{gi}][{hi}]"] = (
                    prompt if isinstance(prompt, str) else "")
    return corpus


def build_mention_corpus(config_repo: Path, tracked: set[str] | None,
                         referrers: dict[str, str]) -> dict[str, str]:
    """Mention corpus: every other tracked markdown file, minus the three bookkeeping docs.

    A mention is prose that would describe something that no longer exists — a README, a design
    record, a third-party note. It is a repair the apply step owes, never evidence of use, which
    is why it is kept apart from the referrer corpus and never reaches temperature.

    Tracked is the filter because an untracked markdown file is not something a PR can edit.
    When the repo has no usable git nothing can be classified as tracked, so the corpus falls
    back to the markdown actually on disk — a superset, measured from a source that was read,
    and `meta.git_tracked` says which of the two happened.
    """
    excluded = set(referrers) | {str(config_repo / rel) for rel in BOOKKEEPING_DOCS}
    if tracked is None:
        paths = sorted(config_repo.rglob("*.md"))
    else:
        paths = sorted(config_repo / rel for rel in tracked if rel.endswith(".md"))
    return {str(p): p.read_text(errors="ignore")
            for p in paths if str(p) not in excluded and p.is_file()}


def _display_name(it: Item) -> str:
    """The name a file would route to. A plugin is written by its short name, never its key."""
    if it.surface == "plugin":
        return it.extra.get("short") or _plugin_short(it.name)
    return it.name


def _own_paths(it: Item, config_repo: Path) -> set[str]:
    """The files that are the item itself — a skill describing itself is not a referrer."""
    if it.surface == "skill":
        return {str(q) for q in Path(it.path).parent.rglob("*.md")}
    if it.surface == "claude-md":
        return {str(config_repo / "CLAUDE.md"), str(config_repo / "operating-constraints.md")}
    return {it.path}


def _name_matches(it: Item, corpus: dict[str, str], config_repo: Path) -> list[str]:
    """Corpus keys whose text carries the item's name as a whole word, its own files aside.

    Word-boundary on both sides and hyphen-aware: `handoff-session` must not count as a hit for
    `handoff`, and `alphabet` must not count for `alpha`.
    """
    rx = re.compile(r"(?<![\w-])" + re.escape(_display_name(it)) + r"(?![\w-])", re.I)
    own = _own_paths(it, config_repo)
    return sorted(k for k, text in corpus.items() if k not in own and rx.search(text))


def attach_referrers(it: Item, corpus: dict[str, str], config_repo: Path) -> None:
    """Steering files that route to this item. The only cross-reference that feeds temperature."""
    if it.surface in UNNAMEABLE_SURFACES:
        return
    it.referrers = _name_matches(it, corpus, config_repo)


def attach_mentions(it: Item, corpus: dict[str, str], config_repo: Path) -> None:
    """Tracked docs that merely talk about this item: prose the apply step owes a repair."""
    if it.surface in UNNAMEABLE_SURFACES:
        return
    it.mentions = _name_matches(it, corpus, config_repo)


def strip_surface_prefix(item_id: str) -> str:
    """`skill:zeta` -> `zeta`: the spelling a route in prose would actually use."""
    return SURFACE_PREFIX_RE.sub("", item_id, count=1)


def _ledger_table_ids(text: str) -> set[str]:
    """Item ids from every date-led row of a ledger table."""
    ids: set[str] = set()
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 2 and LEDGER_DATE_RE.match(cells[0]):
            item = re.sub(r"\s*\(.*\)$", "", cells[1].strip("`").strip())
            if item:
                ids.add(item)
    return ids


def ledger_ids(config_repo: Path) -> tuple[set[str], set[str]]:
    """(retired ids, kept ids) from the ledger's two tables. No ledger yet means two empty sets.

    An absent ledger is not a missing source: before the first retirement there is nothing to
    read, and both answers are honestly empty rather than unknown.
    """
    path = config_repo / LEDGER_REL
    if not path.is_file():
        return set(), set()
    text = path.read_text(errors="ignore")
    m = LEDGER_KEPT_HEADING_RE.search(text)
    retired_text, kept_text = (text[:m.start()], text[m.start():]) if m else (text, "")
    return _ledger_table_ids(retired_text), _ledger_table_ids(kept_text)


def paused_command_names(config_repo: Path) -> set[str]:
    """Commands renamed to `.disabled`.

    Read from the directory rather than from the enumerated rows, so a `--surface skill` run
    still sees them: a dangling route is a fact about the referrer, not about the lane swept.
    """
    root = config_repo / "commands"
    if not root.is_dir():
        return set()
    suffix = ".md.disabled"
    return {f.name[: -len(suffix)] for f in root.iterdir()
            if f.is_file() and f.name.endswith(suffix)}


def missing_names(config_repo: Path) -> set[str]:
    """Every name a route can dangle on: paused commands plus everything the ledger retired.

    A paused command still has a file, so a route to it resolves to nothing a session can run;
    a retired one has no file at all. Both are routes that need patching, and the ledger's ids
    are surface-qualified, so they shed their prefix to match the way a route is written.
    """
    retired, _ = ledger_ids(config_repo)
    names = paused_command_names(config_repo) | {strip_surface_prefix(i) for i in retired}
    return {n for n in names if n}


def kept_ids(config_repo: Path) -> set[str]:
    """Surface-qualified ids Kyle already ruled `keep`, from the ledger's kept table."""
    return ledger_ids(config_repo)[1]


def attach_kept(it: Item, kept: set[str]) -> None:
    """A recorded keep ruling is not re-litigated; the flag is what suppresses the row later."""
    if it.id in kept and "kept" not in it.flags:
        it.flags.append("kept")


def _item_text(it: Item) -> str:
    """The item's own text — where its outgoing routes are written."""
    if it.surface == "claude-md":
        return it.extra.get("body", "")
    if it.surface == "hook":
        return it.extra.get("command", "")
    if it.surface in ("skill", "command", "agent", "output-style"):
        try:
            return Path(it.path).read_text(errors="ignore")
        except OSError:
            return ""
    return ""


def attach_dangling(it: Item, missing: set[str]) -> None:
    """Routes this item writes that resolve to nothing runnable.

    A route is strict: `/name` or `` `name` ``. Bare prose words are not routes — several of
    these names are ordinary English (`learn`, `old`), and counting every sentence that happens
    to use one would bury the handful of routes that genuinely need patching.
    """
    text = _item_text(it)
    hits = sorted(n for n in missing
                  if n != it.name and re.search(r"(?:/|`)" + re.escape(n) + r"(?![\w-])", text))
    it.routes_to_missing = hits
    if hits and "dangling" not in it.flags:
        it.flags.append("dangling")


def _claude_md_carries(repo: Path, name: str) -> bool:
    """Whether a project's own CLAUDE.md carries a section (or constraints paragraph) by name.

    A global rule copied into a project is a copy by heading, not by file, so the match is on
    the same units the global surface is split into.
    """
    for rel in ("CLAUDE.md", ".claude/CLAUDE.md"):
        path = repo / rel
        if not path.is_file():
            continue
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        titles = {t for t, _, _ in split_sections(text)}
        titles |= {t for t, _, _ in split_bold_paragraphs(text)}
        if name in titles:
            return True
    return False


def _is_the_config_repo(repo: Path, config_repo: Path | None) -> bool:
    """Whether a directory under the projects root is the config repo itself, or a worktree of it.

    The config repo is the source of every global item, not a downstream copy of one — counting
    it would report the global CLAUDE.md back as evidence that the global CLAUDE.md is vendored
    somewhere. Its worktrees are the same repo at another commit and say the same thing twice.
    A worktree's `.git` is a file naming the main repo's git directory, which is how one is
    recognised without shelling out.
    """
    if config_repo is None:
        return False
    try:
        if repo.resolve() == config_repo.resolve():
            return True
        dot_git = repo / ".git"
        if dot_git.is_file():
            pointer = dot_git.read_text(errors="ignore").strip()
            if pointer.startswith("gitdir:"):
                target = Path(pointer.split(":", 1)[1].strip())
                return str(target).startswith(str((config_repo / ".git").resolve()))
    except OSError:
        return False
    return False


def vendored_copies(projects_root: Path, it: Item, config_repo: Path | None = None) -> list[str]:
    """Repo directory names under the projects root that carry a copy of this item.

    Names, never paths: this repo is public and the report is committed to it. The fleet is
    report-only — knowing the blast radius is the whole point, and no edit is ever made here.
    """
    if it.surface not in VENDORABLE_SURFACES or not projects_root.is_dir():
        return []
    hits: list[str] = []
    for repo in sorted(projects_root.iterdir()):
        if not repo.is_dir() or _is_the_config_repo(repo, config_repo):
            continue
        dot = repo / ".claude"
        if it.surface == "skill":
            found = (dot / "skills" / it.name / "SKILL.md").is_file()
        elif it.surface == "command":
            found = (dot / "commands" / f"{it.name}.md").is_file()
        elif it.surface == "agent":
            found = (dot / "agents" / f"{it.name}.md").is_file()
        else:
            found = _claude_md_carries(repo, it.name)
        if found:
            hits.append(repo.name)
    return hits


def git_last_edited(repo: Path, rel: str) -> str | None:
    """ISO date of the last commit touching a path, or None when git cannot say."""
    try:
        out = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%as", "--", rel],
                             capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    return out or None


def last_edited(config_repo: Path, it: Item) -> str | None:
    """When the item's own files last changed: git for tracked items, mtime for everything else.

    An untracked skill is invisible to git by construction, and mtime is the only date it has.
    A skill is dated by its whole directory, because a rewrite of its reference file is an edit
    to the skill even when SKILL.md never moved.
    """
    if it.surface not in ("skill", "command", "agent", "output-style"):
        return None
    path = Path(it.path)
    target = path.parent if it.surface == "skill" else path
    if it.tracked:
        try:
            rel = str(target.relative_to(config_repo))
        except ValueError:
            rel = None
        if rel:
            found = git_last_edited(config_repo, rel)
            if found:
                return found
    return _mtime_date(target)


# ---------------------------------------------------------------- assembly

def note_last_used(it: Item, *dates: str | None) -> None:
    """Last used is the latest date across every source that measured this item."""
    it.last_used = max((d for d in (it.last_used, *dates) if d), default=None)


def attach_usage(it: Item, history: History, transcripts: Transcripts, since: datetime) -> None:
    """Typed counts from the prompt history, session-chosen counts from the transcripts.

    Only skills and commands have a typed spelling (`TYPED_SURFACES`); an agent, an MCP server
    and a plugin are reached by a session on its own, so the transcripts are their whole
    evidence and their typed counts stay unmeasured rather than reading a measured 0 for
    something Kyle could not have typed. A surface with no source at all is left alone here.
    """
    if it.surface in TYPED_SURFACES:
        it.slash_all, it.slash_90d, last_typed = history.count(slash_pattern(it.name), since)
        it.tool_all, it.tool_90d, last_auto = transcripts.count(
            "skill", skill_spellings(it.name), since)
        note_last_used(it, last_typed, last_auto)
    elif it.surface == "agent":
        it.tool_all, it.tool_90d, last_auto = transcripts.count("agent", it.name, since)
        note_last_used(it, last_auto)
    elif it.surface == "mcp":
        it.tool_all, it.tool_90d, last_auto = transcripts.count(
            "mcp", it.extra.get("key") or it.name, since)
        note_last_used(it, last_auto)
    elif it.surface == "plugin":
        it.tool_all, it.tool_90d, last_auto = plugin_usage(it, transcripts, since)
        note_last_used(it, last_auto)


def flag_auto_only(it: Item) -> None:
    """Kyle never types it, but sessions keep choosing it.

    Informational only — `auto_only` is evidence about how an item is reached, not a reason to
    retire or keep it, so it never touches `proposed`.
    """
    if (it.surface in TYPED_SURFACES and (it.slash_90d or 0) == 0
            and (it.tool_90d or 0) >= AUTO_ONLY_MIN_AUTO and "auto_only" not in it.flags):
        it.flags.append("auto_only")


def attach_triggers(it: Item, history: History, since: datetime, triggers: dict | None) -> None:
    """Trigger-phrase hits from the prompt history.

    A CLAUDE.md section is never typed by name, so its only usage evidence is how often Kyle
    said something that should have fired it — and that list of phrases can only come from the
    sidecar. No entry, or a `null` entry, means no phrase is a fair proxy for the rule, so the
    counts stay None and render as unmeasured. Reporting 0 there would read as "never fired",
    which is the one thing this script must never claim about a source it did not read.
    """
    if it.surface == "claude-md":
        pats = (triggers or {}).get(it.name)
    elif it.surface in ("skill", "command"):
        pats = phrases_from_description(it.description)
    else:
        pats = None
    if not pats:
        return
    it.trigger_all, it.trigger_90d, last = history.count_any(pats, since)
    if last and (it.last_used is None or last > it.last_used):
        it.last_used = last


def _measured(*counts: int | None) -> list[int]:
    """Only the counts a source actually produced. An unmeasured source contributes nothing —
    not a zero, which would be indistinguishable from a source that was read and found empty."""
    return [c for c in counts if c is not None]


def temperature(it: Item, window_start: str) -> str:
    """`new` wins over every count; otherwise recent uses decide, then any evidence at all.

    `cold` is a *measured* claim that an item went unused, so it is only ever reached when some
    source was read and came back empty. An item no source could score — a hook entry, a memory
    directory, a CLAUDE.md section with no trigger phrases in the sidecar — is `unknown`. Folding
    the unmeasured counts through `or 0` instead would manufacture the very zero the whole script
    exists to refuse, and `cold` proposes `retire`.
    """
    if it.added and it.added >= window_start:
        return "new"
    if it.surface in UNMEASURABLE_SURFACES:
        return "unknown"
    recent = _measured(it.slash_90d, it.tool_90d, it.trigger_90d)
    if sum(recent) >= HOT_MIN_USES:
        return "hot"
    if sum(recent) >= WARM_MIN_USES:
        return "warm"
    ever = _measured(it.slash_all, it.tool_all, it.trigger_all)
    if it.referrers or sum(ever):
        return "cool"
    if not ever:
        return "unknown"
    return "cold"


def propose(it: Item, window_start: str) -> PrecedenceRow:
    """Walk the precedence table top-down; the first row that holds decides.

    Sets `proposed`, `shown` and `precedence` on the item and hands the winning row back so the
    caller can collapse on it.
    """
    for row in PRECEDENCE_TABLE:
        if row.test(it, window_start):
            it.proposed, it.shown, it.precedence = row.proposed, row.shown, row.key
            return row
    raise AssertionError(f"precedence table fell through for {it.id}")   # pragma: no cover


def mark_oversized(items: list[Item]) -> None:
    """Top decile of always-loaded bytes within a surface, when the surface has enough items.

    Only sized items rank: a paused command and a disabled plugin cost a session nothing, so
    they are not "the heavy end" of anything. Under `OVERSIZED_MIN_SIZED_ITEMS` a top decile is
    one item picked out of a handful, which is a ranking dressed up as a finding.
    """
    by_surface: dict[str, list[Item]] = {}
    for it in items:
        if it.bytes_always_loaded > 0:
            by_surface.setdefault(it.surface, []).append(it)
    for sized in by_surface.values():
        if len(sized) < OVERSIZED_MIN_SIZED_ITEMS:
            continue
        sized.sort(key=lambda i: i.bytes_always_loaded)
        cutoff = sized[int(len(sized) * OVERSIZED_TOP_DECILE)].bytes_always_loaded
        for it in sized:
            if it.bytes_always_loaded >= cutoff and "oversized" not in it.flags:
                it.flags.append("oversized")


def _collapse_key(it: Item, row: PrecedenceRow) -> str | None:
    """Which collapsed row an item belongs to, or None when it keeps a row of its own."""
    if row.collapse == "plugin":
        canonical = it.duplicate_of or ""
        return f"duplicate:{canonical.split(':', 1)[0]}" if canonical else None
    if row.collapse == "class":
        flag = "disabled_comment" if "disabled_comment" in it.flags else "empty"
        return f"{it.surface}:{flag}"
    return None


def _collapse_title(key: str, members: list[Item]) -> str:
    """What a collapsed row says in the Item column. Never a member's name: a memory slug is a
    private project path, and 36 loose copies of one plugin's skills are one judgment call."""
    n = len(members)
    kind, _, what = key.partition(":")
    if kind == "duplicate":
        return f"{n} loose skill {'copy' if n == 1 else 'copies'} of plugin {what}"
    if what == "disabled_comment":
        return f"{n} hook {'entry' if n == 1 else 'entries'} commented out"
    return f"{n} empty auto-memory {'directory' if n == 1 else 'directories'}"


def collapse_rows(items: list[Item], window_start: str) -> list[dict]:
    """Fold the mechanical classes into one row each, so trivia does not bury the judgment calls.

    Members keep their own records — every field, every flag — and simply stop carrying a row of
    their own; `collapsed_into` says which row stands in for them, and the row names its members
    in the JSON so an apply pass can act on all of them from one ruling.
    """
    groups: dict[str, list[Item]] = {}
    for it in items:
        row = PRECEDENCE_BY_KEY.get(it.precedence or "")
        if row is None or not row.collapse:
            continue
        key = _collapse_key(it, row)
        if key:
            groups.setdefault(key, []).append(it)
    out = []
    for key in sorted(groups):
        members = groups[key]
        for it in members:
            it.shown, it.collapsed_into = False, key
        row = PRECEDENCE_BY_KEY[members[0].precedence]
        out.append({"key": key, "surface": members[0].surface, "title": _collapse_title(key, members),
                    "proposed": row.proposed, "precedence": row.key, "count": len(members),
                    "members": [m.id for m in members],
                    "member_names": [m.name for m in members],
                    "bytes_always_loaded": sum(m.bytes_always_loaded for m in members)})
    return out


def omitted_summary(items: list[Item]) -> list[dict]:
    """One entry per precedence row that suppresses items, in the table's own order.

    Collapsed members are not counted here: they are represented in the proposals table by their
    collapsed row, not omitted from it. Names of items on a count-only surface are never listed —
    a memory directory is named for the project path it belongs to and this report is public.
    """
    suppressed = [it for it in items if not it.shown and it.collapsed_into is None]
    out = []
    for row in PRECEDENCE_TABLE:
        if row.shown:
            continue
        members = [it for it in suppressed if it.precedence == row.key]
        # `hot`/`warm` is a silent keep: the spec counts it and stops. Everything else is named.
        nameable = (row.key != "hot-warm"
                    and [m for m in members if m.surface not in COUNT_ONLY_SURFACES])
        out.append({"key": row.key, "title": row.title, "count": len(members),
                    "names": sorted(m.name for m in nameable) if nameable else [],
                    "ids": sorted(m.id for m in members)})
    return out


def compute_totals(items: list[Item], surfaces: tuple[str, ...],
                   config_repo: Path | None = None) -> dict:
    """Always-loaded weight per enumerated surface. Surfaces not read are absent, not zero."""
    totals = {s: {"items": 0, "always_loaded_chars": 0} for s in SURFACE_ORDER if s in surfaces}
    for it in items:
        bucket = totals.setdefault(it.surface, {"items": 0, "always_loaded_chars": 0})
        bucket["items"] += 1
        bucket["always_loaded_chars"] += it.bytes_always_loaded
    # Nested CLAUDE.md sections overlap, so their sum overstates the surface: measure the files.
    if "claude-md" in totals and config_repo is not None:
        totals["claude-md"]["always_loaded_chars"] = claude_md_file_bytes(config_repo)
    totals["ALL"] = {"items": sum(v["items"] for v in totals.values()),
                     "always_loaded_chars": sum(v["always_loaded_chars"] for v in totals.values())}
    return totals


def build_inventory(cfg: Config) -> Inventory:
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=cfg.since_days)
    window_start = since.date().isoformat()

    # Evidence first: a surface must never be counted before the source that scores it was read.
    history = History(cfg.claude_home / "history.jsonl")
    transcripts = Transcripts(cfg.claude_home / "projects", cfg.cache_path)

    tracked = git_tracked(cfg.config_repo)
    added = first_added_dates(cfg.config_repo)
    # The plugin cache is read whenever skills are, filtered out or not: a loose skill copy can
    # only be called a duplicate against the plugin that ships the canonical one.
    plugins: list[Item] = []
    if {"plugin", "skill"} & set(cfg.surfaces):
        plugins = enumerate_plugins(cfg.claude_home)

    items: list[Item] = []
    if "skill" in cfg.surfaces:
        skills = (enumerate_skills(cfg.config_repo, tracked, added)
                  + enumerate_untracked_skills(cfg.config_repo, tracked))
        flag_duplicate_skills(skills, plugin_skill_canonicals(plugins))
        items += skills
    if "command" in cfg.surfaces:
        items += enumerate_commands(cfg.config_repo, tracked, added)
    if "agent" in cfg.surfaces:
        items += enumerate_agents(cfg.config_repo, tracked, added)
    if "output-style" in cfg.surfaces:
        items += enumerate_output_styles(cfg.config_repo, tracked, added, cfg.claude_home)
    if "plugin" in cfg.surfaces:
        items += plugins
    if "mcp" in cfg.surfaces:
        items += enumerate_mcp(cfg.claude_json, cfg.claude_home, transcripts.keys("mcp"))
    if "hook" in cfg.surfaces:
        items += enumerate_hooks(cfg.claude_home)
    if "memory" in cfg.surfaces:
        items += enumerate_memory(cfg.claude_home)
    if "claude-md" in cfg.surfaces:
        items += enumerate_claude_md(cfg.config_repo, tracked, added)

    # Cross-references are built from the repo rather than from the enumerated rows, so a
    # `--surface` run still resolves a route to a command it did not list.
    corpus = build_corpus(cfg.config_repo, cfg.claude_home)
    mention_corpus = build_mention_corpus(cfg.config_repo, tracked, corpus)
    missing = missing_names(cfg.config_repo)
    kept = kept_ids(cfg.config_repo)

    for it in items:
        attach_usage(it, history, transcripts, since)
        attach_triggers(it, history, since, cfg.triggers)
        flag_auto_only(it)
        attach_referrers(it, corpus, cfg.config_repo)
        attach_mentions(it, mention_corpus, cfg.config_repo)
        attach_dangling(it, missing)
        attach_kept(it, kept)
        it.vendored_copies = vendored_copies(cfg.projects_root, it, cfg.config_repo)
        it.last_edited = last_edited(cfg.config_repo, it)
        # Referrers are in place before this line by design: they are what makes `cool` real.
        it.temperature = temperature(it, window_start)

    # Both of these read the whole item list, so they come after it is complete: `oversized` is
    # a rank within a surface, and the precedence table reads `oversized`.
    mark_oversized(items)
    for it in items:
        propose(it, window_start)
    collapsed = collapse_rows(items, window_start)
    omitted = omitted_summary(items)

    meta = {
        "since_days": cfg.since_days,
        "since": window_start,
        "generated": now.isoformat(timespec="seconds"),
        "surfaces": list(cfg.surfaces),
        "history_rows": len(history.rows),
        "transcripts_scanned": transcripts.files_scanned,
        "transcripts_cache_hits": transcripts.cache_hits,
        "transcripts_unreadable": transcripts.files_unreadable,
        "git_tracked": tracked is not None,
        "thresholds": {"window_default_days": WINDOW_DEFAULT_DAYS, "hot_min_uses": HOT_MIN_USES,
                       "warm_min_uses": WARM_MIN_USES, "auto_only_min_auto": AUTO_ONLY_MIN_AUTO,
                       "oversized_min_sized_items": OVERSIZED_MIN_SIZED_ITEMS,
                       "oversized_top_decile": OVERSIZED_TOP_DECILE},
        "config_repo": str(cfg.config_repo),
        "claude_home": str(cfg.claude_home),
        "caveat": LOCAL_CORPUS_CAVEAT,
    }
    return Inventory(items=items, totals=compute_totals(items, cfg.surfaces, cfg.config_repo),
                     meta=meta, collapsed=collapsed, omitted=omitted)


# ---------------------------------------------------------------- output

def _fmt(n: int | None) -> str:
    return UNMEASURED if n is None else str(n)


def _name_cell(name: str) -> str:
    """A name as a code span inside a table cell.

    CLAUDE.md heading names are arbitrary prose: an unescaped `|` would end the cell early and a
    bare backtick would close the span mid-name, and the name has to survive verbatim because it
    is the key Kyle rules by and the key the trigger sidecar is keyed on.
    """
    safe = name.replace("|", "\\|")
    fence = "``" if "`" in safe else "`"
    pad = " " if safe.startswith("`") or safe.endswith("`") else ""
    return f"{fence}{pad}{safe}{pad}{fence}"


def _name_list(names: list[str], limit: int = EVIDENCE_NAMES_MAX) -> str:
    """The first few names, then how many more. A table cell is a pointer, not a manifest."""
    head = ", ".join(names[:limit])
    extra = len(names) - limit
    return f"{head} +{extra} more" if extra > 0 else head


def evidence_summary(it: Item, since_days: int) -> str:
    """One cell of counts, dates and names. Never a path, and never a count nobody measured.

    Referrers and mentions are reported as counts: which files they are is a fact about the
    apply step, lives in the local JSON, and would put private paths in a public report.
    Vendored copies are named, because repo basenames are what a later fleet prune needs and
    are the one downstream detail the redaction rules allow — but only the first few of them:
    one CLAUDE.md section is vendored in 23 repos, and 23 repo names in a table cell is the
    right content in the wrong place. The full list is in the JSON the ledger reads.
    """
    parts = [f"typed {_fmt(it.slash_90d)}/{since_days}d · {_fmt(it.slash_all)} all",
             f"auto {_fmt(it.tool_90d)}/{_fmt(it.tool_all)}",
             f"trig {_fmt(it.trigger_90d)}/{_fmt(it.trigger_all)}",
             f"last {it.last_used or UNMEASURED}",
             f"added {it.added or UNMEASURED}",
             f"edited {it.last_edited or UNMEASURED}",
             f"refs {len(it.referrers)}",
             f"mentions {len(it.mentions)}",
             f"{it.bytes_always_loaded:,} chars"]
    if it.vendored_copies:
        parts.append("vendored in " + _name_list(it.vendored_copies))
    if it.duplicate_of:
        parts.append(f"dup of `{it.duplicate_of}`")
    if it.routes_to_missing:
        parts.append("routes→ " + _name_list(it.routes_to_missing))
    return " · ".join(parts)


def count_only_summary(surface: str, rows: list) -> str:
    """One line standing in for every row of a surface whose names cannot be printed.

    An auto-memory directory is named for the project path it belongs to, so printing the names
    would publish Kyle's private project list in a public repo. The count, how many are empty and
    what the rest weigh is everything a ruling needs; the names are in the local JSON.
    """
    empty = sum(1 for i in rows if "empty" in i.flags)
    chars = sum(i.bytes_always_loaded for i in rows)
    return (f"{len(rows)} {surface} entries · {empty} flagged `empty` · "
            f"{len(rows) - empty} holding files · {chars:,} chars. "
            f"Names are project path slugs and are not printed; they are in the local JSON.")


def proposal_rows(inv: Inventory) -> list[dict]:
    """The rows that need a ruling, in the order Kyle rules them.

    Grouped by surface with CLAUDE.md last (the highest-judgment rows come once the mechanical
    ones are settled), `retire` first inside a surface, then `ask`, then `relocate`, heaviest
    first inside that. Collapsed rows sort with the items they stand in for.
    """
    # A count-only surface never renders a row of its own here, whatever the precedence table
    # says: a memory directory's name is a project path slug and this report is public. Their
    # rulings reach the table through collapsed rows, whose titles are counts.
    rows = [{"surface": i.surface, "title": _name_cell(i.name), "proposed": i.proposed,
             "evidence": None, "flags": i.flags, "temperature": i.temperature, "item": i}
            for i in inv.items if i.shown and i.surface not in COUNT_ONLY_SURFACES]
    for c in inv.collapsed:
        names = ("" if c["surface"] in COUNT_ONLY_SURFACES
                 else _name_list([_name_cell(n) for n in sorted(c["member_names"])]))
        rows.append({"surface": c["surface"], "title": c["title"], "proposed": c["proposed"],
                     "evidence": (f"{c['count']} item{'' if c['count'] == 1 else 's'} · "
                                  f"{c['bytes_always_loaded']:,} chars"
                                  + (f" · {names}" if names else "")),
                     "flags": ["collapsed"], "temperature": UNMEASURED, "item": None})
    rows.sort(key=lambda r: (SURFACE_ORDER.index(r["surface"]),
                             VERDICT_ORDER.get(r["proposed"], 9),
                             -(r["item"].bytes_always_loaded if r["item"] else 0),
                             r["title"]))
    return rows


def render_proposals(inv: Inventory) -> list[str]:
    """The table Kyle rules from: one numbered row per judgment call and nothing else."""
    rows = proposal_rows(inv)
    out = ["## Proposals", "",
           f"{len(rows)} rows need a ruling. Grouped by surface with `claude-md` last; `retire` "
           "first inside a surface, then `ask`, then `relocate`. Everything else is omitted and "
           "summarised below.", ""]
    if not rows:
        return out + ["Nothing on this run.", ""]
    out += ["| # | Surface | Item | Proposed | Evidence | Flags | Temp |",
            "|---|---|---|---|---|---|---|"]
    for n, r in enumerate(rows, 1):
        evidence = (r["evidence"] if r["evidence"] is not None
                    else evidence_summary(r["item"], inv.meta["since_days"]))
        out.append(f"| {n} | {r['surface']} | {r['title']} | {r['proposed'] or UNMEASURED} | "
                   f"{evidence} | {', '.join(r['flags']) or UNMEASURED} | {r['temperature']} |")
    return out + [""]


def render_omitted(inv: Inventory) -> list[str]:
    """Why every other row is not in front of Kyle, by count and — where it is safe — by name."""
    out = ["## Omitted from the proposals", "",
           "Each line is one row of the precedence table doing its job. Names are listed except "
           "for the silent keeps, which are counted, and for surfaces whose names are private.",
           ""]
    for entry in inv.omitted:
        names = f": {', '.join(_name_cell(n) for n in entry['names'])}" if entry["names"] else ""
        # A count that outruns its name list is the count-only surfaces being withheld, not a
        # name quietly dropped: say so rather than leaving the arithmetic to the reader.
        held = entry["count"] - len(entry["names"])
        if names and held:
            names += f" (+{held} on a surface whose names are private)"
        out.append(f"- **{entry['key']}** — {entry['title']} — {entry['count']}{names}")
    auto = sorted(i.name for i in inv.items if "auto_only" in i.flags)
    listed = f": {', '.join(_name_cell(n) for n in auto)}" if auto else ""
    out += [f"- **auto_only** — never typed, but sessions keep choosing it (evidence, not a "
            f"verdict) — {len(auto)}{listed}", ""]
    return out


def render_markdown(inv: Inventory) -> str:
    """The redacted view: names, counts and dates only — no paths, no private detail."""
    m = inv.meta
    scanned = _fmt(m["transcripts_scanned"])
    out = [f"# Steering inventory — {m['generated'][:10]}", "",
           f"Window: last {m['since_days']} days (since {m['since']}). "
           f"History rows: {m['history_rows']:,}. Transcripts scanned: {scanned} "
           f"({_fmt(m['transcripts_cache_hits'])} from cache). "
           f"Surfaces: {', '.join(m['surfaces'])}.", "",
           m["caveat"], "",
           "Read-only; an Instrument, never a Gate. An em dash is unmeasured, never zero.", "",
           "## Totals", "", "| Surface | Items | Always-loaded chars |", "|---|---|---|"]
    for s in [x for x in SURFACE_ORDER if x in inv.totals] + ["ALL"]:
        t = inv.totals[s]
        out.append(f"| {s} | {t['items']} | {t['always_loaded_chars']:,} |")
    out += [""] + render_proposals(inv) + render_omitted(inv)
    out += ["## Full inventory", "",
            "Every item the run read, proposals and omissions alike, with the evidence behind "
            "its row."]
    for s in SURFACE_ORDER:
        rows = sorted((i for i in inv.items if i.surface == s),
                      key=lambda i: (TEMP_ORDER.get(i.temperature, 9), -i.bytes_always_loaded,
                                     i.name))
        if not rows:
            continue
        if s in COUNT_ONLY_SURFACES:
            out += ["", f"## {s}", "", count_only_summary(s, rows)]
            continue
        out += ["", f"## {s}", "", "| Item | Evidence | Flags | Temp | Proposed |",
                "|---|---|---|---|---|"]
        for i in rows:
            out.append(f"| {_name_cell(i.name)} | {evidence_summary(i, m['since_days'])} | "
                       f"{', '.join(i.flags) or UNMEASURED} | {i.temperature} | "
                       f"{i.proposed or UNMEASURED} |")
    return "\n".join(out) + "\n"


def render_json(inv: Inventory) -> str:
    """The full view: every field, paths included. Written to the local cache, never committed."""
    return json.dumps({"meta": inv.meta, "totals": inv.totals, "collapsed": inv.collapsed,
                       "omitted": inv.omitted, "items": [i.to_dict() for i in inv.items]},
                      indent=1)


def render_totals_delta(before: dict, after: dict) -> str:
    """Always-loaded weight per surface, before against after, from two JSON runs.

    The token-weight goal is a measurement or it is nothing (spec story 52): the PR body carries
    this table, taken from two runs of this script, rather than a claim written by hand.
    """
    surfaces = [s for s in SURFACE_ORDER if s in before.get("totals", {})
                or s in after.get("totals", {})] + ["ALL"]
    stamp = (str(before.get("meta", {}).get("generated", UNMEASURED))[:10],
             str(after.get("meta", {}).get("generated", UNMEASURED))[:10])
    out = [f"## Always-loaded weight — {stamp[0]} → {stamp[1]}", "",
           "| Surface | Items | Before chars | After chars | Delta |", "|---|---|---|---|---|"]
    for s in surfaces:
        b = before.get("totals", {}).get(s) or {"items": 0, "always_loaded_chars": 0}
        a = after.get("totals", {}).get(s) or {"items": 0, "always_loaded_chars": 0}
        delta = a["always_loaded_chars"] - b["always_loaded_chars"]
        out.append(f"| {s} | {b['items']} → {a['items']} | {b['always_loaded_chars']:,} | "
                   f"{a['always_loaded_chars']:,} | {delta:+,} |")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- CLI

def _default_config_repo(claude_home: Path) -> Path:
    """The config repo is whatever `<claude home>/skills` resolves into."""
    skills = claude_home / "skills"
    if skills.is_symlink():
        return skills.resolve().parent
    return claude_home


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Read-only inventory of every global Claude Code steering surface.")
    ap.add_argument("--since", type=int, default=WINDOW_DEFAULT_DAYS,
                    help=f"window in days (default {WINDOW_DEFAULT_DAYS})")
    ap.add_argument("--json", help="write the full inventory as JSON here")
    ap.add_argument("--md", help="write the redacted markdown report here "
                                 "(default: stdout when --json is absent)")
    ap.add_argument("--claude-home", default=os.path.expanduser("~/.claude"))
    ap.add_argument("--config-repo", default=None,
                    help="default: resolved target of <claude home>/skills")
    ap.add_argument("--projects-root", default=os.path.expanduser("~/Projects"))
    ap.add_argument("--claude-json", default=os.path.expanduser("~/.claude.json"))
    ap.add_argument("--triggers", default=None,
                    help="JSON: CLAUDE.md section title -> [regex,...] | null "
                         "(default: claude_md_triggers.json beside this script)")
    ap.add_argument("--no-cache", action="store_true",
                    help="do not read or write the transcript cache")
    ap.add_argument("--surface", default=None, help="restrict the inventory to one surface")
    ap.add_argument("--compare", nargs=2, metavar=("BEFORE", "AFTER"), default=None,
                    help="two JSON files from earlier runs: print the before/after totals table "
                         "with deltas and exit, reading nothing else")
    args = ap.parse_args(argv)

    if args.compare:
        try:
            before, after = (load_json(Path(p)) for p in args.compare)
        except SourceMissing as e:
            print(f"ERROR comparison input missing or unreadable: {e}", file=sys.stderr)
            return EXIT_SOURCE_MISSING
        table = render_totals_delta(before, after)
        if args.md:
            Path(args.md).write_text(table)
        else:
            sys.stdout.write(table)
        return EXIT_OK

    if args.surface is not None and args.surface not in ENUMERATED_SURFACES:
        print(f"ERROR unknown surface {args.surface!r}; valid surfaces: "
              f"{', '.join(ENUMERATED_SURFACES)}", file=sys.stderr)
        return EXIT_USAGE
    surfaces = (args.surface,) if args.surface else tuple(ENUMERATED_SURFACES)

    claude_home = Path(args.claude_home)
    config_repo = Path(args.config_repo) if args.config_repo else _default_config_repo(claude_home)
    triggers_path = (Path(args.triggers) if args.triggers
                     else Path(__file__).with_name("claude_md_triggers.json"))
    triggers = None
    if triggers_path.exists():
        try:
            triggers = load_json(triggers_path)
        except SourceMissing as e:
            print(f"ERROR triggers file unreadable: {e}", file=sys.stderr)
            return EXIT_SOURCE_MISSING

    cache = None if args.no_cache else claude_home / "cache" / "retire" / "transcripts.json"
    cfg = Config(claude_home=claude_home, config_repo=config_repo,
                 projects_root=Path(args.projects_root), claude_json=Path(args.claude_json),
                 since_days=args.since, triggers=triggers, cache_path=cache, surfaces=surfaces)
    try:
        inv = build_inventory(cfg)
    except SourceMissing as e:
        print(f"ERROR source missing or unreadable — refusing to report a false 0: {e}",
              file=sys.stderr)
        return EXIT_SOURCE_MISSING
    except EmptySurface as e:
        print(f"ERROR surface enumerated to zero items where files exist: {e}", file=sys.stderr)
        return EXIT_EMPTY_SURFACE

    if args.json:
        Path(args.json).write_text(render_json(inv))
    md = render_markdown(inv)
    if args.md:
        Path(args.md).write_text(md)
    elif not args.json:
        sys.stdout.write(md)
    print(f"OK {inv.totals['ALL']['items']} items · "
          f"{inv.totals['ALL']['always_loaded_chars']:,} always-loaded chars · "
          f"{inv.meta['history_rows']:,} history rows", file=sys.stderr)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
