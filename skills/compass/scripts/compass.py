#!/usr/bin/env python3
"""Helper for the compass skill: reads topic files, never writes them.

Subcommands (JSON on stdout; exit 0 on success, 1 when `check` finds violations, 2 on a usage
or read error, including a file that is not UTF-8):

  check <file>   Validate one topic file against references/file-format.md and report every
                 violation as {"valid": bool, "violations": [{"rule", "line", "message"}]}.
  list           One record per topic in the compass folder: {"topics": [{"slug", "topic",
                 "why" (shortened), "counts": {status: n}, "status", "last_touched"}],
                 "skipped": [{"file", "error"}]}, open topics first, then closed, each
                 newest-touched first.
  match <query>  Resolve a query against slugs and display names, case-insensitively, each query
                 word matching a whole word or the start of one:
                 {"result": "single" | "several" | "none", "matches": [{"slug", "topic",
                 "status"}], "skipped": [{"file", "error"}]}.
  recall <file> [n]
                 Up to n (default 3) answered questions for the resume warm-up, never recalled
                 first, then oldest last-recalled date, ties by tree number:
                 {"questions": [{"number", "text", "last_recalled"}]}; empty when none is
                 answered.
  render <file>  Check the file, then draw it as one self-contained <slug>.html beside it: the
                 Overview's ideas as a concept map (edges from its `Links:` list) and the
                 question tree coloured by status. Writes only that HTML, never the topic file:
                 {"written": path}; a file check rejects prints the check report, exits 1 and
                 writes nothing.

`list` and `match` read `--dir` (default ~/Learning/compass); a missing folder holds no topics,
and a file that cannot be read lands in `skipped` instead of failing the whole folder.

The file format is the contract; references/file-format.md is its prose definition and this
parser is its executable one. Keep the two in step.
"""
import argparse
import datetime
import json
import math
import re
from html import escape
import sys
from pathlib import Path

EXIT_OK, EXIT_INVALID, EXIT_ERROR = 0, 1, 2

DEFAULT_DIR = "~/Learning/compass"
WHY_LIMIT = 60
RECALL_DEFAULT = 3

FRONTMATTER_REQUIRED = ("topic", "why", "status", "created", "updated")
FRONTMATTER_OPTIONAL = ("workspace", "map")
TOPIC_STATUSES = ("open", "closed")
QUESTION_STATUSES = ("open", "answered", "parked", "prereq")
ANSWERED_BY = ("claude", "kyle")
QUESTION_FIELDS = ("status", "answered by", "last recalled", "park reason")
QUESTION_SUBSECTIONS = ("Answer", "Sources")
SECTION_ORDER = ("Overview", "Questions", "Close-out", "Session log")
REQUIRED_SECTIONS = ("Questions", "Session log")

DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
H2 = re.compile(r"^##\s+(.*?)\s*$")
H3 = re.compile(r"^###\s+(.*?)\s*$")
H4 = re.compile(r"^####\s+(.*?)\s*$")
QUESTION_HEADING = re.compile(r"^Q([0-9.]+)\s*:\s*(.*)$")
TREE_NUMBER = re.compile(r"^[1-9][0-9]*(\.[1-9][0-9]*)*$")
FIELD = re.compile(r"^-\s+([A-Za-z][A-Za-z ]*?)\s*:\s*(.*?)\s*$")
LOG_ENTRY = re.compile(r"^-\s+(\d{4}-\d{2}-\d{2})\b")
IDEA = re.compile(r"^\d+\.\s+\*\*\s*(\S.*?)\s*\*\*\s*[—–:-]?\s*(.*?)\s*$")
# An Overview sub-heading, bolded or not: `Links:` and `**Links:**` both start the list.
OVERVIEW_HEAD = re.compile(r"^\**(Links|Sources|How they connect):\**\s*(.*?)\s*$")
LINK = re.compile(r"^-\s+(\S.*?)\s+→\s+(\S.*?):\s+(\S.*?)\s*$")
BULLET = re.compile(r"^\s*[-*]\s+(\S.*?)\s*$")
URL = re.compile(r"https?://[^\s<>\"']+")


def is_date(text: str) -> bool:
    """YYYY-MM-DD and a real calendar date."""
    if not DATE.match(text):
        return False
    try:
        datetime.date.fromisoformat(text)
    except ValueError:
        return False
    return True


class Report:
    def __init__(self):
        self.violations = []

    def add(self, rule: str, line, message: str):
        self.violations.append({"rule": rule, "line": line, "message": message})


def strip_fences(lines):
    """Yield (lineno, text, in_fence) so headings inside code blocks are never structure."""
    opener = None
    for i, text in enumerate(lines, start=1):
        m = FENCE.match(text)
        if m and opener is None:
            opener = m.group(1)
            yield i, text, True
            continue
        if (m and opener and m.group(1)[0] == opener[0] and len(m.group(1)) >= len(opener)
                and not m.group(2).strip()):
            opener = None
            yield i, text, True
            continue
        yield i, text, opener is not None


