# Persona format

Persona files live in a teach workspace at `personas/<NN>-<slug>.md`. The two-digit prefix
orders them; `/mock-call <slug>` matches the part after the prefix. Every section below is
required; the workspace's contract check greps for the headings.

```md
# Persona: {fictional name}, {role}

## Who they are
{2–3 sentences: role, the situation they're in, what's on their desk this week. Fictional person; scenario facts cited from ./research/ digests by file name.}

## What they care about
- {the two or three things that decide whether they keep talking}

## How they talk
{The vocabulary they will actually use, as a short list. Every term here is one the debrief may score.}

## Opening line
{What they say when they pick up or call back. Say which: Kyle dialed them, or they are returning his voicemail.}

## Curveballs
1. {an objection or question that tests a specific term}
2. {…}
3. {…}

## What credible sounds like
{2–3 sentences: the answers that would make this person keep talking. Not a script; a bar.}

## Terms this persona tests
- {term} · {reference/<file>.html | lessons/<file>.html | not yet taught}
```

Rules:
- Fictional names, always. A persona modeled on a real person may only ask questions; it never asserts a fact about a real firm.
- No contact details of any kind.
- "Terms this persona tests" is what the debrief scores and what persona selection counts. Keep it to the terms the persona would actually make Kyle use.
- Update the pointer after `· ` when a lesson or reference doc covers the term; until then it reads `not yet taught`.
