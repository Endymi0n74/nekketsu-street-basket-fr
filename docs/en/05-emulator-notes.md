# 05 — Emulator notes: pitfalls and working APIs

Two emulators were used; both have finicky Lua APIs. This page is the memo of
the discoveries, so nobody has to walk through the same dead ends.

## Mesen 2.1.1 Desktop (Windows) — reference emulator

Launch (GUI mode, mandatory):

```bash
cd "/c/Users/endymion/Desktop/Mesen_2.1.1_Windows"
CAP_PREFIX=_m ./Mesen.exe D:/Codex/nes_translate/fr.nes \
  D:/Codex/nes_translate/_mesen_dump.lua --enableStdout
```

### BROKEN API on this build (do not retry)

| API | Symptom |
|---|---|
| `emu.setInput(table, port)` | **No-op**: `getInput` sees nothing, `$04` stays 00. Tested with 1/2/3 args, ports 0/1, all button names. |
| `emu.read(debug, memType, addr)` | **Ignores the address**: always returns the 1st byte of the domain (PRG=0x4C, CHR=0x7F, WRAM=0x00). |
| `emu.write(...)` | **Silent no-op**: no memory callback fired. |
| `emu.addCheat(...)` | Signature error (expects 2 params, unreliable behaviour). |
| `emu.takeScreenshot()` in `--testrunner` | Returns 0 bytes. **Use GUI mode.** |

### Working API

| API | Usage |
|---|---|
| `emu.takeScreenshot()` | GUI mode: returns the **PNG bytes** (write them to a file yourself). |
| `emu.addMemoryCallback(fn, emu.callbackType.write, addr, addr, emu.memType.InternalRam)` | WRAM write hooks → state machine (`$0588/$0589/$04`…). |
| `emu.addEventCallback(fn, emu.eventType.endFrame)` | Per-frame tick (counters, periodic screenshots). |
| `emu.addEventCallback(fn, emu.callbackType.exec, addr, addr, memType)` | Exec hook (e.g. `$FF98`, end of the input poll) — **fires reliably**, but cannot write. |

Available memTypes: `InternalRam`, `PrgRom` (alias `nesPrgRom=45`),
`callbackType.exec=2`.

### Input: the only reliable path is the real keyboard

See `docs/03-input.md`. Summary: **Mapping2** (S=A, A=B, W=Start, Q=Select,
arrows), mandatory window focus (`AttachThreadInput` +
`SetForegroundWindow`), keys sent **in the same PowerShell process** via
`SendKeys`. `AllowBackgroundInput` alone is not enough.

## BizHawk (EmuHawk + quickerNES) — used 15-16/08

- `emu.frameadvance()` **deadlocks** in `--lua` mode (script on the main
  thread → deadlock). Use event hooks instead.
- `memory.usememorydomain("PPU")` / `"VRAM"` **do not exist** in quickerNES:
  an invalid name is silently ignored (the previous domain stays active) →
  the "PPU dumps" of 16/08 were actually **WRAM** (2 KB, folded) and constant
  CHR.
- Real domains (legacy API `memory.getmemorydomainlist()`): `WRAM`, `CHR`,
  `CIRAM (nametables)`, `PRG ROM`, `CHR VROM`, `PALRAM`, `OAM`, `System Bus`.
- **`joypad.set` works** (fr3/fr4 runs: navigation up to the match and the
  MEMBERS screen) — the reliable input path of BizHawk.

## Validated workflow (17/08) to reach a screen

1. Launch Mesen in GUI with a Lua hook script (`tools/_mt_hook.lua` or
   `tools/_tact.lua`) that logs `$0588/$0589/$04` and takes screenshots
   (periodic + on every state change).
2. Drive the keyboard with `tools/_drive2.ps1` (focus + SendKeys, reads the
   Lua log to branch per screen).
3. Analyse the PNGs with `tools/_ascii_preview.py` (ASCII preview in the
   terminal) and/or the text decoders.

## Operational tips

- `taskkill //F //IM Mesen.exe` then relaunch: runs are long (boot → quiz →
  title ≈ 2-3 min); a savestate at the menu would speed things up (savestate
  API exists but is unusable for input on this build).
- The Lua log file can be read by PowerShell while the game runs (the
  "log lines: 0" is transient: re-read with retries).
- Avoid em-dashes and non-ASCII in `.ps1` files (PowerShell encoding).
