"""Check that internal markdown links and <img src> targets resolve.

External links (http/https/mailto), anchors (#...) and link fragments
(target#anchor) are skipped.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def check_md(path):
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")
    bad = []

    for m in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", text):
        target = m.group(1).strip()
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        t = target.split("#")[0]
        if not t:
            continue
        if not (path.parent / t).resolve().exists():
            bad.append(f"{rel}: missing link -> {target}")

    for m in re.finditer(r'<img[^>]*src="([^"]+)"', text):
        target = m.group(1)
        if not (path.parent / target).resolve().exists():
            bad.append(f"{rel}: missing image -> {target}")

    return bad


bad = []
for p in sorted(ROOT.rglob("*.md")):
    if ".git" in p.parts:
        continue
    bad += check_md(p)

if bad:
    for b in bad:
        print("FAIL:", b)
    sys.exit(1)
print("all internal links OK")
