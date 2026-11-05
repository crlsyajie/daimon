#!/usr/bin/env python3
"""crop.py <image> <x%> <y%> <w%> <h%> <out.jpg>
Crops a region given as percentages of the frame (x, y = top-left corner) at full resolution."""
import os, sys
from PIL import Image, ImageOps

src, x, y, w, h, out = sys.argv[1], *map(float, sys.argv[2:6]), sys.argv[6]
im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
W, H = im.size
box = (max(0, round(x / 100 * W)), max(0, round(y / 100 * H)),
       min(W, round((x + w) / 100 * W)), min(H, round((y + h) / 100 * H)))
c = im.crop(box)
if max(c.size) < 768:  # small regions are enlarged so detail is visible
    s = 768 / max(c.size)
    c = c.resize((round(c.size[0] * s), round(c.size[1] * s)), Image.LANCZOS)
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
c.save(out, "JPEG", quality=92)
print(out, c.size)