def parse_frontmatter(lines, report):
    """Return (fields, field_lines, body_start_index)."""
    if not lines or lines[0].strip() != "---":
        report.add("frontmatter-missing", 1, "file must open with a '---' frontmatter block")
        return {}, {}, 0
    fields, where = {}, {}
    for idx in range(1, len(lines)):
        text = lines[idx]
        if text.strip() == "---":
            return fields, where, idx + 1
        if not text.strip():
            continue
        key, sep, value = text.partition(":")
        key = key.strip()
        if not sep:
            report.add("frontmatter-syntax", idx + 1, f"frontmatter line is not 'key: value': {text!r}")
            continue
        if key in fields:
            report.add("frontmatter-field", idx + 1, f"frontmatter key '{key}' appears twice")
        elif key not in FRONTMATTER_REQUIRED + FRONTMATTER_OPTIONAL:
            report.add("frontmatter-field", idx + 1, f"unknown frontmatter key '{key}' (known: "
                       f"{', '.join(FRONTMATTER_REQUIRED + FRONTMATTER_OPTIONAL)})")
        fields[key] = value.strip()
        where[key] = idx + 1
    report.add("frontmatter-missing", 1, "frontmatter block is never closed with '---'")
    return fields, where, len(lines)


def parse_body(lines, start):
    """Split the body into ## sections: [{name, line, lines: [(lineno, text, in_fence)]}]."""
    sections, current = [], None
    for lineno, text, in_fence in strip_fences(lines):
        if lineno <= start:
            continue
        m = None if in_fence else H2.match(text)
        if m:
            current = {"name": m.group(1), "line": lineno, "lines": []}
            sections.append(current)
        elif current is not None:
            current["lines"].append((lineno, text, in_fence))
    return sections


def parse_questions(section_lines, report):
    """Parse the Questions section into a list of question dicts."""
    questions, q, sub = [], None, None
    for lineno, text, in_fence in section_lines:
        h3 = None if in_fence else H3.match(text)
        if h3:
            sub = None
            m = QUESTION_HEADING.match(h3.group(1))
            if not m:
                report.add("question-heading", lineno,
                           f"question heading must read '### Q<number>: <text>': {text!r}")
                q = None
                continue
            q = {"number": m.group(1), "text": m.group(2).strip(), "line": lineno,
                 "fields": {}, "field_lines": {}, "subsections": {}}
            questions.append(q)
            continue
        if q is None:
            if text.strip():
                report.add("question-field", lineno,
                           f"stray line outside any '### Q<number>: <text>' question: {text!r}")
            continue
        h4 = None if in_fence else H4.match(text)
        if h4:
            sub = h4.group(1)
            if sub in q["subsections"]:
                report.add("question-subsection", lineno,
                           f"Q{q['number']}: subsection '#### {sub}' appears twice")
                q["subsections"][sub]["lines"].extend(["", text])
                continue
            q["subsections"][sub] = {"line": lineno, "lines": []}
            continue
        if sub is not None:
            q["subsections"][sub]["lines"].append(text)
            continue
        f = FIELD.match(text)
        if f:
            key = f.group(1).lower()
            if key in q["fields"]:
                report.add("question-field", lineno, f"Q{q['number']}: field '{key}' appears twice")
            q["fields"][key] = f.group(2)
            q["field_lines"][key] = lineno
        elif text.strip():
            report.add("question-field", lineno,
                       f"Q{q['number']}: expected a '- key: value' field line, got {text!r}")
    return questions


def check_question(q, report):
    label, fields = f"Q{q['number']}", q["fields"]
    if not q["text"]:
        report.add("question-heading", q["line"], f"{label}: question text is empty")
    if "last recalled" not in fields:
        report.add("question-field", q["line"], f"{label}: missing '- last recalled:' field")
    for key in fields:
        if key not in QUESTION_FIELDS:
            report.add("question-field", q["field_lines"][key],
                       f"{label}: unknown field '{key}' (known: {', '.join(QUESTION_FIELDS)})")
    for name, sub in q["subsections"].items():
        if name not in QUESTION_SUBSECTIONS:
            report.add("question-subsection", sub["line"],
                       f"{label}: unknown subsection '#### {name}' "
                       f"(known: {', '.join(QUESTION_SUBSECTIONS)})")
    status = fields.get("status")
    if not status:
        report.add("question-status", q["line"], f"{label}: missing '- status:' field")
    elif status not in QUESTION_STATUSES:
        report.add("question-status", q["field_lines"]["status"],
                   f"{label}: status {status!r} is not one of {', '.join(QUESTION_STATUSES)}")
    recalled = fields.get("last recalled")
    if recalled and not is_date(recalled):
        report.add("last-recalled-date", q["field_lines"]["last recalled"],
                   f"{label}: 'last recalled' must be empty or YYYY-MM-DD, got {recalled!r}")
    if status == "answered":
        if fields.get("answered by") not in ANSWERED_BY:
            report.add("answered-by", q["field_lines"].get("answered by", q["line"]),
                       f"{label}: answered questions need '- answered by:' set to "
                       f"{' or '.join(ANSWERED_BY)}")
        answer = q["subsections"].get("Answer")
        if not answer or not any(l.strip() for l in answer["lines"]):
            report.add("answered-needs-answer", q["line"],
                       f"{label}: answered questions need a non-empty '#### Answer'")
        sources = q["subsections"].get("Sources")
        items = [l for l in (sources["lines"] if sources else [])
                 if re.match(r"^\s*[-*]\s+\S", l)]
        if not items:
            report.add("answered-needs-sources", q["line"],
                       f"{label}: answered questions need a '#### Sources' list with at least one item")
    if status != "answered":
        if "answered by" in fields:
            report.add("question-field", q["field_lines"]["answered by"],
                       f"{label}: '- answered by:' is only for answered questions")
        for name, sub in q["subsections"].items():
            if name in QUESTION_SUBSECTIONS:
                report.add("question-subsection", sub["line"],
                           f"{label}: '#### {name}' is only for answered questions")
    if status != "parked" and "park reason" in fields:
        report.add("question-field", q["field_lines"]["park reason"],
                   f"{label}: '- park reason:' is only for parked questions")
    if status == "parked" and not fields.get("park reason"):
        report.add("parked-needs-reason", q["line"],
                   f"{label}: parked questions need a non-empty '- park reason:'")


