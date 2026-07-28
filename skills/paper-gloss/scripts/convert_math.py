#!/usr/bin/env python3
"""Mechanically typeset the unambiguous Tier 1 math in a glossed HTML page.

Usage:
    python3 convert_math.py <file.html>            # dry run, writes nothing
    python3 convert_math.py <file.html> --apply
    python3 convert_math.py <file.html> --json out.json

Implements the Tier 1 half of `../references/math-rendering.md` — unicode plus
`<i>`/`<sub>`/`<sup>` inside a `<span class="math">`. Tier 2 (native MathML for
2-D layout) and Tier 3 (verbatim fallback) stay hand-authored; this script
refuses those and reports them so a human works the remainder.

**Deliberately timid.** It converts only what it fully understands, and a
refusal is a normal outcome rather than an error. Silence is not success: the
refusal list is the hand-authoring worklist, and `--apply` prints it.

Four safety rules, each learned from a way this went wrong on a real page:

  * Only the bytes between and including the `$` delimiters are replaced, so
    surrounding prose is untouched by construction.

  * Tag interiors are masked. An `<img alt="... $W_U J_\\ell$.">` is math
    inside an *attribute*; converting it emits `</span>." loading="lazy">` —
    markup nested in an attribute value, which silently breaks the tag.
    `check_math.py` cannot catch this, because its `scannable()` blanks tags
    before scanning, so attribute values are invisible to the gate.

  * A span whose ORIGINAL bytes contain `<` is refused, even though masking
    would make it look like plain text. That is how a `<button class=
    "gloss-term">` nested inside `$\\text{...}$` — the pre-contract wrapper's
    artifact — reaches a human instead of being deleted silently and
    unaccounted for in the term tally.

  * `$$…$$` display blocks are masked first. Otherwise a match starting at the
    second `$` converts a display block's interior and leaves stray `$`.
"""
import argparse
import json
import re
import sys
from collections import Counter

GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε",
    "varepsilon": "ε", "zeta": "ζ", "eta": "η", "theta": "θ", "iota": "ι",
    "kappa": "κ", "lambda": "λ", "mu": "μ", "nu": "ν", "xi": "ξ", "pi": "π",
    "rho": "ρ", "sigma": "σ", "tau": "τ", "upsilon": "υ", "phi": "φ",
    "varphi": "φ", "chi": "χ", "psi": "ψ", "omega": "ω", "ell": "ℓ",
    "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ", "Xi": "Ξ",
    "Pi": "Π", "Sigma": "Σ", "Upsilon": "Υ", "Phi": "Φ", "Psi": "Ψ",
    "Omega": "Ω",
}
RELATIONS = {
    "approx": "≈", "sim": "∼", "simeq": "≃", "propto": "∝", "equiv": "≡",
    "leq": "≤", "le": "≤", "geq": "≥", "ge": "≥", "neq": "≠", "ne": "≠",
    "ll": "≪", "gg": "≫", "pm": "±", "mp": "∓", "times": "×", "cdot": "·",
    "cdots": "⋯", "ldots": "…", "dots": "…", "in": "∈", "notin": "∉",
    "subset": "⊂", "subseteq": "⊆", "supset": "⊃", "cup": "∪", "cap": "∩",
    "emptyset": "∅", "forall": "∀", "exists": "∃", "to": "→",
    "rightarrow": "→", "leftarrow": "←", "mapsto": "↦", "implies": "⟹",
    "iff": "⟺", "infty": "∞", "partial": "∂", "nabla": "∇", "odot": "⊙",
    "oplus": "⊕", "otimes": "⊗", "langle": "⟨", "rangle": "⟩",
    "perp": "⊥", "circ": "∘", "star": "⋆", "cong": "≅",
}
CAL = {
    "A": "𝒜", "B": "ℬ", "C": "𝒞", "D": "𝒟", "E": "ℰ", "F": "ℱ", "G": "𝒢",
    "H": "ℋ", "I": "ℐ", "J": "𝒥", "K": "𝒦", "L": "ℒ", "M": "ℳ", "N": "𝒩",
    "O": "𝒪", "P": "𝒫", "Q": "𝒬", "R": "ℛ", "S": "𝒮", "T": "𝒯", "U": "𝒰",
    "V": "𝒱", "W": "𝒲", "X": "𝒳", "Y": "𝒴", "Z": "𝒵",
}
BB = {"R": "ℝ", "N": "ℕ", "Z": "ℤ", "Q": "ℚ", "C": "ℂ", "E": "𝔼", "P": "ℙ"}
UPRIGHT_WORD = re.compile(r"[A-Za-z0-9 ,.\-+]*")
SPACING_MACROS = {",", ";", ":", "!", " ", "quad", "qquad"}

