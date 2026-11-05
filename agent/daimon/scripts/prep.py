#!/usr/bin/env python3
"""prep.py <image> <work_dir>
Writes full.jpg (long side 2048) and four overlapping quarter views (55% of each side) for close inspection."""
import os, sys
from PIL import Image, ImageOps

src, out = sys.argv[1], sys.argv[2]
os.makedirs(os.path.join(out, "crops"), exist_ok=True)
im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
W, H = im.size
print(f"{os.path.basename(src)}: {W}x{H} px, {os.path.getsize(src)/1e6:.1f} MB")

def save(img, name, long=2048):
    s = min(1.0, long / max(img.size))
    if s < 1:
        img = img.resize((round(img.size[0] * s), round(img.size[1] * s)), Image.LANCZOS)
    img.save(os.path.join(out, name), "JPEG", quality=90)

save(im, "full.jpg")
for name, x0, y0 in [("q_tl", 0, 0), ("q_tr", .45, 0), ("q_bl", 0, .45), ("q_br", .45, .45)]:
    box = (round(x0 * W), round(y0 * H), round((x0 + .55) * W), round((y0 + .55) * H))
    save(im.crop(box), name + ".jpg")
    print(f"{name}.jpg covers x {x0*100:.0f}-{(x0+.55)*100:.0f}%, y {y0*100:.0f}-{(y0+.55)*100:.0f}%")
