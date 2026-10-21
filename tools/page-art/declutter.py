"""Trace the city photo at several levels of decluttering.

Same edge trace as before, then per level:
- simplify each outline more (larger Douglas-Peucker tolerance),
- drop short scraps and zig-zag bits (lots of sharp turning per length; clean outlines are kept),
- drop lines that mostly run on top of / right next to lines already kept
  (longest lines are kept first), which removes the doubled edges and pile-ups.
Writes level SVGs (light lines, transparent) for the site, plus a dark-on-white preview each.
"""
import sys, json
import cv2, numpy as np

src, outdir = sys.argv[1], sys.argv[2]
levels = json.loads(sys.argv[3])     # list of {name, eps, min_len, wiggle, near, overlap}
S = 2
img = cv2.resize(cv2.imread(src), None, fx=S, fy=S, interpolation=cv2.INTER_CUBIC)
H, W = img.shape[:2]
g = cv2.bilateralFilter(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 9, 30, 7)
e = cv2.Canny(g, 40, 110, L2gradient=True)
e[: int(298 * S), :] = 0
keep_cols = np.zeros(W, bool); keep_cols[int(104*S):int(170*S)] = True; keep_cols[int(1008*S):] = True
e[int(298*S):int(350*S), ~keep_cols] = 0
contours, _ = cv2.findContours(e, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

def length(a): return float(np.sum(np.hypot(*np.diff(a, axis=0).T))) if len(a) > 1 else 0.0

stats = {}
for lv in levels:
    cand = []
    for c in contours:
        if cv2.arcLength(c, False) < lv["min_len"] * S: continue
        a = cv2.approxPolyDP(c, lv["eps"] * S, False).reshape(-1, 2).astype(float)
        if len(a) < 2: continue
        L = length(a)
        if L < lv["min_len"] * S: continue
        # zig-zag measure: total turning (radians) per 100px of line; clean outlines turn little
        v = np.diff(a, axis=0); ang = np.arctan2(v[:, 1], v[:, 0])
        turn = np.abs((np.diff(ang) + np.pi) % (2 * np.pi) - np.pi)
        turn = turn[turn > 0.35].sum()                 # ignore gentle bends
        if turn / (L / S) * 100 > lv["wiggle"]: continue
        cand.append((L, a))
    cand.sort(key=lambda t: -t[0])
    occ = np.zeros((H, W), np.uint8)
    r = int(lv["near"] * S)
    kept = []
    for L, a in cand:
        test = np.zeros((H, W), np.uint8)
        cv2.polylines(test, [a.astype(np.int32)], False, 255, 1)
        ys, xs = np.nonzero(test)
        if len(xs) == 0: continue
        covered = occ[ys, xs].mean() / 255.0
        if covered > lv["overlap"]: continue
        kept.append(a)
        cv2.polylines(occ, [a.astype(np.int32)], False, 255, 2 * r + 1)
    total = sum(length(a) for a in kept) / S
    stats[lv["name"]] = {"lines": len(kept), "length_px": round(total)}
    d = "".join("M" + "L".join(f"{x / S:.1f} {y / S:.1f}" for x, y in a) for a in kept)
    vw, vh = W // S, H // S
    open(f"{outdir}/{lv['name']}.raw.svg", "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vw} {vh}" width="{vw}" height="{vh}">'
        f'<path fill="none" stroke="#c9c6bf" stroke-width="0.9" stroke-linecap="round" stroke-linejoin="round" d="{d}"/></svg>')
print(json.dumps(stats))
