# 06 — How to translate another NES game (porting guide)

[Français](../06-porting-guide.md)

This guide explains how to reuse this repository's toolset to translate
**another NES game**. It follows the method used for Nekketsu Street Basket,
step by step, clarifying what is reused as-is and what must be redone for each
game.

## Reused as-is

- `tools/dis6502.py` — 6502 disassembler (any 6502 ROM).
- `tools/make_ips.py` — IPS generation with built-in verification (universal).
- `tools/nes_state_hook.lua` — generic Mesen harness (addresses via env).
- `tools/nes_driver.ps1` — generic keyboard driver (data-defined sequences,
  button→key mapping); `tools/_focus.ps1`, `_sendkey.ps1` as helpers.
- `tools/_ascii_preview.py`, `tools/_read_text.py` — screenshot analysis.
- `.github/` — CI workflow + `check_ips.py` + `check_links.py`.
- Emulator knowledge: broken Mesen 2.1.1 API / BizHawk — see
  [docs/en/05-emulator-notes.md](05-emulator-notes.md).

## Redone for each game

- The **addresses** (state, input, dispatcher, trampolines).
- The **text map**: blocks, control bytes, name tokens, font.
- `translations.py` (the content) and `patch_rom.py` constants
  (BLOCKS, LETTER, NAME_PATTERNS, EN/OUT).
- The CI round-trip test magic bytes.

---

## Step 1 — Set up the environment

1. Clone the repo: `git clone https://github.com/Endymi0n74/nes-translation`.
2. Copy `tools/` and `.github/` into your project.
3. Prepare your base ROM (dump of the original game) and Mesen 2.1.1 (GUI mode).
4. Run the generic harness to check it works (defaults = Nekketsu; change the
   addresses once you know them):

```bash
HOOK_OUTDIR=D:/tmp ./Mesen.exe your_rom.nes tools/nes_state_hook.lua --enableStdout
```

## Step 2 — Map the state machine (the longest part)

1. **Find the controller-read routine.** Disassemble the fixed bank with
   `dis6502.py` and look for the classic pattern: a `$4016` write followed by
   8 shifted reads (the NES protocol is universal; only the storage addresses
   change). For Nekketsu: `$F973` (raw read) → `$04/$05` (this-frame presses)
   → `$06/$07` (held state) → `$00/$01`.
2. **Confirm the poll with the harness**: `HOOK_EXEC=<routine end>` → the
   counter should approach ~60/frame.
3. **Find the state address.** Hook WRAM writes on the addresses where the
   code stores state; when you see a byte changing only on screen transitions,
   that's the state (`$0588` on Nekketsu). The substate (`$0589`) often
   changes right after.
4. **Locate the dispatcher**: `LDA state` → table index → `JMP`. On Nekketsu:
   `$CA79` / table `$CA8B`. Handlers are often **bank-switch trampolines**
   (e.g. `$FC38`) that switch to another bank.
5. **Draw the flow**: boot → screens → menus, using the harness captures
   (`HOOK_ADDRS="state:0x0588:snap,sub:0x0589"`) and `_ascii_preview.py` to
   identify each screen without opening images.

> Nekketsu tip: the quiz lasts ~8,000 frames without input — never wait
> passively, send A taps every ~2 s via `tools/nes_driver.ps1`.

## Step 3 — Find and extract the text

1. **Scan the banks** for text areas. The workspace has one-shot exploration
   scripts to adapt: `scan_ascii_text.py` (ASCII text), `find_text.py`
   (letter-tile ranges), `find_font.py` / `find_chtab.py` (font location in
   the CHR banks), `find_ptr_tables.py` (pointer tables), `diff_roms.py`
   (compare two ROMs to see what a patch changes).
2. **Identify the encoding**: the NES font often limits the charset
   (`a-z`, `0-9`, space, `!?.'` on Nekketsu). Note the limits — the FR text
   must fit them.
3. **Structure the text**: spot control bytes (line/box ends), name tokens
   (small patterns like `D7 D8 1F` = [KUNIO]) and the byte budgets per letter
   piece.
4. **Create `translations.py`** for your game: keys `(bank:offset, line)`,
   values = lists of FR strings per letter piece, in order.

## Step 4 — Adapt the patcher

1. In `patch_rom.py`: change `EN`/`OUT`, `LETTER` (charset),
   `NAME_PATTERNS` (name tokens), `BLOCKS` (patched text areas).
2. Handle special cases like on Nekketsu:
   - **Aligned-slot menus** (9 commands, pointers) → rewrite strings and
     pointers explicitly (`patch_command_menu`).
   - **Dialogue boxes over budget** → rewrite the box with rebalanced lines
     (`patch_quiz_box`, `patch_box9`…).
   - **DTE tables** (name compression) → adjust the pairs (`HOST:` →
     `HOTE:`).
3. Generate the IPS: `make_ips.py` (verifies the re-application itself).

## Step 5 — Verify in the emulator

1. Run the patched ROM with the harness + the generic keyboard driver
   (`tools/nes_driver.ps1`, data-defined sequences).
2. Compare FR vs base screenshots (crops, `_ascii_preview.py`).
3. Check the critical screens: menus, dialogues, ending screen.

## Step 6 — Set up CI

1. Copy `.github/workflows/ci.yml` + `.github/scripts/`.
2. Adapt `test_roundtrip.py`: the **magic bytes** (bytes your `patch_rom.py`
   asserts on) and the special box zone (guaranteed overrun). The principle —
   synthetic ROMs, no copyrighted content — stays identical.

## Step 7 — Publish

- `make_ips.py` → two IPS files (on the JAP and/or EN base ROM).
- README with the base/result ROM CRC32s (never include the ROMs themselves).
- License + credits (see `LICENSE` and `CONTRIBUTING.md` in the repo).

---

## Estimated effort (Nekketsu experience)

| Phase | Difficulty |
|---|---|
| State-machine mapping | ⭐⭐⭐ the longest (input injection included) |
| Text/font extraction | ⭐⭐ |
| Patcher adaptation | ⭐⭐ |
| Verification + CI | ⭐ |

The ready-made toolset avoids starting from scratch: the remaining bulk of the
work is **reading the game** (addresses + text), not writing tools.
