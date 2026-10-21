"""paper4: trace a landscape photo (lone tree on a plain) into a light line drawing.

Traces the mountain silhouette and the plain's far edge and the tree (outline, cross-hatched
canopy, light hatching on the trunk, shadow), and adds dashes on the plain. Lines are #c9c6bf on
transparent, like the other page art.

Usage: python3 trace_horizon_tree.py SRC.jpg OUT.svg PREVIEW.png [tree_x] [tree_scale]
  tree_x      x position of the trunk base in the 1080-wide drawing (photo: 270; live: 100)
  tree_scale  size of the tree relative to the photo (1.0)

Every line has its own opacity (stroke-opacity, on top of the page's pageArt opacity):
the mountains are dimmer than the rest; the plain's dashes fade from the bottom (heavy,
most visible) to the horizon (thin, faint). PREVIEW.png shows the drawing light-on-dark.

The thresholds (horizon search band rows 420-500, tree box x 215-375 / y 400-535) are specific
to the source photo; adjust them for another photo.
"""
import sys, random
import cv2, numpy as np

src, out_svg, out_png = sys.argv[1:4]
TX = float(sys.argv[4]) if len(sys.argv) > 4 else 270
TS = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0

im = cv2.imread(src)
H, W = im.shape[:2]
f = im.astype(float)
B, G, R = f[..., 0], f[..., 1], f[..., 2]
lum = f.mean(2)
TREE = (200, 390, 395, 545)            # x0, x1, y0, y1 in the photo
TRUNK_X0, TRUNK_Y0 = 266, 524          # trunk base in the photo

def smooth(a, k):
    k = int(k) | 1
    pad = np.pad(a, k // 2, mode="edge")
    return np.convolve(pad, np.ones(k) / k, mode="valid")

# --- horizon lines ---------------------------------------------------------------------
ground, mount = np.zeros(W), np.zeros(W)
for x in range(W):
    red = (R - B)[465:530, x] > 45                       # the plain is red-brown
    ok = red[:-2] & red[1:-1] & red[2:]
    ground[x] = 465 + np.argmax(ok)
    sky = np.median(lum[430:445, x])
    seg = lum[448:int(ground[x]), x]
    idx = np.where(seg < min(150, sky - 40))[0]           # mountains: clearly darker than the sky
    mount[x] = 448 + idx[0] if len(idx) else ground[x]
tree_cols = (np.arange(W) > TREE[0] - 8) & (np.arange(W) < TREE[1] + 8)
for a in (ground, mount):
    a[tree_cols] = np.interp(np.where(tree_cols)[0], np.where(~tree_cols)[0], a[~tree_cols])
ground = smooth(np.median(np.lib.stride_tricks.sliding_window_view(np.pad(ground, 7, mode="edge"), 15), 1), 21)
mount = smooth(np.median(np.lib.stride_tricks.sliding_window_view(np.pad(mount, 5, mode="edge"), 11), 1), 7)
mount = np.minimum(mount, ground - 1)

paths = []   # (points, width, opacity)

def poly(pts, eps=0.8):
    a = np.array(pts, np.float32).reshape(-1, 1, 2)
    return cv2.approxPolyDP(a, eps, False).reshape(-1, 2)

# --- horizon: dimmer than the rest, but visible --------------------------------------------
MOUNT_A, EDGE_A, MHATCH_A = 0.45, 0.55, 0.3
run = []
for x in range(W):
    if ground[x] - mount[x] > 3:
        run.append((x, mount[x]))
    elif run:
        if len(run) > 25: paths.append((poly(run), 1.0, MOUNT_A))
        run = []
if len(run) > 25: paths.append((poly(run), 1.0, MOUNT_A))
paths.append((poly([(x, ground[x]) for x in range(W)]), 1.0, EDGE_A))

rng = random.Random(4)
for x in range(0, W, 5):                       # slanted hatching so the mountains read as solid
    if ground[x] - mount[x] > 7 and rng.random() < 0.6:
        y0_ = mount[x] + 2 + rng.random() * 2
        y1_ = min(ground[x] - 1.5, y0_ + (ground[x] - mount[x]) * rng.uniform(0.4, 0.8))
        if y1_ - y0_ > 2: paths.append((np.array([(x, y0_), (x - (y1_ - y0_) * 0.5, y1_)]), 0.6, MHATCH_A))

# --- tree ------------------------------------------------------------------------------------
x0, x1, y0, y1 = TREE
crop = f[y0:y1, x0:x1]
cl = crop.mean(2)
cb, cg, cr = crop[..., 0], crop[..., 1], crop[..., 2]
mask = (((cg - cb > 6) & (cl < 165) & (cr - cb < 70)) | (cl < 75)).astype(np.uint8) * 255
mask[TRUNK_Y0 - y0:, :] = 0                                        # cut off the shadow
mask[474 - y0:, :240 - x0] = 0; mask[474 - y0:, 300 - x0:] = 0     # below the canopy: trunk only
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((4, 4), np.uint8))
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(mask)
keep = ((lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])) * 255).astype(np.uint8)
keep = ((cv2.GaussianBlur(keep, (3, 3), 0) > 110) * 255).astype(np.uint8)   # soften the outline
CANOPY_BOTTOM = 474 - y0                                           # rows below this: trunk