def parse_overview(section_lines, report):
    """Parse the Overview into {ideas: [{term, text}], connect, links: [{source, target,
    label, line}], sources}. The prose stays free text; only the `Links:` list is checked:
    one `- <term> → <term>: <label>` bullet per line, both ends bolded idea terms, no self-link."""
    ideas, connect, links, sources, mode = [], [], [], [], None
    for lineno, text, in_fence in section_lines:
        line = text.strip()
        if in_fence:
            continue
        head = OVERVIEW_HEAD.match(line)
        if head:
            mode = {"Links": "links", "Sources": "sources"}.get(head.group(1), "connect")
            if mode == "connect":
                connect.append(head.group(2))
            continue
        if mode == "links":
            if not line:
                continue
            m = LINK.match(line)
            if m:
                links.append({"source": m.group(1), "target": m.group(2),
                              "label": m.group(3), "line": lineno})
            else:
                report.add("overview-link", lineno,
                           f"a Links line must read '- <term> → <term>: <label>': {text!r}")
            continue
        if mode == "sources":
            b = BULLET.match(text)
            if b:
                sources.append(b.group(1))
            continue
        if mode == "connect" and line:
            connect.append(line)
            continue
        if mode == "connect":
            mode = None
        m = IDEA.match(line)
        if m:
            ideas.append({"term": m.group(1), "text": m.group(2), "line": lineno})
    terms = {}
    for idea in ideas:
        key = idea["term"].casefold()
        if key in terms:
            report.add("overview-idea", idea["line"],
                       f"key idea '{idea['term']}' repeats '{terms[key]}'; each term names one idea")
        else:
            terms[key] = idea["term"]
    for link in links:
        for end in ("source", "target"):
            name = link[end]
            if name.casefold() not in terms:
                report.add("overview-link", link["line"],
                           f"link end '{name}' is not a bolded key idea "
                           f"(known: {', '.join(terms.values()) or 'none'})")
            else:
                link[end] = terms[name.casefold()]
        if link["source"].casefold() == link["target"].casefold():
            report.add("overview-link", link["line"],
                       f"'{link['source']}' links to itself")
    return {"ideas": ideas, "connect": " ".join(c for c in connect if c), "links": links,
            "sources": sources}


def check_frontmatter(fields, field_lines, report):
    for key in FRONTMATTER_REQUIRED:
        if not fields.get(key):
            report.add("frontmatter-field", field_lines.get(key, 1),
                       f"frontmatter field '{key}' is missing or empty")
    status = fields.get("status")
    if status and status not in TOPIC_STATUSES:
        report.add("topic-status", field_lines["status"],
                   f"topic status {status!r} is not one of {', '.join(TOPIC_STATUSES)}")
    for key in ("created", "updated"):
        value = fields.get(key)
        if value and not is_date(value):
            report.add("frontmatter-date", field_lines[key],
                       f"frontmatter '{key}' must be YYYY-MM-DD, got {value!r}")


def check_tree(questions, report):
    seen = {}
    for q in questions:
        number = q["number"]
        if not TREE_NUMBER.match(number):
            report.add("tree-number", q["line"],
                       f"Q{number}: tree numbers are dot-separated positive integers "
                       "without leading zeros (Q1, Q1.2, Q3.1.4)")
            continue
        if number in seen:
            report.add("tree-duplicate", q["line"],
                       f"Q{number}: number already used at line {seen[number]}")
            continue
        seen[number] = q["line"]
    for number, line in seen.items():
        parent = number.rpartition(".")[0]
        if parent and parent not in seen:
            report.add("tree-orphan", line, f"Q{number}: parent Q{parent} does not exist")


def has_text(section) -> bool:
    return any(text.strip() for _, text, _ in section["lines"])


