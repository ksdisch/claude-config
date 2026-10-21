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

`list` and `match` read `--dir` (default ~/Learning/compass); a missing folder holds no topics,
and a file that cannot be read lands in `skipped` instead of failing the whole folder.

The file format is the contract; references/file-format.md is its prose definition and this
parser is its executable one. Keep the two in step.
"""
import argparse
import json
import re
import sys
from pathlib import Path

EXIT_OK, EXIT_INVALID, EXIT_ERROR = 0, 1, 2

DEFAULT_DIR = "~/Learning/compass"
WHY_LIMIT = 60
RECALL_DEFAULT = 3

FRONTMATTER_REQUIRED = ("topic", "why", "status", "created", "updated")
FRONTMATTER_OPTIONAL = ("workspace",)
TOPIC_STATUSES = ("open", "closed")
QUESTION_STATUSES = ("open", "answered", "parked", "prereq")
ANSWERED_BY = ("claude", "kyle")
QUESTION_FIELDS = ("status", "answered by", "last recalled", "park reason")
QUESTION_SUBSECTIONS = ("Answer", "Sources")
SECTION_ORDER = ("Overview", "Questions", "Close-out", "Session log")
REQUIRED_SECTIONS = ("Questions", "Session log")

DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FENCE = re.compile(r"^\s*(```|~~~)")
H2 = re.compile(r"^##\s+(.*?)\s*$")
H3 = re.compile(r"^###\s+(.*?)\s*$")
H4 = re.compile(r"^####\s+(.*?)\s*$")
QUESTION_HEADING = re.compile(r"^Q([0-9.]+)\s*:\s*(.*)$")
TREE_NUMBER = re.compile(r"^[1-9][0-9]*(\.[1-9][0-9]*)*$")
FIELD = re.compile(r"^-\s+([A-Za-z][A-Za-z ]*?)\s*:\s*(.*?)\s*$")
LOG_ENTRY = re.compile(r"^-\s+(\d{4}-\d{2}-\d{2})\b")


class Report:
    def __init__(self):
        self.violations = []

    def add(self, rule: str, line, message: str):
        self.violations.append({"rule": rule, "line": line, "message": message})


def strip_fences(lines):
    """Yield (lineno, text, in_fence) so headings inside code blocks are never structure."""
    in_fence = False
    for i, text in enumerate(lines, start=1):
        if FENCE.match(text):
            yield i, text, True
            in_fence = not in_fence
            continue
        yield i, text, in_fence


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
            continue
        h4 = None if in_fence else H4.match(text)
        if h4:
            sub = h4.group(1)
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
    if recalled and not DATE.match(recalled):
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
    if status == "parked" and not fields.get("park reason"):
        report.add("parked-needs-reason", q["line"],
                   f"{label}: parked questions need a non-empty '- park reason:'")


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
        if value and not DATE.match(value):
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
            if text.strip() and not continuation and not LOG_ENTRY.match(text):
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
        return path.read_text(encoding="utf-8")
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
        if not p.is_file():
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


def words(text: str) -> list:
    return [w for w in re.split(r"[^0-9a-z]+", text.casefold()) if w]


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
    if not words(args.query):
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
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
