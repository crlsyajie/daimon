#!/usr/bin/env python3
"""Daimon local check: score how strongly a photo reads as AI-generated, tile by tile, fully offline.

  python daimon_check.py photo.jpg [more.jpg ...] [--out results/]

Needs only: onnxruntime, pillow, numpy.
Writes <name>_daimon.png (heatmap of the tiles that read most AI) and <name>_daimon.json, and prints a summary.
"""
import argparse, json, math, os, sys
import numpy as np
import onnxruntime as ort
from PIL import Image, ImageDraw, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402

BANDS = [(35, "Reads as real"), (65, "Borderline: some areas read as AI"), (101, "Reads as AI")]


def check(sess, path, out_dir):
    src = ImageOps.exif_transpose(Image.open(path))
    img = common.canonical(src)
    tiles = common.grid_crops(img, max_per_side=4)
    x = np.stack([np.asarray(c, dtype=np.float32) / 255.0 for c, _ in tiles]).transpose(0, 3, 1, 2)
    logits = sess.run(None, {"tiles": x})[0]
    probs = 1 / (1 + np.exp(-logits))
    score = round(100 / (1 + math.exp(-float(np.mean(logits)))))
    label = next(t for lim, t in BANDS if score < lim)

    # heatmap: average tile probabilities over the pixels each tile covers
    W, H = img.size
    acc, cnt = np.zeros((H, W)), np.zeros((H, W))
    for (c, (bx, by, bw, bh)), p in zip(tiles, probs):
        x0, y0 = round(bx * W), round(by * H)
        acc[y0:y0 + common.CROP, x0:x0 + common.CROP] += p
        cnt[y0:y0 + common.CROP, x0:x0 + common.CROP] += 1
    heat = acc / np.maximum(cnt, 1)
    view = src.convert("RGB").resize((W, H))
    red = np.zeros((H, W, 4), dtype=np.uint8)
    red[..., 0] = 230
    red[..., 1] = 40
    red[..., 2] = 40
    red[..., 3] = (np.clip((heat - 0.5) * 2, 0, 1) * 150).astype(np.uint8)
    over = Image.alpha_composite(view.convert("RGBA"), Image.fromarray(red, "RGBA")).convert("RGB")
    d = ImageDraw.Draw(over)
    order = np.argsort(-probs)
    hot = []
    for k in order[:3]:
        bx, by, bw, bh = tiles[k][1]
        if probs[k] < 0.5:
            break
        d.rectangle([bx * W, by * H, (bx + bw) * W, (by + bh) * H], outline=(255, 230, 0), width=3)
        hot.append({"x": round(bx * 100, 1), "y": round(by * 100, 1), "w": round(bw * 100, 1), "h": round(bh * 100, 1),
                    "ai": round(float(probs[k]) * 100)})
    d.rectangle([0, 0, W, 34], fill=(20, 23, 28))
    d.text((10, 10), f"Daimon local check  {score}/100 AI-likeness  {label}", fill=(255, 255, 255))

    base = os.path.splitext(os.path.basename(path))[0]
    os.makedirs(out_dir, exist_ok=True)
    png = os.path.join(out_dir, base + "_daimon.png")
    over.save(png)
    result = {"file": path, "ai_likeness": score, "verdict": label, "hot_areas_percent": hot,
              "tiles": [{"box_percent": [round(v * 100, 1) for v in b], "ai": round(float(p) * 100)} for (_, b), p in zip(tiles, probs)]}
    json.dump(result, open(os.path.join(out_dir, base + "_daimon.json"), "w"), indent=1)
    return result, png


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("images", nargs="+")
    ap.add_argument("--out", default="daimon_results")
    ap.add_argument("--model", default=os.path.join(HERE, "daimon_realism.onnx"))
    a = ap.parse_args()
    sess = ort.InferenceSession(a.model, providers=["CPUExecutionProvider"])
    for p in a.images:
        r, png = check(sess, p, a.out)
        hot = ", ".join(f"x{h['x']:.0f}% y{h['y']:.0f}% ({h['ai']}%)" for h in r["hot_areas_percent"]) or "none"
        print(f"{os.path.basename(p)}: {r['ai_likeness']}/100 AI-likeness - {r['verdict']}\n  most AI-looking areas: {hot}\n  heatmap: {png}")


if __name__ == "__main__":
    main()
