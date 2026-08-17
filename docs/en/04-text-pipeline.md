# 04 — Text pipeline, font and patching

## Font

- **Outline** font (hollow letters), 16 px = 2 tile rows (top row = top bar
  of the letter).
- Screenshot reading threshold: `max(r,g,b) > 60`.
- Available charset: `a-z`, space, `0-9`, `! ? . '` — **no accents, commas or
  dashes** (limited font). The French text respects this.

## Text-reading tools

| Tool | Role |
|---|---|
| `tools/_read_text.py` | 8×8 glyphs of a screen (PNG screenshot) |
| `tools/_decode_all.py` | EN glyph reference → FR decoding |
| `tools/_decode_screen_text.py` / `_decode_screens.py` | Screen decoding with the patch font |
| `tools/_ascii_preview.py` | ASCII rendering of a screenshot (quick terminal preview) |

> Note: the bitmap match against CHR ROM (`_font_match.py`) was inconclusive —
> the font is not found as-is in the CHR banks (probable palette/shadow
> transformation). To re-investigate.

## Translation table (`tools/translations.py`)

Source of truth for the translations. Key = `(bank:offset, line)`, value =
list of French strings, one per **letter piece (L)** of the line, in order.
Control bytes and **name tokens (K)** are preserved by the patcher.

Examples:

```python
# In-game tactics (5 cells × 9 chars)
T[('B3:00F732', 0)] = ['offensif marque frimeur automatic defensif']
# In-game command menu (9 commands, aligned cells + pointers)
#   tir, ball en l'air, attaque, frappe, passe, ball, dunk, arme, hasard
# Downtown Quiz dialogues (bank 4)
T[('B4:0126FE', 34)] = ['exact!']
T[('B4:0126FE', 40)] = ['quel comeback']
```

### Name token patterns

```python
NAME_PATTERNS = [
    bytes([0xD7, 0xD8, 0x1F]),
    bytes([0xDA, 0xD6]),
    bytes([0xD5, 0xD3, 0xD9]),
    bytes([0xD4, 0xDB, 0xDC]),
    bytes([0xD2, 0xD1, 0x19]),
]
```

## Application (`tools/patch_rom.py`)

Strategy: **keep every non-letter byte in place** (controls, name tokens) and
replace only letter bytes with French. Each French string must fit within the
byte budget of its L piece (otherwise padded with spaces).

Patched blocks (banks 3 and 4), e.g.:
`(3, 0x00F6B4, 115)` team names / locations (kept in English: proper nouns),
`(3, 0x00F732, 46)` tactics,
`(4, 0x0126FE, 2293)` quiz dialogues, etc.

## IPS generation (`tools/make_ips.py`)

Produces both patches:
- `orig_jp.nes → fr.nes` → `Nekketsu Street Basket (JPN) FR.ips` (19 KB, recommended),
- `en.nes → fr.nes` → `Nekketsu Street Basket (v1.2 Final) FR.ips` (4 KB).

IPS format: `PATCH` header, `(offset 3 B, size 2 B, data)` records, RLE
records when size = 0, `EOF` trailer.
