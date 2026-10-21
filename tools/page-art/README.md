# Page-art tools

Scripts used to make the faint background images on the paper pages (`pageArt` in a paper's
front matter; see `layouts/_default/single.html` and the page-art section of
`assets/css/extended/custom.css`). Hugo ignores this folder; nothing here is published.

Requirements: Python 3 with Pillow, NumPy, OpenCV (`cv2`); Node with Playwright for
`render_favicon.js`; `pdftoppm` (poppler) to turn PDF pages into images.

All site art uses the mid text colour `#c9c6bf` for lines, on a transparent background, so it
works on the dark page. The page sets the opacity (usually 0.16–0.22).

| Script | Used for | What it does |
| --- | --- | --- |
| `trace_photo.py` | paper3 (city photo) | Edge-traces a photo into simplified outlines (SVG + dark-on-white preview). Args: `SRC OUT.svg PREVIEW.png low high eps min_len` (used: `40 110 1.6 22`). **The sky mask (rows above y≈298, cloud band 298–350 except two tower columns) is specific to that photo — edit it for a new one.** |
| `declutter.py` | paper3 variants | Same trace, then removes clutter at chosen levels: more simplification, drops zig-zag scraps (turning per length), drops lines lying on or next to longer kept lines. Args: `SRC OUTDIR 'JSON levels'`. Variant C (live) used `{"name":"v40","eps":2.0,"min_len":30,"wiggle":15,"near":2.8,"overlap":0.46}`. Same photo-specific sky mask. |
| `finish_edges.py` | paper3 | Clips a traced SVG to an inset frame and joins nearby cut points along each edge, so buildings cut by the frame get a closing wall or base. Args: `IN.svg OUT.svg PREVIEW.png inset gap` (used: `10 26`). |
| `trace_horizon_tree.py` | paper4 (live) | Traces a photo of a lone tree on a plain: mountain ridge and plain edge (dimmed), tree outline with cross-hatched canopy, hatched trunk and shadow, and dashes on the plain that are heavy at the bottom and fade towards the horizon. Near the left, right and bottom edges all lines except the tree fade out, starting at a ragged distance from the edge. Each line has its own `stroke-opacity`. Args: `SRC OUT.svg PREVIEW.png tree_x tree_scale` (used: `100 1.0`, tree moved left so it clears the text column from about 1160px wide). Thresholds are specific to that photo. |
| `draw_campus.py` | paper2 | An original isometric line drawing of a tech-office district (towers, campus buildings, a round glass building, parks, parking, roads with cars, rooftop details, rooftop signs with simple invented marks; no real logos). Faces filled with the page colour for hidden lines; fades out through a blurred, ragged mask. Output slimmed (merged paths, one CSS fill rule). Args: `OUT.svg [seed]` (used: seed 3). Not traced from anything. |
| `draw_valley.py` | paper4 (earlier) | The previous hand-built (procedural) drawing of a hiker on a ledge over a river valley. Args: `OUT.svg PREVIEW.png`. Not traced from any photo. No longer used. |
| `triangle_band.py` | old7 title band | Builds the triangle band behind the title, each triangle filled with a faint map crop, thinning out at the bottom and sides. Args: `SRC_DIR OUT.png` where SRC_DIR holds the map crops named in the script. Convert the PNG to WebP afterwards. |
| `light_lines.py` | old7 maps, book2 map | Greyscale; dark ink → opaque light lines, paper → transparent. `--lossless --sharpen` gives the crisp Rome version. |
| `cutout_figure.py` | book1 | Cuts a figure out of a flat-coloured background (the thesis cover), greyscale with transparency. |
| `render_favicon.js` | favicons | Renders `static/favicon.svg` with Chromium to 16/32/48/180 px PNGs. Build `favicon.ico` from the 16/32/48 PNGs with Pillow (`save(..., sizes=[...], append_images=[...])`). |

The book2 Rome marker (large ring with a dark centre) was drawn onto the light-lines image with
Pillow at the Rome position of the source map; see the git history of
`content/papers/book2/bg-full.webp`.

Image rights: only use images the user owns or has licensed. Don't trace or clean up
watermarked stock previews; draw an original instead (as for the earlier paper4 drawing).

## trace_network_map.py (paper3)

`python3 trace_network_map.py SRC.png OUT.svg` turns the user's own flat-colour European cluster network map into a greyscale SVG: countries as faint fills (white borders kept as gaps), network lines found by testing every node pair, circles brightest (blue dimmest, green brighter, yellow near white, hatched yellow/purple kept as light/dark stripes), ragged blurred edge fade on land and lines. Colour thresholds are specific to that image. Used with opacity 0.3, fit width.