def check_sections(sections, topic_status, report):
    """Section names, order, presence, and the Close-out / status pairing."""
    by_name, last_rank = {}, -1
    for s in sections:
        name = s["name"]
        if name not in SECTION_ORDER:
            report.add("section-unknown", s["line"],
                       f"unknown section '## {name}' (known, in order: {', '.join(SECTION_ORDER)})")
            continue
        if name in by_name:
            report.add("section-duplicate", s["line"], f"section '## {name}' appears twice")
            continue
        by_name[name] = s
        rank = SECTION_ORDER.index(name)
        if rank < last_rank:
            report.add("section-order", s["line"],
                       f"section '## {name}' is out of order (order: {', '.join(SECTION_ORDER)})")
        last_rank = max(last_rank, rank)
    for name in REQUIRED_SECTIONS:
        if name not in by_name:
            report.add("section-missing", None, f"required section '## {name}' is missing")
    close_out = by_name.get("Close-out")
    if topic_status == "closed" and (close_out is None or not has_text(close_out)):
        report.add("closed-needs-close-out", close_out["line"] if close_out else None,
                   "a closed topic needs a non-empty '## Close-out'")
    if topic_status == "open" and close_out is not None:
        report.add("close-out-on-open", close_out["line"],
                   "an open topic must not have a '## Close-out' (close the topic or remove it)")
    log = by_name.get("Session log")
    if log is not None:
        for lineno, text, _ in log["lines"]:
            continuation = text[:1] in (" ", "\t")
            entry = LOG_ENTRY.match(text)
            if text.strip() and not continuation and not (entry and is_date(entry.group(1))):
                report.add("session-log-entry", lineno,
                           f"session log lines must read '- YYYY-MM-DD — <what moved>': {text!r}")
    return by_name


def check_text(text: str) -> Report:
    report = Report()
    lines = text.splitlines()
    fields, field_lines, body_start = parse_frontmatter(lines, report)
    if body_start:
        check_frontmatter(fields, field_lines, report)
    sections = parse_body(lines, body_start)
    by_name = check_sections(sections, fields.get("status"), report)
    if "Overview" in by_name:
        parse_overview(by_name["Overview"]["lines"], report)
    if "Questions" in by_name:
        questions = parse_questions(by_name["Questions"]["lines"], report)
        check_tree(questions, report)
        for q in questions:
            check_question(q, report)
    return report


class ReadError(Exception):
    """A topic file that cannot be read as UTF-8 text; str() is the message to print."""


def read_text(path: Path) -> str:
    """The one place a topic file is read, so every subcommand fails the same way."""
    try:
        return path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise ReadError(f"cannot read {path}: {exc.strerror}") from exc
    except UnicodeDecodeError as exc:
        raise ReadError(f"cannot read {path}: not UTF-8 text "
                        f"(byte {exc.start}: {exc.reason})") from exc


def cmd_check(args) -> int:
    path = Path(args.file).expanduser()
    try:
        text = read_text(path)
    except ReadError as exc:
        print(json.dumps({"error": str(exc)}))
        return EXIT_ERROR
    report = check_text(text)
    valid = not report.violations
    print(json.dumps({"valid": valid, "violations": report.violations}, indent=2))
    return EXIT_OK if valid else EXIT_INVALID


def parse_lenient(path: Path):
    """Read and parse a topic file without judging it: (frontmatter fields, questions).
    list, match and recall must work on a file check rejects, so violations are discarded.
    Raises ReadError when the file cannot be read."""
    lines = read_text(path).splitlines()
    scratch = Report()
    fields, _, body_start = parse_frontmatter(lines, scratch)
    questions = [q for section in parse_body(lines, body_start) if section["name"] == "Questions"
                 for q in parse_questions(section["lines"], scratch)]
    return fields, questions


def read_topic(path: Path) -> dict:
    """Summarize one topic file for list and match."""
    fields, questions = parse_lenient(path)
    counts = dict.fromkeys(QUESTION_STATUSES, 0)
    for q in questions:
        status = q["fields"].get("status")
        if status in counts:
            counts[status] += 1
    return {"slug": path.stem, "topic": fields.get("topic") or path.stem,
            "why": shorten(fields.get("why", "")), "counts": counts,
            "status": fields.get("status", ""), "last_touched": fields.get("updated", "")}


def shorten(text: str, limit: int = WHY_LIMIT) -> str:
    """Cut at the last word boundary within the limit and mark the cut with an ellipsis."""
    if len(text) <= limit:
        return text
    cut = text[:limit + 1].rpartition(" ")[0] or text[:limit]
    return cut.rstrip(" ,;:.-—") + "…"


def read_topics(folder):
    """(topics, skipped): one unreadable file is reported in skipped, never fatal to the rest."""
    root = Path(folder).expanduser()
    if not root.is_dir():
        return [], []
    topics, skipped = [], []
    for p in sorted(root.glob("*.md")):
        if p.name.startswith(".") or not p.is_file():
            continue
        try:
            topics.append(read_topic(p))
        except ReadError as exc:
            skipped.append({"file": p.name, "error": str(exc)})
    topics.sort(key=lambda t: t["slug"])
    topics.sort(key=lambda t: t["last_touched"], reverse=True)
    topics.sort(key=lambda t: t["status"] == "closed")
    return topics, skipped


def cmd_list(args) -> int:
    try:
        topics, skipped = read_topics(args.dir)
    except OSError as exc:
        print(json.dumps({"error": f"cannot read {exc.filename}: {exc.strerror}"}))
        return EXIT_ERROR
    print(json.dumps({"topics": topics, "skipped": skipped}, indent=2, ensure_ascii=False))
    return EXIT_OK


