"""Greyscale line version of the user's European cluster network map (paper3).

Usage: python3 trace_network_map.py SRC.png OUT.svg [variant]
  variant "a" (default): countries as faint fills, coast as a line, network lines, circles.

Reads the user's flat-colour map: pale-blue land with white borders, grey network
lines, blue / green / yellow / hatched (yellow, purple) circles. Thresholds are
specific to that image.
"""
import sys, numpy as np, cv2
from scipy import ndimage as ndi

src, out = sys.argv[1], sys.argv[2]
im = cv2.cvtColor(cv2.imread(src), cv2.COLOR_BGR2RGB).astype(int)
H, W = im.shape[:2]
R, G, B = im[..., 0], im[..., 1], im[..., 2]
lum = (R + G + B) / 3
def near(c, t): return (abs(R-c[0]) + abs(G-c[1]) + abs(B-c[2])) < t

# ---- nodes ---------------------------------------------------------------
nodes = []  # (x, y, r, kind)
def comps(mask, kind, minarea, r):
    lab, n = ndi.label(mask)
    for i in range(1, n+1):
        a = (lab == i).sum()
        if a < minarea: continue
        cy, cx = ndi.center_of_mass(lab == i)
        nodes.append((cx, cy, r, kind))
comps(near((86,191,225),60), 'blue', 300, 12)
comps(near((0,153,70),90), 'green', 500, 15)
comps(near((243,206,0),90), 'yellow', 500, 15)
# hatched circles: group stripe pieces
for kind, m in [('hatch-yellow', near((243,206,0),90)), ('hatch-purple', (B>180)&(R<170)&(G<80))]:
    lab, n = ndi.label(m)
    pts = [ndi.center_of_mass(lab==i) for i in range(1,n+1) if 30 < (lab==i).sum() < 200]
    if pts:
        cy, cx = np.mean(pts, axis=0); nodes.append((cx, cy, 15, kind))

# ---- network lines: test every node pair ---------------------------------
dark = (lum < 238) & ~near((86,191,225),120)
dark = cv2.dilate(dark.astype(np.uint8), np.ones((3,3),np.uint8)) > 0
edges = []
for i in range(len(nodes)):
    for j in range(i+1, len(nodes)):
        (x1,y1,r1,_),(x2,y2,r2,_) = nodes[i], nodes[j]
        d = np.hypot(x2-x1, y2-y1)
        if d < 10: continue
        ts = np.arange(r1+9, d-r2-9, 2) / d
        if len(ts) < 3: continue
        xs, ys = x1 + (x2-x1)*ts, y1 + (y2-y1)*ts
        # skip if the segment runs through another node (it's two edges then)
        blocked = any(k not in (i,j) and np.min(np.hypot(xs-nodes[k][0], ys-nodes[k][1])) < nodes[k][2]+2 for k in range(len(nodes)))
        if blocked: continue
        if dark[ys.round().astype(int).clip(0,H-1), xs.round().astype(int).clip(0,W-1)].mean() > 0.9:
            edges.append((i, j))

# ---- land ----------------------------------------------------------------
pale = (lum > 236) & (lum < 252) & (B - R >= 10)
nodemask = np.zeros((H,W), np.uint8)
for x,y,r,k in nodes: cv2.circle(nodemask, (int(x),int(y)), r+10, 1, -1)
linemask = (lum < 240) & ~pale
countries = (pale | (linemask & (cv2.dilate(pale.astype(np.uint8), np.ones((5,5),np.uint8))>0)) | (nodemask>0)).astype(np.uint8)
countries = cv2.morphologyEx(countries, cv2.MORPH_OPEN, np.ones((2,2),np.uint8))
land = cv2.morphologyEx(countries, cv2.MORPH_CLOSE, np.ones((7,7),np.uint8))
land = ndi.binary_fill_holes(land) & cv2.morphologyEx(land, cv2.MORPH_CLOSE, np.ones((7,7),np.uint8)).astype(bool)

def paths(mask, eps, mode):
    cs, _ = cv2.findContours(mask.astype(np.uint8), mode, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cs:
        if cv2.contourArea(c) < 60: continue
        p = cv2.approxPolyDP(c, eps, True)[:,0]
        out.append('M' + 'L'.join(f'{a},{b}' for a,b in p) + 'Z')
    return out

fill_d = ' '.join(paths(countries, 1.2, cv2.RETR_CCOMP))
coast_d = ' '.join(paths(land, 1.5, cv2.RETR_LIST))

# ---- ragged edge fade (mask) ---------------------------------------------
rng = np.random.default_rng(7)
def ragged():
    pts = []
    for side in range(4):
        for t in np.linspace(0, 1, 14, endpoint=False):
            inset = 70 + rng.uniform(0, 90)
            if side == 0: pts.append((inset + t*(W-2*inset), 60))           # top: nothing there, small inset
            elif side == 1: pts.append((W - inset, 60 + t*(H-120)))
            elif side == 2: pts.append((W - inset - t*(W-2*inset), H - inset*0.6))
            else: pts.append((inset*0.5, H - 60 - t*(H-120)))
    return 'M' + 'L'.join(f'{x:.0f},{y:.0f}' for x,y in pts) + 'Z'

# ---- SVG ---------------------------------------------------------------
INK, LIGHT = '#c9c6bf', '#f0ede6'
shade = {'blue': (INK, .45), 'green': (INK, .8), 'yellow': (LIGHT, 1.0)}
o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
     '<defs><filter id="b" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="45"/></filter>',
     f'<mask id="m" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><path d="{ragged()}" fill="#fff" filter="url(#b)"/></mask>',
     f'<pattern id="hy" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="6" fill="{INK}" fill-opacity=".35"/><rect width="3" height="6" fill="{LIGHT}"/></pattern>',
     f'<pattern id="hp" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="6" fill="{INK}" fill-opacity=".08"/><rect width="3" height="6" fill="{INK}" fill-opacity=".42"/></pattern>',
     '</defs>',
     f'<g mask="url(#m)">',
     f'<path d="{fill_d}" fill="{INK}" fill-opacity=".09" fill-rule="evenodd"/>',
     f'<path d="{coast_d}" fill="none" stroke="{INK}" stroke-opacity=".32" stroke-width="1.3" stroke-linejoin="round"/>',
     f'<g stroke="{INK}" stroke-opacity=".5" stroke-width="1.3" stroke-linecap="round">']
for i,j in edges:
    o.append(f'<line x1="{nodes[i][0]:.1f}" y1="{nodes[i][1]:.1f}" x2="{nodes[j][0]:.1f}" y2="{nodes[j][1]:.1f}"/>')
o.append('</g></g><g>')
for x,y,r,k in nodes:
    if k == 'blue':
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="19" fill="{INK}" fill-opacity=".12"/>')
    if k.startswith('hatch'):
        pat = 'hy' if k == 'hatch-yellow' else 'hp'
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="url(#{pat})" stroke="{INK}" stroke-opacity=".7" stroke-width="1.2"/>')
    else:
        c, a = shade[k]
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{c}" fill-opacity="{a}"/>')
o.append('</g></svg>')
open(out, 'w').write('\n'.join(o))
print(len(nodes), 'nodes', len(edges), 'edges')
