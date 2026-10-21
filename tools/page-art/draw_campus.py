"""paper2: an original isometric line drawing of a tech-office district (not traced from anything).

Office towers, low campus buildings, a round glass building, parks, parking, roads with cars,
rooftop details (solar panels, helipads, roof gardens, plant rooms). No signs or logos. Light lines (#c9c6bf) on transparent; faces are
filled with the page colour (#1b1c20) so nearer buildings hide the lines behind them, which is
invisible on the page itself. The drawing fades out towards the edges through a blurred, ragged
mask, so it ends organically.

Usage: python3 draw_campus.py OUT.svg [seed]
"""
import sys, math, random

out = sys.argv[1]
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 3
rng = random.Random(SEED)

W, H = 1600, 1000
S = 11.0                       # px per grid unit
CX, CY = 800, -60              # screen position of grid origin
C30, S30 = math.cos(math.pi / 6), 0.5
BG = "#1b1c20"
INK = "#c9c6bf"

def P(gx, gy, z=0.0):
    return (CX + (gx - gy) * S * C30, CY + (gx + gy) * S * S30 - z * S)

def fmt(pts):
    return " ".join("%.1f,%.1f" % p for p in pts)

items = []                     # (depth, svg)

def add(depth, svg):
    items.append((depth, svg))

def line(a, b, w=0.6, o=0.6):
    return '<path d="M%.1f %.1fL%.1f %.1f" stroke-width="%s" stroke-opacity="%s"/>' % (*a, *b, w, o)

def polyline(pts, w=0.6, o=0.6, closed=False):
    d = "M" + "L".join("%.1f %.1f" % p for p in pts) + ("Z" if closed else "")
    return '<path d="%s" stroke-width="%s" stroke-opacity="%s"/>' % (d, w, o)

def face(pts, w=0.9, o=1.0):
    return '<polygon points="%s" fill="%s" stroke-width="%s" stroke-opacity="%s"/>' % (fmt(pts), BG, w, o)

def ellipse_pts(gx, gy, r, z, n=40, a0=0, a1=2 * math.pi):
    return [P(gx + r * math.cos(a0 + (a1 - a0) * i / n), gy + r * math.sin(a0 + (a1 - a0) * i / n), z)
            for i in range(n + 1)]

# --- elements ------------------------------------------------------------------------------
def box(x, y, w, d, h, windows="grid", top_extra=None):
    """building; returns svg. Visible: top, face +x (right), face +y (left)."""
    s = []
    x1, y1 = x + w, y + d
    s.append(face([P(x1, y, 0), P(x1, y1, 0), P(x1, y1, h), P(x1, y, h)]))       # right face
    s.append(face([P(x, y1, 0), P(x1, y1, 0), P(x1, y1, h), P(x, y1, h)]))       # left face
    s.append(face([P(x, y, h), P(x1, y, h), P(x1, y1, h), P(x, y1, h)]))         # roof
    fl = 0.7                                                                      # floor height
    if windows == "grid":
        for k in range(1, int(h / fl)):
            z = k * fl
            s.append(line(P(x1, y, z), P(x1, y1, z), 0.45, 0.45))
            s.append(line(P(x, y1, z), P(x1, y1, z), 0.45, 0.45))
        for t in frange(0.9, d - 0.3, 0.9):
            s.append(line(P(x1, y + t, 0.3), P(x1, y + t, h - 0.25), 0.4, 0.3))
        for t in frange(0.9, w - 0.3, 0.9):
            s.append(line(P(x + t, y1, 0.3), P(x + t, y1, h - 0.25), 0.4, 0.3))
    elif windows == "bands":                                                      # ribbon windows
        for k in range(int(h / fl)):
            z0, z1 = k * fl + 0.12, k * fl + 0.3
            for z in (z0, z1):
                s.append(line(P(x1, y + 0.2, z), P(x1, y1 - 0.2, z), 0.45, 0.45))
                s.append(line(P(x + 0.2, y1, z), P(x1 - 0.2, y1, z), 0.45, 0.45))
    elif windows == "glass":                                                      # curtain wall
        for t in frange(0.5, d - 0.2, 0.5):
            s.append(line(P(x1, y + t, 0), P(x1, y + t, h), 0.4, 0.35))
        for t in frange(0.5, w - 0.2, 0.5):
            s.append(line(P(x + t, y1, 0), P(x + t, y1, h), 0.4, 0.35))
        for z in frange(1.2, h - 0.2, 1.2):
            s.append(line(P(x1, y, z), P(x1, y1, z), 0.4, 0.35))
            s.append(line(P(x, y1, z), P(x1, y1, z), 0.4, 0.35))
    # door
    dx = x + w * 0.5
    s.append(polyline([P(dx - 0.35, y1, 0), P(dx - 0.35, y1, 0.35), P(dx + 0.35, y1, 0.35), P(dx + 0.35, y1, 0)], 0.6, 0.7))
    # parapet
    s.append(polyline([P(x + .15, y + .15, h), P(x1 - .15, y + .15, h), P(x1 - .15, y1 - .15, h), P(x + .15, y1 - .15, h)], 0.4, 0.45, True))
    if top_extra: s += top_extra(x, y, w, d, h)
    return "".join(s)

