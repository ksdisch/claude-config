# Math rendering contract

How LaTeX from a `paper-eli5` markdown becomes typeset notation in a published
HTML artifact. Loaded on demand by `/paper-gloss` (Phase 2 and RETROFIT) and cited
by `/paper-figures` for its re-publish verify — **one copy, two consumers**. Amend
here, never fork a second copy into a SKILL.md.

## Why this file exists

Artifacts must be self-contained: no CDN, no external `src=`, no `@import`. That
rules out loading KaTeX or MathJax the ordinary way. It does **not** rule out
rendering math — it rules out rendering it with someone else's JavaScript. Every
tier below is plain markup the browser already knows how to lay out.

The prior behavior was to ship the TeX as literal characters, so a reader saw
`$n_{\text{vocab}}$` in the middle of a sentence. That is the bug this contract
closes.

---

## The ladder

Work down it. Use the **first** tier that renders the expression faithfully.

### Tier 1 — unicode + HTML (the default)

All inline math, and any display equation that is a single line of symbols. Wrap
every converted expression in `<span class="math">…</span>`.

| TeX | HTML | Renders |
|---|---|---|
| `$k$` | `<i>k</i>` | *k* |
| `$n_{\text{vocab}}$` | `<i>n</i><sub>vocab</sub>` | *n*<sub>vocab</sub> |
| `$d_{\text{model}}$` | `<i>d</i><sub>model</sub>` | *d*<sub>model</sub> |
| `$h_{l-1}$` | `<i>h</i><sub>l−1</sub>` | *h*<sub>l−1</sub> |
| `$x^2$` | `<i>x</i><sup>2</sup>` | *x*² |
| `$W_Q^{(l)}$` | `<i>W</i><sub>Q</sub><sup>(l)</sup>` | *W*<sub>Q</sub><sup>(l)</sup> |
| `$n_{\text{vocab}} > d_{\text{model}}$` | `<i>n</i><sub>vocab</sub> &gt; <i>d</i><sub>model</sub>` | *n*<sub>vocab</sub> > *d*<sub>model</sub> |
| `$\text{attn}(h)$` | `attn(<i>h</i>)` | attn(*h*) |
| `$\mathbb{R}^d$` | `ℝ<sup>d</sup>` | ℝ<sup>d</sup> |
| `$\|x\|$` | `‖<i>x</i>‖` | ‖*x*‖ |

Symbol table — use the character, never the macro name:

| Macro | Char | Macro | Char | Macro | Char |
|---|---|---|---|---|---|
| `\alpha \beta \gamma \delta` | α β γ δ | `\epsilon \theta \lambda \mu` | ε θ λ μ | `\pi \sigma \phi \psi` | π σ φ ψ |
| `\Delta \Sigma \Omega \Lambda` | Δ Σ Ω Λ | `\approx \sim \propto` | ≈ ∼ ∝ | `\leq \geq \neq` | ≤ ≥ ≠ |
| `\in \notin \subset` | ∈ ∉ ⊂ | `\to \mapsto \implies` | → ↦ ⟹ | `\ll \gg` | ≪ ≫ |
| `\times \cdot \pm` | × · ± | `\infty \partial \nabla` | ∞ ∂ ∇ | `\odot \oplus \otimes` | ⊙ ⊕ ⊗ |
| `\sum \prod \int` | ∑ ∏ ∫ | `\forall \exists` | ∀ ∃ | `\langle \rangle` | ⟨ ⟩ |

Typography rules:

- **Single-letter variables are italic** (`<i>`). This is what distinguishes *n*
  the variable from "n" the word, and it is the one cue that makes unicode math
  read as math.
- **Multi-letter names are upright.** `\text{}`, `\mathrm{}`, `\operatorname{}`,
  and function names (`attn`, `softmax`, `log`, `max`, `argmin`) never get `<i>`.
  Subscript words from `\text{vocab}` are upright too — `<sub>vocab</sub>`, not
  `<sub><i>vocab</i></sub>`.
- **Minus is U+2212 (`−`), not a hyphen.** `h_{l-1}` → `<sub>l−1</sub>`.
- **Digits are upright.** Never `<i>2</i>`.
- Thin-space around binary relations is the browser's job; don't hand-kern.

### Tier 2 — native MathML

Only when the expression needs two-dimensional layout: fractions, sums or
integrals with limits, matrices, roots, stacked accents. Anything Tier 1 can
express, Tier 1 should express — MathML is heavier markup and its typography is
weaker than a plain `<sub>`.

```html
<div class="scroll-x">
  <math display="block">
    <mrow>
      <mi>a</mi><mo>=</mo>
      <munderover><mo>∑</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow><mi>k</mi></munderover>
      <msub><mi>c</mi><mi>i</mi></msub>
      <msub><mi>v</mi><mi>i</mi></msub>
    </mrow>
  </math>
</div>
```

