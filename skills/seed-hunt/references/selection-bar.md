# The selection bar — what qualifies a paper as the next seed

This is the living memory of the seed-hunt skill. It is updated by Phase 1 (the harvest)
at the start of every hunt, with Kyle's sign-off on the diff — never silently. Each
lesson cites the project evidence that earned it, because a bar entry without evidence is
just an opinion.

## The recipe (proven twice, as of 2026-07-06)

Take a published primitive and *reproduce and measure* a narrow slice of it honestly, at
hobby scale, under pre-committed statistical gates. The honest framing, always:
"reproduced and measured a published finding — here is the narrow, measured slice."
Never "I invented this."

## The bar

Score every candidate against each entry. A paper doesn't have to ace all of them, but a
hard fail on 1, 2, or 5 is disqualifying; the rest are weights, and *narrow* clears
become the fit-pilot's named risks in the next project's KICKOFF.

1. **"Reproduce and measure, never invent" is the entire defensibility.** Qualify a paper
   only if it offers a primitive re-implementable small AND a claim measurable as a
   narrow delta at hobby scale. *(forge-gap D1; decay-pin KICKOFF framing.)*

2. **Cheap + deterministic or it dies.** No GPU/training; models via OpenRouter at
   pennies (decay-pin's entire v1+v2: ~350+ episodes, single-digit dollars). Success must
   be gradable by a deterministic oracle — mechanical pass/fail — never an LLM judge.
   Papers whose evaluation is inherently judge-y (open-ended generation quality) fail.
   *(forge-gap; decay-pin grader.py, D6.)*

3. **Prefer a mechanically verifiable manipulation.** decay-pin's superpower: the
   intervention (constraint evicted / present / re-injected) was verified per trial by
   string search — free, model-free, before trusting any outcome. A paper whose
   manipulation can't be checked mechanically forces you to trust the model twice.
   *(decay-pin M0 eviction gate through M5 visibility gate.)*

4. **Confound hygiene.** Pick claims that can't be explained by training priors.
   decay-pin rejected destructive-op and privacy scenarios because trained aversion would
   contaminate "the in-context rule decayed." Ask of every candidate: could the effect
   exist without the paper's mechanism? *(decay-pin D2, D13.)*

5. **Statistics is the binding constraint.** It was, in all eleven forge-gap stages and
   all six decay-pin stages — never the code, never the cost. Proportion outcomes need
   N≈20–40/arm; equivalence claims need 40 *clean* trials; a small promised effect nulls
   at affordable N. Prefer big expected deltas or tunable difficulty. *(forge-gap D7/D16;
   decay-pin D8, D11.)*

6. **Pre-commit the gates as code — and a null is a headline.** decay-pin encoded every
   verdict (m0.py–m5.py) before any paid run and dry-ran them against real data (wrong-arm
   input exits INVALID). M4's STRATEGY-NULL was a *reportable result* because it was
   pre-committed. Prefer papers where even the null tells a story. *(decay-pin M4;
   forge-gap kill-triggers.)*

7. **Must be stage-able and pilot-gated.** Every project starts with a fit-pilot carrying
   kill/swap triggers, and every paid wave sits behind a free mechanical gate plus an N≈5
   smoke (decay-pin's M4 smoke caught a real crash before it could poison an arm).
   Measured-rate cost estimates beat guessing — three decay-pin stages running. The paper
   must tolerate that style. *(forge-gap S0–S11; decay-pin M0, D18, D20.)*

8. **Range vs reuse is Kyle's call, not yours.** Reusing the harness muscle (tool loops,
   Wilson/Newcombe) is fast but "more of the same"; a new surface (RAG / memory /
   multi-agent / evals) shows range at higher build cost. Put the trade-off in the
   decision brief with the current weight stated.
   **Current weight (2026-07-06):** two projects now sit on the same harness
   (forge-gap built it, decay-pin copy-adapted it per D1), so the "more of the same"
   concern is heavier than it was — a third tool-loop project needs a positive reason
   beyond speed.

## Watchlist (downgraded, not forgotten)

- **The capability cliff** *(forge-gap S7/S8)*: strong models ace simple mechanical tasks;
  weak ones fail wholesale at 0%. Downgraded after decay-pin's M0 — all three cheap
  models held clean ~0% floors, so the cliff didn't bite there. Still: if a candidate's
  phenomenon *requires model failures*, flag the plausibility that a cheap model exhibits
  them, and make it the fit-pilot's first question.

## Project ledger

| project | paper / seed | span | headline outcome | closed |
|---|---|---|---|---|
| forge-gap (`~/Desktop/forge-gap`, archived) | the "Forge" self-hosted-reliability framing | S0–S11 | reproduced + measured the reliability gap; recipe established | S11, PR #18, merge `ed4c08f` (~2026-06) |
| decay-pin (`~/Projects/decay-pin`) | arXiv 2606.22528 — Governance Decay + Constraint Pinning | M0–M5 | 0%→100%→0% arc (floor/truncate/pinned) on 3 models, replicated on a 2nd task; v2 strategy axis: truncate 20/20 · summarize 2/40 (STRATEGY-NULL) · head-tail 0/40 (PROTECTIVE) | M5, PR #18, merge `5ae1a0a` (2026-07-06) |
