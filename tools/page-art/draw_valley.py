"""Original line drawing: a hiker on a rock ledge above a river valley with layered ridges.

Drawn from scratch (not traced). Nearer forms hide the ones behind them, so ranges end where
they meet the next ridge; the outer forms are closed inside the frame.
Output: SVG with light lines on transparent (site) and a dark-on-white preview PNG.
"""
import sys, math, random
import numpy as np

out_svg, out_png = sys.argv[1], sys.argv[2]
W, H = 1600, 1000
paths = []                       # (points, stroke width)

def jag(ctrl, rough, seed, depth=6):
    """Midpoint displacement between control points: sharp, natural ridgelines."""
    r = random.Random(seed)
    pts = [tuple(p) for p in ctrl]
    for d in range(depth):
        out = [pts[0]]
        amp = rough / (1.9 ** d)
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + r.uniform(-amp, amp)
            out += [(mx, my), (x2, y2)]
        pts = out
    return pts

def sil(pts):
    """Silhouette function y(x) of a ridge (for hiding what lies behind it)."""
    xs = np.array([p[0] for p in pts]); ys = np.array([p[1] for p in pts]); o = np.argsort(xs)
    return lambda x: np.interp(x, xs[o], ys[o], left=1e9, right=1e9)

def visible(pts, fronts, pad=3):
    """Split a polyline into runs that are not hidden behind any front silhouette."""
    runs, cur = [], []
    for x, y in pts:
        hidden = any(y > f(x) - pad for f in fronts)
        if hidden:
            if len(cur) > 1: runs.append(cur)
            cur = []
        else:
            cur.append((x, y))
    if len(cur) > 1: runs.append(cur)
    return runs

def add(pts, sw, fronts=()):
    for run in (visible(pts, fronts) if fronts else [pts]):
        paths.append((run, sw))

def hatch(ridge_pts, fronts, step, length, slant, sw, seed, keep=0.6, below=None):
    """Short slope strokes hanging off a ridge, like contour shading on a mountain face."""
    r = random.Random(seed)
    for i in range(0, len(ridge_pts) - 1, step):
        if r.random() > keep: continue
        x, y = ridge_pts[i]
        L = length * r.uniform(.5, 1.2)
        s = slant * r.uniform(.6, 1.4)
        seg = [(x + s * t * L, y + 4 + t * L) for t in np.linspace(0, 1, 6)]
        if below is not None: seg = [(a, b) for a, b in seg if b < below(a)]
        if len(seg) > 1: add(seg, sw, fronts)

# ---------------- layers, front to back ----------------
# 1 foreground rock (left), overhanging the valley
rock = [(26, 990), (18, 900), (30, 800), (22, 720), (40, 676), (60, 655), (130, 662), (210, 648), (300, 652), (380, 640), (470, 636), (560, 628), (612, 632),
        (628, 646), (622, 668), (596, 684), (540, 694), (505, 716), (492, 760), (506, 806), (486, 852),
        (500, 902), (484, 948), (496, 1000)]
f_rock = sil(rock[4:16] + [(18, 700)])
def in_rock(x, y): return x < 500 and y > 650

# 2 right valley wall: a big massif with cliff faces
right = jag([(1000, 610), (1080, 560), (1150, 470), (1215, 430), (1260, 360), (1300, 330), (1350, 352),
             (1400, 300), (1460, 318), (1510, 300), (1550, 400), (1575, 520), (1590, 640), (1592, 700)], 34, 4)
f_right = sil(right)
# 3 left valley wall, lower, sloping down to the gap
left = jag([(22, 700), (70, 610), (200, 590), (330, 600), (380, 590), (430, 560), (520, 500), (610, 470), (700, 458), (790, 480), (880, 520), (960, 566),
            (1010, 604)], 26, 3)
f_left = sil(left)
# 4 far range, mostly hidden behind the walls
far = jag([(30, 640), (120, 540), (230, 430), (330, 380), (420, 400), (520, 330), (600, 360), (690, 300), (760, 330),
           (850, 270), (930, 318), (1010, 290), (1090, 360), (1150, 400), (1230, 520), (1290, 620)], 30, 1)
