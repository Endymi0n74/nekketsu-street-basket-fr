# 02 — State machine

## Variables

- `$0588`: main state (written on every screen change).
- `$0589`: substate (sub-machine of the current screen).
- Writes are hookable via `emu.addMemoryCallback(..., emu.callbackType.write,
  addr, addr, emu.memType.InternalRam)` (see `tools/_tact.lua`,
  `tools/_mt_hook.lua`).

## Dispatcher

Bank 7, `$CA79`:

```asm
CA79: LDA $0588          ; current state
      ...                ; indexes a table at $CA8B
      JMP (handler)      ; jumps to the state handler
```

The `$CA8B` table holds the handler addresses, which are actually
**bank-switch stubs**: e.g. state 2 (menu/SORT) points to `$CAB0` → stub
`$FC38` → bank switch → real handler at `$8000` in **bank 3**.

Menu substates are dispatched through a table at `$802A` (bank 3).

## Observed flow (via WRAM hooks + screenshots)

```
boot ──► state 04 (Downtown quiz) ──► state 03 (title, attract)
        state 03 ── substate cycle 0x80-0x84 ──► state 00 (attract) ──► 03...
        [Start/A at title] ──► state 02 (SORT menu — team sort)
```

- The **quiz** (state 04) lasts ~8,000 frames (~133 s) without input on
  Mesen; repeated A taps advance it much faster (finished at f2206 in one run).
- The **title** (state 03) loops in attract: substates 80-84, returning to
  state 00.
- The **SORT menu** (state 02): substate cycle 08 → 07 → 05. It is a
  3-position cursor; pressing **A** triggers SELECT (substate 88 → 07) and
  records a character pick (2 picks then back to the menu) — the state exit
  has not been triggered yet.

## Handlers located (bank 3)

| Address | Substate | Role |
|---|---|---|
| `$81C6` | 0 | Menu entry (drawing) |
| `$87B2` | 4 | Draws the 4 SORT characters |
| `$88CE` | 5 | Cursor phase (reads `$04` with `AND #$03` / `AND #$90`) |
| `$89C5` / `$8A80` | 7 | Selection (active path `$8B38`) |
| `$8BA2` | 8 | Active handler while in the menu (~1×/frame); input read at `$8C11` |

## Analysis pitfall

**Linear** disassembly drifts in data tables: the addresses above were
confirmed by **exec hooks** (the sub-8 handler `$8BA2` runs ~1×/frame while
in the menu) and by watching `$0588/$0589` writes — not by raw disassembly
alone.
