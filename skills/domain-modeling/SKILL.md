---
name: domain-modeling
description: Actively build and sharpen a project's domain model while designing — challenge terms against the glossary, invent edge-case scenarios that force precision, and write the vocabulary and hard-to-reverse decisions down the moment they crystallize. Use when the conversation keeps tripping over what a word means, when two names are circulating for one concept, when a term in the discussion contradicts the code, or when Kyle is writing/editing a CONTEXT.md or recording an ADR. Triggers on "what do we even call this", "are those the same thing", "domain model", "glossary", "ubiquitous language", "bounded context", "write an ADR for this". NOT for: merely *reading* an existing glossary for vocabulary (that's a one-line habit, not this skill), maintaining a project wiki's pages and decision ledger (use project-wiki), or generating a documentation set from an audit plan (use artifacts-generate).
---

# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the *active* discipline: challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallize. (Merely *reading* `CONTEXT.md` for vocabulary is not this skill: that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.)

## During the session

### Challenge against the glossary

When a term conflicts with the existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y. Which is it?"

### Sharpen fuzzy language

When a vague or overloaded term shows up, propose a precise canonical term. "You're saying 'account': do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force precision about the boundaries between concepts.

### Cross-reference with code

When Kyle states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible. Which is right?"

### Update the glossary inline

When a term is resolved, write it down right there. Don't batch these up: capture them as they happen. Format in [CONTEXT-FORMAT.md](CONTEXT-FORMAT.md).

`CONTEXT.md` should be totally devoid of implementation details. It is not a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

## Where things get written

Create files lazily — only when there's something to write. The glossary is uncontested; **decisions are not**, so check what the repo already has before creating a parallel ledger.

| The repo has | Glossary goes to | Decisions go to |
|---|---|---|
| Nothing yet | a root `CONTEXT.md`, created on the first resolved term | `docs/adr/NNNN-slug.md`, created on the first ADR — format in [ADR-FORMAT.md](ADR-FORMAT.md) |
| An existing `docs/adr/` | root `CONTEXT.md` | that directory, continuing its numbering and its house format, not this skill's |
| Wiki sentinel files (`PROJECT.md`, `Wiki/`, `HANDOFF.md`) | root `CONTEXT.md` | **`Decisions.md`, via `project-wiki`** — that skill owns the ledger and its append-and-supersede rules. Do not open a second `docs/adr/` alongside it. |
| A `CONTEXT-MAP.md` at the root | the per-context `CONTEXT.md` the topic belongs to; ask if it's unclear which | context-specific `docs/adr/` for context-local decisions, the root one for system-wide |

Two ledgers for one project is the failure this table exists to prevent: the decision that mattered ends up in whichever one the next session doesn't read.

### Offer ADRs sparingly

Only offer to record a decision when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip it. Easy to reverse? You'll just reverse it. Not surprising? Nobody will wonder why. No real alternative? There's nothing to record beyond "we did the obvious thing."

## When a wayfinder map dispatched this

`grilling` and `domain-modeling` are the pair that resolve the default wayfinder ticket type. The division of labor: grilling works the question, domain-modeling keeps the vocabulary honest while it's being worked, and writes down what settles.

One thing to watch. A wayfinder ticket resolves into a **resolution comment on the ticket** — that's the canonical record, and the map's Decisions-so-far gists it. Don't *also* mint an ADR for the same decision unless it independently clears the three-part bar above; a map whose every ticket spawned an ADR has just duplicated itself into `docs/adr/`.

## Unattended runs

The challenges are questions, and questions need an answer. With nobody there: write the glossary entries you can settle from the code alone (a term the code already names unambiguously), and collect every genuine ambiguity as a list of open questions with your recommended reading of each — marked as unconfirmed. Never resolve a contested term or record an ADR on your own authority.

---

Vendored from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT, Copyright (c) 2026 Matt Pocock), adapted to house conventions. Full notice: `THIRD-PARTY.md` in the claude-config repo.
