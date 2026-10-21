"""Build the triangle band that sits behind the paper title.

Whole triangles in alternating up/down rows (the pattern from B.pdf page 1), each showing a
faint greyscale map crop; the spaces between triangles are fully transparent. The band thins
out irregularly towards the bottom (the date line) and towards the sides.
"""
import math, random, sys
from PIL import Image, ImageDraw, ImageOps

src_dir, out_path = sys.argv[1], sys.argv[2]
random.seed(11)

SCALE = 2                      # render at 2x for sharp edges on retina screens
W, H = 820, 192                # band size in CSS px
S = 44                         # triangle side before shrinking (CSS px)
SHRINK = 0.80                  # leaves even gaps between neighbours
ROWS = 5

# textures: the three maps, greyscale, ink -> light grey with alpha (paper transparent)
def texture(name):
    g = ImageOps.grayscale(Image.open(f"{src_dir}/{name}").convert("RGB"))
    g.thumbnail((1400, 1400), Image.LANCZOS)
    return ImageOps.invert(g)
pool = [texture("A-crop.png"), texture("Chi-crop.png"), texture("C2-crop.png")]

band = Image.new("RGBA", (W * SCALE, H * SCALE), (0, 0, 0, 0))
h = S * math.sqrt(3) / 2
cols = int(W / (S / 2)) + 2
for r in range(ROWS):
    y0 = r * h
    for i in range(-1, cols):
        up = (i + r) % 2 == 0
        x0 = i * S / 2
        pts = [(x0, y0 + h), (x0 + S, y0 + h), (x0 + S / 2, y0)] if up else \
              [(x0, y0), (x0 + S, y0), (x0 + S / 2, y0 + h)]
        if min(p[0] for p in pts) < 0 or max(p[0] for p in pts) > W:
            continue                                   # whole triangles only
        cx = sum(p[0] for p in pts) / 3; cy = sum(p[1] for p in pts) / 3
        pts = [(cx + (px - cx) * SHRINK, cy + (py - cy) * SHRINK) for px, py in pts]
        # organic falloff: weaker and sparser further down and towards the sides
        down = [0.85, 0.8, 0.72, 0.55, 0.3][r]
        edge = min(cx, W - cx) / 170.0
        side = max(0.0, min(1.0, edge))
        strength = down * (0.35 + 0.65 * side) * random.uniform(0.55, 1.0)
        keep = [0.97, 0.93, 0.88, 0.62, 0.3][r] * (0.45 + 0.55 * side)
        if random.random() > keep or strength < 0.08:
            continue
        # map crop for this triangle
        tex = random.choice(pool)
        tw = int(S * SCALE * random.uniform(1.4, 2.2))
        tx = random.randint(0, tex.width - tw); ty = random.randint(0, tex.height - tw)
        patch = tex.crop((tx, ty, tx + tw, ty + tw)).resize((int(S * SCALE), int(S * SCALE)), Image.LANCZOS)
        # alpha: faint base tint so the shape reads + the map lines on top
        alpha = patch.point(lambda v, s=strength: int(min(255, (22 + v * 0.75) * s)))
        mask = Image.new("L", band.size, 0)
        sp = [(px * SCALE, py * SCALE) for px, py in pts]
        ImageDraw.Draw(mask).polygon(sp, fill=255)
        bx = int(min(p[0] for p in sp)); by = int(min(p[1] for p in sp))
        layer_a = Image.new("L", band.size, 0); layer_a.paste(alpha, (bx, by))
        tri_a = Image.composite(layer_a, Image.new("L", band.size, 0), mask)
        colour = Image.new("RGBA", band.size, (201, 198, 191, 0)); colour.putalpha(tri_a)
        band = Image.alpha_composite(band, colour)

band.save(out_path, optimize=True)
print("saved", band.size)
