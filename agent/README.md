# Daimon agent for Claude chat

Send a photo in any Claude chat with **Check Photo** or **CP** (any case: CP, cp, Cp, cP). Claude runs the full
Daimon review and replies with the verdict, the fails with fix prompts, and a report file you can open.

## Install (one time)

1. In Claude, go to **Settings → Capabilities** and make sure **Code execution and file creation** is on.
2. In **Settings → Capabilities → Skills**, upload `daimon-skill.zip`.
3. **Optional but recommended:** in **Settings → Profile → personal preferences**, paste this line so the short
   trigger always fires:

   > When I send an image with "Check Photo" or "CP" (any letter case) anywhere in my message, always run the daimon skill on it before anything else.

## Use

| You send | What happens |
|---|---|
| photo + `CP` | Photoreal review |
| photo + `cp hybrid` | Hybrid review: CGI is allowed, but the people must be real |
| photo + `Cp 3D` | 3D review: it may look rendered, but no hallucinations |
| photo + `CP billboard for Nike, must show the shoe` | Whatever follows the keyword is used as the brief |
| several photos + `CP` | One report for each photo |

The reply opens with **PASS** or **FAIL** and gives the score, a numbered list of fails, a copy-ready fix prompt
for each one, and the top strength. The attached `…-daimon.html` file holds the full report: markers on the frame,
crops, the 20-person panel and the checklist.

## Files

- `daimon/SKILL.md`: what Claude does when triggered
- `daimon/references/`: the realism standard and the 20 director profiles, with sources
- `daimon/scripts/`: Pillow scripts to prepare the image, crop zones and build the report
- `daimon/assets/report.html`: the report template

To rebuild the zip after editing:

```bash
cd agent && rm -f daimon-skill.zip && zip -qr daimon-skill.zip daimon -x "*.DS_Store"
```
