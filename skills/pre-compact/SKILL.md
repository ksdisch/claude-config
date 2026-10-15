---
name: pre-compact
description: Checkpoint a long session before /compact so nothing settled lives only in the conversation, then give an honest "safe to compact" or "not yet, because X". Use when "/compact" arrives as a plain message mid-turn, or Kyle says "about to compact", "am I good to compact?", "checkpoint", "save state", "I'm near 150k", or types /pre-compact — even without naming the skill. Writes settled decisions, open items, deferrals, and a "Next step" line into the active skill's existing durable home (wayfinder ticket file, CONTEXT.md/ADRs, spec, issue files, branch) or a short .scratch checkpoint, commits and pushes the feature branch, and replies with SHA, settled list, what's left, and a git-checked verdict. Never runs /compact, pushes to main, merges, touches PRs, resolves a ticket awaiting confirmation, or continues the work. NOT for moving to a fresh session (/handoff-session writes a paste-able prompt and stops); this keeps the same session alive across compaction.
---

# pre-compact — save what's settled, then say whether compacting is safe

Compaction is lossy. Anything agreed in conversation but not written to disk can come
back garbled or not at all. This skill is a **checkpoint only**: write the state down,
push it, and give a verdict. Don't advance the work, tidy files, or "improve" anything
along the way, because the session continues after compaction and the next turn picks
up from what you saved.

## 1. If "/compact" arrived as a message, say so in one line

/compact is a built-in that only runs when Kyle types it at an idle prompt; sent
mid-turn, it reaches you as plain text. Before any tool call, say in one line that it
didn't run because it arrived mid-turn, and that you're saving the session first. The
final reply repeats it once, with "type it again now". Never try to run it.

## 2. Find the durable home

Use the home the active skill already owns. Don't invent a new document type when one
of these fits:

| Active work | Home for what's settled |
|---|---|
| wayfinder ticket | That ticket's file under `.scratch/<effort>/issues/` — a `### Checkpoint — working notes, not the answer` entry under `## Comments`, with the date |
| grill-with-docs / domain-modeling | `CONTEXT.md` (terms) and `docs/adr/` (decisions), matching the existing files' format |
| to-spec | The spec file |
| to-tickets | The issue files plus `tickets.md` |
| implement / implement-spec | Committed work on the branch; progress notes as a comment on the ticket being built |
| none of the above | A short `.scratch/<slug>/checkpoint.md` |

If the home has nowhere natural for open items and the next step (CONTEXT.md, for
example), put those in `.scratch/<slug>/checkpoint.md` next to it. On a repeat
checkpoint in the same session, update your earlier entry in place rather than stacking
a second one.

## 3. Write the state down

An edit Kyle already approved but you haven't made yet (terms agreed for CONTEXT.md,
for example) is settled work: make it now if you can write it without a new decision.
If it needs one (the terms were agreed but their meaning never was), list it as open
instead.

Write it for an agent reading cold after compaction:

- **Settled.** Each decision with Kyle's actual choice: whether Kyle took your
  recommendation or picked something else, and what it was.
- **Open.** Questions still being worked in this item.
- **Deferred.** Each item pushed elsewhere, with the item it went to, named by its title.
  Don't edit the receiving item. If it doesn't already state the question, say so under
  what's left.
- **Files touched** this session.
- **Next step.** One line a post-compaction agent can act on without rereading anything.

A grilling ticket isn't resolved until Kyle confirms shared understanding. Leave its
`Status:`, claim, and open state alone, and don't write the formal Answer or touch the
map's Decisions-so-far.

## 4. Commit and push the feature branch

- Work on a feature branch. If you're on the default branch, branch first (`docs/` or
  `feat/`, per the global git workflow).
- Stage only files this session touched, by path. Other sessions' dirty or untracked
  files stay exactly as they are.
- Make one checkpoint commit. Don't amend it or follow it with a polish pass.
  Write a descriptive message (e.g. `docs(<effort>): checkpoint <item> before
  compaction`) and end it with the attribution lines the session's system reminder gives.
- `git push -u origin <branch>`. Never push to the default branch, merge, open or close
  a PR, or close a ticket. Those wait for Kyle. If the push fails, don't touch remote
  or upstream config; report it and hand the fix to Kyle.

## 5. Check readiness against git, not memory

Run `git status --porcelain` and `git rev-list --count @{u}..HEAD`. Then the verdict is:

- **Safe to compact** only when none of this session's files show as modified or
  untracked, the ahead count is 0, and nothing said in conversation is missing
  from what you wrote. Reread the last few exchanges for any choice or caveat you
  skipped.
  "No upstream configured" counts as not pushed. Pushed is the bar because it puts the
  notes off this machine and in reach of other sessions.
- **Not yet** otherwise, naming exactly what would be lost (e.g. "the push failed: no
  upstream", "your last answer, on rest days, isn't in the ticket yet").

Other sessions' dirty files don't affect the verdict. Mention them in one line as
left untouched.

If you mention context size, point to the status line. Never state a token count.

## 6. Reply in this shape

Name every ticket, decision, or finding by its title, or gloss any ID on first use
(`ticket 03 (how rest days pass)`).

```
Everything from this <session kind> is saved: commit <sha>, pushed to <branch>. <If
/compact arrived mid-turn: "Your /compact didn't run because it arrived while I was
mid-turn. Type it again now and it will." Otherwise: the verdict sentence.>

Where it stands. <N> questions are settled, and <you took my recommendation on each |
you took it on all but #k, where you chose …>:
1. <Plain-language gist of a settled decision>
2. ...

<Open items in this <ticket | item>, including a next question not yet asked, or
"Nothing on this ticket is left to ask."> <Each deferral:
"X goes to "<other item's title>".">

<One thing I need from you: … — e.g. confirm the summary above is our shared
understanding, after compacting or right away. Once you do, I'll: <the resolve steps
the active skill takes next>.> (Omit if nothing is needed.)

The full notes are in <the home>:
code "<absolute path>"
```

When the verdict is **not yet**, the first line becomes "Not yet": what would be lost
(cite the local SHA if there is one) and the one step that fixes it. Keep the rest of
the shape, and don't tell Kyle to type /compact.

## Follow-up: "So I'm good to compact now?"

Answer only that question. Rerun step 5. If it's clean, reply in one or two lines: yes,
`<sha>` is on `origin/<branch>`, and nothing since the checkpoint exists only in
conversation. If something new was settled after the checkpoint, save it (steps 3–4)
and answer "Yes, now", with the new SHA. Don't repeat the full summary.
