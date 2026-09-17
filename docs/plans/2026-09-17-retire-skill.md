# retire Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `retire` skill — an evidence-ranked subtraction pass over the global steering surface (CLAUDE.md sections, skills, commands, agents, plugins, MCP servers, hooks, output styles, auto-memory) that proposes retire/keep verdicts Kyle ratifies, applies them with full bookkeeping, and measures before → after weight — then run the first sweep on the live config.

**Architecture:** One read-only Python script (`steering_inventory.py`) owns enumeration and counting and exits non-zero instead of reporting a false zero; one prose skill (`SKILL.md` + `references/bookkeeping.md`) owns judgment, ratification, and the per-surface apply checklist; one ledger (`docs/retired.md`) owns "why is X gone / how do I get it back". Two PRs: **PR A** lands the tooling (Tasks 1–11); **PR B** lands the pilot's actual removals (Task 12).

**Tech Stack:** Python 3 stdlib (`argparse`, `json`, `re`, `subprocess`, `dataclasses`, `unittest`), git, `gh`, the existing `scripts/check-doc-sync.py` pre-push gate, the `adversarial-review` skill.

**Spec:** `docs/superpowers/specs/2026-09-17-retire-skill-design.md` — read it first; this plan implements it and nothing else. Decision IDs below (D1–D9) are the spec's §4 table.

---

## Read before starting

- **Live symlink.** `~/.claude/skills` → `~/Projects/claude-config/skills`, so `skills/retire/SKILL.md` is live as `/retire` the moment it exists on disk, on whatever branch is checked out. Keep the description honest from the first commit. Work on `feat/retire-skill` (already created; the spec is its first commit).
- **Repo rules that bite:** any change under `skills/**`, `commands/**`, `agents/**`, or `CLAUDE.md` is a behavioral diff — propose at least a single review round before merge (global CLAUDE.md, review-gate proposal; interactive = Kyle rules). The reference-doc row and playbook card land in the **same commit** as `SKILL.md`; `scripts/check-doc-sync.py` runs at `git push` and blocks otherwise. Run it yourself before pushing: `python3 scripts/check-doc-sync.py`.
- **Hooks that block you:** `~/.claude/hooks/block-rm-rf.sh` rejects `rm -rf` outside `/tmp/` — use `git rm` for tracked files and `mv` into `~/.claude/backups/` for untracked ones. The safety-net plugin blocks `xargs … sh -c`, `git checkout --`, and `git reset --hard`. zsh mangles `$ref:path`; run scripts under `bash` or brace every expansion.
- **Verified data shapes (2026-09-17)** the script depends on:
  - Transcript lines: `{"type":"assistant","timestamp":"2026-08-22T05:06:54.425Z","message":{"content":[{"type":"tool_use","name":"Skill","input":{"skill":"project-wiki","args":"…"}}]}, …}`. Agent dispatch: `"name":"Agent"`, `input.subagent_type`. MCP calls: `"name":"mcp__<server>__<tool>"`. Compact JSON, no spaces after colons — the substring needles `"name":"Skill"` etc. are exact.
  - `~/.claude/history.jsonl` rows: `{"display": "...", "timestamp": "1775107126825", "project": "...", "sessionId": "..."}` — timestamp is epoch **milliseconds as a string**.
  - Three `SKILL.md` files (`cc-yt-idea-mine`, `youtube-breakdown`, `youtube-transcript`) use `description: >-` folded block scalars; the frontmatter parser must join them.
  - Plugin cache: `~/.claude/plugins/installed_plugins.json` → `plugins[key][0].installPath`; `SKILL.md` files sit at varying depths below it (mattpocock nests `skills/engineering/<name>/SKILL.md`), so `rglob`.
  - `~/.claude.json` → `mcpServers` (user scope): `kapture`, `todoist`, `notebooklm-mcp`, `basic-memory`, `MCP_DOCKER`.
  - `~/.claude/settings.json` → `hooks` events: `PreToolUse`, `Stop`, `Notification`, `UserPromptSubmit`, `SessionEnd`; each event is a list of groups, each group has `hooks: [{type, command|prompt}]`.
- **Scratchpad** for intermediate files: `/private/tmp/claude-501/-Users-kyledisch-Projects-claude-config/<session>/scratchpad` (never `/tmp` directly).
- **Public repo.** Never write private repo paths into `docs/retired.md`; repo basenames only.

## File structure

| File | Responsibility |
|---|---|
| `skills/retire/scripts/steering_inventory.py` | Read-only inventory: enumerate surfaces, attach evidence, compute temperature, emit JSON/Markdown, exit codes. Create. |
| `skills/retire/scripts/claude_md_triggers.json` | Trigger-phrase regexes per global CLAUDE.md section (`null` = unknown, reported as `—` not 0). Create. |
| `skills/retire/scripts/tests/test_steering_inventory.py` | Fixture-driven unit tests (`unittest`, stdlib). Create. |
| `skills/retire/SKILL.md` | The skill: modes, prime directives, procedure, ratification table, handoffs, failure table. Create. |
| `skills/retire/references/bookkeeping.md` | Per-surface apply checklist with exact commands. Create. |
| `docs/retired.md` | Retirement ledger + "Kept on purpose" table. Create (seeded with headers only). |
| `docs/command-skill-reference.md` | One row under "Session & Context Management" (line ~100) + one intro sentence pointing at the ledger (after line 8). Modify. |
| `docs/usage-playbook.md` | One card, anchor `#retire`, in "Session & Context Management" (after the `orchestrate` card, before line 610). Modify. |
| `docs/reports/2026-09-XX-steering-inventory.md` | The first read-only live inventory (Task 8) and the pilot's before → after (Task 12). Create. |
| `BACKLOG.md` | Three v2 stubs; status lines on absorbed items. Modify. |
| `docs/ideas/coliseum-commands-earn-their-keep.md`, `docs/ideas/minimal-initial-prompt.md` | One status line each: built / absorbed. Modify. |

---

### Task 1: Module skeleton, frontmatter parser, section splitter, fixture

**Files:**
- Create: `skills/retire/scripts/steering_inventory.py`
- Create: `skills/retire/scripts/tests/__init__.py` (empty)
- Create: `skills/retire/scripts/tests/test_steering_inventory.py`

- [ ] **Step 1: Write the fixture builder and the first failing tests**

The fixture is built once here and reused by every later task — it already contains everything Tasks 2–7 need (skills, commands, agents, plugins, hooks, history, transcripts, memory dirs, MCP config, vendored copies, a ledger).

