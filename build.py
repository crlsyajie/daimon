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
