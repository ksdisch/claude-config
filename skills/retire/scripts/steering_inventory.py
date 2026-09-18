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
ENUMERATED_SURFACES = ["skill"]

# Coldest first: the rows that need a ruling come before the rows that earned their place.
TEMP_ORDER = {"cold": 0, "cool": 1, "new": 2, "warm": 3, "hot": 4, "unknown": 5}

# Minimal precedence: temperature alone decides. The full table (flags, collapse, oversized)
# replaces this mapping; keep the single source of truth here when it does.
PROPOSED_BY_TEMPERATURE = {
    "cold": "retire",
    "cool": "ask",
    "warm": None,               # None = omitted from the ratification table, kept silently
    "hot": None,
    "new": None,
    "unknown": None,
}

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
    slash_all: int = 0                   # typed by Kyle, all time
    slash_90d: int = 0                   # typed by Kyle, inside the window
    tool_all: int | None = None          # session-chosen (Skill / Agent / mcp__), all time
    tool_90d: int | None = None
    last_used: str | None = None         # ISO date
    trigger_all: int | None = None       # None = no trigger list known (reported as —, never 0)
    trigger_90d: int | None = None
    referrers: list[str] = field(default_factory=list)
    routes_to_missing: list[str] = field(default_factory=list)
    vendored_copies: list[str] = field(default_factory=list)
    duplicate_of: str | None = None
    added: str | None = None             # ISO date the item first appeared
    last_edited: str | None = None
    flags: list[str] = field(default_factory=list)
    temperature: str = "unknown"
    proposed: str | None = None          # None = omitted from the ratification table
    extra: dict = field(default_factory=dict)

    @property
    def invocations_all(self) -> int:
        return self.slash_all + (self.tool_all or 0)

    @property
    def invocations_90d(self) -> int:
        return self.slash_90d + (self.tool_90d or 0)

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


# ---------------------------------------------------------------- claude-home surfaces
#
# Plugins, MCP servers, hook entries and auto-memory directories are enumerated here. Not yet
# built; add the enumerators to this section and their surface names to ENUMERATED_SURFACES.


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
#
# Session-chosen usage (Skill tool calls, Agent dispatches, mcp__<server>__ tool names) with a
# per-file cache keyed by path, size and mtime. Not yet built: until it is, tool_* stays None
# and renders as unmeasured rather than as 0.


# ---------------------------------------------------------------- cross-references
#
# Referrers (steering files that route to an item) versus mentions (every other tracked doc),
# dangling routes, vendored copies in the fleet, plugin duplicates, ledger read-back. Not yet
# built: until it is, `referrers` stays empty and only usage feeds temperature.


# ---------------------------------------------------------------- assembly

def attach_usage(it: Item, history: History, since: datetime) -> None:
    """Typed counts from the prompt history. Session-chosen counts come from the transcripts."""
    if it.surface in ("skill", "command"):
        it.slash_all, it.slash_90d, last = history.count(slash_pattern(it.name), since)
        if last and (it.last_used is None or last > it.last_used):
            it.last_used = last


def temperature(it: Item, window_start: str) -> str:
    """`new` wins over every count; otherwise recent uses decide, then any evidence at all."""
    if it.added and it.added >= window_start:
        return "new"
    recent = it.slash_90d + (it.tool_90d or 0) + (it.trigger_90d or 0)
    if recent >= HOT_MIN_USES:
        return "hot"
    if recent >= WARM_MIN_USES:
        return "warm"
    ever = it.slash_all + (it.tool_all or 0) + (it.trigger_all or 0)
    if it.referrers or ever:
        return "cool"
    return "cold"


def propose(it: Item) -> str | None:
    """The proposed verdict. None means the row is kept silently, off the ratification table."""
    return PROPOSED_BY_TEMPERATURE.get(it.temperature)


def compute_totals(items: list[Item], surfaces: tuple[str, ...]) -> dict:
    """Always-loaded weight per enumerated surface. Surfaces not read are absent, not zero."""
    totals = {s: {"items": 0, "always_loaded_chars": 0} for s in SURFACE_ORDER if s in surfaces}
    for it in items:
        bucket = totals.setdefault(it.surface, {"items": 0, "always_loaded_chars": 0})
        bucket["items"] += 1
        bucket["always_loaded_chars"] += it.bytes_always_loaded
    totals["ALL"] = {"items": sum(v["items"] for v in totals.values()),
                     "always_loaded_chars": sum(v["always_loaded_chars"] for v in totals.values())}
    return totals