f_far = sil(far)
# 5 distant peaks peeking through the gap
back = jag([(820, 470), (900, 430), (960, 410), (1010, 440), (1060, 420), (1120, 470)], 12, 9)

fronts_left = [f_rock]
fronts_right = [f_rock]
fronts_far = [f_rock, f_left, f_right]
fronts_back = [f_rock, f_left, f_right, f_far]

add(back, 0.8, fronts_back)
add(far, 1.0, fronts_far)
hatch(far, fronts_far, 5, 22, -0.35, 0.7, 11, keep=.4)
hatch(far, fronts_far, 9, 34, 0.25, 0.7, 12, keep=.3)
# snow: short strokes under the highest far peaks
r = random.Random(5)
for cx, top in [(850, 270), (690, 300), (1010, 290)]:
    for j in range(4):
        y = top + 14 + j * 9; w = 10 + j * 9
        add([(cx - w, y + r.uniform(-2, 2)), (cx - w * .2, y - 3), (cx + w * .4, y + 2), (cx + w, y - 1)], 0.8, fronts_far)

add(left, 1.3, fronts_left)
hatch(left, fronts_left, 4, 30, 0.45, 0.7, 21, keep=.5)
hatch(left, fronts_left, 7, 60, 0.6, 0.7, 22, keep=.35)
add(right, 1.4, fronts_right)
f_foot = sil(jag([(1030, 640), (1180, 660), (1330, 676), (1460, 690), (1592, 700)], 8, 34))
hatch(right, fronts_right, 3, 40, -0.25, 0.7, 31, keep=.55, below=f_foot)
hatch(right, fronts_right, 5, 95, -0.12, 0.7, 32, keep=.4, below=f_foot)
# foot of the right massif, where its slope meets the valley floor
foot = jag([(1030, 640), (1180, 660), (1330, 676), (1460, 690), (1592, 700)], 8, 34)
add(foot, 1.0, [f_rock])

# valley floor and river, from the gap (1005, 612) towards the viewer
t = np.linspace(0, 1, 160)
rx = 1005 - 60 * t + 110 * np.sin(t * 7.5) * t ** 1.2 - 140 * t ** 2
ry = 612 + (1000 - 612) * t ** 1.15
rw = 2 + 64 * t ** 1.7
bank_l = [(x - w, y) for x, y, w in zip(rx, ry, rw)]
bank_r = [(x + w, y) for x, y, w in zip(rx, ry, rw)]
add(bank_l, 1.1, [f_rock]); add(bank_r, 1.1, [f_rock])
r = random.Random(41)
for i in range(40, 160, 9):                   # ripples
    y = ry[i] + 3; add([(rx[i] - rw[i] * .45, y), (rx[i] - rw[i] * .05, y + 1)], 0.7, [f_rock])
    if r.random() < .5: add([(rx[i] + rw[i] * .1, y + 6), (rx[i] + rw[i] * .5, y + 6)], 0.7, [f_rock])
# trees: rows of small crowns along both banks and on the lower slopes, scaled by distance
r = random.Random(42)
def crown(x, y, s):
    a = np.linspace(math.pi, 2 * math.pi, 7)
    return [(x + s * np.cos(q), y + s * 1.1 * np.sin(q) * (1 + .25 * r.random())) for q in a]
for n in range(260):
    y = r.uniform(625, 990)
    tt = ((y - 612) / (1000 - 612)) ** (1 / 1.15)
    cxr = np.interp(tt, t, rx); w = np.interp(tt, t, rw)
    side = r.choice((-1, 1))
    x = cxr + side * (w + r.uniform(8, 60 + 380 * tt))
    s = 2.5 + 9 * tt
    fl, fr = f_left(x), f_right(x)
    if (fl < 1e8 and y < fl + 20) or (fr < 1e8 and y < fr + 30): continue
    if x > 1580 or x < 30: continue
    if x < 520 and y > 640: continue                       # behind the rock
    add(crown(x, y, s), 0.8, [f_rock])
