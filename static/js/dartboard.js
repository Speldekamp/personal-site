/* Dartboard tool: interactive pathway figure for /data/dartboard-tool-test/.
   Data from Table 1 of GS4S Policy brief no. 4 (transcribed from the source figures).
   Codes per ring, centre outwards: E essential, H helps, A must be absent,
   U usually absent, N does not matter. */
(function () {
  'use strict';

  var DATA = {
    manufacturing: {
      name: 'Manufacturing',
      head: 'Made with skills: inflow programmes power every pathway.',
      sub: 'Three of the four pathways also rely on automation.',
      paths: [
        [5, 'UEUNUEUA', 'Where formal barriers are high and automation is not an option, firms depend on skill inflow programmes. Simpler visa, permit and diploma procedures make those programmes work.'],
        [6, 'UHUENEUE', 'Non-EU recruitment, backed by inflow programmes and automation, keeps these firms staffed. Faster work permits pay off directly.'],
        [15, 'UHUNEEHE', 'The most common route: EU hiring, inflow programmes and automation together. Support for intra-EU mobility and for automation reinforce each other.'],
        [3, 'HUUHEEHE', 'Even where language and partner-job barriers exist, firms close gaps through EU hiring, inflow programmes and automation. Integration support lowers the cost.']
      ]
    },
    health: {
      name: 'Health',
      head: 'Outsourcing is the standard treatment in health.',
      sub: 'Automation adds to it where firms also recruit internationally.',
      paths: [
        [13, 'UHUHHNEE', 'Outsourcing and automation do the heavy lifting, with recruitment from inside and outside the EU on top. Support for technology adoption and open hiring routes both count.'],
        [4, 'UHUHAHEN', 'These firms outsource and recruit beyond the EU, not within it. Fast-track routes for non-EU health workers matter most here.'],
        [4, 'UHUAHHEN', 'The mirror image of Pathway 2: outsourcing plus hiring within the EU, not beyond it. Intra-EU mobility and diploma recognition are the levers.'],
        [14, 'UHNHHHEE', 'The broadest toolkit: outsourcing and automation, helped by every form of recruitment. It works whatever the cause of the shortage.']
      ]
    },
    construction: {
      name: 'Construction',
      head: 'Outsourcing is the cornerstone of construction.',
      sub: 'Automation only plays a supporting role.',
      paths: [
        [14, 'UHUNHHEH', 'Outsourcing carries the load, with EU hiring, inflow programmes and some automation in support. Policy that eases subcontracting across borders reaches these firms first.'],
        [13, 'UHNHHHEH', 'Outsourcing again, now backed by recruitment from inside and outside the EU. Open, simple hiring routes help these firms most.']
      ]
    },
    it: {
      name: 'IT',
      head: 'Bots need brains: automation works best with new talent.',
      sub: 'Where automation is missing, larger firms hire from outside the EU instead.',
      paths: [
        [27, 'UHUHHENN', 'The largest group relies on skill inflow programmes, helped by hiring from inside and outside the EU. Well-run inflow programmes are the main lever.'],
        [13, 'UHUEHNHA', 'Without automation, these firms hire from outside the EU. Quick, predictable work permits are what they need.'],
        [19, 'UHUNHEHE', 'Automation paired with inflow programmes: new tools and new talent go together. Fund both at once.'],
        [18, 'UHUHNEHE', 'The same pairing of automation and inflow programmes, with non-EU hiring in support.'],
        [25, 'UHNHHEHE', 'Automation and inflow programmes, whatever the cause of the shortage. Investment in both pays off broadly.'],
        [6, 'HUNHHEHE', 'Even where language and partner-job barriers exist, firms combine automation with inflow programmes. Integration support helps them keep the talent.']
      ]
    }
  };
  var ORDER = ['manufacturing', 'health', 'construction', 'it'];

  /* Ring labels as in the source figures: first line bold, second line regular. */
  var RINGS = [
    ['Informal barriers', '(language, partner jobs)'],
    ['Formal barriers', '(visas, permits, diplomas)'],
    ['Shortage caused by', 'lack of training'],
    ['Hiring from', 'outside the EU'],
    ['Hiring from', 'within the EU'],
    ['Skill inflow', 'programmes'],
    ['Outsourcing or', 'offshoring'],
    ['Automation', '']
  ];
  /* The same rings, as phrases for the side text. */
  var PHRASES = [
    'informal barriers (language, partner jobs)',
    'formal barriers (visas, permits, diplomas)',
    'a shortage caused by lack of training',
    'hiring from outside the EU',
    'hiring from within the EU',
    'skill inflow programmes',
    'outsourcing or offshoring',
    'automation'
  ];
  var STATES = { E: 'Essential', H: 'Helps', A: 'Must be absent', U: 'Usually absent', N: 'Does not matter' };
  var STATE_ORDER = ['E', 'H', 'A', 'U', 'N'];

  /* [fill, mark colour, mark width] per state, plus figure colours. */
  var PALETTES = {
    dark: {
      E: ['#4d7a33', '#f0ede6', 2.6], H: ['#2c3a27', '#9cc27f', 2], A: ['#b8352c', '#f0ede6', 2.6], U: ['#43302a', '#e3936a', 2], N: ['#2a2c31', null, 0],
      gap: '#1b1c20', outline: '#3a3d44', lblSet: '#36302b', lblAct: '#27292e', lblLine: '#1b1c20', lblBold: '#f0ede6', lblText: '#c9c6bf',
      hub: '#24262b', hubLine: '#3a3d44', hubText: '#f0ede6', hubSub: '#a3a6ad', sel: '#f0ede6', dim: 0.32, swLine: '#3a3d44'
    },
    light: {
      E: ['#43761f', '#ffffff', 2.6], H: ['#e2eedb', '#2f5e14', 2], A: ['#ff0000', '#ffffff', 2.6], U: ['#f6c9ab', '#c9581c', 2], N: ['#f2f2f2', null, 0],
      gap: '#1b1c20', outline: '#c9c6bf', lblSet: '#fde6cf', lblAct: '#fcf4ec', lblLine: '#e8c9b5', lblBold: '#34304e', lblText: '#34304e',
      hub: '#34304e', hubLine: '#34304e', hubText: '#ffffff', hubSub: '#f2a58a', sel: '#f0ede6', dim: 0.38, hDim: 0.9, swLine: '#1b1c20'
    }
  };

  var NS = 'http://www.w3.org/2000/svg';
  var CX = 350;
  var R = [92, 123, 154, 185, 216, 247, 278, 309, 340];
  var HALF = 38; /* half-angle of the label wedge at the top */

  function xy(r, a) {
    var t = a * Math.PI / 180;
    return [CX + r * Math.sin(t), CX - r * Math.cos(t)];
  }
  function pt(r, a) {
    var p = xy(r, a);
    return p[0].toFixed(2) + ' ' + p[1].toFixed(2);
  }
  function sect(a0, a1, r0, r1) {
    var L = (a1 - a0) > 180 ? 1 : 0;
    return 'M' + pt(r1, a0) + ' A' + r1 + ' ' + r1 + ' 0 ' + L + ' 1 ' + pt(r1, a1) +
      ' L' + pt(r0, a1) + ' A' + r0 + ' ' + r0 + ' 0 ' + L + ' 0 ' + pt(r0, a0) + ' Z';
  }
  function markPath(code, x, y, s) {
    s = s || 1;
    if (code === 'E' || code === 'H') {
      return 'M' + (x - 4.6 * s) + ' ' + (y + 0.2 * s) + ' L' + (x - 1.4 * s) + ' ' + (y + 3.5 * s) + ' L' + (x + 4.8 * s) + ' ' + (y - 3.7 * s);
    }
    if (code === 'A' || code === 'U') {
      var k = 3.6 * s;
      return 'M' + (x - k) + ' ' + (y - k) + ' L' + (x + k) + ' ' + (y + k) + ' M' + (x + k) + ' ' + (y - k) + ' L' + (x - k) + ' ' + (y + k);
    }
    return '';
  }
  function el(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function h(tag, cls, text, parent) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    if (parent) parent.appendChild(e);
    return e;
  }
  function listSentence(items) {
    var s = items.length === 1 ? items[0]
      : items.slice(0, -1).join(', ') + ' and ' + items[items.length - 1];
    return s.charAt(0).toUpperCase() + s.slice(1) + '.';
  }
  function swatch(P, code, parent) {
    var svg = el('svg', { viewBox: '0 0 20 20', width: 18, height: 18, 'aria-hidden': 'true', 'class': 'db-swatch' }, parent);
    el('rect', { x: 1, y: 1, width: 18, height: 18, rx: 4, fill: P[code][0], stroke: P.swLine, 'stroke-width': 1 }, svg);
    if (P[code][1]) {
      el('path', { d: markPath(code, 10, 10, 0.85), fill: 'none', stroke: P[code][1], 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, svg);
    }
    return svg;
  }

  function mount(root) {
    var state = { sector: 'manufacturing', sel: 0, mode: 'dark' };

    var top = h('div', 'db-top', null, root);
    var sectorGroup = h('div', 'db-seg db-sectors', null, top);
    sectorGroup.setAttribute('role', 'group');
    sectorGroup.setAttribute('aria-label', 'Sector');
    var sectorButtons = ORDER.map(function (k) {
      var b = h('button', null, DATA[k].name, sectorGroup);
      b.type = 'button';
      b.addEventListener('click', function () { state.sector = k; state.sel = 0; render(); });
      return b;
    });
    var modeGroup = h('div', 'db-seg db-mode', null, top);
    modeGroup.setAttribute('role', 'group');
    modeGroup.setAttribute('aria-label', 'Colours');
    var modeButtons = [['dark', 'Dark'], ['light', 'Light']].map(function (m) {
      var b = h('button', null, m[1], modeGroup);
      b.type = 'button';
      b.addEventListener('click', function () { state.mode = m[0]; render(); });
      return [m[0], b];
    });

    var intro = h('div', 'db-intro', null, root);
    var introHead = h('div', 'db-head', null, intro);
    var introSub = h('div', 'db-sub', null, intro);

    var body = h('div', 'db-body', null, root);
    var left = h('div', 'db-panel db-left', null, body);
    var fig = h('div', 'db-fig', null, body);
    var right = h('div', 'db-panel db-right', null, body);
    left.setAttribute('aria-live', 'polite');
    right.setAttribute('aria-live', 'polite');

    var foot = h('div', 'db-foot', null, root);
    var legend = h('div', 'db-legend', null, foot);
    h('div', 'db-note', 'Inner three rings: the setting firms face. Outer five rings: what firms do. Wedge size = number of firms. Read each wedge from the centre outwards. Click a wedge to read about it.', foot);
    h('div', 'db-source', 'Based on Table 1 of GS4S Policy brief no. 4.', foot);

    function render() {
      var P = PALETTES[state.mode];
      var D = DATA[state.sector];
      var total = D.paths.reduce(function (t, p) { return t + p[0]; }, 0);
      var span = 360 - 2 * HALF;

      introHead.textContent = D.head;
      introSub.textContent = D.sub;
      sectorButtons.forEach(function (b, i) { b.setAttribute('aria-pressed', ORDER[i] === state.sector ? 'true' : 'false'); });
      modeButtons.forEach(function (m) { m[1].setAttribute('aria-pressed', m[0] === state.mode ? 'true' : 'false'); });

      var a = HALF;
      var wedges = D.paths.map(function (p, i) {
        var a0 = a, a1 = a + span * p[0] / total;
        a = a1;
        return { i: i, n: p[0], codes: p[1], take: p[2], a0: a0, a1: a1, mid: (a0 + a1) / 2 };
      });

      var svg = el('svg', { viewBox: '0 0 700 700', role: 'group', 'aria-label': D.name + ': ' + D.paths.length + ' pathways, ' + total + ' firms' });
      var gCells = el('g', {}, svg);
      var gLabels = el('g', {}, svg);
      var gMarks = el('g', { 'pointer-events': 'none' }, svg);
      var gLines = el('g', { 'pointer-events': 'none' }, svg);
      var gHub = el('g', { 'pointer-events': 'none' }, svg);
      var gHits = el('g', {}, svg);

      wedges.forEach(function (w) {
        var o = w.i === state.sel ? 1 : P.dim;
        for (var k = 0; k < 8; k++) {
          var c = w.codes[k];
          el('path', { d: sect(w.a0, w.a1, R[k], R[k + 1]), fill: P[c][0], opacity: o, stroke: P.gap, 'stroke-width': 1.5 }, gCells);
          if (P[c][1]) {
            var p = xy((R[k] + R[k + 1]) / 2, w.mid);
            el('path', { d: markPath(c, p[0], p[1]), fill: 'none', stroke: P[c][1], 'stroke-width': P[c][2], 'stroke-linecap': 'round', 'stroke-linejoin': 'round', opacity: (c === 'H' && P.hDim && w.i !== state.sel) ? P.hDim : o }, gMarks);
          }
        }
        var desc = RINGS.map(function (r, k) { return (r[0] + ' ' + r[1]).trim() + ': ' + STATES[w.codes[k]].toLowerCase(); }).join('; ');
        var hit = el('path', {
          'class': 'db-hit', d: sect(w.a0, w.a1, R[0], R[8]), fill: 'transparent',
          stroke: w.i === state.sel ? P.sel : 'none', 'stroke-width': 2,
          tabindex: 0, role: 'button', 'aria-pressed': w.i === state.sel ? 'true' : 'false',
          'aria-label': 'Pathway ' + (w.i + 1) + ', ' + w.n + ' firms. ' + desc
        }, gHits);
        var pick = function () {
          var hadFocus = document.activeElement === hit;
          state.sel = w.i;
          render();
          if (hadFocus) focusHit(w.i);
        };
        hit.addEventListener('click', pick);
        hit.addEventListener('keydown', function (e) {
          if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(); }
        });
      });

      /* Label wedge: ring names in the top slice */
      for (var k = 0; k < 8; k++) {
        el('path', { d: sect(-HALF, HALF, R[k], R[k + 1]), fill: k < 3 ? P.lblSet : P.lblAct, stroke: P.lblLine, 'stroke-width': 1 }, gLabels);
        var y = CX - (R[k] + R[k + 1]) / 2;
        var two = RINGS[k][1] !== '';
        var t1 = el('text', { x: CX, y: two ? y - 2.5 : y + 4, 'text-anchor': 'middle', 'font-size': 11.5, 'font-weight': 600, fill: P.lblBold, 'aria-hidden': 'true' }, gLabels);
        t1.textContent = RINGS[k][0];
        if (two) {
          var t2 = el('text', { x: CX, y: y + 9.5, 'text-anchor': 'middle', 'font-size': 10.5, fill: P.lblText, 'aria-hidden': 'true' }, gLabels);
          t2.textContent = RINGS[k][1];
        }
      }

      /* Gaps: between the setting and action rings, and between wedges */
      el('circle', { cx: CX, cy: CX, r: R[3], fill: 'none', stroke: P.gap, 'stroke-width': 4.5 }, gLines);
      [HALF].concat(wedges.map(function (w) { return w.a1; })).forEach(function (b) {
        el('path', { d: 'M' + pt(R[0] - 3, b) + ' L' + pt(R[8] + 3, b), stroke: P.gap, 'stroke-width': 5 }, gLines);
      });
      el('circle', { cx: CX, cy: CX, r: R[8] + 2, fill: 'none', stroke: P.outline, 'stroke-width': 2 }, gLines);

      /* Centre: sector, pathways, firms */
      el('circle', { cx: CX, cy: CX, r: R[0] - 3, fill: P.hub, stroke: P.hubLine, 'stroke-width': 1 }, gHub);
      el('text', { x: CX, y: CX - 8, 'text-anchor': 'middle', 'font-size': 24, 'font-weight': 500, fill: P.hubText }, gHub).textContent = D.name;
      el('text', { x: CX, y: CX + 18, 'text-anchor': 'middle', 'font-size': 15, fill: P.hubSub }, gHub).textContent = D.paths.length + ' pathways';
      el('text', { x: CX, y: CX + 38, 'text-anchor': 'middle', 'font-size': 15, fill: P.hubSub }, gHub).textContent = total + ' firms';

      fig.replaceChildren(svg);

      /* Legend */
      legend.replaceChildren();
      STATE_ORDER.forEach(function (c) {
        var item = h('span', 'db-legend-item', null, legend);
        swatch(P, c, item);
        h('span', null, STATES[c], item);
      });

      /* Side text: in the column on the same side as the selected wedge */
      var w = wedges[state.sel];
      var onRight = Math.sin(w.mid * Math.PI / 180) > 0;
      var target = onRight ? right : left;
      (onRight ? left : right).replaceChildren();
      fillPanel(target, P, D, w.i, w.n, w.codes, w.take);
      fitHeight();
    }

    function fillPanel(target, P, D, i, n, codes, takeText) {
      target.replaceChildren();
      var main = h('div', 'db-path', null, target);
      h('div', 'db-title', 'Pathway ' + (i + 1), main);
      h('div', 'db-firms', n + (n === 1 ? ' firm' : ' firms') + ' in ' + (D.name === D.name.toUpperCase() ? D.name : D.name.toLowerCase()), main);
      STATE_ORDER.forEach(function (c) {
        var items = [];
        for (var k = 0; k < 8; k++) if (codes[k] === c) items.push(PHRASES[k]);
        if (!items.length) return;
        var g = h('div', 'db-group', null, main);
        var lab = h('div', 'db-label', null, g);
        swatch(P, c, lab);
        h('span', null, STATES[c], lab);
        h('div', 'db-items', listSentence(items), g);
      });
      var take = h('div', 'db-take', null, target);
      h('div', 'db-title', 'Takeaway', take);
      h('div', 'db-items db-take-text', takeText, take);
    }

    /* Keep the legend in one place: the figure row is as tall as the
       tallest pathway text of any sector at the current width. */
    function fitHeight() {
      body.style.minHeight = '';
      var cols = getComputedStyle(body).gridTemplateColumns.split(' ').length;
      if (cols < 3) return;
      var P = PALETTES[state.mode];
      var probe = h('div', 'db-panel db-right', null, body);
      probe.style.cssText = 'position:absolute;visibility:hidden;left:0;top:0;width:' + right.getBoundingClientRect().width + 'px';
      var max = 0;
      ORDER.forEach(function (k) {
        DATA[k].paths.forEach(function (p, i) {
          fillPanel(probe, P, DATA[k], i, p[0], p[1], p[2]);
          max = Math.max(max, probe.getBoundingClientRect().height);
        });
      });
      body.removeChild(probe);
      body.style.minHeight = Math.ceil(Math.max(max, fig.getBoundingClientRect().height)) + 'px';
    }

    var resizeTimer;
    window.addEventListener('resize', function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(fitHeight, 100);
    });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitHeight);

    function focusHit(i) {
      var hits = fig.querySelectorAll('.db-hit');
      if (hits[i]) hits[i].focus();
    }

    render();
  }

  function init() {
    var roots = document.querySelectorAll('.dartboard');
    for (var i = 0; i < roots.length; i++) mount(roots[i]);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
