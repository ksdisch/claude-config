#!/usr/bin/env python3
"""Verify the reference index and the usage playbook stay 1:1.

`docs/command-skill-reference.md` lists one row per custom command, skill, and
subagent; `docs/usage-playbook.md` holds one card per item. The house rule is that
a row and its card change in the same commit — this script is what makes that rule
*verified* rather than asserted. It runs as this repo's `pre-push` git hook (see
`CLAUDE.md` → Reference Doc Maintenance) and by hand from anywhere:

    python3 scripts/check-doc-sync.py

Scope: it compares the two docs **to each other**. It does not check that every
item file has a row — see the follow-ups on PR #57.

Exit 0 = in sync (prints a one-line summary, so a silent run is never mistaken
for a pass). Exit 1 = drift, with every problem named on stderr.

Checks, in report order:
  1. Every index row for an item carries a `config →` link.
  2. Every link resolves to a real card — not to a section heading, and not to
     nothing.
  3. The card a row links **is that row's item**. Existence isn't enough: a
     copy-pasted anchor or a rename propagated to only one doc leaves a row
     pointing at some *other* item's card.
  4. No two rows claim the same card.
  5. No card is an orphan.
  6. No two headings collide into one anchor — GitHub silently suffixes the
     second, which re-points an existing link at the wrong card.

A card heading may carry a project suffix to disambiguate a duplicate item name
(`### \\`/verify\\` (DogHood)` → `#verify-doghood`); the item name inside the
backticks is what must match the row.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
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


def cards(playbook: str) -> dict[str, str]:
    """Card anchor → the item name in its heading. A card is a heading whose text
    starts with a backticked item name; section headings are plain prose."""
    found = {}
    for match in HEADING.finditer(playbook):
        text = match.group(1)
        if not text.startswith("`"):
            continue
        name = BACKTICKED.search(text)
        if name:
            found[anchor(text)] = name.group(1)
    return found


def main() -> int:
    reference_path, playbook_path = REPO / REFERENCE, REPO / PLAYBOOK
    if not (reference_path.is_file() and playbook_path.is_file()):
        print(
            f"doc sync check could not run: expected {REFERENCE} and {PLAYBOOK} "
            f"under {REPO}.",
            file=sys.stderr,
        )
        return 1

    reference = reference_path.read_text()
    playbook = playbook_path.read_text()

    rows = item_rows(reference)
    card_map = cards(playbook)
    all_anchors = [anchor(h) for h in HEADING.findall(playbook)]

    problems: list[str] = []

    unlinked = [(n, ln) for ln, n, a in rows if a is None]
    if unlinked:
        problems.append(
            "index rows with no `config →` link to a playbook card:\n"
            + "\n".join(f"    {REFERENCE}:{ln}  {n}" for n, ln in unlinked)
        )

    dangling = [(n, ln, a) for ln, n, a in rows if a and a not in card_map]
    if dangling:
        problems.append(
            "index rows linking to something that is not a card:\n"
            + "\n".join(f"    {REFERENCE}:{ln}  {n} → #{a}" for n, ln, a in dangling)
        )

    mismatched = [
        (n, ln, a, card_map[a])
        for ln, n, a in rows
        if a and a in card_map and card_map[a] != n
    ]
    if mismatched:
        problems.append(
            "index rows pointing at another item's card (copy-pasted anchor, or a\n"
            "  rename propagated to only one doc):\n"
            + "\n".join(
                f"    {REFERENCE}:{ln}  row {n!r} → #{a}, which is the card for {card!r}"
                for n, ln, a, card in mismatched
            )
        )

    claims = Counter(a for _, _, a in rows if a)
    shared = sorted(a for a, count in claims.items() if count > 1)
    if shared:
        problems.append(
            "one card claimed by several index rows:\n"
            + "\n".join(f"    {PLAYBOOK}  #{a} ({claims[a]} rows)" for a in shared)
        )

    orphans = sorted(a for a in card_map if a not in claims)
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
        print(f"doc sync check: in sync — {len(rows)} index rows, {len(card_map)} cards.")
        return 0

    print(
        f"doc sync check FAILED — {REFERENCE} and {PLAYBOOK} are not 1:1.\n"
        f"({len(rows)} index rows, {len(card_map)} cards)\n",
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
