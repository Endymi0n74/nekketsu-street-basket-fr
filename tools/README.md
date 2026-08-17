# tools/ — outillage de rétro-ingénierie & traduction

Scripts utilisés pour la traduction FR de *Nekketsu Street Basket* (désassemblage,
extraction du texte, patch, pilotage d'émulateur). Pour l'anglais, voir
[../README.en.md](../README.en.md) et [../docs/en](../docs/en).

> **Générique vs Nekketsu-spécifique** : les scripts nommés `nes_*` sont
> réutilisables sur **n'importe quel jeu NES** (configuration par variables
> d'environnement / données). Les scripts `_*` (préfixe `_`) sont les versions
> Nekketsu-spécifiques qui ont servi à l'analyse. Pièges émulateurs :
> [../docs/05-emulator-notes.md](../docs/05-emulator-notes.md).

---

## Désassemblage & patch (Python)

| Fichier | Description | Usage |
|---|---|---|
| `dis6502.py` | Désassembleur 6502 minimal (module) | `from dis6502 import disasm_line` — voir [../docs/01-disassembly.md](../docs/01-disassembly.md) |
| `make_ips.py` | Génère les 2 IPS (JPN→FR, EN→FR) avec auto-vérification (réapplication comparée) | `python make_ips.py` (ROMs `orig_jp.nes`/`en.nes` → `fr.nes` dans le cwd) |
| `patch_rom.py` | Applique les traductions sur la ROM (blocs génériques + patchs spéciaux : menu de commandes, boîtes du quiz, DTE, boot) | `python patch_rom.py` (lit `en.nes`, écrit `fr.nes` ; `translations.py` requis) |
| `translations.py` | Table de traductions FR — **source de vérité** (clé `(banque:offset, ligne)` → listes de chaînes) | importé par `patch_rom.py` |

## Lecture d'écrans & texte (Python)

| Fichier | Description | Usage |
|---|---|---|
| `_ascii_preview.py` | Rendu ASCII d'un screenshot pour aperçu dans le terminal | `python _ascii_preview.py shot.png [scale] [y0 y1]` |
| `_read_text.py` | Glyphes 8×8 d'un écran (bitmap brut) | `python _read_text.py shot.png` |
| `_decode_all.py` | Référence de glyphes EN → décodage FR (police du patch) | `python _decode_all.py` |
| `_decode_screen_text.py` | Décodage d'un screenshot par correspondance avec les tuiles CHR de la ROM | `python _decode_screen_text.py rom.nes shot.png [row0 row1]` |
| `_decode_screens.py` | Décodage du bytecode d'écran (stream PPU) d'une ROM | one-shot, ROM en dur à adapter |

## Mesen 2.1.1 — harnais Lua (mode GUI)

Lancement : `Mesen.exe <rom> <script.lua> --enableStdout`
(voir [../docs/05-emulator-notes.md](../docs/05-emulator-notes.md) pour les API
cassées/marchantes).

| Fichier | Description |
|---|---|
| `nes_state_hook.lua` | **GÉNÉRIQUE** : traçage machine à états — hooks d'écriture WRAM par adresses, screenshots périodiques + à chaque changement, compteur d'exécutions. Config : `HOOK_ADDRS`/`HOOK_EXEC`/`HOOK_SNAP_EVERY`/`HOOK_OUTDIR`/`HOOK_PREFIX`/`HOOK_MEMTYPE`/`HOOK_MAX_FRAMES` |
| `_tact.lua` | Hooks `$0588`/`$0589` + screenshots (périodiques + changement d'état) — Nekketsu |
| `_mt_hook.lua` | Trace `$04`/`$0588`/`$0589` + navigation probes (title→…) — Nekketsu |
| `_mt_nav.lua` | Navigation vers un match + probe du menu TACTIQUES — Nekketsu |
| `_mt_state.lua` | Dump état + manette au titre, observation A/Start/Select — Nekketsu |
| `_nav_log.lua` | Screenshots toutes les 60 frames + log état/`$04` — Nekketsu |
| `_mesen_dump.lua` | Harnais de capture title→SORT (12 écrans + WRAM) ; `CAP_PREFIX=_e` pour `en.nes` |
| `_mesen_dump2.lua` | Exploration au-delà du SORT (15 écrans) ; `CAP_PREFIX` |

## Pilotes clavier (PowerShell, Windows)

Le focus fenêtre + envoi des touches doivent se faire **dans le même processus**
(sinon la console vole le focus) — voir [../docs/03-input.md](../docs/03-input.md).

| Fichier | Description | Usage |
|---|---|---|
| `nes_driver.ps1` | **GÉNÉRIQUE** : pilote à séquences configurables (`wait`/`tap`/`hold`/`taps`/`until`), mapping bouton→touche, branche selon l'état du log. Config : `$KEYMAP`/`$SEQ` + env `NESDRV_LOG`/`NESDRV_DLOG`/`NESDRV_PROC` | `powershell -NoProfile -ExecutionPolicy Bypass -File nes_driver.ps1` |
| `_drive2.ps1` | Pilote adaptatif Nekketsu (speed-up quiz → Start → A) — référence | idem |
| `_drive_test.ps1` | Démo : focus + tap S, vérifier `$04` dans le log Lua | idem |
| `_focus.ps1` | Focus de la fenêtre Mesen (AttachThreadInput + repli clic) | `powershell -File _focus.ps1` |
| `_sendkey.ps1` | Envoi d'une touche (tap ou hold) | `powershell -File _sendkey.ps1 -key X [-hold 80]` |

---

## Démarrage rapide (générique, autre jeu NES)

```bash
# 1. Observer le jeu (état, sous-états, manette, captures)
HOOK_OUTDIR=D:/tmp ./Mesen.exe ma_rom.nes tools/nes_state_hook.lua --enableStdout

# 2. Piloter la navigation (séquences dans $SEQ de nes_driver.ps1)
powershell -NoProfile -ExecutionPolicy Bypass -File tools/nes_driver.ps1
```

Guide complet pour traduire un autre jeu : [../docs/06-porting-guide.md](../docs/06-porting-guide.md).
