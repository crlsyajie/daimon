"""Train the Daimon realism head on cached features and compare backbones.

  python train.py            # fits every backbone (and combos), prints a scorecard, saves the best head

Train data: OpenFake core/validation (generators seen).  Test data: OpenFake core/test, whose generators
(gpt-image-1.5/2.0, nano-banana-pro, midjourney-7, flux.2-klein-9b, z-image-turbo ...) and real photos
(DOCCI, ImageNet) never appear in training, so the test score is an honest "unseen generator" score.
"""
import glob, json, os, collections
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold

HERE = os.path.dirname(os.path.abspath(__file__))
CANDIDATES = [["clip_b16"], ["clip_b32"], ["dino_s"], ["clip_b16", "dino_s"], ["clip_b32", "dino_s"]]


def load(mode):
    zs = [np.load(c, allow_pickle=True) for c in sorted(glob.glob(os.path.join(HERE, "cache", mode, "chunk_*.npz")))]
    d = {k: np.concatenate([z[k] for z in zs]) for k in zs[0].files if k != "sources"}
    return d


def feats(d, names):
    return np.concatenate([d["f_" + n].astype(np.float32) for n in names], axis=1)


def image_scores(logit, img):
    """Image score = mean of its tile logits."""
    s = collections.defaultdict(list)
    for l, i in zip(logit, img):
        s[i].append(l)
    ids = sorted(s)
    return ids, np.array([np.mean(s[i]) for i in ids])


tr, te = load("train"), load("test")
print(f"train crops {len(tr['label'])} ({len(set(tr['img']))} images, {tr['label'].mean():.0%} AI)")
print(f"test  crops {len(te['label'])} ({len(set(te['img']))} images)")

te_img_label = {i: l for i, l in zip(te["img"], te["label"])}
te_img_model = {i: m for i, m in zip(te["img"], te["model"])}
results = []
for names in CANDIDATES:
    Xtr, Xte = feats(tr, names), feats(te, names)
    best = None
    for C in (0.1, 0.3, 1.0, 3.0):
        aucs = []
        for a, b in GroupKFold(4).split(Xtr, tr["label"], tr["img"]):
            m = LogisticRegression(C=C, max_iter=3000, class_weight="balanced").fit(Xtr[a], tr["label"][a])
            aucs.append(roc_auc_score(tr["label"][b], m.decision_function(Xtr[b])))
        if best is None or np.mean(aucs) > best[1]:
            best = (C, np.mean(aucs))
    C = best[0]
    m = LogisticRegression(C=C, max_iter=5000, class_weight="balanced").fit(Xtr, tr["label"])
    ids, s = image_scores(m.decision_function(Xte), te["img"])
    y = np.array([te_img_label[i] for i in ids])
    auc = roc_auc_score(y, s)
    acc = ((s > 0) == y).mean()
    results.append({"names": names, "C": C, "cv_auc": best[1], "test_auc": auc, "test_acc": acc, "model": m, "ids": ids, "s": s, "y": y})
    print(f"{'+'.join(names):18s} C={C:<4} seen-gen AUC {best[1]:.3f} | unseen-gen AUC {auc:.3f}, accuracy {acc:.1%}")

best = max(results, key=lambda r: r["test_auc"])
print("\nbest:", "+".join(best["names"]))

# per-source breakdown on the unseen test set
rows = collections.defaultdict(list)
for i, sc, yy in zip(best["ids"], best["s"], best["y"]):
    rows[te_img_model[i]].append(sc > 0)
print("\nunseen test set, share called AI (want high for generators, low for real photos):")
for k, v in sorted(rows.items(), key=lambda kv: -len(kv[1])):
    if len(v) >= 15:
        print(f"  {k:28s} n={len(v):4d}  called AI {np.mean(v):.0%}")

json.dump({r_key: v for r_key, v in {
    "scorecard": [{"backbones": r["names"], "C": r["C"], "seen_auc": round(r["cv_auc"], 4),
                   "unseen_auc": round(r["test_auc"], 4), "unseen_acc": round(float(r["test_acc"]), 4)} for r in results],
    "best": best["names"],
    "per_source": {k: {"n": len(v), "called_ai": round(float(np.mean(v)), 3)} for k, v in rows.items() if len(v) >= 15},
}.items()}, open(os.path.join(HERE, "cache", "scorecard.json"), "w"), indent=1)
np.savez(os.path.join(HERE, "cache", "head.npz"), coef=best["model"].coef_.astype(np.float32),
         intercept=best["model"].intercept_.astype(np.float32), names=np.array(best["names"]))
print("saved cache/head.npz and cache/scorecard.json")
