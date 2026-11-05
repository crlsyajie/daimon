# Daimon local realism model

An offline model that scores how strongly each part of a photo reads as AI-generated, and draws a heatmap of
the worst areas. It's meant as a fast, free pre-check before the full Daimon review.

## Status: paused, not trained yet

- **Streamed so far:** features for 2,595 of the planned 12,000 training images, saved in `cache/train/` (19 MB).
- **Still to do:** the rest of the training images, the 4,000 test images, training, and export.
- **Missing file:** the model file `daimon_realism.onnx` doesn't exist yet.

## How it works

- **Data:** [OpenFake v2](https://huggingface.co/datasets/ComplexDataLab/OpenFake) (CC BY-NC 4.0). It has real
  photos plus images from Nano Banana, GPT Image, Flux.2, Midjourney, Seedream, Veo and Kling frames, and many more.
  Anime and illustration generators are left out.
- **Training images:** taken from `core/validation`.
- **Test images:** taken from `core/test`, whose generators and real-photo sources never appear in training. That
  makes the test score an honest score on unseen generators.
- **Images are never saved:** each one is streamed and cut into 224 px tiles. Only the tiles' features from frozen
  base models are kept: CLIP ViT-B/16, CLIP ViT-B/32 and DINOv2-small.
- **Training:** a linear head is trained on each base model and on combinations of them, and the one that scores
  best on unseen generators wins.
- **Export:** the winning base model and head become one `daimon_realism.onnx`, kept under 100 MB, using int8
  weights if needed.

## Resume

Use Python 3.12. Feature extraction picks up where it stopped: row groups already done are skipped.

```bash
pip install torch torchvision open_clip_torch transformers pyarrow fsspec huggingface_hub onnx onnxruntime onnxscript scikit-learn pillow numpy
cd model
python extract.py train 12000
python extract.py test 4000
python train.py
python export.py
```

## Use, once trained

```bash
python daimon_check.py photo.jpg --out results/
```

It prints a 0–100 AI-likeness score and the most AI-looking areas. It also writes `<name>_daimon.png` (the heatmap)
and `<name>_daimon.json`. It needs only `onnxruntime`, `pillow` and `numpy`.

## Limits

- A detector picks up traces of generation that people can't see. A high score means "a detector would catch
  this", which isn't the same as "an audience would notice". Daimon's full review judges the second.
- The training data is licensed for non-commercial use only, so the model is too.