```python
# skills/retire/scripts/tests/test_steering_inventory.py
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import steering_inventory as si  # noqa: E402

NOW = datetime.now(timezone.utc)


def ms(days_ago: int) -> str:
    return str(int((NOW - timedelta(days=days_ago)).timestamp() * 1000))


def iso(days_ago: int) -> str:
    return (NOW - timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def tool_use(days_ago: int, name: str, inp: dict) -> str:
    return json.dumps({"type": "assistant", "timestamp": iso(days_ago),
                       "message": {"content": [{"type": "tool_use", "name": name, "input": inp}]}})


def make_fixture(root: Path) -> "si.Config":
    repo, home, projects = root / "claude-config", root / "home", root / "Projects"
    write(repo / "CLAUDE.md",
          "# Top\n\n@~/.claude/operating-constraints.md\n\n"
          "## Improvement Mode\n\nWhen I say improvement mode, ask first.\n\n"
          "## Git Workflow\n\nAlways branch.\n\n### Sub rule\n\nNested.\n\n"
          "```markdown\n# Not a heading\n```\n")
    write(repo / "operating-constraints.md", "Scope discipline.\n")
    write(repo / "skills/alpha/SKILL.md",
          '---\nname: alpha\ndescription: Alpha does things. Use when Kyle says "alpha please" or '
          '"run alpha now". Hands off to beta and /old.\n---\n\n# Alpha\n')
    write(repo / "skills/beta/SKILL.md",
          "---\nname: beta\ndescription: >-\n  Beta does other\n  things across lines.\n---\n\n# Beta\n")
    write(repo / "skills/tdd/SKILL.md", "---\nname: tdd\ndescription: Loose copy of tdd.\n---\n")
    write(repo / "commands/gamma.md", "---\ndescription: Gamma command.\n---\nRun gamma.\n")
    write(repo / "commands/old.md.disabled", "---\ndescription: Old command.\n---\n")
    write(repo / "agents/judge.md", "---\nname: judge\ndescription: Judge agent.\n---\n")
    write(repo / "output-styles/plain.md", "---\nname: plain\ndescription: Plain style.\n---\n")
    write(repo / "docs/retired.md",
          "# Retired items\n\n| Date | Item | Surface | Why | Evidence at retirement | Restore | Downstream copies |\n"
          "|---|---|---|---|---|---|---|\n| 2026-01-01 | zeta | skill | gone | 0 | git | — |\n")
    plugin_dir = home / "plugins/cache/mp/mp/1.0.0"
    write(plugin_dir / "skills/tdd/SKILL.md", "---\nname: tdd\ndescription: Plugin tdd skill.\n---\n")
    write(home / "plugins/installed_plugins.json", json.dumps({"version": 2, "plugins": {
        "mp@mp": [{"scope": "user", "installPath": str(plugin_dir), "version": "1.0.0"}],
        "off@x": [{"scope": "user", "installPath": str(home / "plugins/cache/x/off/1.0.0"), "version": "1.0.0"}]}}))
    write(home / "settings.json", json.dumps({
        "enabledPlugins": {"mp@mp": True, "off@x": False},
        "hooks": {
            "Stop": [{"hooks": [
                {"type": "prompt", "prompt": "Kyle's CLAUDE.md defines Improvement Mode; pausing there is fine."},
                {"type": "command", "command": "# DISABLED 2026-08-13: afplay ding.aiff"}]}],
            "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "bash guard.sh"}]}]}}))
    write(home / "history.jsonl", "\n".join(json.dumps(r) for r in [
        {"display": "/alpha do the thing", "timestamp": ms(3), "project": "/p", "sessionId": "s1"},
        {"display": "alpha please, now", "timestamp": ms(5), "project": "/p", "sessionId": "s1"},
        {"display": "/gamma", "timestamp": ms(200), "project": "/p", "sessionId": "s2"},
        {"display": "/mp:tdd", "timestamp": ms(10), "project": "/p", "sessionId": "s3"},
        {"display": "let's talk about alphabet soup", "timestamp": ms(1), "project": "/p", "sessionId": "s3"},
    ]) + "\n")
    write(home / "projects/-p1/t1.jsonl", "\n".join([
        tool_use(2, "Skill", {"skill": "alpha"}),
        tool_use(150, "Agent", {"subagent_type": "judge", "prompt": "x"}),
        tool_use(4, "mcp__todoist__todoist_create_task", {"content": "x"}),
        tool_use(6, "Skill", {"skill": "mp:tdd"}),
        json.dumps({"type": "user", "timestamp": iso(2), "message": {"content": "hello"}}),
    ]) + "\n")
    (home / "projects/-p2/memory").mkdir(parents=True)
    write(home / "projects/-p3/memory/MEMORY.md", "# mem\n")
    write(root / "claude.json", json.dumps({"mcpServers": {"todoist": {"command": "npx"}, "docker": {"command": "docker"}}}))
    (projects / "repoA/.claude/skills/alpha").mkdir(parents=True)
    write(projects / "repoB/.claude/commands/gamma.md", "vendored\n")
    return si.Config(claude_home=home, config_repo=repo, projects_root=projects,
                     claude_json=root / "claude.json", since_days=90,
                     triggers={"Improvement Mode": ["improvement mode"]}, cache_path=None)


class FixtureCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.cfg = make_fixture(self.root)

    def tearDown(self):
        self._tmp.cleanup()


class ParsingTests(unittest.TestCase):
    def test_frontmatter_single_line(self):
        fm = si.parse_frontmatter('---\nname: alpha\ndescription: Alpha "x".\nallowed-tools: Bash, Read\n---\nbody')
        self.assertEqual(fm["name"], "alpha")
        self.assertEqual(fm["description"], 'Alpha "x".')
        self.assertEqual(fm["allowed-tools"], "Bash, Read")

    def test_frontmatter_folded_block_scalar(self):
        fm = si.parse_frontmatter("---\nname: beta\ndescription: >-\n  Beta does other\n  things across lines.\nx: 1\n---\n")
        self.assertEqual(fm["description"], "Beta does other things across lines.")
        self.assertEqual(fm["x"], "1")

    def test_frontmatter_missing(self):
        self.assertEqual(si.parse_frontmatter("no front matter"), {})

    def test_split_sections_skips_fenced_headings(self):
        text = ("# Top\n\n## A\n\nbody a\n\n### A1\n\nnested\n\n## B\n\n```md\n# not a heading\n```\nend\n")
        secs = list(si.split_sections(text))
        titles = [t for t, _, _ in secs]
        self.assertEqual(titles, ["A", "A1", "B"])
        a_body = secs[0][1]
        self.assertIn("### A1", a_body)          # ## A runs to the next ## (includes its ###)
        self.assertNotIn("not a heading", titles)
        self.assertEqual(secs[2][2], 11)          # 1-based line number of "## B"


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd ~/Projects/claude-config && python3 -m unittest skills.retire.scripts.tests.test_steering_inventory -v 2>&1 | tail -5`
Expected: `ModuleNotFoundError: No module named 'steering_inventory'` (or ImportError on `skills.retire`).

Note: `python3 -m unittest` needs `skills/retire/scripts/tests/__init__.py`; create it empty. If package import of `skills.retire.scripts` fails because `skills/` has no `__init__.py`, run the file directly instead — the test file inserts its parent on `sys.path`: `python3 skills/retire/scripts/tests/test_steering_inventory.py -v`. Use whichever form works and keep using it.

- [ ] **Step 3: Write the module skeleton**

```python
#!/usr/bin/env python3
"""steering_inventory.py — enumerate every global Claude Code steering surface with usage evidence.

Read-only. An Instrument, never a Gate (see CONTEXT.md in claude-config): it informs a human
ruling and blocks nothing.

Exit codes:
  0  inventory complete
  2  a required source was missing or unreadable (never silently reported as 0)
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

EXIT_OK, EXIT_SOURCE_MISSING, EXIT_EMPTY_SURFACE = 0, 2, 3
SURFACE_ORDER = ["claude-md", "skill", "command", "agent", "output-style", "plugin", "mcp", "hook", "memory"]
TEMP_ORDER = {"cold": 0, "cool": 1, "warm": 2, "hot": 3, "unknown": 4}


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
    Supports `>`, `>-`, `|`, `|-` block scalars (folded joins with spaces, literal with newlines)."""
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
            while i < len(lines) and lines[i].strip() != "---" and (lines[i].startswith(" ") or lines[i].strip() == ""):
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
    A section's body runs to the next heading of the same or higher level."""
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
    id: str                    # "skill:mock-call", "claude-md:Improvement Mode", "plugin:swift-lsp@claude-plugins-official"
    surface: str               # one of SURFACE_ORDER
    name: str
    path: str
    bytes_always_loaded: int
    tracked: bool | None = None          # None = repo has no git
    paused: bool = False                 # commands/<x>.md.disabled
    description: str = ""
    slash_all: int = 0
    slash_90d: int = 0
    tool_all: int = 0                    # Skill / Agent / mcp__ tool_use events
    tool_90d: int = 0
    last_used: str | None = None         # ISO date
    trigger_all: int | None = None       # None = no trigger list known (reported as —, never 0)
    trigger_90d: int | None = None
    referrers: list[str] = field(default_factory=list)
    routes_to_missing: list[str] = field(default_factory=list)
    vendored_copies: list[str] = field(default_factory=list)
    duplicate_of: str | None = None
    last_edited: str | None = None
    flags: list[str] = field(default_factory=list)
    temperature: str = "unknown"
    extra: dict = field(default_factory=dict)

    @property
    def invocations_all(self) -> int:
        return self.slash_all + self.tool_all

    @property
    def invocations_90d(self) -> int:
        return self.slash_90d + self.tool_90d

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
    since_days: int = 90
    triggers: dict | None = None         # claude-md section title -> list[regex] | None
    cache_path: Path | None = None


@dataclass
class Inventory:
    items: list
    totals: dict
    meta: dict
```

- [ ] **Step 4: Run the parsing tests to verify they pass**

Run: `python3 skills/retire/scripts/tests/test_steering_inventory.py -v 2>&1 | tail -8`
Expected: 4 tests in `ParsingTests` PASS (`FixtureCase` has no tests yet).

- [ ] **Step 5: Commit**

```bash
git add skills/retire/scripts/steering_inventory.py skills/retire/scripts/tests/__init__.py skills/retire/scripts/tests/test_steering_inventory.py
git commit -m "feat(retire): inventory script skeleton — frontmatter parser, section splitter, item model

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01F6oTCwzx8WmJuYuN4Q3nJr"
```

---

### Task 2: Config-repo enumerators (CLAUDE.md sections, skills, commands, agents, output styles)

**Files:**
- Modify: `skills/retire/scripts/steering_inventory.py` (append after the model section)
- Modify: `skills/retire/scripts/tests/test_steering_inventory.py` (add a test class)

- [ ] **Step 1: Write the failing tests**

```python
class ConfigRepoEnumeratorTests(FixtureCase):
    def test_claude_md_sections_and_constraints(self):
        items = si.enumerate_claude_md(self.cfg.config_repo)
        names = [i.name for i in items]
        self.assertEqual(names, ["operating-constraints.md", "Improvement Mode", "Git Workflow", "Sub rule"])
        imp = next(i for i in items if i.name == "Improvement Mode")
        self.assertEqual(imp.surface, "claude-md")
        self.assertGreater(imp.bytes_always_loaded, 20)
        self.assertEqual(imp.extra["line"], 5)
        self.assertIn("ask first", imp.extra["body"])

    def test_skills(self):
        items = si.enumerate_skills(self.cfg.config_repo, tracked=None)
        by = {i.name: i for i in items}
        self.assertEqual(sorted(by), ["alpha", "beta", "tdd"])
        self.assertEqual(by["beta"].description, "Beta does other things across lines.")
        self.assertEqual(by["beta"].bytes_always_loaded, len("Beta does other things across lines."))
        self.assertIsNone(by["alpha"].tracked)
        self.assertEqual(by["alpha"].id, "skill:alpha")

    def test_skills_tracked_flag(self):
        items = si.enumerate_skills(self.cfg.config_repo, tracked={"skills/alpha/SKILL.md"})
        by = {i.name: i for i in items}
        self.assertTrue(by["alpha"].tracked)
        self.assertFalse(by["beta"].tracked)

    def test_skills_empty_surface_raises(self):
        (self.cfg.config_repo / "skills/alpha/SKILL.md").unlink()
        (self.cfg.config_repo / "skills/beta/SKILL.md").unlink()
        (self.cfg.config_repo / "skills/tdd/SKILL.md").unlink()
        with self.assertRaises(si.EmptySurface):
            si.enumerate_skills(self.cfg.config_repo, tracked=None)

    def test_commands_including_paused(self):
        items = si.enumerate_commands(self.cfg.config_repo, tracked=None)
        by = {i.name: i for i in items}
        self.assertEqual(sorted(by), ["gamma", "old"])
        self.assertFalse(by["gamma"].paused)
        self.assertEqual(by["gamma"].bytes_always_loaded, len("Gamma command."))
        self.assertTrue(by["old"].paused)
        self.assertIn("paused", by["old"].flags)
        self.assertEqual(by["old"].bytes_always_loaded, 0)

    def test_agents_and_output_styles(self):
        agents = si.enumerate_agents(self.cfg.config_repo, tracked=None)
        styles = si.enumerate_output_styles(self.cfg.config_repo, tracked=None)
        self.assertEqual([a.id for a in agents], ["agent:judge"])
        self.assertEqual([s.id for s in styles], ["output-style:plain"])
        self.assertEqual(agents[0].bytes_always_loaded, len("Judge agent."))

    def test_missing_claude_md_raises(self):
        (self.cfg.config_repo / "CLAUDE.md").unlink()
        with self.assertRaises(si.SourceMissing):
            si.enumerate_claude_md(self.cfg.config_repo)
```

- [ ] **Step 2: Run to verify they fail**

Run: `python3 skills/retire/scripts/tests/test_steering_inventory.py -v 2>&1 | grep -E 'ERROR|FAIL|Ran'`
Expected: 7 errors, `AttributeError: module 'steering_inventory' has no attribute 'enumerate_claude_md'` (and siblings).

- [ ] **Step 3: Implement the enumerators**

Append to `steering_inventory.py`:

```python
# ---------------------------------------------------------------- config-repo surfaces

def git_tracked(repo: Path) -> set[str] | None:
    """Set of git-tracked relative paths, or None when the repo has no usable git."""
    try:
        out = subprocess.run(["git", "-C", str(repo), "ls-files"], capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return {ln for ln in out.split("\n") if ln}


def _tracked_flag(tracked: set[str] | None, rel: str) -> bool | None:
    return None if tracked is None else rel in tracked


def enumerate_claude_md(config_repo: Path) -> list[Item]:
    items: list[Item] = []
    oc = config_repo / "operating-constraints.md"
    cm = config_repo / "CLAUDE.md"
    if not cm.exists():
        raise SourceMissing(f"{cm} missing")
    if oc.exists():
        text = oc.read_text(errors="ignore")
        items.append(Item(id="claude-md:operating-constraints.md", surface="claude-md", name="operating-constraints.md",
                          path=str(oc), bytes_always_loaded=len(text), extra={"body": text, "line": 1}))
    for title, body, line_no in split_sections(cm.read_text(errors="ignore")):
        items.append(Item(id=f"claude-md:{title}", surface="claude-md", name=title, path=str(cm),
                          bytes_always_loaded=len(body), extra={"body": body, "line": line_no}))
    return items


def _md_items(root: Path, surface: str, tracked: set[str] | None, config_repo: Path,
              suffixes: tuple[str, ...] = (".md",)) -> list[Item]:
    if not root.is_dir():
        return []
    items: list[Item] = []
    entries = sorted(root.iterdir())
    for f in entries:
        if not f.is_file():
            continue
        paused = False
        name = None
        for suf in suffixes:
            if f.name.endswith(suf):
                name = f.name[: -len(suf)]
                paused = suf.endswith(".disabled")
                break
        if name is None:
            continue
        fm = parse_frontmatter(f.read_text(errors="ignore"))
        desc = fm.get("description", "")
        rel = str(f.relative_to(config_repo))
        it = Item(id=f"{surface}:{name}", surface=surface, name=name, path=str(f),
                  bytes_always_loaded=0 if paused else len(desc), tracked=_tracked_flag(tracked, rel),
                  paused=paused, description=desc)
        if paused:
            it.flags.append("paused")
        items.append(it)
    if not items and entries:
        raise EmptySurface(f"{surface}: {root} has entries but no items")
    return items


def enumerate_skills(config_repo: Path, tracked: set[str] | None) -> list[Item]:
    root = config_repo / "skills"
    if not root.is_dir():
        raise SourceMissing(f"{root} missing")
    items: list[Item] = []
    entries = [d for d in sorted(root.iterdir()) if d.is_dir()]
    for d in entries:
        sk = d / "SKILL.md"
        if not sk.exists():
            continue
        fm = parse_frontmatter(sk.read_text(errors="ignore"))
        desc = fm.get("description", "")
        rel = f"skills/{d.name}/SKILL.md"
        items.append(Item(id=f"skill:{d.name}", surface="skill", name=d.name, path=str(sk),
                          bytes_always_loaded=len(desc), tracked=_tracked_flag(tracked, rel), description=desc))
    if not items and entries:
        raise EmptySurface(f"skill: {root} has directories but no SKILL.md files")
    return items


def enumerate_commands(config_repo: Path, tracked: set[str] | None) -> list[Item]:
    return _md_items(config_repo / "commands", "command", tracked, config_repo, suffixes=(".md.disabled", ".md"))


def enumerate_agents(config_repo: Path, tracked: set[str] | None) -> list[Item]:
    return _md_items(config_repo / "agents", "agent", tracked, config_repo)


def enumerate_output_styles(config_repo: Path, tracked: set[str] | None) -> list[Item]:
    return _md_items(config_repo / "output-styles", "output-style", tracked, config_repo)
```

- [ ] **Step 4: Run to verify they pass**

Run: `python3 skills/retire/scripts/tests/test_steering_inventory.py -v 2>&1 | grep -E 'ERROR|FAIL|Ran|OK'`
Expected: `Ran 11 tests` … `OK`.

- [ ] **Step 5: Commit**

```bash
git add skills/retire/scripts/
git commit -m "feat(retire): enumerate CLAUDE.md sections, skills, commands, agents, output styles

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01F6oTCwzx8WmJuYuN4Q3nJr"
```

---

### Task 3: Claude-home enumerators (plugins, MCP servers, hooks, memory dirs)

**Files:**
- Modify: `skills/retire/scripts/steering_inventory.py`
- Modify: `skills/retire/scripts/tests/test_steering_inventory.py`

- [ ] **Step 1: Write the failing tests**

```python
class ClaudeHomeEnumeratorTests(FixtureCase):
    def test_plugins(self):
        items = si.enumerate_plugins(self.cfg.claude_home)
        by = {i.name: i for i in items}
        self.assertEqual(sorted(by), ["mp@mp", "off@x"])
        self.assertTrue(by["mp@mp"].extra["enabled"])
        self.assertEqual(by["mp@mp"].bytes_always_loaded, len("Plugin tdd skill."))
        self.assertEqual([s["name"] for s in by["mp@mp"].extra["skills"]], ["tdd"])
        self.assertIn("disabled", by["off@x"].flags)
        self.assertEqual(by["off@x"].bytes_always_loaded, 0)

    def test_mcp_servers(self):
        items = si.enumerate_mcp(self.cfg.claude_json)
        self.assertEqual([i.id for i in items], ["mcp:docker", "mcp:todoist"])
        self.assertEqual(items[1].extra["command"], "npx")

    def test_hooks(self):
        items = si.enumerate_hooks(self.cfg.claude_home)
        ids = [i.id for i in items]
        self.assertEqual(ids, ["hook:PreToolUse[0][0]", "hook:Stop[0][0]", "hook:Stop[0][1]"])
        stop_cmd = next(i for i in items if i.id == "hook:Stop[0][1]")
        self.assertIn("disabled_comment", stop_cmd.flags)
        prompt = next(i for i in items if i.id == "hook:Stop[0][0]")
        self.assertEqual(prompt.extra["type"], "prompt")
        self.assertIn("Improvement Mode", prompt.extra["command"])

    def test_memory_dirs(self):
        items = si.enumerate_memory(self.cfg.claude_home)
        by = {i.name: i for i in items}
        self.assertEqual(sorted(by), ["-p2", "-p3"])
        self.assertIn("empty", by["-p2"].flags)
        self.assertEqual(by["-p3"].extra["files"], 1)
        self.assertEqual(by["-p3"].bytes_always_loaded, len("# mem\n"))

    def test_missing_settings_raises(self):
        (self.cfg.claude_home / "settings.json").unlink()
        with self.assertRaises(si.SourceMissing):
            si.enumerate_plugins(self.cfg.claude_home)
```

- [ ] **Step 2: Run to verify they fail**

Run: `python3 skills/retire/scripts/tests/test_steering_inventory.py -v 2>&1 | grep -E 'ERROR|FAIL|Ran'`
Expected: 5 errors, `AttributeError … 'enumerate_plugins'` and siblings.

- [ ] **Step 3: Implement**

Append:

```python
# ---------------------------------------------------------------- claude-home surfaces

def enumerate_plugins(claude_home: Path) -> list[Item]:
    settings = load_json(claude_home / "settings.json")
    installed = load_json(claude_home / "plugins" / "installed_plugins.json")
    enabled = settings.get("enabledPlugins") or {}
    items: list[Item] = []
    for key, entries in sorted((installed.get("plugins") or {}).items()):
        entry = entries[0] if entries else {}
        install = Path(entry.get("installPath") or "")
        skills: list[dict] = []
        if install.is_dir():
            for sk in sorted(install.rglob("SKILL.md")):
                fm = parse_frontmatter(sk.read_text(errors="ignore"))
                skills.append({"name": fm.get("name") or sk.parent.name, "description": fm.get("description", ""), "path": str(sk)})
        is_enabled = bool(enabled.get(key, False))
        it = Item(id=f"plugin:{key}", surface="plugin", name=key, path=str(install),
                  bytes_always_loaded=sum(len(s["description"]) for s in skills) if is_enabled else 0,
                  extra={"enabled": is_enabled, "skills": skills, "version": entry.get("version")})
        if not is_enabled:
            it.flags.append("disabled")
        items.append(it)
    return items


def enumerate_mcp(claude_json: Path) -> list[Item]:
    d = load_json(claude_json)
    items: list[Item] = []
    for name, cfg in sorted((d.get("mcpServers") or {}).items()):
        cfg = cfg or {}
        items.append(Item(id=f"mcp:{name}", surface="mcp", name=name, path=str(claude_json), bytes_always_loaded=0,
                          extra={"command": cfg.get("command"), "type": cfg.get("type"), "url": cfg.get("url")}))
    return items


def enumerate_hooks(claude_home: Path) -> list[Item]:
    settings = load_json(claude_home / "settings.json")
    items: list[Item] = []
    for event, groups in sorted((settings.get("hooks") or {}).items()):
        for gi, group in enumerate(groups or []):
            for hi, hook in enumerate((group or {}).get("hooks") or []):
                cmd = hook.get("command") or hook.get("prompt") or ""
                label = (cmd.strip().splitlines() or [""])[0][:60]
                it = Item(id=f"hook:{event}[{gi}][{hi}]", surface="hook", name=f"{event}: {label}",
                          path=str(claude_home / "settings.json"), bytes_always_loaded=0,
                          extra={"event": event, "matcher": group.get("matcher"), "type": hook.get("type"), "command": cmd})
                if cmd.lstrip().startswith("#"):
                    it.flags.append("disabled_comment")
                items.append(it)
    return items


def enumerate_memory(claude_home: Path) -> list[Item]:
    items: list[Item] = []
    for mem in sorted((claude_home / "projects").glob("*/memory")):
        files = [f for f in mem.rglob("*") if f.is_file()]
        it = Item(id=f"memory:{mem.parent.name}", surface="memory", name=mem.parent.name, path=str(mem),
                  bytes_always_loaded=sum(f.stat().st_size for f in files), extra={"files": len(files)})
        if not files:
            it.flags.append("empty")
        items.append(it)
    return items
```

- [ ] **Step 4: Run to verify they pass**

Run: `python3 skills/retire/scripts/tests/test_steering_inventory.py -v 2>&1 | grep -E 'ERROR|FAIL|Ran|OK'`
Expected: `Ran 16 tests` … `OK`.

- [ ] **Step 5: Commit**

```bash
git add skills/retire/scripts/
git commit -m "feat(retire): enumerate plugins, MCP servers, hooks, memory dirs

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01F6oTCwzx8WmJuYuN4Q3nJr"
```

---

### Task 4: History index (slash commands and trigger phrases)

**Files:**
- Modify: `skills/retire/scripts/steering_inventory.py`
- Modify: `skills/retire/scripts/tests/test_steering_inventory.py`

- [ ] **Step 1: Write the failing tests**

```python
class HistoryTests(FixtureCase):
    def test_loads_rows(self):
        h = si.History(self.cfg.claude_home / "history.jsonl")
        self.assertEqual(len(h.rows), 5)

    def test_slash_count_respects_window_and_boundary(self):
        h = si.History(self.cfg.claude_home / "history.jsonl")
        since = NOW - timedelta(days=90)
        self.assertEqual(h.count(si.slash_pattern("alpha"), since), (1, 1, (NOW - timedelta(days=3)).date().isoformat()))
        self.assertEqual(h.count(si.slash_pattern("gamma"), since)[:2], (1, 0))
        self.assertEqual(h.count(si.slash_pattern("mp:tdd"), since)[:2], (1, 1))
        self.assertEqual(h.count(si.slash_pattern("tdd"), since)[:2], (0, 0))   # /mp:tdd is not /tdd

    def test_count_any_phrases(self):
        h = si.History(self.cfg.claude_home / "history.jsonl")
        since = NOW - timedelta(days=90)
        pats = si.phrases_from_description('Use when Kyle says "alpha please" or "run alpha now".')
        self.assertEqual(pats, [r"alpha\ please", r"run\ alpha\ now"])
        self.assertEqual(h.count_any(pats, since)[:2], (1, 1))
        self.assertEqual(h.count_any(["improvement mode"], since)[:2], (0, 0))

    def test_missing_history_raises(self):
        with self.assertRaises(si.SourceMissing):
            si.History(self.cfg.claude_home / "nope.jsonl")

    def test_empty_history_raises(self):
        (self.cfg.claude_home / "history.jsonl").write_text("")
        with self.assertRaises(si.SourceMissing):
            si.History(self.cfg.claude_home / "history.jsonl")
```

- [ ] **Step 2: Run to verify they fail**

Run: `python3 skills/retire/scripts/tests/test_steering_inventory.py -v 2>&1 | grep -E 'ERROR|FAIL|Ran'`
Expected: 5 errors, `AttributeError … 'History'`.

- [ ] **Step 3: Implement**

Append:

```python
# ---------------------------------------------------------------- evidence: history.jsonl

def slash_pattern(name: str) -> str:
    """Regex for a prompt that starts with /<name> (not /<name>-more, not /<name>:sub)."""
    return r"^\s*/" + re.escape(name) + r"(?![\w:-])"


def phrases_from_description(desc: str) -> list[str]:
    """Trigger phrases are the double-quoted strings in a description (8–80 chars), escaped for regex."""
    return [re.escape(p.lower()) for p in re.findall(r'"([^"]{8,80})"', desc)]


class History:
    def __init__(self, path: Path):
        if not path.exists():
            raise SourceMissing(f"history file missing: {path}")
        self.rows: list[tuple[datetime, str]] = []
        with open(path, errors="ignore") as fh:
            for line in fh:
                try:
                    d = json.loads(line)
                    dt = datetime.fromtimestamp(int(d.get("timestamp")) / 1000, tz=timezone.utc)
                except (ValueError, TypeError, OverflowError):
                    continue
                self.rows.append((dt, (d.get("display") or "").lower()))
        if not self.rows:
            raise SourceMissing(f"history file parsed to zero rows: {path}")

    def count_any(self, patterns: list[str], since: datetime) -> tuple[int, int, str | None]:
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
```

- [ ] **Step 4: Run to verify they pass**

Run: `python3 skills/retire/scripts/tests/test_steering_inventory.py -v 2>&1 | grep -E 'ERROR|FAIL|Ran|OK'`
Expected: `Ran 21 tests` … `OK`.

- [ ] **Step 5: Commit**

```bash
git add skills/retire/scripts/
git commit -m "feat(retire): history.jsonl index for slash-command and trigger-phrase counts

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01F6oTCwzx8WmJuYuN4Q3nJr"
```

---

### Task 5: Transcript usage with a per-file cache

**Files:**
- Modify: `skills/retire/scripts/steering_inventory.py`
- Modify: `skills/retire/scripts/tests/test_steering_inventory.py`

- [ ] **Step 1: Write the failing tests**

```python
class TranscriptTests(FixtureCase):
    def test_extract_events(self):
        evs = si.extract_events(self.cfg.claude_home / "projects/-p1/t1.jsonl")
        kinds = [(k, n) for _, k, n in evs]
        self.assertEqual(kinds, [("skill", "alpha"), ("agent", "judge"), ("mcp", "todoist"), ("skill", "mp:tdd")])

    def test_counts(self):
        t = si.Transcripts(self.cfg.claude_home / "projects", cache_path=None)
        since = NOW - timedelta(days=90)
        self.assertEqual(t.files_scanned, 1)
        self.assertEqual(t.count("skill", "alpha", since)[:2], (1, 1))
        self.assertEqual(t.count("agent", "judge", since)[:2], (1, 0))
        self.assertEqual(t.count("mcp", "todoist", since)[:2], (1, 1))
        self.assertEqual(t.count("mcp", "docker", since), (0, 0, None))

    def test_cache_roundtrip(self):
        cache = self.root / "cache.json"
        t1 = si.Transcripts(self.cfg.claude_home / "projects", cache_path=cache)
        self.assertTrue(cache.exists())
        t2 = si.Transcripts(self.cfg.claude_home / "projects", cache_path=cache)
        self.assertEqual(len(t1.events), len(t2.events))
        self.assertEqual(t2.cache_hits, 1)

    def test_no_transcripts_raises(self):
        with self.assertRaises(si.SourceMissing):
            si.Transcripts(self.root / "nowhere", cache_path=None)
```

- [ ] **Step 2: Run to verify they fail**

Run: `python3 skills/retire/scripts/tests/test_steering_inventory.py -v 2>&1 | grep -E 'ERROR|FAIL|Ran'`
Expected: 4 errors, `AttributeError … 'extract_events'` / `'Transcripts'`.

- [ ] **Step 3: Implement**

Append:

```python
# ---------------------------------------------------------------- evidence: transcripts

NEEDLES = ('"name":"Skill"', '"name":"Agent"', '"name":"mcp__')


def extract_events(path: Path) -> list[list]:
    """[[iso_ts, kind, key], …] for every Skill / Agent / mcp__ tool_use in one transcript.
    Substring-filters each line before JSON-parsing it; the corpus is gigabytes."""
    out: list[list] = []
    try:
        fh = open(path, errors="ignore")
    except OSError:
        return out
    with fh:
        for line in fh:
            if not any(n in line for n in NEEDLES):
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            ts = d.get("timestamp")
            msg = d.get("message")
            if not ts or not isinstance(msg, dict):
                continue
            for c in msg.get("content") or []:
                if not (isinstance(c, dict) and c.get("type") == "tool_use"):
                    continue
                name = c.get("name") or ""
                inp = c.get("input") or {}
                if name == "Skill" and inp.get("skill"):
                    out.append([ts, "skill", str(inp["skill"])])
                elif name == "Agent" and inp.get("subagent_type"):
                    out.append([ts, "agent", str(inp["subagent_type"])])
                elif name.startswith("mcp__"):
                    parts = name.split("__")
                    if len(parts) >= 2 and parts[1]:
                        out.append([ts, "mcp", parts[1]])
    return out


class Transcripts:
    def __init__(self, projects_root: Path, cache_path: Path | None):
        files = sorted(projects_root.rglob("*.jsonl")) if projects_root.is_dir() else []
        if not files:
            raise SourceMissing(f"no transcripts under {projects_root}")
        cache: dict = {}
        if cache_path and cache_path.exists():
            try:
                cache = json.loads(cache_path.read_text())
            except ValueError:
                cache = {}
        self.events: list[tuple[datetime, str, str]] = []
        self.cache_hits = 0
        for p in files:
            st = p.stat()
            key = str(p)
            c = cache.get(key)
            if c and c.get("size") == st.st_size and c.get("mtime") == st.st_mtime:
                evs = c["events"]
                self.cache_hits += 1
            else:
                evs = extract_events(p)
                cache[key] = {"size": st.st_size, "mtime": st.st_mtime, "events": evs}
            for ts, kind, k in evs:
                try:
                    dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
                except ValueError:
                    continue
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                self.events.append((dt, kind, k))
        if cache_path:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(json.dumps(cache))
        self.files_scanned = len(files)

    def count(self, kind: str, key: str, since: datetime) -> tuple[int, int, str | None]:
        total = recent = 0
        last: datetime | None = None
        for dt, k, name in self.events:
            if k == kind and name == key:
                total += 1
                if dt >= since:
                    recent += 1
                if last is None or dt > last:
                    last = dt
        return total, recent, (last.date().isoformat() if last else None)
```

- [ ] **Step 4: Run to verify they pass**

Run: `python3 skills/retire/scripts/tests/test_steering_inventory.py -v 2>&1 | grep -E 'ERROR|FAIL|Ran|OK'`
Expected: `Ran 25 tests` … `OK`.

- [ ] **Step 5: Commit**

```bash
git add skills/retire/scripts/
git commit -m "feat(retire): transcript usage extraction with per-file cache

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01F6oTCwzx8WmJuYuN4Q3nJr"
```

---

### Task 6: Referrers, dangling routes, vendored copies, duplicates, last-edited

**Files:**
- Modify: `skills/retire/scripts/steering_inventory.py`
- Modify: `skills/retire/scripts/tests/test_steering_inventory.py`

- [ ] **Step 1: Write the failing tests**

```python
class CrossReferenceTests(FixtureCase):
    def _skills(self):
        return {i.name: i for i in si.enumerate_skills(self.cfg.config_repo, tracked=None)}

    def test_corpus_includes_prompt_hooks(self):
        corpus = si.build_corpus(self.cfg.config_repo, self.cfg.claude_home)
        self.assertIn("settings.json:Stop prompt hook", corpus)
        self.assertTrue(any(k.endswith("skills/alpha/SKILL.md") for k in corpus))

    def test_referrers_exclude_own_files(self):
        corpus = si.build_corpus(self.cfg.config_repo, self.cfg.claude_home)
        by = self._skills()
        si.attach_referrers(by["beta"], corpus, self.cfg.config_repo)
        self.assertEqual([Path(r).name for r in by["beta"].referrers], ["SKILL.md"])
        self.assertTrue(by["beta"].referrers[0].endswith("skills/alpha/SKILL.md"))
        si.attach_referrers(by["alpha"], corpus, self.cfg.config_repo)
        self.assertEqual(by["alpha"].referrers, [])

    def test_claude_md_section_referrer_is_the_stop_hook(self):
        corpus = si.build_corpus(self.cfg.config_repo, self.cfg.claude_home)
        imp = next(i for i in si.enumerate_claude_md(self.cfg.config_repo) if i.name == "Improvement Mode")
        si.attach_referrers(imp, corpus, self.cfg.config_repo)
        self.assertEqual(imp.referrers, ["settings.json:Stop prompt hook"])

    def test_missing_names_and_dangling(self):
        cmds = si.enumerate_commands(self.cfg.config_repo, tracked=None)
        missing = si.missing_names(cmds, self.cfg.config_repo)
        self.assertEqual(missing, {"old", "zeta"})
        by = self._skills()
        si.attach_dangling(by["alpha"], missing)
        self.assertEqual(by["alpha"].routes_to_missing, ["old"])
        self.assertIn("dangling", by["alpha"].flags)
        si.attach_dangling(by["beta"], missing)
        self.assertEqual(by["beta"].routes_to_missing, [])

    def test_vendored_copies(self):
        by = self._skills()
        self.assertEqual(si.vendored_copies(self.cfg.projects_root, by["alpha"]), ["repoA"])
        gamma = si.enumerate_commands(self.cfg.config_repo, tracked=None)[0]
        self.assertEqual(si.vendored_copies(self.cfg.projects_root, gamma), ["repoB"])
        self.assertEqual(si.vendored_copies(self.cfg.projects_root, by["beta"]), [])

    def test_duplicates(self):
        plugins = si.enumerate_plugins(self.cfg.claude_home)
        idx = si.plugin_skill_index(plugins)
        self.assertEqual(idx, {"tdd": "mp:tdd"})

    def test_last_edited_falls_back_to_mtime(self):
        by = self._skills()
        d = si.last_edited(self.cfg.config_repo, by["alpha"])
        self.assertEqual(d, datetime.now(timezone.utc).date().isoformat())
```

- [ ] **Step 2: Run to verify they fail**

Run: `python3 skills/retire/scripts/tests/test_steering_inventory.py -v 2>&1 | grep -E 'ERROR|FAIL|Ran'`
Expected: 7 errors, `AttributeError … 'build_corpus'` and siblings.

- [ ] **Step 3: Implement**

Append:

```python
# ---------------------------------------------------------------- cross-references

def build_corpus(config_repo: Path, claude_home: Path) -> dict[str, str]:
    """path -> text for every file that can route to an item. Prompt hooks count as referrers."""
    files: list[Path] = []
    files += sorted((config_repo / "skills").rglob("*.md")) if (config_repo / "skills").is_dir() else []
    files += sorted((config_repo / "commands").glob("*.md*")) if (config_repo / "commands").is_dir() else []
    files += sorted((config_repo / "agents").glob("*.md")) if (config_repo / "agents").is_dir() else []
    files += [config_repo / "CLAUDE.md", config_repo / "operating-constraints.md"]
    corpus = {str(p): p.read_text(errors="ignore") for p in files if p.is_file()}
    settings_path = claude_home / "settings.json"
    if settings_path.exists():
        try:
            settings = load_json(settings_path)
        except SourceMissing:
            settings = {}
        for event, groups in (settings.get("hooks") or {}).items():
            for group in groups or []:
                for hook in (group or {}).get("hooks") or []:
                    if hook.get("type") == "prompt":
                        corpus[f"settings.json:{event} prompt hook"] = hook.get("prompt") or ""
    return corpus


def _own_paths(it: Item, config_repo: Path) -> set[str]:
    if it.surface == "skill":
        return {str(q) for q in Path(it.path).parent.rglob("*.md")}
    if it.surface == "claude-md":
        return {str(config_repo / "CLAUDE.md"), str(config_repo / "operating-constraints.md")}
    return {it.path}


def _display_name(it: Item) -> str:
    return it.name.split("@")[0] if it.surface == "plugin" else it.name


def attach_referrers(it: Item, corpus: dict[str, str], config_repo: Path) -> None:
    if it.surface in ("hook", "memory"):
        return
    rx = re.compile(r"(?<![\w-])" + re.escape(_display_name(it)) + r"(?![\w-])", re.I)
    own = _own_paths(it, config_repo)
    it.referrers = sorted(k for k, text in corpus.items() if k not in own and rx.search(text))


def missing_names(command_items: list[Item], config_repo: Path) -> set[str]:
    """Names a route can dangle on: paused commands + everything in docs/retired.md's Item column."""
    names = {c.name for c in command_items if c.paused}
    ledger = config_repo / "docs" / "retired.md"
    if ledger.exists():
        for ln in ledger.read_text(errors="ignore").splitlines():
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(cells) >= 3 and re.match(r"\d{4}-\d{2}-\d{2}", cells[0]):
                names.add(re.sub(r"\s*\(.*\)$", "", cells[1].strip("`")))
    return names


def _item_text(it: Item) -> str:
    if it.surface == "claude-md":
        return it.extra.get("body", "")
    if it.surface in ("skill", "command", "agent", "output-style"):
        try:
            return Path(it.path).read_text(errors="ignore")
        except OSError:
            return ""
    if it.surface == "hook":
        return it.extra.get("command", "")
    return ""


def attach_dangling(it: Item, missing: set[str]) -> None:
    """A route is `/name` or `` `name` ``; bare prose words don't count (too noisy for names like `learn`)."""
    text = _item_text(it)
    hits = sorted(n for n in missing if n != it.name and re.search(r"(?:/|`)" + re.escape(n) + r"(?![\w-])", text, re.I))
    it.routes_to_missing = hits
    if hits and "dangling" not in it.flags:
        it.flags.append("dangling")


def vendored_copies(projects_root: Path, it: Item) -> list[str]:
    if it.surface not in ("skill", "command", "agent") or not projects_root.is_dir():
        return []
    hits: list[str] = []
    for repo in sorted(projects_root.iterdir()):
        if not repo.is_dir():
            continue
        c = repo / ".claude"
        if it.surface == "skill" and (c / "skills" / it.name).is_dir():
            hits.append(repo.name)
        elif it.surface == "command" and (c / "commands" / f"{it.name}.md").exists():
            hits.append(repo.name)
        elif it.surface == "agent" and (c / "agents" / f"{it.name}.md").exists():
            hits.append(repo.name)
    return hits


def plugin_skill_index(plugin_items: list[Item]) -> dict[str, str]:
    """skill name -> 'pluginshort:name' for every skill an ENABLED plugin ships."""
    idx: dict[str, str] = {}
    for p in plugin_items:
        if not p.extra.get("enabled"):
            continue
        short = p.name.split("@")[0]
        for s in p.extra.get("skills", []):
            idx.setdefault(s["name"], f"{short}:{s['name']}")
    return idx


def git_last_edited(repo: Path, rel: str) -> str | None:
    try:
        out = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%as", "--", rel],
                             capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    return out or None


def last_edited(config_repo: Path, it: Item) -> str | None:
    if it.surface not in ("skill", "command", "agent", "output-style"):
        return None
    p = Path(it.path)
    if it.tracked:
        rel = f"skills/{it.name}" if it.surface == "skill" else str(p.relative_to(config_repo))
        d = git_last_edited(config_repo, rel)
        if d:
            return d
    try:
        return datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).date().isoformat()
    except OSError:
        return None
```

- [ ] **Step 4: Run to verify they pass**

Run: `python3 skills/retire/scripts/tests/test_steering_inventory.py -v 2>&1 | grep -E 'ERROR|FAIL|Ran|OK'`
Expected: `Ran 32 tests` … `OK`.

- [ ] **Step 5: Commit**

```bash
git add skills/retire/scripts/
git commit -m "feat(retire): referrers, dangling routes, vendored copies, duplicates, last-edited

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01F6oTCwzx8WmJuYuN4Q3nJr"
```

---

### Task 7: Assembly, temperature, totals, renderers, CLI

**Files:**
- Modify: `skills/retire/scripts/steering_inventory.py`
- Modify: `skills/retire/scripts/tests/test_steering_inventory.py`

- [ ] **Step 1: Write the failing tests**

```python
class InventoryTests(FixtureCase):
    def setUp(self):
        super().setUp()
        self.inv = si.build_inventory(self.cfg)
        self.by = {i.id: i for i in self.inv.items}

    def test_temperatures(self):
        t = {k: v.temperature for k, v in self.by.items()}
        self.assertEqual(t["skill:alpha"], "warm")          # 1 slash + 1 tool + 1 trigger in window
        self.assertEqual(t["skill:beta"], "cool")           # unused, but alpha refers to it
        self.assertEqual(t["skill:tdd"], "cold")
        self.assertEqual(t["command:gamma"], "cool")        # used 200 days ago
        self.assertEqual(t["command:old"], "cool")          # alpha routes to it
        self.assertEqual(t["agent:judge"], "cool")
        self.assertEqual(t["output-style:plain"], "cold")
        self.assertEqual(t["claude-md:Improvement Mode"], "cool")   # Stop hook names it
        self.assertEqual(t["claude-md:Git Workflow"], "cold")
        self.assertEqual(t["plugin:mp@mp"], "warm")
        self.assertEqual(t["mcp:todoist"], "warm")
        self.assertEqual(t["mcp:docker"], "cold")

    def test_evidence_fields(self):
        a = self.by["skill:alpha"]
        self.assertEqual((a.slash_90d, a.tool_90d, a.trigger_90d), (1, 1, 1))
        self.assertEqual(a.vendored_copies, ["repoA"])
        self.assertEqual(a.routes_to_missing, ["old"])
        self.assertEqual(a.last_used, (NOW - timedelta(days=2)).date().isoformat())
        self.assertEqual(self.by["skill:tdd"].duplicate_of, "mp:tdd")
        self.assertIn("duplicate", self.by["skill:tdd"].flags)
        self.assertEqual(self.by["claude-md:Improvement Mode"].trigger_all, 0)
        self.assertIsNone(self.by["claude-md:Git Workflow"].trigger_all)
        self.assertEqual(self.by["agent:judge"].last_used, (NOW - timedelta(days=150)).date().isoformat())

    def test_totals_and_meta(self):
        cm = (self.cfg.config_repo / "CLAUDE.md").read_text() + (self.cfg.config_repo / "operating-constraints.md").read_text()
        self.assertEqual(self.inv.totals["claude-md"]["always_loaded_chars"], len(cm))
        self.assertEqual(self.inv.totals["skill"]["always_loaded_chars"],
                         sum(len(d) for d in ("Alpha does things. Use when Kyle says \"alpha please\" or \"run alpha now\". Hands off to beta and /old.",
                                              "Beta does other things across lines.", "Loose copy of tdd.")))
        self.assertEqual(self.inv.totals["plugin"]["always_loaded_chars"], len("Plugin tdd skill."))
        self.assertEqual(self.inv.totals["ALL"]["items"], len(self.inv.items))
        self.assertEqual(self.inv.meta["history_rows"], 5)
        self.assertEqual(self.inv.meta["transcripts_scanned"], 1)

    def test_renderers(self):
        md = si.render_markdown(self.inv)
        self.assertIn("## Totals", md)
        self.assertIn("## claude-md", md)
        self.assertIn("| `Improvement Mode`", md)
        js = json.loads(si.render_json(self.inv))
        self.assertEqual(js["meta"]["since_days"], 90)
        first = js["items"][0]
        self.assertNotIn("body", first["extra"])
        self.assertIn("invocations_90d", first)

    def test_oversized_flag_needs_ten_items(self):
        self.assertFalse(any("oversized" in i.flags for i in self.inv.items))


class CliTests(FixtureCase):
    def _args(self, *extra):
        return ["--claude-home", str(self.cfg.claude_home), "--config-repo", str(self.cfg.config_repo),
                "--projects-root", str(self.cfg.projects_root), "--claude-json", str(self.cfg.claude_json),
                "--triggers", str(self.root / "triggers.json"), "--no-cache", *extra]

    def setUp(self):
        super().setUp()
        (self.root / "triggers.json").write_text(json.dumps({"Improvement Mode": ["improvement mode"], "Git Workflow": None}))

    def test_writes_json_and_md(self):
        out_json, out_md = self.root / "inv.json", self.root / "inv.md"
        rc = si.main(self._args("--json", str(out_json), "--md", str(out_md)))
        self.assertEqual(rc, 0)
        self.assertIn("## Totals", out_md.read_text())
        self.assertEqual(json.loads(out_json.read_text())["meta"]["since_days"], 90)

    def test_missing_source_exits_2(self):
        (self.cfg.claude_home / "history.jsonl").unlink()
        self.assertEqual(si.main(self._args()), 2)

    def test_empty_surface_exits_3(self):
        for n in ("alpha", "beta", "tdd"):
            (self.cfg.config_repo / f"skills/{n}/SKILL.md").unlink()
        self.assertEqual(si.main(self._args()), 3)
```

- [ ] **Step 2: Run to verify they fail**

Run: `python3 skills/retire/scripts/tests/test_steering_inventory.py -v 2>&1 | grep -E 'ERROR|FAIL|Ran'`
Expected: 8 errors, `AttributeError … 'build_inventory'` / `'main'`.

- [ ] **Step 3: Implement**

Append:

```python
# ---------------------------------------------------------------- assembly

def attach_usage(it: Item, history: History, transcripts: Transcripts, since: datetime) -> None:
    last_s = last_t = None
    if it.surface in ("skill", "command"):
        it.slash_all, it.slash_90d, last_s = history.count(slash_pattern(it.name), since)
        it.tool_all, it.tool_90d, last_t = transcripts.count("skill", it.name, since)
    elif it.surface == "agent":
        it.tool_all, it.tool_90d, last_t = transcripts.count("agent", it.name, since)
    elif it.surface == "plugin":
        short = it.name.split("@")[0]
        lasts: list[str | None] = []
        for sk in it.extra.get("skills", []):
            key = f"{short}:{sk['name']}"
            a, r, l1 = history.count(slash_pattern(key), since)
            b, s, l2 = transcripts.count("skill", key, since)
            it.slash_all += a; it.slash_90d += r; it.tool_all += b; it.tool_90d += s
            lasts += [l1, l2]
        last_s = max((x for x in lasts if x), default=None)
    elif it.surface == "mcp":
        it.tool_all, it.tool_90d, last_t = transcripts.count("mcp", it.name, since)
    else:
        return
    it.last_used = max((d for d in (last_s, last_t) if d), default=None)


def attach_triggers(it: Item, history: History, since: datetime, triggers: dict | None) -> None:
    if it.surface == "claude-md":
        pats = (triggers or {}).get(it.name)
    elif it.surface in ("skill", "command", "agent", "plugin"):
        pats = phrases_from_description(it.description)
    else:
        pats = None
    if not pats:
        it.trigger_all = it.trigger_90d = None
        return
    it.trigger_all, it.trigger_90d, last = history.count_any(pats, since)
    if last and (it.last_used is None or last > it.last_used):
        it.last_used = last


def temperature(it: Item) -> str:
    recent = it.invocations_90d + (it.trigger_90d or 0)
    if recent >= 5:
        return "hot"
    if recent >= 1:
        return "warm"
    if it.referrers or it.invocations_all or (it.trigger_all or 0):
        return "cool"
    return "cold"


def mark_oversized(items: list[Item]) -> None:
    """Top decile of always-loaded bytes within a surface, only when the surface has ≥10 sized items."""
    for surface in SURFACE_ORDER:
        sized = sorted((i for i in items if i.surface == surface and i.bytes_always_loaded > 0), key=lambda i: i.bytes_always_loaded)
        if len(sized) < 10:
            continue
        cutoff = sized[int(len(sized) * 0.9)].bytes_always_loaded
        for i in sized:
            if i.bytes_always_loaded >= cutoff:
                i.flags.append("oversized")


def compute_totals(items: list[Item], config_repo: Path) -> dict:
    totals = {s: {"items": 0, "always_loaded_chars": 0} for s in SURFACE_ORDER}
    for it in items:
        totals[it.surface]["items"] += 1
        if it.surface != "claude-md":
            totals[it.surface]["always_loaded_chars"] += it.bytes_always_loaded
    cm = 0
    for f in ("CLAUDE.md", "operating-constraints.md"):
        p = config_repo / f
        if p.exists():
            cm += len(p.read_text(errors="ignore"))
    totals["claude-md"]["always_loaded_chars"] = cm      # file bytes, not the sum of nested sections
    totals["ALL"] = {"items": sum(v["items"] for v in totals.values()),
                     "always_loaded_chars": sum(v["always_loaded_chars"] for v in totals.values())}
    return totals


def build_inventory(cfg: Config) -> Inventory:
    since = datetime.now(timezone.utc) - timedelta(days=cfg.since_days)
    tracked = git_tracked(cfg.config_repo)
    items: list[Item] = []
    items += enumerate_claude_md(cfg.config_repo)
    items += enumerate_skills(cfg.config_repo, tracked)
    commands = enumerate_commands(cfg.config_repo, tracked)
    items += commands
    items += enumerate_agents(cfg.config_repo, tracked)
    items += enumerate_output_styles(cfg.config_repo, tracked)
    plugins = enumerate_plugins(cfg.claude_home)
    items += plugins
    items += enumerate_mcp(cfg.claude_json)
    items += enumerate_hooks(cfg.claude_home)
    items += enumerate_memory(cfg.claude_home)

    history = History(cfg.claude_home / "history.jsonl")
    transcripts = Transcripts(cfg.claude_home / "projects", cfg.cache_path)
    corpus = build_corpus(cfg.config_repo, cfg.claude_home)
    dup_index = plugin_skill_index(plugins)
    missing = missing_names(commands, cfg.config_repo)

    for it in items:
        attach_usage(it, history, transcripts, since)
        attach_triggers(it, history, since, cfg.triggers)
        attach_referrers(it, corpus, cfg.config_repo)
        attach_dangling(it, missing)
        it.vendored_copies = vendored_copies(cfg.projects_root, it)
        if it.surface == "skill" and it.name in dup_index:
            it.duplicate_of = dup_index[it.name]
            it.flags.append("duplicate")
        it.last_edited = last_edited(cfg.config_repo, it)
    mark_oversized(items)
    for it in items:
        it.temperature = temperature(it)
    meta = {"since_days": cfg.since_days, "since": since.date().isoformat(),
            "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "history_rows": len(history.rows), "transcripts_scanned": transcripts.files_scanned,
            "transcripts_cache_hits": transcripts.cache_hits, "git_tracked": tracked is not None,
            "config_repo": str(cfg.config_repo), "claude_home": str(cfg.claude_home)}
    return Inventory(items=items, totals=compute_totals(items, cfg.config_repo), meta=meta)


# ---------------------------------------------------------------- output

def _fmt_trig(n: int | None) -> str:
    return "—" if n is None else str(n)


def evidence_summary(it: Item, since_days: int) -> str:
    parts = [f"use {it.invocations_90d}/{since_days}d · {it.invocations_all} all",
             f"trig {_fmt_trig(it.trigger_90d)}/{_fmt_trig(it.trigger_all)}",
             f"last {it.last_used or '—'}", f"refs {len(it.referrers)}", f"{it.bytes_always_loaded:,} chars"]
    if it.vendored_copies:
        parts.append(f"vendored ×{len(it.vendored_copies)}")
    if it.duplicate_of:
        parts.append(f"dup of `{it.duplicate_of}`")
    if it.routes_to_missing:
        parts.append("routes→ " + ", ".join(it.routes_to_missing))
    return " · ".join(parts)


def render_markdown(inv: Inventory) -> str:
    m = inv.meta
    out = [f"# Steering inventory — {m['generated'][:10]}", "",
           f"Window: last {m['since_days']} days (since {m['since']}). History rows: {m['history_rows']:,}. "
           f"Transcripts scanned: {m['transcripts_scanned']:,}. Read-only; an Instrument, never a Gate.", "",
           "## Totals", "", "| Surface | Items | Always-loaded chars |", "|---|---|---|"]
    for s in SURFACE_ORDER + ["ALL"]:
        t = inv.totals[s]
        out.append(f"| {s} | {t['items']} | {t['always_loaded_chars']:,} |")
    for s in SURFACE_ORDER:
        rows = sorted((i for i in inv.items if i.surface == s), key=lambda i: (TEMP_ORDER[i.temperature], -i.bytes_always_loaded, i.name))
        if not rows:
            continue
        out += ["", f"## {s}", "", "| Item | Evidence | Flags | Temp |", "|---|---|---|---|"]
        for i in rows:
            out.append(f"| `{i.name}` | {evidence_summary(i, m['since_days'])} | {', '.join(i.flags) or '—'} | {i.temperature} |")
    return "\n".join(out) + "\n"


def render_json(inv: Inventory) -> str:
    return json.dumps({"meta": inv.meta, "totals": inv.totals, "items": [i.to_dict() for i in inv.items]}, indent=1)


# ---------------------------------------------------------------- CLI

def _default_config_repo(claude_home: Path) -> Path:
    skills = claude_home / "skills"
    return skills.resolve().parent if skills.is_symlink() else claude_home


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Read-only inventory of every global Claude Code steering surface.")
    ap.add_argument("--since", type=int, default=90, help="window in days (default 90)")
    ap.add_argument("--json", help="write the full inventory as JSON here")
    ap.add_argument("--md", help="write the markdown report here (default: stdout when --json is absent)")
    ap.add_argument("--claude-home", default=os.path.expanduser("~/.claude"))
    ap.add_argument("--config-repo", default=None, help="default: resolved target of ~/.claude/skills")
    ap.add_argument("--projects-root", default=os.path.expanduser("~/Projects"))
    ap.add_argument("--claude-json", default=os.path.expanduser("~/.claude.json"))
    ap.add_argument("--triggers", default=None, help="JSON: CLAUDE.md section title -> [regex,…] | null (default: claude_md_triggers.json beside this script)")
    ap.add_argument("--no-cache", action="store_true", help="do not read or write the transcript cache")
    args = ap.parse_args(argv)

    claude_home = Path(args.claude_home)
    config_repo = Path(args.config_repo) if args.config_repo else _default_config_repo(claude_home)
    triggers_path = Path(args.triggers) if args.triggers else Path(__file__).with_name("claude_md_triggers.json")
    triggers = None
    if triggers_path.exists():
        try:
            triggers = json.loads(triggers_path.read_text())
        except ValueError as e:
            print(f"ERROR triggers file unreadable: {triggers_path}: {e}", file=sys.stderr)
            return EXIT_SOURCE_MISSING
    cfg = Config(claude_home=claude_home, config_repo=config_repo, projects_root=Path(args.projects_root),
                 claude_json=Path(args.claude_json), since_days=args.since, triggers=triggers,
                 cache_path=None if args.no_cache else claude_home / "cache" / "retire" / "transcripts.json")
    try:
        inv = build_inventory(cfg)
    except SourceMissing as e:
        print(f"ERROR source missing or unreadable — refusing to report a false 0: {e}", file=sys.stderr)
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
    print(f"OK {inv.totals['ALL']['items']} items · {inv.totals['ALL']['always_loaded_chars']:,} always-loaded chars · "
          f"{inv.meta['transcripts_scanned']:,} transcripts ({inv.meta['transcripts_cache_hits']:,} cached)", file=sys.stderr)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run to verify they pass**

Run: `python3 skills/retire/scripts/tests/test_steering_inventory.py -v 2>&1 | grep -E 'ERROR|FAIL|Ran|OK'`
Expected: `Ran 40 tests` … `OK`.

If `test_temperatures` fails on `plugin:mp@mp`: the plugin item's `description` is empty, so `attach_triggers` sets `None`; its warmth must come from `slash_90d` (`/mp:tdd`) + `tool_90d` (`Skill mp:tdd`) = 2 → `warm`. Check `slash_pattern("mp:tdd")` escapes the colon.

- [ ] **Step 5: Smoke the CLI against the fixture by hand**

Run (from repo root, with a throwaway fixture):
```bash
python3 - <<'EOF'
import sys, tempfile
from pathlib import Path
sys.path.insert(0, "skills/retire/scripts/tests"); sys.path.insert(0, "skills/retire/scripts")
import test_steering_inventory as t, steering_inventory as si
d = Path(tempfile.mkdtemp()); cfg = t.make_fixture(d)
print(si.render_markdown(si.build_inventory(cfg)))
EOF
```
Expected: a Totals table followed by per-surface tables; `alpha` row shows `use 2/90d · 2 all · trig 1/1 · … · vendored ×1 · routes→ old`.

- [ ] **Step 6: Commit**

```bash
git add skills/retire/scripts/
git commit -m "feat(retire): inventory assembly, temperatures, totals, markdown/JSON renderers, CLI

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01F6oTCwzx8WmJuYuN4Q3nJr"
```

---

### Task 8: Trigger sidecar and the first live read-only run

**Files:**
- Create: `skills/retire/scripts/claude_md_triggers.json`
- Create: `docs/reports/2026-09-XX-steering-inventory.md` (use today's date)

- [ ] **Step 1: Write the trigger sidecar**

Titles must match the global CLAUDE.md headings **exactly** (arrow, backticks, parenthetical dates included). Verify with `grep -n -E '^#{2,3} ' CLAUDE.md` before writing; if a heading has changed, change the key.

```json
{
  "operating-constraints.md": null,
  "Kickoff Mode → run the `/kickoff` skill": ["kickoff mode", "new project idea", "^\\s*/kickoff"],
  "Improvement Mode": ["improvement mode"],
  "New Feature Mode": ["new feature mode", "feature mode"],
  "Git Workflow": null,
  "Clarifying questions and option formatting": null,
  "Never show me a bare identifier (added 2026-08-13)": ["bare identifier", "\\bgloss"],
  "Planner/Builder Protocol (added 2026-07-27)": ["run-config", "--effort", "planner/builder"],
  "Reference Doc Maintenance": ["reference doc", "playbook card", "check-doc-sync"],
  "When to update": null,
  "Format rules": null,
  "Local-Markdown Issue Tracker: Tickets Index (added 2026-08-22)": ["/to-tickets", "tickets\\.md", "/implement-spec", "/wayfinder"],
  "Project Wiki": ["/wiki-init", "/wiki-backfill", "project-wiki", "handoff\\.md"]
}
```

`null` means "no trigger phrase is a fair proxy for this rule" — the report shows `—`, never `0`, so a rule like Git Workflow (which fires on every session, silently) is never mistaken for dead.

- [ ] **Step 2: Run the live inventory (read-only)**

Run:
```bash
python3 skills/retire/scripts/steering_inventory.py \
  --json "$SCRATCH/inventory.json" --md docs/reports/$(date +%F)-steering-inventory.md
```
where `$SCRATCH` is the session scratchpad. First run scans ~6,100 transcripts (3.1 GB) and takes a few minutes; it writes `~/.claude/cache/retire/transcripts.json` so re-runs are seconds.

Expected on stderr: `OK <N> items · <M> always-loaded chars · 6,1xx transcripts (0 cached)`; exit 0.

- [ ] **Step 3: Sanity-check the numbers against this session's hand counts**

Run:
```bash
python3 - <<EOF
import json; inv=json.load(open("$SCRATCH/inventory.json")); by={i["id"]:i for i in inv["items"]}
print("adversarial-review tool_all", by["skill:adversarial-review"]["tool_all"], "(hand count 2026-09-17: 158)")
print("Improvement Mode trigger_all", by["claude-md:Improvement Mode"]["trigger_all"], "(hand: 0)")
print("New Feature Mode trigger_all", by["claude-md:New Feature Mode"]["trigger_all"], "(hand: 0)")
print("duplicates", sum(1 for i in inv["items"] if "duplicate" in i["flags"]), "(hand: 36)")
print("dangling", [i["name"] for i in inv["items"] if "dangling" in i["flags"]], "(hand: backlog-hygiene, reorient, replenish, brainstorm, prompt-optimize)")
print("kapture mcp tool_all", by["mcp:kapture"]["tool_all"], "(hand: 2635)")
print("totals", inv["totals"]["ALL"])
EOF
```
Expected: `adversarial-review` ≥ 158 (it may have grown), Improvement/Feature Mode = 0, duplicates = 36, the five dangling names present (others may appear too — the hand grep was narrower), kapture ≥ 2635. If any is lower than the hand count, the extraction is missing events — fix before proceeding (compare `grep -rc '"name":"Skill","input":{"skill":"adversarial-review"' ~/.claude/projects` with the JSON).

- [ ] **Step 4: Commit the sidecar and the report**

```bash
git add skills/retire/scripts/claude_md_triggers.json docs/reports/$(date +%F)-steering-inventory.md
git commit -m "feat(retire): CLAUDE.md trigger sidecar + first live read-only steering inventory

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01F6oTCwzx8WmJuYuN4Q3nJr"
```

---

### Task 9: Ledger file and the reference-doc pointer

**Files:**
- Create: `docs/retired.md`
- Modify: `docs/command-skill-reference.md:8` (intro paragraph)

- [ ] **Step 1: Seed the ledger**

```markdown
# Retired items

One line per removal from the global steering surface. Source of truth for "why is X gone"
and "how do I get it back". Written by the [`retire`](../skills/retire/SKILL.md) skill; edit
by hand only to correct a line. Restore a tracked item with
`git show <sha>^:<path> > <path>` (the SHA is the retirement commit); an untracked one from
the backup path. Downstream copies are repo **names** only (this repo is public) so a later
fleet prune knows what to hunt.

| Date | Item | Surface | Why | Evidence at retirement | Restore | Downstream copies |
|---|---|---|---|---|---|---|

## Kept on purpose

Items ruled `keep` with a clause, so they aren't re-proposed. Re-open only if usage changes.

| Date | Item | Keep because |
|---|---|---|
```

- [ ] **Step 2: Add the pointer sentence to the reference doc intro**

In `docs/command-skill-reference.md`, after the line `Every row below links to its card with \`config →\`.` add one sentence:

```markdown
Items removed on purpose are logged in [`retired.md`](retired.md) with restore pointers.
```

- [ ] **Step 3: Verify doc-sync still passes**

Run: `python3 scripts/check-doc-sync.py`
Expected: passes (the ledger is not a row or card).

- [ ] **Step 4: Commit**

```bash
git add docs/retired.md docs/command-skill-reference.md
git commit -m "docs: seed docs/retired.md ledger and point the reference index at it

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01F6oTCwzx8WmJuYuN4Q3nJr"
```

---

### Task 10: The skill — SKILL.md, bookkeeping reference, index row, playbook card (one commit)

**Files:**
- Create: `skills/retire/SKILL.md`
- Create: `skills/retire/references/bookkeeping.md`
- Modify: `docs/command-skill-reference.md` (row after the `orchestrate` row, ~line 100)
- Modify: `docs/usage-playbook.md` (card after the `orchestrate` card, before `### Quality & Debugging` ~line 610)

- [ ] **Step 1: Write `skills/retire/SKILL.md`**

````markdown
---
name: retire
description: Evidence-ranked subtraction for the global steering surface — inventories every CLAUDE.md section, skill, command, agent, plugin, MCP server, hook, output style, and auto-memory dir with usage evidence from history and transcripts; proposes retire / keep / merge / relocate verdicts; applies only what Kyle ratifies, with full bookkeeping (index row, playbook card, referrers, .gitignore, ledger, backups) and a before → after weight table. Modes: `/retire` (sweep), `/retire --report` (read-only), `/retire <item>…` (targeted). Use when Kyle types /retire or says "retire", "cleanse my config", "declutter claude code", "what can I get rid of", "prune my skills", "what's steering my sessions". NOT for: relocating content that stays (/trim-context), repo-side bloat inside a project (/trim-context there), pruning vendored copies in other repos (reported only), or re-opening the harness-disable ruling (decided 2026-08-22).
---

# Retire

**The subtract verb.** The config only grows: everything was added for a reason and nothing has a
removal path, so old intent keeps steering new sessions and every request pays for it. Retire
inventories every global steering surface with evidence, proposes verdicts, and removes only what
Kyle ratifies — completely, reversibly, and with the bookkeeping done.

Design: `docs/superpowers/specs/2026-09-17-retire-skill-design.md`. Ledger: `docs/retired.md`.
Apply checklist: `references/bookkeeping.md`. Inventory: `scripts/steering_inventory.py`.

## Prime directives

1. **Ratify before remove.** Nothing is removed for an unratified row. Silence is not consent:
   unanswered rows are not applied.
2. **Never `rm -rf`.** Tracked items: `git rm`. Untracked items: tar to `~/.claude/backups/retired-<date>/`
   then `mv` out. (`block-rm-rf.sh` rejects `rm -rf` outside `/tmp/` anyway.)
3. **Untracked settings change only on Kyle's per-item word.** `~/.claude/settings.json`,
   `~/.claude.json`, plugin toggles — back the file up first (`<file>.pre-retire-<ts>`).
4. **Never touch a project repo.** Vendored copies are reported in the ledger and PR, never edited.
5. **No false cleans.** The inventory script exits 2/3 rather than report a 0 it didn't measure.
   A failed run stops the skill; it never proceeds on partial evidence.
6. **Branch + PR, review gate proposed.** Diffs under `skills/**`, `commands/**`, `agents/**`, or
   `CLAUDE.md` are behavioral: propose at least a single review round. Interactive: Kyle rules.

## Modes

| Form | Behavior |
|---|---|
| `/retire` | Sweep: Steps 0–6. |
| `/retire --report` | Steps 0–2, write the report, stop. No edits. |
| `/retire <item> [<item>…]` | Targeted: Step 0, then Steps 3–6 for the named items only. Names resolve across surfaces (`mock-call`, `commands/learn`, `plugin:swift-lsp`, `mcp:MCP_DOCKER`, `claude-md:Improvement Mode`); an ambiguous name stops and asks. |

## Procedure

### Step 0 — Preflight

- Confirm the config repo (`~/.claude/skills` → its resolved parent) has a clean tree; create
  `chore/retire-<date>` from `main`. Never work on `main`, never stash or reset Kyle's work.
- Run the inventory:
  ```bash
  python3 skills/retire/scripts/steering_inventory.py --json "$SCRATCH/before.json" --md "$SCRATCH/before.md"
  ```
  Exit 2 or 3 → report the stderr line and **stop**.

### Step 1 — Inventory

Read `$SCRATCH/before.md`. Note the Totals table (this is the "before" column of Step 5).

### Step 2 — Propose verdicts

The script gives each item a **temperature** and **flags**; the skill proposes a **verdict**:

| Signal | Proposed verdict |
|---|---|
| `cold`, not `paused` | `retire` |
| `duplicate` | `retire` the non-canonical copy (the loose `skills/` copy when a plugin ships the same skill) |
| `dangling` | not a verdict on this item — an apply step: patch the route (Step 4, referrers) |
| `hot` | `keep` (silent, no ledger line) unless `oversized` → `relocate` |
| `paused` (`.md.disabled`) | `ask`: retire → ledger, or stay paused |
| `disabled_comment` hook, `empty` memory dir | `retire` (mechanical) |
| everything else | `ask` |

Verdict classes: `retire` · `keep` (optionally with a "keep because" clause → ledger's Kept table)
· `merge-into <x>` (retire this, record the merge; the merge edit is a follow-up PR) ·
`relocate` (stays; hand the item to `/trim-context`; no edit here) · `ask`.

A rare-but-load-bearing item (`envsetup`, `claudify-repo`) is exactly why `cold` proposes and
never decides.

`--report`: write `docs/reports/<date>-steering-inventory.md` = the script's markdown plus this
verdict table, commit on the branch, and stop.

### Step 3 — Ratification (STOP)

Present one table, every row titled (global bare-identifier rule), grouped by surface, `retire`
rows first, then `ask`, then `relocate`. Omit silent `keep` rows but say how many.

```
| # | Item | Surface | Evidence | Proposed | Why |
|---|---|---|---|---|---|
| 1 | Improvement Mode (CLAUDE.md §22–36) | claude-md | 0 hits ever · 1 referrer (Stop hook) · 1.1k chars | retire | never triggered in 5,398 prompts |
| 2 | mock-call (skill) | skill | 0/90d · 3 all-time · last 2026-07-02 · 0 referrers · 651 chars | ask | cold but recent; interview |
```

Say: *"Answer by row: `1 retire, 2 keep — interview season, 5 relocate, rest as proposed`.
Unanswered rows are not applied."* Then **STOP and wait**. In an unattended run there is no
one to answer: write the table to the report file and stop — retire never applies unratified.

Parse the reply. `rest as proposed` applies the proposed verdict to every row not named.
`ask` rows without an answer stay unapplied.

### Step 4 — Apply

For each ratified `retire` row, run the surface's checklist in `references/bookkeeping.md`,
in order, verifying each step before the next. A step that can't complete cleanly stops
**that item** (never a partial removal) and is reported. Untracked settings items wait for
Kyle's word at this step even though the row was ratified — the row ratified the *verdict*;
the file edit gets its own one-word confirmation because it isn't reversible by git.

`keep` with a clause → append to the ledger's **Kept on purpose** table. `merge-into` → retire
the item; write "merge-into <x>" in the ledger's Why column. `relocate` → list the items in the
PR body under "Hand to /trim-context"; make no edit.

### Step 5 — Measure

Re-run the inventory to `$SCRATCH/after.json` / `after.md`. Assert every retired item is absent
from every surface it was on. Build the before → after table from the two Totals sections:

```
Surface                          Before    After    Δ
Global CLAUDE.md + constraints   24,033   19,450  -4,583
Skill descriptions (skills/)     34,108   21,200 -12,908
```

If Kyle pastes `/context` output from a fresh session before and after, include it as the
wire-level check; do not try to run `/context` yourself.

### Step 6 — Ship

- `python3 scripts/check-doc-sync.py` must pass. Commit per item or per surface (conventional
  commits: `chore(retire): remove <item> — <why>`), push, open the PR with: the ratification
  table as ruled, the before → after table, the ledger diff, "Hand to /trim-context" (if any),
  and "Downstream copies (report only)" listing each retired item's vendored repos by name.
- Propose the review scope per the global gate (skills/CLAUDE.md diffs: at least single round)
  and, interactively, **STOP** for Kyle's call. Brief him: what changed, commit SHAs, PR link.

## Failure table

| Situation | Do |
|---|---|
| Inventory exits 2 (source missing) | Report the stderr line; stop. Never estimate. |
| Inventory exits 3 (empty surface) | Report; stop. Something is wrong with the checkout. |
| Referrer edit can't be excised cleanly | Leave the line; list it under "Needs a hand" in the PR. |
| Bare `/x` stops resolving after removing a loose plugin copy | Not a blocker: note the new spelling `plugin:x` in the playbook card that mentioned it. |
| Dirty tree at preflight | Stop and say what's dirty. Never stash. |
| An item is named in `/retire <item>` but ambiguous | List the matches; ask. |

## Handoffs

| Situation | Hand to |
|---|---|
| `relocate` verdict | `/trim-context` |
| retired item has vendored copies | ledger + PR body; a future fleet prune (`docs/ideas/fleet-manifest-reconcile.md`) |
| `merge-into` | follow-up PR |
| a CLAUDE.md rule is hook-convertible | `BACKLOG.md` stub; converting is its own change |
````

- [ ] **Step 2: Write `skills/retire/references/bookkeeping.md`**

````markdown
# Bookkeeping checklist — per retired item

Run in order. Verify each step before the next. A step that cannot complete cleanly stops the
item and is reported — never a partial removal. `$DATE` = today (`date +%F`); `$BK` =
`~/.claude/backups/retired-$DATE`.

## Skill (tracked, `skills/<name>/`)

1. `git rm -r skills/<name>`
2. Delete the row in `docs/command-skill-reference.md` and the card (`#### \`<name>\``) in
   `docs/usage-playbook.md`. `python3 scripts/check-doc-sync.py` must pass.
3. Referrers (from the inventory's `referrers` list): surgical excision —
   read the line, identify every other item token on it, remove only the target fragment,
   re-read and assert every other token survived; if the line is a whole sentence about the
   item, delete the sentence. If unsure, leave it and report. A `merge-into` target replaces
   the route instead of removing it.
4. Ledger line in `docs/retired.md`:
   `| $DATE | <name> | skill | <why, one clause> | <evidence_summary from the inventory> | git show <sha>^:skills/<name>/SKILL.md | <vendored_copies repo names or —> |`
   The SHA is the commit that removes it — write the line, commit, then amend the SHA in a
   follow-up commit, or use the retirement commit's parent-of notation `<sha>^`.
5. Re-run the inventory; assert `skill:<name>` is absent.

## Skill (untracked — gitignored, e.g. the loose mattpocock copies, `adhd`, `interview-prep`)

1. `mkdir -p "$BK" && tar czf "$BK/<name>.tar.gz" -C skills <name>`
2. `mv skills/<name> "$BK/<name>"`  (never `rm -rf`)
3. Remove the item's line(s) from `.gitignore`; if the comment block above now describes
   nothing, remove it too. Also remove any mention in `THIRD-PARTY.md` "Not listed here".
4. Referrers: as for tracked skills.
5. Ledger line with Restore = `$BK/<name>.tar.gz`.
6. Re-run the inventory; assert absent. **For a plugin duplicate**, also verify the bare name:
   open a fresh session and type `/<name>`; if it no longer resolves, the namespaced form
   (`/plugin:<name>`) is the spelling — note it in the ledger Why column.

## Command (`commands/<name>.md` or `.md.disabled`)

1. `git rm commands/<name>.md` (or `.md.disabled`).
2. Row + card: as for skills. A `.disabled` item's row was already rewritten "Disabled" — delete
   it now; its card too.
3. Referrers: as for skills. For a paused command, the `dangling` items in the inventory are
   exactly the referrers to patch.
4. Ledger line with Restore = `git show <sha>^:commands/<name>.md`.
5. Re-inventory; assert absent.

## Agent (`agents/<name>.md`)

1. `git rm agents/<name>.md`
2. Row under "Custom Subagents" in the reference doc; card under `## Custom Subagents` in the
   playbook (`### \`<name>\``). Doc-sync must pass.
3. Referrers: skills that dispatch it by name (`subagent_type: <name>`) must be edited or the
   skill itself retired — never leave a dispatch to a missing agent.
4. Ledger line; re-inventory.

## CLAUDE.md section

1. Show Kyle the exact section (heading through the line before the next same-level heading).
2. Delete it. If a `relocate` verdict was ruled instead, hand to `/trim-context` and do nothing.
3. Referrers: the Stop-hook prompt in `settings.json` names the mode sections — that edit is a
   **settings edit** (Kyle's word, backup first). Other CLAUDE.md sections that cross-reference
   the removed one: excise the sentence.
4. Ledger line with Restore = `git show <sha>^:CLAUDE.md` and the old line range in Why.
5. Re-inventory; assert `claude-md:<title>` is absent and the Totals row shrank.

## Output style (`output-styles/<name>.md`)

`git rm`; ledger line; re-inventory. No row/card exists for output styles.

## Plugin

1. Kyle's word, per plugin.
2. `cp ~/.claude/settings.json ~/.claude/settings.json.pre-retire-$(date +%s)`
3. Set `"enabledPlugins": {"<key>": false}` — or `claude plugin uninstall <key>` if Kyle wants it
   gone from disk too.
4. Ledger line (Surface `plugin`, Restore = "set enabledPlugins true" or "claude plugin install").
5. Re-inventory; the plugin item should show `disabled` (or be absent).

## MCP server

1. Kyle's word, per server.
2. `cp ~/.claude.json ~/.claude.json.pre-retire-$(date +%s)`
3. Remove the key from `mcpServers` (user scope). For a claude.ai connector, add
   `{"serverName": "claude.ai <Name>"}` to `deniedMcpServers` in `settings.json` instead.
4. Ledger line with the removed JSON block in Restore (one line, `\`{"command": …}\``).
5. Re-inventory; assert absent.

## Hook entry

1. Kyle's word, per entry.
2. Back up `settings.json` as above; delete the entry from its `hooks` array (and the empty
   group/event if nothing remains).
3. Ledger line with the removed command text in Restore.
4. Re-inventory.

## Auto-memory dir

- Empty dir: `rmdir ~/.claude/projects/<slug>/memory` (no word needed; nothing to lose).
- Non-empty: Kyle's word; `tar czf "$BK/memory-<slug>.tar.gz" -C ~/.claude/projects/<slug> memory`
  then move the files out. Ledger line with Restore = the tarball.

## Downstream copies (report only — every surface)

Append the item's `vendored_copies` repo names to its ledger line and to the PR body under
"Downstream copies (report only)". Do not edit those repos.
````

- [ ] **Step 3: Add the index row**

In `docs/command-skill-reference.md`, in the `### Session & Context Management` table, after the `orchestrate` row:

```markdown
| [`retire`](../skills/retire/SKILL.md) | Evidence-ranked subtraction for the global steering surface — inventories every CLAUDE.md section, skill, command, agent, plugin, MCP server, hook, and memory dir with usage evidence, proposes retire/keep verdicts you ratify, applies them with full bookkeeping and a retirement ledger, and reports before → after weight. Sweep, `--report`, or targeted `/retire <item>`. · [config →](usage-playbook.md#retire) |
```

- [ ] **Step 4: Add the playbook card**

In `docs/usage-playbook.md`, at the end of the `### Session & Context Management` section (after the `orchestrate` card, before `### Quality & Debugging`):

```markdown
#### `retire`

- **Run config:** Fable 5.1 · `xhigh` — ruling on what still steers you is convention-setting
  judgment; the counting is a script and needs no model at all.
- **Reach for it when:**
  - Sessions start heavy, or an old convention keeps steering new work and you want it gone,
    not relocated.
  - You're removing one thing and want the bookkeeping done — row, card, referrers, ledger:
    `/retire <item>`.
  - Quarterly: `/retire --report` for a read-only look at what went cold.
- **Pairs well with:** [`/trim-context`](#trim-context) (where `relocate` verdicts go),
  [`adversarial-review`](#adversarial-review) (the gate every apply pass proposes),
  [`/claudify-repo`](#claudify-repo) (vendored copies are reported, never pruned).
- **Notes:** nothing is removed before you ratify its row, and unanswered rows are not applied.
  Tracked items go through branch + PR; `settings.json`, `~/.claude.json`, and plugin toggles
  change only on your per-item word with a backup first. Never touches a project repo. The
  inventory script exits non-zero rather than report a false 0. Restore paths live in
  [`docs/retired.md`](retired.md).
```

- [ ] **Step 5: Verify doc-sync and that the skill is live**

Run: `python3 scripts/check-doc-sync.py && ls ~/.claude/skills/retire/SKILL.md`
Expected: doc-sync passes; the symlinked path exists.

- [ ] **Step 6: Commit (one commit — the sync rule)**

```bash
git add skills/retire/SKILL.md skills/retire/references/bookkeeping.md docs/command-skill-reference.md docs/usage-playbook.md
git commit -m "feat(retire): the retire skill — sweep / --report / targeted, bookkeeping checklist, index row, playbook card

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01F6oTCwzx8WmJuYuN4Q3nJr"
```

---

### Task 11: End-to-end `--report` run, push, PR A

**Files:**
- Modify: `docs/reports/<date>-steering-inventory.md` (append the verdict table)

- [ ] **Step 1: Run `/retire --report` as the skill, not by hand**

In the session, type `/retire --report`. Follow SKILL.md Steps 0–2. Expected: the report file gains
a "Proposed verdicts" table; the branch gets one commit; the skill stops without editing anything
else. If the skill drifts (edits something, asks the wrong question), fix `SKILL.md` and re-run.

- [ ] **Step 2: Push and update PR A**

PR A was opened when the spec and this plan landed (2026-09-17) — find it with
`gh pr list --head feat/retire-skill`. Push to it and replace its body; do not open a second PR.

```bash
python3 scripts/check-doc-sync.py && git push origin feat/retire-skill
gh pr edit "$(gh pr list --head feat/retire-skill --json number -q '.[0].number')" --body-file "$SCRATCH/pr-a.md"
```
`$SCRATCH/pr-a.md` body: spec link, what the script measures, the live Totals table from the report,
the test count, and this footer:
```
🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01F6oTCwzx8WmJuYuN4Q3nJr
```

- [ ] **Step 3: Propose the review scope and STOP**

The diff adds `skills/retire/**` (behavioral) and a tested script. Recommend **single round**:
the behavioral surface is one new skill with no callers yet; the script has 40 tests; the docs
are mechanical. Interactive: wait for Kyle's call. After the review lands clean and Kyle approves,
merge PR A and delete the remote branch.

---

### Task 12: Pilot sweep on the live config (PR B)

Run only after PR A is merged (the skill must be on `main` so the live symlink shows the reviewed
version). This task is the actual cleanse Kyle asked for.

- [ ] **Step 1: `git checkout main && git pull`, then type `/retire`**

Follow SKILL.md end to end. Step 0 creates `chore/retire-<date>`. The ratification table will
include at least these rows (from the 2026-09-17 evidence; the live run decides the exact list):

| Expected row | Proposed | Note |
|---|---|---|
| 36 loose mattpocock skill copies (`skills/ask-matt` … `skills/writing-shape`) + `find-skills` | retire (duplicate) | D7. Before applying, verify: `mv skills/tdd "$SCRATCH/tdd-probe"`, open a fresh session, type `/tdd`; note whether it resolves; `mv` it back. Then apply for all 36 per the untracked-skill checklist; remove the whole `.gitignore` block and the THIRD-PARTY.md paragraph. |
| Improvement Mode, New Feature Mode (CLAUDE.md) | retire | 0 hits ever. Referrer: the Stop-hook prompt sentence naming the modes — settings edit, Kyle's word. |
| Kickoff Mode section | relocate / shrink | 2 hits; the skill exists. Propose `ask`: shrink to one pointer line, or leave. |
| `/autonomous-milestone.md.disabled`, `/learn.md.disabled` | ask | D5. Retire → ledger, or stay paused. Either way patch the five dangling routes (`backlog-hygiene`, `reorient`, `replenish`, `/brainstorm`, `/prompt-optimize`). |
| 4 comment-only disabled hook entries (Stop ×2, Notification ×2) | retire | settings edit, Kyle's word. |
| ~30 empty `memory/` dirs | retire | mechanical. |
| `mcp:MCP_DOCKER` (failing to connect) | ask | Kyle's word. |
| kapture / claude-in-chrome / playwright (three browser automators) | ask | usage favors kapture; ask before touching. |
| every other `cold` item | ask | the sweep's real output. |

- [ ] **Step 2: STOP at ratification; Kyle rules**

- [ ] **Step 3: Apply per `references/bookkeeping.md`; measure; ship PR B**

PR B body: the ruled table, before → after Totals, the ledger diff, "Hand to /trim-context",
"Downstream copies (report only)". Propose review scope: **single round** (CLAUDE.md and
skill-referrer edits are behavioral; every removal is one `git rm` plus doc rows). STOP for Kyle.

- [ ] **Step 4: After merge — the wire-level check**

Ask Kyle to open a fresh session and run `/context`; paste the number into
`docs/reports/<date>-steering-inventory.md` under "After (wire-level)". Commit on a
`docs/` branch, or fold into the next PR.

---

### Task 13: Backlog and idea-doc bookkeeping

**Files:**
- Modify: `BACKLOG.md` (three stubs under `## Open`; status line on "Minimal initial prompt")
- Modify: `docs/ideas/coliseum-commands-earn-their-keep.md`, `docs/ideas/minimal-initial-prompt.md`

- [ ] **Step 1: Add three v2 stubs under `## Open` in `BACKLOG.md`** (house format, `Added:` = today)

```markdown
### [Feature] retire: fleet prune lane
- **Why:** `retire` reports vendored copies of a retired item but never edits a project repo; 16 repos (13 public) carry the global kit, and the July 2026 PII purge showed what a copy that outlives its source costs. Needs `fleet-manifest-reconcile`'s per-item manifest and its landmine list (single-line command lists, zsh refspecs, false-clean sweeps).
- **Acceptance:** `/retire` gains a `--fleet` flag that opens one PR per downstream repo removing the retired item, with the refuse-if-unsure excision guard, and reports every repo it could not clean.
- **Size:** L
- **Added:** <today>

### [Feature] retire: per-project CLAUDE.md lane
- **Why:** The global lane audits `~/.claude`; the biggest per-project files (`stopwatch` 38.7k chars, `hush-gauge` 31.2k) are invisible to it, and `/trim-context` relocates without ever retiring.
- **Acceptance:** `/retire` run at a project root inventories that repo's `CLAUDE.md` sections and `.claude/` items with the same evidence fields, scoped to that project's transcripts.
- **Size:** M
- **Added:** <today>

### [Improvement] retire: periodic `--report` cadence
- **Why:** The sweep is only as good as the habit of running it. A quarterly read-only report keeps "what went cold" visible without a Stop-hook tracer.
- **Acceptance:** One `/schedule`d or calendar-reminded `/retire --report` run per quarter, with the report committed to `docs/reports/`.
- **Size:** S
- **Added:** <today>
```

- [ ] **Step 2: Mark the absorbed items**

In `BACKLOG.md`, the `### [Improvement] Minimal initial prompt: salience audit for always-loaded instructions` item gets a first bullet:
```markdown
- **Status:** **Absorbed <today>** — the `retire` skill's CLAUDE.md lane (trigger-phrase evidence per section, `hook_convertible` flag at ratification). Spec: `docs/superpowers/specs/2026-09-17-retire-skill-design.md`.
```
Check `grep -n -i coliseum BACKLOG.md`; if the Coliseum idea has a backlog item, give it the same Status line reading "Built <today> as the `retire` skill".

In `docs/ideas/coliseum-commands-earn-their-keep.md`, change the Status line to:
```markdown
**Status:** Built <today> as [`retire`](../../skills/retire/SKILL.md) — evidence from the transcript corpus directly, no Stop-hook tracer. Spec: [`2026-09-17-retire-skill-design.md`](../superpowers/specs/2026-09-17-retire-skill-design.md).
```
In `docs/ideas/minimal-initial-prompt.md`, change the Status line to:
```markdown
**Status:** Absorbed <today> by [`retire`](../../skills/retire/SKILL.md)'s CLAUDE.md lane. Spec: [`2026-09-17-retire-skill-design.md`](../superpowers/specs/2026-09-17-retire-skill-design.md).
```

- [ ] **Step 3: Commit (this can ride in PR A or PR B — whichever is open)**

```bash
git add BACKLOG.md docs/ideas/coliseum-commands-earn-their-keep.md docs/ideas/minimal-initial-prompt.md
git commit -m "docs(backlog): retire v2 stubs; mark Coliseum built and minimal-initial-prompt absorbed

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01F6oTCwzx8WmJuYuN4Q3nJr"
```

---

## Self-review against the spec

- **§5.1 modes** → Task 10 SKILL.md "Modes". **§5.2 surfaces** → Tasks 2–3 enumerators, Task 10 bookkeeping per surface. **§5.3 evidence fields** → Tasks 4–7 (`Item` fields). **§5.4 temperature + verdicts** → Task 7 `temperature()`, Task 10 Step 2 table. **§5.5 ratification** → Task 10 Step 3. **§5.6 apply checklist** → `references/bookkeeping.md`. **§5.7 ledger** → Task 9. **§5.8 safety** → prime directives + exit codes. **§5.9 measure** → Task 10 Step 5. **§5.10 handoffs** → Task 10 "Handoffs". **§6 conventions** → Task 9 pointer; D5 handled in Task 12's paused-command row. **§7 script contract** → Tasks 1–8. **§8 pilot** → Task 12. **§9 phases** → PR A = Tasks 1–11, PR B = Task 12. **§11 backlog** → Task 13.
- **Placeholders:** `2026-09-XX` / `<today>` / `<sha>` are deliberate run-time values; every code step is complete.
- **Type consistency:** `Config(claude_home, config_repo, projects_root, claude_json, since_days, triggers, cache_path)` is used identically in the fixture, `build_inventory`, and `main`. `Transcripts.cache_hits` is set in Task 5 and read in Task 7's meta. `last_edited(config_repo, it)` takes two args in Task 6 and Task 7. `Item.to_dict()` strips `extra["body"]`, which `enumerate_claude_md` sets and `_item_text` reads.

## Run-config note

Continue in the current Fable 5.1 session after compaction — phases 1–2 are small and the pilot (Task 12) is
ruling-with-Kyle judgment. If starting fresh: `claude --model claude-fable-5-1 --effort xhigh`. Tasks 1–7 are
mechanical enough to dispatch to one Sonnet 5 subagent at `medium` with this plan file as its brief; review its
diff before Task 8.
