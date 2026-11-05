#!/usr/bin/env python3
"""build_report.py <work_dir>
Reads <work_dir>/review.json and writes <work_dir>/report.html with the images embedded."""
import base64, io, json, os, sys
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "assets", "report.html")
PANEL = os.path.join(HERE, "..", "references", "panel.json")
LIMIT = 15 * 1024 * 1024


def embed(path, base, width):
    p = path if os.path.isabs(path) else os.path.join(base, path)
    if not os.path.exists(p):
        sys.exit(f"missing file: {p}")
    im = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
    if im.size[0] > width:
        im = im.resize((width, round(im.size[1] * width / im.size[0])), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


d = os.path.abspath(sys.argv[1])
review = json.load(open(os.path.join(d, "review.json")))
for a in review.get("assets", []):
    a["src"] = embed(a.pop("path"), d, 1800)
for key in ("issues", "strengths"):
    for it in review.get(key, []):
        if it.get("crop"):
            it["crop_src"] = embed(it.pop("crop"), d, 720)

profiles = json.load(open(PANEL))
for field in review.get("panel", []):
    prof = profiles.get(field.get("field"), {})
    for m in field.get("members", []):
        p = prof.get(m.get("name"), {})
        m.setdefault("lens", p.get("lens", ""))
        m.setdefault("pattern", p.get("pattern", ""))

fails = [i for i in review.get("issues", []) if i.get("severity") == "fail"]
review["verdict"] = "FAIL" if fails else "PASS"
review["fail_count"] = len(fails)

payload = json.dumps(review, ensure_ascii=False).replace("</", "<\\/")
html = open(TEMPLATE).read()
html = html.replace("__REPORT_TITLE__", review.get("title", "Daimon report"))
html = html.replace("/*__DATA__*/null", payload)
out = os.path.join(d, "report.html")
open(out, "w").write(html)
size = os.path.getsize(out)
print(f"{out}  {size/1048576:.1f} MB  verdict={review['verdict']}  fails={len(fails)}")
if size > LIMIT:
    print("WARNING: over 15 MB. Use fewer or smaller crops.")