tree_paths = []
cs, _ = cv2.findContours(keep, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
for c in cs:
    if cv2.arcLength(c, True) < 30: continue
    p = cv2.approxPolyDP(c, 1.0, True).reshape(-1, 2).astype(float)
    tree_paths.append((np.vstack([p, p[:1]]) + (x0, y0), 1.0, 1.0))

# leaves: cross-hatching, the mountains' slanted strokes in both directions; a stroke is
# more likely to be kept where the canopy is darker (its shaded underside)
gray = cv2.cvtColor(im[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)
dark = cv2.GaussianBlur(gray, (0, 0), 3).astype(float)
canopy = cv2.erode(keep, np.ones((5, 5), np.uint8)); canopy[CANOPY_BOTTOM - 2:, :] = 0
ch, cw = canopy.shape
for slope in (-0.5, 0.5):                     # same slant as the mountain hatching, and mirrored
    for c in np.arange(-ch, cw + ch, 4.5):
        run = []
        for yy in np.arange(0, ch, 0.5):
            xx = c + slope * yy
            inside = 0 <= xx < cw and canopy[int(yy), int(xx)] > 0
            if inside: run.append((xx, yy))
            if (not inside or yy + 0.5 >= ch) and len(run) > 4:
                r0, r1 = np.array(run[0]), np.array(run[-1])
                L = np.hypot(*(r1 - r0))
                pos = 0.0
                while pos < L - 2:                    # break long runs into strokes with gaps
                    seg = rng.uniform(5, 12)
                    pa, pb = r0 + (r1 - r0) * pos / L, r0 + (r1 - r0) * min(L, pos + seg) / L
                    mx, my = (pa + pb) / 2
                    if rng.random() < 0.25 + 0.6 * max(0, (110 - dark[int(my), int(mx)]) / 70):
                        tree_paths.append((np.array([pa, pb]) + (x0, y0), 0.6, 0.6))
                    pos += seg + rng.uniform(2, 5)
            if not inside: run = []

# trunk: light tessellation, short slanted strokes across the trunk
for yy in range(CANOPY_BOTTOM + 1, TRUNK_Y0 - y0 - 2, 3):
    row = np.nonzero(keep[yy, 240 - x0:300 - x0])[0]
    if len(row) < 4 or rng.random() < 0.3: continue
    xa, xb = row[0] + 240 + 1.2, row[-1] + 240 - 1.2
    if xb - xa < 2: continue
    tree_paths.append((np.array([(xa, yy + y0 + 1.2), (xb, yy + y0 - 1.2)]), 0.45, 0.6))

# shadow under the tree: a flat ellipse of short horizontal strokes, denser near the trunk
for k in range(115):
    t = rng.uniform(0, 2 * np.pi); r = rng.random() ** 0.7
    cx = TRUNK_X0 - 24 + 82 * r * np.cos(t); cy = TRUNK_Y0 + 3 + 7.5 * r * np.sin(t)
    L = rng.uniform(5, 13) * (1.2 - 0.5 * r)
    tree_paths.append((np.array([(cx - L / 2, cy), (cx + L / 2, cy)]), 0.7, 0.8 - 0.35 * r))

def place(p):   # move/scale the tree about its trunk base, keeping the base on the ground
    gy = np.interp(TX, np.arange(W), ground)
    new_base = gy + (TRUNK_Y0 - ground[TRUNK_X0]) * TS   # depth below the plain edge scales too
    return (p - (TRUNK_X0, TRUNK_Y0)) * TS + (TX, new_base)

tree_paths = [(place(p), w, o) for p, w, o in tree_paths]
tmask = np.zeros((H, W), np.uint8)                 # where the placed tree stands
for p, w, o in tree_paths:
    if w >= 1.0 and len(p) > 3:
        cv2.fillPoly(tmask, [np.round(p).astype(np.int32)], 255)
tmask = cv2.dilate(tmask, np.ones((7, 7), np.uint8))

# --- plain: dashes, heavy and most visible at the bottom, thin and faint towards the horizon -
def free(xa, xb, yy):
    """split [xa, xb] at row yy around the tree"""
    seg, cur = [], None
    for xi in np.arange(xa, xb, 1.5):
        ok = 0 <= xi < W and 0 <= yy < H and tmask[int(yy), int(xi)] == 0
        if ok and cur is None: cur = xi
        if not ok and cur is not None: seg.append((cur, xi - 1.5)); cur = None
    if cur is not None: seg.append((cur, xb))
    return [(p, q) for p, q in seg if q - p > 2]

top = float(ground.max()) + 4
y, gap = top, 3.2                                   # rows spaced in perspective
while y < H - 2:
    t = (y - top) / (H - top)                       # 0 at the horizon, 1 at the bottom
    width = round(0.45 + 0.5 * t, 2)                # 0.45 far away -> 0.95 near
    alpha = round(0.25 + 0.75 * t ** 0.8, 2)        # faint far away -> full near
    x = rng.uniform(-10, 10)
    while x < W:
        L = rng.uniform(4, 14) * (1 + 1.6 * t)
        if rng.random() < 0.55:
            yy = y + rng.uniform(-0.8, 0.8)
            tilt = rng.uniform(-0.06, 0.06) * L
            for a_, b_ in free(x, min(x + L, W), yy):
                paths.append((np.array([(a_, yy), (b_, yy + tilt)]), width, alpha))
        x += L + rng.uniform(8, 24) * (1 + 1.5 * t)
    y += gap
    gap *= 1.08

def clip(p):
    """resample a polyline at ~1px and cut it where it crosses the placed tree"""
    out, cur = [], []
    for (ax, ay), (bx, by) in zip(p[:-1], p[1:]):
        n = max(1, int(np.hypot(bx - ax, by - ay)))
        for k in range(n + 1):
            x, y = ax + (bx - ax) * k / n, ay + (by - ay) * k / n
            if 0 <= y < H and 0 <= x < W and tmask[int(y), int(x)] > 0:
                if len(cur) > 1: out.append(np.array(cur))
                cur = []
            else:
                cur.append((x, y))
    if len(cur) > 1: out.append(np.array(cur))
    return [poly(q, 0.4) for q in out if np.hypot(*(q[-1] - q[0])) > 1.5]

paths = [(q, w, o) for p, w, o in paths for q in clip(p)] + tree_paths

# --- write -------------------------------------------------------------------------------------
def d(p): return "M" + "L".join("%.1f %.1f" % (a, b) for a, b in p)
groups = {}
for p, w, o in paths:
    groups.setdefault((round(w, 2), round(o, 1)), []).append(d(p))
svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H),
       '<g fill="none" stroke="#c9c6bf" stroke-linecap="round" stroke-linejoin="round">']
