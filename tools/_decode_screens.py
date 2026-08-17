import sys
sys.path.insert(0, '.')
prg = open('en.nes','rb').read()[16:16+8*16384]

def rd16(off): return prg[off] | (prg[off+1]<<8)

def decode_stream(off):
    """Decode screen bytecode stream at PRG offset. Returns (ppu_start, list of (addr, tile))."""
    out = []
    i = off
    while True:
        b = prg[i]; i += 1
        if b == 0:
            break
        cmd = (b & 0xC0) >> 6
        cnt = b & 0x3F
        if cmd in (0, 1):
            for _ in range(cnt):
                out.append(prg[i]); i += 1
        elif cmd == 2:
            w = prg[i]; i += 1
            tile = prg[i]; i += 1
            for _ in range(w):
                for _ in range(cnt):
                    out.append(tile)
        elif cmd == 3:
            w = prg[i]; i += 1
            save = i
            for _ in range(cnt):
                i = save
                for _ in range(w):
                    out.append(prg[i]); i += 1
    return out, i

def render(nametable, start):
    """Render a 32x30 nametable grid. `start` = PPU addr of first cell."""
    base = start & 0xFFF
    grid = [['  ']*32 for _ in range(30)]
    for k, t in enumerate(nametable):
        a = (base + k) & 0xFFF
        if a >= 0x3C0:  # attribute table
            continue
        r = (a // 32) % 30
        c = a % 32
        if 0 <= r < 30 and 0 <= c < 32:
            grid[r][c] = f"{t:02X}"
    return grid

for screen in [0x1D, 0x2B]:
    desc = rd16(0x1D8C4 + 2*screen)
    stream = rd16(desc & 0x3FFF)
    yidx = prg[(desc & 0x3FFF) + 6]
    lo = prg[0x1DB71 + yidx]
    hi = prg[0x1DB7E + yidx]
    ppu = lo | (hi << 8)
    tiles, end = decode_stream(stream & 0x3FFF)
    print(f"=== Screen ${screen:02X}: stream PRG 0x{stream:04X} ({end-stream} octets), {len(tiles)} tuiles, PPU ${ppu:04X} (Y={yidx:02X}) ===")
    grid = render(tiles, ppu)
    for r in range(30):
        print(f"{r:2d} " + ' '.join(grid[r]))
    print()
