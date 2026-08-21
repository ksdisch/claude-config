# Spec template: mandatory "module changes & interfaces" section

**Status:** Idea — not committed. Mined from ""Software Fundamentals Matter More Than Ever" — Matt Pocock" (https://www.youtube.com/watch?v=v4F1gFy-hqg) by `cc-yt-idea-mine` on 2026-08-21.

## Premise

Pocock builds module awareness into his planning artifacts: "inside the PRD I'm specific
about the module changes and the interfaces inside those modules, how they're being
modified." The module map "needs to be part of our ubiquitous language… we need to build
it into our planning skills as well" — Kent Beck's "invest in the design of the system
every day," applied at spec time.

## The bet

A small diff to `to-spec` (and possibly the `specifier` agent): every spec names which
modules change and exactly how their interfaces change, not just what behavior results.
This keeps interface design — the part the human owns under the gray-box posture
([`gray-box-review-policy`](gray-box-review-policy.md)) — explicit and reviewable at
planning time, for the cost of one template section.

## Decisions / open questions

- `to-spec` only, or also `specifier` (whose Gherkin output is behavior-shaped by
  design — an interface-changes section may fit its QA-procedure file better than the
  `.feature`)?
- Hard requirement vs. "when the change touches module interfaces" conditional — specs
  for pure-behavior tweaks shouldn't grow boilerplate.

## Credible first step

Add the section to `to-spec`'s template with the conditional phrasing, use it on the
next real spec, and judge whether `specifier` needs it too.

## Dependencies

Nothing version-sensitive — a template change to skills in this repo. Verification at
capture (2026-08-21): no capability claims to check.

## Explicitly out of scope

Changing what `to-tickets` or `implement` do with the section (they inherit it for
free), and any enforcement mechanism beyond the template itself.

## Source segment

> "We need to build it into our planning skills as well. So, my write a PRD, inside the
> PRD I'm specific about the module changes and the interfaces inside those modules, how
> they're being modified. I'm thinking about them all the time. And this comes from Kent
> Beck. Invest in the design of the system every day."
