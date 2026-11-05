"""Frozen vision backbones whose features the Daimon head is trained on."""
import numpy as np
import torch

DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

SPECS = {
    # name: (loader, normalisation mean, std, feature size)
    "clip_b16": ("open_clip", "ViT-B-16-quickgelu", "openai"),
    "clip_b32": ("open_clip", "ViT-B-32-quickgelu", "openai"),
    "dino_s": ("hf", "facebook/dinov2-small", None),
}

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)
CLIP_MEAN = (0.48145466, 0.4578275, 0.40821073)
CLIP_STD = (0.26862954, 0.26130258, 0.27577711)


class Backbone(torch.nn.Module):
    """Takes a float tensor (B, 3, 224, 224) in 0-1 range, returns L2-normalised features."""

    def __init__(self, name):
        super().__init__()
        kind, arch, tag = SPECS[name]
        self.name = name
        if kind == "open_clip":
            import open_clip
            model, _, _ = open_clip.create_model_and_transforms(arch, pretrained=tag)
            self.net = model.visual
            mean, std = CLIP_MEAN, CLIP_STD
            self.kind = "clip"
        else:
            from transformers import AutoModel
            self.net = AutoModel.from_pretrained(arch)
            mean, std = IMAGENET_MEAN, IMAGENET_STD
            self.kind = "dino"
        self.register_buffer("mean", torch.tensor(mean).view(1, 3, 1, 1))
        self.register_buffer("std", torch.tensor(std).view(1, 3, 1, 1))
        self.eval()

    def forward(self, x):
        x = (x - self.mean) / self.std
        if self.kind == "clip":
            f = self.net(x)
        else:
            h = self.net(pixel_values=x).last_hidden_state
            f = torch.cat([h[:, 0], h[:, 1:].mean(1)], dim=1)
        return torch.nn.functional.normalize(f, dim=-1)


def to_tensor(crops):
    arr = np.stack([np.asarray(c, dtype=np.float32) / 255.0 for c in crops])
    return torch.from_numpy(arr).permute(0, 3, 1, 2).contiguous()


def load(names):
    return {n: Backbone(n).to(DEVICE) for n in names}


@torch.no_grad()
def embed(models, crops, batch=32):
    out = {n: [] for n in models}
    for i in range(0, len(crops), batch):
        x = to_tensor(crops[i:i + batch]).to(DEVICE)
        for n, m in models.items():
            out[n].append(m(x).float().cpu().numpy())
    return {n: np.concatenate(v) for n, v in out.items()}