# Anything needing two-dimensional layout or an accent is Tier 2 or Tier 3.
REFUSE_ALWAYS = (
    "\\frac", "\\begin", "\\end", "\\sum", "\\prod", "\\int", "\\oint",
    "\\sqrt", "\\left", "\\right", "\\big", "\\Big", "\\bigg", "\\Bigg",
    "\\hat", "\\bar", "\\tilde", "\\vec", "\\over", "\\matrix",
    "\\substack", "\\limits", "\\\\",
)

MASK = [
    re.compile(r"\$\$.*?\$\$", re.S),                                   # display first
    re.compile(r"<(script|style)\b[^>]*>.*?</\1\s*>", re.S | re.I),
    re.compile(r"<code\b[^>]*>.*?</code\s*>", re.S | re.I),
    re.compile(r"<h[1-6][^>]*>\s*(?:[\dIVXivx]+[.)]?\s*)?"
               r"(?:references|bibliography|works cited)\s*</h[1-6]\s*>.*", re.S | re.I),
    re.compile(r"<[^>]*>"),                                             # tag interiors LAST
]
MATH_RUN = re.compile(r"\$(?!\s)([^$\n]{1,300}?)(?<!\s)\$")

# `<` and `>` are deliberately absent: by the time spacing runs the string is
# HTML, so a literal `<` is only ever a tag delimiter and including it here
# would shred every <i> and <sub>. Those two relations arrive as entities and
# are handled by BINARY_ENTITY.
BINARY = set("=≤≥≠≈∼≃∝≡≪≫±∓×·∈∉⊂⊆⊃∪∩→←↦⟹⟺⊕⊗⊙∘⊥≅")
BINARY_ENTITY = re.compile(r"\s*(&lt;|&gt;)\s*")


class Refuse(Exception):
    """Raised anywhere in the walk to abandon a span to hand-authoring."""


def _blank(match):
    """Equal-length whitespace so offsets into the original stay valid."""
    return "".join("\n" if c == "\n" else " " for c in match.group(0))


def masked(html):
    out = html
    for pattern in MASK:
        out = pattern.sub(_blank, out)
    return out


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def read_group(s, i):
    """Read a `{...}` group, allowing nesting. Returns (inner, next_index)."""
    if i >= len(s) or s[i] != "{":
        raise Refuse("expected {")
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
    raise Refuse("unbalanced brace")


def render(s, upright=False):
    """Render a TeX fragment to HTML, or raise Refuse.

    `upright` is set for sub/superscript content. The contract sets script
    text upright — `<sub>vocab</sub>`, `<sub>Q</sub>`, `<sub>l−1</sub>` — so a
    script letter reads as a label rather than as a nested variable.
    """
    out, i, n = [], 0, len(s)
    while i < n:
        c = s[i]

        if c.isspace():
            out.append(" ")
            i += 1
            continue

        if c == "\\":
            m = re.match(r"\\([a-zA-Z]+)", s[i:])
            if m:
                name = m.group(1)
                i += m.end()
                # TeX consumes whitespace that terminates a control word, so
                # `\alpha x` is "αx" and `\langle v` is "⟨v" — not "α x".
                while i < n and s[i] == " ":
                    i += 1
                if name in ("text", "mathrm", "mathsf", "operatorname"):
                    inner, i = read_group(s, i)
                    if not UPRIGHT_WORD.fullmatch(inner):
                        raise Refuse("complex text argument")
                    out.append(esc(inner).replace("-", "−"))
                elif name == "mathcal":
                    inner, i = read_group(s, i)
                    if inner not in CAL:
                        raise Refuse("mathcal argument")
                    out.append(CAL[inner])
                elif name == "mathbb":
                    inner, i = read_group(s, i)
                    if inner not in BB:
                        raise Refuse("mathbb argument")
                    out.append(BB[inner])
                elif name in GREEK:
                    out.append(GREEK[name])
                elif name in RELATIONS:
                    out.append(RELATIONS[name])
                elif name in SPACING_MACROS:
                    out.append(" ")
                else:
                    raise Refuse("unknown macro " + name)
                continue
            nxt = s[i + 1] if i + 1 < n else ""
            if nxt in "{}%$&#_":
                out.append(esc(nxt))
                i += 2
                continue
            if nxt in ",;:! ":
                out.append(" ")
                i += 2
                continue
            raise Refuse("stray backslash")

        if c in "_^":
            if not out:
                raise Refuse("script with no base")
            if i + 1 >= n:
                raise Refuse("dangling script")
            if s[i + 1] == "{":
                inner, i = read_group(s, i + 1)
            else:
                m = re.match(r"\\[a-zA-Z]+|[A-Za-z0-9]", s[i + 1:])
                if not m:
                    raise Refuse("bad script argument")
                inner = m.group(0)
                i += 1 + m.end()
            tag = "sub" if c == "_" else "sup"
            out.append(f"<{tag}>{render(inner, upright=True).strip()}</{tag}>")
            continue

        if c.isalpha():
            out.append(c if upright else f"<i>{c}</i>")
            i += 1
            continue

        if c.isdigit():
            m = re.match(r"[0-9]+(?:\.[0-9]+)?", s[i:])
            out.append(m.group(0))          # digits upright
            i += m.end()
            continue

        if c == "-":
            out.append("−")                 # U+2212, not a hyphen
            i += 1
            continue
        if c == "'":
            out.append("′")
            i += 1
            continue
        if c in "+=<>()[]|/,.*:;":
            out.append(esc(c))
            i += 1
            continue

        raise Refuse("unhandled character " + repr(c))

    return "".join(out)


