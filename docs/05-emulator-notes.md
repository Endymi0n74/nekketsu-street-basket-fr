# 05 — Notes émulateurs : pièges et API qui marchent

Deux émulateurs ont été utilisés. Les deux ont des API Lua capricieuses ;
cette page est le mémo des découvertes pour ne pas repasser par les mêmes
impasses.

## Mesen 2.1.1 Desktop (Windows) — l'émulateur de référence

Lancement (mode GUI, indispensable) :

```bash
cd "/c/Users/endymion/Desktop/Mesen_2.1.1_Windows"
CAP_PREFIX=_m ./Mesen.exe D:/Codex/nes_translate/fr.nes \
  D:/Codex/nes_translate/_mesen_dump.lua --enableStdout
```

### API CASSÉE sur ce build (ne pas réessayer)

| API | Symptôme |
|---|---|
| `emu.setInput(table, port)` | **No-op** : `getInput` ne voit rien, `$04` reste 00. Testé avec 1/2/3 args, ports 0/1, tous noms de boutons. |
| `emu.read(debug, memType, addr)` | **Ignore l'adresse** : renvoie toujours le 1er octet du domaine (PRG=0x4C, CHR=0x7F, WRAM=0x00). |
| `emu.write(...)` | **No-op silencieux** : aucun memory callback déclenché. |
| `emu.addCheat(...)` | Erreur de signature (2 paramètres attendus, comportement non fiable). |
| `emu.takeScreenshot()` en `--testrunner` | Renvoie 0 octet. **Utiliser le mode GUI.** |

### API qui MARCHE

| API | Usage |
|---|---|
| `emu.takeScreenshot()` | Mode GUI : renvoie les **octets PNG** (à écrire soi-même dans un fichier). |
| `emu.addMemoryCallback(fn, emu.callbackType.write, addr, addr, emu.memType.InternalRam)` | Hooks d'écriture WRAM → machine à états (`$0588/$0589/$04`…). |
| `emu.addEventCallback(fn, emu.eventType.endFrame)` | Tick par frame (compteurs, screenshots périodiques). |
| `emu.addEventCallback(fn, emu.callbackType.exec, addr, addr, memType)` | Hook exec (ex. `$FF98`, fin du poll input) — **se déclenche bien**, mais ne permet pas d'écrire. |

MemTypes disponibles : `InternalRam`, `PrgRom` (alias `nesPrgRom=45`),
`callbackType.exec=2`.

### Input : seule voie fiable = clavier réel

Voir `docs/03-input.md`. En résumé : mapping **Mapping2** (S=A, A=B, W=Start,
Q=Select, flèches), focus fenêtre obligatoire (`AttachThreadInput` +
`SetForegroundWindow`), touches envoyées **dans le même processus** PowerShell
via `SendKeys`. `AllowBackgroundInput` seul ne suffit pas.

## BizHawk (EmuHawk + quickerNES) — utilisé les 15-16/08

- `emu.frameadvance()` **se bloque** en mode `--lua` (script sur le thread
  principal → deadlock). Utiliser des event hooks à la place.
- `memory.usememorydomain("PPU")` / `"VRAM"` **n'existent pas** dans
  quickerNES : un nom invalide est ignoré SILENCIEUSEMENT (le domaine
  précédent reste actif) → les « dumps PPU » du 16/08 étaient en réalité de la
  **WRAM** (2 Ko repliée) et du CHR constant.
- Vrais domains (API legacy `memory.getmemorydomainlist()`) : `WRAM`, `CHR`,
  `CIRAM (nametables)`, `PRG ROM`, `CHR VROM`, `PALRAM`, `OAM`, `System Bus`.
- **`joypad.set` fonctionne** (runs fr3/fr4 : navigation jusqu'au match et à
  l'écran MEMBERS) — c'est la voie d'input fiable de BizHawk.

## Workflow validé (17/08) pour avancer vers un écran

1. Lancer Mesen en GUI avec un script Lua de hooks
   (`tools/_mt_hook.lua` ou `tools/_tact.lua`) qui log `$0588/$0589/$04` et
   prend des screenshots (périodiques + à chaque changement d'état).
2. Piloter le clavier avec `tools/_drive2.ps1` (focus + SendKeys, lecture du
   log Lua pour brancher selon l'écran).
3. Analyser les PNG avec `tools/_ascii_preview.py` (aperçu ASCII dans le
   terminal) et/ou les décodeurs de texte.

## Relances / astuces opérationnelles

- `taskkill //F //IM Mesen.exe` puis relancer : les runs sont longs (boot →
  quiz → titre ≈ 2-3 min), un savestate au menu accélérerait (API savestate
  présente mais inutilisable pour l'input sur ce build).
- Le fichier de log Lua peut être lu par PowerShell pendant que le jeu tourne
  (le « log lines: 0 » est transitoire : relire avec retries).
- Éviter les tirets cadratin et non-ASCII dans les `.ps1` (encodage PowerShell).
