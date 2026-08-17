"""Read text tiles from a NES screenshot. Usage: python _read_text.py file.png [r0 r1]
Prints each ink-bearing 8x8 tile as solid blocks, one tile per column group."""
import sys
from PIL import Image

def main():
    path = sys.argv[1]
    r0 = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    r1 = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    im = Image.open(path).convert("RGB")
    px = im.load()
    print(f"# {path} rows {r0}-{r1}")
    for ty in range(r0, r1):
        # ink per tile
        ink = []
        for tx in range(32):
            c = 0
            for y in range(ty*8, ty*8+8):
                for x in range(tx*8, tx*8+8):
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
        if not groups:
            print(f"row {ty}: (empty)")
            continue
        print(f"row {ty}:")
        for (a, b) in groups:
            print(f"  tiles {a}-{b}:")
            for i in range(8):
                y = ty*8 + i
                line = ""
                for tx in range(a, b+1):
                    for x in range(tx*8, tx*8+8):
                        r, g, bl = px[x, y]
                        line += "#" if max(r, g, bl) > 60 else "."
                    line += " "
                print("   " + line)

main()
