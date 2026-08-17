"""Decode FR screenshots using a glyph reference built from EN screenshots (same font).
Letters sit in the bottom tile row of each 2-row text line (top row = shadow/outline).
Usage: python _decode_all.py
"""
from PIL import Image

def glyph(path, ty, tx):
    im = Image.open(path).convert("RGB")
    px = im.load()
    return "".join(
        "#" if max(px[x, y]) > 60 else "."
        for y in range(ty * 8, ty * 8 + 8)
        for x in range(tx * 8, tx * 8 + 8)
    )

def groups_in(path, ty):
    im = Image.open(path).convert("RGB")
    px = im.load()
    groups, cur = [], None
    for tx in range(32):
        c = sum(1 for y in range(ty * 8, ty * 8 + 8) for x in range(tx * 8, tx * 8 + 8)
                if max(px[x, y]) > 60)
        if c > 1:
            if cur is None: cur = [tx, tx]
            else: cur[1] = tx
        else:
            if cur: groups.append(cur); cur = None
    if cur: groups.append(cur)
    return groups

# Build reference: glyph -> letter by labeling EN glyphs manually here.
# EN strings identified so far (from the game + README):
# a4 line1: "SORT:" then more glyphs; we map glyphs and print.
ref = {}

def learn(shot, ty, tx, ch):
    g = glyph(shot, ty, tx)
    if g not in ref:
        ref[g] = ch

# Use EN a4 known letters: t1=S t2=O t3=R t4=T t5=: t8=S t9=A t10=T
learn("_e_shot_a4.png", 25, 1, "S")
learn("_e_shot_a4.png", 25, 2, "O")
learn("_e_shot_a4.png", 25, 3, "R")
learn("_e_shot_a4.png", 25, 4, "T")
learn("_e_shot_a4.png", 25, 5, ":")
learn("_e_shot_a4.png", 25, 9, "A")
learn("_e_shot_a4.png", 25, 8, "S")

# Also learn from EN s1/st2 text (needs identification) - dump EN texts first
print("===== EN texts =====")
for tag in ["t1", "s1", "s1b", "a1", "a1b", "d1", "a2", "a2b", "a3", "a3b", "st2", "a4"]:
    for ty in (25, 27):
        gs = groups_in(f"_e_shot_{tag}.png", ty)
        if gs:
            tiles = []
            for (a, b) in gs:
                for tx in range(a, b + 1):
                    tiles.append(f"t{tx}")
            print(f"EN {tag} row{ty}: {' '.join(tiles)}")
print()
print("===== FR texts (glyph IDs) =====")
for tag in ["t1", "s1", "s1b", "a1", "a1b", "d1", "a2", "a2b", "a3", "a3b", "st2", "a4"]:
    for ty in (25, 27):
        gs = groups_in(f"_m_shot_{tag}.png", ty)
        if gs:
            parts = []
            for (a, b) in gs:
                for tx in range(a, b + 1):
                    g = glyph(f"_m_shot_{tag}.png", ty, tx)
                    ch = ref.get(g, "?")
                    parts.append(ch)
            print(f"FR {tag} row{ty}: {' '.join(parts)}")
