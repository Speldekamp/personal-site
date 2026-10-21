"""Cut a figure out of a flat-coloured background and make it greyscale (book1: the thesis-cover arrows).

    python3 cutout_figure.py PAGE.png OUT.webp --crop x0 y0 x1 y1 [--bg 55 95 130] [--tol 55] [--width 900]

Render the PDF page first, e.g. `pdftoppm -r 300 -png cover.pdf page`.
Pixels within --tol of the background colour are removed; the largest remaining shape is kept and
any background showing through inside it is filled back in. Output: greyscale with transparency.
"""
import argparse
import numpy as np, cv2
from PIL import Image, ImageOps

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--crop", type=int, nargs=4, required=True)
ap.add_argument("--bg", type=int, nargs=3, default=[55, 95, 130])
ap.add_argument("--tol", type=float, default=55)
ap.add_argument("--width", type=int, default=900)
a = ap.parse_args()

im = Image.open(a.src).convert("RGB").crop(tuple(a.crop))
px = np.asarray(im).astype(int)
mask = (np.sqrt(((px - np.array(a.bg)) ** 2).sum(2)) > a.tol).astype(np.uint8)
n, lab, st, _ = cv2.connectedComponentsWithStats(mask, 8)
mask = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
inv = (1 - mask).astype(np.uint8)
n2, lab2, st2, _ = cv2.connectedComponentsWithStats(inv, 4)
h, w = mask.shape
for i in range(1, n2):                               # fill holes that don't touch the border
    x, y, ww, hh, _ = st2[i]
    if x > 0 and y > 0 and x + ww < w and y + hh < h:
        mask[lab2 == i] = 1
alpha = cv2.GaussianBlur(mask.astype(np.float32) * 255, (3, 3), 0).astype(np.uint8)
out = Image.merge("LA", (ImageOps.grayscale(im), Image.fromarray(alpha))).convert("RGBA")
out = out.crop(Image.fromarray(alpha).getbbox())
out = out.resize((a.width, round(out.height * a.width / out.width)), Image.LANCZOS)
out.save(a.out, "WEBP", quality=80, method=6, alpha_quality=90)
print(a.out, out.size)
