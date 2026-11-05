"""Shared image preparation for training and inference.

Every image goes through the same steps, so the model sees the same kind of input
at training time and when it checks your work:
  1. convert to RGB
  2. resize so the short side is SHORT_SIDE px (never upscale past 1.0)
  3. re-encode as JPEG, so a file's format (PNG vs JPEG) can't give the answer away
  4. cut CROP x CROP tiles; each tile gets its own score
"""
import io, random
from PIL import Image

SHORT_SIDE = 512
CROP = 224
JPEG_Q = 90

CLIP_MEAN = (0.48145466, 0.4578275, 0.40821073)
CLIP_STD = (0.26862954, 0.26130258, 0.27577711)


def canonical(img, short_side=SHORT_SIDE, quality=JPEG_Q):
    img = img.convert("RGB")
    w, h = img.size
    s = min(1.0, short_side / min(w, h))
    if s < 1.0:
        img = img.resize((max(CROP, round(w * s)), max(CROP, round(h * s))), Image.BICUBIC)
    if min(img.size) < CROP:
        s = CROP / min(img.size)
        img = img.resize((round(img.size[0] * s) + 1, round(img.size[1] * s) + 1), Image.BICUBIC)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=quality)
    buf.seek(0)
    return Image.open(buf).convert("RGB")


def train_view(img, rng=random):
    """Randomised version of canonical() so the model learns to ignore size and compression."""
    return canonical(img, short_side=rng.randint(448, 640), quality=rng.randint(75, 95))


def random_crops(img, n, rng=random):
    w, h = img.size
    out = []
    for _ in range(n):
        x = rng.randint(0, w - CROP)
        y = rng.randint(0, h - CROP)
        out.append(img.crop((x, y, x + CROP, y + CROP)))
    return out


def grid_crops(img, max_per_side=4):
    """Overlapping tiles covering the whole image. Returns [(crop, (x, y, w, h) in 0-1 units)]."""
    w, h = img.size

    def starts(length):
        n = min(max_per_side, max(1, -(-length // CROP)))
        if n == 1:
            return [(length - CROP) // 2]
        return [round(i * (length - CROP) / (n - 1)) for i in range(n)]

    out = []
    for y in starts(h):
        for x in starts(w):
            out.append((img.crop((x, y, x + CROP, y + CROP)), (x / w, y / h, CROP / w, CROP / h)))
    return out