def convert_body(body):
    """Convert one `$…$` body to HTML, or return None to refuse it."""
    if "<" in body:
        return None                          # raw markup: human territory
    # `<` and `>` reach us entity-escaped, because the page escapes prose.
    # They are relations, not markup — decode, render, let esc() restore them.
    # This is what makes `$n_{\text{vocab}} > d_{\text{model}}$` convertible.
    decoded = (body.replace("&lt;", "<").replace("&gt;", ">")
                   .replace("&amp;", "&"))
    if "&" in decoded:
        return None                          # some other entity: refuse
    if any(t in decoded for t in REFUSE_ALWAYS):
        return None                          # Tier 2 / Tier 3
    try:
        out = render(decoded)
    except Refuse:
        return None
    out = re.sub(r"\s*([" + re.escape("".join(BINARY)) + r"])\s*", r" \1 ", out)
    out = BINARY_ENTITY.sub(r" \1 ", out)
    out = re.sub(r"\s+", " ", out)
    out = re.sub(r"([⟨(\[])\s+", r"\1", out)     # no padding just inside a fence
    out = re.sub(r"\s+([⟩)\]])", r"\1", out)
    out = out.strip()
    return out or None


def plan(html):
    """Return (edits, refusals) without touching anything.

    `edits` is a list of (start, end, replacement) against the ORIGINAL string.
    `refusals` is a Counter of the original `$…$` text left for a human.
    """
    scan = masked(html)
    edits, refused = [], Counter()
    for m in MATH_RUN.finditer(scan):
        original = html[m.start():m.end()]
        if "<" in original:
            refused[original] += 1
            continue
        rendered = convert_body(m.group(1))
        if rendered is None:
            refused[original] += 1
            continue
        edits.append((m.start(), m.end(), f'<span class="math">{rendered}</span>'))
    return edits, refused


def apply_edits(html, edits):
    """Apply right-to-left so earlier offsets stay valid."""
    for start, end, replacement in sorted(edits, reverse=True):
        html = html[:start] + replacement + html[end:]
    return html


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("html")
    ap.add_argument("--apply", action="store_true", help="write the file in place")
    ap.add_argument("--json", dest="json_out", default=None,
                    help="write the refusal worklist as JSON")
    args = ap.parse_args(argv)

    with open(args.html, encoding="utf-8") as fh:
        html = fh.read()

    edits, refused = plan(html)

    print(f"convertible : {len(edits)} spans", file=sys.stderr)
    print(f"refused     : {sum(refused.values())} spans "
          f"({len(refused)} unique) -> hand-author", file=sys.stderr)
    # Never silent: the refusal list IS the remaining work.
    for text, count in refused.most_common():
        print(f"  {count:3d}  {text[:110]}", file=sys.stderr)

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump({"file": args.html,
                       "converted": len(edits),
                       "refused": sum(refused.values()),
                       "worklist": [{"tex": t, "count": c}
                                    for t, c in refused.most_common()]},
                      fh, indent=2)
            fh.write("\n")

    if args.apply:
        with open(args.html, "w", encoding="utf-8") as fh:
            fh.write(apply_edits(html, edits))
        print(f"APPLIED {len(edits)} conversions", file=sys.stderr)
    else:
        print("(dry run — nothing written; pass --apply)", file=sys.stderr)

    # Exit non-zero while hand-authoring remains, so a caller cannot mistake a
    # partial pass for a finished one. `check_math.py` is still the gate.
    return 1 if refused else 0


if __name__ == "__main__":
    raise SystemExit(main())
