"""ASCII preview of a screenshot. Usage: python _ascii_preview.py file.png [scale] [startY endY]"""
import sys
from PIL import Image

def main():
    path = sys.argv[1]
    scale = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    im = Image.open(path).convert("L")
    print(f"# {path} {im.size}")
    if len(sys.argv) > 4:
        y0, y1 = int(sys.argv[3]), int(sys.argv[4])
        im = im.crop((0, y0, im.width, y1))
    # downsample by 2x2 -> one char, then scale
    w = int(im.width / 2)
    h = int(im.height / 2)
    im = im.resize((w, h))
    if scale != 1.0:
        im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    px = im.load()
    chars = " .:-=+*#%@"
    for y in range(im.height):
        line = ""
        for x in range(im.width):
            v = px[x, y]
            line += chars[min(len(chars) - 1, v * len(chars) // 256)]
        print(line)

main()
