---
name: to-spec
description: "Turn the current conversation into a spec: no interview, just synthesis of what's already been discussed. Writes it where the repo keeps specs (docs/specs/ absent a convention); optionally publishes it to the issue tracker. NOT for: interviewing a half-baked idea into shape (use grilling or kickoff) — by the time this fires, the decisions already exist in the conversation."
disable-model-invocation: true
---

This skill takes the current conversation context and codebase understanding and produces a spec. Do NOT interview Kyle; just synthesize what you already know.

## Process

1. Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the spec (`CONTEXT.md`, via `CONTEXT-MAP.md` when there's more than one), and respect any ADRs in the area you're touching.

2. Sketch out the seams at which you're going to test the feature — "seam" in the codebase-design skill's sense. Existing seams should be preferred to new ones. Use the highest seam possible. If new seams are needed, propose them at the highest point you can. The fewer seams across the codebase, the better - the ideal number is one.

   Check with Kyle that these seams match his expectations.

3. Write the spec using the template below, and put it **where the repo already keeps specs** — absent a convention, `docs/specs/<slug>.md` (the same convention wayfinder's cleared maps collapse into). Commit it; a spec that isn't in git is invisible to every other session.

4. **Publish to the tracker only if Kyle wants it there** — as one issue carrying the spec body, labelled `ready-for-agent` per the triage skill's vocabulary (create the label first if the repo doesn't have it), so agents can grab it. On a **public** repo's tracker, ask before the first write: everyone watching the repo receives what lands there (the same guard as wayfinder's tracker.md).

5. Name the natural next move and stop: `to-tickets` breaks the spec into tracer-bullet tickets with blocking edges; a well-specified chunk can go straight to a builder session.

<spec-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A LONG, numbered list of user stories. Each user story should be in the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

This list of user stories should be extremely extensive and cover all aspects of the feature.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it within the relevant decision and note briefly that it came from a prototype. Trim to the decision-rich parts, not a working demo, just the important bits.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Out of Scope

A description of the things that are out of scope for this spec.

## Further Notes

Any further notes about the feature.

</spec-template>

---

Vendored from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT, Copyright (c) 2026 Matt Pocock), adapted to house conventions. Full notice: `THIRD-PARTY.md` in the claude-config repo.
