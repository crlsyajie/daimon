# Daimon

A strict realism QA checker for AI-made photos and videos, built as a Claude artifact.

Upload a photo or video, pick a mode, and Claude reviews it the way a hard-to-please director would. The standard is simple: the audience should only know it's AI if the creator tells them.

## What a review gives you

- **A PASS or FAIL verdict.** Any single fail means FAIL.
- **Markers on the frame** for every problem, each with a close-up crop.
- **For each problem:** what's wrong, why it gives the image away, how to fix it, and a fix prompt ready to copy.
- **Strengths**, so you know what to keep.
- **A 20-person panel** that scores the piece. There are five each of film directors, cinematographers, photographers and VFX supervisors, each judging by their own documented working habits.
- **Usage:** estimated tokens for each review, plus a log of the reviews you've run on that device.

## Modes

| Mode | Standard |
|---|---|
| Photoreal | Must pass as a real photo or real footage. |
| Hybrid | Realism with CGI is fine, but the people must be real and nothing can be hallucinated. |
| 3D / stylized | May look rendered, but nothing can be hallucinated. |

## How it works

The page runs in the browser and asks Claude through the artifact `sample` capability with images on (`{"sample": {"images": true}}`). Reviews use the viewer's own Claude usage.

- **Photos:** the page sends the full frame plus four overlapping close-up tiles. Claude's coordinates are mapped from the tiles back onto the full frame.
- **Videos:** the page takes up to 16 evenly spaced frames in the browser. Export as H.264 MP4. Some codecs, such as ProRes, won't decode in a browser.

## Files

- `daimon.src.html`: the whole app, including the page, prompt, director panel and report renderer.
- `build.py`: builds `daimon.html` from the source. If an example review report exists, it is injected so the page opens on a sample report. Set `DAIMON_EXAMPLE=/path/to/report.html` to use a different one.

## Build and publish

```bash
python3 build.py
```

Publish `daimon.html` as a Claude artifact with the capability `{"sample": {"images": true}}`.

`daimon.html` is a build output, so it isn't committed.
