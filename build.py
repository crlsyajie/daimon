#!/usr/bin/env python3
"""Build daimon.html from daimon.src.html.

If an example review report exists (from the realism-qa skill), its data is
injected so the page opens on a sample report. Without one, the page opens
straight on the upload screen.
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
example_report = os.environ.get("DAIMON_EXAMPLE", os.path.expanduser(
    "~/Documents/Claude Folder/QA Reviews/2026-11-05-park-ball-toss/report.html"))

src = open(os.path.join(HERE, "daimon.src.html")).read()
out = src
if os.path.exists(example_report):
    rep = open(example_report).read()
    m = re.search(r"const R = (\{.*?\});\nconst MODES", rep, re.S)
    if not m:
        sys.exit("example data not found in " + example_report)
    out = src.replace("/*__EXAMPLE__*/null", m.group(1))
    print("example:", example_report)
else:
    print("no example report found; building without one")

dst = os.path.join(HERE, "daimon.html")
open(dst, "w").write(out)
print(dst, f"{os.path.getsize(dst)/1048576:.2f} MB")

# --pages: also write site/index.html, a standalone page for GitHub Pages.
# Reviews need Claude, so outside Claude the page shows the example report
# and links the "open in Claude" note to the published artifact.
if "--pages" in sys.argv:
    artifact = os.environ.get("DAIMON_ARTIFACT_URL", "https://claude.ai/artifact/N6eWHwhUrgWnvDHqiqpaK7")
    note = "Open Daimon in Claude to run reviews."
    if note not in out:
        sys.exit("open-in-Claude note not found in daimon.src.html")
    page = out.replace(note, f'<a href="{artifact}" target="_blank" rel="noopener">Open Daimon in Claude</a> to run reviews.', 1)
    page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            '<meta name="description" content="Daimon: strict realism QA for AI-made photos and video.">\n'
            + page + '\n</html>\n')
    os.makedirs(os.path.join(HERE, "site"), exist_ok=True)
    site = os.path.join(HERE, "site", "index.html")
    open(site, "w").write(page)
    print(site, f"{os.path.getsize(site)/1048576:.2f} MB")
