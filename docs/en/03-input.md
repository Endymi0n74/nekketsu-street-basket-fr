# 03 — Input routines and injection

## Routines (bank 7)

The game polls the controller **every frame**:

```asm
$F973: raw read $4016/$4017 → accumulates into $04/$05 (P1/P2)
$F8EA: edge detection
       $04/$05 = this-frame presses
       $06/$07 = held state
$FF80: depending on $058D bit 1 → $F949 or $F911 (adapted reads),
       then copies $06/$07 → $00/$01 (what game logic reads)
$FF98: end of poll (useful exec hook: runs ~1×/frame)
```

### Bit mapping

| Bit | Button |
|---|---|
| 7 | A |
| 6 | B |
| 5 | Select |
| 4 | Start |
| 3 | Up |
| 2 | Down |
| 1 | Left |
| 0 | Right |

Screen logic reads input from `$04+Y` with masks: e.g. the SORT menu:
`AND #$03` (Left/Right = move cursor), `AND #$90` (A/Start = select).

## Injection: the problem

On **Mesen 2.1.1 Desktop** (Windows build), the Lua input/memory API is
broken:

- `emu.setInput({...}, 1)` → **no-op** (verified: `getInput` sees nothing).
- `emu.read(debug, memType, addr)` → ignores the address (returns the first
  byte of the domain).
- `emu.write(...)` → silent no-op (no callback fired).
- `emu.addCheat(...)` → unexpected signature (error).

Neither write hooks nor exec callbacks can inject input, and `emu.read` rules
out self-adaptive navigation from Lua.

## Chosen solution: PowerShell keyboard driver

The **input manager → $4016** path is independent of the Lua API: real
keyboard presses reach the game. Two constraints were discovered:

1. **Active keyboard mapping = Mapping2** (Mesen 2.1.1 default):

   | NES button | Key |
   |---|---|
   | A | **S** |
   | B | **A** |
   | Start | **W** |
   | Select | **Q** |
   | D-pad | arrows |
   | Turbo A / B | X / Z |

2. **Window focus is mandatory**: `AllowBackgroundInput` alone is not
   enough; and each separate `powershell.exe` opens a console that steals
   focus. The working solution: **focus + key sending in the same PowerShell
   process**:

   - `AttachThreadInput` + `ShowWindow` + `BringWindowToTop` +
     `SetForegroundWindow` (see `tools/_focus.ps1`),
   - then `[System.Windows.Forms.SendKeys]::SendWait("s")` (key = S).

Verified result: an S tap during the poll produces `$04 = 0x80` (A) in the
hooks — input reaches game logic.

## Provided drivers

| File | Role |
|---|---|
| `tools/_focus.ps1` | Mesen window focus (AttachThreadInput method + click fallback) |
| `tools/_sendkey.ps1` | Sends one key |
| `tools/_drive_test.ps1` | Demo: focus + tap S → check `$04` |
| `tools/_drive2.ps1` | Adaptive driver: reads the Lua log, presses per screen (retries) — Nekketsu-specific |
| `tools/nes_driver.ps1` | **Generic** driver: data-defined sequences (`wait`/`tap`/`hold`/`taps`/`until`), button→key mapping, branches on state — reusable on another game |

## Known navigation sequences

- **BizHawk (fr3/fr4 runs, joypad API)**: title → Start → A → A → A×4 →
  match → Select; `fr4` shows the MEMBERS screen (team selection) after 14 A.
- **Mesen (keyboard driver)**: A taps during the quiz → title → one A tap →
  SORT menu (state 02). Launching a match is being worked on.

> Tip: do not wait out the quiz (~8,000 frames). Repeated A taps every ~2 s
> advance it (finished at f2206 in one run).