WORD_SYMBOLS = "#+"


def words(text: str) -> list:
    """Runs of Unicode letters and digits, casefolded. '#' and '+' stay part of a word so
    'C#' and 'C++' remain distinct from each other and from 'C'."""
    out, cur = [], ""
    for ch in text.casefold():
        if ch.isalnum() or (ch in WORD_SYMBOLS and cur):
            cur += ch
        else:
            if cur:
                out.append(cur)
            cur = ""
    if cur:
        out.append(cur)
    return out


def match_topics(query: str, topics: list) -> dict:
    """An exact slug or display name wins outright; otherwise every query word must be a
    whole word, or the start of one, in the slug or the display name ("lifetime" finds
    "Rust lifetimes"; "in" does not find "networking")."""
    wanted = words(query)
    slug_form, name_form = "-".join(wanted), query.strip().casefold()
    exact = [t for t in topics if t["slug"] == slug_form or t["topic"].casefold() == name_form]

    def hit(t):
        have = words(f"{t['slug']} {t['topic']}")
        return all(any(h.startswith(w) for h in have) for w in wanted)

    hits = exact if len(exact) == 1 else [t for t in topics if hit(t)]
    result = "none" if not hits else "single" if len(hits) == 1 else "several"
    return {"result": result,
            "matches": [{"slug": t["slug"], "topic": t["topic"], "status": t["status"]}
                        for t in hits]}


def cmd_match(args) -> int:
    if not any(ch.isalnum() for ch in args.query):
        print(json.dumps({"error": "match needs a query with at least one letter or digit"}))
        return EXIT_ERROR
    try:
        topics, skipped = read_topics(args.dir)
    except OSError as exc:
        print(json.dumps({"error": f"cannot read {exc.filename}: {exc.strerror}"}))
        return EXIT_ERROR
    print(json.dumps({**match_topics(args.query, topics), "skipped": skipped},
                     indent=2, ensure_ascii=False))
    return EXIT_OK


def tree_key(number: str) -> tuple:
    """Tree order: Q1 < Q1.2 < Q2 < Q10. Lenient, so a malformed number still sorts."""
    return tuple(int(part) if part.isdigit() else 0 for part in number.split("."))


def recall_questions(path: Path, n: int) -> list:
    """Answered questions for the warm-up: never recalled first, then oldest recall date, ties
    by tree number. A file check rejects still yields its answered questions."""
    _, questions = parse_lenient(path)
    answered = [q for q in questions if q["fields"].get("status") == "answered"]
    answered.sort(key=lambda q: (bool(q["fields"].get("last recalled")),
                                 q["fields"].get("last recalled", ""), tree_key(q["number"])))
    return [{"number": q["number"], "text": q["text"],
             "last_recalled": q["fields"].get("last recalled", "")} for q in answered[:n]]


def cmd_recall(args) -> int:
    path = Path(args.file).expanduser()
    try:
        questions = recall_questions(path, args.n)
    except ReadError as exc:
        print(json.dumps({"error": str(exc)}))
        return EXIT_ERROR
    print(json.dumps({"questions": questions}, indent=2, ensure_ascii=False))
    return EXIT_OK


# ---------------------------------------------------------------- render
#
# Geometry is computed here and the page only draws: ideas sit on an ellipse in Overview
# order, clockwise from the top, so the same file always renders to the same bytes. The page
# is one file with no script, no external URL and system fonts, themed light and dark through
# CSS variables, and every string from the topic file is escaped.

MAP_W, MAP_H = 760, 500
MAP_RX, MAP_RY = 270, 190
NODE_CHARS, NODE_CHAR_W, NODE_LINE_H, NODE_PAD = 16, 7.4, 17, 12
NODE_MIN_W, NODE_MAX_W = 96, 172
LABEL_CHARS = 30
PAIR_OFFSET = 9
LABEL_CHAR_W, LABEL_H = 6.2, 15
LABEL_SPOTS = (0.5, 0.38, 0.62, 0.28, 0.72)


def wrap(text: str, width: int) -> list:
    """Greedy word wrap; a word longer than the width is cut into width-long pieces."""
    lines, cur = [], ""
    for word in text.split():
        while len(word) > width:
            if cur:
                lines.append(cur)
                cur = ""
            lines.append(word[:width])
            word = word[width:]
        if not word:
            continue
        if cur and len(cur) + 1 + len(word) > width:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}" if cur else word
    return lines + [cur] if cur else lines


def fmt(n: float) -> str:
    return f"{n:.1f}".rstrip("0").rstrip(".")


def clip(cx, cy, hw, hh, dx, dy):
    """Where the ray from a box's centre along (dx, dy) leaves the box."""
    ts = [t for t in ((hw / abs(dx)) if dx else None, (hh / abs(dy)) if dy else None) if t]
    t = min(ts) if ts else 0
    return cx + dx * t, cy + dy * t


