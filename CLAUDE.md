# Operating Constraints

@~/.claude/operating-constraints.md

---

# Claude Code Modes

Three structured modes for working with Claude Code. Type the trigger phrase to activate.

---

## Kickoff Mode → run the `/kickoff` skill

**Purpose:** Start a brand new project from a rough, half-baked idea — interview it into shape before any code.
**Trigger:** `/kickoff`, "kickoff mode", or "new project idea" (followed by the idea).

When any of those fire, **invoke the `kickoff` skill** (`~/.claude/skills/kickoff/`) — do not improvise the interview inline. The skill runs the deep, adaptive, one-question-at-a-time discovery interview (for as long as the idea needs), produces an approved kickoff brief + phased plan, and — only after I confirm at a gate — scaffolds `~/Projects/<slug>/`, a git repo, and a private GitHub repo with the brief inside. Briefs are archived in `~/Projects/_kickoffs/`. For light throwaway experiments, use `/mini` instead.

---

## Improvement Mode

**Purpose:** Fix, refine, or optimize something that already exists in the project but isn't working well.
**When to use:** Something feels off — slow performance, bad UX, ugly layout, confusing flow, or a bug you can't fully describe.
**Trigger:** Say "improvement mode" followed by what bugs you.

When I say "improvement mode", before making any changes:
- Ask me what part of the project I want to improve
- Ask me what's wrong with it or what bugs me about it
- Ask me what "better" looks like in my words
- Review the current code/implementation yourself and tell me what you see
- Propose 2-3 approaches ranked by effort vs. impact
- Wait for me to pick one before changing anything

---

## New Feature Mode

**Purpose:** Add a new capability or feature to an existing project without breaking what's already there.
**When to use:** You want the project to do something it doesn't do yet and need Claude Code to figure out where and how it fits.
**Trigger:** Say "new feature mode" or "feature mode" followed by your idea.

When I say "new feature mode" or "feature mode", before building anything:
- Ask me to describe the feature in plain language
- Ask me why I want it (what problem does it solve)
- Review the existing project structure and tell me how/where this feature would fit
- Flag any conflicts with how things currently work
- Propose how it connects to existing features
- Summarize the plan and wait for approval before writing code

---

## Git Workflow

- Always create a feature branch before making changes
- Branch naming: `feat/`, `fix/`, `refactor/`, `docs/`
- Commit frequently with descriptive messages
- Never push to main autonomously, but you may push when I explicitly authorize the specific commit (e.g. "yes, push to main", "commit and push to main"). A blanket pre-approval doesn't count — each push needs its own go-ahead.

## Clarifying questions and option formatting
- Ask 1–3 high-leverage clarifying questions up front whenever a prompt is ambiguous or uses fuzzy terminology — I prefer alignment over rework. When offering options: give each a short label, a 1–2 sentence merits/tradeoffs description, and mark your "(Recommended)" pick. If you assume rather than ask, surface the assumptions before acting on them.