def frange(a, b, st):
    v = a
    while v < b:
        yield v; v += st

def roof_solar(x, y, w, d, h):
    s = []
    for r in frange(0.6, d - 0.6, 0.9):
        a, b = x + 0.5, x + w - 0.5
        q = [P(a, y + r, h + 0.05), P(b, y + r, h + 0.05), P(b, y + r + 0.55, h + 0.3), P(a, y + r + 0.55, h + 0.3)]
        s.append(polyline(q, 0.45, 0.6, True))
        for c in frange(a + 0.7, b, 0.7):
            s.append(line(P(c, y + r, h + 0.05), P(c, y + r + 0.55, h + 0.3), 0.35, 0.4))
    return s

def roof_helipad(x, y, w, d, h):
    cx, cy = x + w / 2, y + d / 2
    r = min(w, d) * 0.32
    s = [polyline(ellipse_pts(cx, cy, r, h), 0.6, 0.7), polyline(ellipse_pts(cx, cy, r * 0.82, h), 0.4, 0.5)]
    a = r * 0.35
    s.append(line(P(cx - a, cy - a * 0.8, h), P(cx - a, cy + a * 0.8, h), 0.6, 0.7))
    s.append(line(P(cx + a, cy - a * 0.8, h), P(cx + a, cy + a * 0.8, h), 0.6, 0.7))
    s.append(line(P(cx - a, cy, h), P(cx + a, cy, h), 0.6, 0.7))
    return s

def roof_garden(x, y, w, d, h):
    s = []
    for _ in range(int(w * d / 4) + 2):
        tx, ty = rng.uniform(x + 0.7, x + w - 0.7), rng.uniform(y + 0.7, y + d - 0.7)
        s.append(tree_svg(tx, ty, h, rng.uniform(0.35, 0.6)))
    s.append(polyline([P(x + .5, y + .5, h), P(x + w - .5, y + .5, h), P(x + w - .5, y + d - .5, h), P(x + .5, y + d - .5, h)], 0.35, 0.35, True))
    return s

def roof_plant(x, y, w, d, h):
    s = []
    for _ in range(rng.randint(1, 3)):
        bw, bd, bh = rng.uniform(0.8, 1.6), rng.uniform(0.8, 1.6), rng.uniform(0.4, 0.8)
        bx, by = rng.uniform(x + 0.4, x + w - bw - 0.4), rng.uniform(y + 0.4, y + d - bd - 0.4)
        s.append(face([P(bx + bw, by, h), P(bx + bw, by + bd, h), P(bx + bw, by + bd, h + bh), P(bx + bw, by, h + bh)], 0.5, 0.7))
        s.append(face([P(bx, by + bd, h), P(bx + bw, by + bd, h), P(bx + bw, by + bd, h + bh), P(bx, by + bd, h + bh)], 0.5, 0.7))
        s.append(face([P(bx, by, h + bh), P(bx + bw, by, h + bh), P(bx + bw, by + bd, h + bh), P(bx, by + bd, h + bh)], 0.5, 0.7))
    return s

