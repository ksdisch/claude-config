---
name: grilling
description: Grill the user relentlessly about a plan, decision, or idea until shared understanding — a rounds-based design-tree interview where every question carries a recommended answer. Use when Kyle wants his thinking pressure-tested before acting on it — "grill me", "grill me on this", "poke holes in this plan", "interrogate this design", "pressure-test this idea", "stress-test my plan", "what am I not thinking about here", "play devil's advocate on this" — or when he types /grilling or /grill-me. NOT for: a brand-new half-baked project idea that needs discovery and scaffolding (use kickoff), picking what to work on next from a backlog (use backlog-hygiene), or reviewing a finished diff before merge (use adversarial-review). Blocks on Kyle's answers by design — do not auto-invoke in unattended runs (cron/Routine, cloud one-shot, autonomous flows); if reached there anyway, follow the body's unattended note.
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled — the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Each question should be formatted like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Each round the user answers reshapes the tree — settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent to find it — don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report — ask the rest of the frontier now. The _decisions_ are the user's — put each to them and wait.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.

**Unattended runs** (subagent, cron/Routine, cloud one-shot, autonomous flow — nobody can answer): do not park on a question. Compute round 1's frontier, write out every question with its recommended answer marked as an unconfirmed working assumption, and stop — that frontier report is the deliverable. Never act on the plan from an unattended run; the interview resumes when a human answers.
