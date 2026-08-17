# 01 — ROM structure and disassembly

## Overview

- **Game**: Nekketsu! Street Basket — Ganbare Dunk Heroes (Famicom, 1993,
  Technos Japan). License screen: "Nekketsu Street Basket".
- **ROM**: 262,160 bytes = 16-byte iNES header + 256 KB of PRG.
- **Cartridge**: no CHR ROM in this file (128 KB PRG + 128 KB PRG? —
  to be confirmed; graphics are read through bank 7 / data banks).

> TBD: the exact PRG/CHR partition of the file. The disassembly work covered
> the **first 8 banks of 16 KB** (`data[16:16+8*16384]` in `patch_rom.py`),
> bank 7 being fixed ($C000-$FFFF CPU).

## Banks

| Bank | ROM offset | CPU space | Observed role |
|---|---|---|---|
| 0-2 | 0x00000-0x0BFFF | $8000-$BFFF (switchable) | — |
| 3 | 0x0C000-0x0FFFF | $8000-$BFFF | Screen handlers (menu, SORT, title, quiz…) |
| 4 | 0x10000-0x13FFF | $8000-$BFFF | Dialogues (Downtown Quiz, plane, credits), text |
| 5-6 | 0x14000-0x1BFFF | $8000-$BFFF | — |
| 7 | 0x1C000-0x1FFFF | $C000-$FFFF (fixed) | System routines: input, state dispatcher, bank-switch trampolines |

CPU addresses in the disassembly are `base + (off % 0x4000)` with
`base = 0x8000` (or 0xC000 for the fixed bank).

## Tool

`tools/dis6502.py`: minimal 6502 disassembler (full opcode table, addressing
modes, `disasm_line(prg, off, base, cpu)`).

Typical use:

```python
import sys; sys.path.insert(0, "tools")
from dis6502 import disasm_line
prg = open("fr.nes", "rb").read()[16:16+8*16384]
for off in range(0x1C000, 0x1C100):  # bank 7
    addr, size, text = disasm_line(prg, off)
    print(f"{addr:04X}: {text}")
```

⚠️ **Linear** disassembly (one instruction per byte) drifts inside data
regions (pointer tables, text). The `analysis/*.txt` outputs are therefore
raw; useful regions were re-disassembled by following branches (see
`docs/02-state-machine.md` and `docs/03-input.md`).

## Key routines located (bank 7)

| Address | Role |
|---|---|
| `$F8D0-$F9A0` | Input block (see 03-input.md) |
| `$F973` | Raw read `$4016/$4017` → `$04/$05` |
| `$F8EA` | Edge detection → `$04/$05` = this-frame presses |
| `$FF80` | Copies `$06/$07` → `$00/$01` (held state for game logic) |
| `$FF98` | End of poll (useful exec hook: runs ~1×/frame) |
| `$CA79` | State dispatcher (LDA `$0588` → table `$CA8B`) |
| `$FC38` | Trampoline: bank switch to the real state handler |

## WRAM addresses used by the state machine

| Address | Role |
|---|---|
| `$0588` | Main state |
| `$0589` | Substate |
| `$058D` | Flags (bit 1 → picks the input-read routine) |
| `$00/$01` | Held state P1 read by game logic |
| `$04/$05` | This-frame presses P1/P2 (edge) |
| `$06/$07` | Held state P1/P2 |