def round_building(cx, cy, r, h):
    s = []
    # body: front half outline + vertical mullions on the visible side
    front = ellipse_pts(cx, cy, r, 0, 40, -math.pi / 4, 3 * math.pi / 4)
    topf = ellipse_pts(cx, cy, r, h, 40, -math.pi / 4, 3 * math.pi / 4)
    s.append('<polygon points="%s" fill="%s" stroke-width="0.9"/>' % (fmt(front + topf[::-1]), BG))
    s.append('<polygon points="%s" fill="%s" stroke-width="0.9"/>' % (fmt(ellipse_pts(cx, cy, r, h, 60)), BG))
    for i in range(1, 22):
        a = -math.pi / 4 + math.pi * i / 22
        s.append(line(P(cx + r * math.cos(a), cy + r * math.sin(a), 0), P(cx + r * math.cos(a), cy + r * math.sin(a), h), 0.4, 0.35))
    for z in frange(0.9, h, 0.9):
        s.append(polyline(ellipse_pts(cx, cy, r, z, 40, -math.pi / 4, 3 * math.pi / 4), 0.4, 0.4))
    # inner courtyard ring on the roof
    s.append(polyline(ellipse_pts(cx, cy, r * 0.55, h, 50), 0.6, 0.7))
    for i in range(10):
        tx, ty = cx + rng.uniform(-r * .3, r * .3), cy + rng.uniform(-r * .3, r * .3)
        s.append(tree_svg(tx, ty, h - 0.2, 0.4))
    return "".join(s)

def tree_svg(gx, gy, z=0.0, size=0.6):
    bx, by = P(gx, gy, z)
    tx, ty = P(gx, gy, z + size * 1.2)
    rr = size * S * 0.8
    return (line((bx, by), (tx, ty + rr * 0.6), 0.5, 0.7) +
            '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke-width="0.6" stroke-opacity="0.85"/>' % (tx, ty, rr, BG))

def car(gx, gy, along_x):
    l, wd, hh = (1.0, 0.5, 0.35) if along_x else (0.5, 1.0, 0.35)
    x, y = gx - l / 2, gy - wd / 2
    return "".join([
        face([P(x + l, y, 0), P(x + l, y + wd, 0), P(x + l, y + wd, hh), P(x + l, y, hh)], 0.5, 0.75),
        face([P(x, y + wd, 0), P(x + l, y + wd, 0), P(x + l, y + wd, hh), P(x, y + wd, hh)], 0.5, 0.75),
        face([P(x, y, hh), P(x + l, y, hh), P(x + l, y + wd, hh), P(x, y + wd, hh)], 0.5, 0.75)])

# --- layout --------------------------------------------------------------------------------
BLOCK, ROAD = 8.0, 2.4
NX, NY = 10, 10
ground = []
# roads: lines along both axes with dashed centre lines
span = NX * (BLOCK + ROAD)
for i in range(NX + 1):
    o = i * (BLOCK + ROAD) - ROAD
    for (a, b) in ((o, o + ROAD),):
        ground.append(line(P(a, -ROAD, 0), P(a, span, 0), 0.6, 0.55))
        ground.append(line(P(b, -ROAD, 0), P(b, span, 0), 0.6, 0.55))
        ground.append(line(P(-ROAD, a, 0), P(span, a, 0), 0.6, 0.55))
        ground.append(line(P(-ROAD, b, 0), P(span, b, 0), 0.6, 0.55))
        m = o + ROAD / 2
        for t in frange(-ROAD, span, 1.4):
            ground.append(line(P(m, t, 0), P(m, t + 0.6, 0), 0.4, 0.4))
            ground.append(line(P(t, m, 0), P(t + 0.6, m, 0), 0.4, 0.4))
