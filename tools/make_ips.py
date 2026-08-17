"""Generate IPS patches that produce fr.nes.

Primary: orig_jp.nes -> fr.nes  (Japanese original ROM, per request to rebase
the translation patch on the Japanese version).
Secondary: en.nes -> fr.nes     (Farid's English v1.2, kept for convenience).

IPS format: 'PATCH' header, records of (offset, size, data),
RLE records when size==0, 'EOF' trailer.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DST = "fr.nes"

BASES = [
    ("orig_jp.nes", "Nekketsu Street Basket (JPN) FR.ips", "japanese"),
    ("en.nes", "Nekketsu Street Basket (v1.2 Final) FR.ips", "english"),
]


def make_ips(src_path, dst_path, out_path):
    src = open(src_path, "rb").read()
    dst = open(dst_path, "rb").read()
    assert len(src) == len(dst), f"size mismatch {len(src)} vs {len(dst)}"

    out = bytearray(b"PATCH")
    i = 0
    n = len(src)
    runs = 0
    bytes_patched = 0
    while i < n:
        if src[i] != dst[i]:
            j = i
            while j < n and src[j] != dst[j]:
                j += 1
            chunk = dst[i:j]
            if len(chunk) > 1 and len(set(chunk)) == 1:
                out += i.to_bytes(3, "big")
                out += (0).to_bytes(2, "big")
                out += len(chunk).to_bytes(2, "big")
                out += bytes([chunk[0]])
            else:
                out += i.to_bytes(3, "big")
                out += len(chunk).to_bytes(2, "big")
                out += chunk
            runs += 1
            bytes_patched += len(chunk)
            i = j
        else:
            i += 1

    out += b"EOF"
    open(out_path, "wb").write(out)
    print(f"wrote {out_path}: {runs} runs, {bytes_patched} bytes patched, {len(out)} bytes total")

    # verify: apply IPS to src, compare with dst
    def apply_ips(rom, ips):
        out_rom = bytearray(rom)
        k = 5
        while ips[k:k+3] != b"EOF":
            off = int.from_bytes(ips[k:k+3], "big")
            size = int.from_bytes(ips[k+3:k+5], "big")
            k += 5
            if size == 0:
                rlen = int.from_bytes(ips[k:k+2], "big")
                val = ips[k+2]
                k += 3
                out_rom[off:off+rlen] = bytes([val]) * rlen
            else:
                out_rom[off:off+size] = ips[k:k+size]
                k += size
        return bytes(out_rom)

    patched = apply_ips(src, out)
    assert patched == dst, "VERIFY FAILED"
    print(f"verify: IPS ({src_path}) -> {dst_path}  OK")


for base, out_name, label in BASES:
    print(f"[{label}] {base} -> {DST}")
    make_ips(base, DST, out_name)
