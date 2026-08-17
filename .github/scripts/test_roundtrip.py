"""Round-trip test: patch_rom.py + make_ips.py on synthetic ROMs.

Builds synthetic en.nes / orig_jp.nes (deterministic non-letter filler plus
the exact bytes patch_rom.py asserts on), runs the real scripts in a temp
dir, then applies each generated IPS back to its base ROM and checks it
reproduces fr.nes byte-for-byte.

Notes:
- No copyrighted ROM is used: every byte is generated here.
- patch_rom.py asserts on specific PRG bytes; the "magic" table below mirrors
  those asserts (command-menu slot cap, boot state, intro entry, DTE pair).
- patch_box35() rebuilds the quiz plane-scene box and asserts the French text
  overruns the English budget while enough padding exists. The crafted box
  below guarantees overrun=1 / padding=80 with the current translations.py.
  If translations.py or patch_rom.py change, adjust the budgets accordingly.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
HEADER = 16
PRG_SIZE = 8 * 16384
ROM_SIZE = HEADER + PRG_SIZE

# PRG offsets -> expected bytes (mirrors patch_rom.py asserts):
#   command menu slot cap LDA #$06 (0xF5B7), boot LDA #$00 (0x1CA08),
#   intro JMP $AB69 (0x0C00F), DTE "ST" pair (0x1FE02).
MAGIC = {
    0xF5B7: bytes([0xA9, 0x06]),
    0x1CA08: bytes([0xA9, 0x00, 0x8D]),
    0x0C00F: bytes([0x4C, 0x69, 0xAB]),
    0x1FE02: bytes([0x23, 0x24]),
}
BOX_OFF, BOX_SIZE = 0x12DDF, 0x12EFB - 0x12DDF  # 284 bytes


def box35() -> bytes:
    """Craft the plane-scene box so patch_box35's overrun assert passes.

    Layout: 8 units of [0xF7, L(budget), 0xF9]. split_lines turns each unit
    into 3 lines ([F7], [L], [F9]) so L-pieces land at box line indices
    1,4,7,10,13,16,19,22 -> B4:0126FE lines 217,220,223,226,229,232,235,238.
    With current translations.py:
      - line 217 'hey! ' (5B) overruns budget 4  -> overrun 1
      - line 229 'detache moi. je deteste voler' (29B) fits in 69  -> pad 40
      - line 235 'au secours' (10B) fits in 50                   -> pad 40
    """
    budgets = [4, 29, 29, 29, 69, 29, 50, 29]
    out = bytearray()
    for b in budgets:
        out += b"\xF7" + b"\x00" * b + b"\xF9"
    assert len(out) == BOX_SIZE, f"box size {len(out)} != {BOX_SIZE}"
    return bytes(out)


def build_rom(fill) -> bytes:
    data = bytearray(ROM_SIZE)
    for i in range(HEADER, ROM_SIZE):
        data[i] = fill(i - HEADER)
    for off, bs in MAGIC.items():
        data[HEADER + off : HEADER + off + len(bs)] = bs
    data[HEADER + BOX_OFF : HEADER + BOX_OFF + BOX_SIZE] = box35()
    return bytes(data)


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def apply_ips(rom: bytes, ips: bytes) -> bytes:
    out = bytearray(rom)
    k = 5
    while ips[k : k + 3] != b"EOF":
        off = int.from_bytes(ips[k : k + 3], "big")
        size = int.from_bytes(ips[k + 3 : k + 5], "big")
        k += 5
        if size == 0:
            rlen = int.from_bytes(ips[k : k + 2], "big")
            out[off : off + rlen] = bytes([ips[k + 2]]) * rlen
            k += 3
        else:
            out[off : off + size] = ips[k : k + size]
            k += size
    return bytes(out)


def main():
    en = build_rom(lambda i: 0x80 + (i % 0x60))
    jp = build_rom(lambda i: 0x80 + ((i * 3) % 0x60))
    assert en != jp, "synthetic bases must differ"

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        for name in ("patch_rom.py", "make_ips.py", "translations.py"):
            shutil.copy(TOOLS / name, d / name)
        (d / "en.nes").write_bytes(en)
        (d / "orig_jp.nes").write_bytes(jp)

        r = run([sys.executable, "patch_rom.py"], d)
        if r.returncode != 0:
            print(r.stdout)
            print(r.stderr)
            sys.exit(f"patch_rom.py failed ({r.returncode})")
        fr = (d / "fr.nes").read_bytes()
        assert len(fr) == ROM_SIZE
        assert fr != en, "patch_rom.py produced no change"

        r = run([sys.executable, "make_ips.py"], d)
        if r.returncode != 0:
            print(r.stdout)
            print(r.stderr)
            sys.exit(f"make_ips.py failed ({r.returncode})")

        for base_name, ips_name in (
            ("orig_jp.nes", "Nekketsu Street Basket (JPN) FR.ips"),
            ("en.nes", "Nekketsu Street Basket (v1.2 Final) FR.ips"),
        ):
            ips = (d / ips_name).read_bytes()
            assert ips[:5] == b"PATCH" and ips[-3:] == b"EOF", ips_name
            patched = apply_ips((d / base_name).read_bytes(), ips)
            assert patched == fr, f"round-trip mismatch: {ips_name}"
            print(f"OK {ips_name}: {len(ips)} bytes, round-trip verified")

    print("round-trip PASS (patch_rom + make_ips on synthetic ROMs)")


if __name__ == "__main__":
    main()
