# research/ Digest Format

Each cached source is one file at `research/<slug>.md`, where the slug is the dash-case of the
source title (drop articles and punctuation: "The Rust Programming Language" →
`rust-programming-language`). Digests exist so later lessons can cite and quote sources without
re-fetching the web.

The `Cached:` line in each `RESOURCES.md` entry is the only handoff to `/teach` — a teaching
session reads the digest before searching the web.

## Template

```md
# {Source title}

- **URL:** {url}
- **Type:** {docs | book | course | video | paper | blog | community}
- **Author/steward:** {who, plus one line on why they are trustworthy}
- **Fetched:** {YYYY-MM-DD — or "not fetched: {reason}" for metadata-only digests}
- **Covers:** {one line: which part of the mission this source serves}
- **Where to get it:** {metadata-only digests only: where to buy, borrow, or enroll}

## Structure
{The source's own shape — table of contents, chapter list, video chapters — so a lesson can
cite "chapter 4" without re-fetching.}

## Key concepts
{The load-bearing ideas, compressed. Aim for the 20% a lesson would actually cite.}

## Notable quotes
{Short attributed excerpts, each with a location (section / page / timestamp).}
```

## Rules

- **Digest, not dump.** Select quotes and compressed concepts only — never a verbatim copy of
  the source. This is both a copyright posture and a usefulness one: a dump is as unreadable
  as the original.
- **Metadata-only digests** (books, paywalls, anything unfetchable): keep the header block
  (including `Covers`), fill in `Where to get it`, and omit `Structure`, `Key concepts`,
  and `Notable quotes` entirely. Never fabricate content for a source that was not fetched.
- **Every digest is linked.** Its `RESOURCES.md` entry carries `Cached: ./research/<slug>.md`.
  A digest no entry links to is an orphan: report it; deleting it is the user's call.
- **Slug collisions.** Two distinct sources can slugify identically; append `-2` (then `-3`,
  …) to the later one.
- **One source per file.** A digest that covers two sources should be two files.
