"""Finish the traced city at the image edges.

Every polyline is clipped to a slightly inset frame (left, right, bottom; the sky at the top is
empty anyway). Where buildings are cut by the frame, the cut points that lie close together on
the same edge are joined by a line along that edge, so each cut-off building gets a closing wall
or base instead of stopping in mid-air. Wide gaps (streets, open space) stay open, which keeps the
finish irregular rather than a full picture frame.
"""
import re, sys
import numpy as np, cv2

src, out_svg, out_png = sys.argv[1:4]
INSET, GAP = float(sys.argv[4]), float(sys.argv[5])

svg = open(src).read()
vw, vh = (float(v) for v in re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg).groups())
d = re.search(r' d="([^"]+)"', svg).group(1)
polys = []
for part in d.split("M")[1:]:
    pts = [tuple(map(float, p.split())) for p in part.split("L")]
    polys.append(pts)

X0, X1, Y1 = INSET, vw - INSET, vh - INSET
def inside(p): return X0 <= p[0] <= X1 and p[1] <= Y1

def clip_seg(a, b):
    """Liang-Barsky against x in [X0, X1], y <= Y1. Returns (p, q, t0, t1) or None."""
    (x1, y1), (x2, y2) = a, b
    dx, dy = x2 - x1, y2 - y1
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x1 - X0), (dx, X1 - x1), (dy, Y1 - y1)):
        if p == 0:
            if q < 0: return None
        else:
            t = q / p
            if p < 0:
                if t > t1: return None
                t0 = max(t0, t)
            else:
                if t < t0: return None
                t1 = min(t1, t)
    return (x1 + t0 * dx, y1 + t0 * dy), (x1 + t1 * dx, y1 + t1 * dy), t0, t1

out_polys, cuts = [], {"left": [], "right": [], "bottom": []}
def note_cut(p):
    if abs(p[0] - X0) < 1e-6: cuts["left"].append(p[1])
    elif abs(p[0] - X1) < 1e-6: cuts["right"].append(p[1])
    elif abs(p[1] - Y1) < 1e-6: cuts["bottom"].append(p[0])

for pts in polys:
    cur = []
    for a, b in zip(pts, pts[1:]):
        r = clip_seg(a, b)
        if r is None:
            if cur: out_polys.append(cur); cur = []
            continue
        p, q, t0, t1 = r
        if t0 > 0:                                   # entering the frame
            if cur: out_polys.append(cur)
            cur = [p]; note_cut(p)
        elif not cur:
            cur = [p]
        cur.append(q)
        if t1 < 1:                                   # leaving the frame
            note_cut(q); out_polys.append(cur); cur = []
    if len(cur) >= 2: out_polys.append(cur)

caps = []
for side, vals in cuts.items():
    vals = sorted(vals)
    run = []
    for v in vals + [None]:
        if run and (v is None or v - run[-1] > GAP):
            if len(run) >= 2 and run[-1] - run[0] > 2:
                a, b = run[0], run[-1]
                caps.append([(X0, a), (X0, b)] if side == "left" else
                            [(X1, a), (X1, b)] if side == "right" else [(a, Y1), (b, Y1)])
            run = []
        if v is not None: run.append(v)
print("polylines:", len(out_polys), "edge caps:", len(caps), {k: len(v) for k, v in cuts.items()})

path = "".join("M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pl) for pl in out_polys + caps if len(pl) >= 2)
open(out_svg, "w").write(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vw:.0f} {vh:.0f}" width="{vw:.0f}" height="{vh:.0f}">'
    f'<path fill="none" stroke="#c9c6bf" stroke-width="0.9" stroke-linecap="round" stroke-linejoin="round" d="{path}"/></svg>')
S = 2
prev = np.full((int(vh * S), int(vw * S)), 255, np.uint8)
for pl in out_polys + caps:
    cv2.polylines(prev, [np.array([(x * S, y * S) for x, y in pl], np.int32)], False, 35, 2, cv2.LINE_AA)
cv2.imwrite(out_png, cv2.resize(prev, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))
