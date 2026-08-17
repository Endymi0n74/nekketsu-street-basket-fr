"""Apply French translations to the EN ROM.

Strategy: keep every non-letter byte (controls, name tokens) exactly in place;
replace letter bytes with French. Each French string must fit within the byte
budget of its L piece (shorter strings padded with spaces 0x00).
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from translations import T

EN = "en.nes"
OUT = "fr.nes"
data = bytearray(open(EN, "rb").read())
prg = data[16:16+8*16384]
orig = bytes(prg)

LETTER = set(range(0x11, 0x2B)) | {0x00} | set(range(0x2B, 0x2F)) | set(range(0x30, 0x3A)) | {0xA1}

NAME_PATTERNS = [
    bytes([0xD7, 0xD8, 0x1F]),
    bytes([0xDA, 0xD6]),
    bytes([0xD5, 0xD3, 0xD9]),
    bytes([0xD4, 0xDB, 0xDC]),
    bytes([0xD2, 0xD1, 0x19]),
]

BLOCKS = [
    (3, 0x00F6B4, 115), (3, 0x00F732, 46),
    (4, 0x0126FE, 2293), (4, 0x013358, 61), (4, 0x0136C6, 890), (4, 0x013EF4, 196),
    (7, 0x01C306, 266),
    (7, 0x01E463, 27), (7, 0x01E49F, 31), (7, 0x01E4BF, 37), (7, 0x01E505, 89),
    (7, 0x01E581, 29), (7, 0x01E59F, 25), (7, 0x01E5D7, 55),
    (7, 0x01E71B, 13), (7, 0x01E729, 27), (7, 0x01E745, 17),
    (7, 0x01E768, 13), (7, 0x01E776, 13),
]

def split_lines(bs):
    """Return list of lines; each line = list of (kind, bytes)."""
    lines = []
    cur = []
    i = 0
    n = len(bs)
    while i < n:
        b = bs[i]
        matched = None
        for pat in NAME_PATTERNS:
            if bs[i:i+len(pat)] == pat:
                matched = pat
                break
        if matched is not None:
            cur.append(('K', matched))
            i += len(matched)
            continue
        if b in LETTER:
            j = i
            while j < n and bs[j] in LETTER:
                j += 1
            cur.append(('L', bytes(bs[i:j])))
            i = j
            continue
        cur.append(('K', bytes([b])))
        i += 1
    line = []
    for kind, b in cur:
        if kind == 'K' and len(b) == 1 and b[0] in (0xF7, 0xF9, 0xF4, 0xF5, 0xF3, 0xFF):
            if line:
                lines.append(line); line = []
            lines.append([('K', b)])
        else:
            line.append((kind, b))
    if line:
        lines.append(line)
    return lines

def encode_fr(s):
    out = []
    for ch in s:
        if ch == ' ':
            out.append(0x00)
        elif 'a' <= ch <= 'z':
            out.append(ord(ch) - ord('a') + 0x11)
        elif '0' <= ch <= '9':
            out.append(ord(ch) - ord('0') + 0x30)
        elif ch == '!':
            out.append(0x2B)
        elif ch == '?':
            out.append(0x2C)
        elif ch == '.':
            out.append(0x2D)
        elif ch == "'":
            out.append(0xA1)
        else:
            raise ValueError(f"cannot encode {ch!r} (in {s!r})")
    return bytes(out)

errors = []
total_in = 0
total_out = 0

# Box 7 (PRG 0x127DB..0x12871) and box 9 (PRG 0x128DA..0x1290F) of
# B4:0126FE are rebuilt wholesale by patch_quiz_box() / patch_box9()
# below ('tout le monde avait failli l'oublier' is 36 chars and
# 'quoi? pas en 1ere classe' is 24 chars, both over their line budgets).
# Skip those lines here to avoid budget errors.
BOX7_SKIP = {('B4:0126FE', i) for i in (34, 36, 40, 42, 46, 48)}
BOX9_SKIP = {('B4:0126FE', i) for i in (63, 65)}
BOX10_SKIP = {('B4:0126FE', i) for i in (68, 70, 74, 76, 80, 82)}
BOX11_SKIP = {('B4:0126FE', i) for i in (85, 87)}
BOX13_SKIP = {('B4:0126FE', 96)}
BOX14_SKIP = {('B4:0126FE', 99), ('B4:0126FE', 101)}
BOX26_SKIP = {('B4:0126FE', 156), ('B4:0126FE', 158), ('B4:0126FE', 164)}
BOX27_SKIP = {('B4:0126FE', 167), ('B4:0126FE', 169), ('B4:0126FE', 175), ('B4:0126FE', 177)}
BOX34_SKIP = {('B4:0126FE', 214)}
BOX35_SKIP = {('B4:0126FE', 229), ('B4:0126FE', 235)}
CREDITS_SKIP = {('B4:0126FE', 254), ('B4:0126FE', 267), ('B4:0126FE', 329)}

for bank, start, length in BLOCKS:
    bs = bytes(prg[start:start+length])
    lines = split_lines(bs)
    key = f"B{bank}:{start:06X}"
    new_lines = []
    for idx, line in enumerate(lines):
        if (key, idx) in BOX7_SKIP or (key, idx) in BOX9_SKIP or (key, idx) in BOX10_SKIP or (key, idx) in BOX11_SKIP or (key, idx) in BOX13_SKIP or (key, idx) in BOX14_SKIP or (key, idx) in BOX26_SKIP or (key, idx) in BOX27_SKIP or (key, idx) in BOX34_SKIP or (key, idx) in BOX35_SKIP or (key, idx) in CREDITS_SKIP:
            new_lines.append(line)
            continue
        pieces = [p for p in line if p[0] == 'L']
        if not pieces:
            new_lines.append(line)
            continue
        fr_list = T.get((key, idx))
        if fr_list is None:
            new_lines.append(line)
            continue
        if len(fr_list) != len(pieces):
            errors.append(f"{key} L{idx}: translation has {len(fr_list)} parts, line has {len(pieces)} L-pieces")
            new_lines.append(line)
            continue
        newline = []
        pi = 0
        for kind, b in line:
            if kind == 'L':
                fr = fr_list[pi]; pi += 1
                budget = len(b)
                try:
                    fb = encode_fr(fr)
                except ValueError as e:
                    errors.append(f"{key} L{idx}: {e}")
                    newline.append(('L', b))
                    continue
                if len(fb) > budget:
                    errors.append(f"{key} L{idx}: {fr!r} is {len(fb)} bytes, budget {budget} (EN {bytes(b)!r})")
                    newline.append(('L', b))
                    continue
                fb = fb + b'\x00' * (budget - len(fb))
                newline.append(('L', fb))
            else:
                newline.append((kind, b))
        new_lines.append(newline)
    # reassemble
    new_bs = b''.join(b for _, b in sum(new_lines, []))
    if len(new_bs) > length:
        errors.append(f"{key}: new block {len(new_bs)} > {length}")
        new_bs = new_bs[:length]
    elif len(new_bs) < length:
        new_bs = new_bs + b'\x00' * (length - len(new_bs))
    prg[start:start+length] = new_bs
    total_in += length
    total_out += len(new_bs)

if errors:
    print(f"ERRORS ({len(errors)}):")
    for e in errors:
        print("  " + e)
else:
    print("no length errors")

# ---------------------------------------------------------------------------
# Command menu (bank 3, PRG 0xF780). The 9 commands are stored as strings
# addressed by a pointer table; the 5 middle ones share one region and are
# shown in fixed 6-char slots on 2x2 menu pages. The generic block patcher
# can't align French words to those slots, so rewrite strings + pointers
# explicitly. 'ball en l'air' (12 chars) needs the slot cap raised 6 -> 12.
# ---------------------------------------------------------------------------
def enc_str(s):
    out = []
    for ch in s:
        if ch == ' ':
            out.append(0x00)
        elif 'a' <= ch <= 'z':
            out.append(ord(ch) - ord('a') + 0x11)
        elif ch == "'":
            out.append(0xA1)
        else:
            raise ValueError(f"cannot encode {ch!r}")
    return bytes(out)

def patch_command_menu(prg):
    # code -> French string (order = pointer table index 0..8)
    cmds = {
        0: "tir",              # shoot
        1: "ball en l'air",    # aim upball
        2: "attaque",          # attack
        3: "frappe",           # strike
        4: "passe",            # pass
        5: "ball",             # ball
        6: "dunk",             # dunk
        7: "arme",             # weapon
        8: "hasard",           # random
    }
    # 'ball en l'air' lives at the free bank-end padding (PRG 0xFFB3 = CPU $BFF3)
    ext_addr = 0x8000 + (0xFFB3 - 0xC000)
    bal = enc_str("ball en l'air") + b'\xff'
    assert len(bal) == 14
    prg[0xFFB3:0xFFB3 + len(bal)] = bal

    # inline layout: all strings except 'ball en l'air', packed at 0xF792
    base = 0xF792
    ptrs = {1: ext_addr}
    for code in (4, 0, 2, 8, 3, 5, 6, 7):
        b = enc_str(cmds[code]) + b'\xff'
        prg[base:base + len(b)] = b
        ptrs[code] = 0x8000 + (base - 0xC000)
        base += len(b)
    assert base <= 0xF7C8, hex(base)
    prg[base:0xF7C8] = b'\x00' * (0xF7C8 - base)

    # rebuild the pointer table (code -> CPU address, little-endian)
    tbl = b''.join(bytes([ptrs[c] & 0xFF, (ptrs[c] >> 8) & 0xFF]) for c in range(9))
    assert len(tbl) == 18
    prg[0xF780:0xF792] = tbl

    # raise per-slot render cap from 6 to 14 (CPU $B5B7 = PRG 0xF5B7) so
    # 'ball en l'air' (13 chars) fits its slot
    assert prg[0xF5B7:0xF5B9] == bytes([0xA9, 0x06]), prg[0xF5B7:0xF5B9].hex()
    prg[0xF5B7:0xF5B9] = bytes([0xA9, 0x0E])


patch_command_menu(prg)

# ---------------------------------------------------------------------------
# Quiz answer box (B4:0126FE box 7, PRG 0x127DB..0x12871, 150 bytes). The
# English 'that's correct. / everyone almost forgot it. / what a comeback. /
# the prize for [KUNIO] is / an all expenses paid trip / to the usa!
# congratulations.' is rewritten as 4 pages so the 36-char French sentence
# 'tout le monde avait failli l'oublier' fits across 2 lines:
#   p1: exact. bravo. / tout le monde
#   p2: avait failli l'oublier. / quel retour.
#   p3: et le gagnant [KUNIO] a / un voyage tout paye
#   p4: aux usa! felicitations.
# 148 bytes <= 150 -> the pointer table (entry 7 -> A7DB) stays valid.
# ---------------------------------------------------------------------------
def patch_quiz_box(prg):
    box = 0x127DB
    name = bytes([0xD4, 0xDB, 0xDC])          # [?1] quiz master name token
    k = bytes([0xD7, 0xD8, 0x1F])             # [KUNIO] name token
    f = lambda s: encode_fr(s)
    # 3 pages (comme l'EN) : 'exact!' + 'tout le monde' fusionnés sur la
    # ligne 1 pour caser 'remporte' / 'tous frais' / 'payes' dans les 150
    # octets disponibles (la boîte 8 suit immédiatement à 0x12871).
    p1 = b'\xF4' + name + f("exact! tout le monde") + b'\xF7' + f("avait failli l'oublier") + b'\xF9'
    p2 = b'\xF7\xF4' + name + f("quel comeback") + b'\xF7' + f("et le gagnant ") + k + f(" remporte") + b'\xF9'
    p3 = b'\xF7\xF4' + name + f("un voyage tous frais") + b'\xF7' + f("payes aux usa! felicitations") + b'\xF5'
    new = p1 + p2 + p3
    assert len(new) <= 150, f"quiz box {len(new)} > 150"
    prg[box:box + len(new)] = new
    prg[box + len(new):box + 150] = b'\x00' * (150 - len(new))

patch_quiz_box(prg)

# ---------------------------------------------------------------------------
# Kunio reaction box (B4:0126FE box 9, PRG 0x128DA..0x1290F, 53 bytes).
# 'quoi? pas en 1ere classe' (24 bytes) exceeds the 20-byte line budget of
# 'what? no first class', so rebalance with line 2 which has 6 bytes of
# slack ('ni d'hotesses? bon.' 19 vs 25): box total 51 <= 53.
# ---------------------------------------------------------------------------
def patch_box9(prg):
    box = 0x128DA
    k = bytes([0xD7, 0xD8, 0x1F])             # [KUNIO] name token
    f = lambda s: encode_fr(s)
    new = b'\xF9\xF4' + k + b'\xDC' + f("quoi? pas en premiere") + b'\xF7' + f("ni d'hotesses? bah.") + b'\xF5'
    assert len(new) <= 53, f"box9 {len(new)} > 53"
    prg[box:box + len(new)] = new
    prg[box + len(new):box + 53] = b'\x00' * (53 - len(new))

patch_box9(prg)

# ---------------------------------------------------------------------------
# Riki narration box (B4:0126FE box 10, PRG 0x1290F..0x129A6, 151 bytes).
# 'a gagne le quiz' (16 bytes) exceeds the 13-byte budget of 'won the quiz',
# so rebuild the whole box with rebalanced lines (total 143 <= 151).
# ---------------------------------------------------------------------------
def patch_box10(prg):
    box = 0x1290F
    riki = bytes([0xDA, 0xD6])                # [RIKI] name token
    dc = b'\xDC'
    k = bytes([0xD7, 0xD8, 0x1F])             # [KUNIO] name token
    f = lambda s: encode_fr(s)
    new = (b'\xF4' + riki + dc + k + f(" a gagne le quiz") + b'\xF7' + f("et un voyage gratuit") + b'\x2E\x2E\x2E' + b'\xF9'
           + b'\xF7\xF4' + riki + dc + f("il veut y aller seul") + b'\xF7' + f("et me laisser ici. moi? meh.") + b'\xF9'
           + b'\xF7\xF4' + riki + dc + f("mais je le suivrai") + b'\xF7' + f("jusqu'au bout du monde.") + b'\xF5')
    assert len(new) <= 151, f"box10 {len(new)} > 151"
    prg[box:box + len(new)] = new
    prg[box + len(new):box + 151] = b'\x00' * (151 - len(new))

patch_box10(prg)

# ---------------------------------------------------------------------------
# Mamoru protest box (B4:0126FE box 11, PRG 0x129A6..0x129CF, 41 bytes).
# 'pourquoi je dois aussi venir?' (29 bytes) exceeds the 25-byte budget of
# 'why do i have to go! too?', so line 1 is shortened to 'mais' (4 vs 8):
# total 40 <= 41.
# ---------------------------------------------------------------------------
def patch_box11(prg):
    box = 0x129A6
    m = bytes([0xD2, 0xD1, 0x19])             # [?2] name token
    dc = b'\xDC'
    f = lambda s: encode_fr(s)
    new = b'\xF4' + m + dc + f("mais") + b'\xF7' + f("pourquoi je dois aussi venir?") + b'\xF5'
    assert len(new) <= 41, f"box11 {len(new)} > 41"
    prg[box:box + len(new)] = new
    prg[box + len(new):box + 41] = b'\x00' * (41 - len(new))

patch_box11(prg)

# ---------------------------------------------------------------------------
# Riki 'look.' box (B4:0126FE box 13, originally PRG 0x12A04..0x12A0E, 10
# bytes). 'regarde' (7 bytes) doesn't fit the 5-byte 'look.' slot and the
# box is sandwiched with no room, so relocate the box to free bank-end space
# at PRG 0x13F99 (CPU $BF99) and repoint entry 13 of the pointer table.
# ---------------------------------------------------------------------------
def patch_box13(prg):
    riki = bytes([0xDA, 0xD6])                # [RIKI] name token
    dc = b'\xDC'
    f = lambda s: encode_fr(s)
    new = b'\xF4' + riki + dc + f("regarde") + b'\xF5'
    assert len(new) <= 30, f"box13 {len(new)} > 30"
    prg[0x13F99:0x13F99 + len(new)] = new
    # repoint pointer table entry 13 (at 0x126CE) AA04 -> BF99
    # bank 4 2nd half: CPU = PRG - 0x8000 (0x12000..0x13FFF -> $A000..$BFFF)
    cpu = 0x13F99 - 0x8000
    assert cpu == 0xBF99
    prg[0x126CE:0x126D0] = bytes([cpu & 0xFF, (cpu >> 8) & 0xFF])

patch_box13(prg)

# ---------------------------------------------------------------------------
# Quiz tournament box (B4:0126FE box 14, PRG 0x12A0E..0x12A34, 38 bytes).
# 'un tournoi de basket' (20 letters) exceeds the 19-letter 'a street
# basketball' slot, but 'de rue?' (7) is shorter than 'tournament?.' (12):
# fixed bytes 7 + 20 + 7 = 34 <= 38, padded to box size.
# ---------------------------------------------------------------------------
def patch_box14(prg):
    m = bytes([0xD2, 0xD1, 0x19])          # name token
    dc = b'\xDC'
    f = lambda s: encode_fr(s)
    new = b'\xF4' + m + dc + f("un tournoi de basket") + b'\xF7' + f("de rue?") + b'\xF5'
    assert len(new) <= 38, f"box14 {len(new)} > 38"
    prg[0x12A0E:0x12A0E + len(new)] = new
    prg[0x12A0E + len(new):0x12A0E + 38] = b'\x00' * (38 - len(new))

patch_box14(prg)

# ---------------------------------------------------------------------------
# Mamoru tire question box (B4:0126FE box 26, PRG 0x12BFD..0x12C46, 73
# bytes, 2 pages). 'on revient pas en pneu?' (23 letters) exceeds the
# 21-letter 'no riding on a tire?.' slot, so the whole box is rebuilt with
# shorter page-1 lines (13+15 vs 18+18): 38 + 29 = 67 <= 73, padded.
# ---------------------------------------------------------------------------
def patch_box26(prg):
    m = bytes([0xD2, 0xD1, 0x19])          # name token
    dc = b'\xDC'
    f = lambda s: encode_fr(s)
    new = (b'\xF4' + m + dc + f("tout est pret") + b'\xF7' + f("pour le retour?") +
           b'\xF9\xF3\xF3\xF7' + b'\xF4' + m + dc + f("on revient pas en pneu?") + b'\xF5')
    assert len(new) <= 73, f"box26 {len(new)} > 73"
    prg[0x12BFD:0x12BFD + len(new)] = new
    prg[0x12BFD + len(new):0x12BFD + 73] = b'\x00' * (73 - len(new))

patch_box26(prg)

# ---------------------------------------------------------------------------
# Johnny plane-tickets box (B4:0126FE box 27, PRG 0x12C46..0x12CA5, 95
# bytes, 2 pages). ' des billets en 1ere classe' (27 letters + <04> control)
# exceeds the 21-letter ' first class tickets!' slot by 5; 'comme tu
# voulais.' (17 vs 22) and 'j'ai tes billets d'avion.' (25 = 25) rebalance:
# total 95, exact fit.
# ---------------------------------------------------------------------------
def patch_box27(prg):
    m = bytes([0xD5, 0xD3, 0xD9])          # [JOHNNY] name token
    dc = b'\xDC'
    f = lambda s: encode_fr(s)
    new = (b'\xF4' + m + dc + f("salut") + bytes([0xD7, 0xD8, 0x1F]) + f(".") +
           b'\xF7' + f("j'ai tes billets d'avion.") + b'\xF9\xF3\xF3\xF7' +
           b'\xF4' + m + dc + b'\x04' + f("des billets en premiere") +
           b'\xF7' + f("comme tu voulais") + b'\xF5')
    assert len(new) <= 95, f"box27 {len(new)} > 95"
    prg[0x12C46:0x12C46 + len(new)] = new
    prg[0x12C46 + len(new):0x12C46 + 95] = b'\x00' * (95 - len(new))

patch_box27(prg)

# ---------------------------------------------------------------------------
# Riki plane-scene box (B4:0126FE box 34, PRG 0x12DAF..0x12DDF, 48 bytes).
# 'c'etait cool la derniere fois' (29 letters) exceeds the 26-letter
# 'wasn't the last trip fun?.' slot, so the French sentence is split across
# the box's two lines: 'c'etait cool la derniere fois' + 'non?.' (34
# letters total). 7 fixed bytes + 34 = 41 <= 48, padded to box size. The
# box stays at the same address and the secondary table at PRG 0x1ACA7 is
# text-independent (identical JP/EN), so no pointer moves.
# ---------------------------------------------------------------------------
def patch_box34(prg):
    riki = bytes([0xDA, 0xD6])            # [RIKI] name token
    dc = b'\xDC'
    f = lambda s: encode_fr(s)
    new = (b'\xF4' + riki + dc + f("c'etait cool la derniere fois") +
           b'\xF7' + f("non?.") + b'\xF5')
    assert len(new) <= 48, f"box34 {len(new)} > 48"
    prg[0x12DAF:0x12DAF + len(new)] = new
    prg[0x12DAF + len(new):0x12DAF + 48] = b'\x00' * (48 - len(new))

patch_box34(prg)

# ---------------------------------------------------------------------------
# Plane-scene box (B4:0126FE box 35, PRG 0x12DDF..0x12EFB, 284 bytes, many
# pages). 'detache moi. je deteste voler' (29 letters) exceeds the 24-letter
# 'untie me. i hate flying.' slot by 5, so the whole box is rebuilt from the
# pristine EN layout (orig) with all current FR lines, letting L229 overrun
# its slot. The 5 extra bytes are reclaimed by trimming invisible trailing
# padding (0x00 spaces) from the padded lines - the box has 28 such bytes.
# Markers and name tokens are preserved exactly; total stays <= 284.
# ---------------------------------------------------------------------------
def patch_box35(prg):
    box = 0x12DDF
    size = 0x12EFB - 0x12DDF                     # 284
    bs = bytes(orig[box:box + size])             # pristine EN box
    lines = split_lines(bs)
    new_bs = bytearray()
    pad_pos = []                                 # indices of padding bytes added
    for idx, line in enumerate(lines):
        blk = ('B4:0126FE', idx + 216)
        fr_list = T.get(blk)
        if fr_list is None:
            for _, b in line:
                new_bs += b
            continue
        pi = 0
        for kind, b in line:
            if kind == 'L':
                fb = encode_fr(fr_list[pi])
                pi += 1
                n = max(0, len(b) - len(fb))
                pad_pos.extend(range(len(new_bs) + len(fb), len(new_bs) + len(fb) + n))
                new_bs += fb + b'\x00' * n
            else:
                new_bs += b
    over = len(new_bs) - size
    assert over > 0, f"box35 should overrun, got {len(new_bs)} <= {size}"
    assert len(pad_pos) >= over, f"box35: only {len(pad_pos)} padding bytes, need {over}"
    # remove exactly `over` invisible padding bytes (tracked positions), last ones first
    for pos in sorted(pad_pos[-over:], reverse=True):
        del new_bs[pos]
    assert len(new_bs) == size, f"box35 rebuilt to {len(new_bs)}, expected {size}"
    prg[box:box + size] = bytes(new_bs)

patch_box35(prg)

# ---------------------------------------------------------------------------
# Credits box (B4:0126FE box 36, PRG 0x12EFB..0x12FF2, 248 bytes). The
# original English credits (my grand master / dte programmer / translators /
# editor / main hacker + team) are rewritten entirely in French, dropping the
# original translation team. Same marker rhythm as EN: title <f3><f4>..<f9>
# + 9x<f3><f7>, entries <f4>ROLE<0e><f7>NAME<f9> + 9x<f3><f7>, final entry
# <f9><f3><f3><f4><f5>. The 6502 code at 0x12FF3+ is never touched.
# ---------------------------------------------------------------------------
def patch_box36(prg):
    box = 0x12EFB
    size = 0x12FF2 - 0x12EFB + 1                # 248
    f = lambda s: encode_fr(s)
    new = (b'\xF3\xF4' + f("merci special a") + b'\xF9' + b'\xF3' * 9 + b'\xF7'
           + b'\xF4' + f("freebuff.com") + b'\x0E\xF7' + f("et endymion74") + b'\xF9' + b'\xF3' * 9 + b'\xF7'
           + b'\xF4' + f("merci d'avoir joue!") + b'\x0E\xF7' + f("a bientot!") + b'\xF9\xF3\xF3\xF4\xF5')
    assert len(new) <= size, f"box36 {len(new)} > {size}"
    prg[box:box + len(new)] = new
    prg[box + len(new):box + size] = b'\x00' * (size - len(new))

patch_box36(prg)

# ---------------------------------------------------------------------------
# Boot flow, as traced from the state machine:
#   state 0 (intro/boxer) -> 70 frames -> state 4 (intro/attract screen)
#   -> state 3 (main menu). START during state 0 jumps to the menu.
#
# Two changes, both identical JP/EN:
#  1. Boot into state 4 instead of state 0: the boxer animation is skipped
#     but the intro screen that follows it (the game's title/attract
#     sequence, "l'intro" with the quiz) still plays before the menu.
#  2. Redirect bank 3's $800F entry (the boxer's dispatcher) straight to
#     $AB38 (the "exit intro -> menu" sequence): this keeps the boxer off
#     the screen everywhere, including the menu's idle attract which also
#     re-enters state 0 through $800F.
# ---------------------------------------------------------------------------
def patch_boot_state(prg):
    # Boot init at $CA08 (PRG 0x1CA08): LDA #$00; STA $0588 -> LDA #$04
    assert prg[0x1CA08:0x1CA0B] == bytes([0xA9, 0x00, 0x8D]), \
        f"unexpected boot state bytes: {prg[0x1CA08:0x1CA0B].hex()}"
    prg[0x1CA08:0x1CA0A] = bytes([0xA9, 0x04])

def patch_skip_intro(prg):
    # PRG 0x0C00F (CPU $800F, bank arg 3): JMP $AB69 -> JMP $AB38
    assert prg[0x0C00F:0x0C012] == bytes([0x4C, 0x69, 0xAB]), \
        f"unexpected intro entry bytes: {prg[0x0C00F:0x0C012].hex()}"
    prg[0x0C00F:0x0C012] = bytes([0x4C, 0x38, 0xAB])

patch_boot_state(prg)
patch_skip_intro(prg)

# ---------------------------------------------------------------------------
# DTE name table (bank 7, PRG 0x1FDEE, decoder $FDC0). The quiz master name
# token <D4><DB><DC> expands via the DTE pairs to "HOST:" (D4="HO", DB="ST",
# DC=": "). Change DB from "ST" to "TE" so every quiz box shows "HOTE:".
# DB is only ever used inside the <D4><DB><DC> token, so this is safe.
# ---------------------------------------------------------------------------
def patch_dte_table(prg):
    # table[21], table[22] (PRG 0x1FE02/0x1FE03): 's' 't' -> 't' 'e'
    assert prg[0x1FE02:0x1FE04] == bytes([0x23, 0x24]), \
        f"unexpected DTE DB entry: {prg[0x1FE02:0x1FE04].hex()}"
    prg[0x1FE02:0x1FE04] = bytes([0x24, 0x15])

patch_dte_table(prg)

# write ROM
data[16:16+8*16384] = prg
open(OUT, "wb").write(data)
print(f"wrote {OUT}")
