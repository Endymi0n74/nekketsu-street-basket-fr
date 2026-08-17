"""Decode text from a NES screenshot by matching 8x8 glyphs against the ROM's CHR tiles.
Usage: python _decode_screen_text.py rom.nes shot.png rowStart rowEnd
"""
import sys
from PIL import Image

ROM = sys.argv[1]
SHOT = sys.argv[2]
R0 = int(sys.argv[3]) if len(sys.argv) > 3 else 0
R1 = int(sys.argv[4]) if len(sys.argv) > 4 else 30

data = open(ROM, "rb").read()
prg_size = 8 * 16384
chr_ = data[16 + prg_size : 16 + prg_size + 16 * 8192]
NBANKS = 16

def tile_masks(bank, tile):
    o = bank * 0x2000 + tile * 16
    d = chr_[o : o + 16]
    b1 = []   # bit 1 pixels
    b2 = []   # bit 2 pixels
    union = []
    for r in range(8):
        lo, hi = d[r * 2], d[r * 2 + 1]
        row1, row2, rowu = "", "", ""
        for b in range(8):
            v = ((lo >> (7 - b)) & 1) | (((hi >> (7 - b)) & 1) << 1)
            row1 += "#" if v & 1 else "."
            row2 += "#" if v & 2 else "."
            rowu += "#" if v else "."
        b1.append(row1); b2.append(row2); union.append(rowu)
    return b1, b2, union

def load_glyphs(path, r0, r1):
    im = Image.open(path).convert("RGB")
    px = im.load()
    out = []
    for ty in range(r0, r1):
        ink = []
        for tx in range(32):
            c = 0
            for y in range(ty * 8, ty * 8 + 8):
                for x in range(tx * 8, tx * 8 + 8):
                    r, g, b = px[x, y]
                    if max(r, g, b) > 60:
                        c += 1
            ink.append(c)
        groups = []
        cur = None
        for tx in range(32):
            if ink[tx] > 1:
                if cur is None: cur = [tx, tx]
                else: cur[1] = tx
            else:
                if cur: groups.append(cur); cur = None
        if cur: groups.append(cur)
        for (a, b) in groups:
            glyphs = []
            for tx in range(a, b + 1):
                g = []
                for y in range(ty * 8, ty * 8 + 8):
                    row = ""
                    for x in range(tx * 8, tx * 8 + 8):
                        r, gg, bl = px[x, y]
                        row += "#" if max(r, gg, bl) > 60 else "."
                    g.append(row)
                glyphs.append(g)
            out.append((ty, a, glyphs))
    return out

def match_score(glyph, mask):
    # count matching ink pixels / total ink; penalize mask pixels not in glyph
    hit = miss = extra = 0
    for y in range(8):
        for x in range(8):
            if glyph[y][x] == "#":
                if mask[y][x] == "#":
                    hit += 1
                else:
                    miss += 1
            else:
                if mask[y][x] == "#":
                    extra += 1
    return hit, miss, extra

def best_match(glyph):
    gink = sum(1 for y in range(8) for x in range(8) if glyph[y][x] == "#")
    best = None
    for bank in range(NBANKS):
        for tile in range(256):
            b1, b2, uni = tile_masks(bank, tile)
            for label, mask in (("b1", b1), ("b2", b2), ("uni", uni)):
                hit, miss, extra = match_score(glyph, mask)
                # score: coverage of glyph by mask, minus penalties
                score = hit - extra * 0.5 - miss * 0.5
                if best is None or score > best[0]:
                    best = (score, bank, tile, label, hit, miss, extra, gink)
    return best

print(f"# {SHOT} rows {R0}-{R1}")
for ty, a, glyphs in load_glyphs(SHOT, R0, R1):
    print(f"row {ty}, tiles {a}-{a + len(glyphs) - 1}:")
    for gi, g in enumerate(glyphs):
        score, bank, tile, label, hit, miss, extra, gink = best_match(g)
        print(f"  glyph {gi} (ink={gink}) -> bank {bank} tile 0x{tile:02X} ({label}) "
              f"score={score:.1f} hit={hit} miss={miss} extra={extra}")
        for row in g:
            print("    " + row)
