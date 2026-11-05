"""Stream OpenFake images, turn them into backbone features, and save only the features.

  python extract.py train 12000   # from core/validation (generators seen in training)
  python extract.py test 4000     # from core/test (generators held out: unseen)

Images are never written to disk. Progress is saved in chunks, so a stopped run resumes.
"""
import io, os, random, sys, time, glob, threading, queue
import numpy as np
import pyarrow.parquet as pq
from PIL import Image
from huggingface_hub import HfFileSystem

import common, backbones

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
REPO = "datasets/ComplexDataLab/OpenFake/core"
BACKBONES = ["clip_b16", "clip_b32", "dino_s"]
# Drawn/anime generators teach nothing about photorealism, so they are left out.
SKIP = ("anime", "illustrious", "ghibli", "animagine", "pony", "cartoon", "pixel", "toon", "manga", "noob")
CHUNK = 400

mode, target = sys.argv[1], int(sys.argv[2])
split = {"train": "validation", "test": "test"}[mode]
out_dir = os.path.join(CACHE, mode)
os.makedirs(out_dir, exist_ok=True)
rng = random.Random(7 if mode == "train" else 11)

fs = HfFileSystem()
shards = sorted(p for p in fs.ls(REPO, detail=False) if os.path.basename(p).startswith(split + "-"))
plan = []
for s in shards:
    n = pq.ParquetFile(fs.open(s, "rb")).metadata.num_row_groups
    plan += [(s, g) for g in range(n)]
rng.shuffle(plan)

done_chunks = sorted(glob.glob(os.path.join(out_dir, "chunk_*.npz")))
seen = set()
have = 0
for c in done_chunks:
    z = np.load(c, allow_pickle=True)
    seen.update(z["sources"].tolist())
    have += len(set(z["img"].tolist()))
plan = [p for p in plan if f"{p[0]}#{p[1]}" not in seen]
print(f"{mode}: {len(shards)} shards, {len(plan)} row groups left, {have} images already done", flush=True)

q = queue.Queue(maxsize=3)


def fetcher():
    for s, g in plan:
        for attempt in range(4):
            try:
                tb = pq.ParquetFile(fs.open(s, "rb")).read_row_group(g, columns=["image", "label", "model"])
                q.put((f"{s}#{g}", tb))
                break
            except Exception as e:
                print("retry", s, g, e, flush=True)
                time.sleep(5 * (attempt + 1))
    q.put(None)


threading.Thread(target=fetcher, daemon=True).start()
models = backbones.load(BACKBONES)

buf = {"feats": {n: [] for n in BACKBONES}, "img": [], "label": [], "model": [], "box": []}
sources = []
img_id = have
t0 = time.time()
chunk_no = len(done_chunks)


def flush():
    global chunk_no, buf, sources
    if not buf["img"]:
        return
    np.savez(os.path.join(out_dir, f"chunk_{chunk_no:04d}.npz"),
             **{f"f_{n}": np.concatenate(v).astype(np.float16) for n, v in buf["feats"].items()},
             img=np.array(buf["img"]), label=np.array(buf["label"]), model=np.array(buf["model"]),
             box=np.array(buf["box"], dtype=np.float32), sources=np.array(sources))
    chunk_no += 1
    buf = {"feats": {n: [] for n in BACKBONES}, "img": [], "label": [], "model": [], "box": []}
    sources = []


pending = 0
while img_id < target:
    item = q.get()
    if item is None:
        break
    src, tb = item
    crops, meta = [], []
    for im, lab, mdl in zip(tb["image"].to_pylist(), tb["label"].to_pylist(), tb["model"].to_pylist()):
        if lab == "fake" and any(k in mdl.lower() for k in SKIP):
            continue
        try:
            img = Image.open(io.BytesIO(im["bytes"]))
            img.load()
        except Exception:
            continue
        y = 1 if lab == "fake" else 0
        if mode == "train":
            v = common.train_view(img, rng)
            for c in common.random_crops(v, 2, rng):
                crops.append(c); meta.append((img_id, y, mdl, (0, 0, 0, 0)))
        else:
            v = common.canonical(img)
            for c, box in common.grid_crops(v, max_per_side=3):
                crops.append(c); meta.append((img_id, y, mdl, box))
        img_id += 1
        pending += 1
        if img_id >= target:
            break
    if crops:
        f = backbones.embed(models, crops)
        for n in BACKBONES:
            buf["feats"][n].append(f[n])
        for i, y, mdl, box in meta:
            buf["img"].append(i); buf["label"].append(y); buf["model"].append(mdl); buf["box"].append(box)
    sources.append(src)
    if pending >= CHUNK:
        flush(); pending = 0
        rate = (img_id - have) / (time.time() - t0)
        print(f"{mode}: {img_id}/{target} images, {rate:.1f}/s, ~{(target - img_id) / max(rate, 1e-6) / 60:.0f} min left", flush=True)
flush()
print(f"{mode}: finished with {img_id} images in {(time.time() - t0) / 60:.1f} min", flush=True)

os._exit(0)  # the download thread can keep Python alive; exit cleanly