def overlaps(a, b) -> bool:
    """Two (x0, y0, x1, y1) boxes intersect."""
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def concept_svg(overview: dict) -> str:
    ideas, links = overview["ideas"], overview["links"]
    n = len(ideas)
    nodes = {}
    for i, idea in enumerate(ideas):
        angle = -math.pi / 2 + 2 * math.pi * i / n
        lines = wrap(idea["term"], NODE_CHARS)
        w = min(NODE_MAX_W, max(NODE_MIN_W, max(len(l) for l in lines) * NODE_CHAR_W + 2 * NODE_PAD))
        h = len(lines) * NODE_LINE_H + 2 * NODE_PAD - 6
        nodes[idea["term"]] = {"x": MAP_W / 2 + MAP_RX * math.cos(angle),
                               "y": MAP_H / 2 + MAP_RY * math.sin(angle),
                               "w": w, "h": h, "lines": lines, "text": idea["text"]}
    pairs = {(l["source"], l["target"]) for l in links}
    taken = [(nd["x"] - nd["w"] / 2 - 4, nd["y"] - nd["h"] / 2 - 4,
              nd["x"] + nd["w"] / 2 + 4, nd["y"] + nd["h"] / 2 + 4) for nd in nodes.values()]
    edges, labels = [], []
    for link in links:
        a, b = nodes[link["source"]], nodes[link["target"]]
        dx, dy = b["x"] - a["x"], b["y"] - a["y"]
        length = math.hypot(dx, dy) or 1
        ux, uy = dx / length, dy / length
        ox, oy = (-uy * PAIR_OFFSET, ux * PAIR_OFFSET) if (link["target"], link["source"]) in pairs else (0, 0)
        x1, y1 = clip(a["x"], a["y"], a["w"] / 2 + 4, a["h"] / 2 + 4, ux, uy)
        x2, y2 = clip(b["x"], b["y"], b["w"] / 2 + 6, b["h"] / 2 + 6, -ux, -uy)
        x1, y1, x2, y2 = x1 + ox, y1 + oy, x2 + ox, y2 + oy
        full = f"{link['source']} → {link['target']}: {link['label']}"
        edges.append(f'<line class="edge" x1="{fmt(x1)}" y1="{fmt(y1)}" x2="{fmt(x2)}" '
                     f'y2="{fmt(y2)}" marker-end="url(#arrow)"><title>{escape(full)}</title></line>')
        label = link["label"] if len(link["label"]) <= LABEL_CHARS else \
            link["label"][:LABEL_CHARS - 1].rstrip() + "…"
        # The first spot along the edge whose label box clears every node and earlier label;
        # the midpoint when none does.
        half = len(label) * LABEL_CHAR_W / 2
        spots = [(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t) for t in LABEL_SPOTS]
        lx, ly = next(((x, y) for x, y in spots
                       if not any(overlaps((x - half, y - LABEL_H / 2, x + half, y + LABEL_H / 2), box)
                                  for box in taken)), spots[0])
        taken.append((lx - half, ly - LABEL_H / 2, lx + half, ly + LABEL_H / 2))
        labels.append(f'<text class="edge-label" x="{fmt(lx)}" y="{fmt(ly + 4)}" '
                      f'text-anchor="middle"><title>{escape(full)}</title>{escape(label)}</text>')
    boxes = []
    for term, nd in nodes.items():
        x, y = nd["x"] - nd["w"] / 2, nd["y"] - nd["h"] / 2
        top = nd["y"] - (len(nd["lines"]) - 1) * NODE_LINE_H / 2 + 5
        spans = "".join(f'<tspan x="{fmt(nd["x"])}" y="{fmt(top + k * NODE_LINE_H)}">{escape(l)}</tspan>'
                        for k, l in enumerate(nd["lines"]))
        boxes.append(f'<g class="node"><title>{escape(term)}: {escape(nd["text"])}</title>'
                     f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(nd["w"])}" height="{fmt(nd["h"])}" rx="7"/>'
                     f'<text text-anchor="middle">{spans}</text></g>')
    return (f'<svg viewBox="0 0 {MAP_W} {MAP_H}" role="img" aria-label="Concept map of the key ideas">'
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            'markerHeight="7" orient="auto-start-reverse"><path class="arrow" d="M0 0L10 5L0 10z"/>'
            '</marker></defs>' + "".join(edges) + "".join(boxes) + "".join(labels) + "</svg>")


def source_html(item: str) -> str:
    m = URL.search(item)
    if not m:
        return escape(item)
    url = m.group(0).rstrip(".,;")
    # A closing ')' belongs to the URL only when it closes a '(' inside it, as Wikipedia's do.
    while url.endswith(")") and url.count(")") > url.count("("):
        url = url[:-1].rstrip(".,;")
    end = m.start() + len(url)
    return (escape(item[:m.start()]) + f'<a href="{escape(url)}">{escape(url)}</a>'
            + escape(item[end:]))


