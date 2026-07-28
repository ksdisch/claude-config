#!/usr/bin/env python3
"""Verify the reference index and the usage playbook stay 1:1.

`docs/command-skill-reference.md` lists one row per custom command, skill, and
subagent; `docs/usage-playbook.md` holds one card per item. The house rule is that
a row and its card change in the same commit — this script is what makes that
rule *verified* rather than asserted. It is wired as a `git push` hook (see
`CLAUDE.md` → Reference Doc Maintenance) and is also runnable by hand:

    python3 scripts/check-doc-sync.py

Exit 0 = in sync, or this isn't the claude-config repo (nothing to check).
Exit 1 = drift; every problem is printed to stderr with the item names.

Checks, in report order:
  1. Every index row for an item carries a `config →` link to a playbook anchor.
  2. Every one of those anchors resolves to a real playbook heading.
  3. Every playbook card is pointed at by a row (no orphan cards).
  4. No two playbook headings produce the same anchor (GitHub silently suffixes
     the second one, which would re-point an existing link at the wrong card).
"""

from __future__ import annotations

import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

REFERENCE = Path("docs/command-skill-reference.md")
PLAYBOOK = Path("docs/usage-playbook.md")
CONFIG_LINK = re.compile(r"\[config →\]\(usage-playbook\.md#([^)]+)\)")
HEADING = re.compile(r"^#{2,6}\s+(.*?)\s*$", re.M)
BACKTICKED = re.compile(r"`([^`]+)`")


def anchor(text: str) -> str:
    """Slugify a heading the way GitHub does: strip formatting, lowercase, drop
    punctuation other than hyphen/underscore, spaces to hyphens."""
    text = text.replace("`", "").strip().lower()
    text = re.sub(r"[^a-z0-9 _\-]", "", text)
    return text.replace(" ", "-")


def repo_root() -> Path | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return Path(out.stdout.strip())


def item_rows(reference: str) -> list[tuple[int, str, str | None]]:
    """Index rows that describe an item: (line number, item name, linked anchor).

    A row qualifies when it has exactly two cells and the first names an item in
    backticks — which excludes header rows (`| Command | What it does |`), the
    `|---|---|` separators, and any non-item table.
    """
    rows = []
    for lineno, line in enumerate(reference.split("\n"), start=1):
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 2:
            continue
        name = BACKTICKED.search(cells[0])
        if not name:
            continue
        link = CONFIG_LINK.search(cells[1])
        rows.append((lineno, name.group(1), link.group(1) if link else None))
    return rows


def cards(playbook: str) -> list[tuple[str, str]]:
    """Card headings as (item name, anchor). A card is a heading whose text is a
    backticked item name; section headings are plain prose and are skipped."""
    found = []
    for match in HEADING.finditer(playbook):
        text = match.group(1)
        if text.startswith("`"):
            found.append((text.strip("`"), anchor(text)))
    return found


def main() -> int:
    root = repo_root()
    if root is None:
        return 0
    reference_path, playbook_path = root / REFERENCE, root / PLAYBOOK
    if not (reference_path.is_file() and playbook_path.is_file()):
        # Not the claude-config repo — nothing this script governs.
        return 0

    reference = reference_path.read_text()
    playbook = playbook_path.read_text()

    rows = item_rows(reference)
    all_anchors = [anchor(h) for h in HEADING.findall(playbook)]
    card_list = cards(playbook)
    card_anchors = {a for _, a in card_list}
    linked_anchors = {a for _, _, a in rows if a}

    problems: list[str] = []

    unlinked = [(n, ln) for ln, n, a in rows if a is None]
    if unlinked:
        problems.append(
            "index rows with no `config →` link to a playbook card:\n"
            + "\n".join(f"    {REFERENCE}:{ln}  {n}" for n, ln in unlinked)
        )

    dangling = [(n, ln, a) for ln, n, a in rows if a and a not in set(all_anchors)]
    if dangling:
        problems.append(
            "index rows linking to a playbook anchor that does not exist:\n"
            + "\n".join(f"    {REFERENCE}:{ln}  {n} → #{a}" for n, ln, a in dangling)
        )

    orphans = sorted(a for a in card_anchors if a not in linked_anchors)
    if orphans:
        problems.append(
            "playbook cards no index row points at:\n"
            + "\n".join(f"    {PLAYBOOK}  #{a}" for a in orphans)
        )

    dupes = sorted(a for a, count in Counter(all_anchors).items() if count > 1)
    if dupes:
        problems.append(
            "playbook headings that collide into one anchor (GitHub suffixes the\n"
            "  second, silently re-pointing an existing link at the wrong card):\n"
            + "\n".join(f"    {PLAYBOOK}  #{a}" for a in dupes)
        )

    if not problems:
        return 0

    print(
        f"doc sync check FAILED — {REFERENCE} and {PLAYBOOK} are not 1:1.\n"
        f"({len(rows)} item rows, {len(card_list)} cards)\n",
        file=sys.stderr,
    )
    for problem in problems:
        print(f"  {problem}\n", file=sys.stderr)
    print(
        "A row and its card change in the same commit — see CLAUDE.md →\n"
        "Reference Doc Maintenance. Fix the docs; do not bypass the check.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
