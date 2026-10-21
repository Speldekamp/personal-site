"""Trace the photo's building edges into a simplified SVG line drawing.

Edges are found on a smoothed, upscaled copy, followed as contours and simplified into
straight-segment polylines (Douglas-Peucker), so buildings come out as clean outlines.
The sky is left empty. Output: an SVG with light lines on a transparent background,
plus a dark-on-white preview PNG.
"""
import sys
import cv2, numpy as np

src, out_svg, out_png = sys.argv[1:4]
low, high, eps, min_len = (float(v) for v in sys.argv[4:8])
S = 2
img = cv2.resize(cv2.imread(src), None, fx=S, fy=S, interpolation=cv2.INTER_CUBIC)
H, W = img.shape[:2]
g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
g = cv2.bilateralFilter(g, 9, 30, 7)
e = cv2.Canny(g, low, high, L2gradient=True)
e[: int(298 * S), :] = 0                                   # sky and clouds stay empty
keep_cols = np.zeros(W, bool); keep_cols[int(104*S):int(170*S)] = True; keep_cols[int(1008*S):] = True
e[int(298*S):int(350*S), ~keep_cols] = 0                   # cloud streaks on the horizon, except the two towers
cs, _ = cv2.findContours(e, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
polys = []
for c in cs:
    if cv2.arcLength(c, False) < min_len * S:
        continue
    a = cv2.approxPolyDP(c, eps * S, False).reshape(-1, 2)
    if len(a) >= 2:
        polys.append(a)
print("contours:", len(cs), "kept:", len(polys))
d = []
for a in polys:
    d.append("M" + "L".join(f"{x / S:.1f} {y / S:.1f}" for x, y in a))
vw, vh = W // S, H // S
open(out_svg, "w").write(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vw} {vh}" width="{vw}" height="{vh}">'
    f'<path fill="none" stroke="#c9c6bf" stroke-width="0.9" stroke-linecap="round" stroke-linejoin="round" d="{"".join(d)}"/></svg>')
prev = np.full((H, W), 255, np.uint8)
for a in polys:
    cv2.polylines(prev, [a.astype(np.int32)], False, 35, 2, cv2.LINE_AA)
cv2.imwrite(out_png, cv2.resize(prev, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))