def tree_html(questions: list) -> str:
    children = {}
    for q in sorted(questions, key=lambda q: tree_key(q["number"])):
        children.setdefault(q["number"].rpartition(".")[0], []).append(q)

    def branch(parent: str) -> str:
        items = []
        for q in children.get(parent, []):
            f, status = q["fields"], q["fields"].get("status", "")
            meta = []
            if status == "answered":
                meta.append(f"answered by {escape(f.get('answered by', ''))}")
            if f.get("last recalled"):
                meta.append(f"recalled {escape(f['last recalled'])}")
            if status == "parked":
                meta.append(f"parked: {escape(f.get('park reason', ''))}")
            if status == "prereq":
                meta.append("prerequisite: answer this first")
            meta_html = f'<p class="meta">{" · ".join(meta)}</p>' if meta else ""
            items.append(f'<li class="q" data-status="{escape(status)}"><div class="q-row">'
                         f'<span class="chip">{escape(status)}</span>'
                         f'<span class="num">Q{escape(q["number"])}</span>'
                         f'<span class="q-text">{escape(q["text"])}</span></div>{meta_html}'
                         f'{branch(q["number"])}</li>')
        return f'<ul class="tree">{"".join(items)}</ul>' if items else ""

    return branch("") or '<p class="empty">No questions yet.</p>'


PAGE_CSS = """
/* Layout: one reading column; the concept map scrolls sideways inside its own frame on a phone. */
:root {
  --ground: #f5f7f8; --panel: #ffffff; --ink: #18232b; --ink-soft: #4d5b66; --rule: #d7dee3;
  --accent: #1f6f78; --edge: #7d8f9b;
  --s-open: #2f5fb3; --s-answered: #2c7a4b; --s-parked: #7a828a; --s-prereq: #a35f00;
  --display: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  --body: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
  --data: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --ground: #11181d; --panel: #18222a; --ink: #e3e9ed; --ink-soft: #9fb0bc; --rule: #2c3a44;
    --accent: #5fb8c1; --edge: #6f8492;
    --s-open: #7ea6f0; --s-answered: #6cc28f; --s-parked: #98a2ab; --s-prereq: #e2a24a;
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --ground: #11181d; --panel: #18222a; --ink: #e3e9ed; --ink-soft: #9fb0bc; --rule: #2c3a44;
  --accent: #5fb8c1; --edge: #6f8492;
  --s-open: #7ea6f0; --s-answered: #6cc28f; --s-parked: #98a2ab; --s-prereq: #e2a24a;
  color-scheme: dark;
}
body { background: var(--ground); color: var(--ink); font-family: var(--body); font-size: 15px;
  line-height: 1.55; margin: 0; }
main { max-width: 820px; margin: 0 auto; padding-block: 32px 48px;
  padding-left: max(16px, env(safe-area-inset-left, 0px));
  padding-right: max(16px, env(safe-area-inset-right, 0px));
  display: flex; flex-direction: column; gap: 36px; }
header { display: flex; flex-direction: column; gap: 12px; }
.eyebrow, section > h2, footer { font-family: var(--data); font-size: 12px; letter-spacing: 0.08em;
  text-transform: uppercase; color: var(--ink-soft); margin: 0; }
h1 { font-family: var(--display); font-weight: 600; font-size: 34px; line-height: 1.15; margin: 0;
  text-wrap: balance; }
.why { margin: 0; max-width: 65ch; }
.why b { color: var(--accent); font-weight: 600; }
.counts { display: flex; flex-wrap: wrap; gap: 8px 18px; font-family: var(--data); font-size: 13px;
  color: var(--ink-soft); }
.counts span { font-variant-numeric: tabular-nums; }
.counts .count { color: var(--ink); font-weight: 600; }
section { display: flex; flex-direction: column; gap: 14px; min-width: 0; }
.map-frame { background: var(--panel); border: 1px solid var(--rule); border-radius: 10px;
  overflow-x: auto; }
.map-frame svg { display: block; width: 100%; min-width: 600px; height: auto; }
.node rect { fill: var(--ground); stroke: var(--accent); stroke-width: 1.5; }
.node text { fill: var(--ink); font-family: var(--body); font-size: 13.5px; font-weight: 600; }
.edge { stroke: var(--edge); stroke-width: 1.4; fill: none; }
.arrow { fill: var(--edge); }
.edge-label { fill: var(--ink-soft); font-family: var(--body); font-size: 11.5px;
  paint-order: stroke; stroke: var(--panel); stroke-width: 5px; stroke-linejoin: round; }
.ideas { margin: 0; padding-left: 1.6em; display: flex; flex-direction: column; gap: 6px;
  max-width: 65ch; }
.ideas b { font-weight: 600; }
.connect { margin: 0; max-width: 65ch; color: var(--ink-soft); }
.connect b { color: var(--ink); font-weight: 600; }
.sources { margin: 0; padding-left: 1.2em; font-size: 13px; color: var(--ink-soft);
  overflow-wrap: anywhere; }
a { color: var(--accent); }
.tree { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 8px; }
.tree .tree { margin-top: 8px; padding-left: 18px; border-left: 1px solid var(--rule); }
.q-row { display: flex; align-items: baseline; gap: 10px; min-width: 0; }
.q-text { min-width: 0; overflow-wrap: anywhere; }
.num { font-family: var(--data); font-size: 13px; font-weight: 600; color: var(--ink-soft);
  font-variant-numeric: tabular-nums; }
.chip { flex: none; width: 74px; text-align: center; font-family: var(--data); font-size: 11px;
  letter-spacing: 0.04em; border-radius: 999px; padding: 1px 0; border: 1px solid currentColor; }
.q[data-status="open"] > .q-row .chip { color: var(--s-open); }
.q[data-status="answered"] > .q-row .chip { color: var(--s-answered); }
.q[data-status="parked"] > .q-row .chip { color: var(--s-parked); }
.q[data-status="parked"] > .q-row .q-text { color: var(--ink-soft); }
.q[data-status="prereq"] > .q-row .chip { color: var(--s-prereq); font-weight: 600; }
.meta { margin: 2px 0 0 84px; font-size: 13px; color: var(--ink-soft); }
.empty { margin: 0; color: var(--ink-soft); }
footer { border-top: 1px solid var(--rule); padding-top: 14px; text-transform: none;
  letter-spacing: 0; overflow-wrap: anywhere; }
@media (max-width: 480px) { h1 { font-size: 27px; } .chip { width: 64px; } .meta { margin-left: 0; } }
"""


