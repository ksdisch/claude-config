#!/usr/bin/env python3
"""Inject harvested figures into a paper-gloss HTML file as base64 data URIs.

Replaces each `.figure-placeholder` div with a real <figure>, and adds the
supporting CSS plus a singleton lightbox. Everything stays inline so the file
remains self-contained and publishable as an Artifact.
"""
import base64
import html as htmllib
import json
import os
import re

PLACEHOLDER = re.compile(
    r'<div class="figure-placeholder">(?P<body>.*?)</div>', re.S
)
# The separator is a literal em dash in the glossed output measured while
# writing the spec, but accept the entity-encoded and ASCII forms too — a
# silently unmatched lead-in would drop the figure with no error.
LEAD_IN = re.compile(
    r"^\s*\[Figure\s+(?P<num>\d+)\]\s*(?:&mdash;|&#8212;|&ndash;|&#8211;|—|–|--|-)\s*"
)
IMG_NOTE = re.compile(r'<span class="img-note">.*?</span>', re.S)
TAG = re.compile(r"<[^>]+>")

MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}

CSS = """
    .paper-figure {
      margin: 2rem auto;
      padding: 0;
      text-align: center;
    }
    .paper-figure img {
      max-width: 100%;
      height: auto;
      border: 1px solid var(--figure-border, rgba(128,128,128,0.3));
      border-radius: 6px;
      background: var(--figure-bg, transparent);
      cursor: zoom-in;
    }
    .paper-figure figcaption {
      margin-top: 0.6rem;
      font-size: 0.88rem;
      line-height: 1.5;
      color: var(--muted, #666);
      text-align: left;
    }
    .figure-lightbox {
      position: fixed;
      inset: 0;
      z-index: 1000;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--lightbox-bg, rgba(0,0,0,0.85));
      cursor: zoom-out;
    }
    .figure-lightbox[hidden] { display: none; }
    .figure-lightbox img {
      max-width: 95vw;
      max-height: 95vh;
      object-fit: contain;
    }
    .figure-lightbox-close {
      position: absolute;
      top: 1rem;
      right: 1rem;
      font-size: 1.6rem;
      line-height: 1;
      background: none;
      border: none;
      color: #fff;
      cursor: pointer;
    }
"""

# The gloss surfaces the lightbox must close, each with its own hook and its own
# DOM fallback so one missing hook cannot suppress the other's fallback. The ids
# and the backdrop class mirror the markup paper-gloss/SKILL.md specifies; the
# class is a belt-and-braces match for pages that style a backdrop without an id.
GLOSS_SURFACES = [
    {"hook": "closeGlossPopover", "ids": ["gloss-popover"], "classes": [], "expanded": []},
    {
        "hook": "closeGlossPanel",
        "ids": ["gloss-panel", "gloss-backdrop"],
        "classes": [".gloss-backdrop"],
        "expanded": ["gloss-panel-toggle"],
    },
]

LIGHTBOX_HTML = """
<div id="figure-lightbox" class="figure-lightbox" role="dialog" aria-modal="true" aria-label="Enlarged figure" hidden>
  <button class="figure-lightbox-close" aria-label="Close">&times;</button>
  <img alt="">
</div>
"""

LIGHTBOX_JS = """
<script>
(function () {
  var box = document.getElementById('figure-lightbox');
  if (!box) return;
  var img = box.querySelector('img');

  function close() {
    box.hidden = true;
    img.removeAttribute('src');
  }

  // Each gloss surface is closed independently: prefer the hook a
  // post-amendment paper-gloss run exports, else drive that surface's own
  // markup. A page that exports only one hook must still get the DOM fallback
  // for the other, or the lightbox opens on top of a live surface.
  var GLOSS_SURFACES = __GLOSS_SURFACES__;

  function closeGlossSurfaces() {
    GLOSS_SURFACES.forEach(function (surface) {
      if (typeof window[surface.hook] === 'function') { window[surface.hook](); return; }
      surface.ids.forEach(function (id) {
        var el = document.getElementById(id);
        if (el) el.hidden = true;
      });
      (surface.classes || []).forEach(function (sel) {
        document.querySelectorAll(sel).forEach(function (el) { el.hidden = true; });
      });
      (surface.expanded || []).forEach(function (id) {
        var el = document.getElementById(id);
        if (el) el.setAttribute('aria-expanded', 'false');
      });
    });
    document.querySelectorAll('.gloss-term--active').forEach(function (b) {
      b.classList.remove('gloss-term--active');
      b.setAttribute('aria-expanded', 'false');
    });
  }

  function open(source) {
    // Only one interactive surface at a time: close the gloss popover and panel.
    closeGlossSurfaces();
    img.src = source.src;
    img.alt = source.alt || '';
    box.hidden = false;
  }

  document.addEventListener('click', function (e) {
    var figImg = e.target.closest('.paper-figure img');
    if (figImg) { open(figImg); return; }
    if (!box.hidden && (e.target === box || e.target.closest('.figure-lightbox-close'))) close();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !box.hidden) close();
  });

  window.closeFigureLightbox = close;
})();
</script>
"""


def lightbox_js(surfaces=None):
    """Render the lightbox script with the gloss-surface table baked in."""
    table = json.dumps(surfaces if surfaces is not None else GLOSS_SURFACES)
    return LIGHTBOX_JS.replace("__GLOSS_SURFACES__", table)


def caption_of(body):
    """Strip the '[Figure N] — ' lead-in and any img-note span."""
    text = IMG_NOTE.sub("", body)
    text = LEAD_IN.sub("", text)
    text = TAG.sub("", text)
    return htmllib.unescape(text).strip()


def data_uri(path):
    ext = os.path.splitext(path)[1].lower()
    mime = MIME.get(ext, "application/octet-stream")
    with open(path, "rb") as fh:
        return f"data:{mime};base64," + base64.b64encode(fh.read()).decode("ascii")


def inject_html(doc, images):
    """Replace placeholder divs with real figures; add CSS and the lightbox."""
    images = {int(k): v for k, v in images.items()}
    injected = 0

    def repl(m):
        nonlocal injected
        body = m.group("body")
        num_m = LEAD_IN.match(body)
        if not num_m:
            return m.group(0)
        num = int(num_m.group("num"))
        path = images.get(num)
        if not path or not os.path.exists(path):
            return m.group(0)
        caption = caption_of(body)
        esc = htmllib.escape(caption, quote=True)
        injected += 1
        return (
            f'<figure class="paper-figure" id="figure-{num}">'
            f'<img src="{data_uri(path)}" alt="{esc}" loading="lazy">'
            f"<figcaption>{htmllib.escape(caption)}</figcaption>"
            f"</figure>"
        )

    out = PLACEHOLDER.sub(repl, doc)
    if injected == 0:
        return out

    if ".paper-figure {" not in out:
        out = out.replace("</style>", CSS + "\n</style>", 1)
    if 'id="figure-lightbox"' not in out:
        out = out.replace("</body>", LIGHTBOX_HTML + lightbox_js() + "\n</body>", 1)
    return out
