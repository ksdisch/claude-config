# Compass topic file format

One markdown file per topic, in the flat folder `~/Learning/compass/`, named `<slug>.md` (a slug already taken gets the first free `-2`, `-3`, … suffix). The file
is the source of truth. `scripts/compass.py check <file>` is the executable version of this page;
when the two disagree, fix whichever is wrong in the same change.

## Whole file

```markdown
---
topic: Rust lifetimes
why: I review Rust PRs at work and need to read borrow-checker errors without guessing.
status: open
workspace:
map:
created: 2026-10-18
updated: 2026-10-20
---

# Rust lifetimes

## Overview
(optional: 5–8 key ideas, how they connect, links, sources)

## Questions

### Q1: What does `'a` actually constrain?
- status: answered
- answered by: claude
- last recalled:

#### Answer
It constrains how long a reference may be used, not how long the value lives. ...

#### Sources
- The Rust Book, ch. 10.3 — https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html
- src/parser.rs:42 (the borrow this question came from)

### Q1.1: Why can't the compiler infer it in a function signature?
- status: open
- last recalled:

### Q2: Do I need to understand variance first?
- status: parked
- park reason: Variance matters for library authors; my why is reading errors.
- last recalled:

## Close-out
(required when status is closed, absent otherwise)

## Session log
- 2026-10-18 — Started; logged Q1, Q2; answered Q1.
- 2026-10-20 — Parked Q2; logged Q1.1.
```

## Frontmatter

Between two `---` lines, one `key: value` per line. Values are plain single-line text: no quotes,
no YAML lists, no line breaks. The value is everything after the first colon, so colons inside a
why are fine.

| Key | Required | Value |
|---|---|---|
| `topic` | yes | Display name |
| `why` | yes | Why Kyle is learning it, one line |
| `status` | yes | `open` or `closed` |
| `workspace` | no | Path to a linked teach workspace (link only; compass never writes there) |
| `map` | no | Link to the topic's published map Artifact, written the first time `--map` publishes it |
| `created` | yes | `YYYY-MM-DD` |
| `updated` | yes | `YYYY-MM-DD`, bumped on every write |

## Sections

`##` headings, in this order. Anything before the first `##` (the `# <topic>` title) is ignored.

1. `## Overview` — optional; at most one, revised in place. Five to eight numbered key ideas
   (term in bold, one sentence each), a `How they connect:` paragraph, an optional `Links:` line
   with one bullet per relation, then a `Sources:` line and a bullet per source. `check` treats
   the prose as free text and checks only the links:

   ```
   Links:
   - Deep module → Interface: keeps it small
   - Interface → Implementation: is the cost of reaching
   ```

   Each bullet is `- <term> → <term>: <label>`, with `→` (not `->`). Both ends name a bolded
   key idea, matched case-insensitively, and an idea never links to itself. `compass.py render`
   draws each bullet as a labelled arrow on the topic's map.
2. `## Questions` — required, may be empty.
3. `## Close-out` — required and non-empty when `status: closed`; must be absent when `open`.
   Reopening moves its text into the session log as an indented continuation of the reopen
   entry, so a reopened file loses nothing.
4. `## Session log` — required, may be empty. Each entry is `- YYYY-MM-DD — <what moved>`;
   an indented line continues the entry above it.

No other `##` sections, and each appears at most once.

## Questions

Each question is a `###` heading, at the same level no matter how deep it nests:

```
### Q<tree number>: <question text>
```

- **Tree number.** Dot-separated positive integers, no leading zeros: `Q1`, `Q1.2`, `Q3.1.4`. A
  child is numbered under its parent and the parent must exist (`Q3.1` needs `Q3`; `Q1.2.1` needs
  `Q1.2`). Numbers are unique and stable for life — never renumber, never reuse. Gaps are allowed.
  The next top-level number is one above the highest in use; the next child of `Q3` is one above
  its highest existing child.
- **Fields.** Directly under the heading, one `- key: value` bullet each, nothing else between
  them:

  | Field | When | Value |
  |---|---|---|
  | `status` | always | `open`, `answered`, `parked` or `prereq` |
  | `last recalled` | always written (may be empty) | empty until first recalled, then `YYYY-MM-DD` |
  | `answered by` | `answered` | `claude`, or `kyle` (Kyle answered first and Claude checked it) |
  | `park reason` | `parked` | one line: why it drifts from the why; removed on unpark |

- **Subsections.** Only for answered questions, after the fields:
  - `#### Answer` — non-empty. For `answered by: kyle`, this is Kyle's answer as checked: what
    held up, and Claude's corrections where it didn't.
  - `#### Sources` — a bullet list with at least one item. A web source is title + URL; a local
    file is its path with a line where it helps; a repo file is `path:line` relative to the repo.

  No other `####` headings. Headings inside fenced code blocks are text, not structure, so an
  answer may quote markdown or code freely.

## What `check` reports

JSON on stdout: `{"valid": bool, "violations": [{"rule", "line", "message"}]}`; `line` is `null`
for a missing section. Exit 0 when valid, 1 when not, 2 when the file can't be read.

| Rule | Meaning |
|---|---|
| `frontmatter-missing` | No opening `---`, or it's never closed |
| `frontmatter-syntax` | A frontmatter line isn't `key: value` |
| `frontmatter-field` | A required key is missing or empty, or a key is unknown or repeated |
| `frontmatter-date` | `created`/`updated` isn't a real `YYYY-MM-DD` date |
| `topic-status` | `status` isn't `open` or `closed` |
| `section-unknown` / `section-duplicate` / `section-order` / `section-missing` | Section shape |
| `closed-needs-close-out` | Closed topic without a non-empty Close-out |
| `close-out-on-open` | Close-out present on an open topic |
| `session-log-entry` | A log line that isn't `- YYYY-MM-DD …` or an indented continuation |
| `question-heading` | A `###` under Questions that isn't `Q<number>: <text>`, or has empty text |
| `tree-number` | A malformed tree number (`Q0`, `Q1.0`, `Q01`, `Q1..2`) |
| `tree-duplicate` | Two questions share a number |
| `tree-orphan` | A child whose parent number doesn't exist |
| `question-field` | Unknown, repeated, missing `last recalled`, misplaced (`answered by` off an answered question, `park reason` off a parked one), or stray line under Questions |
| `question-subsection` | A `####` other than Answer or Sources, a repeated one, or one on a question that isn't answered |
| `question-status` | Missing status, or not one of the four |
| `last-recalled-date` | Non-empty `last recalled` that isn't a real `YYYY-MM-DD` date |
| `answered-by` | Answered question without `answered by: claude` or `kyle` |
| `answered-needs-answer` | Answered question without a non-empty Answer |
| `answered-needs-sources` | Answered question without a non-empty Sources list |
| `parked-needs-reason` | Parked question without a park reason |
| `overview-link` | A `Links:` bullet that isn't `- <term> → <term>: <label>`, names an end that isn't a bolded key idea, or links an idea to itself |

## The rendered map

`compass.py render <file>` checks the file, then writes `<slug>.html` beside it, the only file
compass writes besides topic files. It is generated output: never hand-edited, never the source of
truth, and ignored by `list` and `match`, which read only `*.md`. A file `check` rejects is not
rendered.