def render_page(path: Path, text: str) -> str:
    lines = text.splitlines()
    scratch = Report()
    fields, _, body_start = parse_frontmatter(lines, scratch)
    sections = {s["name"]: s for s in parse_body(lines, body_start)}
    questions = parse_questions(sections["Questions"]["lines"], scratch)
    counts = dict.fromkeys(QUESTION_STATUSES, 0)
    for q in questions:
        counts[q["fields"]["status"]] += 1
    topic = fields["topic"]

    parts = [f'<header><p class="eyebrow">Compass map · topic {escape(fields["status"])}</p>'
             f'<h1>{escape(topic)}</h1><p class="why"><b>Why</b> {escape(fields["why"])}</p>'
             '<div class="counts">'
             + "".join(f'<span><span class="count" data-count="{s}">{counts[s]}</span> {s}</span>'
                       for s in QUESTION_STATUSES)
             + "</div></header>"]
    if "Overview" in sections:
        ov = parse_overview(sections["Overview"]["lines"], scratch)
        body = []
        if ov["ideas"]:
            body.append(f'<div class="map-frame">{concept_svg(ov)}</div>')
            body.append('<ol class="ideas">' + "".join(
                f'<li><b>{escape(i["term"])}</b> — {escape(i["text"])}</li>' for i in ov["ideas"])
                + "</ol>")
        if ov["connect"]:
            body.append(f'<p class="connect"><b>How they connect:</b> {escape(ov["connect"])}</p>')
        if ov["sources"]:
            body.append('<ul class="sources">' + "".join(
                f"<li>{source_html(s)}</li>" for s in ov["sources"]) + "</ul>")
        parts.append('<section><h2>Overview</h2>' + "".join(body) + "</section>")
    parts.append(f'<section><h2>Questions</h2>{tree_html(questions)}</section>')
    parts.append(f'<footer>Drawn by compass.py render from {escape(path.name)}, last updated '
                 f'{escape(fields["updated"])}. Edit the topic file, never this page.</footer>')
    return ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<meta name="claude:viewport-fit-sides" content="cover">\n'
            f"<title>{escape(topic)}</title>\n<style>{PAGE_CSS}</style>\n</head>\n<body>\n<main>"
            + "".join(parts) + "</main>\n</body>\n</html>\n")


def cmd_render(args) -> int:
    path = Path(args.file).expanduser()
    try:
        text = read_text(path)
    except ReadError as exc:
        print(json.dumps({"error": str(exc)}))
        return EXIT_ERROR
    report = check_text(text)
    if report.violations:
        print(json.dumps({"valid": False, "violations": report.violations}, indent=2))
        return EXIT_INVALID
    out = path.with_suffix(".html")
    try:
        out.write_text(render_page(path, text), encoding="utf-8")
    except OSError as exc:
        print(json.dumps({"error": f"cannot write {out}: {exc.strerror}"}))
        return EXIT_ERROR
    print(json.dumps({"written": str(out)}, ensure_ascii=False))
    return EXIT_OK


def positive_int(text: str) -> int:
    value = int(text)
    if value < 1:
        raise argparse.ArgumentTypeError(f"n must be a positive integer, got {text}")
    return value


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="compass.py", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p_check = sub.add_parser("check", help="validate one topic file")
    p_check.add_argument("file")
    p_check.set_defaults(func=cmd_check)
    p_list = sub.add_parser("list", help="one record per topic in the compass folder")
    p_list.add_argument("--dir", default=DEFAULT_DIR)
    p_list.set_defaults(func=cmd_list)
    p_match = sub.add_parser("match", help="resolve a query to a topic")
    p_match.add_argument("query")
    p_match.add_argument("--dir", default=DEFAULT_DIR)
    p_match.set_defaults(func=cmd_match)
    p_recall = sub.add_parser("recall", help="answered questions for the resume warm-up")
    p_recall.add_argument("file")
    p_recall.add_argument("n", nargs="?", type=positive_int, default=RECALL_DEFAULT)
    p_recall.set_defaults(func=cmd_recall)
    p_render = sub.add_parser("render", help="draw the topic as <slug>.html beside it")
    p_render.add_argument("file")
    p_render.set_defaults(func=cmd_render)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
