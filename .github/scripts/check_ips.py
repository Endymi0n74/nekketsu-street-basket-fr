"""Validate the IPS patches in patch/ (PATCH header, records, EOF trailer).

IPS format: 5-byte "PATCH" header, then records:
  - offset   : 3 bytes big-endian
  - size     : 2 bytes big-endian (0 => RLE record)
  - data     : size bytes, or 2-byte RLE length + 1 value byte
Trailer: literal "EOF".
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATCHES = sorted((ROOT / "patch").glob("*.ips"))


def validate(path):
    data = path.read_bytes()
    if data[:5] != b"PATCH":
        raise SystemExit(f"{path.name}: missing PATCH header")
    i, n, recs = 5, len(data), 0
    while i < n:
        if data[i : i + 3] == b"EOF":
            if i + 3 != n:
                raise SystemExit(f"{path.name}: trailing data after EOF")
            return recs
        if i + 5 > n:
            raise SystemExit(f"{path.name}: truncated record header at {i}")
        size = int.from_bytes(data[i + 3 : i + 5], "big")
        i += 5
        if size == 0:
            # RLE record: 2-byte run length + 1 value byte
            if i + 3 > n:
                raise SystemExit(f"{path.name}: truncated RLE record at {i}")
            i += 3
        else:
            if i + size > n:
                raise SystemExit(f"{path.name}: truncated data record at {i}")
            i += size
        recs += 1
    raise SystemExit(f"{path.name}: missing EOF trailer")


if not PATCHES:
    raise SystemExit("no IPS files found in patch/")
for p in PATCHES:
    recs = validate(p)
    print(f"OK {p.name}: {recs} records")
print(f"{len(PATCHES)} IPS file(s) valid")
