#!/usr/bin/env python3
"""Fail a glossed HTML page that still contains unrendered LaTeX.

Usage:
    python3 check_math.py <file.html> [-o hits.json]

Exits non-zero if any residual TeX survives into reader-visible text. See
`../references/math-rendering.md` for the conversion contract this enforces.

HTML only, deliberately. In the `paper-eli5` markdown, `$…$` is the *correct*
canonical form — it is the grammar `/paper-gloss` consumes, and GitHub renders
it. TeX is only a defect once it reaches the published page.

Two calibration decisions, both learned from how the original bug shipped:

  * A bare `$` is never a hit. Papers say "$5M in compute", and an inline pair
    is only credited when nothing follows the opening `$` or precedes the
    closing `$` but non-space — which is what rules out "we spent $5M and $8M".
    Tight ranges ("$5M–$8M") carry no such whitespace, so a digit-initial body
    ending on a separator is rejected as currency too. A gate that cries wolf
    gets ignored, and an ignored gate is why raw `$n_{\\text{vocab}}$` reached
    a reader in the first place.

  * A `<pre class="equation">` carrying no `data-math-verbatim="1"` IS scanned.
    The verbatim attribute is a deliberate, reported Tier-3 fallback; its
    absence means an equation nobody triaged. Exempting every `<pre>` would
    have let the exact construct this gate exists for pass silently.
"""
import argparse
import json
import re
import sys

# --- regions that are not reader-visible prose, blanked before scanning ---
# Each is replaced by equal-length whitespace so byte offsets, and therefore
# line numbers and context lines, stay true to the original file.
SCRIPT_STYLE = re.compile(r"<(script|style)\b[^>]*>.*?</\1\s*>", re.S | re.I)
VERBATIM = re.compile(
    r"<(\w+)\b[^>]*\bdata-math-verbatim\s*=\s*[\"']?1[\"']?[^>]*>.*?</\1\s*>", re.S | re.I
)
CODE = re.compile(r"<code\b[^>]*>.*?</code\s*>", re.S | re.I)
# A leading number is allowed because `paper-eli5` carries headings verbatim
# from the source, and papers routinely write "## 7. References". Without it
# the cut misses, the whole bibliography is scanned, and a citation title
# containing TeX ("On $L_p$ norms") fails a gate the operator cannot satisfy —
# constraint 4 forbids rewriting the references section. `convert_math.py`
# imports this pattern so both tools cut at exactly the same place.
REFERENCES = re.compile(
    r"<h[1-6][^>]*>\s*(?:[\dIVXivx]+[.)]?\s*)?"
    r"(?:references|bibliography|works cited)\s*</h[1-6]\s*>.*",
    re.S | re.I,
)
TAG = re.compile(r"<[^>]*>", re.S)

# --- residual-TeX detectors ---
BARE_MACROS = (
    "frac sqrt sum prod int oint lim log exp min max argmin argmax "
    "alpha beta gamma delta epsilon varepsilon zeta eta theta iota kappa lambda "
    "mu nu xi pi rho sigma tau upsilon phi varphi chi psi omega "
    "Gamma Delta Theta Lambda Xi Pi Sigma Upsilon Phi Psi Omega "
    "approx sim simeq propto equiv leq geq neq ll gg pm mp times cdot cdots ldots "
    "in notin subset subseteq supset cup cap emptyset forall exists "
    "to rightarrow leftarrow mapsto implies iff infty partial nabla "
    "odot oplus otimes langle rangle lVert rVert lvert rvert "
    "left right big Big bigg Bigg quad qquad displaystyle nonumber "
    "hat bar tilde vec dot ddot prime "
    "begin end operatorname limits"
).split()

DETECTORS = [
    ("display-dollars", re.compile(r"\$\$")),
    ("latex-delimiter", re.compile(r"\\[\(\)\[\]]")),
    ("braced-sub-superscript", re.compile(r"[_^]\s*\{")),
    ("macro-with-argument", re.compile(r"\\[a-zA-Z]+\s*\{")),
    ("tex-macro", re.compile(r"\\(?:%s)(?![a-zA-Z])" % "|".join(BARE_MACROS))),
]