add(-1e9, "".join(ground))

centre = (NX - 1) / 2
for i in range(NX):
    for j in range(NY):
        bx, by = i * (BLOCK + ROAD), j * (BLOCK + ROAD)
        dist = math.hypot(i - centre, j - centre) / centre      # 0 centre .. ~1.4 corners
        hmul = max(0.35, 1.25 - 0.75 * dist)
        kind = rng.random()
        if (i, j) == (6, 6):
            add(bx + by + BLOCK, round_building(bx + BLOCK / 2, by + BLOCK / 2, BLOCK * 0.45, 4.5))
            continue
        if kind < 0.14:                                          # park
            for _ in range(int(14 + 8 * rng.random())):
                tx, ty = rng.uniform(bx + .6, bx + BLOCK - .6), rng.uniform(by + .6, by + BLOCK - .6)
                add(tx + ty, tree_svg(tx, ty, 0, rng.uniform(0.5, 0.8)))
            path = [P(bx, by + BLOCK * 0.3), P(bx + BLOCK * 0.5, by + BLOCK * 0.55), P(bx + BLOCK, by + BLOCK * 0.6)]
            add(bx + by, polyline(path, 0.45, 0.45))
            continue
        if kind < 0.24:                                          # parking lot
            s = [polyline([P(bx + .3, by + .3), P(bx + BLOCK - .3, by + .3), P(bx + BLOCK - .3, by + BLOCK - .3), P(bx + .3, by + BLOCK - .3)], 0.4, 0.45, True)]
            for r in (by + 1.5, by + 5.0):
                for t in frange(bx + 0.6, bx + BLOCK - 0.4, 0.9):
                    s.append(line(P(t, r), P(t, r + 1.6), 0.35, 0.35))
            add(bx + by, "".join(s))
            for r in (by + 2.3, by + 5.8):
                for t in frange(bx + 1.05, bx + BLOCK - 0.6, 0.9):
                    if rng.random() < 0.55: add(t + r, car(t, r, False))
            continue
        # one to three buildings on the block
        n = 1 if kind < 0.55 else rng.choice([2, 3])
        if n == 1:
            parts = [(bx + .5, by + .5, BLOCK - 1, BLOCK - 1)]
        elif n == 2:
            parts = [(bx + .5, by + .5, BLOCK - 1, BLOCK * 0.45), (bx + .5, by + BLOCK * 0.55 + .2, BLOCK - 1, BLOCK * 0.45 - .7)]
        else:
            parts = [(bx + .5, by + .5, BLOCK * 0.45, BLOCK - 1), (bx + BLOCK * 0.55, by + .5, BLOCK * 0.45 - .5, BLOCK * 0.45),
                     (bx + BLOCK * 0.55, by + BLOCK * 0.55, BLOCK * 0.45 - .5, BLOCK * 0.45 - .5)]
        for (x, y, w, d) in parts:
            tall = rng.random() < 0.35 * hmul
            h = (rng.uniform(9, 15) if tall else rng.uniform(2.2, 5.5)) * hmul + 1
            win = rng.choice(["grid", "glass", "bands"]) if h > 6 else rng.choice(["bands", "grid"])
            extra = rng.choice([roof_solar, roof_plant, roof_garden, roof_helipad, None]) if w > 3 and d > 3 else roof_plant
            if w > 3 and rng.random() < 0.45 and extra in (roof_garden, roof_helipad):
                extra = roof_plant          # (where a rooftop sign used to stand; keeps the layout)
            add(x + w + y + d, box(x, y, w, d, h, win, extra))
        # a few trees along the block edge
        for t in frange(bx + 1, bx + BLOCK, 2.2):
            add(t + by + BLOCK + 0.6, tree_svg(t, by + BLOCK + 0.55, 0, 0.45))