# foreground ground line: the rock and the valley floor stand on it; open where the river runs
gy = 990
gl = np.interp(1.0, t, rx) - np.interp(1.0, t, rw); gr = np.interp(1.0, t, rx) + np.interp(1.0, t, rw)
add(jag([(26, gy), (300, gy - 2), (gl - 4, gy)], 3, 61), 1.1)
add(jag([(gr + 4, gy), (1200, gy - 3), (1592, gy - 1)], 3, 62), 1.1)
add([(1592, 700), (1592, gy - 1)], 1.0)          # right end of the valley floor

# rock: outline, strata, cracks, ledge texture
add(rock, 1.7)
r = random.Random(51)
for k, y in enumerate([700, 742, 790, 842, 896, 950]):
    xs = np.linspace(44, 470 - (k % 2) * 20, 40)
    ys = y + 7 * np.sin(xs / 41 + k * 1.7)
    pts = list(zip(xs, ys)); s = r.randint(0, 5); e = len(pts) - r.randint(0, 6)
    add(pts[s:e], 0.9)
for x0, y0 in [(150, 664), (330, 652), (440, 646), (90, 720), (260, 770), (400, 830), (180, 880)]:
    add([(x0, y0), (x0 + r.uniform(-6, 6), y0 + 22), (x0 + r.uniform(-10, 10), y0 + 44)], 0.8)
add([(90, 662), (190, 657)], 0.8); add([(300, 650), (420, 642)], 0.8); add([(470, 640), (560, 633)], 0.8)
# underside shadow lines of the overhang
add([(520, 700), (600, 686)], 0.8); add([(512, 712), (560, 704)], 0.8)

# hiker near the tip, facing the valley (about 70px tall)
hx, hy = 566, 629
def p(dx, dy): return (hx + dx, hy - dy)
for f in [
    [p(-7, 0), p(-5, 14), p(-3, 30)],                         # back leg
    [p(6, 0), p(5, 14), p(2, 30)],                            # front leg
    [p(-5, 30), p(-6, 52), p(-1, 57), p(5, 54), p(5, 30), p(-5, 30)],   # torso
    [p(5, 51), p(12, 40), p(14, 29)],                         # arm
    [p(-6, 54), p(-15, 53), p(-17, 36), p(-14, 30), p(-6, 31)],         # backpack
    [p(-15, 46), p(-6, 46)],                                  # pack strap
]: add(f, 1.4)
a = np.linspace(0, 2 * math.pi, 18)
add(list(zip(hx + 1 + 5.5 * np.cos(a), hy - 64 + 6 * np.sin(a))), 1.4)       # head
add([p(14, 29), p(19, 0)], 1.0)                                              # walking pole

# a few high cloud wisps on the right, clear of the page title
for (x, y, L) in [(1120, 150, 230), (1290, 186, 170), (1010, 210, 130), (1380, 128, 120)]:
    xs = np.linspace(x, x + L, 24); ys = y + 5 * np.sin(np.linspace(0, math.pi, 24))
    add(list(zip(xs, ys)), 0.8)

# ---------------- write ----------------
by_w = {}
for pts, sw in paths:
    by_w.setdefault(sw, []).append("M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts))
groups = "".join(f'<path stroke-width="{sw}" d="{"".join(ds)}"/>' for sw, ds in sorted(by_w.items()))
open(out_svg, "w").write(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
    f'<g fill="none" stroke="#c9c6bf" stroke-linecap="round" stroke-linejoin="round">{groups}</g></svg>')

import cv2
prev = np.full((H, W), 255, np.uint8)
for pts, sw in paths:
    cv2.polylines(prev, [np.array(pts, np.int32)], False, 35, max(1, int(round(sw * 1.3))), cv2.LINE_AA)
cv2.imwrite(out_png, prev)
print(len(paths), "paths")