# A closed pair on one line, with no whitespace immediately inside either
# delimiter. The whitespace rule is what makes spaced currency prose safe.
INLINE_DOLLAR = re.compile(r"\$(?!\s)([^$\n]{1,200}?)(?<!\s)\$")

# ...but a range written tight — "$5M–$8M", "$1M-$2M", "$100k/$1M" — has no
# whitespace inside either delimiter, so the rule above happily reads "5M–" as
# a math body. A money amount is digit-initial with an optional magnitude
# suffix, and no real expression *ends* on a separator; that pairing is the
# signature of two prices, not one expression.
CURRENCY_RANGE = re.compile(r"^\d[\d.,]*[a-zA-Z]{0,2}[-–—/,;]$")


def _blank(match):
    """Equal-length whitespace, newlines preserved so line numbers hold."""
    return "".join("\n" if c == "\n" else " " for c in match.group(0))


def scannable(html):
    """Blank every non-prose region, then every tag, leaving only text nodes.

    Order matters: `<script>` bodies and verbatim blocks go first, because
    their contents can contain markup that would otherwise confuse the tag
    pass, and the References cut must happen while its heading tags are still
    intact to be found.
    """
    for pattern in (SCRIPT_STYLE, VERBATIM, CODE, REFERENCES):
        html = pattern.sub(_blank, html)
    return TAG.sub(_blank, html)


def looks_like_math(body):
    """Is the inside of a `$…$` pair plausibly math rather than prose?

    A backslash, subscript, or superscript settles it — a TeX signal always
    wins, so this never suppresses a real hit. Failing that, a tight currency
    range is rejected outright, and otherwise only a short body containing a
    letter counts — that admits `$k$` and `$W$` while rejecting `$100$`, which
    in running prose is far more likely money than a lone numeric constant.
    """
    if any(c in body for c in "\\_^"):
        return True
    if CURRENCY_RANGE.match(body):
        return False
    return len(body) <= 6 and any(c.isalpha() for c in body)


def find_hits(html):
    """Return merged residual-TeX spans, each with line number and context.

    Detectors overlap heavily by design — `$n_{\\text{vocab}}$` trips four of
    them at once. Overlapping spans are merged so the reported count is the
    number of expressions actually left unrendered, not the number of regex
    matches. Reporting matches would inflate one missed variable into four.
    """
    text = scannable(html)
    spans = []
    for kind, pattern in DETECTORS:
        for m in pattern.finditer(text):
            spans.append([m.start(), m.end(), {kind}])
    for m in INLINE_DOLLAR.finditer(text):
        if looks_like_math(m.group(1)):
            spans.append([m.start(), m.end(), {"inline-dollars"}])

    spans.sort(key=lambda s: (s[0], s[1]))
    merged = []
    for start, end, kinds in spans:
        if merged and start < merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
            merged[-1][2] |= kinds
        else:
            merged.append([start, end, set(kinds)])

    lines = html.splitlines()
    hits = []
    for start, end, kinds in merged:
        line_no = text.count("\n", 0, start) + 1
        context = lines[line_no - 1].strip() if line_no <= len(lines) else ""
        hits.append(
            {
                "line": line_no,
                "kinds": sorted(kinds),
                "snippet": text[start:end].strip(),
                "context": context[:200],
            }
        )
    return hits


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("html")
    ap.add_argument("-o", "--out", default=None, help="write the hit list as JSON")
    args = ap.parse_args(argv)

    with open(args.html, encoding="utf-8") as fh:
        html = fh.read()

    hits = find_hits(html)
    verbatim = len(VERBATIM.findall(html))
    payload = {"file": args.html, "found": len(hits), "verbatim_blocks": verbatim, "hits": hits}

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, indent=2) + "\n")

    for h in hits:
        print(
            f"{args.html}:{h['line']}: unrendered math ({', '.join(h['kinds'])}): "
            f"{h['snippet']}\n    {h['context']}",
            file=sys.stderr,
        )
    # The count is of hits actually found, never of anything declared upfront.
    print(
        f"{len(hits)} unrendered, {verbatim} verbatim fallback"
        f"{'' if verbatim == 1 else 's'}",
        file=sys.stderr,
    )
    return 1 if hits else 0


if __name__ == "__main__":
    raise SystemExit(main())