- `<mi>` variables (auto-italic), `<mn>` numbers, `<mo>` operators, `<mtext>` words.
- `<mfrac>`, `<msub>`, `<msup>`, `<msubsup>`, `<munderover>`, `<msqrt>`, `<mtable>`.
- Native in every current browser. **No JS, no webfont, no external asset** — it
  costs nothing against the page-size budget and inherits `currentColor`, so it
  themes for free in both light and dark.
- Keep it inside the existing `<div class="scroll-x">`. A wide equation must
  scroll in its own container; the page itself never scrolls sideways.

### Tier 3 — verbatim fallback

When the math is too complex to render faithfully — dense multi-line derivations,
commutative diagrams, heavy custom macros — keep the original TeX:

```html
<pre class="equation" data-math-verbatim="1">\mathcal{L} = \mathbb{E}_{x\sim D}\left[ … \right]</pre>
```

`data-math-verbatim="1"` is **required**, and it is load-bearing twice over: it is
how `check_math.py` tells a deliberate fallback apart from math that was missed,
and it is what the final report counts.

This tier is `paper-eli5` constraint 5 ("NEVER INVENT") applied to math. A
silently mangled equation is worse than an honest monospace one — a reader can
still read TeX, but cannot detect a subscript that moved. **Falling back is
always allowed; falling back without the attribute and the report line is not.**

---

## Two rules that collide with existing spec text

### Escaping

`paper-gloss/SKILL.md` requires literal `<`, `>`, `&` in source prose to be
entity-escaped. That rule is about **prose text**. Math spans are authored markup:

- `<span class="math">`, `<i>`, `<sub>`, `<sup>`, `<math>` and its children are
  emitted as **live tags**.
- Any `<`, `>`, `&` appearing *inside* math content is escaped — `&lt;`, `&gt;`,
  `&amp;`.
- Prefer the real relation character where one exists: `\leq` → `≤`, not `&lt;=`.

### Term-wrapping

`d_{\text{model}}` renders as `<sub>model</sub>`. If "model" is an approved gloss
term, the term-wrapper would inject a `<button class="gloss-term">` **inside a
subscript** — breaking the notation and inflating the occurrence tally.

`.math` spans and `<math>` elements join equations, tables, figure captions,
citations, and references in the never-wrap bucket. Verified in Phase 3 by the
existing non-prose-passthrough check.

---

## CSS

Add to the single inline `<style>`, every value through a CSS variable like the
rest of the page:

```css
.math { white-space: nowrap; }          /* a variable never wraps mid-symbol */
.math i { font-style: italic; }
sub, sup { font-size: 0.75em; line-height: 0; position: relative; }
sub { bottom: -0.25em; }
sup { top: -0.5em; }
math { font-size: 1.05em; color: inherit; }
```

`line-height: 0` on `sub`/`sup` is what stops a subscript from opening up the
leading of any paragraph that contains one — without it, prose with inline math
develops visibly uneven line spacing.

---

## The mechanical pass

```bash
python3 scripts/convert_math.py <file.html>            # dry run: print the worklist
python3 scripts/convert_math.py <file.html> --apply
```

Implements Tier 1 only, and only where it is certain. It reports three
outcomes:

- **converted** — unambiguous Tier 1.
- **refused** — the hand-authoring worklist: every `$$…$$` display block,
  anything needing 2-D layout, any span containing a `.gloss-term` button, and
  any bare amount (`$100$`, `$0.5$`) whose reading as money or as a constant a
  tool cannot settle. It exits non-zero while refusals remain, so a partial
  pass cannot be mistaken for a finished one.
- **skipped** — spans that are definitely money, like the tight range
  `$5-$10`. Printed, but deliberately outside the worklist and the exit code:
  filing a price as "typeset this by the ladder" invites the operator to
  mangle it by hand. **This is the only bucket with no downstream detector** —
  the gate cannot see these either — so read it, and treat a long one as a
  sign the calibration is off.

The dividing line is *certainty*, not category. Anything ambiguous is refused
into the worklist, where a human sees it; only an unmistakable price is
dropped from the exit code.

It never scans a tag interior. Math inside an attribute (`<img alt="… $x$">`)
is reader-facing only as plain text, and injecting a `<span>` there breaks the
tag — a failure the gate below cannot see, because it blanks tags before
scanning. That also means **attribute TeX is out of scope for both tools**: if
a page carries math in `alt` text, say so rather than assuming a clean gate
means a clean page.

## The gate

```bash
python3 scripts/check_math.py <file.html>        # from the paper-gloss skill dir
```

Exits non-zero and prints every residual-TeX hit with its line number and
surrounding context. It must exit clean before any publish or re-publish.

Scanned: all body text, including `<pre class="equation">`. A `<pre>` carrying no
`data-math-verbatim="1"` is an equation nobody triaged, and that is exactly what
this gate is for.

Not scanned, by design: `<code>` elements, `<script>`/`<style>` bodies, anything
marked `data-math-verbatim="1"`, and everything from the References heading to the
end of the document. A bare `$` is never a hit on its own — papers say "$5M in
compute", and a tight range like "$5M–$8M" is rejected too (a digit-initial body
ending on a separator is currency, not an expression). A gate that cries wolf
gets ignored, which is the same failure mode that let the original bug ship.
