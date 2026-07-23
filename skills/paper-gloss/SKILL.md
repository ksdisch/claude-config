---
name: paper-gloss
description: Post-process a paper-eli5 output by annotating every occurrence of selected jargon terms with a plain-English expansion followed by the original term in parentheses. AI proposes the candidate term list with expansions; you trim it; the skill runs a context-aware substitution pass across the entire document. Run after /paper-eli5 when specific terms are still opaque after the first rewrite. Output is a new -glossed.md file beside the input.
---

# Paper Gloss — annotate every jargon term in a paper-eli5 output

A companion to `/paper-eli5`. Takes a finished eli5 output and produces a second
pass where every approved technical term is replaced inline at **each occurrence**
with a plain-English expansion, with the original term immediately following in
parentheses — so you never have to remember what a term means from an earlier
paragraph.

Example substitution:
> **Before:** "The model is trained using backpropagation."
> **After:** "The model is trained using a step where errors are traced backward through each layer to adjust the model's internal dials (backpropagation)."

The substitutions are context-aware: the expansion is rewritten to fit the
sentence grammatically, not spliced in mechanically.

---

## Parse `$ARGUMENTS`

- **Local path** to a `-eli5.md` file → the target document.
- **No argument** → ask which file. Scan the current directory / `docs/papers/` for
  `*-eli5.md` files and show the list.
- **Unattended with no argument** → report the ambiguity; don't guess.

---

## Phase 1 — Propose term list (STOP here for approval)

Read the entire eli5 file. Identify every term that is still likely to be opaque
to a smart newcomer: field-specific vocabulary, acronyms, multi-word technical
phrases, named methods/architectures, statistical concepts. Do **not** include
ordinary English words or very common terms (e.g., "model", "data", "method"
used in plain senses).

For each candidate term, produce one plain-English expansion — a tight phrase or
clause that conveys the meaning and fits inline in a sentence. Expansions must:
- Be concise enough to read in-line without interrupting flow (aim for 1 clause,
  never more than 2 sentences)
- Capture the term's meaning accurately, not approximately
- Read naturally as a noun-phrase or clause so they can substitute the term
  grammatically

Present the list as a numbered table:

```
| # | Term (as it appears) | Proposed plain-English expansion |
|---|----------------------|----------------------------------|
| 1 | stochastic gradient descent | a method that nudges the model's settings using the error signal from a small random sample of training examples each step |
| 2 | …                    | …                                |
```

Then **STOP and ask Kyle**:

> "Here are the terms I found. Reply with the numbers you want to keep (e.g.
> '1, 3, 5'), or 'all' to keep the whole list, or 'none' to cancel. You can
> also correct any expansion by writing '4: [your preferred wording]'."

Do not proceed to Phase 2 until you have Kyle's response. This is a hard gate.

---

## Phase 2 — Substitution pass

Apply the approved glossary. Work section by section, one section at a time,
appending output to the target file (or a scratch accumulator — see Deliver).

For each section:
1. Read the section text.
2. For each paragraph that contains one or more approved terms:
   - Rewrite only the affected sentences so the term is replaced by its
     plain-English expansion, with the original term immediately after in
     parentheses, fitting the sentence grammatically.
   - Every other word in the paragraph is preserved exactly — do not simplify,
     rephrase, or restructure anything beyond the substitution site.
   - If a term appears multiple times in one sentence, annotate each occurrence.
3. For paragraphs with no approved terms: copy verbatim.

### Hard constraints for Phase 2

- **EVERY occurrence** of an approved term is substituted — not just the first
  per section or first in the document.
- **Grammar first.** If pasting the expansion directly produces an ungrammatical
  sentence, adjust surrounding words minimally to make it read cleanly — but the
  substitution itself (expansion + (original term)) must be present.
- **No other edits.** Don't take this pass as an opportunity to rephrase, simplify
  further, or fix anything else. The only diffs from the input file should be the
  term substitutions.
- **Equations, tables, figure placeholders:** pass through verbatim. Do not
  substitute inside equation blocks, table cells, or `[Figure N]` placeholders.
  Substitute inside the *plain-words gloss lines* if a term appears there.
- **Inline citations** (`[12]`, `(Smith et al., 2023)`): stay exactly where they are.
- **Header block at the top**: update (or append a note to) the header block
  indicating this is the glossed version and listing the substituted terms.

---

## Phase 3 — Verify

After the pass:
- Scan the output for each approved term's **exact string**. Verify no bare
  (un-annotated) occurrences remain. If any are found, go back and annotate them.
- Confirm paragraph counts per section match the input file (substitution never
  merges or splits paragraphs).
- Confirm headings are identical to the input file.

Report any discrepancies before delivering.

---

## Phase 4 — Deliver

- **Output path:** same directory as the input file, with `-glossed` appended to
  the slug before the extension: `<slug>-eli5-glossed.md`.
- **Header block addition:** add a "Glossed terms" section to the header block
  listing each substituted term and its expansion, for reference.
- **Git (when in a repo):** normal global workflow — feature branch, commit, push,
  PR, merge autonomously, brief Kyle — unless the project CLAUDE.md tightens it.
  Outside a repo: just write the file.
- **Send the file** to Kyle via SendUserFile.
- **Final report:** output path; number of terms substituted; per-term occurrence
  count; any spots where a bare term could not be cleanly substituted (flag with
  the section + reason).

---

## Definition of done

The glossed file exists at its output path with the updated header block; Phase 3
passed clean (no bare approved terms remain, paragraph counts and headings match
input); the file was sent via SendUserFile; the final report lists path, per-term
tallies, and every flag.
