#!/usr/bin/env python3
"""Verify the reference index and the usage playbook stay 1:1.

`docs/command-skill-reference.md` lists one row per custom command, skill, and
subagent; `docs/usage-playbook.md` holds one card per item. The house rule is that
a row and its card change in the same commit — this script is what makes that rule
*verified* rather than asserted. It runs as this repo's `pre-push` git hook (see
`CLAUDE.md` → Reference Doc Maintenance) and by hand from anywhere:

    python3 scripts/check-doc-sync.py

Scope: it compares the two docs to each other **and** the index to this repo's own
item files. What it still can't check is project-specific items, which live in
other repos' `.claude/` folders and have no file here — their rows are unlinked,
so nothing verifies they exist. It also can't tell you what a card should *say*.

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
  7. Every tracked command, skill, and subagent file has an index row, no row
     links to an item file that no longer exists, and each row's name matches
     the file it links.

A card heading may carry a project suffix to disambiguate a duplicate item name
(`### \\`/verify\\` (DogHood)` → `#verify-doghood`); the item name inside the
backticks is what must match the row.

Table rows that name no item are reported as warnings rather than dropped, so a
malformed row can't quietly exempt itself from every check above.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REFERENCE = Path("docs/command-skill-reference.md")
PLAYBOOK = Path("docs/usage-playbook.md")
CONFIG_LINK = re.compile(r"\[config →\]\(usage-playbook\.md#([^)]+)\)")
HEADING = re.compile(r"^#{2,6}\s+(.*?)\s*$", re.M)
BACKTICKED = re.compile(r"`([^`]+)`")
# A global row opens with a link to the item's own file; project-specific rows
# name the item in bare backticks, since their files live in another repo.
ITEM_LINK = re.compile(r"^\|\s*\[`([^`]+)`\]\(\.\./([^)]+)\)")
# Markdown escapes a literal pipe inside a cell as `\|`; a plain split("|")
# would read that as a cell boundary and mis-shape the row.
CELL_SPLIT = re.compile(r"(?<!\\)\|")
ITEM_DIRS = ("commands", "skills", "agents")


def anchor(text: str) -> str:
    """Slugify a heading the way GitHub does: strip formatting, lowercase, drop
    punctuation other than hyphen/underscore, spaces to hyphens."""
    text = text.replace("`", "").strip().lower()
    text = re.sub(r"[^a-z0-9 _\-]", "", text)
    return text.replace(" ", "-")


def item_rows(reference: str) -> tuple[list[tuple[int, str, str | None]], list[tuple[int, str]]]:
    """Split the index's table rows into items and leftovers.

    Returns `(rows, unrecognized)`, where a row is an item when it has exactly
    two cells and the first names an item in backticks. Everything else that is
    still table-shaped comes back as `unrecognized` so the caller can warn about
    it: a row the parser drops is a row exempt from every check, and that
    exemption is invisible in both docs unless it's reported.

    Genuine header rows (`| Command | What it does |`) are recognized by the
    `|---|---|` separator directly beneath them, not by their content — so they
    are excluded without also excusing a malformed item row that happens to lack
    backticks.
    """
    rows: list[tuple[int, str, str | None]] = []
    unrecognized: list[tuple[int, str]] = []
    lines = reference.split("\n")

    for lineno, line in enumerate(lines, start=1):
        text = line.strip()
        if not text.startswith("|") or text.startswith("|---"):
            continue
        below = lines[lineno].strip() if lineno < len(lines) else ""
        if below.startswith("|---"):
            continue

        cells = [c.strip() for c in CELL_SPLIT.split(text.strip("|"))]
        name = BACKTICKED.search(cells[0]) if cells else None
        if len(cells) != 2 or not name:
            unrecognized.append((lineno, text))
            continue

        link = CONFIG_LINK.search(cells[1])
        rows.append((lineno, name.group(1), link.group(1) if link else None))

    return rows, unrecognized


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


def item_file_name(path: str) -> str | None:
    """The index row name a repo item file must appear under — or None when the
    path is part of an item rather than the item itself (a skill's
    `references/`, a command's helper script)."""
    parts = path.split("/")
    if len(parts) == 2 and parts[0] == "commands" and parts[1].endswith(".md"):
        return "/" + parts[1][: -len(".md")]
    if len(parts) == 2 and parts[0] == "agents" and parts[1].endswith(".md"):
        return parts[1][: -len(".md")]
    if len(parts) == 3 and parts[0] == "skills" and parts[2] == "SKILL.md":
        return parts[1]
    return None


def git(args: list[str]) -> str | None:
    """Run a git command in this repo; None if git or the object is unavailable."""
    try:
        result = subprocess.run(
            ["git", "-C", str(REPO), *args],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout


def read_doc(path: Path, rev: str | None) -> str | None:
    """One of the two docs, from the working tree or from a revision."""
    if rev is None:
        full = REPO / path
        return full.read_text() if full.is_file() else None
    return git(["show", f"{rev}:{path.as_posix()}"])


def tracked_items(rev: str | None) -> dict[str, str] | None:
    """Every item file → the row name it must appear under.

    Sourced from git, so a skill kept out of this public repo on purpose
    (`skills/interview-prep/` is gitignored) is excluded because git doesn't
    list it — not because of an exemption list that would silently drift.
    Returns None when git can't answer, which the caller reports rather than
    treating as "nothing to check".
    """
    if rev is None:
        out = git(["ls-files", "-z", *ITEM_DIRS])
    else:
        out = git(["ls-tree", "-r", "--name-only", "-z", rev, "--", *ITEM_DIRS])
    if out is None:
        return None

    found = {}
    for path in out.split("\0"):
        name = item_file_name(path) if path else None
        if name:
            found[path] = name
    return found


def linked_items(reference: str) -> dict[str, tuple[int, str]]:
    """Item-file path → (line number, row name) for every row that links a file
    in this repo. Project-specific rows name their item in bare backticks with no
    link, so they never appear here — their files live in another repo."""
    found = {}
    for lineno, line in enumerate(reference.split("\n"), start=1):
        match = ITEM_LINK.match(line.strip())
        if match and match.group(2).split("/")[0] in ITEM_DIRS:
            found[match.group(2)] = (lineno, match.group(1))
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument(
        "--rev",
        metavar="SHA",
        help="check the docs as they exist in this revision instead of in the "
        "working tree — what the pre-push hook uses, so enforcement is a "
        "property of the commits being pushed rather than of whatever happens "
        "to be checked out.",
    )
    args = parser.parse_args(argv)
    rev = args.rev
    # Abbreviate a full sha for readability; leave a branch or tag name intact.
    short = rev[:12] if rev and re.fullmatch(r"[0-9a-fA-F]{40,}", rev) else rev
    where = f" at {short}" if rev else ""

    reference = read_doc(REFERENCE, rev)
    playbook = read_doc(PLAYBOOK, rev)

    if reference is None or playbook is None:
        # In a checkout, a missing doc means a broken working copy — an error.
        if rev is None:
            print(
                f"doc sync check could not run: expected {REFERENCE} and {PLAYBOOK} "
                f"under {REPO}.",
                file=sys.stderr,
            )
            return 1

        # At a revision it usually means the commit simply predates the docs —
        # true of every branch cut before they landed, and not something to block
        # a push over. Say which doc was absent, so a deliberate deletion is
        # visible rather than mistaken for a clean pass.
        absent = ", ".join(
            str(p) for p, text in ((REFERENCE, reference), (PLAYBOOK, playbook))
            if text is None
        )
        print(
            f"doc sync check: not verified{where} — {absent} does not exist there, "
            f"so there is no pairing to check.",
            file=sys.stderr,
        )
        return 0

    rows, unrecognized = item_rows(reference)
    card_map = cards(playbook)
    all_anchors = [anchor(h) for h in HEADING.findall(playbook)]

    problems: list[str] = []
    warnings: list[str] = []

    if unrecognized:
        warnings.append(
            "table rows that name no item, so none of the checks below apply to\n"
            "  them (a description with an unescaped `|`, or a name without backticks):\n"
            + "\n".join(
                f"    {REFERENCE}:{ln}  {text[:88]}" for ln, text in unrecognized
            )
        )

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

    tracked = tracked_items(rev)
    if tracked is None:
        warnings.append(
            "could not list this repo's item files (git unavailable), so the two docs\n"
            "  were checked against each other only — nothing verified that every\n"
            "  command, skill, and subagent file has an index row."
        )
    else:
        linked = linked_items(reference)

        missing = sorted(p for p in tracked if p not in linked)
        if missing:
            problems.append(
                "item files with no index row (add the row AND its playbook card):\n"
                + "\n".join(
                    f"    {p}  → expected a row named {tracked[p]!r}" for p in missing
                )
            )

        stale = sorted(p for p in linked if p not in tracked)
        if stale:
            problems.append(
                "index rows linking to something that is not a tracked item file\n"
                "  (deleted, renamed, or never committed):\n"
                + "\n".join(
                    f"    {REFERENCE}:{linked[p][0]}  {linked[p][1]} → {p}" for p in stale
                )
            )

        misnamed = sorted(p for p in linked if p in tracked and linked[p][1] != tracked[p])
        if misnamed:
            problems.append(
                "index rows whose name disagrees with the file they link (a rename\n"
                "  that reached one of the two):\n"
                + "\n".join(
                    f"    {REFERENCE}:{linked[p][0]}  row {linked[p][1]!r} links {p}, "
                    f"which is {tracked[p]!r}"
                    for p in misnamed
                )
            )

    for warning in warnings:
        print(f"doc sync check: warning — {warning}\n", file=sys.stderr)

    if not problems:
        counted = "" if tracked is None else f", {len(tracked)} item files"
        print(
            f"doc sync check: in sync{where} — {len(rows)} index rows, "
            f"{len(card_map)} cards{counted}."
        )
        return 0

    counted = "" if tracked is None else f", {len(tracked)} item files"
    print(
        f"doc sync check FAILED{where} — {REFERENCE} and {PLAYBOOK} are out of sync.\n"
        f"({len(rows)} index rows, {len(card_map)} cards{counted})\n",
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
