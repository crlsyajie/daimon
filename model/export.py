"""Export backbone(s) + trained head as one ONNX file: daimon_realism.onnx

Input  "tiles": float32 (N, 3, 224, 224), RGB in 0-1 range (made by common.canonical + common.grid_crops)
Output "logit": float32 (N,), > 0 means the tile reads as AI-generated

If the file would be over GitHub's 100 MB limit, weights are stored as int8 (dynamic quantization)
and the export checks that the scores still agree with the full-precision model.
"""
import json, os, sys, glob
import numpy as np
import torch
import onnxruntime as ort

import backbones, common
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "daimon_realism.onnx")
LIMIT_MB = 95

h = np.load(os.path.join(HERE, "cache", "head.npz"))
names = h["names"].tolist()


class Daimon(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.bbs = torch.nn.ModuleList([backbones.Backbone(n) for n in names])
        self.head = torch.nn.Linear(h["coef"].shape[1], 1)
        with torch.no_grad():
            self.head.weight.copy_(torch.from_numpy(h["coef"]))
            self.head.bias.copy_(torch.from_numpy(h["intercept"]))

    def forward(self, tiles):
        f = torch.cat([b(tiles) for b in self.bbs], dim=1)
        return self.head(f).squeeze(1)


model = Daimon().eval()

# sample tiles from local images to check the export against PyTorch
samples = sys.argv[1:] or glob.glob(os.path.expanduser("~/Documents/Claude Folder/QA Reviews/*/media/*.jpg"))
tiles = []
for p in samples[:6]:
    tiles += [c for c, _ in common.grid_crops(common.canonical(Image.open(p)), 4)]
x = backbones.to_tensor(tiles)
with torch.no_grad():
    ref = model(x).numpy()

fp32 = OUT.replace(".onnx", ".fp32.onnx")
torch.onnx.export(model, x[:2], fp32, input_names=["tiles"], output_names=["logit"],
                  dynamic_axes={"tiles": {0: "n"}, "logit": {0: "n"}}, opset_version=17, dynamo=False)


def check(path):
    s = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
    got = s.run(None, {"tiles": x.numpy()})[0]
    return float(np.abs(got - ref).max()), float(np.corrcoef(got, ref)[0, 1]), float(((got > 0) == (ref > 0)).mean())


size = os.path.getsize(fp32) / 1e6
print(f"fp32 export {size:.0f} MB, check vs PyTorch (max diff, corr, same call): {check(fp32)}")
if size <= LIMIT_MB:
    os.replace(fp32, OUT)
else:
    from onnxruntime.quantization import quantize_dynamic, QuantType
    quantize_dynamic(fp32, OUT, weight_type=QuantType.QInt8)
    os.remove(fp32)
    print(f"int8 export {os.path.getsize(OUT)/1e6:.0f} MB, check vs PyTorch (max diff, corr, same call): {check(OUT)}")

card = json.load(open(os.path.join(HERE, "cache", "scorecard.json")))
meta = {
    "name": "daimon-realism", "version": "1.0",
    "backbones": names, "input": "tiles float32 (N,3,224,224) RGB 0-1", "output": "logit per tile, >0 = reads as AI",
    "prep": {"short_side": common.SHORT_SIDE, "jpeg_quality": common.JPEG_Q, "tile": common.CROP},
    "trained_on": "OpenFake v2 core/validation (CC BY-NC 4.0), anime/illustration generators excluded",
    "scorecard": card,
}
json.dump(meta, open(os.path.join(HERE, "daimon_realism.json"), "w"), indent=1)
print("wrote", OUT, f"{os.path.getsize(OUT)/1e6:.0f} MB", "and daimon_realism.json")