def build_inventory(cfg: Config) -> Inventory:
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=cfg.since_days)
    window_start = since.date().isoformat()

    # Evidence first: a surface must never be counted before the source that scores it was read.
    history = History(cfg.claude_home / "history.jsonl")

    tracked = git_tracked(cfg.config_repo)
    added = first_added_dates(cfg.config_repo)
    items: list[Item] = []
    if "skill" in cfg.surfaces:
        items += enumerate_skills(cfg.config_repo, tracked, added)

    for it in items:
        attach_usage(it, history, since)
        it.temperature = temperature(it, window_start)
        it.proposed = propose(it)

    meta = {
        "since_days": cfg.since_days,
        "since": window_start,
        "generated": now.isoformat(timespec="seconds"),
        "surfaces": list(cfg.surfaces),
        "history_rows": len(history.rows),
        "transcripts_scanned": None,          # unmeasured in this build
        "transcripts_cache_hits": None,
        "git_tracked": tracked is not None,
        "thresholds": {"window_default_days": WINDOW_DEFAULT_DAYS, "hot_min_uses": HOT_MIN_USES,
                       "warm_min_uses": WARM_MIN_USES, "auto_only_min_auto": AUTO_ONLY_MIN_AUTO},
        "config_repo": str(cfg.config_repo),
        "claude_home": str(cfg.claude_home),
        "caveat": LOCAL_CORPUS_CAVEAT,
    }
    return Inventory(items=items, totals=compute_totals(items, cfg.surfaces), meta=meta)


# ---------------------------------------------------------------- output

def _fmt(n: int | None) -> str:
    return UNMEASURED if n is None else str(n)


def evidence_summary(it: Item, since_days: int) -> str:
    parts = [f"typed {it.slash_90d}/{since_days}d · {it.slash_all} all",
             f"auto {_fmt(it.tool_90d)}/{_fmt(it.tool_all)}",
             f"trig {_fmt(it.trigger_90d)}/{_fmt(it.trigger_all)}",
             f"last {it.last_used or UNMEASURED}",
             f"added {it.added or UNMEASURED}",
             f"refs {len(it.referrers)}",
             f"{it.bytes_always_loaded:,} chars"]
    if it.vendored_copies:
        parts.append(f"vendored ×{len(it.vendored_copies)}")
    if it.duplicate_of:
        parts.append(f"dup of `{it.duplicate_of}`")
    if it.routes_to_missing:
        parts.append("routes→ " + ", ".join(it.routes_to_missing))
    return " · ".join(parts)


def render_markdown(inv: Inventory) -> str:
    """The redacted view: names, counts and dates only — no paths, no private detail."""
    m = inv.meta
    scanned = _fmt(m["transcripts_scanned"])
    out = [f"# Steering inventory — {m['generated'][:10]}", "",
           f"Window: last {m['since_days']} days (since {m['since']}). "
           f"History rows: {m['history_rows']:,}. Transcripts scanned: {scanned}. "
           f"Surfaces: {', '.join(m['surfaces'])}.", "",
           m["caveat"], "",
           "Read-only; an Instrument, never a Gate. An em dash is unmeasured, never zero.", "",
           "## Totals", "", "| Surface | Items | Always-loaded chars |", "|---|---|---|"]
    for s in [x for x in SURFACE_ORDER if x in inv.totals] + ["ALL"]:
        t = inv.totals[s]
        out.append(f"| {s} | {t['items']} | {t['always_loaded_chars']:,} |")
    for s in SURFACE_ORDER:
        rows = sorted((i for i in inv.items if i.surface == s),
                      key=lambda i: (TEMP_ORDER.get(i.temperature, 9), -i.bytes_always_loaded,
                                     i.name))
        if not rows:
            continue
        out += ["", f"## {s}", "", "| Item | Evidence | Flags | Temp | Proposed |",
                "|---|---|---|---|---|"]
        for i in rows:
            out.append(f"| `{i.name}` | {evidence_summary(i, m['since_days'])} | "
                       f"{', '.join(i.flags) or UNMEASURED} | {i.temperature} | "
                       f"{i.proposed or UNMEASURED} |")
    return "\n".join(out) + "\n"


def render_json(inv: Inventory) -> str:
    """The full view: every field, paths included. Written to the local cache, never committed."""
    return json.dumps({"meta": inv.meta, "totals": inv.totals,
                       "items": [i.to_dict() for i in inv.items]}, indent=1)


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
    args = ap.parse_args(argv)

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
