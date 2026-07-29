(function () {
  'use strict';
  if (window.__pgAnnotInit) return;
  window.__pgAnnotInit = true;

  /* ---------- config ---------- */
  var SLUG = document.body.getAttribute('data-pg-slug') || 'paper';
  var KEY = 'pg-annotations:' + SLUG;
  var CTX = 32;
  var EXCLUDE = 'script,style,.math,math,pre.equation,' +
    '#gloss-popover,#gloss-panel,#gloss-backdrop,#figure-lightbox,.pg-annot-ui';

  /* ---------- storage ---------- */
  function load() {
    try {
      var raw = localStorage.getItem(KEY);
      if (raw) {
        var p = JSON.parse(raw);
        if (p && p.v === 1 && Array.isArray(p.annotations)) return p;
      }
    } catch (e) { /* private mode or corrupt payload: start empty */ }
    return { v: 1, slug: SLUG, title: document.title, annotations: [] };
  }
  var storageOk = true;
  function persist() {
    // Never silent: partitioned iframe storage is a live path, and a badge
    // that counts up while nothing persists is the lie D3 forbids.
    try {
      localStorage.setItem(KEY, JSON.stringify(store));
      storageOk = true;
    } catch (e) {
      storageOk = false;
    }
    updateHint();
  }
  function updateHint() {
    var h = panel && panel.querySelector('.pg-annot-hint');
    if (!h) return;
    h.textContent = storageOk
      ? 'Notes live in this browser only — export to keep them safe.'
      : '⚠️ Not saved in this browser (storage unavailable) — export before you close this tab.';
  }
  var store = load();
  var posCache = {};   // id -> {bi, start} for document-order sorting
  var orphans = [];    // ids that failed to re-anchor this session

  function newId() {
    return 'a-' + Date.now().toString(36) + '-' +
      Math.random().toString(36).slice(2, 6);
  }
  function byId(id) {
    for (var i = 0; i < store.annotations.length; i++) {
      if (store.annotations[i].id === id) return store.annotations[i];
    }
    return null;
  }

  /* ---------- anchoring ---------- */
  function allBlocks() {
    return Array.prototype.slice.call(
      document.querySelectorAll('[data-pg-block]'));
  }
  function blockOf(node) {
    var el = node.nodeType === 1 ? node : node.parentElement;
    return el ? el.closest('[data-pg-block]') : null;
  }
  function sectionOf(block) {
    var bs = allBlocks(), i = bs.indexOf(block);
    for (var k = i; k >= 0; k--) {
      if (/^H[1-6]$/.test(bs[k].tagName)) return bs[k].textContent.trim();
    }
    return '';
  }
  function offsetIn(block, container, offset) {
    var r = document.createRange();
    r.selectNodeContents(block);
    r.setEnd(container, offset);
    return r.toString().length;
  }
  function captureTarget(range) {
    var b1 = blockOf(range.startContainer);
    var b2 = blockOf(range.endContainer);
    if (!b1 || b1 !== b2) return null;   // v1: single-block highlights only
    var text = b1.textContent;
    var start = offsetIn(b1, range.startContainer, range.startOffset);
    var exact = range.toString();
    if (!exact.trim()) return null;
    return {
      pid: b1.getAttribute('data-pg-block'),
      exact: exact,
      prefix: text.slice(Math.max(0, start - CTX), start),
      suffix: text.slice(start + exact.length, start + exact.length + CTX),
      offset: start,
      section: sectionOf(b1)
    };
  }
  function indexesOf(hay, needle) {
    var out = [], i = hay.indexOf(needle);
    while (i !== -1) { out.push(i); i = hay.indexOf(needle, i + 1); }
    return out;
  }
  function scoreAt(text, i, a) {
    var s = 0;
    if (a.prefix &&
        text.slice(Math.max(0, i - a.prefix.length), i) === a.prefix) s += 2;
    if (a.suffix &&
        text.slice(i + a.exact.length,
                   i + a.exact.length + a.suffix.length) === a.suffix) s += 2;
    if (typeof a.offset === 'number') {
      s -= Math.min(1, Math.abs(i - a.offset) / 1000);
    }
    return s;
  }
  function locate(a) {
    var candidates = [];
    var own = a.pid &&
      document.querySelector('[data-pg-block="' + a.pid + '"]');
    if (own) candidates.push(own);
    allBlocks().forEach(function (b) { if (b !== own) candidates.push(b); });
    for (var k = 0; k < candidates.length; k++) {
      var b = candidates[k], text = b.textContent;
      var hits = indexesOf(text, a.exact);
      if (!hits.length) continue;
      var best = hits[0], bestScore = -Infinity;
      for (var h = 0; h < hits.length; h++) {
        var s = scoreAt(text, hits[h], a);
        if (s > bestScore) { bestScore = s; best = hits[h]; }
      }
      return { block: b, start: best, end: best + a.exact.length };
    }
    return null;
  }

  /* ---------- mark rendering ---------- */
  function markRange(block, start, end, id, noted) {
    var walker = document.createTreeWalker(block, NodeFilter.SHOW_TEXT, null);
    var pos = 0, node, jobs = [];
    while ((node = walker.nextNode())) {
      var len = node.nodeValue.length;
      var nStart = pos, nEnd = pos + len;
      pos = nEnd;
      if (nEnd <= start || nStart >= end) continue;
      if (node.parentElement && node.parentElement.closest(EXCLUDE)) continue;
      jobs.push({
        node: node,
        from: Math.max(start, nStart) - nStart,
        to: Math.min(end, nEnd) - nStart
      });
    }
    jobs.forEach(function (j) {
      var target = j.node;
      if (j.from > 0) target = target.splitText(j.from);
      if (j.to - j.from < target.nodeValue.length) target.splitText(j.to - j.from);
      var m = document.createElement('mark');
      m.className = 'pg-hl' + (noted ? ' pg-hl--noted' : '');
      m.setAttribute('data-annot-id', id);
      target.parentNode.insertBefore(m, target);
      m.appendChild(target);
    });
    return jobs.length;
  }
  function unmark(id) {
    var marks = document.querySelectorAll(
      'mark.pg-hl[data-annot-id="' + id + '"]');
    Array.prototype.forEach.call(marks, function (m) {
      var parent = m.parentNode;
      while (m.firstChild) parent.insertBefore(m.firstChild, m);
      parent.removeChild(m);
      parent.normalize();
    });
  }
  function renderAnnotation(a, blockIndex) {
    var loc = locate(a);
    if (!loc) { orphans.push(a.id); return; }
    var made = markRange(loc.block, loc.start, loc.end, a.id, !!a.note);
    if (!made) {
      // quote matched, but every segment sits in excluded content (math,
      // chrome): no mark exists to jump to, so file it as unanchored rather
      // than letting a ghost row with a dead Jump button count as anchored
      orphans.push(a.id);
      return;
    }
    var marker = loc.block.getAttribute('data-pg-block');
    if (a.pid !== marker) a.pid = marker;  // heal drift
    posCache[a.id] = { bi: blockIndex.get(loc.block), start: loc.start };
  }
  function renderAll() {
    Array.prototype.forEach.call(
      document.querySelectorAll('mark.pg-hl'),
      function (m) {
        var parent = m.parentNode;
        while (m.firstChild) parent.insertBefore(m.firstChild, m);
        parent.removeChild(m);
      });
    posCache = {};
    orphans = [];
    var blockIndex = new Map();
    allBlocks().forEach(function (b, i) { blockIndex.set(b, i); });
    store.annotations.forEach(function (a) { renderAnnotation(a, blockIndex); });
    persist();  // pids may have healed
  }
  function ordered() {
    return store.annotations.slice().sort(function (x, y) {
      var px = posCache[x.id], py = posCache[y.id];
      if (px && py) return (px.bi - py.bi) || (px.start - py.start);
      if (px) return -1;
      if (py) return 1;
      return (x.created || '').localeCompare(y.created || '');
    });
  }

  /* ---------- surface coordination ---------- */
  function closeOtherSurfaces() {
    // Prefer the hooks a post-amendment page exports; the six retrofit
    // targets mostly predate them (five export nothing, jacobian-lens only
    // closeGlossSurfaces + closeFigureLightbox), so also drive the surfaces'
    // own markup by id — same layered pattern as paper-figures' lightbox.
    ['closeGlossSurfaces', 'closeGlossPopover', 'closeGlossPanel',
     'closeFigureLightbox'].forEach(function (fn) {
      if (typeof window[fn] === 'function') window[fn]();
    });
    ['gloss-popover', 'gloss-panel', 'gloss-backdrop', 'figure-lightbox']
      .forEach(function (id) {
        var n = document.getElementById(id);
        if (n && !n.hidden) n.hidden = true;
      });
    var gt = document.getElementById('gloss-panel-toggle');
    if (gt) gt.setAttribute('aria-expanded', 'false');
    // sweep the active-term state too (same as paper-figures' fallback) —
    // hiding the popover alone leaves .gloss-term--active desynced
    Array.prototype.forEach.call(
      document.querySelectorAll('.gloss-term--active'),
      function (b) {
        b.classList.remove('gloss-term--active');
        b.setAttribute('aria-expanded', 'false');
      });
  }
  function closeAnnotationUI() {
    hideToolbar();
    closeEditor(false);
    closePanel();
    fallback.hidden = true;
  }
  window.closeAnnotationUI = closeAnnotationUI;

  /* ---------- UI construction ---------- */
  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html !== undefined) e.innerHTML = html;
    return e;
  }

  var toolbar = el('div', 'pg-annot-toolbar pg-annot-ui',
    '<button type="button" data-act="hl">Highlight</button>' +
    '<button type="button" data-act="note">Note</button>');
  toolbar.hidden = true;

  var editor = el('div', 'pg-annot-editor pg-annot-ui',
    '<div class="pg-annot-editor-quote"></div>' +
    '<textarea rows="4" placeholder="Add a note…"></textarea>' +
    '<div class="pg-annot-actions">' +
    '<button type="button" data-act="delete">Delete</button>' +
    '<button type="button" data-act="cancel">Cancel</button>' +
    '<button type="button" data-act="save">Save</button></div>');
  editor.hidden = true;

  var toggle = el('button', 'pg-annot-toggle pg-annot-ui');
  toggle.type = 'button';
  toggle.setAttribute('aria-expanded', 'false');

  var backdrop = el('div', 'pg-annot-backdrop pg-annot-ui');
  backdrop.hidden = true;

  var panel = el('aside', 'pg-annot-panel pg-annot-ui',
    '<button type="button" class="pg-annot-panel-close" aria-label="Close">×</button>' +
    '<h2>Annotations</h2>' +
    '<div class="pg-annot-hint">Notes live in this browser only — export to keep them safe.</div>' +
    '<div class="pg-annot-actions" style="justify-content:flex-start">' +
    '<button type="button" data-act="export-md">Export Markdown</button>' +
    '<button type="button" data-act="export-json">Export JSON</button>' +
    '<button type="button" data-act="import">Import</button>' +
    '<input type="file" accept=".json,application/json" hidden></div>' +
    '<div class="pg-annot-status"></div>' +
    '<ol class="pg-annot-list"></ol>' +
    '<div class="pg-annot-orphans" hidden><h3>Unanchored</h3><ol></ol></div>');
  panel.hidden = true;

  var fallback = el('div', 'pg-annot-fallback pg-annot-ui',
    '<p class="pg-annot-fallback-msg"></p>' +
    '<textarea readonly></textarea>' +
    '<div class="pg-annot-actions">' +
    '<button type="button" data-act="copy">Copy</button>' +
    '<button type="button" data-act="close">Close</button></div>');
  fallback.hidden = true;

  [toolbar, editor, toggle, backdrop, panel, fallback].forEach(function (n) {
    document.body.appendChild(n);
  });

  function updateBadge() {
    toggle.textContent = '✏️ Notes (' + store.annotations.length + ')';
  }
  function status(msg) {
    panel.querySelector('.pg-annot-status').textContent = msg || '';
  }

  /* ---------- toolbar ---------- */
  function hideToolbar() { toolbar.hidden = true; }
  function placeAt(node, rect) {
    node.style.left = Math.max(8, Math.min(
      window.scrollX + rect.left,
      window.scrollX + document.documentElement.clientWidth - node.offsetWidth - 8
    )) + 'px';
    node.style.top = (window.scrollY + rect.top - node.offsetHeight - 8) + 'px';
  }
  function maybeShowToolbar() {
    var sel = window.getSelection();
    if (!sel || sel.rangeCount === 0 || sel.isCollapsed) { hideToolbar(); return; }
    var range = sel.getRangeAt(0);
    var anchor = range.startContainer.nodeType === 1 ?
      range.startContainer : range.startContainer.parentElement;
    if (anchor && anchor.closest('.pg-annot-ui')) return;
    if (!captureTarget(range)) { hideToolbar(); return; }
    toolbar.hidden = false;
    placeAt(toolbar, range.getBoundingClientRect());
  }
  document.addEventListener('mouseup', function () {
    setTimeout(maybeShowToolbar, 0);
  });
  // Touch selection (long-press handles) and keyboard selection (Shift+arrows)
  // don't reliably emit mouseup — selectionchange is the path that covers them.
  var selTimer = null;
  document.addEventListener('selectionchange', function () {
    clearTimeout(selTimer);
    selTimer = setTimeout(maybeShowToolbar, 250);
  });
  toolbar.addEventListener('mousedown', function (e) { e.preventDefault(); });
  toolbar.addEventListener('click', function (e) {
    var btn = e.target.closest('button');
    if (!btn) return;
    var sel = window.getSelection();
    if (!sel || sel.rangeCount === 0) { hideToolbar(); return; }
    var target = captureTarget(sel.getRangeAt(0));
    hideToolbar();
    if (!target) return;
    sel.removeAllRanges();
    var a = {
      id: newId(), exact: target.exact, prefix: target.prefix,
      suffix: target.suffix, pid: target.pid, offset: target.offset,
      note: '', section: target.section,
      created: new Date().toISOString()
    };
    store.annotations.push(a);
    persist();
    renderAll();
    updateBadge();
    if (btn.getAttribute('data-act') === 'note') openEditor(a.id, true);
  });

  /* ---------- editor ---------- */
  var editorState = { id: null, fresh: false };
  function openEditor(id, fresh) {
    var a = byId(id);
    if (!a) return;
    closeOtherSurfaces();
    closePanel();
    hideToolbar();
    editorState = { id: id, fresh: !!fresh };
    editor.querySelector('.pg-annot-editor-quote').textContent =
      a.exact.length > 200 ? a.exact.slice(0, 200) + '…' : a.exact;
    editor.querySelector('textarea').value = a.note || '';
    editor.hidden = false;
    var m = document.querySelector('mark.pg-hl[data-annot-id="' + id + '"]');
    if (m) placeAt(editor, m.getBoundingClientRect());
    else { editor.style.left = '50%'; editor.style.top = (window.scrollY + 120) + 'px'; }
    editor.querySelector('textarea').focus();
  }
  function removeAnnotation(id) {
    unmark(id);
    store.annotations = store.annotations.filter(function (a) { return a.id !== id; });
    delete posCache[id];
    persist();
    updateBadge();
  }
  function closeEditor(commit) {
    // Closing without commit DISMISSES — it never deletes. "Highlight →
    // start a note → click a jargon term to check it" is the page's most
    // natural gesture and must not destroy the highlight; only the explicit
    // Cancel button discards a fresh one (below).
    if (editor.hidden) return;
    var a = byId(editorState.id);
    if (a && commit) {
      a.note = editor.querySelector('textarea').value.trim();
      persist();
      renderAll();
    }
    editor.hidden = true;
    editorState = { id: null, fresh: false };
  }
  editor.addEventListener('click', function (e) {
    var btn = e.target.closest('button');
    if (!btn) return;
    var act = btn.getAttribute('data-act');
    if (act === 'save') closeEditor(true);
    else if (act === 'cancel') {
      var wasFresh = editorState.fresh, freshId = editorState.id;
      closeEditor(false);
      var fa = byId(freshId);
      if (wasFresh && fa && !fa.note) removeAnnotation(freshId);
    }
    else if (act === 'delete') {
      var id = editorState.id;
      editorState = { id: null, fresh: false };
      editor.hidden = true;
      removeAnnotation(id);
      refreshPanelList();
    }
  });

  /* ---------- panel ---------- */
  function openPanel() {
    closeOtherSurfaces();
    hideToolbar();
    closeEditor(false);
    refreshPanelList();
    panel.hidden = false;
    backdrop.hidden = false;
    // hide the toggle while the panel is open: its z-index sits below the
    // lightbox and the backdrop by design, so it must not be the close control
    toggle.hidden = true;
    toggle.setAttribute('aria-expanded', 'true');
  }
  function closePanel() {
    panel.hidden = true;
    backdrop.hidden = true;
    toggle.hidden = false;
    toggle.setAttribute('aria-expanded', 'false');
  }
  function itemFor(a, anchored) {
    var li = document.createElement('li');
    var sec = el('div', 'pg-annot-item-section');
    sec.textContent = a.section || '';
    var q = el('blockquote', 'pg-annot-item-quote');
    q.textContent = a.exact.length > 140 ? a.exact.slice(0, 140) + '…' : a.exact;
    var note = el('div', 'pg-annot-item-note');
    note.textContent = a.note || '';
    var actions = el('div', 'pg-annot-item-actions');
    if (anchored) {
      var jump = el('button', '', 'Jump'); jump.type = 'button';
      jump.addEventListener('click', function () {
        closePanel();
        var m = document.querySelector('mark.pg-hl[data-annot-id="' + a.id + '"]');
        if (!m) return;
        m.scrollIntoView({ block: 'center' });
        m.classList.add('pg-hl--flash');
        setTimeout(function () { m.classList.remove('pg-hl--flash'); }, 1300);
      });
      actions.appendChild(jump);
    }
    var edit = el('button', '', 'Edit'); edit.type = 'button';
    edit.addEventListener('click', function () { openEditor(a.id, false); });
    var del = el('button', '', 'Delete'); del.type = 'button';
    del.addEventListener('click', function () {
      removeAnnotation(a.id);
      refreshPanelList();
    });
    actions.appendChild(edit);
    actions.appendChild(del);
    li.appendChild(sec); li.appendChild(q);
    if (a.note) li.appendChild(note);
    li.appendChild(actions);
    return li;
  }
  function refreshPanelList() {
    var list = panel.querySelector('.pg-annot-list');
    var orphanBox = panel.querySelector('.pg-annot-orphans');
    var orphanList = orphanBox.querySelector('ol');
    list.innerHTML = '';
    orphanList.innerHTML = '';
    ordered().forEach(function (a) {
      if (orphans.indexOf(a.id) === -1) list.appendChild(itemFor(a, true));
      else orphanList.appendChild(itemFor(a, false));
    });
    orphanBox.hidden = orphanList.children.length === 0;
  }
  toggle.addEventListener('click', function () {
    if (panel.hidden) openPanel(); else closePanel();
  });
  panel.querySelector('.pg-annot-panel-close')
    .addEventListener('click', closePanel);
  backdrop.addEventListener('click', closePanel);

  /* ---------- export / import ---------- */
  function exportPayload() {
    return {
      v: 1, kind: 'paper-gloss-annotations', slug: SLUG,
      title: store.title || document.title, url: location.href,
      exported: new Date().toISOString(), annotations: ordered()
    };
  }
  function toMarkdown(p) {
    var lines = [
      '---',
      'paper: "' + p.title.replace(/"/g, '\\"') + '"',
      'url: "' + p.url + '"',
      'exported: ' + p.exported,
      'tags: [paper-annotations]',
      '---',
      '',
      '# Annotations — ' + p.title,
      ''
    ];
    var section = null;
    p.annotations.forEach(function (a) {
      var s = a.section || 'Untitled section';
      if (s !== section) { section = s; lines.push('## ' + s, ''); }
      lines.push('> ' + a.exact.replace(/\r?\n/g, ' '), '');
      if (a.note) lines.push(a.note, '');
    });
    return lines.join('\n');
  }
  function showFallback(filename, text, msg) {
    closeOtherSurfaces();
    fallback.querySelector('.pg-annot-fallback-msg').textContent =
      (msg || 'Saving isn’t available here.') +
      ' Copy the text below into a file named ' + filename + '.';
    fallback.querySelector('textarea').value = text;
    fallback.hidden = false;
  }
  fallback.addEventListener('click', function (e) {
    var btn = e.target.closest('button');
    if (!btn) return;
    if (btn.getAttribute('data-act') === 'close') { fallback.hidden = true; return; }
    var ta = fallback.querySelector('textarea');
    ta.select();
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(ta.value).then(function () {
        btn.textContent = 'Copied ✓';
      }, function () { btn.textContent = 'Press ⌘C to copy'; });
    } else { btn.textContent = 'Press ⌘C to copy'; }
  });
  function saveFile(filename, text) {
    var dl = window.claude && window.claude.downloads;
    if (!dl) { showFallback(filename, text); return; }
    dl.save({ filename: filename, data: text }).then(function () {
      status('Saved ' + filename);
    }, function (err) {
      if (err && err.code === 'declined') return;  // viewer's call; no retry
      if (err && err.code === 'rate_limited') {
        showFallback(filename, text,
          'A download prompt was already open — copy instead, or try again shortly.');
        return;
      }
      showFallback(filename, text);
    });
  }
  function importPayload(text) {
    var p;
    try { p = JSON.parse(text); } catch (e) { status('Import failed: not valid JSON'); return; }
    if (!p || p.v !== 1 || !Array.isArray(p.annotations)) {
      status('Import failed: not an annotations export'); return;
    }
    var existing = {};
    store.annotations.forEach(function (a) { existing[a.id] = true; });
    var added = 0, skipped = 0;
    p.annotations.forEach(function (a) {
      if (a && a.id && !existing[a.id] && typeof a.exact === 'string') {
        store.annotations.push(a); existing[a.id] = true; added++;
      } else skipped++;
    });
    persist();
    renderAll();
    updateBadge();
    refreshPanelList();
    status('Imported ' + added + (skipped ? ' (skipped ' + skipped + ' duplicate/invalid)' : '') +
      (p.slug !== SLUG ? ' — note: export was from "' + p.slug + '"' : ''));
  }
  panel.addEventListener('click', function (e) {
    var btn = e.target.closest('button[data-act]');
    if (!btn) return;
    var act = btn.getAttribute('data-act');
    if (act === 'export-md') saveFile(SLUG + '-annotations.md', toMarkdown(exportPayload()));
    else if (act === 'export-json') saveFile(SLUG + '-annotations.json', JSON.stringify(exportPayload(), null, 2));
    else if (act === 'import') panel.querySelector('input[type="file"]').click();
  });
  panel.querySelector('input[type="file"]').addEventListener('change', function () {
    var f = this.files && this.files[0];
    this.value = '';
    if (!f) return;
    var reader = new FileReader();
    reader.onload = function () { importPayload(String(reader.result)); };
    reader.readAsText(f);
  });

  /* ---------- global coordination listeners ---------- */
  document.addEventListener('click', function (e) {
    var t = e.target;
    if (!t || !t.closest) return;
    // another surface is opening: get out of its way (their own handlers run too)
    if (t.closest('.gloss-term') || t.closest('#gloss-panel-toggle') ||
        t.closest('.paper-figure img')) {
      closeAnnotationUI();
      return;
    }
    if (t.closest('.pg-annot-ui')) return;
    var m = t.closest('mark.pg-hl');
    if (m && !m.closest('.gloss-term')) {   // a highlight inside a gloss button defers to the popover
      closeOtherSurfaces();
      openEditor(m.getAttribute('data-annot-id'), false);
      return;
    }
    hideToolbar();
    closeEditor(false);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeAnnotationUI();
  });

  /* ---------- init ---------- */
  renderAll();
  updateBadge();
})();