for (w, o), ds in sorted(groups.items()):
    op = "" if o >= 1 else ' stroke-opacity="%s"' % o
    svg.append('<path stroke-width="%s"%s d="%s"/>' % (w, op, "".join(ds)))
svg.append("</g></svg>")
open(out_svg, "w").write("".join(svg))

# preview: light lines on the page colour, at full strength (the page adds its own opacity)
S = 2
bg = np.array([32, 28, 27], float)                  # #1b1c20 in BGR
ink = np.array([191, 198, 201], float)              # #c9c6bf in BGR
prev = np.zeros((H * S, W * S, 3), float); prev[:] = bg
byop = {}
for p, w, o in paths:
    byop.setdefault(round(min(1, o), 1), []).append((p, w))
for o, items in sorted(byop.items()):           # one layer per opacity level
    layer = np.zeros((H * S, W * S), np.uint8)
    for p, w in items:
        cv2.polylines(layer, [np.round(p * S * 16).astype(np.int32)], False, 255,
                      max(1, int(round(w * S))), cv2.LINE_AA, shift=4)
    m = (layer / 255.0 * o)[..., None]
    prev = prev * (1 - m) + ink * m
cv2.imwrite(out_png, prev.astype(np.uint8))
print(out_svg, sum(len(v) for v in groups.values()), "paths")