# cars on the roads and round billboards at some corners
for i in range(NX + 1):
    o = i * (BLOCK + ROAD) - ROAD
    for t in frange(0, span, 3.1):
        if rng.random() < 0.18: add(o + .6 + t, car(o + 0.6, t, False))
        if rng.random() < 0.18: add(o + 1.8 + t, car(o + 1.8, t, False))
        if rng.random() < 0.18: add(t + o + .6, car(t, o + 0.6, True))
        if rng.random() < 0.18: add(t + o + 1.8, car(t, o + 1.8, True))
items.sort(key=lambda t: t[0])

# --- organic fade: a ragged, blurred mask -------------------------------------------------------
mr = random.Random(SEED + 11)
cx, cy, rx, ry = 800, 560, 640, 350
pts = []
for k in range(48):
    a = 2 * math.pi * k / 48
    f = 1 + 0.07 * math.sin(3 * a + 1.3) + 0.05 * math.sin(7 * a + 0.4) + mr.uniform(-0.04, 0.04)
    pts.append((cx + rx * f * math.cos(a), cy + ry * f * math.sin(a)))

# drop items that lie wholly outside the faded area (keeps the file small)
import re
def inside(px, py, poly, grow=1.25):
    qx, qy = cx + (px - cx) / grow, cy + (py - cy) / grow
    c = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > qy) != (y2 > qy) and qx < (x2 - x1) * (qy - y1) / (y2 - y1) + x1: c = not c
    return c
num = re.compile(r"(?:points=\"|M|cx=\")(-?[\d.]+)[ ,\"]+(?:cy=\")?(-?[\d.]+)")
kept = []
for dpt, it in items:
    m = num.search(it)
    if dpt == -1e9 or (m and inside(float(m.group(1)), float(m.group(2)), pts)):
        kept.append((dpt, it))
items = kept

svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H),
       '<defs><filter id="soft" x="-20%%" y="-20%%" width="140%%" height="140%%"><feGaussianBlur stdDeviation="60"/></filter>'
       '<mask id="fade" maskUnits="userSpaceOnUse" x="0" y="0" width="%d" height="%d">' % (W, H),
       '<polygon points="%s" fill="#fff" filter="url(#soft)"/></mask></defs>' % fmt(pts),
       '<style>.d polygon,.d circle{fill:%s}</style>' % BG,
       '<g class="d" mask="url(#fade)" fill="none" stroke="%s" stroke-width="0.9" stroke-linecap="round" stroke-linejoin="round">' % INK]
body = "".join(s for _, s in items)
# slim the file: shorter numbers, and merge runs of consecutive paths with the same stroke into one
body = re.sub(r"(\d+\.\d)\d*", r"\1", body)
body = re.sub(r"(\d+)\.0(?!\d)", r"\1", body)
seg = re.compile(r'<path d="([^"]+)" stroke-width="([^"]+)" stroke-opacity="([^"]+)"/>')
outp, last, buf = [], None, []
pos = 0
for m in seg.finditer(body):
    if m.start() != pos or (m.group(2), m.group(3)) != last:
        if buf: outp.append('<path d="%s" stroke-width="%s" stroke-opacity="%s"/>' % ("".join(buf), *last)); buf = []
        outp.append(body[pos:m.start()])
    last = (m.group(2), m.group(3)); buf.append(m.group(1)); pos = m.end()
if buf: outp.append('<path d="%s" stroke-width="%s" stroke-opacity="%s"/>' % ("".join(buf), *last))
outp.append(body[pos:])
body = "".join(outp).replace(" L", "L")
# faces and tree crowns get the page colour from one CSS rule instead of an attribute each
body = body.replace(' fill="%s"' % INK, ' style="fill:%s"' % INK).replace(' fill="%s"' % BG, "")
body = body.replace(' stroke-opacity="1"', "").replace(' stroke-width="0.9"', "")
svg.append(body)
svg.append("</g></svg>")
open(out, "w").write("".join(svg))
print(out, len(items), "items")
