"""Turn a dark-on-light image (map, line drawing) into faint light lines on a transparent background.

Used for the MicRO maps (old7) and the Roads to Rome map (book2).
Greyscale; ink becomes opaque light grey (#c9c6bf), paper becomes transparent.

    python3 light_lines.py IN.png OUT.webp [--width 1600] [--paper 236] [--gain 1.45] [--lossless]

--paper  grey level at and above which a pixel counts as paper (fully transparent)
--gain   how fast darker ink becomes opaque
"""
import argparse
from PIL import Image, ImageOps, ImageFilter

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--width", type=int, default=0)
ap.add_argument("--paper", type=int, default=236)
ap.add_argument("--gain", type=float, default=1.45)
ap.add_argument("--sharpen", action="store_true")
ap.add_argument("--lossless", action="store_true", help="lossless WebP with 8 alpha levels (crisp thin lines)")
a = ap.parse_args()

g = ImageOps.grayscale(Image.open(a.src).convert("RGB"))
if a.width and g.width != a.width:
    g = g.resize((a.width, round(g.height * a.width / g.width)), Image.LANCZOS)
if a.sharpen:
    g = g.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))
alpha = g.point(lambda v: 0 if v >= a.paper else min(255, int((a.paper - v) * a.gain)))
if a.lossless:
    alpha = alpha.point(lambda v: 0 if v < 16 else min(255, round(v / (255 / 7)) * round(255 / 7)))
out = Image.new("RGBA", g.size, (201, 198, 191, 0))
out.putalpha(alpha)
if a.lossless:
    out.save(a.out, "WEBP", lossless=True, method=6)
else:
    out.save(a.out, "WEBP", quality=60, method=6, alpha_quality=60)
print(a.out, out.size)
