# 05 — Notes émulateurs : pièges et API qui marchent

*Voir aussi [`docs/05-emulator-notes.md`](https://github.com/Endymi0n74/nekketsu-street-basket-fr/blob/main/docs/05-emulator-notes.md).*

## Mesen 2.1.1 Desktop (Windows) — émulateur de référence

Lancement (mode GUI, indispensable) :

```bash
cd "/c/Users/endymion/Desktop/Mesen_2.1.1_Windows"
CAP_PREFIX=_m ./Mesen.exe D:/Codex/nes_translate/fr.nes \
  D:/Codex/nes_translate/_mesen_dump.lua --enableStdout
```

### API CASSÉE sur ce build (ne pas réessayer)

| API | Symptôme |
|---|---|
| `emu.setInput(table, port)` | **No-op** : `getInput` ne voit rien |
| `emu.read(debug, memType, addr)` | **Ignore l'adresse** (1er octet du domaine) |
| `emu.write(...)` | **No-op silencieux** |
| `emu.addCheat(...)` | Erreur de signature |
| `emu.takeScreenshot()` en `--testrunner` | Renvoie 0 octet — mode GUI obligatoire |

### API qui MARCHE

| API | Usage |
|---|---|
| `emu.takeScreenshot()` | Mode GUI : renvoie les **octets PNG** |
| `emu.addMemoryCallback(...)` | Hooks d'écriture WRAM (machine à états) |
| `emu.addEventCallback(fn, emu.eventType.endFrame)` | Tick par frame |
| exec callbacks (ex. `$FF98`) | Se déclenchent, mais ne peuvent pas écrire |

MemTypes : `InternalRam`, `PrgRom` (`nesPrgRom=45`), `callbackType.exec=2`.

### Input : seule voie fiable = clavier réel

Voir [[Input]]. Mapping2 (S=A, A=B, W=Start, Q=Select), focus obligatoire,
touches envoyées dans le même processus PowerShell via `SendKeys`.

## BizHawk (EmuHawk + quickerNES)

- `emu.frameadvance()` **se bloque** en mode `--lua` → event hooks.
- `memory.usememorydomain("PPU")` / `"VRAM"` **n'existent pas** dans
  quickerNES (noms invalides ignorés silencieusement → dumps WRAM repliée).
- Vrais domains : `WRAM`, `CHR`, `CIRAM`, `PRG ROM`, `CHR VROM`, `PALRAM`,
  `OAM`, `System Bus`.
- **`joypad.set` fonctionne** (runs fr3/fr4 jusqu'au match).

## Workflow validé

1. Mesen GUI + script Lua de hooks. Le harnais **générique**
   `tools/nes_state_hook.lua` (configurable par variables d'environnement,
   défauts = Nekketsu) est recommandé — pour un autre jeu NES, changer les
   adresses via `HOOK_ADDRS`/`HOOK_EXEC` (voir l'en-tête du script) :
   logs d'écritures par adresse, screenshots périodiques + à chaque
   changement d'état, compteur d'exécutions d'une routine.
2. `tools/nes_driver.ps1` (générique) : séquences configurables
   (`wait`/`tap`/`hold`/`taps`/`until`), mapping bouton → touche, branche
   selon l'état lu dans le log. `_drive2.ps1` = version Nekketsu spécifique.
3. Analyse des PNG avec `tools/_ascii_preview.py` et les décodeurs.

## Astuces

- `taskkill //F //IM Mesen.exe` puis relancer : boot → quiz → titre ≈ 2-3 min.
- Le « log lines: 0 » du driver est transitoire → retries (5×).
- Éviter le non-ASCII dans les `.ps1` (encodage PowerShell).
